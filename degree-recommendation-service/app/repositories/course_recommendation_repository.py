# app/repositories/course_recommendation_repository.py
import csv
from typing import List, Optional
from pathlib import Path

from app.domain.course_recommendation import CourseRecommendation
from app.core.paths import DATA_DIR


class CourseRecommendationRepository:
    """
    Repository responsible for loading course recommendations with interest/skill metadata
    from the Course_Recommendation_Dataset.csv.
    """

    def __init__(self, dataset_path: Optional[Path] = None):
        if dataset_path is None:
            dataset_path = Path(DATA_DIR) / "Course_Recommendation_Dataset.csv"
        self.dataset_path = dataset_path
        self._courses: List[CourseRecommendation] = []
        self._courses_by_code: dict = {}

    def load_courses(self) -> List[CourseRecommendation]:
        """
        Load courses from CSV and cache them in memory.
        """
        if self._courses:
            return self._courses  # cached

        with open(self.dataset_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Normalize keys to handle BOM and whitespace
                normalized_row = {
                    (str(k).lstrip("\ufeff").strip() if k is not None else ""): v
                    for k, v in row.items()
                }

                try:
                    course = CourseRecommendation.from_csv(normalized_row)
                    self._courses.append(course)

                    # Index by course code for quick lookup
                    if course.course_code:
                        self._courses_by_code[course.course_code] = course
                except Exception as e:
                    # Log but don't fail on individual parsing errors
                    print(f"Warning: Failed to parse course row: {e}")
                    continue

        return self._courses

    def get_all_courses(self) -> List[CourseRecommendation]:
        """
        Public method to get all courses.
        """
        return self.load_courses()

    def get_course_by_code(self, course_code: str) -> Optional[CourseRecommendation]:
        """
        Get a specific course by its course code.
        """
        if not self._courses:
            self.load_courses()
        return self._courses_by_code.get(course_code)

    def get_courses_by_stream(self, stream: str) -> List[CourseRecommendation]:
        """
        Get all courses for a specific stream.
        """
        courses = self.get_all_courses()
        stream_lower = stream.lower()
        return [c for c in courses if c.stream and stream_lower in c.stream.lower()]

    def get_courses_by_codes(
        self, course_codes: List[str]
    ) -> List[CourseRecommendation]:
        """
        Get multiple courses by their course codes.
        """
        if not self._courses:
            self.load_courses()
        return [
            self._courses_by_code[code]
            for code in course_codes
            if code in self._courses_by_code
        ]
