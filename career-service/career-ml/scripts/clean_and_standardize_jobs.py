"""
clean_and_standardize_jobs.py
==============================
Clean and standardize the unified jobs dataset.

Inputs  : data/processed/jobs_unified.csv
Outputs : data/processed/jobs_cleaned.csv

Standardisations:
  1. Title normalisation   – strip prefixes, map common aliases
  2. Experience parsing    – extract min / max years
  3. Salary parsing        – extract min / max + currency (LKR / USD)
  4. Job type classification – full-time, part-time, contract, remote, hybrid
  5. Remote policy         – on-site, remote, hybrid
  6. Industry tagging      – keyword-based classification
  7. Location normalisation – city + country from free text
  8. NLP-assisted cleaning – spaCy for entity extraction (optional)

Additional columns added:
  experience_min, experience_max, salary_min, salary_max, salary_currency,
  job_type_clean, remote_policy, industry_clean, location_city,
  location_country

Prerequisites:
    pip install pandas tqdm
    # Optional for NLP:
    pip install spacy
    python -m spacy download en_core_web_sm

Run:
    cd career-ml
    python scripts/clean_and_standardize_jobs.py [--input FILE] [--no-spacy]
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
INPUT_CSV     = PROCESSED_DIR / "jobs_unified.csv"
OUTPUT_CSV    = PROCESSED_DIR / "jobs_cleaned.csv"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
#  1. TITLE NORMALISATION
# ══════════════════════════════════════════════════════════════════════

# Common prefix / suffix noise to strip
TITLE_STRIP_PATTERNS = [
    r"^(urgent|hiring|immediate|new|hot)\s*[:\-–|!]*\s*",
    r"\s*[-–|]\s*(apply\s+now|closing\s+soon|new)$",
    r"\s*\(re-?advertis(?:ed|ement)\)",
    r"\s*\(.*vacancy.*\)",
]

# Alias mapping: common alternative titles → canonical form
TITLE_ALIASES: dict[str, str] = {
    "se":       "Software Engineer",
    "swe":      "Software Engineer",
    "sde":      "Software Development Engineer",
    "qa":       "QA Engineer",
    "qae":      "QA Engineer",
    "sse":      "Senior Software Engineer",
    "tl":       "Tech Lead",
    "pm":       "Project Manager",
    "ba":       "Business Analyst",
    "devops":   "DevOps Engineer",
    "ml":       "Machine Learning Engineer",
    "ds":       "Data Scientist",
    "de":       "Data Engineer",
    "ux":       "UX Designer",
    "ui":       "UI Designer",
    "sre":      "Site Reliability Engineer",
    "dba":      "Database Administrator",
    "sa":       "Solutions Architect",
}


def clean_title(title: str) -> str:
    t = str(title).strip()
    for pat in TITLE_STRIP_PATTERNS:
        t = re.sub(pat, "", t, flags=re.IGNORECASE).strip()
    # Title-case normalise
    t = re.sub(r"\s+", " ", t).strip()
    # If the entire title is an abbreviation, expand it
    if t.upper() in TITLE_ALIASES:
        return TITLE_ALIASES[t.upper()]
    # Capitalise properly
    if t == t.upper() and len(t) > 5:
        t = t.title()
    return t


# ══════════════════════════════════════════════════════════════════════
#  2. EXPERIENCE PARSING
# ══════════════════════════════════════════════════════════════════════

def parse_experience(raw: str) -> tuple[float | None, float | None]:
    """Return (min_years, max_years) from free-text experience field."""
    if not raw or str(raw) == "nan":
        return None, None
    text = str(raw).lower()

    # Range: "3-5 years" or "3 to 5 years"
    m = re.search(r"(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)\s*(?:years?|yrs?)", text)
    if m:
        return float(m.group(1)), float(m.group(2))

    # "5+ years" or "minimum 5 years"
    m = re.search(r"(\d+\.?\d*)\s*\+?\s*(?:years?|yrs?)", text)
    if m:
        val = float(m.group(1))
        return val, val + 3  # heuristic upper bound

    return None, None


# ══════════════════════════════════════════════════════════════════════
#  3. SALARY PARSING
# ══════════════════════════════════════════════════════════════════════

def parse_salary(raw: str) -> tuple[float | None, float | None, str]:
    """Return (min, max, currency) from free-text salary field."""
    if not raw or str(raw) == "nan":
        return None, None, ""
    text = str(raw).replace(",", "").strip()

    # Detect currency
    cur = "LKR"
    if any(c in text.lower() for c in ["usd", "$", "dollar"]):
        cur = "USD"
    elif any(c in text.lower() for c in ["gbp", "£", "pound"]):
        cur = "GBP"

    # Range: "100000 - 200000"
    m = re.search(r"(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)", text)
    if m:
        return float(m.group(1)), float(m.group(2)), cur

    # Single figure: "100000"
    m = re.search(r"(\d{4,}\.?\d*)", text)
    if m:
        val = float(m.group(1))
        return val, None, cur

    return None, None, ""


# ══════════════════════════════════════════════════════════════════════
#  4. JOB TYPE CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════

def classify_job_type(row: pd.Series) -> str:
    blob = " ".join(str(row.get(c, "")) for c in
                    ["job_title", "description", "requirements_text", "job_type"]).lower()
    if "intern" in blob:
        return "internship"
    if "contract" in blob or "freelance" in blob:
        return "contract"
    if "part-time" in blob or "part time" in blob:
        return "part-time"
    return "full-time"


# ══════════════════════════════════════════════════════════════════════
#  5. REMOTE POLICY
# ══════════════════════════════════════════════════════════════════════

def detect_remote_policy(row: pd.Series) -> str:
    blob = " ".join(str(row.get(c, "")) for c in
                    ["job_title", "description", "location", "job_type"]).lower()
    if "hybrid" in blob:
        return "hybrid"
    if "remote" in blob or "work from home" in blob or "wfh" in blob:
        return "remote"
    return "on-site"


# ══════════════════════════════════════════════════════════════════════
#  6. INDUSTRY TAGGING
# ══════════════════════════════════════════════════════════════════════

INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "fintech":        ["bank", "fintech", "payment", "insurance", "trading",
                       "financial", "capital market"],
    "healthtech":     ["health", "medical", "pharma", "hospital", "clinical"],
    "edtech":         ["education", "e-learning", "university", "school",
                       "lms", "mooc"],
    "ecommerce":      ["e-commerce", "ecommerce", "retail", "marketplace",
                       "shop", "takas"],
    "telecom":        ["telecom", "dialog", "mobitel", "slt", "airtel",
                       "axiata"],
    "travel":         ["travel", "hotel", "booking", "airline", "tourism"],
    "gaming":         ["game", "gaming", "esports"],
    "cybersecurity":  ["security", "cyber", "soc", "siem", "penetration"],
    "ai_ml":          ["machine learning", "artificial intelligence", "ml ",
                       "deep learning", "nlp", "computer vision"],
    "cloud":          ["cloud", "aws", "azure", "gcp", "saas", "paas",
                       "infrastructure"],
    "enterprise_sw":  ["erp", "crm", "sap", "oracle", "enterprise software"],
}


def classify_industry(row: pd.Series) -> str:
    blob = " ".join(str(row.get(c, "")) for c in
                    ["description", "industry", "company_name", "job_title"]).lower()
    scores: dict[str, int] = {}
    for ind, kws in INDUSTRY_KEYWORDS.items():
        scores[ind] = sum(1 for kw in kws if kw in blob)
    best = max(scores, key=scores.get) if scores else ""
    return best if scores.get(best, 0) > 0 else "IT/Software"


# ══════════════════════════════════════════════════════════════════════
#  7. LOCATION NORMALISATION
# ══════════════════════════════════════════════════════════════════════

SL_CITIES = [
    "colombo", "kandy", "galle", "jaffna", "negombo", "matara",
    "kurunegala", "batticaloa", "trincomalee", "anuradhapura",
    "ratnapura", "badulla", "kalutara", "moratuwa", "dehiwala",
    "mount lavinia", "kotte", "pitakotte", "malabe", "kaduwela",
    "orion city", "trace expert city", "katubedda", "rajagiriya",
]

INTL_CITIES = {
    "bangalore": ("Bangalore", "India"),
    "bengaluru": ("Bangalore", "India"),
    "hyderabad": ("Hyderabad", "India"),
    "pune":      ("Pune", "India"),
    "mumbai":    ("Mumbai", "India"),
    "chennai":   ("Chennai", "India"),
    "london":    ("London", "UK"),
    "new york":  ("New York", "USA"),
    "singapore": ("Singapore", "Singapore"),
    "dubai":     ("Dubai", "UAE"),
}


def normalise_location(raw: str) -> tuple[str, str]:
    """Return (city, country)."""
    if not raw or str(raw) == "nan":
        return "", "Sri Lanka"
    text = str(raw).lower().strip()

    # Check international cities first
    for key, (city, country) in INTL_CITIES.items():
        if key in text:
            return city, country

    # Check SL cities
    for city in SL_CITIES:
        if city in text:
            return city.title(), "Sri Lanka"

    if "sri lanka" in text or "sl" in text:
        return "Colombo", "Sri Lanka"

    if "remote" in text:
        return "Remote", ""

    return raw.strip().title(), "Sri Lanka"


# ══════════════════════════════════════════════════════════════════════
#  8. NLP-ASSISTED ENRICHMENT (optional, spaCy)
# ══════════════════════════════════════════════════════════════════════

def _load_spacy():
    if not HAS_SPACY:
        return None
    try:
        return spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])
    except OSError:
        print("  ⚠ spaCy model 'en_core_web_sm' not found – skipping NLP enrichment")
        return None


def spacy_extract(nlp, text: str) -> dict:
    """Use NER to pull ORG / GPE / MONEY entities."""
    if not nlp or not text:
        return {}
    doc = nlp(str(text)[:5000])
    result: dict = {"orgs": [], "locations": [], "money": []}
    for ent in doc.ents:
        if ent.label_ == "ORG":
            result["orgs"].append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            result["locations"].append(ent.text)
        elif ent.label_ == "MONEY":
            result["money"].append(ent.text)
    return result


# ══════════════════════════════════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════════════════════════════════

def run_pipeline(df: pd.DataFrame, use_spacy: bool = True) -> pd.DataFrame:
    """Apply all cleaning & standardisation steps."""
    print(f"\n  Input rows: {len(df)}")

    # -- Title --
    print("  [1/7] Normalising titles …")
    df["job_title_clean"] = df["job_title"].apply(clean_title)

    # -- Experience --
    print("  [2/7] Parsing experience …")
    exp = df["experience_raw"].apply(parse_experience)
    df["experience_min"] = exp.apply(lambda x: x[0])
    df["experience_max"] = exp.apply(lambda x: x[1])

    # -- Salary --
    print("  [3/7] Parsing salary …")
    sal = df["salary_raw"].apply(parse_salary)
    df["salary_min"]      = sal.apply(lambda x: x[0])
    df["salary_max"]      = sal.apply(lambda x: x[1])
    df["salary_currency"] = sal.apply(lambda x: x[2])

    # -- Job type --
    print("  [4/7] Classifying job types …")
    df["job_type_clean"] = df.apply(classify_job_type, axis=1)

    # -- Remote policy --
    print("  [5/7] Detecting remote policy …")
    df["remote_policy"] = df.apply(detect_remote_policy, axis=1)

    # -- Industry --
    print("  [6/7] Tagging industries …")
    df["industry_clean"] = df.apply(classify_industry, axis=1)

    # -- Location --
    print("  [7/7] Normalising locations …")
    locs = df["location"].apply(normalise_location)
    df["location_city"]    = locs.apply(lambda x: x[0])
    df["location_country"] = locs.apply(lambda x: x[1])

    # -- Optional spaCy enrichment --
    if use_spacy and HAS_SPACY:
        nlp = _load_spacy()
        if nlp:
            print("  [+] spaCy NER enrichment …")
            for idx in tqdm(df.index, desc="  NER", unit="row"):
                blob = str(df.at[idx, "description"])[:3000]
                ents = spacy_extract(nlp, blob)
                if ents.get("locations") and not df.at[idx, "location_city"]:
                    df.at[idx, "location_city"] = ents["locations"][0]

    # Drop fully empty description rows
    df = df[~((df["job_title_clean"] == "") & (df["description"] == ""))]

    # Reset index
    df = df.reset_index(drop=True)
    print(f"\n  Output rows: {len(df)}")
    return df


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean & standardise the unified jobs dataset")
    parser.add_argument("--input", type=str, default=str(INPUT_CSV),
                        help="Input CSV path")
    parser.add_argument("--output", type=str, default=str(OUTPUT_CSV),
                        help="Output CSV path")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Skip spaCy NER enrichment")
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)

    print("=" * 70)
    print("  Clean & Standardize Jobs")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print("=" * 70)

    if not input_path.exists():
        print(f"  ✗ Input file not found: {input_path}")
        return

    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    df = run_pipeline(df, use_spacy=not args.no_spacy)

    df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
    print(f"\n  ✓ Saved cleaned data → {output_path}")

    # Summary stats
    print(f"\n  ── Summary ──")
    print(f"  Rows           : {len(df)}")
    if "job_type_clean" in df.columns:
        print(f"  Job types      : {df['job_type_clean'].value_counts().to_dict()}")
    if "remote_policy" in df.columns:
        print(f"  Remote policy  : {df['remote_policy'].value_counts().to_dict()}")
    if "industry_clean" in df.columns:
        print(f"  Top industries : {df['industry_clean'].value_counts().head(5).to_dict()}")
    if "location_country" in df.columns:
        print(f"  Countries      : {df['location_country'].value_counts().head(5).to_dict()}")
    exp_filled = df["experience_min"].notna().sum() if "experience_min" in df.columns else 0
    sal_filled = df["salary_min"].notna().sum() if "salary_min" in df.columns else 0
    print(f"  Experience parsed: {exp_filled} / {len(df)}")
    print(f"  Salary parsed    : {sal_filled} / {len(df)}")


if __name__ == "__main__":
    main()
