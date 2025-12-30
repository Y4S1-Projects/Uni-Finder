# app/engines/rules_engine.py
from typing import Tuple

from app.domain.student import StudentProfile
from app.domain.program import DegreeProgram
from app.repositories.cutoff_repository import CutoffRepository


cutoff_repo = CutoffRepository()


def check_eligibility(
    student: StudentProfile,
    program: DegreeProgram,
    district: str
) -> Tuple[bool, str]:
    """
    Determines if a student is eligible for a degree program.
    """

    # 1. Stream check
    if student.stream.lower() != program.stream.lower():
        return False, "Stream mismatch"

    # 2. Subject prerequisites
    missing = set(program.subject_prerequisites) - set(student.subjects)
    if missing:
        return False, f"Missing required subjects: {', '.join(missing)}"

    # 3. District-based cutoff
    cutoff = cutoff_repo.get_cutoff(program.degree_name, district)

    if cutoff is None:
        return False, "No cutoff data available for this district"

    if student.zscore < cutoff:
        return False, f"Z-score below district cutoff ({cutoff})"

    return True, "Eligible based on stream, subjects, and Z-score"
