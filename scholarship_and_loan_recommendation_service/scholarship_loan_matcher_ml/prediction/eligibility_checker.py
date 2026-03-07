"""Eligibility rules engine for scholarship & loan matching with context-aware explanations."""

from __future__ import annotations

import re
from typing import Any, Dict, List


def _extract_numbers(text: str) -> List[float]:
    if not text:
        return []
    return [float(num) for num in re.findall(r"\d+(?:\.\d+)?", str(text))]


def _add_reason(target: Dict[str, List[str]], key: str, message: str) -> None:
    target.setdefault(key, []).append(message)


def _clean_name(name: str) -> str:
    """Remove year from scholarship/loan names."""
    if not name:
        return name
    # Remove patterns like ", 2018", ", 2020", " in 2018", " (2018)", etc.
    name = re.sub(r',\s*\d{4}\s*$', '', name)
    name = re.sub(r'\s+in\s+\d{4}\s*$', '', name)
    name = re.sub(r'\s*\(\d{4}\)\s*$', '', name)
    return name.strip()


def evaluate_eligibility(
    student_profile: Dict[str, Any], 
    record: Dict[str, Any],
    match_type: str = None
) -> Dict[str, Any]:
    """
    Evaluate a single scholarship/loan record against the student profile.
    
    Args:
        student_profile: Student profile data
        record: Scholarship/loan record
        match_type: 'scholarship' or 'loan' for context-aware explanations
    
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
    is_scholarship = match_type == "scholarship" or record.get("record_type") == "scholarship"
    is_loan = match_type == "loan" or record.get("record_type") == "loan"
    
    # Clean record name to remove years
    if "name" in record:
        record["name"] = _clean_name(str(record.get("name", "")))

    # --- Z-Score / Merit-based evaluation (Scholarships) ---
    z_score = student_profile.get("z_score")
    if z_score is not None and is_scholarship:
        z_score_text = (
            record.get("z_score_requirement")
            or record.get("gpa_requirement")
            or record.get("eligibility")
            or ""
        )
        z_score_numbers = _extract_numbers(z_score_text)
        if z_score_numbers:
            try:
                z_score_val = float(z_score)
                min_required = min(z_score_numbers)
                if z_score_val >= min_required:
                    _add_reason(
                        reasons,
                        "passed",
                        f"Your Z-Score of {z_score_val:.4f} meets the minimum requirement of {min_required:.4f} for this merit-based scholarship.",
                    )
                else:
                    _add_reason(
                        reasons,
                        "failed",
                        f"Your Z-Score of {z_score_val:.4f} is below the minimum requirement of {min_required:.4f}. This scholarship prioritizes high-achieving students.",
                    )
            except (TypeError, ValueError):
                pass
        elif z_score_val := float(z_score) if z_score else None:
            # No explicit requirement, but high Z-score is still a merit indicator
            if z_score_val >= 1.5:
                _add_reason(
                    reasons,
                    "passed",
                    f"Your Z-Score of {z_score_val:.4f} indicates strong academic merit, which is favorable for scholarship consideration.",
                )

    # --- A/L Stream matching (Scholarships) ---
    al_stream = student_profile.get("al_stream")
    if al_stream and is_scholarship:
        program_text = " ".join(
            str(part or "").lower()
            for part in [
                record.get("program_type"),
                record.get("name"),
                record.get("description"),
                record.get("eligibility"),
            ]
        )
        stream_lower = str(al_stream).lower()
        if stream_lower in program_text:
            _add_reason(
                reasons,
                "passed",
                f"Your A/L stream ({al_stream}) aligns with this scholarship's focus areas.",
            )
        else:
            _add_reason(
                reasons,
                "failed",
                f"This scholarship may prioritize different A/L streams. Your stream ({al_stream}) is not clearly mentioned in the requirements.",
            )

    # --- District / Region rule (Scholarships - quota-based) ---
    district = student_profile.get("district")
    region = (record.get("region") or record.get("eligible_region") or "").lower()
    if district and isinstance(district, str) and region and is_scholarship:
        if district.lower() in region:
            _add_reason(
                reasons,
                "passed",
                f"Your district ({district}) is eligible for this scholarship. Some scholarships have district-based quotas to ensure regional representation.",
            )
        else:
            _add_reason(
                reasons,
                "failed",
                f"Your district ({district}) may not be in the eligible region for this scholarship. Check if there are district-specific quotas.",
            )

    # --- Financial Need Evaluation (Scholarships) ---
    income = student_profile.get("family_income") or student_profile.get("annual_household_income")
    income_text = record.get("income_criteria") or record.get("eligibility") or ""
    income_numbers = _extract_numbers(income_text)
    
    if income is not None and income_numbers and is_scholarship:
        try:
            income_val = float(income)
            max_income = max(income_numbers)
            if income_val <= max_income:
                _add_reason(
                    reasons,
                    "passed",
                    f"Your annual household income of LKR {income_val:,.0f} is within the maximum threshold of LKR {max_income:,.0f} for need-based scholarships.",
                )
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"Your annual household income of LKR {income_val:,.0f} exceeds the maximum threshold of LKR {max_income:,.0f}. This scholarship is designed for students with greater financial need.",
                )
        except (TypeError, ValueError):
            pass

    # Samurdhi Recipient (Scholarships)
    samurdhi = student_profile.get("samurdhi_recipient")
    if samurdhi is True and is_scholarship:
        _add_reason(
            reasons,
            "passed",
            "As a Samurdhi recipient, you may qualify for additional need-based scholarship opportunities.",
        )

    # --- Loan Qualification Criteria ---
    if is_loan:
        # A/L Year requirement
        al_year = student_profile.get("al_year")
        if al_year:
            record_year_text = record.get("eligibility") or record.get("description") or ""
            # Check if recent A/L years are mentioned
            recent_years = ["2020", "2021", "2022", "2023", "2024"]
            if any(year in record_year_text for year in recent_years):
                _add_reason(
                    reasons,
                    "passed",
                    f"Your A/L year ({al_year}) may be eligible for this loan program. Verify the specific year requirements.",
                )

        # General Test Score
        general_test = student_profile.get("general_test_score")
        if general_test is not None:
            test_text = record.get("eligibility") or record.get("description") or ""
            test_numbers = _extract_numbers(test_text)
            if test_numbers:
                min_test = min(test_numbers)
                try:
                    test_val = float(general_test)
                    if test_val >= min_test:
                        _add_reason(
                            reasons,
                            "passed",
                            f"Your General Test score of {test_val} meets the minimum requirement of {min_test} for loan qualification.",
                        )
                    else:
                        _add_reason(
                            reasons,
                            "failed",
                            f"Your General Test score of {test_val} is below the minimum requirement of {min_test}. This may affect loan eligibility.",
                        )
                except (TypeError, ValueError):
                    pass

        # A/L Results
        al_passed_all_3 = student_profile.get("al_passed_all_3")
        al_at_least_s = student_profile.get("al_at_least_s")
        if al_passed_all_3:
            _add_reason(
                reasons,
                "passed",
                "You have passed all 3 A/L subjects, which is a strong qualification indicator for education loans.",
            )
        elif al_at_least_s:
            _add_reason(
                reasons,
                "passed",
                "You have at least 'S' passes in A/L subjects, which may qualify you for certain loan programs.",
            )

        # Guarantor Availability
        guarantor = student_profile.get("guarantor_availability")
        if guarantor:
            if guarantor.lower() in ["1 guarantor", "2 guarantors"]:
                _add_reason(
                    reasons,
                    "passed",
                    f"Having {guarantor.lower()} strengthens your loan application. Most banks require guarantors for education loans.",
                )
            elif guarantor.lower() == "none":
                _add_reason(
                    reasons,
                    "failed",
                    "This loan requires a guarantor, but you indicated no guarantor availability. Consider finding a suitable guarantor to improve eligibility.",
                )

        # Employment Status
        employment = student_profile.get("employment_status")
        if employment:
            if employment.lower() == "employed full-time":
                _add_reason(
                    reasons,
                    "passed",
                    "Your full-time employment status may improve loan approval chances, as it indicates repayment capacity.",
                )
            elif employment.lower() == "unemployed":
                _add_reason(
                    reasons,
                    "failed",
                    "Being unemployed may affect loan approval. Lenders typically prefer applicants with income sources or guarantors.",
                )

        # Target Institute Type
        institute_type = student_profile.get("target_institute_type")
        if institute_type:
            record_text = " ".join(
                str(part or "").lower()
                for part in [
                    record.get("name"),
                    record.get("description"),
                    record.get("eligibility"),
                ]
            )
            institute_lower = str(institute_type).lower()
            if institute_lower in record_text:
                _add_reason(
                    reasons,
                    "passed",
                    f"This loan program supports {institute_type}, which matches your target institution type.",
                )

        # Loan Amount
        loan_amount = student_profile.get("loan_amount_required")
        if loan_amount is not None:
            max_amount_text = record.get("eligibility") or record.get("description") or ""
            max_amount_numbers = _extract_numbers(max_amount_text)
            if max_amount_numbers:
                max_loan = max(max_amount_numbers)
                try:
                    amount_val = float(loan_amount)
                    if amount_val <= max_loan:
                        _add_reason(
                            reasons,
                            "passed",
                            f"Your required loan amount of LKR {amount_val:,.0f} is within the maximum limit of LKR {max_loan:,.0f}.",
                        )
                    else:
                        _add_reason(
                            reasons,
                            "failed",
                            f"Your required loan amount of LKR {amount_val:,.0f} exceeds the maximum limit of LKR {max_loan:,.0f}. Consider applying for a lower amount or multiple loans.",
                        )
                except (TypeError, ValueError):
                    pass

    # --- Field of Study matching (Both) ---
    field_of_study = student_profile.get("field_of_study")
    if field_of_study and field_of_study.lower() not in ["education_loan", ""]:
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
        field_lower = str(field_of_study).lower()
        if field_lower in program_blob:
            if is_scholarship:
                _add_reason(
                    reasons,
                    "passed",
                    f"Your preferred field of study ({field_of_study}) aligns with this scholarship's focus area.",
                )
            else:
                _add_reason(
                    reasons,
                    "passed",
                    f"Your preferred field of study ({field_of_study}) is supported by this loan program.",
                )
        else:
            if is_scholarship:
                _add_reason(
                    reasons,
                    "failed",
                    f"Your preferred field of study ({field_of_study}) is not clearly mentioned in this scholarship's requirements. Verify if your field is eligible.",
                )
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"Your preferred field of study ({field_of_study}) may not be explicitly supported by this loan program. Check with the lender for field-specific eligibility.",
                )

    # --- Age rule (Both) ---
    age = student_profile.get("age")
    criteria_text = record.get("age_criteria") or ""
    age_numbers = _extract_numbers(criteria_text)
    if age is not None and age_numbers:
        try:
            age_val = float(age)
            lower = min(age_numbers)
            upper = max(age_numbers)
            if lower <= age_val <= upper:
                _add_reason(reasons, "passed", f"Your age ({age_val}) is within the required range of {lower}-{upper} years.")
            else:
                _add_reason(
                    reasons,
                    "failed",
                    f"Your age ({age_val}) is outside the required range of {lower}-{upper} years.",
                )
        except (TypeError, ValueError):
            pass

    # --- Gender rule (Both) ---
    student_gender = (student_profile.get("gender") or "").lower()
    record_gender = (
        (record.get("gender") or record.get("eligible_gender") or record.get("required_gender") or "")
        .strip()
        .lower()
    )
    if record_gender:
        if student_gender and student_gender in record_gender:
            _add_reason(reasons, "passed", f"Your gender matches the requirement for this opportunity.")
        elif student_gender:
            _add_reason(
                reasons,
                "failed",
                f"This opportunity has specific gender requirements that may not match your profile.",
            )

    # --- University Registration Status (Scholarships) ---
    uni_status = student_profile.get("uni_registration_status")
    if uni_status and is_scholarship:
        status_text = " ".join(
            str(part or "").lower()
            for part in [
                record.get("name"),
                record.get("description"),
                record.get("eligibility"),
            ]
        )
        status_lower = str(uni_status).lower()
        if status_lower in status_text or "state" in status_lower and "state" in status_text:
            _add_reason(
                reasons,
                "passed",
                f"Your university registration status ({uni_status}) aligns with this scholarship's eligibility criteria.",
            )

    # Determine eligibility
    has_failed = len(reasons["failed"]) > 0
    eligible = not has_failed

    return {
        "eligible": eligible,
        "reasons": reasons,
    }
