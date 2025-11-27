"""Eligibility rules engine for scholarship & loan matching."""

from __future__ import annotations

import re
from typing import Any, Dict, List


def _extract_numbers(text: str) -> List[float]:
    if not text:
        return []
    return [float(num) for num in re.findall(r"\d+(?:\.\d+)?", str(text))]


def _add_reason(target: Dict[str, List[str]], key: str, message: str) -> None:
    target.setdefault(key, []).append(message)


def evaluate_eligibility(student_profile: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single scholarship/loan record against the student profile.

    Returns:
        {
            "eligible": bool,
            "reasons": {
                "passed": [...],
                "failed": [...],
            },
        }
    """
    reasons = {"passed": [], "failed": []}  # type: ignore[assignment]

    # --- Age rule -----------------------------------------------------------
    age = student_profile.get("age")
    criteria_text = record.get("age_criteria") or ""
    age_numbers = _extract_numbers(criteria_text)
    if age is not None and age_numbers:
        try:
            age_val = float(age)
            lower = min(age_numbers)
            upper = max(age_numbers)
            if lower <= age_val <= upper:
                _add_reason(reasons, "passed", f"Age {age_val} is within required range {lower}-{upper}.")
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"Age {age_val} is outside required range {lower}-{upper}.",
                )
        except (TypeError, ValueError):
            pass

    # --- Region / district rule --------------------------------------------
    district = student_profile.get("district")
    region = (record.get("region") or record.get("eligible_region") or "").lower()
    if district and isinstance(district, str) and region:
        if district.lower() in region:
            _add_reason(reasons, "passed", f"District '{district}' matches eligible region '{region}'.")
        else:
            _add_reason(
                reasons,
                "failed",
                f"District '{district}' may be outside eligible region '{region}'.",
            )

    # --- Gender rule --------------------------------------------------------
    student_gender = (student_profile.get("gender") or "").lower()
    record_gender = (
        (record.get("gender") or record.get("eligible_gender") or record.get("required_gender") or "")
        .strip()
        .lower()
    )
    if record_gender:
        if student_gender and student_gender in record_gender:
            _add_reason(reasons, "passed", f"Gender '{student_gender}' matches requirement '{record_gender}'.")
        elif student_gender:
            _add_reason(
                reasons,
                "failed",
                f"Gender '{student_gender}' may not match required gender '{record_gender}'.",
            )

    # --- Study field / program rule ----------------------------------------
    field_of_study = (student_profile.get("field_of_study") or "").lower()
    program_blob = " ".join(
        str(part or "").lower()
        for part in [
            record.get("program_type"),
            record.get("loan_type"),
            record.get("name"),
            record.get("description"),
            record.get("eligibility"),
        ]
    )
    if field_of_study:
        if field_of_study and field_of_study in program_blob:
            _add_reason(
                reasons,
                "passed",
                f"Field of study '{field_of_study}' appears in program description.",
            )
        else:
            _add_reason(
                reasons,
                "failed",
                f"Field of study '{field_of_study}' not clearly mentioned in program details.",
            )

    # --- Family income rule -------------------------------------------------
    income = student_profile.get("family_income")
    income_text = record.get("income_criteria") or record.get("eligibility") or ""
    income_numbers = _extract_numbers(income_text)
    if income is not None and income_numbers:
        try:
            income_val = float(income)
            max_income = max(income_numbers)
            if income_val <= max_income:
                _add_reason(
                    reasons,
                    "passed",
                    f"Family income {income_val} is within allowed maximum {max_income}.",
                )
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"Family income {income_val} exceeds allowed maximum {max_income}.",
                )
        except (TypeError, ValueError):
            pass

    # --- GPA / Z-score rule -------------------------------------------------
    gpa = student_profile.get("gpa") or student_profile.get("z_score")
    gpa_text = (
        record.get("gpa_requirement")
        or record.get("z_score_requirement")
        or record.get("eligibility")
        or ""
    )
    gpa_numbers = _extract_numbers(gpa_text)
    if gpa is not None and gpa_numbers:
        try:
            gpa_val = float(gpa)
            min_required = min(gpa_numbers)
            if gpa_val >= min_required:
                _add_reason(
                    reasons,
                    "passed",
                    f"GPA/Z-score {gpa_val} meets minimum requirement {min_required}.",
                )
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"GPA/Z-score {gpa_val} is below minimum requirement {min_required}.",
                )
        except (TypeError, ValueError):
            pass

    # Determine eligibility
    has_failed = len(reasons["failed"]) > 0
    eligible = not has_failed

    return {
        "eligible": eligible,
        "reasons": reasons,
    }


