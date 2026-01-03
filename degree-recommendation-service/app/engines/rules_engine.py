# app/engines/rules_engine.py
from typing import Tuple

from app.domain.student import StudentProfile
from app.domain.program import DegreeProgram
from app.engines.cutoff_matcher import CutoffMatcher


cutoff_matcher = CutoffMatcher()


def check_eligibility(
    student: StudentProfile, program: DegreeProgram, district: str
) -> Tuple[bool, str]:
    """
    Determines if a student is eligible for a degree program
    using semantic cutoff matching.
    """

    # 1. Stream check (only if program declares a stream)
    if program.stream and student.stream:
        if student.stream.lower() != program.stream.lower():
            return False, "Stream mismatch"

    # 2. Subject prerequisites (only if program declares prerequisites)
    if program.subject_prerequisites:
        missing = set(program.subject_prerequisites) - set(student.subjects)
        if missing:
            return False, f"Missing required subjects: {', '.join(sorted(missing))}"

    # 3. AI-based cutoff resolution
    cutoff, match_info = cutoff_matcher.get_cutoff_semantic(
        program_name=program.degree_name, district=district
    )

    if cutoff is None:
        # Keep the wording consistent and explicit for callers/tests.
        return False, f"Cutoff unavailable: {match_info}"

    # 4. Z-score check
    if student.zscore < cutoff:
        return False, f"Z-score below cutoff ({cutoff})"

    return True, f"Eligible ({match_info})"
