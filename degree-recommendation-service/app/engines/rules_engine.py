# app/engines/rules_engine.py
from typing import Tuple, List, Dict

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

        # Check if any required subjects are missing
        missing = []
        for req_subject in program.subject_requirements:
            req_lower = req_subject.lower()
            # Check for partial matches (e.g., "Mathematics" in "Combined Mathematics")
            found = any(
                req_lower in student_sub or student_sub in req_lower
                for student_sub in student_subjects_lower
            )
            if not found:
                missing.append(req_subject)

        if missing:
            details["subjects_match"] = False
            return False, f"Missing required subjects: {', '.join(missing)}", details

        details["subjects_match"] = True
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
