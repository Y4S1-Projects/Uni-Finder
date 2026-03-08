"""Get current dataset statistics without triggering an update."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore[assignment]

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed_data"
PIPELINE_DIR = BASE_DIR / "pipeline"

SCHOLARSHIPS_PATH = PROCESSED_DIR / "scholarships_clean.csv"
LOANS_PATH = PROCESSED_DIR / "loans_clean.csv"
METADATA_PATH = PIPELINE_DIR / "last_update.json"


def get_dataset_stats() -> Dict[str, Any]:
    """Return current dataset stats (scholarships count, loans count, last_updated) for API use."""
    stats: Dict[str, Any] = {"scholarships": 0, "loans": 0, "last_updated": None}
    if pd is None:
        return stats
    try:
        if SCHOLARSHIPS_PATH.exists():
            df = pd.read_csv(SCHOLARSHIPS_PATH)
            stats["scholarships"] = int(len(df))
        if LOANS_PATH.exists():
            df = pd.read_csv(LOANS_PATH)
            stats["loans"] = int(len(df))
        if METADATA_PATH.exists():
            with METADATA_PATH.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
                stats["last_updated"] = metadata.get("timestamp")
    except Exception:
        pass
    return stats


def main() -> None:
    if pd is None:
        print(json.dumps({"error": "pandas not installed"}))
        sys.exit(1)
    try:
        stats = get_dataset_stats()
        print(json.dumps(stats))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()

