"""Scholarship data cleaning module - refactored from scholarship_data_cleaner.py."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical scholarship schema fields
CANONICAL_SCHOLARSHIP_FIELDS = [
    "name",
    "provider",
    "scholarship_type",
    "description",
    "eligibility",
    "benefits",
    "deadline",
    "url",
    "country",
    "degree_level",
    "field_of_study",
    "financial_need_required",
    "source",
]


def clean_scholarships(raw_path: str | Path, output_path: str | Path) -> Dict[str, int | float]:
    """
    Clean raw scholarship CSV and output standardized CSV.

    Args:
        raw_path: Path to raw_scholarships.csv from master_scraper
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

    logger.info(f"Loading raw scholarships from {raw_path}")
    try:
        df = pd.read_csv(raw_path, encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to load raw CSV: {e}")
        raise

    original_count = len(df)
    logger.info(f"Loaded {original_count} raw scholarship records")

    # Track statistics
    stats = {
        "rows_input": original_count,
        "duplicates_removed": 0,
        "invalid_rows_fixed": 0,
    }

    # Standardize columns to canonical schema
    df = _standardize_scholarship_columns(df)
    df = _remove_duplicates_scholarships(df, stats)
    df = _clean_text_fields_scholarships(df)
    df = _extract_funding_amount_scholarships(df)
    df = _extract_deadline_scholarships(df)
    df = _clean_eligibility_scholarships(df)
    df = _add_scholarship_type(df)
    df = _add_eligibility_region(df)
    df = _map_to_canonical_schema_scholarships(df)
    df = _remove_empty_rows_scholarships(df, stats)
    df = _add_data_quality_score_scholarships(df)

    # Ensure all canonical fields exist
    for field in CANONICAL_SCHOLARSHIP_FIELDS:
        if field not in df.columns:
            df[field] = 'N/A'

    # Reorder to canonical schema
    df = df[CANONICAL_SCHOLARSHIP_FIELDS]

    final_count = len(df)
    stats["rows_output"] = final_count

    logger.info(f"Saving cleaned scholarships to {output_path}")
    df.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"Cleaned {final_count} scholarship records saved")

    return stats


def _standardize_scholarship_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw columns to internal standard names."""
    logger.info("Standardizing column names...")

    # Map common variations to standard names
    column_mapping = {
        'application_url': 'url',
        'eligible_region': 'country',
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

    return df


def _remove_duplicates_scholarships(df: pd.DataFrame, stats: Dict) -> pd.DataFrame:
    """Remove duplicate scholarships."""
    logger.info("Removing duplicates...")
    initial_count = len(df)

    # Remove exact duplicates based on name and source
    df = df.drop_duplicates(subset=['name', 'source'], keep='first')

    # Remove near-duplicates (same name)
    df = df.drop_duplicates(subset=['name'], keep='first')

    removed = initial_count - len(df)
    stats["duplicates_removed"] = removed
    logger.info(f"Removed {removed} duplicates. Remaining: {len(df)}")
    return df


def _clean_text_fields_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize text fields."""
    logger.info("Cleaning text fields...")
    text_columns = ['name', 'description', 'eligibility', 'contact']

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            df[col] = df[col].replace(['N/A', 'n/a', 'NA', 'None', 'none', '', 'nan'], 'N/A')
            df[col] = df[col].str.replace(r'<[^>]+>', '', regex=True)

    logger.info("Text fields cleaned")
    return df


def _extract_funding_amount_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and standardize funding amounts."""
    logger.info("Extracting and standardizing funding amounts...")

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
                return f"Rs. {amount}"

        if '%' in text:
            return text.strip()

        if any(word in text.lower() for word in ['varies', 'based', 'up to', 'minimum']):
            return text.strip()

        return text if text else 'N/A'

    if 'funding_amount' in df.columns:
        df['funding_amount'] = df['funding_amount'].apply(extract_amount)

    logger.info("Funding amounts standardized")
    return df


def _extract_deadline_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and standardize deadline information."""
    logger.info("Extracting and standardizing deadlines...")

    def extract_deadline_date(text):
        if text == 'N/A' or pd.isna(text):
            return 'N/A'

        text = str(text).strip()
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        if any(word in text.lower() for word in ['week', 'month', 'day', 'hour']):
            return text.strip()

        if any(word in text.lower() for word in ['ongoing', 'rolling', 'continuous']):
            return 'Ongoing'

        return text if text else 'N/A'

    if 'deadline' in df.columns:
        df['deadline'] = df['deadline'].apply(extract_deadline_date)

    logger.info("Deadlines standardized")
    return df


def _clean_eligibility_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and structure eligibility criteria."""
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


def _add_scholarship_type(df: pd.DataFrame) -> pd.DataFrame:
    """Categorize scholarship type based on name and description."""
    logger.info("Categorizing scholarship types...")

    def categorize_scholarship(row):
        text = (str(row.get('name', '')) + ' ' + str(row.get('description', ''))).lower()

        if any(word in text for word in ['merit', 'academic', 'performance', 'exam', 'gpa']):
            return 'Merit-Based'
        elif any(word in text for word in ['need', 'income', 'poor', 'low-income', 'financial']):
            return 'Need-Based'
        elif any(word in text for word in ['sport', 'athletic', 'talent']):
            return 'Talent-Based'
        elif any(word in text for word in ['bursary', 'grant']):
            return 'Grant/Bursary'
        elif any(word in text for word in ['government', 'mahapola']):
            return 'Government'
        else:
            return 'General'

    df['scholarship_type'] = df.apply(categorize_scholarship, axis=1)
    logger.info("Scholarship types categorized")
    return df


def _add_eligibility_region(df: pd.DataFrame) -> pd.DataFrame:
    """Extract eligible regions/countries."""
    logger.info("Extracting eligible regions...")

    def extract_region(row):
        text = (str(row.get('name', '')) + ' ' + str(row.get('description', '')) +
                ' ' + str(row.get('eligibility', ''))).lower()

        if 'sri lanka' in text or 'sliit' in text or 'ousl' in text:
            return 'Sri Lanka'
        elif any(word in text for word in ['local', 'domestic']):
            return 'Local'
        elif any(word in text for word in ['foreign', 'overseas', 'international', 'abroad']):
            return 'International'
        elif any(word in text for word in ['both', 'local or']):
            return 'Both'
        else:
            return 'Unknown'

    df['country'] = df.apply(extract_region, axis=1)
    logger.info("Eligible regions extracted")
    return df


def _map_to_canonical_schema_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Map internal fields to canonical schema."""
    logger.info("Mapping to canonical schema...")

    # Map provider from source
    if 'provider' not in df.columns:
        df['provider'] = df.get('source', 'N/A')

    # Map benefits (extract from description if not present)
    if 'benefits' not in df.columns:
        df['benefits'] = 'N/A'

    # Map degree_level (extract from description/eligibility)
    if 'degree_level' not in df.columns:
        def extract_degree_level(row):
            text = (str(row.get('description', '')) + ' ' + str(row.get('eligibility', ''))).lower()
            if any(word in text for word in ['undergraduate', 'bachelor', 'bsc', 'ba']):
                return 'Undergraduate'
            elif any(word in text for word in ['postgraduate', 'master', 'masters', 'msc', 'ma', 'phd', 'doctorate']):
                return 'Postgraduate'
            else:
                return 'N/A'
        df['degree_level'] = df.apply(extract_degree_level, axis=1)

    # Map field_of_study
    if 'field_of_study' not in df.columns:
        df['field_of_study'] = 'N/A'

    # Map financial_need_required
    if 'financial_need_required' not in df.columns:
        def extract_financial_need(row):
            text = (str(row.get('name', '')) + ' ' + str(row.get('description', ''))).lower()
            if any(word in text for word in ['need', 'income', 'poor', 'low-income', 'financial']):
                return 'yes'
            return 'no'
        df['financial_need_required'] = df.apply(extract_financial_need, axis=1)

    logger.info("Mapped to canonical schema")
    return df


def _remove_empty_rows_scholarships(df: pd.DataFrame, stats: Dict) -> pd.DataFrame:
    """Remove rows where critical fields are all N/A."""
    logger.info("Removing rows with missing critical information...")
    initial_count = len(df)

    df = df[(df['name'] != 'N/A') & (df['source'] != 'N/A')]

    removed = initial_count - len(df)
    stats["invalid_rows_fixed"] = removed
    logger.info(f"Removed {removed} rows with missing critical info. Remaining: {len(df)}")
    return df


def _add_data_quality_score_scholarships(df: pd.DataFrame) -> pd.DataFrame:
    """Add data quality score (0-100) based on field completeness."""
    logger.info("Calculating data quality scores...")

    def calculate_quality_score(row):
        score = 0
        fields = ['name', 'description', 'eligibility', 'funding_amount', 'deadline', 'contact']

        for field in fields:
            if field in row.index and row[field] != 'N/A' and pd.notna(row[field]):
                score += 100 / len(fields)

        return round(score, 2)

    df['data_quality_score'] = df.apply(calculate_quality_score, axis=1)
    logger.info("Data quality scores added")
    return df


