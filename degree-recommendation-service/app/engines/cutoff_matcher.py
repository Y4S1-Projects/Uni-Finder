# app/engines/cutoff_matcher.py
from typing import Optional, Tuple
from app.repositories.cutoff_repository import CutoffRepository


class CutoffMatcher:
    """
    Matches degree programs to their Z-score cutoffs using the new dataset structure.
    Uses course codes for precise matching.
    """

    def __init__(self):
        self.cutoff_repo = CutoffRepository()
        # Load cutoff data once
        self.cutoff_repo.load()

    def get_cutoff_for_course(
        self,
        course_code: str,
        district: str,
        preferred_university: Optional[str] = None,
    ) -> Tuple[Optional[float], str]:
        """
        Get Z-score cutoff for a course in a specific district.

        Args:
            course_code: Course code from University_Courses_Dataset
            district: Student's district
            preferred_university: If specified, get cutoff for that university

        Returns:
            (cutoff_zscore, explanation_message)
        """
        if preferred_university:
            # Get cutoff for specific university
            cutoff = self.cutoff_repo.get_cutoff(
                course_code, preferred_university, district
            )
            if cutoff is not None:
                return cutoff, f"Cutoff for {preferred_university}: {cutoff:.4f}"
            else:
                return (
                    None,
                    f"No cutoff data for {preferred_university} in {district} (may be NQC)",
                )

        # Get minimum cutoff across all universities offering this course
        result = self.cutoff_repo.get_min_cutoff_for_course(course_code, district)

        if result:
            min_zscore, university = result
            return min_zscore, f"Min cutoff: {min_zscore:.4f} at {university}"
        else:
            return None, f"No cutoff data available for district {district}"

    def get_all_university_cutoffs(self, course_code: str, district: str) -> list:
        """
        Get cutoffs for all universities offering a course in a district.
        Returns list of (university, zscore) tuples.
        """
        all_offerings = self.cutoff_repo.get_all_cutoffs_for_course(course_code)

        results = []
        for offering in all_offerings:
            university = offering["university"]
            zscore = offering["cutoffs_by_district"].get(district)
            if zscore is not None:
                results.append((university, zscore))

        # Sort by Z-score (ascending - easier first)
        results.sort(key=lambda x: x[1])
        return results
