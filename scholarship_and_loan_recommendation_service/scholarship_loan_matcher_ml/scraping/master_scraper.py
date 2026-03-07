"""Coordinator that runs all scraper modules and produces raw CSV outputs."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Callable

from .bank_education_loans_scraper import run_scraper as bank_loans_scraper
from .mohe_student_loans_scraper import run_scraper as mohe_loans_scraper
from .mohe_scraper import run_scraper as mohe_scholarship_scraper
from .ou_scholarships_scraper import run_scraper as ou_scholarship_scraper
from .scholarship_positions_scraper import run_scraper as positions_scraper
from .sliit_scraper import run_scraper as sliit_scraper

logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "raw_data"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_SCHOLARSHIPS_PATH = RAW_DATA_DIR / "raw_scholarships.csv"
RAW_LOANS_PATH = RAW_DATA_DIR / "raw_loans.csv"

SCHOLARSHIP_FIELDS = [
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

LOAN_FIELDS = [
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

SCHOLARSHIP_SCRAPERS: List[Tuple[str, Callable[[], List[Dict[str, str]]]]] = [
    ("mohe", mohe_scholarship_scraper),
    ("ousl", ou_scholarship_scraper),
    ("scholarship_positions", positions_scraper),
    ("sliit", sliit_scraper),
]

LOAN_SCRAPERS: List[Tuple[str, Callable[[], List[Dict[str, str]]]]] = [
    ("bank_education_loans", bank_loans_scraper),
    ("mohe_student_loans", mohe_loans_scraper),
]


def _run_collect(scrapers: Iterable[Tuple[str, Callable[[], List[Dict[str, str]]]]]) -> List[Dict[str, str]]:
    """Execute each scraper and aggregate the records."""
    results: List[Dict[str, str]] = []
    for name, scraper_func in scrapers:
        try:
            logger.info("Running scraper: %s", name)
            records = scraper_func() or []
            logger.info("%s produced %d records", name, len(records))
            results.extend(records)
        except Exception as exc:
            logger.exception("Scraper %s failed: %s", name, exc)
    return results


def _write_csv(path: Path, records: List[Dict[str, str]], fieldnames: List[str]) -> None:
    """Write standardized records to CSV."""
    if not records:
        logger.warning("No records available for %s", path.name)
        return

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fieldnames})
    logger.info("Saved %d rows to %s", len(records), path)


def run_master_scraper() -> Dict[str, List[Dict[str, str]]]:
    """Public entry point to run all scrapers and persist raw CSVs."""
    logger.info("Starting master scraper")
    scholarships = _run_collect(SCHOLARSHIP_SCRAPERS)
    loans = _run_collect(LOAN_SCRAPERS)

    _write_csv(RAW_SCHOLARSHIPS_PATH, scholarships, SCHOLARSHIP_FIELDS)
    _write_csv(RAW_LOANS_PATH, loans, LOAN_FIELDS)

    logger.info(
        "Master scraper completed: %d scholarships, %d loans",
        len(scholarships),
        len(loans),
    )

    return {
        "scholarships": scholarships,
        "loans": loans,
    }


if __name__ == "__main__":
    run_master_scraper()

