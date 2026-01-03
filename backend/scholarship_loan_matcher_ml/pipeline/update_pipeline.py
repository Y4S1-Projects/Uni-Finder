"""Unified dataset update pipeline: scrapers → cleaners → merge with existing → processed data."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd

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

    # Step 2: Clean scholarships and merge with existing
    logger.info("Step 2: Cleaning scholarship data and merging with existing")
    scholarship_clean_success = False
    if RAW_SCHOLARSHIPS_PATH.exists():
        try:
            # Load existing cleaned data if it exists
            existing_scholarships_df = None
            existing_count = 0
            if CLEAN_SCHOLARSHIPS_PATH.exists():
                try:
                    existing_scholarships_df = pd.read_csv(CLEAN_SCHOLARSHIPS_PATH, encoding='utf-8')
                    existing_count = len(existing_scholarships_df)
                    logger.info("Loaded %d existing scholarship records to merge", existing_count)
                except Exception as e:
                    logger.warning("Failed to load existing scholarships for merging: %s", e)
            
            # Clean new scraped data (write to temp file first)
            temp_clean_path = CLEAN_SCHOLARSHIPS_PATH.parent / "scholarships_clean_temp.csv"
            clean_stats = clean_scholarships(
                RAW_SCHOLARSHIPS_PATH, temp_clean_path
            )
            new_count = clean_stats.get("rows_output", 0)
            logger.info("Cleaned %d new scholarship records", new_count)
            
            # Merge with existing data
            if existing_scholarships_df is not None and new_count > 0:
                new_scholarships_df = pd.read_csv(temp_clean_path, encoding='utf-8')
                
                # Create a unique identifier for deduplication (name + provider)
                existing_scholarships_df['_merge_key'] = (
                    existing_scholarships_df['name'].fillna('').str.lower().str.strip() + '|' +
                    existing_scholarships_df['provider'].fillna('').str.lower().str.strip()
                )
                new_scholarships_df['_merge_key'] = (
                    new_scholarships_df['name'].fillna('').str.lower().str.strip() + '|' +
                    new_scholarships_df['provider'].fillna('').str.lower().str.strip()
                )
                
                # Find duplicates
                duplicates_mask = new_scholarships_df['_merge_key'].isin(existing_scholarships_df['_merge_key'])
                duplicates_count = duplicates_mask.sum()
                
                # Keep only new records (not duplicates)
                new_unique_df = new_scholarships_df[~duplicates_mask].copy()
                new_unique_count = len(new_unique_df)
                
                # Remove merge key before combining
                existing_scholarships_df = existing_scholarships_df.drop(columns=['_merge_key'])
                new_unique_df = new_unique_df.drop(columns=['_merge_key'])
                
                # Combine existing + new unique records
                merged_df = pd.concat([existing_scholarships_df, new_unique_df], ignore_index=True)
                merged_count = len(merged_df)
                
                logger.info(
                    "Merged scholarships: %d existing + %d new = %d total (%d duplicates skipped)",
                    existing_count, new_unique_count, merged_count, duplicates_count
                )
                
                # Save merged result
                merged_df.to_csv(CLEAN_SCHOLARSHIPS_PATH, index=False, encoding='utf-8')
                temp_clean_path.unlink(missing_ok=True)  # Remove temp file
                
                summary["cleaner_results"]["scholarships"] = {
                    "success": True,
                    "rows_input": clean_stats.get("rows_input", 0),
                    "rows_output": merged_count,
                    "existing_count": existing_count,
                    "new_count": new_count,
                    "new_unique_count": new_unique_count,
                    "duplicates_removed": clean_stats.get("duplicates_removed", 0) + duplicates_count,
                    "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
                }
            else:
                # No existing data or no new data, just use cleaned new data
                if temp_clean_path.exists():
                    temp_clean_path.rename(CLEAN_SCHOLARSHIPS_PATH)
                summary["cleaner_results"]["scholarships"] = {
                    "success": True,
                    "rows_input": clean_stats.get("rows_input", 0),
                    "rows_output": new_count,
                    "existing_count": existing_count,
                    "new_count": new_count,
                    "new_unique_count": new_count,
                    "duplicates_removed": clean_stats.get("duplicates_removed", 0),
                    "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
                }
            
            scholarship_clean_success = True
        except Exception as e:
            error_msg = f"Scholarship cleaning/merging failed: {str(e)}"
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

    # Step 3: Clean loans and merge with existing
    logger.info("Step 3: Cleaning loan data and merging with existing")
    loan_clean_success = False
    if RAW_LOANS_PATH.exists():
        try:
            # Load existing cleaned data if it exists
            existing_loans_df = None
            existing_count = 0
            if CLEAN_LOANS_PATH.exists():
                try:
                    existing_loans_df = pd.read_csv(CLEAN_LOANS_PATH, encoding='utf-8')
                    existing_count = len(existing_loans_df)
                    logger.info("Loaded %d existing loan records to merge", existing_count)
                except Exception as e:
                    logger.warning("Failed to load existing loans for merging: %s", e)
            
            # Clean new scraped data (write to temp file first)
            temp_clean_path = CLEAN_LOANS_PATH.parent / "loans_clean_temp.csv"
            clean_stats = clean_loans(RAW_LOANS_PATH, temp_clean_path)
            new_count = clean_stats.get("rows_output", 0)
            logger.info("Cleaned %d new loan records", new_count)
            
            # Merge with existing data
            if existing_loans_df is not None and new_count > 0:
                new_loans_df = pd.read_csv(temp_clean_path, encoding='utf-8')
                
                # Create a unique identifier for deduplication (name + provider)
                existing_loans_df['_merge_key'] = (
                    existing_loans_df['name'].fillna('').str.lower().str.strip() + '|' +
                    existing_loans_df['provider'].fillna('').str.lower().str.strip()
                )
                new_loans_df['_merge_key'] = (
                    new_loans_df['name'].fillna('').str.lower().str.strip() + '|' +
                    new_loans_df['provider'].fillna('').str.lower().str.strip()
                )
                
                # Find duplicates
                duplicates_mask = new_loans_df['_merge_key'].isin(existing_loans_df['_merge_key'])
                duplicates_count = duplicates_mask.sum()
                
                # Keep only new records (not duplicates)
                new_unique_df = new_loans_df[~duplicates_mask].copy()
                new_unique_count = len(new_unique_df)
                
                # Remove merge key before combining
                existing_loans_df = existing_loans_df.drop(columns=['_merge_key'])
                new_unique_df = new_unique_df.drop(columns=['_merge_key'])
                
                # Combine existing + new unique records
                merged_df = pd.concat([existing_loans_df, new_unique_df], ignore_index=True)
                merged_count = len(merged_df)
                
                logger.info(
                    "Merged loans: %d existing + %d new = %d total (%d duplicates skipped)",
                    existing_count, new_unique_count, merged_count, duplicates_count
                )
                
                # Save merged result
                merged_df.to_csv(CLEAN_LOANS_PATH, index=False, encoding='utf-8')
                temp_clean_path.unlink(missing_ok=True)  # Remove temp file
                
                summary["cleaner_results"]["loans"] = {
                    "success": True,
                    "rows_input": clean_stats.get("rows_input", 0),
                    "rows_output": merged_count,
                    "existing_count": existing_count,
                    "new_count": new_count,
                    "new_unique_count": new_unique_count,
                    "duplicates_removed": clean_stats.get("duplicates_removed", 0) + duplicates_count,
                    "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
                }
            else:
                # No existing data or no new data, just use cleaned new data
                if temp_clean_path.exists():
                    temp_clean_path.rename(CLEAN_LOANS_PATH)
                summary["cleaner_results"]["loans"] = {
                    "success": True,
                    "rows_input": clean_stats.get("rows_input", 0),
                    "rows_output": new_count,
                    "existing_count": existing_count,
                    "new_count": new_count,
                    "new_unique_count": new_count,
                    "duplicates_removed": clean_stats.get("duplicates_removed", 0),
                    "invalid_rows_fixed": clean_stats.get("invalid_rows_fixed", 0),
                }
            
            loan_clean_success = True
        except Exception as e:
            error_msg = f"Loan cleaning/merging failed: {str(e)}"
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

