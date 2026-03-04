# app/engines/explanation_engine.py
"""
Explanation Engine - Generates personalized explanations for course recommendations.

Uses Google Gemini API to create human-readable explanations of why specific courses
are recommended based on student interests and skills.
"""

import re
from typing import List, Optional
from difflib import SequenceMatcher

import google.generativeai as genai

from app.core.config import settings
from app.domain.course_recommendation import CourseRecommendation


class ExplanationEngine:
    """
    Generates personalized explanations for course recommendations using Gemini API.
    Optimized for single API call per search session (15 RPM free tier limitation).
    """

    def __init__(self):
        """Initialize Gemini API client."""
        if not settings.GOOGLE_GEMINI_API_KEY:
            raise ValueError(
                "GOOGLE_GEMINI_API_KEY is not set in .env file. "
                "Please add your Gemini API key to proceed."
            )
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def extract_overlapping_keywords(
        self,
        student_input: str,
        course: CourseRecommendation,
        max_keywords: int = 10,
    ) -> List[str]:
        """
        Extract keywords/interests that overlap between student input and course data.

        Args:
            student_input: Student's expressed interests/skills
            course: CourseRecommendation object with interests, skills, roles
            max_keywords: Maximum number of keywords to extract

        Returns:
            List of overlapping keywords
        """
        # Prepare all course-related keywords for matching
        course_keywords = set()
        course_keywords.update(course.interests)
        course_keywords.update(course.job_roles)
        course_keywords.update(course.core_skills)

        # Normalize for comparison
        student_input_lower = student_input.lower()
        overlapping = []

        for keyword in course_keywords:
            keyword_lower = keyword.lower()
            # Check for exact match or substring match
            if keyword_lower in student_input_lower or self._is_similar(
                student_input_lower, keyword_lower
            ):
                overlapping.append(keyword)

        # Return top matches
        return overlapping[:max_keywords]

    def _is_similar(self, str1: str, str2: str, threshold: float = 0.6) -> bool:
        """
        Check if two strings are similar using SequenceMatcher.

        Args:
            str1: First string
            str2: Second string
            threshold: Similarity threshold (0-1)

        Returns:
            True if strings are similar above threshold
        """
        ratio = SequenceMatcher(None, str1, str2).ratio()
        return ratio >= threshold

    def generate_explanations(
        self,
        student_input: str,
        ranked_courses: List[tuple[CourseRecommendation, float]],
        max_courses: int = 5,
    ) -> dict:
        """
        Generate personalized explanations for top recommended courses.

        Args:
            student_input: Student's interests/skills description
            ranked_courses: List of (CourseRecommendation, similarity_score) tuples
            max_courses: Maximum number of courses to explain

        Returns:
            Dictionary with course codes mapped to explanations
        """
        # Limit to top courses
        top_courses = ranked_courses[:max_courses]

        # Extract overlapping keywords for each course
        keyword_map = {}
        for course, score in top_courses:
            keywords = self.extract_overlapping_keywords(student_input, course)
            keyword_map[course.course_code] = {
                "keywords": keywords,
                "score": score,
                "course": course,
            }

        # Batch all explanations in single API call to respect rate limits
        explanations = self._call_gemini_batch(student_input, keyword_map)

        return explanations

    def _call_gemini_batch(self, student_input: str, keyword_map: dict) -> dict:
        """
        Call Gemini API once with batch explanation request.

        Args:
            student_input: Student's interests/skills
            keyword_map: Dict mapping course codes to keywords and metadata

        Returns:
            Dictionary with course codes mapped to explanations
        """
        # Build comprehensive prompt for all courses at once
        course_details = []
        for course_code, data in keyword_map.items():
            course = data["course"]
            score = data["score"]
            keywords = data["keywords"]

            course_details.append(
                f"""
Course: {course.course_name} (Code: {course.course_code})
Stream: {course.stream}
Match Score: {score:.1%}
Matched Interests: {', '.join(keywords) if keywords else 'General alignment'}
Course Specializations: {', '.join(course.interests[:5]) if course.interests else 'N/A'}
Career Paths: {', '.join(course.job_roles[:5]) if course.job_roles else 'N/A'}
"""
            )

        prompt = f"""You are an educational career advisor. Generate concise, personalized explanations for why these courses match a student's interests.

Student Profile: {student_input}

Recommended Courses:
{''.join(course_details)}

For each course, provide a brief 2-3 sentence explanation (max 100 words) that:
1. Highlights specific matched interests/skills
2. Explains career relevance
3. Makes the recommendation feel personalized

Format your response as:
COURSE-CODE: <explanation>

Be encouraging and specific. Avoid generic phrases."""

        try:
            response = self.model.generate_content(prompt)
            explanations_dict = self._parse_gemini_response(
                response.text, list(keyword_map.keys())
            )
            return explanations_dict
        except Exception as e:
            # Fallback: generate simple explanations if API fails
            print(f"Warning: Gemini API error: {e}")
            return self._fallback_explanations(keyword_map)

    def _parse_gemini_response(
        self, response_text: str, course_codes: List[str]
    ) -> dict:
        """
        Parse Gemini API response into dictionary of explanations.

        Args:
            response_text: Raw text response from Gemini
            course_codes: List of expected course codes

        Returns:
            Dictionary mapping course codes to explanations
        """
        explanations = {}

        # Split by course codes
        for course_code in course_codes:
            pattern = rf"{course_code}:\s*(.+?)(?={course_codes[-1] if course_code == course_codes[-1] else '(?:[0-9]+:)|$'})"
            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
            if match:
                explanation = match.group(1).strip()
                # Clean up extra whitespace
                explanation = " ".join(explanation.split())
                explanations[course_code] = explanation
            else:
                # Fallback if parsing fails
                explanations[course_code] = (
                    "This course aligns well with your interests and career goals."
                )

        return explanations

    def _fallback_explanations(self, keyword_map: dict) -> dict:
        """
        Generate fallback explanations if Gemini API is unavailable.

        Args:
            keyword_map: Dict mapping course codes to keywords and metadata

        Returns:
            Dictionary with simple explanations
        """
        explanations = {}
        for course_code, data in keyword_map.items():
            course = data["course"]
            keywords = data["keywords"]

            if keywords:
                explanation = (
                    f"This course matches your interests in {', '.join(keywords[:3])}. "
                    f"It prepares you for careers in {', '.join(course.job_roles[:2] if course.job_roles else ['relevant fields'])}."
                )
            else:
                explanation = (
                    f"This {course.stream} program aligns with your academic profile "
                    f"and opens paths to {', '.join(course.job_roles[:2] if course.job_roles else ['diverse careers'])}."
                )

            explanations[course_code] = explanation

        return explanations
