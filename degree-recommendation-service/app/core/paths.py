# app/core/paths.py
from pathlib import Path
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / settings.DATA_DIR

PROGRAM_CATALOG_PATH = DATA_DIR / "program_catalog.csv"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
METADATA_PATH = DATA_DIR / "metadata.json"
