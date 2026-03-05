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

    def _call_gemini_api(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Generic method to call Gemini API with any prompt.

        Args:
            prompt: The prompt to send to Gemini
            max_tokens: Maximum tokens in response

        Returns:
            Response text from Gemini

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                ),
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")

    # ========== Dream vs. Reality Explanation Methods ==========

    def generate_al_explanation(
        self,
        student_input: str,
        reality_course: CourseRecommendation,
        is_mismatch: bool,
        dream_course: Optional[CourseRecommendation] = None,
    ) -> str:
        """
        Generate explanation for A/L students with dream vs. reality awareness.

        Args:
            student_input: Student's expressed interests
            reality_course: Top eligible course (what they CAN study)
            is_mismatch: Whether their dream differs from reality
            dream_course: Top interest match (what they WANT to study) if mismatch

        Returns:
            Personalized explanation string
        """
        if is_mismatch and dream_course:
            prompt = f"""
Act as a compassionate Sri Lankan University Career Counselor.

STUDENT CONTEXT:
- The student's interest is: "{student_input}"
- Their #1 interest aligns with: {dream_course.course_name} ({dream_course.stream} stream)
- However, their A/L results make them INELIGIBLE for that degree
- Based on STRICT eligibility, we recommend: {reality_course.course_name} ({reality_course.stream} stream)

TASK:
Write a 3-sentence explanation (max 80 words):
1. ACKNOWLEDGE: Gently recognize their interest in {dream_course.course_name}
2. REALITY: Explain why their A/L stream/scores don't allow that path
3. ALTERNATIVE: Show how {reality_course.course_name} is still a valuable choice that:
   - Incorporates some of their interests
   - Opens realistic career paths: {', '.join(reality_course.job_roles[:3])}
   - Builds on their actual strengths

TONE: Empathetic but honest. Avoid phrases like "unfortunately" or "sadly".
Focus on the POSITIVE aspects of the alternative.
"""
        else:
            prompt = f"""
Act as a Sri Lankan University Career Counselor.

STUDENT CONTEXT:
- The student's interest is: "{student_input}"
- We are recommending (strictly eligible): {reality_course.course_name} ({reality_course.stream} stream)
- This is a STRONG match for both their interests AND eligibility

TASK:
Write a 2-sentence explanation (max 60 words):
1. Explain why this course fits their interests
2. Highlight the career paths it opens: {', '.join(reality_course.job_roles[:3])}

TONE: Encouraging and confident.
"""

        try:
            return self._call_gemini_api(prompt, max_tokens=150)
        except Exception as e:
            # Fallback explanation
            if is_mismatch and dream_course:
                return (
                    f"While your interests align with {dream_course.course_name}, "
                    f"your A/L profile makes you eligible for {reality_course.course_name}. "
                    f"This program still offers strong career paths in {', '.join(reality_course.job_roles[:2])}."
                )
            else:
                return (
                    f"{reality_course.course_name} is an excellent match for your interests. "
                    f"It prepares you for careers in {', '.join(reality_course.job_roles[:2])}."
                )

    def generate_ol_explanation(
        self,
        student_input: str,
        top_course: CourseRecommendation,
        suggested_stream: str,
    ) -> str:
        """
        Generate explanation for O/L students with stream guidance.

        Args:
            student_input: Student's expressed interests
            top_course: Top recommended course to aim for
            suggested_stream: A/L stream needed for that course

        Returns:
            Personalized explanation with stream guidance
        """
        prompt = f"""
Act as a Sri Lankan University Career Counselor speaking to an O/L student.

STUDENT CONTEXT:
- The student's interest is: "{student_input}"
- Based on this, their dream degree is: {top_course.course_name}
- To qualify, they need to choose: {suggested_stream} stream at A/L

TASK:
Write a 3-sentence explanation (max 80 words):
1. Connect their interests to {top_course.course_name}
2. Recommend the {suggested_stream} stream as their path
3. Mention O/L subjects they should focus on (especially Math/Science if needed)

TONE: Motivational and forward-looking. This is their chance to shape their future.
"""

        try:
            return self._call_gemini_api(prompt, max_tokens=150)
        except Exception as e:
            return (
                f"Your interests in '{student_input}' align well with {top_course.course_name}. "
                f"To pursue this path, you should select the {suggested_stream} stream at A/L. "
                f"Focus on building a strong foundation in your O/L subjects, especially Math and Science."
            )
