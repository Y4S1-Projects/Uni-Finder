"""Match engine that uses freshly cleaned datasets (scholarships + loans)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from scholarship_loan_matcher_ml.data_loader.load_datasets import load_cleaned_datasets

# Eligibility engine
try:
    from scholarship_loan_matcher_ml.prediction.eligibility_checker import evaluate_eligibility
except ImportError:  # Fallback if executed as script without package context
    from pathlib import Path as _Path
    import importlib.util as _importlib

    _elig_path = _Path(__file__).resolve().parents[1] / "prediction" / "eligibility_checker.py"
    _spec = _importlib.spec_from_file_location("eligibility_checker", _elig_path)
    _module = _importlib.module_from_spec(_spec)
    _spec.loader.exec_module(_module)  # type: ignore
    evaluate_eligibility = _module.evaluate_eligibility


TEXT_FIELDS = [
    "name",
    "description",
    "eligibility",
    "program_type",
    "loan_type",
    "region",
    "special_benefits",
]

PROFILE_TEXT_FIELDS = [
    "education_level",
    "field_of_study",
    "family_income",
    "district",
    "age",
    "study_interests",
    "career_goals",
    "extracurriculars",
    "desired_program_type",
]


def _build_corpus(df: pd.DataFrame, fields: List[str]) -> pd.Series:
    safe_df = df.copy()
    for field in fields:
        if field not in safe_df.columns:
            safe_df[field] = ""
    corpus = (
        safe_df[fields]
        .fillna("")
        .agg(lambda row: " ".join(part for part in row if part), axis=1)
        .str.lower()
    )
    return corpus


def _build_profile_text(profile: Dict[str, Any]) -> str:
    parts: List[str] = []
    for field in PROFILE_TEXT_FIELDS:
        value = profile.get(field)
        if value:
            parts.append(str(value))
    if skills := profile.get("skills"):
        parts.append(" ".join(skills if isinstance(skills, list) else [skills]))
    return " ".join(parts).lower()


def _train_vectorizer(corpus: pd.Series, max_features: int = 8000) -> TfidfVectorizer:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=1,
        strip_accents="unicode",
    )
    vectorizer.fit(corpus)
    return vectorizer


def _fit_similarity_model(embeddings) -> NearestNeighbors:
    model = NearestNeighbors(metric="cosine", algorithm="brute")
    model.fit(embeddings)
    return model


def compute_final_score(similarity_score: float, eligibility_result: Dict[str, Any]) -> Tuple[float, float, float]:
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
            rule_score = 0.5
        adjusted_similarity = similarity_score / 2.0

    final_score = (0.7 * adjusted_similarity) + (0.3 * rule_score)
    return (
        float(round(final_score, 4)),
        float(round(rule_score, 4)),
        float(round(adjusted_similarity, 4)),
    )


@lru_cache(maxsize=1)
def _load_and_prepare() -> Dict[str, Any]:
    datasets = load_cleaned_datasets()
    scholarships = datasets["scholarships"].copy()
    loans = datasets["loans"].copy()

    # Ensure record_type present
    if "record_type" not in scholarships.columns:
        scholarships["record_type"] = "scholarship"
    if "record_type" not in loans.columns:
        loans["record_type"] = "loan"

    combined = pd.concat([scholarships, loans], ignore_index=True)
    combined["text_corpus"] = _build_corpus(combined, TEXT_FIELDS)

    vectorizer = _train_vectorizer(combined["text_corpus"])
    embeddings = vectorizer.transform(combined["text_corpus"])
    model = _fit_similarity_model(embeddings)

    return {
        "scholarships": scholarships,
        "loans": loans,
        "combined": combined,
        "vectorizer": vectorizer,
        "model": model,
    }


def _clean_name(name: str) -> str:
    """Remove year from scholarship/loan names."""
    if not name:
        return name
    import re
    # Remove patterns like ", 2018", ", 2020", " in 2018", " (2018)", etc.
    name = re.sub(r',\s*\d{4}\s*$', '', str(name))
    name = re.sub(r'\s+in\s+\d{4}\s*$', '', name)
    name = re.sub(r'\s*\(\d{4}\)\s*$', '', name)
    return name.strip()


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


def match_profile(profile: Dict[str, Any], top_n: int = 5, candidate_pool: int = 25) -> Dict[str, Any]:
    if not isinstance(profile, dict):
        raise ValueError("Profile must be a dictionary.")

    resources = _load_and_prepare()
    combined_df: pd.DataFrame = resources["combined"]
    vectorizer: TfidfVectorizer = resources["vectorizer"]
    model: NearestNeighbors = resources["model"]

    if combined_df.empty:
        return {"scholarships": [], "loans": [], "combined": [], "explanations": {"why_accepted": [], "why_rejected": []}}

    profile_text = _build_profile_text(profile)
    if not profile_text.strip():
        raise ValueError("Profile text cannot be empty. Provide more details.")

    query_vec = vectorizer.transform([profile_text])
    n_neighbors = min(max(candidate_pool, top_n), len(combined_df))
    distances, indices = model.kneighbors(query_vec, n_neighbors=n_neighbors)

    scored_results: List[Dict[str, Any]] = []
    # Determine match type from profile or record
    match_type = profile.get("desired_program_type") or profile.get("match_type")

    for dist, idx in zip(distances[0], indices[0]):
        record = combined_df.iloc[idx].to_dict()
        similarity = 1 - float(dist)

        eligibility = evaluate_eligibility(profile, record, match_type=match_type)
        final_score, rule_score, adj_similarity = compute_final_score(similarity, eligibility)

        # Prioritize explicit field-of-study preferences in the final score.
        field_bonus = 0.0
        field_of_study = str(profile.get("field_of_study") or "").strip()
        if field_of_study and field_of_study.lower() not in ["education_loan", "all fields"]:
            passed_reasons = (eligibility.get("reasons", {}) or {}).get("passed", []) or []
            failed_reasons = (eligibility.get("reasons", {}) or {}).get("failed", []) or []
            passed_text = " ".join(passed_reasons).lower()
            failed_text = " ".join(failed_reasons).lower()

            # If eligibility rules explicitly say the field of study matches, give a strong boost.
            if "field of study" in passed_text:
                field_bonus += 0.10
            # If rules say the field of study does NOT match, penalize.
            if "field of study" in failed_text:
                field_bonus -= 0.10

            # Also look directly for the preferred field string inside the record text
            # (name, description, eligibility, program/loan type).
            field_lower = field_of_study.lower()
            record_blob = " ".join(
                str(part or "").lower()
                for part in [
                    record.get("program_type"),
                    record.get("loan_type"),
                    record.get("name"),
                    record.get("description"),
                    record.get("eligibility"),
                ]
            )
            if field_lower and field_lower in record_blob:
                field_bonus += 0.15
            else:
                # Small penalty when the preferred field is clearly not mentioned.
                field_bonus -= 0.05

        boosted_final = max(0.0, min(1.0, final_score + field_bonus))

        record.update(
            {
                "similarity_score": adj_similarity,
                "rule_score": rule_score,
                "final_score": boosted_final,
                "eligibility_status": "eligible" if eligibility.get("eligible") else "ineligible",
                "eligibility_reasons": eligibility.get("reasons", {}),
            }
        )
        scored_results.append(record)

    # Rank strictly by final score (highest first) so the best matches
    # always appear at the top of the list.
    ranked = sorted(scored_results, key=lambda rec: rec.get("final_score", 0.0), reverse=True)
    cleaned_ranked = []
    for rec in ranked:
        cleaned_rec = {k: _clean_value(v) for k, v in rec.items()}
        # Ensure name is cleaned
        if "name" in cleaned_rec:
            cleaned_rec["name"] = _clean_name(str(cleaned_rec.get("name", "")))
        cleaned_ranked.append(cleaned_rec)

    scholarships = [rec for rec in cleaned_ranked if rec.get("record_type") == "scholarship"][:top_n]
    loans = [rec for rec in cleaned_ranked if rec.get("record_type") == "loan"][:top_n]
    combined_top = cleaned_ranked[:top_n]

    why_accepted: List[str] = []
    why_rejected: List[str] = []
    for rec in combined_top:
        reasons = rec.get("eligibility_reasons", {}) or {}
        why_accepted.extend(reasons.get("passed", []) or [])
        why_rejected.extend(reasons.get("failed", []) or [])

    return {
        "scholarships": scholarships,
        "loans": loans,
        "combined": combined_top,
        "explanations": {
            "why_accepted": why_accepted,
            "why_rejected": why_rejected,
        },
    }


__all__ = ["match_profile"]




