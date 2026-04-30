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


# Overwrite check_eligibility temporarily with debug prints
def check_eligibility_debug(student, program, district):
    from pathlib import Path

    details = {}
    student_subjects_lower = [s.lower() for s in student.subjects]

    rules_path = Path("data/course_subject_rules.json")
    course_rules = {}
    if rules_path.exists():
        with open(rules_path, "r", encoding="utf-8") as f:
            course_rules = json.load(f)

    course_code_norm = program.course_code.lstrip("0") or "0"
    rule_ast = course_rules.get(course_code_norm, {"type": "ANY_SUBJECT"})

    print(f"\nAST for {program.course_code}: {json.dumps(rule_ast)}")

    def evaluate_ast(node) -> bool:
        if not node:
            return True
        node_type = node.get("type", "UNKNOWN")
        if node_type == "ANY_SUBJECT":
            return True
        if node_type == "SUBJECT":
            req_sub = node.get("name", "").lower()
            aliases = {
                "ict": [
                    "ict",
                    "information & communication technology",
                    "information and communication technology",
                    "it",
                ],
                "information & communication technology": [
                    "ict",
                    "information & communication technology",
                    "information and communication technology",
                    "it",
                ],
                "math": ["mathematics", "math", "maths"],
                "mathematics": ["mathematics", "math", "maths"],
                "combined math": [
                    "combined mathematics",
                    "combined math",
                    "combined maths",
                ],
                "combined mathematics": [
                    "combined mathematics",
                    "combined math",
                    "combined maths",
                ],
                "higher math": ["higher mathematics", "higher math", "higher maths"],
                "higher mathematics": [
                    "higher mathematics",
                    "higher math",
                    "higher maths",
                ],
                "agri sci": ["agri sci", "agricultural science"],
                "agricultural science": ["agri sci", "agricultural science"],
            }

            for student_sub in student_subjects_lower:
                if req_sub == student_sub:
                    print(f"    [MATCH] {req_sub} == {student_sub}")
                    return True
                if req_sub in student_sub or student_sub in req_sub:
                    if req_sub == "mathematics" and (
                        "combined" in student_sub or "higher" in student_sub
                    ):
                        pass
                    else:
                        print(f"    [MATCH] {req_sub} in {student_sub} (substring)")
                        return True

                req_aliases = aliases.get(req_sub, [])
                if any(a == student_sub for a in req_aliases):
                    print(f"    [MATCH] alias of {req_sub} == {student_sub}")
                    return True

                student_aliases = aliases.get(student_sub, [])
                if any(a == req_sub for a in student_aliases):
                    print(f"    [MATCH] {req_sub} == alias of {student_sub}")
                    return True
            print(f"    [NO MATCH] {req_sub}")
            return False

        if node_type == "AND":
            return all(evaluate_ast(op) for op in node.get("operands", []))

        if node_type == "OR":
            return any(evaluate_ast(op) for op in node.get("operands", []))

        if node_type == "MIN_COUNT":
            count = node.get("count", 1)
            matches = sum(1 for op in node.get("operands", []) if evaluate_ast(op))
            return matches >= count

        return False

    return evaluate_ast(rule_ast)


for p in programs:
    code = p.course_code.lstrip("0") or "0"
    if code == "8":
        res = check_eligibility_debug(student, p, "Colombo")
        print(f"Result: {res}")
