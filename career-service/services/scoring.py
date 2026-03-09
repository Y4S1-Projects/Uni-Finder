"""
Career Recommendation Scoring — Compatibility Shim
====================================================
This module re-exports from scoring_engine.py for backward compatibility.
All scoring logic now lives in scoring_engine.py (Phase B).
"""

# Re-export everything from the new engine
from .scoring_engine import (
    normalize_domain,
    compute_final_score,
    generate_ranking_explanation,
    FullScoreBreakdown as ScoreBreakdown,
    FullScoreBreakdown,
    compute_domain_preference_score,
    compute_experience_fit_score,
    compute_career_goal_fit_score,
    compute_education_fit_score,
    RELATED_DOMAINS,
    DOMAIN_NORMALIZER,
    WEIGHTS_WITH_DOMAIN as DEFAULT_WEIGHTS,
    WEIGHTS_NO_DOMAIN as NO_PREFERENCE_WEIGHTS,
)

__all__ = [
    "normalize_domain",
    "compute_final_score",
    "generate_ranking_explanation",
    "ScoreBreakdown",
    "FullScoreBreakdown",
    "compute_domain_preference_score",
    "compute_experience_fit_score",
    "compute_career_goal_fit_score",
    "compute_education_fit_score",
    "RELATED_DOMAINS",
    "DOMAIN_NORMALIZER",
    "DEFAULT_WEIGHTS",
    "NO_PREFERENCE_WEIGHTS",
]
