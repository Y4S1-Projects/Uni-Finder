# app/engines/rules_engine.py
from typing import Tuple, List, Dict
import json
from pathlib import Path

from app.domain.student import StudentProfile
from app.domain.program import DegreeProgram
from app.engines.cutoff_matcher import CutoffMatcher

cutoff_matcher = CutoffMatcher()


def check_eligibility(
    student: StudentProfile,
    program: DegreeProgram,
    district: str,
    university: str = None,
) -> Tuple[bool, str, Dict]:
    """
    Determines if a student is eligible for a degree program.

    Z-Score Special Values:
    - zscore=None or zscore <= 0: Skip Z-score check (indicate "no Z-score filtering")
    - zscore > 0: Perform Z-score cutoff validation

    Stream Special Values:
    - stream=None, stream="", stream="Any": Skip stream check (interests-only mode)
    - Otherwise: Validate stream match with program requirements

    Returns:
        (is_eligible, reason, details_dict)
    """
    details = {
        "stream_match": False,
        "subjects_match": False,
        "zscore_check": None,
        "cutoff_info": None,
    }

    # 1. Stream check
    # Skip stream check if student.stream is None, empty, or "Any"
    student_stream_provided = (
        student.stream
        and student.stream.strip()
        and student.stream.strip().lower() != "any"
    )

    if student_stream_provided and program.stream:
        program_stream_lower = program.stream.lower()
        student_stream_lower = student.stream.lower()

        # Check for partial match (e.g., "Science" matches "Physical Science")
        if (
            student_stream_lower in program_stream_lower
            or program_stream_lower in student_stream_lower
        ):
            details["stream_match"] = True
        else:
            return (
                False,
                f"Stream mismatch: requires {program.stream}, you have {student.stream}",
                details,
            )
    else:
        # No stream provided or "Any" stream - skip check
        details["stream_match"] = True

    # 2. Subject prerequisites
    if program.subject_requirements:
        student_subjects_lower = [s.lower() for s in student.subjects]

        # Load the pre-compiled AST logic mapping
        rules_path = Path("data/course_subject_rules.json")
        course_rules = {}
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                course_rules = json.load(f)

        # Get the course rule (fallback to ANY_SUBJECT if not found)
        # JSON keys are padded to 3 digits (e.g., '008', '065')
        try:
            course_code_norm = f"{int(program.course_code):03d}"
        except ValueError:
            course_code_norm = program.course_code

        rule_ast = course_rules.get(course_code_norm, {"type": "ANY_SUBJECT"})

        def evaluate_ast(node) -> bool:
            if not node:
                return True

            node_type = node.get("type", "UNKNOWN")

            if node_type == "ANY_SUBJECT":
                return True

            if node_type == "SUBJECT":
                req_sub = node.get("name", "").lower()
                # Substring match robustly
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
                    "higher math": [
                        "higher mathematics",
                        "higher math",
                        "higher maths",
                    ],
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
                        return True
                    if req_sub in student_sub or student_sub in req_sub:
                        if req_sub == "mathematics" and (
                            "combined" in student_sub or "higher" in student_sub
                        ):
                            pass
                        else:
                            return True

                    req_aliases = aliases.get(req_sub, [])
                    if any(a == student_sub for a in req_aliases):
                        return True

                    student_aliases = aliases.get(student_sub, [])
                    if any(a == req_sub for a in student_aliases):
                        return True
                return False

            if node_type == "AND":
                operands = node.get("operands", [])
                return all(evaluate_ast(op) for op in operands)

            if node_type == "OR":
                operands = node.get("operands", [])
                return any(evaluate_ast(op) for op in operands)

            if node_type == "MIN_COUNT":
                count = node.get("count", 1)
                operands = node.get("operands", [])
                matches = sum(1 for op in operands if evaluate_ast(op))
                return matches >= count

            return False

        # Evaluate the AST against the student's subjects
        is_subject_match = evaluate_ast(rule_ast)

        if is_subject_match:
            details["subjects_match"] = True
        else:
            details["subjects_match"] = False
            return (
                False,
                f"Missing required subjects based on rule evaluation.",
                details,
            )
    else:
        # No specific subject requirements
        details["subjects_match"] = True

    # 3. Z-score cutoff check (using course code)
    cutoff, cutoff_info = cutoff_matcher.get_cutoff_for_course(
        course_code=program.course_code,
        district=district,
        preferred_university=university,
    )

    details["cutoff_info"] = cutoff_info

    if cutoff is None:
        # No cutoff data available
        if student.zscore is None:
            # Student didn't provide Z-score, recommend based on other criteria
            return True, f"Eligible by stream & subjects. {cutoff_info}", details
        else:
            # Student has Z-score but no cutoff to compare
            return True, f"Eligible by stream & subjects. {cutoff_info}", details

    # 4. Z-score comparison
    # Z-score <= 0 means "don't check Z-score" (special case for Scenarios 01, 03, 04)
    zscore_check_enabled = student.zscore is not None and student.zscore > 0

    if zscore_check_enabled:
        if cutoff is not None:
            meets_cutoff = student.zscore >= cutoff
            details["zscore_check"] = meets_cutoff
            details["zscore_details"] = {
                "student_zscore": student.zscore,
                "required_cutoff": cutoff,
                "meets_requirement": meets_cutoff,
            }

            if not meets_cutoff:
                return (
                    False,
                    f"Z-score {student.zscore:.4f} below cutoff {cutoff:.4f}. {cutoff_info}",
                    details,
                )
            else:
                return (
                    True,
                    f"Eligible: Z-score {student.zscore:.4f} meets cutoff {cutoff:.4f}. {cutoff_info}",
                    details,
                )
        else:
            # Student has zscore but no cutoff data
            details["zscore_check"] = True
            return True, f"Eligible by stream & subjects. {cutoff_info}", details
    else:
        # Z-score not provided or <= 0 (skip check) - treat as eligible by stream/subjects
        details["zscore_check"] = True  # Can't fail what wasn't checked
        if cutoff is not None:
            return (
                True,
                f"Eligible by stream & subjects. Cutoff is {cutoff:.4f} (no Z-score check). {cutoff_info}",
                details,
            )
        else:
            return True, f"Eligible by stream & subjects. {cutoff_info}", details


def check_eligibility_all_universities(
    student: StudentProfile, program: DegreeProgram, district: str
) -> List[Dict]:
    """
    Check eligibility across all universities offering the program.
    Returns list of university options with eligibility status.
    """
    university_cutoffs = cutoff_matcher.get_all_university_cutoffs(
        program.course_code, district
    )

    results = []
    for university, cutoff in university_cutoffs:
        is_eligible, reason, details = check_eligibility(
            student, program, district, university
        )

        results.append(
            {
                "university": university,
                "cutoff": cutoff,
                "is_eligible": is_eligible,
                "reason": reason,
                "details": details,
            }
        )

    return results
