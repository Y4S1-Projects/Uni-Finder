# app/domain/student.py
from typing import List, Optional


class StudentProfile:
    def __init__(
        self, stream: str, subjects: List[str], zscore: Optional[float], interests: str
    ):
        self.stream = stream
        self.subjects = subjects
        self.zscore = zscore
        self.interests = interests

    def __repr__(self):
        return (
            f"StudentProfile(stream={self.stream}, "
            f"subjects={self.subjects}, "
            f"zscore={self.zscore})"
        )
