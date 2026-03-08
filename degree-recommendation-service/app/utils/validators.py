# app/utils/validators.py
"""
Validation utilities for student input validation.
Implements flexible Sri Lanka A/L stream rules with cross-stream subjects.
"""
from typing import List, Tuple

STREAM_ALIASES = {
    "science": "Physical Science",
    "physical science": "Physical Science",
    "physical science (maths)": "Physical Science",
    "biological science": "Biological Science",
    "bio science": "Biological Science",
    "engineering technology": "Engineering Technology",
    "bio-systems technology": "Bio-Systems Technology",
    "biosystems technology": "Bio-Systems Technology",
    "arts": "Arts",
    "commerce": "Commerce",
    "technology": "Technology",  # legacy umbrella stream
}

SUBJECT_ALIASES = {
    "ict": "Information & Communication Technology",
    "information and communication technology": "Information & Communication Technology",
    "business stats": "Business Statistics",
    "combined maths": "Combined Mathematics",
    "higher maths": "Higher Mathematics",
    "dancing": "Dance",
    "drama & theatre": "Drama",
    "communication and media studies": "Communication & Media Studies",
    "logic and scientific method": "Logic & Scientific Method",
    "agriculture": "Agricultural Science",
    "agri science": "Agricultural Science",
    "buddhist studies": "Buddhism",
    "buddhist civilization": "Buddhism",
    "hindu civilization": "Hinduism",
    "christian civilization": "Christianity",
    "islamic studies": "Islam",
}

PHYSICAL_SCIENCE_CORE = {"Combined Mathematics", "Physics"}
PHYSICAL_SCIENCE_OPTIONALS = {
    "Chemistry",
    "Information & Communication Technology",
    "Higher Mathematics",
}

BIO_SCIENCE_CORE = {"Biology", "Chemistry"}
BIO_SCIENCE_OPTIONALS = {
    "Physics",
    "Agricultural Science",
    "Information & Communication Technology",
}

COMMERCE_STANDARD = {"Accounting", "Business Studies", "Economics"}
COMMERCE_ALLOWED = COMMERCE_STANDARD.union(
    {
        "Business Statistics",
        "Geography",
        "Political Science",
        "History",
        "Logic & Scientific Method",
        "English",
        "Information & Communication Technology",
        "Agricultural Science",
        "Combined Mathematics",
        "Physics",
        "French",
        "German",
    }
)

TECH_CATEGORY_C = {
    "Information & Communication Technology",
    "Economics",
    "Geography",
    "Home Economics",
    "English",
    "Communication & Media Studies",
    "Art",
    "Business Studies",
    "Accounting",
    "Mathematics",
    "Agricultural Science",
}

ARTS_ALLOWED = {
    "Economics",
    "Geography",
    "History",
    "Accounting",
    "Business Statistics",
    "Political Science",
    "Logic & Scientific Method",
    "Home Economics",
    "Communication & Media Studies",
    "Information & Communication Technology",
    "Agricultural Science",
    "Combined Mathematics",
    "Higher Mathematics",
    "Buddhism",
    "Hinduism",
    "Christianity",
    "Islam",
    "Islamic Civilization",
    "Greek & Roman Civilization",
    "Art",
    "Dance",
    "Music",
    "Drama",
    "Sinhala",
    "Tamil",
    "English",
    "Arabic",
    "Pali",
    "Sanskrit",
    "French",
    "German",
    "Russian",
    "Japanese",
    "Chinese",
    "Hindi",
    "Civil Tech",
    "Mechanical Tech",
    "Electrical/Electronic Tech",
    "Food Tech",
    "Agro Tech",
    "Bio-Resource Tech",
}

ARTS_TECH_SUBJECTS = {
    "Civil Tech",
    "Mechanical Tech",
    "Electrical/Electronic Tech",
    "Food Tech",
    "Agro Tech",
    "Bio-Resource Tech",
}

STREAM_SUBJECTS = {
    "Physical Science": sorted(PHYSICAL_SCIENCE_CORE.union(PHYSICAL_SCIENCE_OPTIONALS)),
    "Biological Science": sorted(BIO_SCIENCE_CORE.union(BIO_SCIENCE_OPTIONALS)),
    "Commerce": sorted(COMMERCE_ALLOWED),
    "Engineering Technology": sorted(
        {"Engineering Technology", "Science for Technology"}.union(TECH_CATEGORY_C)
    ),
    "Bio-Systems Technology": sorted(
        {"Bio-Systems Technology", "Science for Technology"}.union(TECH_CATEGORY_C)
    ),
    "Arts": sorted(ARTS_ALLOWED),
    "Technology": sorted(
        {
            "Engineering Technology",
            "Bio-Systems Technology",
            "Science for Technology",
        }.union(TECH_CATEGORY_C)
    ),
}


def _normalize_stream(stream: str) -> str:
    if not stream:
        return ""
    return STREAM_ALIASES.get(stream.strip().lower(), stream.strip())


def _normalize_subject(subject: str) -> str:
    if not subject:
        return ""
    cleaned = " ".join(subject.strip().split())
    lower = cleaned.lower()
    return SUBJECT_ALIASES.get(lower, cleaned)


def _invalid_subjects(subjects: List[str], allowed_set: set[str]) -> List[str]:
    return [subject for subject in subjects if subject not in allowed_set]


def _validate_physical_science(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    allowed = PHYSICAL_SCIENCE_CORE.union(PHYSICAL_SCIENCE_OPTIONALS)
    invalid = _invalid_subjects(subjects, allowed)
    if invalid:
        return False, "Invalid subjects for Physical Science stream", invalid
    if len(subjects) != 3:
        return False, "Physical Science requires exactly 3 subjects", []
    if not PHYSICAL_SCIENCE_CORE.issubset(set(subjects)):
        return False, "Physical Science requires Combined Mathematics and Physics", []
    optionals = [s for s in subjects if s in PHYSICAL_SCIENCE_OPTIONALS]
    if len(optionals) != 1:
        return (
            False,
            "Physical Science requires exactly one optional subject: Chemistry, Information & Communication Technology, or Higher Mathematics",
            [],
        )
    return True, "", []


def _validate_biological_science(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    allowed = BIO_SCIENCE_CORE.union(BIO_SCIENCE_OPTIONALS)
    invalid = _invalid_subjects(subjects, allowed)
    if invalid:
        return False, "Invalid subjects for Biological Science stream", invalid
    if len(subjects) != 3:
        return False, "Biological Science requires exactly 3 subjects", []
    if not BIO_SCIENCE_CORE.issubset(set(subjects)):
        return False, "Biological Science requires Biology and Chemistry", []
    optionals = [s for s in subjects if s in BIO_SCIENCE_OPTIONALS]
    if len(optionals) != 1:
        return (
            False,
            "Biological Science requires exactly one optional subject: Physics, Agricultural Science, or Information & Communication Technology",
            [],
        )
    return True, "", []


def _validate_commerce(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    invalid = _invalid_subjects(subjects, COMMERCE_ALLOWED)
    if invalid:
        return False, "Invalid subjects for Commerce stream", invalid
    if len(subjects) != 3:
        return False, "Commerce requires exactly 3 subjects", []
    standard_count = sum(1 for subject in subjects if subject in COMMERCE_STANDARD)
    if standard_count < 2:
        return (
            False,
            "Commerce requires at least two of: Accounting, Business Studies, Economics",
            [],
        )
    return True, "", []


def _validate_engineering_technology(
    subjects: List[str],
) -> Tuple[bool, str, List[str]]:
    allowed = {"Engineering Technology", "Science for Technology"}.union(
        TECH_CATEGORY_C
    )
    invalid = _invalid_subjects(subjects, allowed)
    if invalid:
        return False, "Invalid subjects for Engineering Technology stream", invalid
    if len(subjects) != 3:
        return False, "Engineering Technology requires exactly 3 subjects", []
    core = {"Engineering Technology", "Science for Technology"}
    if not core.issubset(set(subjects)):
        return (
            False,
            "Engineering Technology stream requires Engineering Technology and Science for Technology",
            [],
        )
    optionals = [s for s in subjects if s in TECH_CATEGORY_C]
    if len(optionals) != 1:
        return (
            False,
            "Engineering Technology requires exactly one Category C optional subject",
            [],
        )
    return True, "", []


def _validate_biosystems_technology(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    allowed = {"Bio-Systems Technology", "Science for Technology"}.union(
        TECH_CATEGORY_C
    )
    invalid = _invalid_subjects(subjects, allowed)
    if invalid:
        return False, "Invalid subjects for Bio-Systems Technology stream", invalid
    if len(subjects) != 3:
        return False, "Bio-Systems Technology requires exactly 3 subjects", []
    core = {"Bio-Systems Technology", "Science for Technology"}
    if not core.issubset(set(subjects)):
        return (
            False,
            "Bio-Systems Technology stream requires Bio-Systems Technology and Science for Technology",
            [],
        )
    optionals = [s for s in subjects if s in TECH_CATEGORY_C]
    if len(optionals) != 1:
        return (
            False,
            "Bio-Systems Technology requires exactly one Category C optional subject",
            [],
        )
    return True, "", []


def _validate_technology_legacy(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    allowed = {
        "Engineering Technology",
        "Bio-Systems Technology",
        "Science for Technology",
    }.union(TECH_CATEGORY_C)
    invalid = _invalid_subjects(subjects, allowed)
    if invalid:
        return False, "Invalid subjects for Technology stream", invalid
    if len(subjects) != 3:
        return False, "Technology requires exactly 3 subjects", []
    if "Science for Technology" not in subjects:
        return False, "Technology stream requires Science for Technology", []
    has_et_or_bst = (
        "Engineering Technology" in subjects or "Bio-Systems Technology" in subjects
    )
    if not has_et_or_bst:
        return (
            False,
            "Technology stream requires either Engineering Technology or Bio-Systems Technology",
            [],
        )
    optionals = [s for s in subjects if s in TECH_CATEGORY_C]
    if len(optionals) != 1:
        return False, "Technology requires exactly one Category C optional subject", []
    return True, "", []


def _validate_arts(subjects: List[str]) -> Tuple[bool, str, List[str]]:
    invalid = _invalid_subjects(subjects, ARTS_ALLOWED)
    if invalid:
        return False, "Invalid subjects for Arts stream", invalid
    if len(subjects) != 3:
        return False, "Arts requires exactly 3 subjects", []
    tech_count = sum(1 for subject in subjects if subject in ARTS_TECH_SUBJECTS)
    if tech_count > 1:
        return False, "Arts allows a maximum of one technological subject", []
    return True, "", []


def validate_stream_subjects(
    stream: str, subjects: List[str]
) -> Tuple[bool, str, List[str]]:
    """Validate stream-subject combinations using official Sri Lanka A/L stream rules."""
    if not stream:
        return False, "Stream is required", []

    normalized_stream = _normalize_stream(stream)
    normalized_subjects = [_normalize_subject(subject) for subject in subjects]

    if not normalized_subjects:
        return False, "At least one subject is required", []

    validators = {
        "Physical Science": _validate_physical_science,
        "Biological Science": _validate_biological_science,
        "Commerce": _validate_commerce,
        "Engineering Technology": _validate_engineering_technology,
        "Bio-Systems Technology": _validate_biosystems_technology,
        "Arts": _validate_arts,
        "Technology": _validate_technology_legacy,
    }

    if normalized_stream not in validators:
        return (
            False,
            (
                f"Invalid stream: {stream}. Must be one of "
                f"{', '.join(validators.keys())}"
            ),
            [],
        )

    is_valid, msg, invalid = validators[normalized_stream](normalized_subjects)
    if not is_valid:
        if invalid:
            preview = ", ".join(STREAM_SUBJECTS.get(normalized_stream, [])[:8])
            return (
                False,
                (
                    f"{msg}: {', '.join(invalid)}. "
                    f"Valid subjects for {normalized_stream}: {preview}..."
                ),
                invalid,
            )
        return False, msg, []

    return True, "", []


def validate_zscore(zscore: float) -> Tuple[bool, str]:
    """Validate Z-score is within acceptable range if provided."""
    if zscore is None:
        return True, ""

    if zscore < -3.0 or zscore > 3.0:
        return False, f"Z-score must be between -3.0 and 3.0 (got {zscore})"

    return True, ""


def validate_student_profile(
    stream: str, subjects: List[str], zscore: float
) -> Tuple[bool, str]:
    """Validate complete student profile."""
    valid_subjects, msg_subjects, _ = validate_stream_subjects(stream, subjects)
    if not valid_subjects:
        return False, msg_subjects

    valid_zscore, msg_zscore = validate_zscore(zscore)
    if not valid_zscore:
        return False, msg_zscore

    return True, ""
