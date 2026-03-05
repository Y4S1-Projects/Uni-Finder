# app/repositories/program_repository.py
import csv
import json
from typing import List, Optional
from pathlib import Path

from app.domain.program import DegreeProgram
from app.core.paths import UNIVERSITY_COURSES_PATH


class ProgramRepository:
    """
    Repository responsible for loading degree programs
    from the University_Courses_Dataset.csv.
    """

    def __init__(self, catalog_path: Path = UNIVERSITY_COURSES_PATH):
        self.catalog_path = catalog_path
        self._programs: List[DegreeProgram] = []
        self._programs_by_code: dict = {}

    def load_programs(self) -> List[DegreeProgram]:
        """
        Load programs from CSV and cache them in memory.
        """
        if self._programs:
            return self._programs  # cached

        with open(self.catalog_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Some CSVs include BOM/whitespace in headers; normalize keys for robustness.
                normalized_row = {
                    (str(k).lstrip("\ufeff").strip() if k is not None else ""): v
                    for k, v in row.items()
                }

                try:
                    program = DegreeProgram.from_csv(normalized_row)
                    self._programs.append(program)

                    # Index by course code for quick lookup
                    if program.course_code:
                        self._programs_by_code[program.course_code] = program
                except Exception as e:
                    # Log but don't fail on individual parsing errors
                    print(f"Warning: Failed to parse program row: {e}")
                    continue

        return self._programs

    def get_all_programs(self) -> List[DegreeProgram]:
        """
        Public method used by pipelines / services.
        """
        return self.load_programs()

    def get_program_by_code(self, course_code: str) -> Optional[DegreeProgram]:
        """
        Get a specific program by its course code.
        """
        if not self._programs:
            self.load_programs()
        return self._programs_by_code.get(course_code)

    def get_programs_by_stream(self, stream: str) -> List[DegreeProgram]:
        """
        Get all programs for a specific stream.
        """
        programs = self.get_all_programs()
        stream_lower = stream.lower()
        return [p for p in programs if p.stream and stream_lower in p.stream.lower()]
