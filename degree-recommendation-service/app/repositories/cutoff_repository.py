# app/repositories/cutoff_repository.py
import csv
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from app.core.paths import CUTOFF_DATASET_PATH


def _normalize_course_code(code: str) -> str:
    """
    Normalize course code to 3-digit format with zero-padding.
    Examples: "1" -> "001", "10" -> "010", "100" -> "100", "019" -> "019"
    """
    if not code:
        return code
    code = str(code).strip()
    # If it's a number, zero-pad to 3 digits
    try:
        num = int(code)
        return f"{num:03d}"
    except ValueError:
        # Non-numeric codes stay as-is
        return code


class CutoffRepository:
    """
    Repository for Z-score cutoff data from Cutoff_Dataset_Mapped.csv.

    Structure:
    - Course Code links to University_Courses_Dataset
    - Each row has: Course, Mapped Course Name, Course Code, University, and district Z-scores
    - Districts: COLOMBO, GAMPAHA, KALUTARA, etc. (25 total)
    - NQC = No Qualified Candidates (treated as None)
    """

    def __init__(self, path: Path = CUTOFF_DATASET_PATH):
        self.path = path
        self._cache: Dict[Tuple[str, str, str], Optional[float]] = {}
        self._by_course_code: Dict[str, List[Dict]] = {}
        self.districts = []

    def load(self):
        """Load cutoff data and build lookup indices"""
        if self._cache:
            return  # already loaded

        with open(self.path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Get district columns (all columns after University)
            all_columns = reader.fieldnames or []
            fixed_columns = [
                "Course",
                "Mapped Course Name",
                "Course Code",
                "University",
            ]
            self.districts = [col for col in all_columns if col not in fixed_columns]

            for row in reader:
                course_code = row.get("Course Code", "").strip()
                course_code = _normalize_course_code(
                    course_code
                )  # Normalize to 3-digit format
                course_name = row.get("Mapped Course Name", "").strip()
                university = row.get("University", "").strip()

                if not course_code or not university:
                    continue

                # Store by course code + university + district
                for district in self.districts:
                    zscore_str = row.get(district, "").strip()

                    # Parse Z-score (NQC = None)
                    zscore = None
                    if zscore_str and zscore_str.upper() != "NQC":
                        try:
                            zscore = float(zscore_str)
                        except ValueError:
                            zscore = None

                    # Cache by (course_code, university, district)
                    key = (course_code, university, district)
                    self._cache[key] = zscore

                # Also index by course code for easier lookup
                if course_code not in self._by_course_code:
                    self._by_course_code[course_code] = []

                self._by_course_code[course_code].append(
                    {
                        "course_name": course_name,
                        "university": university,
                        "cutoffs_by_district": {
                            district: self._cache.get(
                                (course_code, university, district)
                            )
                            for district in self.districts
                        },
                    }
                )

    def get_cutoff(
        self,
        course_code: str,
        university: str,
        district: str,
    ) -> Optional[float]:
        """
        Get Z-score cutoff for a specific course code, university, and district.
        Returns None if NQC or not found.
        """
        self.load()
        course_code = _normalize_course_code(course_code)  # Normalize lookup key
        key = (course_code.strip(), university.strip(), district.strip())
        return self._cache.get(key)

    def get_all_cutoffs_for_course(self, course_code: str) -> List[Dict]:
        """
        Get all university offerings and their cutoffs for a course code.
        Useful for showing all available options to students.
        """
        self.load()
        course_code = _normalize_course_code(course_code)  # Normalize lookup key
        return self._by_course_code.get(course_code.strip(), [])

    def get_min_cutoff_for_course(
        self,
        course_code: str,
        district: str,
    ) -> Optional[Tuple[float, str]]:
        """
        Get the minimum (easiest) Z-score cutoff for a course across all universities
        offering it in the specified district.

        Returns: (min_zscore, university_name) or None if not available
        """
        self.load()
        all_offerings = self.get_all_cutoffs_for_course(course_code)

        min_zscore = None
        min_university = None

        for offering in all_offerings:
            zscore = offering["cutoffs_by_district"].get(district.strip())
            if zscore is not None:
                if min_zscore is None or zscore < min_zscore:
                    min_zscore = zscore
                    min_university = offering["university"]

        if min_zscore is not None:
            return (min_zscore, min_university)
        return None
