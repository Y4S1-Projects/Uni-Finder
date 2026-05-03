# app/services/interest_recommendation_service.py
"""
Interest-Based Recommendation Service - 3-Step Pipeline.

Step 1: Eligibility Filtering (using rules_engine)
Step 2: Semantic Interest Matching (using similarity_engine)
Step 3: Explainable AI (using explanation_engine with Gemini)
"""

from typing import Dict, List, Optional
from fastapi import HTTPException

from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine
from app.repositories.program_repository import ProgramRepository
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.utils.stream_mapper import map_to_standard_streams, standard_stream_sort_key


class InterestRecommendationService:
    """
    Implements 3-step recommendation pipeline:
    1. Eligibility Filter - rules-based filtering
    2. Semantic Interest Matching - similarity scoring
    3. Explainable AI - personalized explanations
    """

    def __init__(
        self,
        similarity_engine: Optional[SimilarityEngine] = None,
        explanation_engine: Optional[ExplanationEngine] = None,
        program_repository: Optional[ProgramRepository] = None,
        course_repository: Optional[CourseRecommendationRepository] = None,
    ):
        self.similarity_engine = similarity_engine or SimilarityEngine()
        self.explanation_engine = explanation_engine or ExplanationEngine()
        self.program_repository = program_repository or ProgramRepository()
        self.course_repository = course_repository or CourseRecommendationRepository()

    def get_interest_based_recommendations(
        self,
        student_input: str,
        eligible_course_codes: List[str],
        max_results: int = 5,
        explain: bool = True,
        ol_marks: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Get interest-based recommendations with 3-step pipeline.

        Args:
            student_input: Student's interests/skills description
            eligible_course_codes: Course codes from eligibility filtering
            max_results: Maximum number of recommendations to return
            explain: Whether to generate explanations (uses Gemini API)
            ol_marks: Optional O/L subject marks organized by core + buckets

        Returns:
            List of recommendations with scores and explanations
        """
        try:
            # Step 1: Load eligible courses
            eligible_courses = self.course_repository.get_courses_by_codes(
                eligible_course_codes
            )

            if not eligible_courses:
                raise HTTPException(
                    status_code=404,
                    detail="No eligible courses found for the given criteria.",
                )

            # Step 2: Semantic Interest Matching
            ranked_courses = self.similarity_engine.rank_courses_by_interest(
                student_input, eligible_courses
            )

            # Limit results
            top_courses = ranked_courses[:max_results]

            # Step 3: Generate Explanations (if enabled)
            explanations = {}
            if explain:
                explanations = self.explanation_engine.generate_explanations(
                    student_input,
                    ranked_courses,
                    max_courses=len(top_courses),
                    ol_marks=ol_marks,
                )

            # Build response
            recommendations = []
            for course, similarity_score in top_courses:
                # Get full program details
                program = self.program_repository.get_program_by_code(
                    course.course_code
                )

                recommendation = {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "stream": course.stream,
                    "match_score_percentage": round(similarity_score * 100, 1),
                    "matched_interests": self.explanation_engine.extract_overlapping_keywords(
                        student_input, course, max_keywords=5
                    ),
                    "job_roles": course.job_roles[:5],  # Top 5 roles
                    "industries": course.industries[:5],  # Top 5 industries
                    "core_skills": course.core_skills[:5],  # Top 5 skills
                    "explanation": explanations.get(
                        course.course_code,
                        "This course aligns with your interests and career goals.",
                    ),
                }

                # Add program details if available
                if program:
                    recommendation.update(
                        {
                            "universities": program.universities,
                            "duration": program.duration,
                            "degree_programme": program.degree_programme,
                            "medium_of_instruction": program.medium_of_instruction,
                        }
                    )

                recommendations.append(recommendation)

            return recommendations

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating interest-based recommendations: {str(e)}",
            )

    def validate_input(self, student_input: str) -> tuple[bool, str]:
        """
        Validate student input string.

        Args:
            student_input: Student's interests/skills description

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not student_input or not isinstance(student_input, str):
            return False, "Student input must be a non-empty string."

        if len(student_input.strip()) < 10:
            return (
                False,
                "Please provide at least 10 characters describing your interests.",
            )

        if len(student_input) > 2000:
            return False, "Student input exceeds maximum length of 2000 characters."

        return True, ""

    def get_ol_career_tree(
        self,
        student_input: str,
        eligible_course_codes: List[str],
        ol_marks: Optional[Dict] = None,
        max_courses: int = 15,
    ) -> Dict:
        """
        Get O/L career tree - hierarchical pathway grouped by A/L streams.

        Args:
            student_input: Student's interests/career goals
            eligible_course_codes: Course codes from eligibility filtering
            ol_marks: Optional O/L subject marks
            max_courses: Maximum courses to analyze (before grouping)

        Returns:
            Hierarchical tree structure with streams as branches
        """
        try:
            # Step 1: Load eligible courses
            eligible_courses = self.course_repository.get_courses_by_codes(
                eligible_course_codes
            )

            if not eligible_courses:
                raise HTTPException(
                    status_code=404,
                    detail="No eligible courses found for the given criteria.",
                )

            # Step 2: Semantic Interest Matching - get more courses
            ranked_courses = self.similarity_engine.rank_courses_by_interest(
                student_input, eligible_courses
            )

            # Take top courses for analysis
            top_courses = ranked_courses[:max_courses]

            # Step 3: Group courses by normalized Sri Lankan A/L stream buckets
            stream_groups = {}
            for course, similarity_score in top_courses:
                mapped_streams = map_to_standard_streams(course.stream)

                # Skip malformed/unmapped stream rows instead of showing noisy stream labels.
                if not mapped_streams:
                    continue

                # Get program details
                program = self.program_repository.get_program_by_code(
                    course.course_code
                )

                for stream in mapped_streams:
                    if stream not in stream_groups:
                        stream_groups[stream] = []

                    stream_groups[stream].append(
                        {
                            "course": course,
                            "score": similarity_score,
                            "program": program,
                        }
                    )

            # Step 4: Build pathways for each stream
            pathways = []
            for stream_name, courses_data in stream_groups.items():
                # Use strongest degree score as stream score (best pathway signal).
                top_stream_score = max(c["score"] for c in courses_data)

                # Get O/L readiness for this stream
                readiness_info = self._assess_ol_readiness(stream_name, ol_marks)

                # Extract unique career paths
                all_careers = []
                for c in courses_data:
                    all_careers.extend(c["course"].job_roles[:3])
                unique_careers = list(dict.fromkeys(all_careers))[:6]  # Top 6 unique

                # Build degree list
                potential_degrees = []
                sorted_courses = sorted(
                    courses_data, key=lambda x: x["score"], reverse=True
                )
                seen_course_codes = set()

                for c in sorted_courses:
                    course = c["course"]
                    if course.course_code in seen_course_codes:
                        continue

                    program = c["program"]
                    universities = program.universities if program else []

                    potential_degrees.append(
                        {
                            "course_code": course.course_code,
                            "course_name": course.course_name,
                            "universities": universities,
                            "match_score_percentage": round(c["score"] * 100, 1),
                        }
                    )

                    seen_course_codes.add(course.course_code)
                    if len(potential_degrees) >= 5:  # Top 5 unique degrees per stream
                        break

                pathways.append(
                    {
                        "stream_name": stream_name,
                        "ol_readiness": readiness_info["text"],
                        "readiness_status": readiness_info["status"],
                        "match_score": round(top_stream_score * 100, 1),
                        "potential_degrees": potential_degrees,
                        "target_careers": unique_careers,
                    }
                )

            # Sort pathways by score then by canonical stream order.
            pathways.sort(
                key=lambda x: (
                    -x["match_score"],
                    standard_stream_sort_key(x["stream_name"]),
                )
            )

            # Step 5: Generate AI counselor advice
            ai_advice = self._generate_pathway_advice(student_input, pathways, ol_marks)

            return {
                "student_goal": student_input,
                "pathways": pathways,
                "ai_counselor_advice": ai_advice,
                "total_streams": len(pathways),
                "total_degrees": sum(len(p["potential_degrees"]) for p in pathways),
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating O/L career tree: {str(e)}",
            )

    def _assess_ol_readiness(
        self, stream_name: str, ol_marks: Optional[Dict]
    ) -> Dict[str, str]:
        """
        Assess if student's O/L marks are suitable for a given A/L stream.

        Args:
            stream_name: Target A/L stream
            ol_marks: Student's O/L marks

        Returns:
            Dict with 'text' (readable summary) and 'status' (excellent/good/needs_improvement)
        """
        if not ol_marks or not ol_marks.get("core"):
            return {
                "text": "No O/L marks provided",
                "status": "unknown",
            }

        core = ol_marks.get("core", {})
        math_grade = core.get("mathematics", "")
        science_grade = core.get("science", "")
        english_grade = core.get("english", "")

        # Define grade scoring
        grade_scores = {"A": 4, "B": 3, "C": 2, "S": 1, "W": 0, "": 0}

        # Stream-specific requirements
        if stream_name in ["Physical Science", "Biological Science"]:
            if (
                not math_grade
                or not science_grade
                or math_grade == "N/A"
                or science_grade == "N/A"
            ):
                return {
                    "text": "Maths & Science highly beneficial",
                    "status": "unknown",
                }

            math_score = grade_scores.get(math_grade, 0)
            science_score = grade_scores.get(science_grade, 0)

            if math_score >= 3 and science_score >= 3:
                return {
                    "text": f"On Track (Maths: {math_grade}, Science: {science_grade})",
                    "status": "excellent",
                }
            elif math_score >= 2 and science_score >= 2:
                return {
                    "text": f"Good Foundation (Maths: {math_grade}, Science: {science_grade})",
                    "status": "good",
                }
            else:
                return {
                    "text": f"Needs Improvement (Maths: {math_grade}, Science: {science_grade})",
                    "status": "needs_improvement",
                }

        elif stream_name == "Commerce":
            if not math_grade or math_grade == "N/A":
                return {
                    "text": "Strong Maths skills beneficial",
                    "status": "unknown",
                }

            math_score = grade_scores.get(math_grade, 0)
            if math_score >= 3:
                return {
                    "text": f"Excellent for Commerce (Maths: {math_grade})",
                    "status": "excellent",
                }
            elif math_score >= 2:
                return {
                    "text": f"Good for Commerce (Maths: {math_grade})",
                    "status": "good",
                }
            else:
                return {
                    "text": f"Strengthen Math Skills (Maths: {math_grade})",
                    "status": "needs_improvement",
                }

        elif stream_name in ["Engineering Technology", "Biosystems Technology"]:
            if (
                not math_grade
                or not science_grade
                or math_grade == "N/A"
                or science_grade == "N/A"
            ):
                return {
                    "text": "STEM subjects highly beneficial",
                    "status": "unknown",
                }

            math_score = grade_scores.get(math_grade, 0)
            science_score = grade_scores.get(science_grade, 0)

            if math_score >= 2 and science_score >= 2:
                return {
                    "text": f"Ready for Technology (Maths: {math_grade}, Science: {science_grade})",
                    "status": "excellent",
                }
            else:
                return {
                    "text": f"Improve STEM Subjects (Maths: {math_grade}, Science: {science_grade})",
                    "status": "needs_improvement",
                }

        else:  # Arts or other streams
            if not english_grade or english_grade == "N/A":
                return {
                    "text": "English proficiency beneficial",
                    "status": "unknown",
                }

            english_score = grade_scores.get(english_grade, 0)
            if english_score >= 3:
                return {
                    "text": f"Strong Foundation (English: {english_grade})",
                    "status": "excellent",
                }
            elif english_score >= 2:
                return {
                    "text": f"Good for Arts Stream (English: {english_grade})",
                    "status": "good",
                }
            else:
                return {
                    "text": f"Strengthen English (English: {english_grade})",
                    "status": "needs_improvement",
                }

    def _generate_pathway_advice(
        self, student_input: str, pathways: List[Dict], ol_marks: Optional[Dict]
    ) -> str:
        """
        Generate holistic AI advice for the entire career tree using Gemini.

        Args:
            student_input: Student's interests
            pathways: List of stream pathways with readiness
            ol_marks: Student's O/L marks

        Returns:
            AI-generated counseling advice
        """
        # Build summary of pathways
        pathway_summary = []
        for p in pathways[:3]:  # Top 3 streams
            degrees = ", ".join(
                [d["course_name"] for d in p.get("potential_degrees", [])[:3]]
            )
            careers = ", ".join(p.get("target_careers", [])[:3])
            pathway_summary.append(
                f"- Stream: {p['stream_name']} (Match: {p['match_score']:.0f}%, O/L Readiness: {p['ol_readiness']})\n"
                f"  Possible Degrees: {degrees}\n"
                f"  Target Careers: {careers}"
            )

        prompt = f"""You are an objective, analytical Sri Lankan educational counselor providing a detailed, highly personal, and realistic A/L stream recommendation.

Student's Stated Goal/Interest: "{student_input}"

Top Recommended Pathways (Based on AI matching):
{chr(10).join(pathway_summary)}

Student's O/L Performance:
{self._format_ol_marks(ol_marks)}

Provide a deeply analytical, highly detailed, and personalized explanation (using HTML formatting like <p> and <strong>). Do NOT use generic flattery or filler text. Your response must be logically justified.

Address the following points directly:
1. Analytical Stream Justification: Objectively explain exactly WHY the top recommended A/L stream matches their stated goal. Do not just say "it matches"; explain the logical connection between the stream's subjects and their goal.
2. Career & Degree Pathways: Specifically mention the degrees and target careers they can achieve through this stream (use the exact data provided above).
3. Realistic O/L Marks Analysis: 
   - If they provided marks: Detail exactly how their specific grades support the chosen stream. If a mark is weak, give realistic, grounded advice on why that subject is critical for the stream and how they must bridge the gap.
   - If they did NOT provide marks (or left them empty): Explicitly state that while no marks were provided, strongly emphasize WHICH specific O/L subjects are absolutely critical for their top stream and why they must ensure a strong foundation in them.

Be strictly realistic, analytical, and highly specific to the student's exact inputs. Speak directly to the student."""

        try:
            import google.generativeai as genai
            from app.core.config import settings

            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash-lite")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback advice
            best_stream = pathways[0]["stream_name"] if pathways else "your top choice"
            top_careers = (
                ", ".join(pathways[0].get("target_careers", [])[:3])
                if pathways and pathways[0].get("target_careers")
                else "exciting career paths"
            )
            top_degrees = (
                ", ".join(
                    [
                        d["course_name"]
                        for d in pathways[0].get("potential_degrees", [])[:2]
                    ]
                )
                if pathways and pathways[0].get("potential_degrees")
                else "advanced university programs"
            )

            fallback = f'<p>Based on your specific interest in <strong>"{student_input}"</strong>, the <strong>{best_stream}</strong> stream is the most logical A/L pathway for you. This stream provides the exact academic foundation required to pursue degrees like <strong>{top_degrees}</strong>, directly paving the way for careers such as <strong>{top_careers}</strong>.</p>'

            has_marks = False
            core_marks = {}
            if ol_marks and ol_marks.get("core"):
                for k, v in ol_marks["core"].items():
                    if (
                        v
                        and v != "N/A"
                        and k
                        not in ["bucket_1_grade", "bucket_2_grade", "bucket_3_grade"]
                    ):
                        has_marks = True
                        core_marks[k] = v

            if has_marks:
                fallback += "<p><strong>O/L Performance Analysis:</strong><br/>"
                strong_subjects = []
                weak_subjects = []
                grade_scores = {"A": 4, "B": 3, "C": 2, "S": 1, "W": 0}

                for subj, grade in core_marks.items():
                    if grade_scores.get(grade, 0) >= 3:
                        strong_subjects.append(f"{subj.title()} ('{grade}')")
                    else:
                        weak_subjects.append(f"{subj.title()} ('{grade}')")

                if strong_subjects:
                    fallback += f"Your strong grades in <strong>{', '.join(strong_subjects)}</strong> are a major advantage. These subjects demonstrate the analytical and foundational skills critical for excelling in the {best_stream} stream. "

                if weak_subjects:
                    fallback += f"However, your performance in <strong>{', '.join(weak_subjects)}</strong> indicates a gap. The {best_stream} stream is highly demanding, so you must proactively bridge this gap through extra practice and focused revision to ensure you don't struggle at the A/L level."
                fallback += "</p>"
            else:
                fallback += f"<p><strong>O/L Foundation Required:</strong><br/>Since you did not provide specific O/L marks, please be aware that the <strong>{best_stream}</strong> stream is rigorous. It is absolutely critical that you have a strong foundation in core subjects related to this stream (such as Mathematics and Science). If you feel weak in these foundational areas, you must focus heavily on them now to succeed at the A/L level.</p>"

            return fallback

    def _format_ol_marks(self, ol_marks: Optional[Dict]) -> str:
        """Format O/L marks for display in prompt."""
        if not ol_marks or not ol_marks.get("core"):
            return "No marks provided"

        core = ol_marks.get("core", {})
        lines = []
        for subject, grade in core.items():
            if grade and subject not in [
                "bucket_1_grade",
                "bucket_2_grade",
                "bucket_3_grade",
            ]:
                lines.append(f"- {subject.replace('_', ' ').title()}: {grade}")

        return "\n".join(lines) if lines else "No marks provided"
