# app/repositories/cutoff_repository.py
import csv
from pathlib import Path
from typing import Optional

from app.core.paths import DATA_DIR


CUTOFF_FILE = DATA_DIR / "cutoff_marks_2024_2025.csv"


class CutoffRepository:
    def __init__(self, path: Path = CUTOFF_FILE):
        self.path = path
        self._cache = {}

    def load(self):
        if self._cache:
            return

        with open(self.path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["program_name"].strip(), row["district"].strip())
                self._cache[key] = float(row["cutoff_zscore"])

    def get_cutoff(
        self,
        program_name: str,
        district: str
    ) -> Optional[float]:
        self.load()
        return self._cache.get((program_name.strip(), district.strip()))
