import csv
import json
import re
from pathlib import Path

DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "University_Courses_Dataset.csv"
OUTPUT_PATH = DATA_DIR / "course_subject_rules.json"

# Common subject mappings
SUBJECTS = [
    "combined mathematics",
    "higher mathematics",
    "mathematics",
    "physics",
    "chemistry",
    "biology",
    "agricultural science",
    "agri sci",
    "information & communication technology",
    "ict",
    "it",
    "business studies",
    "economics",
    "accounting",
    "business stats",
    "geography",
    "history",
    "political sci",
    "english",
    "french",
    "german",
    "logic & scientific method",
    "sinhala",
    "tamil",
    "arabic language",
    "islam",
    "islamic civilization",
    "technology",
    "engineering technology",
    "biosystems technology",
    "science for technology",
]


def extract_subjects(text):
    """Extract subjects from a chunk of text."""
    found = []
    text_lower = text.lower()

    # Sort by length to match longest first (e.g. Combined Mathematics before Mathematics)
    sorted_subjects = sorted(SUBJECTS, key=len, reverse=True)
    temp_text = text_lower

    for sub in sorted_subjects:
        if sub in temp_text:
            found.append({"type": "SUBJECT", "name": sub})
            temp_text = temp_text.replace(sub, " *** ")

    return found


def parse_requirement(code_norm, req_text):
    req_lower = req_text.lower().strip()

    # Hardcoded ASTs for complex exceptions
    if code_norm == "016":
        return {
            "type": "OR",
            "operands": [
                {
                    "type": "AND",
                    "operands": [
                        {"type": "SUBJECT", "name": "business studies"},
                        {"type": "SUBJECT", "name": "accounting"},
                        {"type": "SUBJECT", "name": "economics"},
                    ],
                },
                {
                    "type": "AND",
                    "operands": [
                        {
                            "type": "MIN_COUNT",
                            "count": 2,
                            "operands": [
                                {"type": "SUBJECT", "name": "business studies"},
                                {"type": "SUBJECT", "name": "accounting"},
                                {"type": "SUBJECT", "name": "economics"},
                            ],
                        },
                        {
                            "type": "MIN_COUNT",
                            "count": 1,
                            "operands": [
                                {"type": "SUBJECT", "name": "agri sci"},
                                {"type": "SUBJECT", "name": "geography"},
                                {"type": "SUBJECT", "name": "business stats"},
                                {"type": "SUBJECT", "name": "german"},
                                {"type": "SUBJECT", "name": "combined mathematics"},
                                {"type": "SUBJECT", "name": "mathematics"},
                                {"type": "SUBJECT", "name": "history"},
                                {"type": "SUBJECT", "name": "political sci"},
                                {"type": "SUBJECT", "name": "english"},
                                {
                                    "type": "SUBJECT",
                                    "name": "logic & scientific method",
                                },
                                {"type": "SUBJECT", "name": "french"},
                                {"type": "SUBJECT", "name": "ict"},
                            ],
                        },
                    ],
                },
            ],
        }

    if code_norm == "077":
        return {
            "type": "OR",
            "operands": [
                {
                    "type": "AND",
                    "operands": [
                        {"type": "SUBJECT", "name": "business studies"},
                        {"type": "SUBJECT", "name": "accounting"},
                        {"type": "SUBJECT", "name": "economics"},
                    ],
                },
                {
                    "type": "AND",
                    "operands": [
                        {
                            "type": "MIN_COUNT",
                            "count": 2,
                            "operands": [
                                {"type": "SUBJECT", "name": "business studies"},
                                {"type": "SUBJECT", "name": "accounting"},
                                {"type": "SUBJECT", "name": "economics"},
                            ],
                        },
                        {
                            "type": "MIN_COUNT",
                            "count": 1,
                            "operands": [
                                {"type": "SUBJECT", "name": "ict"},
                                {"type": "SUBJECT", "name": "combined mathematics"},
                                {
                                    "type": "SUBJECT",
                                    "name": "logic & scientific method",
                                },
                                {"type": "SUBJECT", "name": "business stats"},
                                {"type": "SUBJECT", "name": "physics"},
                            ],
                        },
                    ],
                },
            ],
        }

    if code_norm == "056":
        return {
            "type": "OR",
            "operands": [
                {
                    "type": "AND",
                    "operands": [
                        {"type": "SUBJECT", "name": "chemistry"},
                        {"type": "SUBJECT", "name": "combined mathematics"},
                        {"type": "SUBJECT", "name": "physics"},
                    ],
                },
                {
                    "type": "AND",
                    "operands": [
                        {"type": "SUBJECT", "name": "business studies"},
                        {"type": "SUBJECT", "name": "accounting"},
                        {"type": "SUBJECT", "name": "economics"},
                    ],
                },
                {
                    "type": "MIN_COUNT",
                    "count": 2,
                    "operands": [
                        {"type": "SUBJECT", "name": "business studies"},
                        {"type": "SUBJECT", "name": "accounting"},
                        {"type": "SUBJECT", "name": "economics"},
                    ],
                },
            ],
        }

    if (
        not req_lower
        or req_lower == "none"
        or req_lower == "n/a"
        or "any 3" in req_lower
        or "any subject" in req_lower
    ):
        return {"type": "ANY_SUBJECT"}

    # Handle explicit OR groups separated by ";" or "OR"
    if (
        "; or " in req_lower
        or " or " in req_lower
        and req_lower.count(" or ") == 1
        and "+" not in req_lower
    ):
        parts = re.split(r";\s*or\s*|\s+or\s+", req_lower)
        if len(parts) > 1:
            or_operands = []
            for p in parts:
                subs = extract_subjects(p)
                if len(subs) > 1:
                    or_operands.append({"type": "AND", "operands": subs})
                elif len(subs) == 1:
                    or_operands.append(subs[0])
            if or_operands:
                return {"type": "OR", "operands": or_operands}

    # Handle "+ X from:" or "+ 3rd from:"
    if "+" in req_lower and "from:" in req_lower:
        parts = req_lower.split("+")
        mandatory_part = parts[0]
        optional_part = parts[1]

        mandatory_subs = extract_subjects(mandatory_part)
        optional_subs = extract_subjects(optional_part)

        and_operands = mandatory_subs

        # Determine count for optional part
        count = 1
        if "2 from" in optional_part:
            count = 2

        if optional_subs:
            if count == 1:
                and_operands.append({"type": "OR", "operands": optional_subs})
            else:
                and_operands.append(
                    {"type": "MIN_COUNT", "count": count, "operands": optional_subs}
                )

        return {"type": "AND", "operands": and_operands}

    # Fallback to simple extraction
    subs = extract_subjects(req_lower)
    if not subs:
        return {"type": "ANY_SUBJECT"}

    # Heuristic for OR vs AND
    if " or " in req_lower or "/" in req_lower:
        # Complex mix, if len is 3 and "or" is present, assume 2 are required?
        # Let's just say MIN_COUNT = len - 1
        if len(subs) > 2:
            return {"type": "MIN_COUNT", "count": len(subs) - 1, "operands": subs}
        return {"type": "OR", "operands": subs}

    # Strict AND
    if len(subs) == 1:
        return subs[0]
    return {"type": "AND", "operands": subs}


def main():
    courses_dict = {}

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Course Code", "").strip()
            try:
                code_norm = f"{int(code):03d}"
            except ValueError:
                code_norm = code

            req = row.get("A/L Subject Requirements", "").strip()
            if code_norm and code_norm not in courses_dict:
                courses_dict[code_norm] = req

    final_rules = {}
    for code, req in courses_dict.items():
        final_rules[code] = parse_requirement(code, req)

    print(f"Writing {len(final_rules)} rules to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_rules, f, indent=2)

    print("Done! Local Boolean AST generated.")


if __name__ == "__main__":
    main()
