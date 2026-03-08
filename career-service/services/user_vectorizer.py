"""
User Vectorizer - Task 3
========================
Converts user form inputs into the same vector space as enhanced job/role profiles.
Creates a 330-dimensional vector: 300 skill dims + 30 categorical dims.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional


class UserVectorizer:
    """
    Converts user profile form data into a vector matching the enhanced
    role/job feature vectors for cosine similarity comparison.
    """

    def __init__(self, feature_meta_path: Path, skills_csv_path: Path):
        """
        Initialize with feature metadata and skills lookup.

        Args:
            feature_meta_path: Path to enhanced_feature_columns.json
            skills_csv_path:   Path to skills.csv
        """
        # Load feature metadata
        with open(feature_meta_path, "r") as f:
            self.meta = json.load(f)

        self.skill_columns = self.meta["skill_columns"]          # 300 skill_ cols
        self.onehot_columns = self.meta["onehot_columns"]        # 30 one-hot cols
        self.all_feature_columns = self.meta["all_feature_columns"]  # 330 total
        self.feature_groups = self.meta["feature_groups"]

        # Value lists for each categorical feature
        self.experience_values = self.meta["experience_values"]
        self.education_values = self.meta["education_values"]
        self.domain_values = self.meta["domain_values"]
        self.status_values = self.meta["status_values"]
        self.jobtype_values = self.meta["jobtype_values"]

        # Build skill name/id lookup
        df_skills = pd.read_csv(skills_csv_path)
        self.skill_id_to_name = dict(zip(df_skills["skill_id"], df_skills["name"]))
        self.skill_name_to_id = {
            name.strip().lower(): sid
            for sid, name in self.skill_id_to_name.items()
        }

        # Build skill_id -> column index mapping
        self.skill_col_index = {
            col: idx for idx, col in enumerate(self.skill_columns)
        }
        # Also map SK001 -> skill_sk001
        self.skill_id_to_col = {}
        for col in self.skill_columns:
            # col = "skill_sk001" -> sid = "SK001"
            suffix = col.replace("skill_", "").upper()
            self.skill_id_to_col[suffix] = col

        print(f"[UserVectorizer] Initialized: {len(self.all_feature_columns)} dims "
              f"({len(self.skill_columns)} skills + {len(self.onehot_columns)} categorical)")

    def encode_skills(self, skill_ids: List[str]) -> np.ndarray:
        """
        Convert skill IDs to 300-dim binary vector.

        Args:
            skill_ids: List of skill IDs (e.g. ["SK001", "SK004"])

        Returns:
            numpy array of length 300
        """
        vector = np.zeros(len(self.skill_columns))
        for sid in skill_ids:
            sid_upper = sid.strip().upper()
            col = self.skill_id_to_col.get(sid_upper)
            if col and col in self.skill_col_index:
                vector[self.skill_col_index[col]] = 1.0
        return vector

    def encode_categorical(self, value: Optional[str], value_list: list, prefix: str) -> np.ndarray:
        """
        One-hot encode a single categorical value.

        Args:
            value:      The value to encode (e.g. "bachelors")
            value_list: All possible values (e.g. ["al", "diploma", ...])
            prefix:     Column prefix (e.g. "edu")

        Returns:
            numpy array of length len(value_list)
        """
        vector = np.zeros(len(value_list))
        if value and value in value_list:
            idx = value_list.index(value)
            vector[idx] = 1.0
        return vector

    def create_user_vector(self, user_profile: dict) -> np.ndarray:
        """
        Convert user form data to vector matching enhanced feature vectors.

        Args:
            user_profile: Dictionary with keys:
                - user_skill_ids: List[str]  (e.g. ["SK001", "SK004"])
                - experience_level: str      (e.g. "1-3")
                - current_status: str        (e.g. "graduate")
                - education_level: str       (e.g. "bachelors")
                - preferred_domain: str      (e.g. "SOFTWARE_ENGINEERING")
                - career_goal: str           (e.g. "switch_career")
                - preferred_job_type: str    (e.g. "full_time")

        Returns:
            numpy array of shape (330,)
        """
        # 1. Skill vector (300 dims)
        skill_ids = user_profile.get("user_skill_ids", [])
        skill_vector = self.encode_skills(skill_ids)

        # 2. Experience level (6 dims)
        exp = user_profile.get("experience_level", "")
        exp_vector = self.encode_categorical(exp, self.experience_values, "exp")

        # 3. Education level (7 dims)
        edu = user_profile.get("education_level", "")
        edu_vector = self.encode_categorical(edu, self.education_values, "edu")

        # 4. Domain (7 dims) - map frontend values to internal domain names
        domain_raw = (user_profile.get("preferred_domain") or "").strip()
        domain = self._map_frontend_domain(domain_raw)
        domain_vector = self.encode_categorical(domain, self.domain_values, "domain")

        # 5. Current status (4 dims) - map frontend values
        status_raw = (user_profile.get("current_status") or "").strip()
        status = self._map_frontend_status(status_raw)
        status_vector = self.encode_categorical(status, self.status_values, "status")

        # 6. Job type (6 dims) - default to full_time if not specified
        jobtype = user_profile.get("preferred_job_type", "full_time") or "full_time"
        jobtype_vector = self.encode_categorical(jobtype, self.jobtype_values, "jobtype")

        # Concatenate all vectors
        user_vector = np.concatenate([
            skill_vector,
            exp_vector,
            edu_vector,
            domain_vector,
            status_vector,
            jobtype_vector,
        ])

        return user_vector

    def _map_frontend_domain(self, domain_raw: str) -> str:
        """Map frontend domain values to internal domain names."""
        mapping = {
            "software_engineering": "SOFTWARE_ENGINEERING",
            "frontend_engineering": "FRONTEND_ENGINEERING",
            "backend_engineering": "BACKEND_ENGINEERING",
            "fullstack_engineering": "FULLSTACK_ENGINEERING",
            "data_engineering": "DATA_ENGINEERING",
            "data_science": "DATA_SCIENCE",
            "data": "DATA",
            "ai_ml": "AI_ML",
            "devops": "DEVOPS",
            "cloud_engineering": "CLOUD_ENGINEERING",
            "security": "SECURITY",
            "qa": "QA",
            "mobile_engineering": "MOBILE",
            "mobile": "MOBILE",
            "ui_ux": "UI_UX",
            "product_management": "PRODUCT_MANAGEMENT",
            "business_analysis": "BUSINESS_ANALYSIS",
            "project_management": "PROJECT_MANAGEMENT",
            "technical_writing": "TECHNICAL_WRITING",
            "blockchain_web3": "BLOCKCHAIN_WEB3",
            "game_development": "GAME_DEVELOPMENT",
            "embedded_systems": "EMBEDDED_SYSTEMS",
        }
        return mapping.get(domain_raw.lower(), "") if domain_raw else ""

    def _map_frontend_status(self, status_raw: str) -> str:
        """Map frontend status values to internal status names."""
        mapping = {
            "student": "student",
            "graduate": "graduate",
            "working": "working",
        }
        return mapping.get(status_raw.lower(), "") if status_raw else ""
