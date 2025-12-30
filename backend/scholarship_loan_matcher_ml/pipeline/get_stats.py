"""Get current dataset statistics without triggering an update."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "pandas not installed"}))
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed_data"
PIPELINE_DIR = BASE_DIR / "pipeline"

SCHOLARSHIPS_PATH = PROCESSED_DIR / "scholarships_clean.csv"
LOANS_PATH = PROCESSED_DIR / "loans_clean.csv"
METADATA_PATH = PIPELINE_DIR / "last_update.json"

stats = {"scholarships": 0, "loans": 0, "last_updated": None}

try:
    if SCHOLARSHIPS_PATH.exists():
        df = pd.read_csv(SCHOLARSHIPS_PATH)
        stats["scholarships"] = len(df)

    if LOANS_PATH.exists():
        df = pd.read_csv(LOANS_PATH)
        stats["loans"] = len(df)

    if METADATA_PATH.exists():
        with METADATA_PATH.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
            stats["last_updated"] = metadata.get("timestamp")

    print(json.dumps(stats))
except Exception as exc:
    err = {"error": str(exc)}
    print(json.dumps(err))
    sys.exit(1)

