"""Data loading utilities for startup"""
import pandas as pd
import json
import joblib
from config import (
    ROLE_PROFILE_CSV,
    CAREER_LADDERS_JSON,
    ROLE_CLASSIFIER_PKL,
    JOB_SKILL_VECTORS_CSV,
    SKILLS_CSV,
    ROLE_ENHANCED_PROFILES_CSV,
    ENHANCED_FEATURE_COLUMNS_JSON,
    JOBS_ENHANCED_FEATURES_CSV,
)


class DataStore:
    """Central data store for all loaded data"""
    role_profiles_df: pd.DataFrame = None
    role_skill_matrix: pd.DataFrame = None
    career_ladders: dict = {}
    role_classifier = None
    skill_columns: list = []
    role_id_to_title: dict = {}
    skill_id_to_name: dict = {}
    # Enhanced features (multi-feature recommendation)
    role_enhanced_profiles: pd.DataFrame = None
    enhanced_feature_meta: dict = {}
    jobs_enhanced_features: pd.DataFrame = None
    user_vectorizer = None


def load_role_profiles():
    """Load role profiles and build skill matrix"""
    try:
        DataStore.role_profiles_df = pd.read_csv(ROLE_PROFILE_CSV)
        print(f"[startup] Loaded role_profiles_df: {len(DataStore.role_profiles_df)} rows")
        
        # Build role-skill matrix for cosine similarity recommender
        DataStore.role_skill_matrix = DataStore.role_profiles_df.pivot_table(
            index="role_id",
            columns="skill_id",
            values="importance",
            fill_value=0
        )
        print(f"[startup] Built role_skill_matrix: {DataStore.role_skill_matrix.shape}")
    except Exception as e:
        print(f"[startup] Failed to load role_profiles: {e}")
        DataStore.role_profiles_df = pd.DataFrame(columns=["role_id", "skill_id", "frequency", "importance"])
        DataStore.role_skill_matrix = pd.DataFrame()


def load_career_ladders():
    """Load career ladder definitions"""
    try:
        with open(CAREER_LADDERS_JSON, "r") as f:
            DataStore.career_ladders = json.load(f)
        print(f"[startup] Loaded CAREER_LADDERS: {list(DataStore.career_ladders.keys())}")
    except Exception as e:
        print(f"[startup] Failed to load career ladders: {e}")
        DataStore.career_ladders = {}


def load_role_classifier():
    """Load the decision tree role classifier model"""
    try:
        DataStore.role_classifier = joblib.load(ROLE_CLASSIFIER_PKL)
        print(f"[startup] Loaded role_classifier: {type(DataStore.role_classifier)}")
    except Exception as e:
        print(f"[startup] Failed to load role classifier: {e}")
        DataStore.role_classifier = None


def load_skill_columns():
    """Load skill columns from training data"""
    try:
        df = pd.read_csv(JOB_SKILL_VECTORS_CSV, nrows=1)
        DataStore.skill_columns = [c for c in df.columns if c.startswith("skill_")]
        print(f"[startup] Loaded {len(DataStore.skill_columns)} skill columns")
    except Exception as e:
        print(f"[startup] Failed to load skill columns: {e}")
        DataStore.skill_columns = []


def load_role_titles():
    """Load role ID to title mapping"""
    try:
        df_roles = pd.read_csv(JOB_SKILL_VECTORS_CSV, usecols=["role_id", "role_title"])
        DataStore.role_id_to_title = dict(zip(df_roles["role_id"], df_roles["role_title"]))
        print(f"[startup] Loaded {len(DataStore.role_id_to_title)} role titles")
    except Exception as e:
        print(f"[startup] Failed to load role titles: {e}")
        DataStore.role_id_to_title = {}


def load_skill_names():
    """Load skill ID to name mapping"""
    try:
        df_skills = pd.read_csv(SKILLS_CSV)
        DataStore.skill_id_to_name = dict(zip(df_skills["skill_id"], df_skills["name"]))
        print(f"[startup] Loaded {len(DataStore.skill_id_to_name)} skill names")
    except Exception as e:
        print(f"[startup] Failed to load skill names: {e}")
        DataStore.skill_id_to_name = {}


def load_enhanced_profiles():
    """Load enhanced role profiles and feature metadata"""
    try:
        if ROLE_ENHANCED_PROFILES_CSV.exists():
            DataStore.role_enhanced_profiles = pd.read_csv(
                ROLE_ENHANCED_PROFILES_CSV, index_col=0
            )
            print(f"[startup] Loaded role_enhanced_profiles: {DataStore.role_enhanced_profiles.shape}")
        else:
            print(f"[startup] Enhanced profiles not found: {ROLE_ENHANCED_PROFILES_CSV}")
            DataStore.role_enhanced_profiles = None
    except Exception as e:
        print(f"[startup] Failed to load enhanced profiles: {e}")
        DataStore.role_enhanced_profiles = None


def load_enhanced_feature_meta():
    """Load enhanced feature column metadata"""
    import json
    try:
        if ENHANCED_FEATURE_COLUMNS_JSON.exists():
            with open(ENHANCED_FEATURE_COLUMNS_JSON, "r") as f:
                DataStore.enhanced_feature_meta = json.load(f)
            print(f"[startup] Loaded enhanced feature metadata: "
                  f"{len(DataStore.enhanced_feature_meta.get('all_feature_columns', []))} features")
        else:
            print(f"[startup] Enhanced feature metadata not found: {ENHANCED_FEATURE_COLUMNS_JSON}")
    except Exception as e:
        print(f"[startup] Failed to load enhanced feature metadata: {e}")


def load_jobs_enhanced_features():
    """Load enhanced job features for display purposes"""
    try:
        if JOBS_ENHANCED_FEATURES_CSV.exists():
            DataStore.jobs_enhanced_features = pd.read_csv(JOBS_ENHANCED_FEATURES_CSV)
            print(f"[startup] Loaded jobs_enhanced_features: {len(DataStore.jobs_enhanced_features)} rows")
        else:
            print(f"[startup] Enhanced features not found: {JOBS_ENHANCED_FEATURES_CSV}")
    except Exception as e:
        print(f"[startup] Failed to load enhanced features: {e}")


def init_user_vectorizer():
    """Initialize the user vectorizer"""
    from config import SKILLS_CSV
    try:
        if ENHANCED_FEATURE_COLUMNS_JSON.exists() and SKILLS_CSV.exists():
            from services.user_vectorizer import UserVectorizer
            DataStore.user_vectorizer = UserVectorizer(
                ENHANCED_FEATURE_COLUMNS_JSON, SKILLS_CSV
            )
        else:
            print("[startup] Cannot init user vectorizer: missing feature metadata or skills CSV")
    except Exception as e:
        print(f"[startup] Failed to init user vectorizer: {e}")


def load_all_data():
    """Load all data at startup"""
    from config import BASE_DIR, ML_DIR, ROLE_CLASSIFIER_PKL
    
    print(f"[startup] BASE_DIR: {BASE_DIR}")
    print(f"[startup] ML_DIR: {ML_DIR}")
    print(f"[startup] ROLE_CLASSIFIER_PKL: {ROLE_CLASSIFIER_PKL}")
    print(f"[startup] Model file exists: {ROLE_CLASSIFIER_PKL.exists()}")
    
    load_role_profiles()
    load_career_ladders()
    load_role_classifier()
    load_skill_columns()
    load_role_titles()
    load_skill_names()
    # Enhanced features
    load_enhanced_profiles()
    load_enhanced_feature_meta()
    load_jobs_enhanced_features()
    init_user_vectorizer()
