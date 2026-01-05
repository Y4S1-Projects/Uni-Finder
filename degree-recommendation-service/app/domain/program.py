# app/domain/program.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import hashlib


class DegreeProgram:
    def __init__(
        self,
        program_id: str,
        degree_name: str,
        stream: str,
        subject_prerequisites: List[str],
        min_zscore: Optional[float],
        syllabus_summary: str,
        career_paths: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.program_id = program_id
        self.degree_name = degree_name
        self.stream = stream
        self.subject_prerequisites = subject_prerequisites
        self.min_zscore = min_zscore
        self.syllabus_summary = syllabus_summary
        self.career_paths = career_paths
        self.metadata = metadata or {}

    @classmethod
    def from_csv(cls, row: dict) -> "DegreeProgram":
        """
        Factory method to create DegreeProgram from CSV row.
        Handles missing and malformed values safely.
        """
        degree_name = _clean_str(
            row.get("degree_name")
            or row.get("Degree")
            or row.get("degree")
            or row.get("program_name")
        )

        institute = _clean_str(row.get("Institute") or row.get("institute"))
        faculty = _clean_str(row.get("Faculty") or row.get("faculty"))
        program_type = _clean_str(row.get("Type") or row.get("type"))

        program_id = _clean_str(
            row.get("program_id") or row.get("id") or row.get("programId")
        )
        if not program_id:
            program_id = _stable_program_id(
                degree_name=degree_name,
                institute=institute,
                faculty=faculty,
                program_type=program_type,
            )

        stream = _clean_str(
            row.get("stream")
            or row.get("Stream")
            or row.get("required_stream")
            or row.get("stream_required")
        )

        subject_prerequisites = _parse_list(
            row.get("subject_prerequisites")
            or row.get("subjects_required")
            or row.get("prerequisites")
        )

        min_zscore = _parse_float(
            row.get("min_zscore_latest")
            or row.get("min_zscore")
            or row.get("min_cutoff")
            or row.get("cutoff_zscore")
        )

        syllabus_summary = _clean_str(
            row.get("syllabus_summary") or row.get("summary") or row.get("description")
        )
        career_paths = _parse_list(row.get("career_paths") or row.get("careers"))

        reserved_keys = {
            "program_id",
            "id",
            "programId",
            "degree_name",
            "Degree",
            "degree",
            "program_name",
            "Institute",
            "institute",
            "Faculty",
            "faculty",
            "Type",
            "type",
            "stream",
            "Stream",
            "required_stream",
            "stream_required",
            "subject_prerequisites",
            "subjects_required",
            "prerequisites",
            "min_zscore_latest",
            "min_zscore",
            "min_cutoff",
            "cutoff_zscore",
            "syllabus_summary",
            "summary",
            "description",
            "career_paths",
            "careers",
        }
        metadata = {
            k: v
            for k, v in row.items()
            if k not in reserved_keys and v not in (None, "")
        }
        if institute:
            metadata.setdefault("institute", institute)
        if faculty:
            metadata.setdefault("faculty", faculty)
        if program_type:
            metadata.setdefault("type", program_type)

        return cls(
            program_id=program_id,
            degree_name=degree_name,
            stream=stream,
            subject_prerequisites=subject_prerequisites,
            min_zscore=min_zscore,
            syllabus_summary=syllabus_summary,
            career_paths=career_paths,
            metadata=metadata,
        )

    def __repr__(self):
        return f"<DegreeProgram {self.program_id} | {self.degree_name}>"


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
