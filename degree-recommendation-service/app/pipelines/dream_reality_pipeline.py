# app/pipelines/dream_reality_pipeline.py
"""
Dream vs. Reality Architecture Pipeline

Separates O/L and A/L recommendation flows:
- O/L Pipeline: Interest-first, suggests matching A/L stream
- A/L Pipeline: Hard eligibility filtering first, graceful dream-vs-reality handling

This solves the "Arts student wanting Software Engineering" problem by ensuring
A/L students ONLY see eligible courses, but system acknowledges their interests.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np

from app.domain.student import StudentProfile
from app.domain.course_recommendation import CourseRecommendation
from app.engines.rules_engine import check_eligibility
from app.engines.hybrid_similarity_engine import HybridSimilarityEngine
from app.repositories.program_repository import ProgramRepository


class DreamRealityPipeline:
    """
    Orchestrates recommendations with clear separation between:
    1. O/L students (dream-first)
    2. A/L students (reality-first with dream acknowledgment)
    """

    def __init__(
        self,
        semantic_weight: float = 0.7,
        tfidf_weight: float = 0.3,
        use_career_mapping: bool = True,
    ):
        """
        Initialize pipeline with hybrid search engine.

        Args:
            semantic_weight: Weight for semantic similarity (0-1)
            tfidf_weight: Weight for TF-IDF keyword matching (0-1)
            use_career_mapping: Enable career-to-degree query expansion
        """
        self.program_repo = ProgramRepository()
        self.hybrid_engine = HybridSimilarityEngine(
            semantic_weight=semantic_weight,
            tfidf_weight=tfidf_weight,
            use_career_mapping=use_career_mapping,
        )

    def recommend(
        self,
        student: StudentProfile,
        district: str,
        is_al_student: bool,
        max_results: int = 5,
    ) -> Dict:
        """
        Main entry point for recommendations.

        Args:
            student: StudentProfile with stream, subjects, zscore, interests
            district: Student's district (for cutoff scores)
            is_al_student: True if student has completed A/L, False if O/L
            max_results: Maximum courses to return

        Returns:
            Dictionary with recommendations and metadata
        """
        all_courses = self._load_courses()

        if is_al_student:
            return self._recommend_al_pipeline(
                student, district, all_courses, max_results
            )
        else:
            return self._recommend_ol_pipeline(student, all_courses, max_results)

    def _load_courses(self) -> List[CourseRecommendation]:
        """Load all courses and convert to CourseRecommendation objects."""
        programs = self.program_repo.get_all_programs()
        courses = []

        for program in programs:
            course = CourseRecommendation(
                course_code=program.course_code,
                course_name=program.course_name,
                stream=program.stream or "",
                interests=program.metadata.get("interests", []),
                job_roles=program.metadata.get("job_roles", []),
                core_skills=program.metadata.get("core_skills", []),
                industries=program.metadata.get("industries", []),
                metadata={
                    "universities": program.universities,
                    "subject_requirements": program.subject_requirements or [],
                },
            )
            courses.append(course)

        return courses

    def _recommend_ol_pipeline(
        self,
        student: StudentProfile,
        all_courses: List[CourseRecommendation],
        max_results: int,
    ) -> Dict:
        """
        Phase 1: O/L Pipeline (Dream-First)

        For O/L students, world is open. Prioritize interests.

        Flow:
        1. Rank ALL courses by interest match
        2. Extract required A/L stream from top match
        3. Suggest that stream as their "path to dream"
        4. Check O/L eligibility rules (future enhancement)

        Args:
            student: O/L student profile
            all_courses: Full course database
            max_results: Top N courses to return

        Returns:
            Dictionary with dream courses and suggested A/L stream
        """
        # Step 1: Rank all courses by interest
        ranked_courses = self.hybrid_engine.rank_courses_by_interest(
            student.interests,
            all_courses,
        )

        # Step 2: Get top match
        top_course, top_score = ranked_courses[0] if ranked_courses else (None, 0.0)

        # Step 3: Extract suggested stream
        suggested_stream = top_course.stream if top_course else "General"

        # Step 4: Prepare recommendations
        recommendations = []
        for course, score in ranked_courses[:max_results]:
            recommendations.append(
                {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "stream": course.stream,
                    "required_subjects": course.metadata.get(
                        "subject_requirements", []
                    ),
                    "universities": course.metadata.get("universities", []),
                    "match_score": round(score, 4),
                    "career_paths": course.job_roles[:5],
                }
            )

        return {
            "pipeline_type": "ol_dream_first",
            "recommended_stream": suggested_stream,
            "top_dream_course": top_course.course_name if top_course else None,
            "recommendations": recommendations,
            "explanation_context": {
                "student_interests": student.interests,
                "suggested_path": f"To pursue {top_course.course_name if top_course else 'your interests'}, focus on the {suggested_stream} stream at A/L.",
            },
        }

    def _recommend_al_pipeline(
        self,
        student: StudentProfile,
        district: str,
        all_courses: List[CourseRecommendation],
        max_results: int,
    ) -> Dict:
        """
        Phase 2: A/L Pipeline (Reality-First with Dream Acknowledgment)

        For A/L students, rules are locked. Prioritize eligibility.

        Flow:
        1. HARD FILTER: Check eligibility on all 126 courses
        2. Rank ONLY eligible courses (Reality)
        3. Silently rank ALL courses to find dream
        4. Detect mismatch (dream != reality)
        5. Flag for explanation engine

        Args:
            student: A/L student profile with stream + zscore
            district: Student's district
            all_courses: Full course database
            max_results: Top N courses to return

        Returns:
            Dictionary with reality recommendations + mismatch metadata
        """
        # Step 1: HARD FILTERING - Get strictly eligible courses
        eligible_courses = []
        eligibility_metadata = {}

        programs = self.program_repo.get_all_programs()

        for idx, course in enumerate(all_courses):
            program = programs[idx]  # Assumes same order
            is_eligible, reason, details = check_eligibility(student, program, district)

            eligibility_metadata[course.course_code] = {
                "is_eligible": is_eligible,
                "reason": reason,
                "details": details,
            }

            if is_eligible:
                eligible_courses.append(course)

        print(
            f"[OK] Hard filtering: {len(eligible_courses)}/{len(all_courses)} courses eligible"
        )

        # Step 2: REALITY RANKING - Rank only eligible courses by INTEREST
        if not eligible_courses:
            return self._handle_no_eligible_courses(
                student, all_courses, eligibility_metadata
            )

        # Rank eligible courses by interest matching
        interest_rankings = self.hybrid_engine.rank_courses_by_interest(
            student.interests,
            eligible_courses,
        )

        # Step 3: DREAM CHECK - What did they actually want?
        dream_rankings = self.hybrid_engine.rank_courses_by_interest(
            student.interests,
            all_courses,
        )

        # Step 4: MISMATCH DETECTION
        top_interest_course, interest_score = (
            interest_rankings[0] if interest_rankings else (None, 0.0)
        )
        top_dream_course, dream_score = (
            dream_rankings[0] if dream_rankings else (None, 0.0)
        )

        is_mismatch = (
            top_dream_course
            and top_interest_course
            and top_dream_course.course_code != top_interest_course.course_code
            and not eligibility_metadata[top_dream_course.course_code]["is_eligible"]
        )

        # ===== NEW: Build ALL_ELIGIBLE courses (Results-based ranking) =====
        all_eligible = []
        for course in eligible_courses:
            metadata = eligibility_metadata.get(course.course_code, {})
            all_eligible.append(
                {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "stream": course.stream,
                    "required_subjects": course.metadata.get(
                        "subject_requirements", []
                    ),
                    "universities": course.metadata.get("universities", []),
                    "career_paths": course.job_roles[:5],
                    "eligibility_status": "ELIGIBLE",
                    "eligibility_reason": metadata.get("reason", ""),
                }
            )

        # ===== NEW: Build INTEREST-FILTERED courses (Interest-based ranking) =====
        recommendations = []
        for course, score in interest_rankings[:max_results]:
            metadata = eligibility_metadata.get(course.course_code, {})
            recommendations.append(
                {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "stream": course.stream,
                    "required_subjects": course.metadata.get(
                        "subject_requirements", []
                    ),
                    "universities": course.metadata.get("universities", []),
                    "interest_match_score": round(score, 4),
                    "career_paths": course.job_roles[:5],
                    "eligibility_status": "ELIGIBLE",
                    "eligibility_reason": metadata.get("reason", ""),
                }
            )

        # Build result with BOTH all_eligible and interest_filtered recommendations
        result = {
            "pipeline_type": "al_results_first_with_interests",
            "all_eligible_courses": all_eligible,  # All eligible courses (results-ranked)
            "recommendations": recommendations,  # Interest-filtered subset (interest-ranked)
            "eligible_count": len(eligible_courses),
            "has_mismatch": is_mismatch,
            "explanation_context": {
                "student_interests": student.interests,
                "student_stream": student.stream,
                "student_zscore": student.zscore,
                "eligible_count": len(eligible_courses),
                "total_courses": len(all_courses),
            },
        }

        if is_mismatch and top_dream_course:
            result["dream_course"] = {
                "course_code": top_dream_course.course_code,
                "course_name": top_dream_course.course_name,
                "stream": top_dream_course.stream,
                "interest_score": round(dream_score, 4),
                "ineligibility_reason": eligibility_metadata[
                    top_dream_course.course_code
                ].get("reason", ""),
            }
            result["explanation_context"]["mismatch_detected"] = True
            result["explanation_context"]["why_not_eligible"] = (
                f"You're interested in {top_dream_course.course_name} ({top_dream_course.stream}), "
                f"but your stream ({student.stream}) with Z-score {student.zscore:.2f} "
                f"doesn't meet the requirements for that program."
            )
        else:
            result["explanation_context"]["mismatch_detected"] = False

        return result

    def _handle_no_eligible_courses(
        self,
        student: StudentProfile,
        all_courses: List[CourseRecommendation],
        eligibility_metadata: Dict,
    ) -> Dict:
        """
        Handle edge case where student has NO eligible courses.

        Could happen if:
        - Z-score too low for all courses
        - Stream has no matching courses
        - Subjects don't meet any requirements

        Args:
            student: Student profile
            all_courses: Full database
            eligibility_metadata: Eligibility check results

        Returns:
            Dictionary with aspirational courses and guidance
        """
        # Find top interest matches regardless of eligibility
        dream_rankings = self.hybrid_engine.rank_courses_by_interest(
            student.interests,
            all_courses,
        )

        # Get rejection reasons for top matches
        aspirational = []
        for course, score in dream_rankings[:5]:
            metadata = eligibility_metadata.get(course.course_code, {})
            aspirational.append(
                {
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "stream": course.stream,
                    "match_score": round(score, 4),
                    "ineligibility_reason": metadata.get("reason", "Unknown"),
                }
            )

        return {
            "pipeline_type": "al_no_eligible_courses",
            "recommendations": [],
            "aspirational_courses": aspirational,
            "explanation_context": {
                "student_interests": student.interests,
                "student_stream": student.stream,
                "student_zscore": student.zscore,
                "no_eligible_courses": True,
                "guidance": (
                    "Unfortunately, your current profile does not meet the eligibility "
                    "requirements for any state university courses. Consider: (1) Re-sitting "
                    "A/L exams to improve Z-score, (2) Exploring private universities or "
                    "vocational training, (3) Consulting a career counselor for alternative paths."
                ),
            },
        }

    def filter_courses_by_similarity(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
        min_similarity: float = 0.3,
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Filter and rank courses by similarity score.

        Args:
            student_input: Student's interests/skills
            courses: List of courses to filter
            min_similarity: Minimum similarity threshold

        Returns:
            Filtered and sorted list of (course, score) tuples
        """
        ranked = self.hybrid_engine.rank_courses_by_interest(student_input, courses)
        return [(course, score) for course, score in ranked if score >= min_similarity]
