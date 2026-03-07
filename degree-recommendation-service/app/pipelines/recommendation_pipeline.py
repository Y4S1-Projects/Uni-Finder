# app/pipelines/recommendation_pipeline.py
from typing import List, Dict, Optional
import numpy as np

from app.domain.student import StudentProfile
from app.engines.rules_engine import check_eligibility
from app.engines.similarity_engine import SimilarityEngine
from app.engines.ranking_engine import RankingEngine
from app.repositories.program_repository import ProgramRepository
from app.core.paths import EMBEDDINGS_PATH


class RecommendationPipeline:
    def __init__(self):
        self.program_repo = ProgramRepository()
        self.similarity_engine = SimilarityEngine()
        self.ranking_engine = RankingEngine()
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
    ) -> List[Dict]:
        """
        Get recommendations with explanations included.
        """
        debug = self.recommend_debug(
            student=student,
            district=district,
            max_results=max_results,
            above_score_count=above_score_count,
        )

        # Combine eligible and above-score recommendations
        all_recommendations = debug["eligible_recommendations"] + debug.get(
            "above_score_recommendations", []
        )

        # Generate explanations for all recommendations
        explanations = self._generate_explanations_batch(
            student.interests, all_recommendations
        )

        # Include explanations and minimal metadata, strip heavy fields
        for item in all_recommendations:
            # Add explanation
            item["explanation"] = explanations.get(
                item["course_code"],
                f"This {item.get('stream_required', 'degree')} program aligns with your academic profile and interests.",
            )

            # Strip heavy explanation fields
            item.pop("reason", None)
            item.pop("subjects_required", None)
            item.pop("stream_required", None)
            item.pop("student_subjects", None)
            item.pop("student_stream", None)
            item.pop("student_zscore", None)
            item.pop("district", None)
            item.pop("eligibility_details", None)
            # Keep eligibility flag to distinguish eligible vs above-score

        return all_recommendations

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

            if is_eligible:
                score = self.ranking_engine.score(is_eligible, similarity)
                debug_entry["score"] = score
                eligible.append(debug_entry)
            else:
                # Check if rejection was due to z-score (aspirational course)
                if (
                    details.get("zscore_check") == False
                    and details.get("stream_match")
                    and details.get("subject_match")
                ):
                    # This is a course the student could reach with higher z-score
                    score = self.ranking_engine.score(False, similarity)
                    debug_entry["score"] = score
                    debug_entry["aspirational"] = True
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

        above_score_recommendations = (
            above_score[:above_score_count] if above_score_count > 0 else []
        )

        return {
            "eligible_recommendations": eligible_recommendations,
            "above_score_recommendations": above_score_recommendations,
            "rejected_programs": rejected,
            "summary": {
                "total_programs": len(programs),
                "eligible_count": len(eligible),
                "above_score_count": len(above_score_recommendations),
                "rejected_count": len(rejected),
            },
        }

    def _generate_explanations_batch(
        self, student_interests: str, recommendations: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate AI-powered explanations for recommendations.

        Uses Gemini API if available, falls back to rule-based explanations.

        Args:
            student_interests: Student's interest description
            recommendations: List of course recommendation dictionaries

        Returns:
            Dictionary mapping course_code to explanation text
        """
        explanations = {}

        try:
            from app.engines.explanation_engine import ExplanationEngine

            explanation_engine = ExplanationEngine()

            # Prepare course codes for explanation generation
            course_codes = [r["course_code"] for r in recommendations]

            # Build a simple format for Gemini
            course_details = []
            for rec in recommendations:
                course_details.append(
                    {
                        "code": rec["course_code"],
                        "name": rec["course_name"],
                        "stream": rec.get("stream_required", "Unknown"),
                        "similarity": rec.get("similarity", 0),
                        "reason": rec.get("reason", "Matches academic profile"),
                    }
                )

            # Generate explanations using Gemini
            explanations = self._call_gemini_for_explanations(
                student_interests, course_details
            )

        except Exception as e:
            # Fallback: generate simple rule-based explanations
            print(f"Note: Using fallback explanations due to: {e}")
            explanations = self._generate_fallback_explanations(recommendations)

        return explanations

    def _call_gemini_for_explanations(
        self, student_interests: str, courses: List[Dict]
    ) -> Dict[str, str]:
        """
        Call Gemini API to generate explanations for courses.

        Args:
            student_interests: Student's interests description
            courses: List of course info dictionaries

        Returns:
            Dictionary mapping course codes to explanations
        """
        try:
            import google.generativeai as genai
            from app.core.config import settings

            if not settings.GOOGLE_GEMINI_API_KEY:
                raise ValueError("Gemini API key not configured")

            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")

            # Build course listing
            course_listing = []
            for course in courses:
                course_listing.append(
                    f"{course['code']}: {course['name']} ({course['stream']})"
                )

            prompt = f"""Generate brief, personalized explanations for why these degree programs match a student's interests.

Student's Interests: {student_interests}

Recommended Programs:
{chr(10).join(course_listing)}

For each program, provide ONLY a 1-2 sentence explanation (max 60 words) explaining:
1. How it matches the student's interests
2. What career opportunities it offers

Format your response EXACTLY as:
CODE: explanation (without repeating the course name)

Examples:
19: This program combines mathematics and technology perfectly, offering career paths in software development and data science.
20: Your passion for helping people aligns directly, preparing you for healthcare careers and making a real difference.

Be encouraging, specific, and concise. Do not include the course name or stream in the explanation."""

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
        self, recommendations: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate simple rule-based explanations when Gemini is unavailable.

        Args:
            recommendations: List of course recommendation dictionaries

        Returns:
            Dictionary mapping course codes to explanations
        """
        explanations = {}

        for rec in recommendations:
            code = rec["course_code"]
            name = rec["course_name"]
            stream = rec.get("stream_required", "degree program")
            reason = rec.get("reason", "matches your interests")
            similarity = rec.get("similarity", 0)

            # Build explanation based on eligibility status
            if rec.get("eligibility"):
                # Eligible course
                explanation = (
                    f"You're eligible for {name}. "
                    f"This {stream} program aligns well with your academic profile and interests ({reason}). "
                    f"It offers diverse career opportunities in this field."
                )
            else:
                # Aspirational course
                if rec.get("aspirational"):
                    explanation = (
                        f"{name} is aligned with your interests, "
                        f"but requires a higher Z-score. "
                        f"With improved performance, this excellent {stream} program could be within reach."
                    )
                else:
                    explanation = (
                        f"{name} is a {stream} program that offers strong alignment "
                        f"with your academic profile and career interests."
                    )

            explanations[code] = explanation

        return explanations
