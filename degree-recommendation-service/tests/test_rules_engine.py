import pytest
from app.domain.student import StudentProfile
from app.engines.rules_engine import check_eligibility
from app.repositories.program_repository import ProgramRepository
from app.repositories.cutoff_repository import CutoffRepository


# Fixture to load repository data once for tests
@pytest.fixture(scope="module")
def setup_repositories():
    cutoff_repo = CutoffRepository()
    cutoff_repo.load()
    program_repo = ProgramRepository()
    programs = {
        p.course_code.lstrip("0") or "0": p for p in program_repo.get_all_programs()
    }
    return programs


def test_physical_science_engineering_eligibility(setup_repositories):
    """Test that a Physical Science student with correct subjects is eligible for Engineering."""
    programs = setup_repositories
    student = StudentProfile(
        stream="Physical Science",
        subjects=["Combined Mathematics", "Physics", "Chemistry"],
        zscore=2.5,
        interests="building structures",
    )

    # "008" is Engineering
    program = programs.get("8")
    assert program is not None

    is_eligible, reason, details = check_eligibility(student, program, "COLOMBO")
    assert is_eligible is True
    assert details["stream_match"] is True
    assert details["subjects_match"] is True


def test_commerce_management_eligibility(setup_repositories):
    """Test that a Commerce student is eligible for Management."""
    programs = setup_repositories
    student = StudentProfile(
        stream="Commerce",
        subjects=["Accounting", "Business Studies", "Geography"],
        zscore=2.0,
        interests="management",
    )

    # "016" is Management
    program = programs.get("16")
    assert program is not None

    is_eligible, reason, details = check_eligibility(student, program, "COLOMBO")
    assert is_eligible is True
    assert details["stream_match"] is True


def test_mismatch_stream_rejection(setup_repositories):
    """Test that an Arts student is rejected from Medicine."""
    programs = setup_repositories
    student = StudentProfile(
        stream="Arts",
        subjects=["Sinhala", "Logic", "History"],
        zscore=2.5,
        interests="medicine",
    )

    # "001" is Medicine
    program = programs.get("1")
    assert program is not None

    is_eligible, reason, details = check_eligibility(student, program, "COLOMBO")
    assert is_eligible is False
    assert details["stream_match"] is False


def test_zscore_cutoff_rejection(setup_repositories):
    """Test that a student with low z-score is rejected but marked as having subject match."""
    programs = setup_repositories
    student = StudentProfile(
        stream="Biological Science",
        subjects=["Biology", "Chemistry", "Physics"],
        zscore=0.5,  # Very low
        interests="medicine",
    )

    program = programs.get("1")

    is_eligible, reason, details = check_eligibility(student, program, "COLOMBO")
    assert is_eligible is False
    assert details["stream_match"] is True
    assert details["subjects_match"] is True
    assert details["zscore_check"] is False


def test_subject_ast_complex_rules(setup_repositories):
    """Test AST resolution for ICT aliasing."""
    programs = setup_repositories
    student = StudentProfile(
        stream="Physical Science",
        subjects=[
            "Combined Mathematics",
            "Physics",
            "Information & Communication Technology",
        ],
        zscore=2.0,
        interests="software engineering",
    )

    # "012" is Computer Science
    program = programs.get("12")
    assert program is not None

    is_eligible, reason, details = check_eligibility(student, program, "COLOMBO")
    assert is_eligible is True
    assert details["subjects_match"] is True
