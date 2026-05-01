# app/pipelines/recommendation_pipeline.py
from typing import List, Dict, Optional
import numpy as np

from app.domain.student import StudentProfile
from app.engines.rules_engine import check_eligibility
from app.engines.similarity_engine import SimilarityEngine
from app.engines.ranking_engine import RankingEngine
from app.repositories.program_repository import ProgramRepository
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.core.paths import EMBEDDINGS_PATH


class RecommendationPipeline:
    def __init__(self):
        self.program_repo = ProgramRepository()
        self.similarity_engine = SimilarityEngine()
        self.ranking_engine = RankingEngine()
        self.course_rec_repo = CourseRecommendationRepository()
        self.embeddings = None
        try:
            self.embeddings = np.load(EMBEDDINGS_PATH)
        except Exception:
            # Embeddings are an optimization; fall back to on-the-fly similarity.
            self.embeddings = None

    def recommend(
        self,
        student: StudentProfile,
        district: str,
        max_results: Optional[int] = None,
        above_score_count: int = 0,
    ) -> Dict:
        """
        Get recommendations with explanations included.
        Always includes aspirational courses (stream+subjects match but Z-score too low).
        """
        debug = self.recommend_debug(
            student=student,
            district=district,
            max_results=max_results,
            above_score_count=above_score_count,
        )

        # Combine eligible and ALL aspirational recommendations
        all_recommendations = debug["eligible_recommendations"] + debug.get(
            "above_score_recommendations", []
        )

        # Generate explanations with full student context
        explanations = self._generate_explanations_batch(
            student, district, all_recommendations
        )

        # Enrich each recommendation with explanation and metadata
        for item in all_recommendations:
            # Add explanation
            item["explanation"] = explanations.get(
                item["course_code"],
                f"This {item.get('stream_required', 'degree')} program aligns with your academic profile.",
            )

            # Enrich with CourseRecommendation metadata (job_roles, industries, skills)
            course_rec = self.course_rec_repo.get_course_by_code(item["course_code"])
            if course_rec:
                item["job_roles"] = course_rec.job_roles[:5]
                item["industries"] = course_rec.industries[:5]
                item["core_skills"] = course_rec.core_skills[:5]

            # Strip heavy internal fields not needed by frontend
            item.pop("reason", None)
            item.pop("subjects_required", None)
            item.pop("student_subjects", None)
            item.pop("student_stream", None)
            item.pop("student_zscore", None)
            item.pop("district", None)
            item.pop("eligibility_details", None)
            # Keep: eligibility, aspirational, stream_required, score

        # Split back into eligible and aspirational
        final_eligible = [
            item for item in all_recommendations if item.get("eligibility") is not False
        ]
        final_aspirational = [
            item for item in all_recommendations if item.get("aspirational") is True
        ]

        return {
            "eligible_recommendations": final_eligible,
            "above_score_recommendations": final_aspirational,
            "summary": debug.get("summary", {}),
        }

    def recommend_debug(
        self,
        student: StudentProfile,
        district: str,
        max_results: Optional[int] = None,
        above_score_count: int = 0,
    ) -> Dict:
        programs = self.program_repo.get_all_programs()
        student_vec = self.similarity_engine.encode_text(student.interests)

        embeddings_ok = (
            self.embeddings is not None
            and isinstance(self.embeddings, np.ndarray)
            and len(self.embeddings) == len(programs)
        )

        eligible = []
        above_score = []  # Courses above student's z-score
        rejected = []

        for idx, program in enumerate(programs):
            # Updated to handle new check_eligibility return signature
            is_eligible, reason, details = check_eligibility(student, program, district)

            if embeddings_ok:
                similarity = float(
                    self.similarity_engine.compute_similarity_vectors(
                        student_vec,
                        self.embeddings[idx],
                    )
                )
            else:
                similarity = float(
                    self.similarity_engine.compute_similarity(
                        student.interests,
                        program.course_name,
                    )
                )

            debug_entry = {
                "course_code": program.course_code,
                "course_name": program.course_name,
                "degree_name": program.course_name,  # Backwards compatibility
                "stream_required": program.stream,
                "subjects_required": program.subject_requirements,
                "universities": program.universities,
                "faculty_department": program.faculty_department,
                "duration": program.duration,
                "degree_programme": program.degree_programme,
                "medium_of_instruction": program.medium_of_instruction,
                "practical_test": program.practical_test,
                "proposed_intake": program.proposed_intake,
                "notes": program.notes,
                "metadata": program.metadata,
                "student_stream": student.stream,
                "student_subjects": student.subjects,
                "student_zscore": student.zscore,
                "district": district,
                "similarity": round(similarity, 4),
                "eligibility": is_eligible,
                "reason": reason,
                "eligibility_details": details,
            }

            has_interests = bool(student.interests and student.interests.strip())
            MIN_SIMILARITY_THRESHOLD = 0.40

            if has_interests and similarity < MIN_SIMILARITY_THRESHOLD:
                debug_entry["eligibility"] = False
                debug_entry["reason"] = (
                    f"Low relevance to your interests (similarity: {similarity:.4f})"
                )
                rejected.append(debug_entry)
                continue

            if is_eligible:
                # We use pure similarity * 100 so the UI Match Score truly reflects interest alignment.
                # Since all courses in this list are eligible, the eligibility weight is redundant.
                debug_entry["score"] = similarity * 100
                eligible.append(debug_entry)
            else:
                # Check if rejection was due to z-score (aspirational course)
                # Bug fix: key is "subjects_match" not "subject_match"
                if (
                    details.get("zscore_check") == False
                    and details.get("stream_match")
                    and details.get("subjects_match")
                ):
                    # This is a course the student could reach with higher z-score
                    # Again, use pure similarity * 100 for the UI
                    debug_entry["score"] = similarity * 100
                    debug_entry["aspirational"] = True
                    # Include Z-score gap info for frontend display
                    zscore_details = details.get("zscore_details", {})
                    if zscore_details:
                        debug_entry["zscore_gap"] = {
                            "student_zscore": zscore_details.get("student_zscore"),
                            "required_cutoff": zscore_details.get("required_cutoff"),
                        }
                    above_score.append(debug_entry)
                else:
                    rejected.append(debug_entry)

        # Sort eligible by score
        eligible.sort(key=lambda x: x["score"], reverse=True)

        # Sort above-score by similarity (most relevant first)
        above_score.sort(key=lambda x: x["similarity"], reverse=True)

        # Apply limits
        eligible_recommendations = (
            eligible if max_results is None else eligible[:max_results]
        )

        # Always include all aspirational courses (frontend filters them)
        above_score_recommendations = above_score

        response = {
            "eligible_recommendations": eligible_recommendations,
            "above_score_recommendations": above_score_recommendations,
            "rejected_programs": rejected,
            "summary": {
                "total_programs": len(programs),
                "eligible_count": len(eligible),
                "above_score_count": len(above_score),
                "rejected_count": len(rejected),
            },
        }

        # Add a global explanation if there are NO recommendations
        if len(eligible_recommendations) == 0 and len(above_score_recommendations) == 0:
            if has_interests:
                response["summary"]["global_explanation"] = (
                    f"While your interest in '{student.interests}' is great, it strongly diverges from the standard pathways available to {student.stream} students. "
                    "In the Sri Lankan university system, your A/L stream strictly dictates your eligible degrees. "
                    "Consider looking into external professional qualifications or degrees in IT/Management that accept students from any stream."
                )
            elif details.get("zscore_check") == False:
                response["summary"]["global_explanation"] = (
                    "Your A/L subjects perfectly align with several degrees, but your Z-Score is currently below the historical cutoffs for these programs in your district. "
                    "Consider exploring external degree programs or diplomas that have lower academic entry barriers."
                )
            else:
                response["summary"]["global_explanation"] = (
                    f"Unfortunately, we couldn't find any state university degrees that strictly match your specific combination of A/L subjects in the {student.stream} stream. "
                    "Some degrees require a very specific combination of subjects (e.g., Chemistry AND Physics)."
                )

        return response

    # ------------------------------------------------------------------
    # Explanation generation
    # ------------------------------------------------------------------

    def _generate_explanations_batch(
        self,
        student: StudentProfile,
        district: str,
        recommendations: List[Dict],
    ) -> Dict[str, str]:
        """
        Generate AI-powered explanations for recommendations.
        Uses full student context (stream, subjects, zscore, district, interests).
        Falls back to rule-based explanations if Gemini is unavailable.
        """
        explanations = {}

        try:
            from app.engines.explanation_engine import ExplanationEngine

            explanation_engine = ExplanationEngine()

            # Build enriched course details for Gemini
            course_details = []
            for rec in recommendations:
                # Look up CourseRecommendation for richer metadata
                course_rec = self.course_rec_repo.get_course_by_code(rec["course_code"])
                job_roles = course_rec.job_roles[:4] if course_rec else []
                industries = course_rec.industries[:3] if course_rec else []
                core_skills = course_rec.core_skills[:3] if course_rec else []

                course_details.append(
                    {
                        "code": rec["course_code"],
                        "name": rec["course_name"],
                        "stream": rec.get("stream_required", "Unknown"),
                        "similarity": rec.get("similarity", 0),
                        "eligibility": rec.get("eligibility", True),
                        "aspirational": rec.get("aspirational", False),
                        "reason": rec.get("reason", ""),
                        "job_roles": job_roles,
                        "industries": industries,
                        "core_skills": core_skills,
                        "zscore_gap": rec.get("zscore_gap"),
                    }
                )

            # Generate explanations using Gemini with full context
            explanations = self._call_gemini_for_explanations(
                student, district, course_details
            )

            # If Gemini returned empty (quota/error), use fallback
            if not explanations:
                print("Note: Gemini returned empty, using fallback explanations")
                explanations = self._generate_fallback_explanations(
                    student, district, recommendations
                )

        except Exception as e:
            # Fallback: generate context-aware rule-based explanations
            print(f"Note: Using fallback explanations due to: {e}")
            explanations = self._generate_fallback_explanations(
                student, district, recommendations
            )

        return explanations

    def _call_gemini_for_explanations(
        self,
        student: StudentProfile,
        district: str,
        courses: List[Dict],
    ) -> Dict[str, str]:
        """
        Call Gemini API to generate comprehensive, personalized explanations.
        Adapts prompt based on available student context.
        """
        try:
            import google.generativeai as genai
            from app.core.config import settings

            if not settings.GOOGLE_GEMINI_API_KEY:
                raise ValueError("Gemini API key not configured")

            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash-lite")

            # Detect what context is available
            has_interests = (
                student.interests
                and student.interests.strip()
                and student.interests.strip().lower()
                not in ("", "general university studies")
            )
            has_zscore = student.zscore is not None and student.zscore > 0

            # Build student profile section
            profile_lines = [
                f"A/L Stream: {student.stream}",
                f"A/L Subjects: {', '.join(student.subjects)}",
            ]
            if has_zscore:
                profile_lines.append(f"Z-Score: {student.zscore:.4f}")
            if district:
                profile_lines.append(f"District: {district}")
            if has_interests:
                profile_lines.append(f"Personal Interests: {student.interests}")

            student_profile = "\n".join(profile_lines)

            # Build course listing with eligibility status
            course_listing = []
            for c in courses:
                status = (
                    "ELIGIBLE" if c["eligibility"] else "ASPIRATIONAL (Z-score too low)"
                )
                roles = ", ".join(c["job_roles"]) if c["job_roles"] else "Various"
                skills = ", ".join(c["core_skills"]) if c["core_skills"] else ""
                industries = ", ".join(c["industries"]) if c["industries"] else ""

                entry = f"{c['code']}: {c['name']} [{status}]"
                entry += f"\n  Career Paths: {roles}"
                if skills:
                    entry += f"\n  Key Skills: {skills}"
                if industries:
                    entry += f"\n  Industries: {industries}"
                if c.get("zscore_gap"):
                    gap = c["zscore_gap"]
                    entry += f"\n  Student Z-Score: {gap['student_zscore']:.4f} | Required: {gap['required_cutoff']:.4f}"

                course_listing.append(entry)

            # Build adaptive prompt
            interest_instruction = ""
            if has_interests:
                interest_instruction = (
                    "- Do NOT just repeat their interests back to them. EXPLAIN the conceptual link.\n"
                    "- Provide a logical JUSTIFICATION for why someone with their specific interests AND their A/L stream would thrive in this specific degree.\n"
                    "- Connect their interests to the course's core skills and career paths."
                )
            else:
                interest_instruction = (
                    "- Explain how their A/L subjects logically prepare them for the core skills taught in this course\n"
                    "- Suggest 2-3 exciting career possibilities this degree opens up"
                )

            eligibility_instruction = ""
            if has_zscore:
                eligibility_instruction = (
                    "- For ELIGIBLE courses: confirm their Z-score qualifies them and be encouraging\n"
                    "- For ASPIRATIONAL courses: acknowledge the Z-score gap, be honest but motivating — "
                    "explain what they'd need to achieve and why it's worth striving for"
                )

            prompt = f"""You are a knowledgeable Sri Lankan University Career Counselor giving personalized advice to an A/L student.

STUDENT PROFILE:
{student_profile}

RECOMMENDED COURSES:
{chr(10).join(course_listing)}

For each course, write a personalized explanation (3-4 sentences, max 100 words) that:
{interest_instruction}
- Reference their specific A/L subjects as preparation for the course
{eligibility_instruction}
- Be specific about career outcomes from the course data provided

FORMAT (strictly follow this):
CODE: explanation

RULES:
- Do NOT include the course name in the explanation (the UI already shows it)
- Do NOT use generic filler phrases like "connects well with this program" or "aligns with your interests"
- EXPLAIN the "why". If they like business and math, explain how those skills are used in the degree's careers.
- DO mention specific careers from the data
- Be encouraging, warm, and specific to THIS student
- Each explanation should feel like personal advice from a counselor who knows this student"""

            response = model.generate_content(prompt)

            # Parse response
            explanations = {}
            for line in response.text.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        explanation = parts[1].strip()
                        # Remove markdown formatting
                        explanation = explanation.replace("**", "").replace("*", "")
                        if explanation:
                            explanations[code] = explanation

            return explanations

        except Exception as e:
            print(f"Gemini API error: {e}")
            return {}

    def _generate_fallback_explanations(
        self,
        student: StudentProfile,
        district: str,
        recommendations: List[Dict],
    ) -> Dict[str, str]:
        """
        Generate context-aware rule-based explanations when Gemini is unavailable.
        Adapts based on available student context (interests, zscore, subjects).
        """
        explanations = {}

        has_interests = (
            student.interests
            and student.interests.strip()
            and student.interests.strip().lower()
            not in ("", "general university studies")
        )
        subjects_str = ", ".join(student.subjects[:3])

        for rec in recommendations:
            code = rec["course_code"]
            name = rec["course_name"]
            stream = rec.get("stream_required", "degree program")

            # Look up career data
            course_rec = self.course_rec_repo.get_course_by_code(code)
            careers = (
                ", ".join(course_rec.job_roles[:2])
                if course_rec and course_rec.job_roles
                else "diverse careers"
            )

            if rec.get("eligibility"):
                # Eligible course
                if has_interests:
                    explanation = (
                        f"Based on your interest in '{student.interests[:60]}', this degree offers a logical pathway to apply those passions professionally. "
                        f"Your analytical skills developed through {subjects_str} will give you a significant advantage in grasping the core concepts. "
                        f"This specific combination of your interests and technical background is highly valued for roles like {careers}."
                    )
                else:
                    explanation = (
                        f"Your {student.stream} subjects ({subjects_str}) directly prepare you for this program. "
                        f"You're eligible based on your academic profile"
                        + (
                            f" and Z-score of {student.zscore:.4f}"
                            if student.zscore
                            else ""
                        )
                        + f". Career paths include {careers}."
                    )
            elif rec.get("aspirational"):
                # Aspirational course — Z-score too low
                gap = rec.get("zscore_gap", {})
                gap_str = ""
                if gap:
                    diff = gap.get("required_cutoff", 0) - gap.get("student_zscore", 0)
                    gap_str = f" (gap of {diff:.4f})"

                if has_interests:
                    explanation = (
                        f"This program matches your interest in {student.interests[:50]}, "
                        f"and your {subjects_str} subjects are the right preparation. "
                        f"However, it requires a higher Z-score{gap_str}. "
                        f"With improved results, you could pursue {careers}."
                    )
                else:
                    explanation = (
                        f"Your {student.stream} subjects ({subjects_str}) are the right fit for this program. "
                        f"It requires a higher Z-score than your current score{gap_str}. "
                        f"With improved performance, this opens paths to {careers}."
                    )
            else:
                explanation = (
                    f"This {stream} program offers career opportunities in {careers}. "
                    f"It's aligned with your academic background."
                )

            explanations[code] = explanation

        return explanations
