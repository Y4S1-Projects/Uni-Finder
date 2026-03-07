"""
Build Enhanced Job Features & Vectors
======================================
Tasks 1 & 2 from the Multi-Feature Career Recommendation System.

This script:
1. Extracts experience_level, education_level, domain, current_status, job_type
   from job descriptions/requirements (since raw metadata columns are mostly empty).
2. One-hot encodes the new features and concatenates with existing 300-dim skill vectors.
3. Saves:
   - jobs_enhanced_features.csv   (human-readable features per job)
   - job_feature_vectors_enhanced.csv  (skill + feature vectors for matching)
   - enhanced_feature_columns.json     (column metadata for the user vectorizer)
"""

import re
import json
import pandas as pd
import numpy as np
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # career-ml/
PROCESSED = BASE_DIR / "data" / "processed"
SKILL_GAP = BASE_DIR / "skill_gap"
CAREER_PATH = BASE_DIR / "career_path"
OUTPUT_DIR = PROCESSED                                      # save alongside existing CSVs

JOBS_LABELED  = PROCESSED / "jobs_labeled.csv"
JOB_VECTORS   = PROCESSED / "job_skill_vectors.csv"
SKILLS_CSV    = PROCESSED / "skills.csv"
LADDERS_JSON  = CAREER_PATH / "career_ladders.json"

# ─── 1. Feature Extraction Functions ────────────────────────────────────────


def extract_experience_level(row) -> str:
    """
    Parse experience level from experience_raw, job_title, description.
    Returns: 'student', '0-1', '1-3', '3-5', '5+', or 'unknown'
    """
    # First check the explicit column if populated
    raw = str(row.get("experience_raw", "")).strip().lower()
    if raw and raw != "nan":
        if raw in ("entry-level", "entry level", "intern", "internship", "trainee"):
            return "0-1"
        if raw in ("junior", "junior-level"):
            return "0-1"
        if raw in ("mid-level", "mid level", "intermediate"):
            return "1-3"
        if raw in ("senior", "senior-level", "lead"):
            return "5+"
        # Try to parse "X years" from raw
        m = re.search(r"(\d+)", raw)
        if m:
            years = int(m.group(1))
            if years == 0:
                return "0-1"
            elif years <= 1:
                return "0-1"
            elif years <= 3:
                return "1-3"
            elif years <= 5:
                return "3-5"
            else:
                return "5+"

    # Parse from description + requirements
    text = (str(row.get("description", "")) + " " + str(row.get("requirements_text", ""))).lower()
    title = str(row.get("job_title", "")).lower()

    # Check title-based hints
    if any(kw in title for kw in ["intern", "trainee", "apprentice"]):
        return "student"
    if any(kw in title for kw in ["junior", "jr.", "jr ", "entry"]):
        return "0-1"
    if any(kw in title for kw in ["senior", "sr.", "sr ", "lead", "principal", "staff"]):
        return "5+"

    # Parse year ranges from text: "2-5 years", "3+ years", "minimum 2 years"
    year_patterns = [
        r"(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"(?:minimum|at least|min)\s*(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*(?:years?|yrs?)\s*(?:minimum|min)",
    ]

    years_found = []
    for pattern in year_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if isinstance(m, tuple):
                years_found.extend(int(x) for x in m if x.isdigit())
            else:
                years_found.append(int(m))

    if years_found:
        min_years = min(years_found)
        if min_years == 0:
            return "0-1"
        elif min_years <= 1:
            return "0-1"
        elif min_years <= 3:
            return "1-3"
        elif min_years <= 5:
            return "3-5"
        else:
            return "5+"

    # Text-based keywords
    if any(kw in text for kw in ["entry level", "entry-level", "no experience required", "fresh graduate", "new graduate"]):
        return "0-1"
    if any(kw in text for kw in ["junior", "beginner", "early career"]):
        return "0-1"
    if any(kw in text for kw in ["mid-level", "mid level", "intermediate"]):
        return "1-3"
    if any(kw in text for kw in ["senior", "lead", "principal", "expert", "seasoned"]):
        return "5+"

    # Infer from role_id (these are mostly entry/junior roles)
    role_id = str(row.get("role_id", "")).upper()
    if "INTERN" in role_id or "TRAINEE" in role_id:
        return "student"
    if "JR_" in role_id or role_id.endswith("_INT"):
        return "0-1"

    return "unknown"


def extract_education_level(row) -> str:
    """
    Extract education level from description/requirements.
    Returns: 'al', 'diploma', 'hnd', 'bachelors', 'masters', 'phd', 'unknown'
    """
    text = (str(row.get("description", "")) + " " + str(row.get("requirements_text", ""))).lower()

    # Check from highest to lowest
    if any(kw in text for kw in ["ph.d", "phd", "doctorate", "doctoral"]):
        return "phd"
    if any(kw in text for kw in ["master's", "masters", "msc", "m.sc", "m.tech", "mba", "m.b.a", "postgraduate", "post-graduate"]):
        return "masters"
    if any(kw in text for kw in ["bachelor's", "bachelors", "b.sc", "bsc", "b.tech", "b.e.", "undergraduate", "degree", "university degree", "college degree", "4-year degree", "4 year degree"]):
        return "bachelors"
    if any(kw in text for kw in ["hnd", "higher national diploma"]):
        return "hnd"
    if any(kw in text for kw in ["diploma", "associate", "associate's"]):
        return "diploma"
    if any(kw in text for kw in ["a/l", "a-level", "a level", "advanced level", "high school"]):
        return "al"

    # Default: most IT jobs in Sri Lanka need at least a bachelor's
    return "bachelors"


def map_to_domain(row) -> str:
    """
    Map each job to a broad domain using role_id -> career_ladders mapping.
    Falls back to text-based inference.
    """
    role_id = str(row.get("role_id", "")).upper()

    # Load career ladders for direct mapping
    domain_map = {}
    try:
        with open(LADDERS_JSON, "r") as f:
            ladders = json.load(f)
        for domain, roles in ladders.items():
            for r in roles:
                domain_map[r] = domain
    except Exception:
        pass

    if role_id in domain_map:
        return domain_map[role_id]

    # Fallback: text + industry column
    industry = str(row.get("industry", "")).lower()
    title = str(row.get("job_title", "")).lower()
    text = (str(row.get("description", "")) + " " + str(row.get("requirements_text", ""))).lower()

    # Industry-based
    industry_map = {
        "artificial intelligence": "AI_ML",
        "machine learning": "AI_ML",
        "data engineering": "DATA",
        "analytics": "DATA",
        "devops": "DEVOPS",
        "quality assurance": "QA",
        "mobile development": "MOBILE",
        "design": "UI_UX",
        "web development": "SOFTWARE_ENGINEERING",
        "technology": "SOFTWARE_ENGINEERING",
        "it services": "SOFTWARE_ENGINEERING",
        "support": "SOFTWARE_ENGINEERING",
        "business analysis": "DATA",
    }

    for key, domain in industry_map.items():
        if key in industry:
            return domain

    # Title / text-based
    if any(kw in title for kw in ["data", "analyst", "analytics", "bi ", "business intelligence"]):
        return "DATA"
    if any(kw in title for kw in ["ml", "machine learning", "ai ", "artificial intelligence", "deep learning"]):
        return "AI_ML"
    if any(kw in title for kw in ["devops", "cloud", "infrastructure", "sre", "platform"]):
        return "DEVOPS"
    if any(kw in title for kw in ["qa", "quality", "test", "sdet"]):
        return "QA"
    if any(kw in title for kw in ["mobile", "ios", "android", "flutter", "react native"]):
        return "MOBILE"
    if any(kw in title for kw in ["ui", "ux", "design", "user experience", "user interface"]):
        return "UI_UX"

    return "SOFTWARE_ENGINEERING"


def infer_current_status(experience_level: str) -> str:
    """Map experience level to likely current status."""
    mapping = {
        "student": "student",
        "0-1": "graduate",
        "1-3": "working",
        "3-5": "working",
        "5+": "working",
        "unknown": "graduate",
    }
    return mapping.get(experience_level, "graduate")


def standardize_job_type(row) -> str:
    """
    Clean job_type values. Extract from text if not available.
    Returns: 'full_time', 'part_time', 'contract', 'internship', 'remote', 'unknown'
    """
    raw = str(row.get("job_type", "")).strip().lower()
    if raw and raw != "nan":
        if "full" in raw:
            return "full_time"
        if "part" in raw:
            return "part_time"
        if "contract" in raw:
            return "contract"
        if "intern" in raw:
            return "internship"
        if "remote" in raw or "freelance" in raw:
            return "remote"

    # Parse from text
    text = (str(row.get("description", "")) + " " + str(row.get("requirements_text", ""))).lower()
    title = str(row.get("job_title", "")).lower()

    if "internship" in title or "intern " in title:
        return "internship"
    if "contract" in text[:500]:  # Usually mentioned early
        return "contract"
    if "part-time" in text or "part time" in text:
        return "part_time"
    if "remote" in text[:500] and ("fully remote" in text or "100% remote" in text):
        return "remote"

    # Default for most jobs
    return "full_time"


# ─── 2. Main Pipeline ───────────────────────────────────────────────────────

def build_enhanced_features():
    """Task 1: Extract and standardize features from jobs_labeled.csv"""
    print("=" * 60)
    print("TASK 1: Feature Extraction from Existing Data")
    print("=" * 60)

    df = pd.read_csv(JOBS_LABELED)
    print(f"Loaded {len(df)} jobs from {JOBS_LABELED.name}")

    # Extract features
    print("Extracting experience levels...")
    df["experience_level"] = df.apply(extract_experience_level, axis=1)

    print("Extracting education levels...")
    df["education_level"] = df.apply(extract_education_level, axis=1)

    print("Mapping to domains...")
    df["domain"] = df.apply(map_to_domain, axis=1)

    print("Inferring current status...")
    df["current_status"] = df["experience_level"].apply(infer_current_status)

    print("Standardizing job types...")
    df["job_type_clean"] = df.apply(standardize_job_type, axis=1)

    # Print distributions
    print("\n--- Feature Distributions ---")
    for col in ["experience_level", "education_level", "domain", "current_status", "job_type_clean"]:
        print(f"\n{col}:")
        print(df[col].value_counts().to_string())

    # Save enhanced features
    output_cols = [
        "job_uid", "job_title", "job_title_clean", "role_id", "role_title",
        "matched_skill_ids", "matched_skills", "matched_skill_count",
        "experience_level", "education_level", "domain", "current_status", "job_type_clean",
    ]
    df_out = df[output_cols]
    out_path = OUTPUT_DIR / "jobs_enhanced_features.csv"
    df_out.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path} ({len(df_out)} rows, {len(output_cols)} columns)")

    return df_out


def build_enhanced_vectors(df_features):
    """Task 2: Combine skill vectors with one-hot encoded categorical features"""
    print("\n" + "=" * 60)
    print("TASK 2: Build Enhanced Job Vectors")
    print("=" * 60)

    # Load existing skill vectors
    df_skills = pd.read_csv(JOB_VECTORS)
    print(f"Loaded skill vectors: {df_skills.shape}")

    skill_cols = [c for c in df_skills.columns if c.startswith("skill_")]
    print(f"Skill dimensions: {len(skill_cols)}")

    # Merge with enhanced features on job_title_clean
    df_merged = df_skills.merge(
        df_features[["job_title_clean", "role_id", "experience_level", "education_level",
                      "domain", "current_status", "job_type_clean"]],
        on=["job_title_clean", "role_id"],
        how="left",
        suffixes=("", "_feat"),
    )
    # Drop duplicates (many-to-one merge may create extra rows)
    df_merged = df_merged.drop_duplicates(subset=["job_title", "role_id"] + skill_cols[:1])
    print(f"Merged dataset: {df_merged.shape}")

    # Fill NaN values in new columns
    for col in ["experience_level", "education_level", "domain", "current_status", "job_type_clean"]:
        df_merged[col] = df_merged[col].fillna("unknown")

    # One-hot encode new features
    experience_vals = ["student", "0-1", "1-3", "3-5", "5+", "unknown"]
    education_vals = ["al", "diploma", "hnd", "bachelors", "masters", "phd", "unknown"]
    domain_vals = ["SOFTWARE_ENGINEERING", "DATA", "AI_ML", "DEVOPS", "QA", "MOBILE", "UI_UX"]
    status_vals = ["student", "graduate", "working", "unknown"]
    jobtype_vals = ["full_time", "part_time", "contract", "internship", "remote", "unknown"]

    feature_columns = {}

    # Experience
    for val in experience_vals:
        col_name = f"exp_{val}"
        df_merged[col_name] = (df_merged["experience_level"] == val).astype(float)
        feature_columns.setdefault("experience_level", []).append(col_name)

    # Education
    for val in education_vals:
        col_name = f"edu_{val}"
        df_merged[col_name] = (df_merged["education_level"] == val).astype(float)
        feature_columns.setdefault("education_level", []).append(col_name)

    # Domain
    for val in domain_vals:
        col_name = f"domain_{val}"
        df_merged[col_name] = (df_merged["domain"] == val).astype(float)
        feature_columns.setdefault("domain", []).append(col_name)

    # Status
    for val in status_vals:
        col_name = f"status_{val}"
        df_merged[col_name] = (df_merged["current_status"] == val).astype(float)
        feature_columns.setdefault("current_status", []).append(col_name)

    # Job Type
    for val in jobtype_vals:
        col_name = f"jobtype_{val}"
        df_merged[col_name] = (df_merged["job_type_clean"] == val).astype(float)
        feature_columns.setdefault("job_type_clean", []).append(col_name)

    # Collect all one-hot columns
    onehot_cols = []
    for cat_cols in feature_columns.values():
        onehot_cols.extend(cat_cols)

    # Build final enhanced vector columns
    all_feature_cols = skill_cols + onehot_cols
    print(f"Total feature dimensions: {len(all_feature_cols)} "
          f"({len(skill_cols)} skills + {len(onehot_cols)} categorical)")

    # Keep metadata + features
    meta_cols = ["job_title", "job_title_clean", "role_id", "role_title"]
    output_cols = meta_cols + all_feature_cols
    df_vectors = df_merged[output_cols]

    # Save enhanced vectors
    vectors_path = OUTPUT_DIR / "job_feature_vectors_enhanced.csv"
    df_vectors.to_csv(vectors_path, index=False)
    print(f"Saved: {vectors_path} ({df_vectors.shape})")

    # Save feature column metadata
    meta = {
        "skill_columns": skill_cols,
        "onehot_columns": onehot_cols,
        "all_feature_columns": all_feature_cols,
        "feature_groups": feature_columns,
        "experience_values": experience_vals,
        "education_values": education_vals,
        "domain_values": domain_vals,
        "status_values": status_vals,
        "jobtype_values": jobtype_vals,
    }
    meta_path = OUTPUT_DIR / "enhanced_feature_columns.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved: {meta_path}")

    # Also build enhanced ROLE-level profiles for faster matching
    build_role_enhanced_profiles(df_merged, skill_cols, onehot_cols, all_feature_cols)

    return df_vectors


def build_role_enhanced_profiles(df_merged, skill_cols, onehot_cols, all_feature_cols):
    """
    Build role-level enhanced profiles by averaging features per role.
    This is used for the primary recommendation (role-level matching).
    """
    print("\n--- Building Enhanced Role Profiles ---")

    # Group by role_id and average all feature columns
    role_profiles = df_merged.groupby("role_id")[all_feature_cols].mean()
    
    # Save role-level enhanced profiles
    role_path = OUTPUT_DIR / "role_enhanced_profiles.csv"
    role_profiles.to_csv(role_path)
    print(f"Saved: {role_path} ({role_profiles.shape})")
    print(f"Roles: {list(role_profiles.index)}")

    return role_profiles


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Multi-Feature Career Recommendation Data Pipeline")
    print("=" * 60)

    # Task 1
    df_features = build_enhanced_features()

    # Task 2
    df_vectors = build_enhanced_vectors(df_features)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  1. {OUTPUT_DIR / 'jobs_enhanced_features.csv'}")
    print(f"  2. {OUTPUT_DIR / 'job_feature_vectors_enhanced.csv'}")
    print(f"  3. {OUTPUT_DIR / 'enhanced_feature_columns.json'}")
    print(f"  4. {OUTPUT_DIR / 'role_enhanced_profiles.csv'}")
