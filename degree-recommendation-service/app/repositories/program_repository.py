# app/repositories/program_repository.py
import csv
import json
from typing import List
from pathlib import Path

from app.domain.program import DegreeProgram
from app.core.paths import PROGRAM_CATALOG_PATH


class ProgramRepository:
    """
    Repository responsible for loading degree programs
    from the program catalog dataset.
    """

    def __init__(self, catalog_path: Path = PROGRAM_CATALOG_PATH):
        self.catalog_path = catalog_path
        self._programs: List[DegreeProgram] = []

    def load_programs(self) -> List[DegreeProgram]:
        """
        Load programs from CSV and cache them in memory.
        """
        if self._programs:
            return self._programs  # cached

        with open(self.catalog_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                program = DegreeProgram.from_csv(row)
                self._programs.append(program)

        return self._programs

    def get_all_programs(self) -> List[DegreeProgram]:
        """
        Public method used by pipelines / services.
        """
        return self.load_programs()
