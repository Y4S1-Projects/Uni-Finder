# tests/test_rules_engine.py
from app.domain.student import StudentProfile
from app.domain.program import DegreeProgram
from app.engines.rules_engine import check_eligibility


def test_student_below_cutoff_is_rejected():
    student = StudentProfile(
        stream="Science",
        subjects=["Physics", "Chemistry", "Combined Mathematics"],
        zscore=1.2,
        interests="Computer Science"
    )

    program = DegreeProgram(
        program_id="TEST-001",
        degree_name="BSc Engineering (Computer Science)",
        stream="Science",
        subject_prerequisites=["Physics", "Chemistry", "Combined Mathematics"],
        min_zscore=None,
        syllabus_summary="",
        career_paths=[]
    )

    eligible, reason = check_eligibility(student, program, "Colombo")

    assert eligible is False
    assert "cutoff" in reason.lower()
