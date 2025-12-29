"""Utility helpers for loading raw scholarship and loan CSV files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

DATA_FILENAMES = {
    "scholarships": "scholarships.csv",
    "loans": "loans.csv",
}

# backend/scholarship_loan_matcher_ml/preprocessing -> parents[2] == backend
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _resolve_csv_path(
    data_dir: Path,
    filename: Optional[str],
    dataset_key: str,
) -> Path:
    target_name = filename or DATA_FILENAMES[dataset_key]
    csv_path = (data_dir / target_name).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file for '{dataset_key}' not found at {csv_path}."
        )
    return csv_path


def _read_csv(csv_path: Path) -> pd.DataFrame:
    """Read a CSV with safe defaults and trimmed headers."""
    try:
        df = pd.read_csv(
            csv_path,
            dtype=str,  # keep raw text; downstream steps will cast as needed
            keep_default_na=False,
            na_values=["", "NA", "N/A", "None"],
            on_bad_lines="skip",
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

    df.columns = [col.strip() for col in df.columns]
    return df


def load_scholarships(
    data_dir: Path = DEFAULT_DATA_DIR,
    filename: Optional[str] = None,
) -> pd.DataFrame:
    """Load the scholarships CSV into a pandas DataFrame."""
    csv_path = _resolve_csv_path(Path(data_dir), filename, "scholarships")
    return _read_csv(csv_path)


def load_loans(
    data_dir: Path = DEFAULT_DATA_DIR,
    filename: Optional[str] = None,
) -> pd.DataFrame:
    """Load the loans CSV into a pandas DataFrame."""
    csv_path = _resolve_csv_path(Path(data_dir), filename, "loans")
    return _read_csv(csv_path)


def load_all_datasets(
    data_dir: Path = DEFAULT_DATA_DIR,
    overrides: Optional[Dict[str, str]] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Load all supported datasets.

    Args:
        data_dir: Optional base directory containing the CSV files.
        overrides: Optional mapping to override default filenames for
            specific datasets. E.g. {"scholarships": "latest.csv"}.

    Returns:
        Dictionary keyed by dataset name with pandas DataFrames.
    """
    overrides = overrides or {}
    scholarships_df = load_scholarships(
        data_dir=data_dir,
        filename=overrides.get("scholarships"),
    )
    loans_df = load_loans(
        data_dir=data_dir,
        filename=overrides.get("loans"),
    )

    return {
        "scholarships": scholarships_df,
        "loans": loans_df,
    }


