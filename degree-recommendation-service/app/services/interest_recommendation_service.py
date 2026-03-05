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
    ) -> List[Dict]:
        """
        Get interest-based recommendations with 3-step pipeline.

        Args:
            student_input: Student's interests/skills description
            eligible_course_codes: Course codes from eligibility filtering
            max_results: Maximum number of recommendations to return
            explain: Whether to generate explanations (uses Gemini API)

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
                    student_input, ranked_courses, max_courses=len(top_courses)
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
