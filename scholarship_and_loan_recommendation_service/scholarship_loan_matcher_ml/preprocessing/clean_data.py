"""Cleaning and normalization pipeline for scholarships and loans."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from .load_data import DEFAULT_DATA_DIR, load_all_datasets

logger = logging.getLogger(__name__)

# Mapping of canonical column names to potential aliases encountered in scraped CSVs.
SCHOLARSHIP_COLUMN_ALIASES: Dict[str, List[str]] = {
    "name": ["name", "scholarship_name", "program_name", "title"],
    "program_type": ["scholarship_type", "type", "category"],
    "region": ["eligible_region", "region", "country"],
    "description": ["description", "details", "summary"],
    "eligibility": ["eligibility", "eligibility_requirements", "criteria"],
    "funding_amount": [
        "funding_amount",
        "amount",
        "award_amount",
        "maximum_award",
        "value",
    ],
    "deadline": ["deadline", "application_deadline", "due_date"],
    "contact": ["contact", "contact_info", "contact_information"],
    "application_url": ["application_url", "apply_url", "url", "website_url"],
    "source": ["source", "provider", "origin"],
    "data_quality_score": ["data_quality_score", "quality_score"],
    "scrape_date": ["scrape_date", "collected_at", "harvested_on"],
}

LOAN_COLUMN_ALIASES: Dict[str, List[str]] = {
    "name": ["name", "loan_product_name", "product_name", "title"],
    "loan_type": ["loan_type", "type", "category"],
    "loan_duration_category": ["loan_duration_category", "duration_category"],
    "description": ["description", "details", "summary"],
    "eligibility": ["eligibility", "criteria", "requirements"],
    "maximum_loan_amount": [
        "maximum_loan_amount",
        "max_loan_amount",
        "funding_amount",
        "amount",
    ],
    "minimum_loan_amount": [
        "minimum_loan_amount",
        "min_loan_amount",
        "min_amount",
    ],
    "funding_amount": ["funding_amount", "total_amount", "principal"],
    "interest_rate": ["interest_rate", "rate"],
    "repayment_period": ["repayment_period", "repayment_terms", "tenure"],
    "age_criteria": ["age_criteria", "age_requirement"],
    "income_criteria": ["income_criteria", "income_requirement"],
    "contact": ["contact", "contact_info", "contact_information"],
    "application_url": ["application_url", "apply_url", "url", "website_url"],
    "source": ["source", "provider", "origin"],
    "data_quality_score": ["data_quality_score", "quality_score"],
    "scrape_date": ["scrape_date", "collected_at", "harvested_on"],
    "deadline": ["deadline", "application_deadline"],
    "special_benefits": ["special_benefits", "benefits", "perks"],
    "bank_name": ["bank_name", "provider", "institution_name"],
    "documents_required": ["documents_required", "required_documents"],
}

COMMON_EMPTY_VALUES = {
    "",
    "n/a",
    "na",
    "none",
    "null",
    "n.a",
    "n.a.",
    "n/a - ongoing",
    "n/a - ongoing scheme",
}

NUMERIC_COLUMNS = {
    "funding_amount",
    "maximum_loan_amount",
    "minimum_loan_amount",
    "data_quality_score",
    "interest_rate",
}

TEXT_DEFAULTS = {
    "program_type": "unspecified",
    "loan_type": "unspecified",
    "deadline": "rolling",
}

CURRENCY_PATTERN = re.compile(r"[-+]?\d[\d,\.]*")


def _normalize_colname(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", name.strip().lower())


def _build_column_map(
    df: pd.DataFrame,
    alias_map: Dict[str, List[str]],
) -> Dict[str, str]:
    """
    Build rename mapping for a dataframe according to a canonical schema.

    Returns:
        Dictionary keyed by original column name with canonical target names.
    """
    normalized_lookup = {_normalize_colname(col): col for col in df.columns}
    rename_map: Dict[str, str] = {}

    for canonical, aliases in alias_map.items():
        matched_column: Optional[str] = None
        for alias in aliases:
            alias_norm = _normalize_colname(alias)
            # direct match
            if alias_norm in normalized_lookup:
                matched_column = normalized_lookup[alias_norm]
                break
            # fuzzy contains match (handles pluralization or prefixes)
            for normalized_col, original_col in normalized_lookup.items():
                if alias_norm in normalized_col or normalized_col in alias_norm:
                    matched_column = original_col
                    break
            if matched_column:
                break
        if matched_column:
            rename_map[matched_column] = canonical

    missing_columns = [
        canonical
        for canonical in alias_map.keys()
        if canonical not in rename_map.values()
    ]
    if missing_columns:
        logger.debug("Columns not found for %s: %s", df.__class__.__name__, missing_columns)

    return rename_map


def _ensure_columns(df: pd.DataFrame, canonical_columns: Iterable[str]) -> pd.DataFrame:
    for column in canonical_columns:
        if column not in df.columns:
            df[column] = pd.NA
    return df


def _standardize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    lowered = {val.lower() for val in COMMON_EMPTY_VALUES}
    for column in df.columns:
        df[column] = df[column].apply(
            lambda value: pd.NA
            if isinstance(value, str) and value.strip().lower() in lowered
            else value
        )
    return df


def _strip_text_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .replace("", pd.NA)
            )
    return df


def _normalize_numeric_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:

            def _parse_value(value: object) -> Optional[float]:
                if value is None or (isinstance(value, float) and np.isnan(value)):
                    return np.nan
                if isinstance(value, (int, float)):
                    return float(value)
                value_str = str(value)
                match = CURRENCY_PATTERN.search(value_str)
                if not match:
                    return np.nan
                cleaned = match.group(0).replace(",", "")
                try:
                    return float(cleaned)
                except ValueError:
                    return np.nan

            df[column] = df[column].map(_parse_value).astype("Float64")
    return df


def _drop_duplicates(df: pd.DataFrame, subset: Iterable[str]) -> pd.DataFrame:
    existing_subset = [col for col in subset if col in df.columns]
    if not existing_subset:
        return df
    return df.drop_duplicates(subset=existing_subset, keep="first")


def _fill_defaults(df: pd.DataFrame, defaults: Dict[str, str]) -> pd.DataFrame:
    for column, default_value in defaults.items():
        if column in df.columns:
            df[column] = df[column].fillna(default_value)
    return df


def _clean_generic_df(
    df: pd.DataFrame,
    alias_map: Dict[str, List[str]],
) -> pd.DataFrame:
    if df.empty:
        df = pd.DataFrame(columns=list(alias_map.keys()))
    else:
        rename_map = _build_column_map(df, alias_map)
        df = df.rename(columns=rename_map)

    df = _ensure_columns(df, alias_map.keys())
    df = _standardize_missing_values(df)
    text_columns = [col for col in alias_map.keys() if col not in NUMERIC_COLUMNS]
    df = _strip_text_columns(df, text_columns)
    df = _normalize_numeric_columns(df, NUMERIC_COLUMNS)
    df = _fill_defaults(df, TEXT_DEFAULTS)
    return df


def clean_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the scholarship dataframe."""
    cleaned = _clean_generic_df(df, SCHOLARSHIP_COLUMN_ALIASES)
    cleaned["record_type"] = "scholarship"
    cleaned = _drop_duplicates(cleaned, subset=["name", "program_type", "deadline"])
    column_order = ["record_type"] + list(SCHOLARSHIP_COLUMN_ALIASES.keys())
    return cleaned[column_order]


def clean_loans(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the loan dataframe."""
    cleaned = _clean_generic_df(df, LOAN_COLUMN_ALIASES)
    cleaned["record_type"] = "loan"
    cleaned = _drop_duplicates(
        cleaned,
        subset=["name", "loan_type", "application_url"],
    )
    column_order = ["record_type"] + list(LOAN_COLUMN_ALIASES.keys())
    return cleaned[column_order]


def combine_datasets(
    scholarships_df: pd.DataFrame,
    loans_df: pd.DataFrame,
) -> pd.DataFrame:
    """Combine cleaned scholarship and loan dataframes."""
    scholarships_df = scholarships_df.copy()
    loans_df = loans_df.copy()

    unified_columns = list(
        dict.fromkeys(
            ["record_type"]
            + list(SCHOLARSHIP_COLUMN_ALIASES.keys())
            + list(LOAN_COLUMN_ALIASES.keys())
        )
    )

    for column in unified_columns:
        if column not in scholarships_df.columns:
            scholarships_df[column] = pd.NA
        if column not in loans_df.columns:
            loans_df[column] = pd.NA

    combined = pd.concat(
        [scholarships_df[unified_columns], loans_df[unified_columns]],
        ignore_index=True,
        sort=False,
    )
    return combined


def preprocess_data(
    data_dir: Path = DEFAULT_DATA_DIR,
) -> pd.DataFrame:
    """
    High-level helper for downstream consumers.

    Loads raw CSVs, cleans individual datasets, and returns a unified dataframe.
    """
    datasets = load_all_datasets(data_dir=data_dir)
    scholarships_df = clean_scholarships(datasets["scholarships"])
    loans_df = clean_loans(datasets["loans"])
    combined_df = combine_datasets(scholarships_df, loans_df)
    logger.info("Preprocessing complete. %s records ready.", len(combined_df))
    return combined_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    merged = preprocess_data()
    output_path = DEFAULT_DATA_DIR / "preprocessed_combined.parquet"
    merged.to_parquet(output_path, index=False)
    logger.info("Combined dataset saved to %s", output_path)

