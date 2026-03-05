"""
Automation pipeline skeleton for weekly ingest → train workflows.

This file defines the linear stages but intentionally omits actual scraping
logic so we can plug in the production crawler once it is ready.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class PipelineContext:
    """Carries intermediate artifacts between pipeline stages."""

    def __init__(self, run_id: str, work_dir: Path):
        self.run_id = run_id
        self.work_dir = work_dir
        self.metadata: Dict[str, Any] = {}
        self.raw_paths: Dict[str, Path] = {}
        self.processed_data: Path | None = None
        self.model_artifacts: Dict[str, Path] = {}


class AutomationPipeline:
    """
    Defines the high-level steps required for automated refreshes.

    Steps (all placeholders for now):
        1. scrape -> download latest CSVs from configured sources.
        2. load -> validate presence of `scholarships.csv` & `loans.csv`.
        3. clean -> call preprocessing utilities.
        4. merge -> unify sources, version outputs.
        5. train -> invoke training pipeline.
        6. update_model -> atomically swap the API-facing artifacts.
    """

    def __init__(self, context: PipelineContext):
        self.context = context

    def run(self) -> None:
        self.scrape()
        self.load()
        self.clean()
        self.merge()
        self.train()
        self.update_model()

    # --- Stage placeholders -------------------------------------------------
    def scrape(self) -> None:
        """Fetch data from remote sources (not implemented yet)."""

    def load(self) -> None:
        """Confirm CSVs exist and record their paths in the context."""

    def clean(self) -> None:
        """Call preprocessing.clean_data to normalize the newly scraped data."""

    def merge(self) -> None:
        """Persist unified dataset with version metadata."""

    def train(self) -> None:
        """Invoke training pipeline to refresh TF-IDF model artifacts."""

    def update_model(self) -> None:
        """Atomically publish the new vectorizer, model, and dataset."""


