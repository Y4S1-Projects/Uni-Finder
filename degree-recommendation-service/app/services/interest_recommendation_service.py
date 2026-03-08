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
            pathway_summary.append(
                f"{p['stream_name']} ({p['match_score']:.0f}% match, {p['ol_readiness']})"
            )

        prompt = f"""You are an educational counselor advising a Sri Lankan O/L student about their A/L stream and career choices.

Student's Goal: {student_input}

Recommended Pathways (in order of match):
{chr(10).join('- ' + s for s in pathway_summary)}

O/L Performance Summary:
{self._format_ol_marks(ol_marks)}

Provide encouraging, actionable advice in 3-4 sentences that:
1. Identifies their BEST stream (the "golden path")
2. Acknowledges their O/L strengths
3. Points out any subject gaps they need to address
4. Motivates them with career outcomes

Be specific, warm, and empowering. Speak directly to the student."""

        try:
            import google.generativeai as genai
            from app.core.config import settings

            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback advice
            best_stream = pathways[0]["stream_name"] if pathways else "your top choice"
            return f"Your interests strongly align with {best_stream}. Focus on building your foundation in key subjects during your A/Levels, and you'll be well-prepared for your chosen career path!"

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
