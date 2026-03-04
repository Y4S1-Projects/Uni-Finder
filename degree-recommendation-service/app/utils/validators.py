# app/utils/validators.py
"""
Validation utilities for student input validation
"""
from typing import List, Tuple

# Stream to subject mapping
STREAM_SUBJECTS = {
    "Science": [
        "Physics",
        "Chemistry",
        "Biology",
        "Combined Mathematics",
        "Mathematics",
        "Botany",
        "Zoology",
        "Agricultural Science",
        "Engineering Technology",
        "Science for Technology",
    ],
    "Arts": [
        "History",
        "Geography",
        "Political Science",
        "Logic",
        "Economics",
        "English",
        "Sinhala",
        "Tamil",
        "Arabic",
        "French",
        "German",
        "Home Economics",
        "Art",
        "Dancing",
        "Music",
        "Drama",
        "Oriental Music",
        "Carnatic Music",
        "Western Music",
        "Buddhist Studies",
        "Hinduism",
        "Christianity",
        "Islam",
    ],
    "Commerce": [
        "Business Studies",
        "Accounting",
        "Economics",
        "Business Statistics",
        "Mathematics",
        "Geography",
        "English",
    ],
    "Technology": [
        "Engineering Technology",
        "Science for Technology",
        "Mathematics",
        "Engineering",
    ],
}


def validate_stream_subjects(
    stream: str, subjects: List[str]
) -> Tuple[bool, str, List[str]]:
    """
    Validate that subjects match the selected stream.

    Args:
        stream: Student's A/L stream
        subjects: List of subjects taken by student

    Returns:
        Tuple of (is_valid, error_message, invalid_subjects)
    """
    if not stream:
        return False, "Stream is required", []

    if stream not in STREAM_SUBJECTS:
        return (
            False,
            f"Invalid stream: {stream}. Must be one of {list(STREAM_SUBJECTS.keys())}",
            [],
        )

    if not subjects:
        return False, "At least one subject is required", []

    valid_subjects_for_stream = [s.lower() for s in STREAM_SUBJECTS[stream]]
    invalid_subjects = []

    for subject in subjects:
        subject_lower = subject.lower()
        # Check if subject belongs to this stream
        if subject_lower not in valid_subjects_for_stream:
            # Check if it belongs to another stream
            invalid_subjects.append(subject)

    if invalid_subjects:
        return (
            False,
            (
                f"Invalid subjects for {stream} stream: {', '.join(invalid_subjects)}. "
                f"Valid subjects for {stream}: {', '.join(STREAM_SUBJECTS[stream][:5])}..."
            ),
            invalid_subjects,
        )

    return True, "", []


def validate_zscore(zscore: float) -> Tuple[bool, str]:
    """
    Validate Z-score is within acceptable range.

    Args:
        zscore: Student's Z-score

    Returns:
        Tuple of (is_valid, error_message)
    """
    if zscore is None:
        return False, "Z-score is required"

    # Z-scores typically range from -3.0 to 3.0 for university admissions
    if zscore < -3.0 or zscore > 3.0:
        return False, f"Z-score must be between -3.0 and 3.0 (got {zscore})"

    return True, ""


def validate_student_profile(
    stream: str, subjects: List[str], zscore: float
) -> Tuple[bool, str]:
    """
    Validate complete student profile.

    Args:
        stream: Student's stream
        subjects: Student's subjects
        zscore: Student's Z-score

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate stream and subjects
    valid_subjects, msg_subjects, invalid = validate_stream_subjects(stream, subjects)
    if not valid_subjects:
        return False, msg_subjects

    # Validate Z-score
    valid_zscore, msg_zscore = validate_zscore(zscore)
    if not valid_zscore:
        return False, msg_zscore

    return True, ""
