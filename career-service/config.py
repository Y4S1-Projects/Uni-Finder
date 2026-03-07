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
# NOTE: Do NOT hard-code API keys here. Configure them via environment variables
# or a local .env file that is NOT committed to Git.

# Optional: load environment variables from a local .env file if present
try:
	from dotenv import load_dotenv

	# Load .env from the career-service directory (one level above this file)
	env_path = BASE_DIR / "career-service" / ".env"
	if env_path.exists():
		load_dotenv(env_path)
		print(f"[config] Loaded environment from {env_path}")
except ImportError:
	# python-dotenv not installed; environment must be set by the OS/shell
	pass

# Prefer GEMINI_API_KEY, but also support GOOGLE_API_KEY for compatibility with google-genai.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if GEMINI_API_KEY:
	# Ensure both env vars are set so google-genai can pick them up
	os.environ.setdefault("GEMINI_API_KEY", GEMINI_API_KEY)
	os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)
else:
	print(
		"[config] Warning: GEMINI_API_KEY/GOOGLE_API_KEY not set; "
		"Gemini explanations will use fallback templates only."
	)

# CORS settings
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
