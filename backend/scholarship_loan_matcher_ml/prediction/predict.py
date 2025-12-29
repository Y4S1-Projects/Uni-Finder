"""Prediction runner using cleaned datasets + eligibility-aware ranking."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

try:
    from scholarship_loan_matcher_ml.matcher.match_engine import match_profile
except ImportError:
    # Fallback if executed without package context
    import importlib.util

    matcher_path = Path(__file__).resolve().parents[1] / "matcher" / "match_engine.py"
    spec = importlib.util.spec_from_file_location("match_engine", matcher_path)
    matcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(matcher)  # type: ignore
    match_profile = matcher.match_profile


def run_prediction(profile: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
    """
    Run the matcher against the latest cleaned datasets.
    Returns scholarships, loans, combined list, and explanations.
    """
    return match_profile(profile, top_n=top_n, candidate_pool=max(top_n * 3, 25))


def _json_safe(obj):
    if obj is None:
        return None
    if isinstance(obj, float):
        if obj != obj:  # NaN check
            return None
        if obj in (float("inf"), float("-inf")):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Predict top scholarships/loans using cleaned datasets.")
    parser.add_argument("--profile", required=True, help="JSON string of student profile.")
    parser.add_argument("--top_n", type=int, default=5, help="Number of matches to return.")
    args = parser.parse_args()

    profile = json.loads(args.profile)
    results = run_prediction(profile, top_n=args.top_n)

    # Maintain backward compatibility: include combined list as "results"
    payload = {
        "results": results.get("combined", []),
        "scholarships": results.get("scholarships", []),
        "loans": results.get("loans", []),
        "explanations": results.get("explanations", {}),
    }

    print(json.dumps(_json_safe(payload), ensure_ascii=False))


if __name__ == "__main__":
    _cli()
