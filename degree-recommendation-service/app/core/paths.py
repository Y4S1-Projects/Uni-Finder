# app/core/paths.py
from pathlib import Path
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / settings.DATA_DIR

# Updated paths for new dataset structure
UNIVERSITY_COURSES_PATH = DATA_DIR / "University_Courses_Dataset.csv"
CUTOFF_DATASET_PATH = DATA_DIR / "Cutoff_Dataset_Mapped.csv"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
METADATA_PATH = DATA_DIR / "metadata.json"

# Legacy compatibility
PROGRAM_CATALOG_PATH = UNIVERSITY_COURSES_PATH
