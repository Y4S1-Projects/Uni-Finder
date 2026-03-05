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

    def get_weighted_text(self) -> str:
        """
        Get weighted text representation that boosts important career-relevant fields.

        Phase 3: Weighted Corpus Construction
        By repeating high-value columns (Job Roles, Core Skills), we mathematically
        force the embedding model to pay more attention to career outcomes.

        Example:
        Bad:  "Computer Science. Software Engineer. Coding"
        Good: "Computer Science. Software Engineer, Software Engineer, Tech Lead.
               Coding, Big Data, Big Data, AI, AI"

        Returns:
            Weighted text string for enhanced semantic matching
        """
        parts = []

        # Course name (weight: 2x) - Important for direct matches
        if self.course_name:
            parts.append(f"Degree: {self.course_name}")
            parts.append(self.course_name)  # Repeat once

        # Job roles (weight: 3x) - MOST IMPORTANT for career mapping
        if self.job_roles:
            roles_text = ", ".join(self.job_roles)
            parts.append(f"Careers: {roles_text}")
            parts.append(roles_text)  # Repeat 1st time
            parts.append(roles_text)  # Repeat 2nd time

        # Core skills (weight: 2x) - Important for technical matching
        if self.core_skills:
            skills_text = ", ".join(self.core_skills)
            parts.append(f"Skills: {skills_text}")
            parts.append(skills_text)  # Repeat once

        # Interests (weight: 1x) - Baseline importance
        if self.interests:
            parts.append(f"Interests: {', '.join(self.interests)}")

        # Industries (weight: 1x) - Context
        if self.industries:
            parts.append(f"Industries: {', '.join(self.industries)}")

        # Stream (weight: 1x) - Categorical info
        if self.stream:
            parts.append(f"Stream: {self.stream}")

        return ". ".join(parts)

    def __repr__(self) -> str:
        return f"CourseRecommendation(code={self.course_code}, name={self.course_name}, stream={self.stream})"
