# app/domain/program.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import hashlib


class DegreeProgram:
    """Represents a degree program from University_Courses_Dataset.csv"""

    def __init__(
        self,
        course_code: str,
        course_name: str,
        stream: str,
        universities: List[str],
        faculty_department: str,
        duration: str,
        degree_programme: str,
        subject_requirements: List[str],
        ol_requirements: Optional[str],
        practical_test: bool,
        proposed_intake: Optional[int],
        medium_of_instruction: str,
        notes: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.course_code = course_code
        self.course_name = course_name
        self.stream = stream
        self.universities = universities
        self.faculty_department = faculty_department
        self.duration = duration
        self.degree_programme = degree_programme
        self.subject_requirements = subject_requirements
        self.ol_requirements = ol_requirements
        self.practical_test = practical_test
        self.proposed_intake = proposed_intake
        self.medium_of_instruction = medium_of_instruction
        self.notes = notes
        self.metadata = metadata or {}

        # Legacy compatibility properties
        self.program_id = f"COURSE-{course_code}"
        self.degree_name = course_name
        self.subject_prerequisites = subject_requirements
        self.min_zscore = None  # Will be determined from cutoff data
        self.syllabus_summary = notes
        self.career_paths = []

    @classmethod
    def from_csv(cls, row: dict) -> "DegreeProgram":
        """
        Factory method to create DegreeProgram from University_Courses_Dataset.csv row.
        Column mapping:
        - Course Name -> course_name
        - Course Code -> course_code
        - Stream -> stream
        - Universities Offering Course -> universities (list)
        - Faculty / Department -> faculty_department
        - Duration -> duration
        - Degree Programme -> degree_programme
        - A/L Subject Requirements -> subject_requirements (list)
        - O/L Special Requirements -> ol_requirements
        - Practical / Aptitude Test -> practical_test (bool)
        - Proposed Intake -> proposed_intake (int)
        - Medium of Instruction -> medium_of_instruction
        - Notes -> notes
        """
        course_name = _clean_str(row.get("Course Name", ""))
        course_code = _clean_str(row.get("Course Code", ""))
        stream = _clean_str(row.get("Stream", ""))

        # Parse universities (semicolon-separated)
        universities_str = _clean_str(row.get("Universities Offering Course", ""))
        universities = (
            [uni.strip() for uni in universities_str.split(";") if uni.strip()]
            if universities_str
            else []
        )

        faculty_department = _clean_str(row.get("Faculty / Department", ""))
        duration = _clean_str(row.get("Duration", ""))
        degree_programme = _clean_str(row.get("Degree Programme", ""))

        # Parse subject requirements
        subject_req_str = _clean_str(row.get("A/L Subject Requirements", ""))
        subject_requirements = _parse_subject_requirements(subject_req_str)

        ol_requirements = _clean_str(row.get("O/L Special Requirements", "")) or None

        # Parse practical test requirement
        practical_str = _clean_str(row.get("Practical / Aptitude Test", "")).lower()
        practical_test = practical_str in ["yes", "true", "required"]

        # Parse proposed intake
        intake_str = _clean_str(row.get("Proposed Intake", ""))
        proposed_intake = _parse_int(intake_str)

        medium_of_instruction = _clean_str(row.get("Medium of Instruction", ""))
        notes = _clean_str(row.get("Notes", ""))

        # Store additional metadata
        metadata = {
            "raw_subject_requirements": subject_req_str,
            "raw_practical_test": row.get("Practical / Aptitude Test", ""),
        }

        return cls(
            course_code=course_code,
            course_name=course_name,
            stream=stream,
            universities=universities,
            faculty_department=faculty_department,
            duration=duration,
            degree_programme=degree_programme,
            subject_requirements=subject_requirements,
            ol_requirements=ol_requirements,
            practical_test=practical_test,
            proposed_intake=proposed_intake,
            medium_of_instruction=medium_of_instruction,
            notes=notes,
            metadata=metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "course_code": self.course_code,
            "course_name": self.course_name,
            "stream": self.stream,
            "universities": self.universities,
            "faculty_department": self.faculty_department,
            "duration": self.duration,
            "degree_programme": self.degree_programme,
            "subject_requirements": self.subject_requirements,
            "ol_requirements": self.ol_requirements,
            "practical_test": self.practical_test,
            "proposed_intake": self.proposed_intake,
            "medium_of_instruction": self.medium_of_instruction,
            "notes": self.notes,
            "metadata": self.metadata,
        }

    def __repr__(self):
        return f"<DegreeProgram {self.course_code} | {self.course_name}>"


def _parse_json_list(value) -> List[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def _parse_list(value) -> List[str]:
    """Parses a list-like cell that may be JSON, comma-separated, or pipe-separated."""
    if value is None:
        return []
    if isinstance(value, list):
        return [_clean_str(v) for v in value if _clean_str(v)]

    text = str(value).strip()
    if not text:
        return []

    # JSON list
    parsed_json = _parse_json_list(text)
    if parsed_json:
        return [_clean_str(v) for v in parsed_json if _clean_str(v)]

    # Delimited list
    delimiter = "|" if "|" in text else ","
    parts = [_clean_str(p) for p in text.split(delimiter)]
    return [p for p in parts if p]


def _parse_float(value) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def _parse_int(value) -> Optional[int]:
    """Parse integer value safely"""
    if not value:
        return None
    try:
        # Remove commas and whitespace
        cleaned = str(value).replace(",", "").strip()
        return int(cleaned)
    except Exception:
        return None


def _parse_subject_requirements(text: str) -> List[str]:
    """
    Parse A/L subject requirements from text.
    Extracts key subject names from requirement descriptions.
    """
    if not text:
        return []

    # Common subject names to extract
    common_subjects = [
        "Physics",
        "Chemistry",
        "Biology",
        "Combined Mathematics",
        "Mathematics",
        "Botany",
        "Zoology",
        "Agricultural Science",
        "Economics",
        "Business Studies",
        "Accounting",
        "Business Statistics",
        "Geography",
        "History",
        "Political Science",
        "Logic",
        "English",
        "Sinhala",
        "Tamil",
        "Arabic",
        "French",
        "German",
        "Art",
        "Dancing",
        "Music",
        "Drama",
        "Engineering Technology",
        "Science",
        "Technology",
    ]

    found_subjects = []
    text_lower = text.lower()

    for subject in common_subjects:
        if subject.lower() in text_lower:
            if subject not in found_subjects:
                found_subjects.append(subject)

    # If no specific subjects found, return general description
    if not found_subjects and text.strip():
        # Check for stream-level requirements
        if "arts" in text_lower:
            return ["Arts Stream"]
        elif "commerce" in text_lower:
            return ["Commerce Stream"]
        elif "science" in text_lower or "bio" in text_lower:
            return ["Science Stream"]

    return found_subjects


def _clean_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _stable_program_id(
    degree_name: str, institute: str = "", faculty: str = "", program_type: str = ""
) -> str:
    """Derive a stable-ish ID when the dataset doesn't provide one."""
    raw = "|".join(
        [
            degree_name.strip().lower(),
            institute.strip().lower(),
            faculty.strip().lower(),
            program_type.strip().lower(),
        ]
    )
    if not raw.strip("|"):
        raw = "unknown"
    digest = hashlib.sha1(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]
    return f"P-{digest}"
