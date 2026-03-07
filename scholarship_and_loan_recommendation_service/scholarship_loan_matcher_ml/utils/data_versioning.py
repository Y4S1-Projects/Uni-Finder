"""
Lightweight data versioning helpers for the automation pipeline.

Provides a placeholder interface for generating version IDs, storing metadata,
and retrieving the most recent successful refresh.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict


def generate_version_id(prefix: str = "run") -> str:
    """Create a timestamped version identifier."""
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{timestamp}"


def write_metadata(version_dir: Path, metadata: Dict) -> Path:
    """
    Persist metadata for the processed dataset/model artifacts.

    For now this simply writes a JSON stub once the automation pipeline fills
    in the real fields (record counts, hashes, etc.).
    """
    version_dir.mkdir(parents=True, exist_ok=True)
    target = version_dir / "metadata.json"
    target.write_text("{}\n")
    return target


def resolve_latest_version(base_dir: Path) -> Path | None:
    """Return the newest version directory, if any exist."""
    if not base_dir.exists():
        return None
    candidates = [path for path in base_dir.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return sorted(candidates)[-1]


