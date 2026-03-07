"""Load cleaned scholarship and loan datasets with fallback to original data."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed_data"
BACKEND_DIR = BASE_DIR.parents[0]
DATA_DIR = BACKEND_DIR / "data"

SCHOLARSHIPS_PATH = PROCESSED_DIR / "scholarships_clean.csv"
LOANS_PATH = PROCESSED_DIR / "loans_clean.csv"

REQUIRED_COLUMNS: List[str] = ["record_type", "name"]
OPTIONAL_COLUMNS: List[str] = ["description", "eligibility"]

logger = logging.getLogger(__name__)


def _validate(df: pd.DataFrame, name: str, strict: bool = True) -> None:
    missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_required:
        raise ValueError(f"{name} is missing required columns: {missing_required}")
    
    if strict:
        missing_optional = [col for col in OPTIONAL_COLUMNS if col not in df.columns]
        if missing_optional:
            logger.warning(f"{name} is missing optional columns: {missing_optional}")


def _load_csv(path: Path, name: str, strict: bool = True) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{name} file not found at {path}")
    df = pd.read_csv(path)
    _validate(df, name, strict=strict)
    return df


def _load_and_clean_fallback() -> Dict[str, pd.DataFrame]:
    """
    Fallback: Load original CSVs and clean them on-the-fly.
    """
    logger.warning("Cleaned datasets not found. Loading and cleaning original data...")
    
    try:
        from scholarship_loan_matcher_ml.preprocessing.load_data import load_all_datasets
        from scholarship_loan_matcher_ml.preprocessing.clean_data import clean_scholarships, clean_loans
    except ImportError:
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))
        from scholarship_loan_matcher_ml.preprocessing.load_data import load_all_datasets
        from scholarship_loan_matcher_ml.preprocessing.clean_data import clean_scholarships, clean_loans
    
    try:
        datasets = load_all_datasets(data_dir=DATA_DIR)
        scholarships_df = clean_scholarships(datasets["scholarships"])
        loans_df = clean_loans(datasets["loans"])
        
        # Ensure record_type is set
        if "record_type" not in scholarships_df.columns:
            scholarships_df["record_type"] = "scholarship"
        if "record_type" not in loans_df.columns:
            loans_df["record_type"] = "loan"
        
        logger.info("Fallback cleaning complete: %d scholarships, %d loans", 
                    len(scholarships_df), len(loans_df))
        
        return {"scholarships": scholarships_df, "loans": loans_df}
    except Exception as e:
        logger.error(f"Fallback cleaning failed: {e}")
        raise


def load_cleaned_datasets(
    scholarships_path: Path | None = None,
    loans_path: Path | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Load cleaned scholarship and loan datasets from processed_data/.
    Falls back to loading and cleaning original data if cleaned files don't exist.
    """
    scholarships_path = scholarships_path or SCHOLARSHIPS_PATH
    loans_path = loans_path or LOANS_PATH

    # Try to load cleaned files first
    if scholarships_path.exists() and loans_path.exists():
        try:
            scholarships_df = _load_csv(Path(scholarships_path), "scholarships")
            loans_df = _load_csv(Path(loans_path), "loans")
            return {"scholarships": scholarships_df, "loans": loans_df}
        except Exception as e:
            logger.warning(f"Error loading cleaned files: {e}. Falling back to original data.")
    
    # Fallback to loading and cleaning original data
    return _load_and_clean_fallback()


__all__ = ["load_cleaned_datasets", "SCHOLARSHIPS_PATH", "LOANS_PATH"]




