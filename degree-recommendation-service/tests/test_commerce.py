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
    stream="Commerce",
    subjects=["Accounting", "Business Studies", "Geography"],
    zscore=None,
    interests="management",
)

print("Testing Commerce student for Management (016)...")
for p in programs:
    code = p.course_code.lstrip("0") or "0"
    if code == "16":
        is_eligible, reason, details = check_eligibility(student, p, "Colombo")
        print(
            f"[{p.course_code}] {p.course_name} -> Eligible: {is_eligible} - Subjects Match: {details.get('subjects_match')}"
        )
        if not is_eligible:
            print(f"  Reason: {reason}")
