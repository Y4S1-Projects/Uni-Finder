"""Loans data cleaning module - refactored from loans_data_cleaner.py."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical loan schema fields
CANONICAL_LOAN_FIELDS = [
    "name",
    "provider",
    "loan_type",
    "interest_rate",
    "eligibility",
    "repayment_terms",
    "max_amount",
    "deadline",
    "url",
    "source",
]


def clean_loans(raw_path: str | Path, output_path: str | Path) -> Dict[str, int | float]:
    """
    Clean raw loan CSV and output standardized CSV.

    Args:
        raw_path: Path to raw_loans.csv from master_scraper
        output_path: Path where cleaned CSV will be written

    Returns:
        Summary dictionary with:
            - rows_input: Number of rows in raw CSV
            - rows_output: Number of rows after cleaning
            - duplicates_removed: Number of duplicate rows removed
            - invalid_rows_fixed: Number of rows with missing/invalid fields fixed
    """
    raw_path = Path(raw_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading raw loans from {raw_path}")
    try:
        df = pd.read_csv(raw_path, encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to load raw CSV: {e}")
        raise

    original_count = len(df)
    logger.info(f"Loaded {original_count} raw loan records")

    # Track statistics
    stats = {
        "rows_input": original_count,
        "duplicates_removed": 0,
        "invalid_rows_fixed": 0,
    }

    # Standardize columns
    df = _standardize_loan_columns(df)
    df = _remove_duplicates_loans(df, stats)
    df = _clean_text_fields_loans(df)
    df = _extract_loan_amounts(df)
    df = _extract_repayment_period(df)
    df = _extract_interest_rate(df)
    df = _extract_age_range(df)
    df = _clean_eligibility_loans(df)
    df = _add_loan_type(df)
    df = _add_loan_duration_category(df)
    df = _map_to_canonical_schema_loans(df)
    df = _remove_empty_rows_loans(df, stats)
    df = _add_data_quality_score_loans(df)

    # Ensure all canonical fields exist
    for field in CANONICAL_LOAN_FIELDS:
        if field not in df.columns:
            df[field] = 'N/A'

    # Reorder to canonical schema
    df = df[CANONICAL_LOAN_FIELDS]

    final_count = len(df)
    stats["rows_output"] = final_count

    logger.info(f"Saving cleaned loans to {output_path}")
    df.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"Cleaned {final_count} loan records saved")

    return stats


def _standardize_loan_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names across different sources."""
    logger.info("Standardizing column names...")

    # Normalize name columns
    if 'bank_name' in df.columns and 'name' not in df.columns:
        df['name'] = df['bank_name']

    if 'loan_product_name' in df.columns:
        if 'name' not in df.columns or df['name'].isna().all():
            df['name'] = df['loan_product_name']

    if 'contact_info' in df.columns and 'contact' not in df.columns:
        df['contact'] = df['contact_info']

    if 'website_url' in df.columns and 'application_url' not in df.columns:
        df['application_url'] = df['website_url']

    # Map to standard names
    column_mapping = {
        'application_url': 'url',
        'maximum_loan_amount': 'max_amount',
        'repayment_period': 'repayment_terms',
    }

    df = df.rename(columns=column_mapping)

    # Ensure standard columns exist
    standard_cols = {
        'name', 'description', 'eligibility', 'funding_amount',
        'deadline', 'contact', 'url', 'source', 'scrape_date'
    }

    for col in standard_cols:
        if col not in df.columns:
            df[col] = 'N/A'

    logger.info(f"Standardized to {len(df.columns)} total columns")
    return df


def _remove_duplicates_loans(df: pd.DataFrame, stats: Dict) -> pd.DataFrame:
    """Remove duplicate loans."""
    logger.info("Removing duplicates...")
    initial_count = len(df)

    if 'name' in df.columns and 'source' in df.columns:
        df = df.drop_duplicates(subset=['name', 'source'], keep='first')

    df = df.drop_duplicates(subset=['name'], keep='first')

    removed = initial_count - len(df)
    stats["duplicates_removed"] = removed
    logger.info(f"Removed {removed} duplicates. Remaining: {len(df)}")
    return df


def _clean_text_fields_loans(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize text fields."""
    logger.info("Cleaning text fields...")
    text_columns = ['name', 'description', 'eligibility', 'contact', 'loan_product_name']

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            df[col] = df[col].replace(['N/A', 'n/a', 'NA', 'None', 'none', '', 'nan'], 'N/A')
            df[col] = df[col].str.replace(r'<[^>]+>', '', regex=True)

    logger.info("Text fields cleaned")
    return df


def _extract_loan_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and standardize loan amounts."""
    logger.info("Extracting and standardizing loan amounts...")

    def extract_amount(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text)
        patterns = [
            r'Rs\.?\s*([\d,]+(?:\.\d{2})?)',
            r'LKR\s*([\d,]+(?:\.\d{2})?)',
            r'\$([\d,]+(?:\.\d{2})?)',
            r'USD\s*([\d,]+(?:\.\d{2})?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                try:
                    float(amount)
                    return f"Rs. {amount}"
                except:
                    return f"Rs. {amount}"

        if '%' in text:
            return text.strip()

        if any(word in text.lower() for word in ['varies', 'based', 'up to', 'minimum', 'maximum']):
            return text.strip()

        return text if text else 'N/A'

    for col in ['funding_amount', 'max_amount', 'minimum_loan_amount']:
        if col in df.columns:
            df[col] = df[col].apply(extract_amount)

    logger.info("Loan amounts standardized")
    return df


def _extract_repayment_period(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and standardize repayment periods."""
    logger.info("Extracting repayment periods...")

    def extract_period(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text).strip()

        year_match = re.search(r'(\d+)\s*(?:year|yr|years|yrs)', text, re.IGNORECASE)
        if year_match:
            years = year_match.group(1)
            return f"{years} years"

        month_match = re.search(r'(\d+)\s*(?:month|months|mo)', text, re.IGNORECASE)
        if month_match:
            months = month_match.group(1)
            return f"{months} months"

        install_match = re.search(r'(\d+)\s*(?:installment|installments|EMI)', text, re.IGNORECASE)
        if install_match:
            installments = install_match.group(1)
            return f"{installments} installments"

        return text if text else 'N/A'

    if 'repayment_terms' in df.columns:
        df['repayment_terms'] = df['repayment_terms'].apply(extract_period)
    elif 'deadline' in df.columns:
        df['repayment_terms'] = df['deadline'].apply(extract_period)

    logger.info("Repayment periods extracted")
    return df


def _extract_interest_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Extract interest rate information."""
    logger.info("Extracting interest rates...")

    def extract_rate(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text).strip()

        percent_match = re.search(r'([\d.]+)\s*%', text)
        if percent_match:
            rate = percent_match.group(1)
            return f"{rate}%"

        if any(word in text.lower() for word in ['free', 'zero', '0%', 'interest-free']):
            return 'Interest-Free'

        if 'competitive' in text.lower() or 'market' in text.lower():
            return text.strip()

        return text if text else 'N/A'

    if 'interest_rate' in df.columns:
        df['interest_rate'] = df['interest_rate'].apply(extract_rate)

    logger.info("Interest rates extracted")
    return df


def _extract_age_range(df: pd.DataFrame) -> pd.DataFrame:
    """Extract age eligibility range."""
    logger.info("Extracting age ranges...")

    def extract_age(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text).strip()

        age_pattern = r'(\d+)\s*(?:to|-|and)\s*(\d+)'
        match = re.search(age_pattern, text)
        if match:
            min_age = match.group(1)
            max_age = match.group(2)
            return f"{min_age}-{max_age} years"

        single_age = re.search(r'(\d+)\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if single_age:
            return f"{single_age.group(1)}+ years"

        return text if text else 'N/A'

    if 'age_criteria' in df.columns:
        df['age_criteria'] = df['age_criteria'].apply(extract_age)

    logger.info("Age ranges extracted")
    return df


def _clean_eligibility_loans(df: pd.DataFrame) -> pd.DataFrame:
    """Clean eligibility criteria."""
    logger.info("Cleaning eligibility criteria...")

    def clean_eligibility_text(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text).strip()
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'\n+', '\n', text)

        if len(text) > 500:
            text = text[:500] + "..."

        return text if text else 'N/A'

    if 'eligibility' in df.columns:
        df['eligibility'] = df['eligibility'].apply(clean_eligibility_text)

    logger.info("Eligibility criteria cleaned")
    return df


def _add_loan_type(df: pd.DataFrame) -> pd.DataFrame:
    """Categorize loan type."""
    logger.info("Categorizing loan types...")

    def categorize_loan(row):
        text = (str(row.get('name', '')) + ' ' + str(row.get('description', ''))).lower()

        if 'government' in text or 'mohe' in text:
            return 'Government Loan'
        elif any(bank in text for bank in ['bank', 'boc', 'commercial', 'peoples', 'hnb', 'nsb', 'pabc']):
            return 'Bank Loan'
        elif 'buddhi' in text or 'nsb' in text:
            return 'NSB Loan'
        elif 'dai' in text or 'awarding' in text:
            return 'DAI Related'
        else:
            return 'Other'

    df['loan_type'] = df.apply(categorize_loan, axis=1)
    logger.info("Loan types categorized")
    return df


def _add_loan_duration_category(df: pd.DataFrame) -> pd.DataFrame:
    """Categorize loan duration."""
    logger.info("Categorizing loan duration...")

    def categorize_duration(row):
        text = str(row.get('repayment_terms', '')).lower()

        if pd.isna(text) or text == 'N/A':
            return 'Unknown'

        year_match = re.search(r'(\d+)', text)
        if year_match:
            years = int(year_match.group(1))
            if years <= 3:
                return 'Short-term (≤3 years)'
            elif years <= 7:
                return 'Medium-term (4-7 years)'
            else:
                return 'Long-term (>7 years)'

        return 'Unknown'

    df['loan_duration_category'] = df.apply(categorize_duration, axis=1)
    logger.info("Loan duration categories added")
    return df


def _map_to_canonical_schema_loans(df: pd.DataFrame) -> pd.DataFrame:
    """Map internal fields to canonical schema."""
    logger.info("Mapping to canonical schema...")

    # Map provider from source or bank_name
    if 'provider' not in df.columns:
        if 'bank_name' in df.columns:
            df['provider'] = df['bank_name']
        else:
            df['provider'] = df.get('source', 'N/A')

    logger.info("Mapped to canonical schema")
    return df


def _remove_empty_rows_loans(df: pd.DataFrame, stats: Dict) -> pd.DataFrame:
    """Remove rows with missing critical information."""
    logger.info("Removing rows with missing critical information...")
    initial_count = len(df)

    df = df[df['name'] != 'N/A']

    removed = initial_count - len(df)
    stats["invalid_rows_fixed"] = removed
    logger.info(f"Removed {removed} rows. Remaining: {len(df)}")
    return df


def _add_data_quality_score_loans(df: pd.DataFrame) -> pd.DataFrame:
    """Add data quality score."""
    logger.info("Calculating data quality scores...")

    def calculate_quality_score(row):
        score = 0
        key_fields = ['name', 'description', 'eligibility', 'funding_amount', 'contact']

        for field in key_fields:
            if field in row.index and row[field] != 'N/A' and pd.notna(row[field]):
                score += 100 / len(key_fields)

        return round(score, 2)

    df['data_quality_score'] = df.apply(calculate_quality_score, axis=1)
    logger.info("Data quality scores added")
    return df


