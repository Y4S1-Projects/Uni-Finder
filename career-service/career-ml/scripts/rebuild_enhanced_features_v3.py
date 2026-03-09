#!/usr/bin/env python3
"""
rebuild_enhanced_features_v3.py — Rebuild Enhanced Vectors from v3 Data
=========================================================================
Phase A, Step 6: Rebuild derived datasets after skill normalization & repair.

This script replaces the stale build_enhanced_features.py pipeline:
- Uses job_skill_vectors_v3.csv   (tier-weighted, 1,147 skills)
- Uses detected_domain from repair (20 domains, not 7)
- Uses skills_v2.csv              (1,147 skills, not 300)
- Generates new enhanced profiles & role profiles
- Generates updated enhanced_feature_columns.json

Outputs:
  - jobs_enhanced_features_v3.csv
  - job_feature_vectors_enhanced_v3.csv
  - enhanced_feature_columns_v3.json
  - role_enhanced_profiles_v3.csv
  - role_skill_profiles_v3.csv

Run:
    cd career-service/career-ml
    python scripts/rebuild_enhanced_features_v3.py
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_normalizer import (
    SkillNormalizer,
    DOMAIN_SKILL_CLUSTERS,
)

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # career-ml/
DATA_DIR = BASE_DIR / "data"
EXPANDED = DATA_DIR / "expanded"
PROCESSED = DATA_DIR / "processed"
CAREER_PATH = BASE_DIR / "career_path"
REPORTS = DATA_DIR / "reports"
REPORTS.mkdir(exist_ok=True)

SKILLS_CSV = EXPANDED / "skills_v2.csv"

# Input: either the v3 (tier-weighted) or fall back to v2_fixed
JSV_V3 = PROCESSED / "job_skill_vectors_v3.csv"
JSV_V2_FIXED = PROCESSED / "job_skill_vectors_v2_fixed.csv"

# Enhanced features from original pipeline (for text-based features)
JOBS_ENHANCED_FEATURES_OLD = PROCESSED / "jobs_enhanced_features.csv"
JOBS_LABELED = PROCESSED / "jobs_labeled.csv"

# Output paths
OUTPUT_FEATURES = PROCESSED / "jobs_enhanced_features_v3.csv"
OUTPUT_VECTORS = PROCESSED / "job_feature_vectors_enhanced_v3.csv"
OUTPUT_COLUMNS = PROCESSED / "enhanced_feature_columns_v3.json"
OUTPUT_ROLE_ENHANCED = PROCESSED / "role_enhanced_profiles_v3.csv"
OUTPUT_ROLE_SKILL = PROCESSED / "role_skill_profiles_v3.csv"
OUTPUT_ROLE_METADATA = PROCESSED / "role_metadata_v3.json"


# ─── Domain enum (matches DOMAIN_SKILL_CLUSTERS) ─────────────────────
ALL_DOMAINS = sorted(DOMAIN_SKILL_CLUSTERS.keys())

EXPERIENCE_LEVELS = ["student", "0-1", "1-3", "3-5", "5+", "unknown"]
EDUCATION_LEVELS = ["al", "diploma", "hnd", "bachelors", "masters", "phd", "unknown"]
STATUS_VALUES = ["student", "graduate", "working", "unknown"]
JOBTYPE_VALUES = ["full_time", "part_time", "contract", "internship", "remote", "unknown"]


# ─── Feature extraction (reused from original, but with better defaults) ──

def extract_experience_from_role(role_id: str) -> str:
    """Extract experience level from role_id suffixes."""
    rid = str(role_id).upper()
    if "INTERN" in rid or "TRAINEE" in rid:
        return "student"
    if "_INT" in rid or "_ENTRY" in rid or "_JR" in rid or "JUNIOR" in rid:
        return "0-1"
    if "_MID" in rid:
        return "1-3"
    if "_SR" in rid or "SENIOR" in rid or "_LEAD" in rid:
        return "5+"
    if "_PRINCIPAL" in rid or "_STAFF" in rid:
        return "5+"
    return "unknown"


def extract_experience_from_seniority(seniority: str) -> str:
    """Map seniority_level column to experience range."""
    sen = str(seniority).lower().strip()
    mapping = {
        "intern": "student",
        "entry": "0-1",
        "junior": "0-1",
        "mid": "1-3",
        "mid-level": "1-3",
        "senior": "5+",
        "lead": "5+",
        "principal": "5+",
        "staff": "5+",
    }
    return mapping.get(sen, "unknown")


def infer_education(experience_level: str) -> str:
    """Default education based on experience level."""
    mapping = {
        "student": "bachelors",
        "0-1": "bachelors",
        "1-3": "bachelors",
        "3-5": "bachelors",
        "5+": "masters",
        "unknown": "bachelors",
    }
    return mapping.get(experience_level, "bachelors")


def infer_status(experience_level: str) -> str:
    """Map experience level → current status."""
    mapping = {
        "student": "student",
        "0-1": "graduate",
        "1-3": "working",
        "3-5": "working",
        "5+": "working",
        "unknown": "graduate",
    }
    return mapping.get(experience_level, "graduate")


def rebuild_all():
    """Main rebuild pipeline."""
    print("=" * 70)
    print("REBUILD ENHANCED FEATURES v3")
    print("=" * 70)

    # Load normalizer
    normalizer = SkillNormalizer(SKILLS_CSV)

    # Load skill vectors
    if JSV_V3.exists():
        print(f"Using tier-weighted vectors: {JSV_V3.name}")
        jsv = pd.read_csv(JSV_V3)
    else:
        print(f"V3 not found, falling back to: {JSV_V2_FIXED.name}")
        jsv = pd.read_csv(JSV_V2_FIXED)

    skill_cols = sorted([c for c in jsv.columns if c.startswith("skill_")])
    meta_cols = [c for c in jsv.columns if not c.startswith("skill_")]
    print(f"Loaded: {len(jsv)} jobs, {len(skill_cols)} skill columns")

    # ─── Step 1: Extract / assign features ────────────────────────────
    print("\n--- Step 1: Feature Extraction ---")

    # Domain: use detected_domain if present (from repair), else infer
    if "detected_domain" in jsv.columns:
        print("  Using detected_domain from repair step")
        jsv["domain"] = jsv["detected_domain"]
    else:
        print("  Detecting domains from skill clusters...")
        domains = []
        for _, row in jsv.iterrows():
            active = [col.replace("skill_", "").upper()
                      for col in skill_cols if row[col] > 0]
            detected = normalizer.detect_domain_from_skills(active)
            domains.append(detected[0][0] if detected else "FULLSTACK_ENGINEERING")
        jsv["domain"] = domains

    # Experience level
    if "seniority_level" in jsv.columns:
        print("  Extracting experience from seniority_level column")
        jsv["experience_level"] = jsv["seniority_level"].apply(extract_experience_from_seniority)
        # Fill unknowns from role_id
        mask = jsv["experience_level"] == "unknown"
        jsv.loc[mask, "experience_level"] = jsv.loc[mask, "role_id"].apply(extract_experience_from_role)
    else:
        print("  Extracting experience from role_id")
        jsv["experience_level"] = jsv["role_id"].apply(extract_experience_from_role)

    # Education & status (inferred defaults)
    jsv["education_level"] = jsv["experience_level"].apply(infer_education)
    jsv["current_status"] = jsv["experience_level"].apply(infer_status)
    jsv["job_type_clean"] = "full_time"  # Default; could be enriched from labeled data

    # Try to enrich from old enhanced features if available
    if JOBS_ENHANCED_FEATURES_OLD.exists():
        print("  Enriching from existing enhanced features...")
        try:
            old_feat = pd.read_csv(JOBS_ENHANCED_FEATURES_OLD)
            if "job_uid" in old_feat.columns and "job_uid" in jsv.columns:
                merge_cols = []
                if "education_level" in old_feat.columns:
                    merge_cols.append("education_level")
                if "job_type_clean" in old_feat.columns:
                    merge_cols.append("job_type_clean")
                if merge_cols:
                    old_subset = old_feat[["job_uid"] + merge_cols].drop_duplicates(subset=["job_uid"])
                    jsv = jsv.merge(old_subset, on="job_uid", how="left", suffixes=("", "_old"))
                    for col in merge_cols:
                        old_col = f"{col}_old"
                        if old_col in jsv.columns:
                            mask = jsv[col].isna() | (jsv[col] == "unknown")
                            jsv.loc[mask, col] = jsv.loc[mask, old_col]
                            jsv.drop(columns=[old_col], inplace=True, errors="ignore")
                    print(f"    Enriched {merge_cols} from old features")
        except Exception as e:
            print(f"    Warning: could not enrich from old features: {e}")

    # Print feature distributions
    for col in ["domain", "experience_level", "education_level", "current_status"]:
        print(f"\n  {col}:")
        vc = jsv[col].value_counts()
        for val, cnt in vc.items():
            print(f"    {val}: {cnt}")

    # ─── Step 2: One-hot encode features ──────────────────────────────
    print("\n--- Step 2: One-Hot Encoding ---")

    feature_columns = {}
    onehot_cols = []

    # Experience
    for val in EXPERIENCE_LEVELS:
        col_name = f"exp_{val}"
        jsv[col_name] = (jsv["experience_level"] == val).astype(float)
        feature_columns.setdefault("experience_level", []).append(col_name)
        onehot_cols.append(col_name)

    # Education
    for val in EDUCATION_LEVELS:
        col_name = f"edu_{val}"
        jsv[col_name] = (jsv["education_level"] == val).astype(float)
        feature_columns.setdefault("education_level", []).append(col_name)
        onehot_cols.append(col_name)

    # Domain — now 20 domains instead of 7!
    for val in ALL_DOMAINS:
        col_name = f"domain_{val}"
        jsv[col_name] = (jsv["domain"] == val).astype(float)
        feature_columns.setdefault("domain", []).append(col_name)
        onehot_cols.append(col_name)

    # Status
    for val in STATUS_VALUES:
        col_name = f"status_{val}"
        jsv[col_name] = (jsv["current_status"] == val).astype(float)
        feature_columns.setdefault("current_status", []).append(col_name)
        onehot_cols.append(col_name)

    # Job Type
    for val in JOBTYPE_VALUES:
        col_name = f"jobtype_{val}"
        jsv[col_name] = (jsv["job_type_clean"] == val).astype(float)
        feature_columns.setdefault("job_type_clean", []).append(col_name)
        onehot_cols.append(col_name)

    all_feature_cols = skill_cols + onehot_cols
    print(f"Total feature dimensions: {len(all_feature_cols)}")
    print(f"  Skill dims:     {len(skill_cols)}")
    print(f"  One-hot dims:   {len(onehot_cols)}")
    print(f"  Domain values:  {len(ALL_DOMAINS)}")

    # ─── Step 3: Save enhanced features ───────────────────────────────
    print("\n--- Step 3: Save Enhanced Features ---")

    feat_cols = ["job_uid", "job_title", "role_id", "role_title",
                 "domain", "experience_level", "education_level",
                 "current_status", "job_type_clean"]
    # Keep only columns that exist
    feat_cols = [c for c in feat_cols if c in jsv.columns]
    jsv[feat_cols].to_csv(OUTPUT_FEATURES, index=False)
    print(f"Saved: {OUTPUT_FEATURES} ({len(jsv)} rows)")

    # ─── Step 4: Save enhanced vectors ────────────────────────────────
    print("\n--- Step 4: Save Enhanced Vectors ---")

    vec_meta_cols = ["job_uid", "job_title", "role_id", "role_title"]
    vec_meta_cols = [c for c in vec_meta_cols if c in jsv.columns]
    vec_output_cols = vec_meta_cols + all_feature_cols
    # Ensure all columns exist
    for col in all_feature_cols:
        if col not in jsv.columns:
            jsv[col] = 0.0
    jsv[vec_output_cols].to_csv(OUTPUT_VECTORS, index=False)
    print(f"Saved: {OUTPUT_VECTORS} ({len(jsv)} rows x {len(vec_output_cols)} cols)")

    # ─── Step 5: Save column metadata ─────────────────────────────────
    print("\n--- Step 5: Save Column Metadata ---")

    meta = {
        "version": "v3",
        "skill_columns": skill_cols,
        "onehot_columns": onehot_cols,
        "all_feature_columns": all_feature_cols,
        "feature_groups": feature_columns,
        "experience_values": EXPERIENCE_LEVELS,
        "education_values": EDUCATION_LEVELS,
        "domain_values": ALL_DOMAINS,
        "status_values": STATUS_VALUES,
        "jobtype_values": JOBTYPE_VALUES,
        "total_dimensions": len(all_feature_cols),
        "skill_dimensions": len(skill_cols),
        "onehot_dimensions": len(onehot_cols),
    }
    with open(OUTPUT_COLUMNS, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved: {OUTPUT_COLUMNS}")

    # ─── Step 6: Build Role-Level Enhanced Profiles ───────────────────
    print("\n--- Step 6: Build Role Enhanced Profiles ---")

    # Group by role_id and average all feature columns
    role_groups = jsv.groupby("role_id")

    # Enhanced profiles (skills + one-hot features)
    role_enhanced = role_groups[all_feature_cols].mean()
    role_enhanced.to_csv(OUTPUT_ROLE_ENHANCED)
    print(f"Saved: {OUTPUT_ROLE_ENHANCED} ({role_enhanced.shape[0]} roles x {role_enhanced.shape[1]} dims)")

    # Skill-only profiles
    role_skill_only = role_groups[skill_cols].mean()
    role_skill_only.to_csv(OUTPUT_ROLE_SKILL)
    print(f"Saved: {OUTPUT_ROLE_SKILL} ({role_skill_only.shape[0]} roles x {role_skill_only.shape[1]} dims)")

    # Role metadata
    role_meta = {}
    for role_id, group in role_groups:
        active_skills = []
        for col in skill_cols:
            mean_val = group[col].mean()
            if mean_val > 0.3:
                sid = col.replace("skill_", "").upper()
                name = normalizer.id_to_name.get(sid, sid)
                active_skills.append({"id": sid, "name": name, "weight": round(mean_val, 3)})

        active_skills.sort(key=lambda x: x["weight"], reverse=True)
        domain = group["domain"].mode().iloc[0] if "domain" in group.columns and not group["domain"].mode().empty else "unknown"
        exp = group["experience_level"].mode().iloc[0] if "experience_level" in group.columns and not group["experience_level"].mode().empty else "unknown"

        role_meta[role_id] = {
            "job_count": len(group),
            "domain": domain,
            "typical_experience": exp,
            "top_skills": active_skills[:30],
            "total_active_skills": len(active_skills),
        }

    with open(OUTPUT_ROLE_METADATA, "w") as f:
        json.dump(role_meta, f, indent=2)
    print(f"Saved: {OUTPUT_ROLE_METADATA} ({len(role_meta)} roles)")

    # ─── Step 7: Print Summary ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("REBUILD COMPLETE — v3 Enhanced Features")
    print("=" * 70)
    print(f"\nOutput files:")
    print(f"  1. {OUTPUT_FEATURES.name}  ({len(jsv)} jobs, features)")
    print(f"  2. {OUTPUT_VECTORS.name}  ({len(jsv)} x {len(all_feature_cols)} dims)")
    print(f"  3. {OUTPUT_COLUMNS.name}")
    print(f"  4. {OUTPUT_ROLE_ENHANCED.name}  ({role_enhanced.shape})")
    print(f"  5. {OUTPUT_ROLE_SKILL.name}  ({role_skill_only.shape})")
    print(f"  6. {OUTPUT_ROLE_METADATA.name}  ({len(role_meta)} roles)")

    print(f"\nDimension comparison:")
    # Try to read old metadata
    old_meta_path = PROCESSED / "enhanced_feature_columns.json"
    if old_meta_path.exists():
        with open(old_meta_path) as f:
            old = json.load(f)
        print(f"  OLD: {len(old.get('skill_columns', []))} skills + "
              f"{len(old.get('onehot_columns', []))} categorical = "
              f"{len(old.get('all_feature_columns', []))} total")
    print(f"  NEW: {len(skill_cols)} skills + {len(onehot_cols)} categorical = "
          f"{len(all_feature_cols)} total")

    print(f"\nDomain coverage:")
    for domain, count in jsv["domain"].value_counts().items():
        role_count = len(jsv[jsv["domain"] == domain]["role_id"].unique())
        print(f"  {domain}: {count} jobs, {role_count} roles")


if __name__ == "__main__":
    rebuild_all()
