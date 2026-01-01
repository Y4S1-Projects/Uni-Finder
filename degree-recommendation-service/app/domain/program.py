# app/domain/program.py
from typing import List, Optional
import json


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
    ):
        self.program_id = program_id
        self.degree_name = degree_name
        self.stream = stream
        self.subject_prerequisites = subject_prerequisites
        self.min_zscore = min_zscore
        self.syllabus_summary = syllabus_summary
        self.career_paths = career_paths

    @classmethod
    def from_csv(cls, row: dict) -> "DegreeProgram":
        """
        Factory method to create DegreeProgram from CSV row.
        Handles missing and malformed values safely.
        """
        return cls(
            program_id=row.get("program_id", "").strip(),
            degree_name=row.get("degree_name", "").strip(),
            stream=row.get("stream", "").strip(),
            subject_prerequisites=_parse_json_list(row.get("subject_prerequisites")),
            min_zscore=_parse_float(row.get("min_zscore_latest")),
            syllabus_summary=row.get("syllabus_summary", "").strip(),
            career_paths=_parse_json_list(row.get("career_paths")),
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


def _parse_float(value) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None
