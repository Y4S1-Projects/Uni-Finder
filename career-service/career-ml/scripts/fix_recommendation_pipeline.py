#!/usr/bin/env python3
"""
fix_recommendation_pipeline.py
==============================
Comprehensive fix for the career recommendation pipeline.

ROOT CAUSE ANALYSIS:
1. assign_role() ignores seniority - always returns entry-level roles
2. role_skill_profiles_v2.csv only has 15 entry-level roles
3. Jobs with mid/senior seniority are incorrectly mapped to entry-level role_ids
4. Recommender can only recommend 15 roles because that's all it has profiles for

FIX PLAN:
1. Create proper seniority-aware role mapping using role_metadata.json
2. Re-label all jobs with correct role_ids based on (category, seniority)
3. Build role skill profiles for all roles observed in job data
4. Rebuild the job_skill_vectors with correct role assignments

Usage:
    python scripts/fix_recommendation_pipeline.py
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import re

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPANDED_DIR = DATA_DIR / "expanded"

# Input files
ROLE_METADATA_PATH = PROCESSED_DIR / "role_metadata.json"
JOB_VECTORS_PATH = PROCESSED_DIR / "job_skill_vectors_v2.csv"
SKILLS_PATH = EXPANDED_DIR / "skills_v2.csv"
CAREER_LADDERS_PATH = PROCESSED_DIR / "career_ladders_v2.json"

# Output files
FIXED_JOB_VECTORS_PATH = PROCESSED_DIR / "job_skill_vectors_v2_fixed.csv"
FIXED_ROLE_PROFILES_PATH = PROCESSED_DIR / "role_skill_profiles_v2_fixed.csv"


def load_role_metadata() -> dict:
    """Load role metadata and build lookup indexes."""
    with open(ROLE_METADATA_PATH) as f:
        roles = json.load(f)
    
    # Build indexes
    by_id = {r["role_id"]: r for r in roles}
    by_domain_seniority = defaultdict(dict)
    
    for r in roles:
        domain = r["domain"]
        seniority = r["seniority_label"]
        by_domain_seniority[domain][seniority] = r["role_id"]
    
    return {
        "roles": roles,
        "by_id": by_id,
        "by_domain_seniority": by_domain_seniority
    }


def load_career_ladders() -> dict:
    """Load career ladders for domain detection."""
    with open(CAREER_LADDERS_PATH) as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY → DOMAIN MAPPING
# ══════════════════════════════════════════════════════════════════════════════

CATEGORY_TO_DOMAIN = {
    "frontend":   "FRONTEND_ENGINEERING",
    "backend":    "BACKEND_ENGINEERING", 
    "fullstack":  "FULLSTACK_ENGINEERING",
    "software":   "SOFTWARE_ENGINEERING",
    "general":    "SOFTWARE_ENGINEERING",
    "data":       "DATA_ENGINEERING",
    "ai_ml":      "AI_ML",
    "devops":     "DEVOPS_SRE",
    "cloud":      "CLOUD_ENGINEERING",
    "security":   "SECURITY",
    "qa":         "QA_TESTING",
    "mobile":     "MOBILE_ENGINEERING",
    "ui_ux":      "UI_UX_DESIGN",
    "management": "PROJECT_MANAGEMENT",
    "database":   "DATA_ENGINEERING",
    "blockchain": "BLOCKCHAIN_WEB3",
    "game":       "GAME_DEVELOPMENT",
    "embedded":   "EMBEDDED_SYSTEMS",
}

# Seniority level names in order (from role_metadata)
SENIORITY_ORDER = ["intern", "junior", "mid", "senior", "staff", "principal", "director", "lead"]

# Fallback mapping when exact seniority not found - pick closest
SENIORITY_FALLBACK = {
    "intern":     ["junior", "mid"],
    "junior":     ["mid", "intern"],
    "mid":        ["junior", "senior"],
    "senior":     ["mid", "staff", "lead"],
    "staff":      ["senior", "principal", "lead"],
    "principal":  ["staff", "senior", "director"],
    "director":   ["principal", "staff", "lead"],
    "lead":       ["senior", "staff", "principal"],
}


def get_role_for_category_seniority(
    category: str, 
    seniority: str, 
    role_meta: dict,
    job_title: str = ""
) -> tuple[str, str]:
    """
    Map (category, seniority) to best matching (role_id, role_title).
    
    Strategy:
    1. Map category to domain
    2. Look up role for domain + seniority
    3. If exact match not found, try fallbacks
    4. Return (role_id, role_title)
    """
    # Normalize inputs
    category = category.lower().strip()
    seniority = seniority.lower().strip()
    
    # Map category to domain
    domain = CATEGORY_TO_DOMAIN.get(category, "SOFTWARE_ENGINEERING")
    
    # Special case: data analyst/scientist vs engineer
    title_lower = job_title.lower()
    if "data scientist" in title_lower or "research scientist" in title_lower:
        domain = "DATA_SCIENCE"
    elif "data analyst" in title_lower and domain == "DATA_ENGINEERING":
        # Keep as DATA_ENGINEERING but prefer analyst roles
        pass
    
    # Get roles for this domain
    domain_roles = role_meta["by_domain_seniority"].get(domain, {})
    
    # Try exact seniority match
    if seniority in domain_roles:
        role_id = domain_roles[seniority]
        role_title = role_meta["by_id"][role_id]["role_title"]
        return role_id, role_title
    
    # Try fallbacks
    for fallback_seniority in SENIORITY_FALLBACK.get(seniority, []):
        if fallback_seniority in domain_roles:
            role_id = domain_roles[fallback_seniority]
            role_title = role_meta["by_id"][role_id]["role_title"]
            return role_id, role_title
    
    # Last resort: get any role from this domain
    if domain_roles:
        role_id = list(domain_roles.values())[0]
        role_title = role_meta["by_id"][role_id]["role_title"]
        return role_id, role_title
    
    # Ultimate fallback
    return "JR_SE", "Junior Software Engineer"


def fix_job_role_assignments(df: pd.DataFrame, role_meta: dict) -> pd.DataFrame:
    """
    Re-assign role_id and role_title based on category + seniority.
    """
    print("\n=== Fixing Job Role Assignments ===")
    
    fixed_data = []
    role_counts = defaultdict(int)
    
    for idx, row in df.iterrows():
        category = row.get("job_category", "general")
        seniority = row.get("seniority_level", "junior")
        job_title = row.get("job_title", "")
        
        # Get correct role
        new_role_id, new_role_title = get_role_for_category_seniority(
            category, seniority, role_meta, job_title
        )
        
        # Track stats
        old_role = row.get("role_id", "")
        if old_role != new_role_id:
            role_counts[f"{old_role} → {new_role_id}"] += 1
        
        # Update row
        row_dict = row.to_dict()
        row_dict["role_id"] = new_role_id
        row_dict["role_title"] = new_role_title
        fixed_data.append(row_dict)
        
        if idx % 5000 == 0 and idx > 0:
            print(f"  Processed {idx:,} jobs...")
    
    print(f"\n  Total jobs processed: {len(fixed_data):,}")
    print(f"\n  Role reassignments:")
    for change, count in sorted(role_counts.items(), key=lambda x: -x[1])[:30]:
        print(f"    {change}: {count:,}")
    
    return pd.DataFrame(fixed_data)


def build_role_skill_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build role skill profiles from job data.
    
    For each role, calculate skill importance as:
    - frequency: % of jobs in role that have this skill
    - importance: weighted by confidence
    """
    print("\n=== Building Role Skill Profiles ===")
    
    # Get skill columns
    skill_cols = [c for c in df.columns if c.startswith("skill_")]
    print(f"  Found {len(skill_cols)} skill columns")
    
    # Group by role
    role_groups = df.groupby("role_id")
    
    profiles = []
    for role_id, group in role_groups:
        n_jobs = len(group)
        
        # Calculate skill importance
        for skill_col in skill_cols:
            skill_values = group[skill_col].values
            
            # Frequency: % of jobs with skill > 0
            has_skill = (skill_values > 0).sum()
            frequency = has_skill / n_jobs if n_jobs > 0 else 0
            
            # Importance: mean of non-zero values (confidence-weighted)
            nonzero = skill_values[skill_values > 0]
            importance = nonzero.mean() if len(nonzero) > 0 else 0
            
            # Combined score
            combined = frequency * importance
            
            if combined > 0.01:  # threshold to reduce noise
                # Extract skill_id from column name (skill_sk001 -> SK001)
                skill_id = skill_col.replace("skill_", "").upper()
                
                profiles.append({
                    "role_id": role_id,
                    "skill_id": skill_id,
                    "frequency": round(frequency, 4),
                    "importance": round(combined, 4),
                })
    
    df_profiles = pd.DataFrame(profiles)
    
    # Get role titles
    role_titles = df[["role_id", "role_title"]].drop_duplicates().set_index("role_id")["role_title"].to_dict()
    df_profiles["role_title"] = df_profiles["role_id"].map(role_titles)
    
    # Get skill names
    try:
        skills_df = pd.read_csv(SKILLS_PATH)
        skill_names = dict(zip(skills_df["skill_id"], skills_df["name"]))
        df_profiles["skill_name"] = df_profiles["skill_id"].map(skill_names)
    except:
        df_profiles["skill_name"] = df_profiles["skill_id"]
    
    print(f"  Generated profiles for {df_profiles['role_id'].nunique()} unique roles")
    print(f"  Total profile entries: {len(df_profiles):,}")
    
    return df_profiles


def generate_diagnostic_report(df_jobs: pd.DataFrame, df_profiles: pd.DataFrame, role_meta: dict):
    """Generate diagnostic report."""
    print("\n" + "="*80)
    print("DIAGNOSTIC REPORT")
    print("="*80)
    
    # Role distribution after fix
    print("\n=== Role Distribution (After Fix) ===")
    role_counts = df_jobs["role_id"].value_counts()
    print(f"Unique roles: {len(role_counts)}")
    print(role_counts.head(30))
    
    # Seniority distribution
    print("\n=== Seniority Distribution ===")
    print(df_jobs["seniority_level"].value_counts())
    
    # Roles by domain
    print("\n=== Roles by Domain ===")
    for role_id in role_counts.index[:20]:
        if role_id in role_meta["by_id"]:
            meta = role_meta["by_id"][role_id]
            print(f"  {role_id}: {meta['domain']} ({meta['seniority_label']})")
    
    # AI/ML specific
    print("\n=== AI/ML Domain Roles ===")
    ai_ml_roles = [r for r in role_counts.index if role_meta["by_id"].get(r, {}).get("domain") == "AI_ML"]
    for role_id in ai_ml_roles:
        count = role_counts[role_id]
        meta = role_meta["by_id"][role_id]
        print(f"  {role_id} ({meta['seniority_label']}): {count:,} jobs")
    
    # Profile coverage
    print("\n=== Role Profile Coverage ===")
    roles_with_profiles = set(df_profiles["role_id"].unique())
    roles_in_metadata = set(role_meta["by_id"].keys())
    print(f"Roles with profiles: {len(roles_with_profiles)}")
    print(f"Roles in metadata: {len(roles_in_metadata)}")
    print(f"Coverage: {100 * len(roles_with_profiles) / len(roles_in_metadata):.1f}%")
    
    # Missing role profiles
    missing = roles_in_metadata - roles_with_profiles
    if missing:
        print(f"\nMissing profiles for {len(missing)} roles:")
        for r in sorted(missing)[:20]:
            meta = role_meta["by_id"][r]
            print(f"  {r}: {meta['role_title']} ({meta['domain']})")


def main():
    print("="*80)
    print("FIX RECOMMENDATION PIPELINE")
    print("="*80)
    
    # Load data
    print("\n[1] Loading data...")
    role_meta = load_role_metadata()
    print(f"  Loaded {len(role_meta['roles'])} roles from metadata")
    
    df_jobs = pd.read_csv(JOB_VECTORS_PATH)
    print(f"  Loaded {len(df_jobs):,} jobs from job_skill_vectors_v2.csv")
    
    # Show current state
    print("\n[2] Current state (BEFORE fix):")
    print(f"  Unique role_ids: {df_jobs['role_id'].nunique()}")
    print(df_jobs["role_id"].value_counts().head(10))
    
    # Fix role assignments
    print("\n[3] Fixing role assignments...")
    df_fixed = fix_job_role_assignments(df_jobs, role_meta)
    
    # Build role profiles
    print("\n[4] Building role skill profiles...")
    df_profiles = build_role_skill_profiles(df_fixed)
    
    # Save outputs
    print("\n[5] Saving outputs...")
    df_fixed.to_csv(FIXED_JOB_VECTORS_PATH, index=False)
    print(f"  Saved: {FIXED_JOB_VECTORS_PATH}")
    
    df_profiles.to_csv(FIXED_ROLE_PROFILES_PATH, index=False)
    print(f"  Saved: {FIXED_ROLE_PROFILES_PATH}")
    
    # Generate report
    generate_diagnostic_report(df_fixed, df_profiles, role_meta)
    
    print("\n" + "="*80)
    print("FIX COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the diagnostic report above")
    print("2. Copy *_fixed.csv files to replace original v2 files:")
    print(f"   cp {FIXED_JOB_VECTORS_PATH} {JOB_VECTORS_PATH}")
    print(f"   cp {FIXED_ROLE_PROFILES_PATH} {PROCESSED_DIR / 'role_skill_profiles_v2.csv'}")
    print("3. Restart the career-service to load new data")
    print("4. Test recommendations with AI/ML skills")


if __name__ == "__main__":
    main()
