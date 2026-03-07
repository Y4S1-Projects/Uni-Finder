"""Utilities for mapping raw UGC stream-rule strings to standard Sri Lankan A/L stream buckets."""

from __future__ import annotations

import re
from typing import List


STANDARD_STREAM_ORDER = [
    "Physical Science",
    "Biological Science",
    "Commerce",
    "Arts",
    "Engineering Technology",
    "Biosystems Technology",
]


def map_to_standard_streams(raw_stream_string: str) -> List[str]:
    """
    Map raw UGC stream requirement text to standard A/L stream buckets.

    Returns up to 6 normalized buckets:
    - Physical Science
    - Biological Science
    - Commerce
    - Arts
    - Engineering Technology
    - Biosystems Technology
    """
    raw = str(raw_stream_string or "").strip().lower()
    if not raw:
        return []

    normalized = raw.replace(";", " ").replace(",", " ").replace("-", " ")
    normalized = normalized.replace("(", " ").replace(")", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    words = set(normalized.split())

    # Global wildcard rules: open to all streams.
    wildcard_markers = [
        "multi-stream any",
        "any all streams eligible",
        "multi stream any",
    ]
    if any(marker in normalized for marker in wildcard_markers):
        return STANDARD_STREAM_ORDER.copy()
    if normalized == "any" or ("multi-stream" in raw and "any" in words):
        return STANDARD_STREAM_ORDER.copy()

    streams = set()

    # Base 4 streams.
    if (
        "physical science" in normalized
        or "phys sci" in normalized
        or "mathematics" in normalized
        or "combined math" in normalized
        or "physical" in words
    ):
        streams.add("Physical Science")

    if (
        "biological science" in normalized
        or "bio sci" in normalized
        or "biological" in words
    ):
        streams.add("Biological Science")

    if "commerce" in words or "management" in words:
        streams.add("Commerce")

    if "arts" in words or "art" in words:
        streams.add("Arts")

    # Technology sub-streams.
    if "engineering technology" in normalized or "et" in words:
        streams.add("Engineering Technology")

    if "biosystems technology" in normalized or "biosystems" in words or "bst" in words:
        streams.add("Biosystems Technology")

    # Generic tech stream labels imply both ET and BST.
    if "technology stream" in normalized or "ict" in words:
        if (
            "Engineering Technology" not in streams
            and "Biosystems Technology" not in streams
        ):
            streams.add("Engineering Technology")
            streams.add("Biosystems Technology")

    # Additional wildcard-like patterns.
    if not streams and "multi-stream" in raw:
        return STANDARD_STREAM_ORDER.copy()

    return [stream for stream in STANDARD_STREAM_ORDER if stream in streams]


def standard_stream_sort_key(stream_name: str) -> int:
    """Sort helper for stable stream display order."""
    try:
        return STANDARD_STREAM_ORDER.index(stream_name)
    except ValueError:
        return len(STANDARD_STREAM_ORDER)
