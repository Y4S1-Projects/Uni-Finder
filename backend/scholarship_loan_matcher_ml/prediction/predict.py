"""Prediction utilities for scholarship & loan matching."""

from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

MODULE_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Import eligibility_checker - handle both module and script execution
try:
    from .eligibility_checker import evaluate_eligibility
except ImportError:
    # When running as standalone script, import directly from file
    import importlib.util
    eligibility_checker_path = Path(__file__).resolve().parent / "eligibility_checker.py"
    spec = importlib.util.spec_from_file_location("eligibility_checker", eligibility_checker_path)
    eligibility_checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eligibility_checker)
    evaluate_eligibility = eligibility_checker.evaluate_eligibility

ARTIFACT_DIR = MODULE_ROOT / "training" / "artifacts"
PROCESSED_DATA_PATH = ARTIFACT_DIR / "processed_dataset.json"
VECTORIZER_PATH = ARTIFACT_DIR / "tfidf_vectorizer.joblib"
MODEL_PATH = ARTIFACT_DIR / "knn_similarity_model.joblib"

TEXT_PROFILE_FIELDS = [
    "education_level",
    "field_of_study",
    "family_income",
    "district",
    "age",
    "study_interests",
    "career_goals",
    "extracurriculars",
]


def _load_dataset() -> pd.DataFrame:
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {PROCESSED_DATA_PATH}. "
            "Run the training pipeline first."
        )
    return pd.read_json(PROCESSED_DATA_PATH)


@lru_cache(maxsize=1)
def _get_vectorizer():
    return joblib.load(VECTORIZER_PATH)


@lru_cache(maxsize=1)
def _get_similarity_model():
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def _get_processed_df():
    return _load_dataset()


def _build_profile_text(profile: Dict[str, Any]) -> str:
    parts = []
    for field in TEXT_PROFILE_FIELDS:
        value = profile.get(field)
        if value:
            parts.append(str(value))
    # add explicit preferences if provided
    if skills := profile.get("skills"):
        parts.append(
            " ".join(skills if isinstance(skills, list) else [skills]))
    if desired_program := profile.get("desired_program_type"):
        parts.append(desired_program)
    return " ".join(parts).lower()


def _extract_numbers(text: str) -> List[float]:
    return [float(num) for num in re.findall(r"\d+(?:\.\d+)?", text)]


def _passes_filters(record: Dict[str, Any], profile: Dict[str, Any]) -> bool:
    # Location match (region vs district)
    district = profile.get("district")
    if district and isinstance(district, str):
        region = str(record.get("region") or "").lower()
        if region and district.lower() not in region:
            return False

    # Age filter
    age = profile.get("age")
    if age:
        try:
            age_value = float(age)
            criteria_text = str(record.get("age_criteria") or "")
            numbers = _extract_numbers(criteria_text)
            if numbers:
                lower = min(numbers)
                upper = max(numbers)
                if age_value < lower or age_value > upper:
                    return False
        except (ValueError, TypeError):
            pass

    # Income filter
    income = profile.get("family_income")
    if income:
        try:
            income_value = float(income)
            criteria_text = str(record.get("income_criteria") or "")
            numbers = _extract_numbers(criteria_text)
            if numbers and income_value > max(numbers):
                return False
        except (ValueError, TypeError):
            pass

    # Program type preference
    desired_program = profile.get("desired_program_type")
    if desired_program:
        program_type = str(record.get("program_type")
                           or record.get("loan_type") or "")
        if program_type and desired_program.lower() not in program_type.lower():
            return False

    return True


def compute_final_score(similarity_score: float, eligibility_result: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute rule_score and final_score for a record.

    - If clearly eligible (no failed reasons): rule_score = 1.0
    - If clearly ineligible (only failed reasons): rule_score = 0.0
    - If mixed (both passed and failed reasons): rule_score in [0.3, 0.7]
    - Similarity is halved for ineligible matches.
    """
    reasons = eligibility_result.get("reasons", {}) or {}
    passed = reasons.get("passed", []) or []
    failed = reasons.get("failed", []) or []

    if eligibility_result.get("eligible"):
        rule_score = 1.0
        adjusted_similarity = similarity_score
    else:
        if passed and failed:
            ratio = len(passed) / (len(passed) + len(failed))
            rule_score = 0.3 + (0.4 * ratio)  # 0.3–0.7
        elif failed:
            rule_score = 0.0
        else:
            # No explicit rules triggered; treat as neutral partial match
            rule_score = 0.5
        adjusted_similarity = similarity_score / 2.0

    final_score = (0.7 * adjusted_similarity) + (0.3 * rule_score)
    return {
        "rule_score": float(round(rule_score, 4)),
        "final_score": float(round(final_score, 4)),
        "similarity_score": float(round(adjusted_similarity, 4)),
    }


def match_student_profile(
    profile: Dict[str, Any],
    top_n: int = 5,
    candidate_pool: int = 25,
) -> List[Dict[str, Any]]:
    if not isinstance(profile, dict):
        raise ValueError("Profile must be a dictionary.")

    processed_df = _get_processed_df()
    if processed_df.empty:
        return []

    vectorizer = _get_vectorizer()
    model = _get_similarity_model()

    profile_text = _build_profile_text(profile)
    if not profile_text.strip():
        raise ValueError("Profile text cannot be empty. Provide more details.")

    query_vec = vectorizer.transform([profile_text])
    n_neighbors = min(max(candidate_pool, top_n), len(processed_df))
    distances, indices = model.kneighbors(query_vec, n_neighbors=n_neighbors)

    scored_results: List[Dict[str, Any]] = []
    for dist, idx in zip(distances[0], indices[0]):
        record = processed_df.iloc[idx].to_dict()
        similarity = 1 - float(dist)

        eligibility = evaluate_eligibility(profile, record)
        scores = compute_final_score(similarity, eligibility)

        record.update(
            {
                "similarity_score": scores["similarity_score"],
                "rule_score": scores["rule_score"],
                "final_score": scores["final_score"],
                "eligibility_status": "eligible"
                if eligibility.get("eligible")
                else "ineligible",
                "eligibility_reasons": eligibility.get("reasons", {}),
            }
        )
        scored_results.append(record)

    filtered_results = [rec for rec in scored_results if _passes_filters(rec, profile)]
    if not filtered_results:
        filtered_results = scored_results  # fall back to similarity order

    # Sort by final_score descending and clean NaN/inf before returning
    ranked = sorted(filtered_results, key=lambda rec: rec.get("final_score", 0.0), reverse=True)

    def _clean_value(v):
        if isinstance(v, float):
            if np.isnan(v) or np.isinf(v):
                return None
            return v
        if isinstance(v, (np.floating, np.integer)):
            v = float(v)
            if np.isnan(v) or np.isinf(v):
                return None
            return v
        return v

    cleaned_results: List[Dict[str, Any]] = []
    for rec in ranked[:top_n]:
        cleaned_rec = {k: _clean_value(v) for k, v in rec.items()}
        cleaned_results.append(cleaned_rec)

    return cleaned_results


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Predict top scholarships/loans.")
    parser.add_argument("--profile", required=True,
                        help="JSON string of student profile.")
    parser.add_argument("--top_n", type=int, default=5,
                        help="Number of matches to return.")
    args = parser.parse_args()

    profile = json.loads(args.profile)
    results = match_student_profile(profile, top_n=args.top_n)

    # --- OPTIONAL extra safety: ensure full structure is JSON-safe ---
    def _json_safe(obj):
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return obj
        if isinstance(obj, (np.floating, np.integer)):
            v = float(obj)
            if np.isnan(v) or np.isinf(v):
                return None
            return v
        if isinstance(obj, dict):
            return {k: _json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_json_safe(v) for v in obj]
        return obj

    safe_payload = _json_safe({"results": results})
    print(json.dumps(safe_payload, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
