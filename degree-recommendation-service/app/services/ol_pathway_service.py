"""
O/L to A/L Stream Pathway Recommendation Service

This service helps O/L students discover their optimal A/L stream and target degrees
based on their interests/career goals and current O/L subject marks.

Pipeline:
1. Semantic Career/Interest Matching → Find target degrees
2. A/L Stream Extraction → Identify required A/L stream
3. O/L Marks Analysis → Compare marks against stream requirements
4. Explainable AI Guidance → Generate personalized explanation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter

from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine
from app.schemas.request import OLPathwayRequest
from app.schemas.response import (
    OLPathwayResponse,
    SubjectAnalysis,
    TargetDegree,
)

logger = logging.getLogger(__name__)


class OLPathwayService:
    """Service for O/L to A/L stream pathway recommendations."""

    def __init__(
        self,
        course_repo: CourseRecommendationRepository,
        similarity_engine: SimilarityEngine,
        explanation_engine: ExplanationEngine,
    ):
        self.course_repo = course_repo
        self.similarity_engine = similarity_engine
        self.explanation_engine = explanation_engine
        self.stream_rules = self._load_stream_rules()

    def _load_stream_rules(self) -> dict:
        """Load O/L stream rules from JSON configuration."""
        rules_path = (
            Path(__file__).parent.parent.parent / "data" / "ol_stream_rules.json"
        )
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _grade_to_numeric(self, grade: str) -> int:
        """Convert letter grade to numeric value."""
        return self.stream_rules["grade_mappings"].get(grade.upper(), 0)

    def get_ol_pathway_recommendation(
        self, request: OLPathwayRequest
    ) -> OLPathwayResponse:
        """
        Get O/L to A/L stream pathway recommendation.

        Args:
            request: OLPathwayRequest with student input and O/L marks

        Returns:
            OLPathwayResponse with recommended stream, degrees, and analysis
        """
        logger.info(
            f"Processing O/L pathway request for input: {request.student_input[:50]}..."
        )

        # Step 1: Semantic Career/Interest Matching
        target_degrees = self._find_target_degrees(
            request.student_input, request.max_degree_results
        )

        # Step 2: A/L Stream Extraction
        recommended_stream, stream_confidence = self._extract_recommended_stream(
            target_degrees
        )

        # Step 3: O/L Marks Analysis
        subject_analysis = self._analyze_ol_marks(request.ol_marks, recommended_stream)
        overall_readiness = self._calculate_overall_readiness(subject_analysis)

        # Step 4: Explainable AI Guidance
        if request.explain:
            explanation, action_plan = self._generate_explanation(
                student_input=request.student_input,
                recommended_stream=recommended_stream,
                target_degrees=target_degrees,
                subject_analysis=subject_analysis,
                overall_readiness=overall_readiness,
            )
        else:
            explanation = "Explanation generation disabled."
            action_plan = []

        return OLPathwayResponse(
            student_input=request.student_input,
            recommended_al_stream=recommended_stream,
            stream_description=self.stream_rules[recommended_stream]["description"],
            stream_match_confidence=stream_confidence,
            target_degrees=target_degrees,
            subject_analysis=subject_analysis,
            overall_readiness=overall_readiness,
            explanation=explanation,
            action_plan=action_plan,
        )

    def _find_target_degrees(
        self, student_input: str, max_results: int
    ) -> List[TargetDegree]:
        """Find target degrees using semantic matching."""
        logger.info("Step 1: Finding target degrees using semantic matching")

        # Get all courses
        all_courses = self.course_repo.get_all_courses()

        # Rank courses by semantic similarity
        ranked_courses = self.similarity_engine.rank_courses_by_interest(
            student_input=student_input,
            courses=all_courses,
        )

        # Take top N results
        target_degrees = []
        for course, score in ranked_courses[:max_results]:
            target_degrees.append(
                TargetDegree(
                    course_code=course.course_code,
                    course_name=course.course_name,
                    stream=course.stream,
                    match_score_percentage=round(score * 100, 1),
                    job_roles=course.job_roles,
                    industries=course.industries,
                )
            )

        logger.info(f"Found {len(target_degrees)} target degrees")
        return target_degrees

    def _extract_recommended_stream(
        self, target_degrees: List[TargetDegree]
    ) -> Tuple[str, float]:
        """
        Extract recommended A/L stream from target degrees.

        Uses majority voting weighted by match scores.
        """
        logger.info("Step 2: Extracting recommended A/L stream")

        if not target_degrees:
            return "Arts", 50.0  # Default fallback

        # Weighted vote: each degree contributes its match score to its stream
        stream_scores = {}
        total_score = 0

        for degree in target_degrees:
            # Normalize stream names (handle multi-stream cases)
            stream = degree.stream
            original_stream = stream

            # Handle multi-stream courses by extracting first valid stream
            # Check for common patterns in stream notation
            if "Physical Science" in stream or "Phys" in stream:
                stream = "Physical Science"
            elif "Biological Science" in stream or "Bio" in stream:
                stream = "Biological Science"
            elif "Commerce" in stream:
                stream = "Commerce"
            elif "Technology" in stream or "Tech" in stream:
                stream = "Technology"
            elif "Arts" in stream:
                stream = "Arts"
            elif "any" in stream.lower() or "multi" in stream.lower():
                # For "any" or "multi" streams without specific mention, default to Physical Science
                stream = "Physical Science"

            score = degree.match_score_percentage
            stream_scores[stream] = stream_scores.get(stream, 0) + score
            total_score += score

            logger.debug(
                f"Degree {degree.course_code}: '{original_stream}' -> '{stream}' (score: {score})"
            )

        # Find stream with highest weighted score
        recommended_stream = max(stream_scores, key=stream_scores.get)
        confidence = (stream_scores[recommended_stream] / total_score) * 100

        logger.info(
            f"Recommended stream: {recommended_stream} (confidence: {confidence:.1f}%)"
        )
        logger.info(f"Stream score distribution: {stream_scores}")
        return recommended_stream, round(confidence, 1)

    def _analyze_ol_marks(
        self, ol_marks: Dict[str, str], stream: str
    ) -> List[SubjectAnalysis]:
        """Analyze O/L marks against stream requirements."""
        logger.info(f"Step 3: Analyzing O/L marks for {stream} stream")

        stream_config = self.stream_rules.get(stream, {})
        core_subjects = stream_config.get("core_subjects", [])
        min_requirements = stream_config.get("minimum_requirement", {})
        ideal_scores = stream_config.get("ideal_score", {})

        analysis = []

        # Analyze core subjects
        for subject in core_subjects:
            student_grade = ol_marks.get(subject, "N/A")
            required_grade = min_requirements.get(subject)
            ideal_grade = ideal_scores.get(subject)

            if student_grade == "N/A":
                # Only mark as critical if there's an actual minimum requirement
                if required_grade:
                    analysis.append(
                        SubjectAnalysis(
                            subject=subject,
                            student_grade="N/A",
                            required_grade=required_grade,
                            ideal_grade=ideal_grade,
                            meets_requirement=False,
                            status="critical",
                            feedback=f"Missing {subject} mark. This subject is required for {stream} stream (minimum: {required_grade}).",
                        )
                    )
                else:
                    # No specific requirement, so missing is less critical
                    analysis.append(
                        SubjectAnalysis(
                            subject=subject,
                            student_grade="N/A",
                            required_grade=required_grade,
                            ideal_grade=ideal_grade,
                            meets_requirement=True,  # No hard requirement
                            status="needs_improvement",
                            feedback=f"{subject} is recommended for {stream} stream. Consider strengthening this area.",
                        )
                    )
                continue

            student_numeric = self._grade_to_numeric(student_grade)
            meets_requirement = True

            if required_grade:
                required_numeric = self._grade_to_numeric(required_grade)
                meets_requirement = student_numeric >= required_numeric

            # Determine status
            if ideal_grade:
                ideal_numeric = self._grade_to_numeric(ideal_grade)
                if student_numeric >= ideal_numeric:
                    status = "excellent"
                    feedback = f"Outstanding! Your {subject} grade is at or above the ideal level."
                elif student_numeric >= ideal_numeric - 1:
                    status = "good"
                    feedback = f"Good performance in {subject}. You're well-prepared for {stream}."
                elif meets_requirement:
                    status = "adequate"
                    feedback = f"You meet the minimum for {subject}, but strengthening this area would help."
                else:
                    status = "needs_improvement"
                    feedback = f"Your {subject} grade is below the minimum. Focus on improving this subject."
            else:
                if student_numeric >= 8:  # B or better
                    status = "excellent"
                    feedback = f"Strong performance in {subject}."
                elif student_numeric >= 7:  # C
                    status = "good"
                    feedback = f"Satisfactory performance in {subject}."
                elif student_numeric >= 6:  # S
                    status = "adequate"
                    feedback = (
                        f"Basic level in {subject}. Consider strengthening this area."
                    )
                else:
                    status = "needs_improvement"
                    feedback = f"Weak performance in {subject}. Improvement needed."

            if not meets_requirement:
                status = "critical"

            analysis.append(
                SubjectAnalysis(
                    subject=subject,
                    student_grade=student_grade,
                    required_grade=required_grade,
                    ideal_grade=ideal_grade,
                    meets_requirement=meets_requirement,
                    status=status,
                    feedback=feedback,
                )
            )

        logger.info(f"Analyzed {len(analysis)} core subjects")
        return analysis

    def _calculate_overall_readiness(
        self, subject_analysis: List[SubjectAnalysis]
    ) -> str:
        """Calculate overall readiness for the stream."""
        if not subject_analysis:
            return "adequate"

        status_counts = Counter([s.status for s in subject_analysis])

        # Check for critical issues
        if status_counts["critical"] > 0:
            return "needs_improvement"

        # Calculate readiness based on status distribution
        excellent_count = status_counts["excellent"]
        good_count = status_counts["good"]
        needs_improvement_count = status_counts["needs_improvement"]

        total = len(subject_analysis)

        if excellent_count >= total * 0.6:
            return "excellent"
        elif (excellent_count + good_count) >= total * 0.6:
            return "good"
        elif needs_improvement_count > total * 0.4:
            return "needs_improvement"
        else:
            return "adequate"

    def _generate_explanation(
        self,
        student_input: str,
        recommended_stream: str,
        target_degrees: List[TargetDegree],
        subject_analysis: List[SubjectAnalysis],
        overall_readiness: str,
    ) -> Tuple[str, List[str]]:
        """Generate personalized explanation using Gemini API."""
        logger.info("Step 4: Generating personalized explanation")

        # Build context for Gemini
        top_degrees = target_degrees[:3]
        degree_names = [d.course_name for d in top_degrees]
        job_roles = []
        for d in top_degrees:
            job_roles.extend(d.job_roles)
        job_roles = list(set(job_roles))[:5]

        # Identify weak subjects
        weak_subjects = [
            s.subject
            for s in subject_analysis
            if s.status in ["needs_improvement", "critical"]
        ]
        strong_subjects = [
            s.subject for s in subject_analysis if s.status == "excellent"
        ]

        prompt = f"""You are a caring Sri Lankan career counselor speaking to an O/L student.

Student's Career Interest: "{student_input}"

Based on their interests, the best career path leads to these degrees:
{', '.join(degree_names)}

These degrees require the A/L {recommended_stream} stream.

O/L Subject Analysis:
- Strong subjects: {', '.join(strong_subjects) if strong_subjects else 'None identified'}
- Subjects needing improvement: {', '.join(weak_subjects) if weak_subjects else 'None'}
- Overall readiness: {overall_readiness}

Target careers: {', '.join(job_roles)}

Write a warm, encouraging 4-5 sentence explanation that:
1. Affirms their career choice matches well with {recommended_stream}
2. Highlights their strengths
3. Honestly addresses any weak subjects (if any) with actionable advice
4. Motivates them about the career opportunities ahead

Then provide 3-4 specific action items they should take to prepare for A/L {recommended_stream}.

Format your response as:
EXPLANATION:
[Your explanation here]

ACTION_PLAN:
- [Action item 1]
- [Action item 2]
- [Action item 3]
- [Action item 4 if needed]
"""

        try:
            # Call Gemini API
            gemini_response = self.explanation_engine._call_gemini_api(
                prompt, max_tokens=500
            )

            # Parse response
            if "EXPLANATION:" in gemini_response and "ACTION_PLAN:" in gemini_response:
                parts = gemini_response.split("ACTION_PLAN:")
                explanation = parts[0].replace("EXPLANATION:", "").strip()
                action_plan_text = parts[1].strip()

                # Parse action items
                action_plan = []
                for line in action_plan_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("•"):
                        action_plan.append(line[1:].strip())
                    elif line and not line.startswith("ACTION_PLAN"):
                        action_plan.append(line)

                return explanation, action_plan
            else:
                # Fallback if format is not as expected
                return gemini_response, []

        except Exception as e:
            logger.warning(f"Gemini API failed, using fallback explanation: {e}")
            return self._fallback_explanation(
                student_input,
                recommended_stream,
                target_degrees,
                weak_subjects,
                strong_subjects,
                overall_readiness,
            )

    def _fallback_explanation(
        self,
        student_input: str,
        stream: str,
        degrees: List[TargetDegree],
        weak_subjects: List[str],
        strong_subjects: List[str],
        readiness: str,
    ) -> Tuple[str, List[str]]:
        """Fallback explanation when Gemini API is unavailable."""
        top_degree = degrees[0] if degrees else None

        explanation = f"Based on your interest in '{student_input}', the A/L {stream} stream is the ideal pathway. "

        if top_degree:
            explanation += f"This will prepare you for {top_degree.course_name} and careers like {', '.join(top_degree.job_roles[:3])}. "

        if strong_subjects:
            explanation += f"Your strong performance in {', '.join(strong_subjects)} is a great foundation. "

        if weak_subjects:
            explanation += f"Focus on strengthening {', '.join(weak_subjects)} to ensure you're fully prepared for A/L {stream}. "

        if readiness == "excellent":
            explanation += "You're in an excellent position to excel in this stream!"
        elif readiness == "good":
            explanation += (
                "With some focused effort, you'll be well-prepared for this stream."
            )
        elif readiness == "needs_improvement":
            explanation += "You'll need to put in extra effort to strengthen your foundation, but it's definitely achievable."

        action_plan = [
            (
                f"Focus on improving {weak_subjects[0]} through extra classes or self-study"
                if weak_subjects
                else "Continue excelling in your current subjects"
            ),
            f"Research more about {stream} stream subjects and requirements",
            "Practice past papers for your weak subjects",
            f"Talk to seniors or teachers about careers in {', '.join(degrees[0].job_roles[:2]) if degrees else stream}",
        ]

        return explanation, action_plan
