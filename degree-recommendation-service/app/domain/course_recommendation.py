# app/domain/course_recommendation.py
from __future__ import annotations
from typing import Any, Dict, List, Optional


class CourseRecommendation:
    """Represents a course with interest, skill, and job role metadata for recommendation matching."""

    def __init__(
        self,
        course_code: str,
        course_name: str,
        stream: str,
        interests: List[str],
        job_roles: List[str],
        industries: List[str],
        core_skills: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.course_code = course_code
        self.course_name = course_name
        self.stream = stream
        self.interests = interests or []
        self.job_roles = job_roles or []
        self.industries = industries or []
        self.core_skills = core_skills or []
        self.metadata = metadata or {}

    @classmethod
    def from_csv(cls, row: Dict[str, str]) -> CourseRecommendation:
        """Create a CourseRecommendation instance from a CSV row."""
        # Normalize keys
        normalized_row = {
            (str(k).lstrip("\ufeff").strip() if k is not None else ""): (
                v or ""
            ).strip()
            for k, v in row.items()
        }

        # Parse comma-separated fields
        def parse_csv_field(value: str) -> List[str]:
            """Parse comma-separated strings into a list, filtering out empty strings."""
            if not value:
                return []
            return [item.strip() for item in value.split(",") if item.strip()]

        return cls(
            course_code=normalized_row.get("Course Code", ""),
            course_name=normalized_row.get("Course Name", ""),
            stream=normalized_row.get("Stream", ""),
            interests=parse_csv_field(normalized_row.get("Interests", "")),
            job_roles=parse_csv_field(normalized_row.get("Job Roles", "")),
            industries=parse_csv_field(normalized_row.get("Industries", "")),
            core_skills=parse_csv_field(normalized_row.get("Core Skills", "")),
        )

    def get_combined_text(self) -> str:
        """
        Get combined text representation of interests, roles, industries, and skills.
        Used for semantic embedding in similarity matching.
        """
        text_parts = [
            self.course_name,
            ", ".join(self.interests),
            ", ".join(self.job_roles),
            ", ".join(self.industries),
            ", ".join(self.core_skills),
        ]
        return " | ".join([part for part in text_parts if part])

    def __repr__(self) -> str:
        return f"CourseRecommendation(code={self.course_code}, name={self.course_name}, stream={self.stream})"
