#!/usr/bin/env python3
"""
rebuild_enhanced_role_profiles.py
==================================
Rebuild enhanced role profiles from the fixed job skill vectors.

This generates a 330-dimensional profile for each role:
- 300 skill dimensions (from skills in job data)
- 30 categorical dimensions (one-hot encoded features)

The categorical features are estimated from the role distribution in job data.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Input files
JOB_VECTORS_PATH = PROCESSED_DIR / "job_skill_vectors_v2_fixed.csv"  # Fixed job data
SKILLS_PATH = DATA_DIR / "expanded" / "skills_v2.csv"
ROLE_METADATA_PATH = PROCESSED_DIR / "role_metadata.json"
FEATURE_META_PATH = PROCESSED_DIR / "enhanced_feature_columns.json"

# Output files  
OUTPUT_PATH = PROCESSED_DIR / "role_enhanced_profiles.csv"


def load_feature_metadata():
    """Load existing feature metadata."""
    with open(FEATURE_META_PATH) as f:
        return json.load(f)


def load_role_metadata():
    """Load role metadata."""
    with open(ROLE_METADATA_PATH) as f:
        roles = json.load(f)
    return {r["role_id"]: r for r in roles}


def estimate_role_categorical_features(role_id: str, role_meta: dict, feature_meta: dict) -> dict:
    """
    Estimate categorical feature values for a role based on metadata.
    
    Returns dict of {feature: value}
    """
    role = role_meta.get(role_id, {})
    
    # Experience level based on seniority
    seniority = role.get("seniority_label", "mid")
    exp_mapping = {
        "intern": "student",
        "junior": "0-1",
        "mid": "1-3",
        "senior": "3-5",
        "staff": "5+",
        "principal": "5+",
        "director": "5+",
        "lead": "5+"
    }
    experience = exp_mapping.get(seniority, "1-3")
    
    # Education level (estimate based on seniority)
    edu_mapping = {
        "intern": "bachelors",
        "junior": "bachelors",
        "mid": "bachelors",
        "senior": "bachelors",
        "staff": "masters",
        "principal": "masters",
        "director": "masters",
        "lead": "masters"
    }
    education = edu_mapping.get(seniority, "bachelors")
    
    # Domain directly from metadata
    domain_raw = role.get("domain", "SOFTWARE_ENGINEERING")
    domain_mapping = {
        "SOFTWARE_ENGINEERING": "SOFTWARE_ENGINEERING",
        "FRONTEND_ENGINEERING": "SOFTWARE_ENGINEERING",
        "BACKEND_ENGINEERING": "SOFTWARE_ENGINEERING", 
        "FULLSTACK_ENGINEERING": "SOFTWARE_ENGINEERING",
        "DATA_ENGINEERING": "DATA",
        "DATA_SCIENCE": "DATA",
        "AI_ML": "AI_ML",
        "DEVOPS_SRE": "DEVOPS",
        "CLOUD_ENGINEERING": "DEVOPS",
        "SECURITY": "SOFTWARE_ENGINEERING",
        "QA_TESTING": "QA",
        "MOBILE_ENGINEERING": "SOFTWARE_ENGINEERING",
        "UI_UX_DESIGN": "UI_UX",
        "PRODUCT_MANAGEMENT": "SOFTWARE_ENGINEERING",
        "BUSINESS_ANALYSIS": "SOFTWARE_ENGINEERING",
        "PROJECT_MANAGEMENT": "SOFTWARE_ENGINEERING",
        "TECHNICAL_WRITING": "SOFTWARE_ENGINEERING",
        "BLOCKCHAIN_WEB3": "SOFTWARE_ENGINEERING",
        "GAME_DEVELOPMENT": "SOFTWARE_ENGINEERING",
        "EMBEDDED_SYSTEMS": "SOFTWARE_ENGINEERING",
    }
    domain = domain_mapping.get(domain_raw, "SOFTWARE_ENGINEERING")
    
    # Status (working prof assumed for all roles)
    status = "working"
    
    # Job type (full_time default)
    jobtype = "full_time"
    
    return {
        "experience": experience,
        "education": education,
        "domain": domain,
        "status": status,
        "jobtype": jobtype
    }


def encode_categorical(value: str, value_list: list) -> np.ndarray:
    """One-hot encode a categorical value."""
    vector = np.zeros(len(value_list))
    if value in value_list:
        idx = value_list.index(value)
        vector[idx] = 1.0
    return vector


def build_enhanced_profiles():
    """Build enhanced role profiles with skill + categorical dimensions."""
    print("=== Building Enhanced Role Profiles ===")
    
    # Load data
    print("\n[1] Loading data...")
    feature_meta = load_feature_metadata()
    role_meta = load_role_metadata()
    df_jobs = pd.read_csv(JOB_VECTORS_PATH)
    
    skill_cols = feature_meta["skill_columns"]
    experience_values = feature_meta["experience_values"]
    education_values = feature_meta["education_values"]
    domain_values = feature_meta["domain_values"]
    status_values = feature_meta["status_values"]
    jobtype_values = feature_meta["jobtype_values"]
    
    print(f"  Loaded {len(skill_cols)} skill columns")
    print(f"  Loaded {len(role_meta)} role definitions")
    print(f"  Loaded {len(df_jobs)} jobs")
    
    # Get unique roles in job data
    roles_in_data = df_jobs["role_id"].unique()
    print(f"  Unique roles in data: {len(roles_in_data)}")
    
    # Build profiles
    print("\n[2] Building profiles...")
    profiles = []
    
    for role_id in roles_in_data:
        role_jobs = df_jobs[df_jobs["role_id"] == role_id]
        n_jobs = len(role_jobs)
        
        # Calculate skill vector (mean of binary skill cols)
        # Get existing skill columns that exist in the dataframe
        existing_skill_cols = [c for c in skill_cols if c in df_jobs.columns]
        skill_vector = role_jobs[existing_skill_cols].mean().values
        
        # Pad to full skill size if needed
        if len(skill_vector) < len(skill_cols):
            padded = np.zeros(len(skill_cols))
            padded[:len(skill_vector)] = skill_vector
            skill_vector = padded
        
        # Get categorical features for this role
        cat_features = estimate_role_categorical_features(role_id, role_meta, feature_meta)
        
        # Encode categorical features
        exp_vector = encode_categorical(cat_features["experience"], experience_values)
        edu_vector = encode_categorical(cat_features["education"], education_values)
        domain_vector = encode_categorical(cat_features["domain"], domain_values)
        status_vector = encode_categorical(cat_features["status"], status_values)
        jobtype_vector = encode_categorical(cat_features["jobtype"], jobtype_values)
        
        # Combine all features
        full_vector = np.concatenate([
            skill_vector,
            exp_vector,
            edu_vector,
            domain_vector,
            status_vector,
            jobtype_vector
        ])
        
        # Store
        profile = {"role_id": role_id}
        
        # Add skill columns
        for i, col in enumerate(skill_cols):
            profile[col] = skill_vector[i] if i < len(skill_vector) else 0.0
        
        # Add categorical one-hot columns
        for i, val in enumerate(experience_values):
            profile[f"exp_{val}"] = exp_vector[i]
        for i, val in enumerate(education_values):
            profile[f"edu_{val}"] = edu_vector[i]
        for i, val in enumerate(domain_values):
            profile[f"domain_{val}"] = domain_vector[i]
        for i, val in enumerate(status_values):
            profile[f"status_{val}"] = status_vector[i]
        for i, val in enumerate(jobtype_values):
            profile[f"jobtype_{val}"] = jobtype_vector[i]
        
        profiles.append(profile)
    
    # Create DataFrame
    df_profiles = pd.DataFrame(profiles)
    df_profiles = df_profiles.set_index("role_id")
    
    print(f"\n  Built profiles for {len(df_profiles)} roles")
    print(f"  Profile dimensions: {len(df_profiles.columns)}")
    
    # Save
    print(f"\n[3] Saving to {OUTPUT_PATH}")
    df_profiles.to_csv(OUTPUT_PATH)
    
    print("\n=== Complete ===")
    print(f"Roles with enhanced profiles: {len(df_profiles)}")
    print(f"Output: {OUTPUT_PATH}")
    
    return df_profiles


if __name__ == "__main__":
    build_enhanced_profiles()
