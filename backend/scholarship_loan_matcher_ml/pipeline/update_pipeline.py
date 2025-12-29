"""Unified dataset update pipeline: scrapers → cleaners → processed data."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import scrapers
from ..scraping.master_scraper import run_master_scraper

# Import cleaners
from ..preprocessing.clean_scholarships import clean_scholarships
from ..preprocessing.clean_loans import clean_loans

logger = logging.getLogger(__name__)

# Directory paths
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "raw_data"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
METADATA_DIR = BASE_DIR / "pipeline"

# File paths
# Master scraper outputs these names, but we'll use the standardized names
MASTER_SCRAPER_SCHOLARSHIPS = RAW_DATA_DIR / "raw_scholarships.csv"
MASTER_SCRAPER_LOANS = RAW_DATA_DIR / "raw_loans.csv"
RAW_SCHOLARSHIPS_PATH = RAW_DATA_DIR / "scholarships_raw.csv"
RAW_LOANS_PATH = RAW_DATA_DIR / "loans_raw.csv"
CLEAN_SCHOLARSHIPS_PATH = PROCESSED_DATA_DIR / "scholarships_clean.csv"
CLEAN_LOANS_PATH = PROCESSED_DATA_DIR / "loans_clean.csv"
LAST_UPDATE_PATH = METADATA_DIR / "last_update.json"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


def _save_last_update_timestamp() -> Dict[str, str]:
    """Save the current timestamp to last_update.json."""
    timestamp_data = {
        "last_update": datetime.now().isoformat(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        with LAST_UPDATE_PATH.open("w", encoding="utf-8") as f:
            json.dump(timestamp_data, f, indent=2)
        logger.info("Saved update timestamp to %s", LAST_UPDATE_PATH)
        return timestamp_data
    except Exception as e:
        logger.warning("Failed to save timestamp: %s", e)
        return timestamp_data


def _load_last_update_timestamp() -> Dict[str, str] | None:
    """Load the last update timestamp from last_update.json."""
    if not LAST_UPDATE_PATH.exists():
        return None
    try:
        with LAST_UPDATE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load timestamp: %s", e)
        return None


def run_full_update() -> Dict[str, Any]:
    """
    Runs scrapers → cleaners → schema normalizer (if needed).

    Returns a summary dictionary detailing:
      - scraper results (success/failure, record counts)
      - cleaner results (rows input/output, duplicates removed, etc.)
      - file paths (raw and cleaned CSV locations)
      - timestamp information
      - overall status

    The pipeline continues running even if individual scrapers or cleaners fail.
    """
    logger.info("=" * 70)
    logger.info("Starting full dataset update pipeline")
    logger.info("=" * 70)

    summary: Dict[str, Any] = {
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "scraper_results": {},
        "cleaner_results": {},
        "file_paths": {
            "raw_scholarships": str(RAW_SCHOLARSHIPS_PATH),
            "raw_loans": str(RAW_LOANS_PATH),
            "clean_scholarships": str(CLEAN_SCHOLARSHIPS_PATH),
            "clean_loans": str(CLEAN_LOANS_PATH),
            "last_update_metadata": str(LAST_UPDATE_PATH),
        },
        "errors": [],
        "warnings": [],
    }

    # Step 1: Run scrapers
    logger.info("Step 1: Running scrapers to generate raw CSVs")
    scraper_success = False
    try:
        scraper_output = run_master_scraper()
        scholarship_count = len(scraper_output.get("scholarships", []))
        loan_count = len(scraper_output.get("loans", []))

        # Rename files to standardized names if master scraper used different names
        if MASTER_SCRAPER_SCHOLARSHIPS.exists() and MASTER_SCRAPER_SCHOLARSHIPS != RAW_SCHOLARSHIPS_PATH:
            logger.info("Renaming %s to %s", MASTER_SCRAPER_SCHOLARSHIPS.name, RAW_SCHOLARSHIPS_PATH.name)
            MASTER_SCRAPER_SCHOLARSHIPS.rename(RAW_SCHOLARSHIPS_PATH)
        if MASTER_SCRAPER_LOANS.exists() and MASTER_SCRAPER_LOANS != RAW_LOANS_PATH:
            logger.info("Renaming %s to %s", MASTER_SCRAPER_LOANS.name, RAW_LOANS_PATH.name)
            MASTER_SCRAPER_LOANS.rename(RAW_LOANS_PATH)

        summary["scraper_results"] = {
            "success": True,
            "scholarships_collected": scholarship_count,
            "loans_collected": loan_count,
            "raw_scholarships_file": str(RAW_SCHOLARSHIPS_PATH),
            "raw_loans_file": str(RAW_LOANS_PATH),
        }
        scraper_success = True
        logger.info(
            "Scrapers completed: %d scholarships, %d loans",
            scholarship_count,
            loan_count,
        )
    except Exception as e:
        error_msg = f"Scraper execution failed: {str(e)}"
        logger.exception(error_msg)
        summary["scraper_results"] = {
            "success": False,
            "error": error_msg,
            "scholarships_collected": 0,
            "loans_collected": 0,
        }
        summary["errors"].append(error_msg)

    # Step 2: Clean scholarships
    logger.info("Step 2: Cleaning scholarship data")
    scholarship_clean_success = False
    if RAW_SCHOLARSHIPS_PATH.exists():
        try:
            clean_stats = clean_scholarships(
                RAW_SCHOLARSHIPS_PATH, CLEAN_SCHOLARSHIPS_PATH
            )
            summary["cleaner_results"]["scholarships"] = {
                "success": True,
                "rows_input": clean_stats.get("rows_input", 0),
                "rows_output": clean_stats.get("rows_output", 0),
                "duplicates_removed": clean_stats.get("duplicates_removed", 0),
                "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
            }
            scholarship_clean_success = True
            logger.info(
                "Scholarship cleaning completed: %d rows input → %d rows output",
                clean_stats.get("rows_input", 0),
                clean_stats.get("rows_output", 0),
            )
        except Exception as e:
            error_msg = f"Scholarship cleaning failed: {str(e)}"
            logger.exception(error_msg)
            summary["cleaner_results"]["scholarships"] = {
                "success": False,
                "error": error_msg,
            }
            summary["errors"].append(error_msg)
    else:
        warning_msg = f"Raw scholarships file not found: {RAW_SCHOLARSHIPS_PATH}"
        logger.warning(warning_msg)
        summary["cleaner_results"]["scholarships"] = {
            "success": False,
            "error": "Raw file not found",
        }
        summary["warnings"].append(warning_msg)

    # Step 3: Clean loans
    logger.info("Step 3: Cleaning loan data")
    loan_clean_success = False
    if RAW_LOANS_PATH.exists():
        try:
            clean_stats = clean_loans(RAW_LOANS_PATH, CLEAN_LOANS_PATH)
            summary["cleaner_results"]["loans"] = {
                "success": True,
                "rows_input": clean_stats.get("rows_input", 0),
                "rows_output": clean_stats.get("rows_output", 0),
                "duplicates_removed": clean_stats.get("duplicates_removed", 0),
                "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
            }
            loan_clean_success = True
            logger.info(
                "Loan cleaning completed: %d rows input → %d rows output",
                clean_stats.get("rows_input", 0),
                clean_stats.get("rows_output", 0),
            )
        except Exception as e:
            error_msg = f"Loan cleaning failed: {str(e)}"
            logger.exception(error_msg)
            summary["cleaner_results"]["loans"] = {
                "success": False,
                "error": error_msg,
            }
            summary["errors"].append(error_msg)
    else:
        warning_msg = f"Raw loans file not found: {RAW_LOANS_PATH}"
        logger.warning(warning_msg)
        summary["cleaner_results"]["loans"] = {
            "success": False,
            "error": "Raw file not found",
        }
        summary["warnings"].append(warning_msg)

    # Step 4: Save timestamp
    logger.info("Step 4: Saving update timestamp")
    timestamp_data = _save_last_update_timestamp()
    summary["timestamp"] = timestamp_data
    summary["last_update"] = timestamp_data.get("timestamp")

    # Determine overall status
    if scraper_success and scholarship_clean_success and loan_clean_success:
        summary["status"] = "success"
        logger.info("=" * 70)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 70)
    elif scraper_success or scholarship_clean_success or loan_clean_success:
        summary["status"] = "partial_success"
        logger.warning("=" * 70)
        logger.warning("Pipeline completed with partial success (some steps failed)")
        logger.warning("=" * 70)
    else:
        summary["status"] = "failed"
        logger.error("=" * 70)
        logger.error("Pipeline failed (all steps failed)")
        logger.error("=" * 70)

    summary["completed_at"] = datetime.now().isoformat()
    summary["duration_seconds"] = (
        datetime.fromisoformat(summary["completed_at"])
        - datetime.fromisoformat(summary["started_at"])
    ).total_seconds()

    return summary


def get_last_update_info() -> Dict[str, Any] | None:
    """
    Retrieve information about the last pipeline run.

    Returns:
        Dictionary with timestamp information, or None if no update has been run.
    """
    return _load_last_update_timestamp()


if __name__ == "__main__":
    # Only run when executed directly, not when imported
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    result = run_full_update()
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 70)

