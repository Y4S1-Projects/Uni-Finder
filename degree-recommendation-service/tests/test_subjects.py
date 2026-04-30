import json
from app.engines.rules_engine import check_eligibility
from app.domain.student import StudentProfile
from app.repositories.program_repository import ProgramRepository
from app.repositories.cutoff_repository import CutoffRepository

cutoff_repo = CutoffRepository()
cutoff_repo.load()

repo = ProgramRepository()
programs = repo.get_all_programs()

student = StudentProfile(
    stream="Physical Science",
    subjects=[
        "Combined Mathematics",
        "Physics",
        "Information & Communication Technology",
    ],
    zscore=None,
    interests="software engineering",
)

for p in programs:
    code = p.course_code.lstrip("0") or "0"
    if code in ["99", "12", "8", "14", "65", "108", "27"]:
        is_eligible, reason, details = check_eligibility(student, p, "Colombo")
        print(f"[{p.course_code}] {p.course_name}")
        print(f"  Required: {p.subject_requirements}")
        print(f"  Raw: {p.metadata.get('raw_subject_requirements')}")
        print(f"  Eligible: {is_eligible} - Reason: {reason}")
        print(f"  Details: {details.get('subjects_match')}")
        print()
