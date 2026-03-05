"""Configuration and constants for the career service"""
from pathlib import Path
import os

# Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "career-ml"

# Data file paths
ROLE_PROFILE_CSV = ML_DIR / "skill_gap" / "role_skill_profiles.csv"
CAREER_LADDERS_JSON = ML_DIR / "career_path" / "career_ladders.json"
ROLE_CLASSIFIER_PKL = ML_DIR / "models" / "decision_tree_role_classifier.pkl"
JOB_SKILL_VECTORS_CSV = ML_DIR / "data" / "processed" / "job_skill_vectors.csv"
SKILLS_CSV = ML_DIR / "data" / "processed" / "skills.csv"

# Gemini API Configuration (from explainability_engine.ipynb)
GEMINI_API_KEY = "AIzaSyD8FymLTIuwptSztOBBtL0XhJYnDFcc7b0"
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# CORS settings
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
