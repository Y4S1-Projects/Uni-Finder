"""
Career recommendation service using cosine similarity + weighted scoring.

The recommendation flow:
  1. Get raw cosine similarity scores (skill match)
  2. Apply weighted scoring considering:
     - skill_match_score (from cosine similarity)
     - domain_preference_score (explicit user preference)
     - experience_fit_score (seniority alignment)
     - career_goal_fit_score (intent alignment)
     - education_fit_score (soft signal)
  3. Rank by final_match_score
  4. Return recommendations with score breakdowns

Supports two modes:
  1. Enhanced (330-dim) — uses skill + categorical features when
     enhanced profiles and user vectorizer are available.
  2. Legacy (300-dim) — uses only skill vectors as fallback.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from data_loader import DataStore
from .career_service import detect_skill_gap, get_next_role, get_domain_for_role
from .scoring import (
    compute_final_score,
    generate_ranking_explanation,
    normalize_domain,
    ScoreBreakdown,
)


# ── helpers ──────────────────────────────────────────────────────────

def _build_legacy_user_vector(user_skill_ids: set, skill_columns: pd.Index) -> np.ndarray:
    """Build a 300-dim binary skill vector (legacy fallback)."""
    vector = np.zeros(len(skill_columns))
    skill_index = {skill: idx for idx, skill in enumerate(skill_columns)}
    for skill_id in user_skill_ids:
        if skill_id in skill_index:
            vector[skill_index[skill_id]] = 1.0
    return vector.reshape(1, -1)


def _enhanced_available() -> bool:
    """Check whether all enhanced-mode assets are ready."""
    return (
        DataStore.role_enhanced_profiles is not None
        and not DataStore.role_enhanced_profiles.empty
        and DataStore.user_vectorizer is not None
    )


def _compute_readiness(user_skills_upper: set, role_id: str) -> float | None:
    """Return readiness score (0-1) from skill-gap analysis, or None."""
    try:
        gap = detect_skill_gap(user_skills_upper, role_id, importance_threshold=0.02)
        return gap.get("readiness_score")
    except Exception:
        return None


# ── main entry point ─────────────────────────────────────────────────

def recommend_careers_for_user(
    user_skill_ids: list,
    top_n: int = 5,
    *,
    experience_level: str | None = None,
    current_status: str | None = None,
    education_level: str | None = None,
    career_goal: str | None = None,
    preferred_domain: str | None = None,
    preferred_job_type: str | None = None,
) -> dict:
    """
    Recommend best-fit career roles using weighted multi-factor scoring.

    The ranking considers:
    - skill_match_score (40%/55%): From cosine similarity
    - domain_preference_score (30%/10%): User's explicit domain preference
    - experience_fit_score (15%/20%): Seniority alignment
    - career_goal_fit_score (10%/10%): Intent alignment
    - education_fit_score (5%/5%): Soft education signal
    
    When enhanced data is available the function uses a 330-dim vector
    for skill similarity. Otherwise it falls back to 300-dim skill-only mode.
    """
    if not user_skill_ids:
        raise ValueError("No skills provided")

    user_skills_upper = set(s.strip().upper() for s in user_skill_ids if s)

    # ── choose enhanced vs legacy path for skill similarity ──
    use_enhanced = _enhanced_available() and any([
        experience_level, current_status, education_level,
        preferred_domain, preferred_job_type,
    ])

    if use_enhanced:
        similarity_scores, role_ids = _enhanced_recommend(
            user_skill_ids=list(user_skills_upper),
            experience_level=experience_level,
            current_status=current_status,
            education_level=education_level,
            preferred_domain=preferred_domain,
            preferred_job_type=preferred_job_type,
        )
        mode = "enhanced"
    else:
        if DataStore.role_skill_matrix is None or DataStore.role_skill_matrix.empty:
            raise ValueError("Role skill matrix not loaded")
        similarity_scores, role_ids = _legacy_recommend(user_skills_upper)
        mode = "legacy"

    # ── compute weighted scores for ALL roles ──
    scored_roles = []
    for i, role_id in enumerate(role_ids):
        skill_score = float(similarity_scores[i])
        role_title = DataStore.role_id_to_title.get(role_id, role_id)
        domain = get_domain_for_role(role_id)
        
        # Get readiness from skill gap analysis
        readiness = 0.5
        skill_gap = None
        try:
            skill_gap = detect_skill_gap(user_skills_upper, role_id, importance_threshold=0.02)
            if skill_gap and "readiness_score" in skill_gap:
                readiness = skill_gap["readiness_score"]
        except Exception:
            pass
        
        # Compute weighted final score using scoring engine
        score_breakdown = compute_final_score(
            skill_match_score=skill_score,
            role_id=role_id,
            role_domain=domain,
            preferred_domain=preferred_domain,
            experience_level=experience_level,
            career_goal=career_goal,
            education_level=education_level,
            readiness_score=readiness,
        )
        
        scored_roles.append({
            "role_id": role_id,
            "role_title": role_title,
            "domain": domain,
            "skill_gap": skill_gap,
            "score_breakdown": score_breakdown,
        })
    
    # ── sort by FINAL score (not raw similarity) & pick top N ──
    scored_roles.sort(key=lambda x: x["score_breakdown"].final_match_score, reverse=True)
    top_roles = scored_roles[:top_n]
    
    # ── build final results with is_best_match flag ──
    results = []
    for rank, role_data in enumerate(top_roles):
        role_id = role_data["role_id"]
        role_title = role_data["role_title"]
        domain = role_data["domain"]
        skill_gap = role_data["skill_gap"]
        breakdown = role_data["score_breakdown"]
        is_best = (rank == 0)
        
        # Career ladder info
        next_role = None
        next_role_title = None
        if domain:
            try:
                next_role = get_next_role(domain, role_id)
                if next_role:
                    next_role_title = DataStore.role_id_to_title.get(next_role, next_role)
            except ValueError:
                pass
        
        # Generate ranking explanation
        explanations = generate_ranking_explanation(
            score_breakdown=breakdown,
            role_title=role_title,
            role_domain=domain,
            preferred_domain=preferred_domain,
            is_best_match=is_best,
        )
        
        results.append({
            "role_id": role_id,
            "role_title": role_title,
            "domain": domain,
            # Scores - use final_match_score for "match_score" display
            "match_score": round(breakdown.final_match_score, 3),
            "skill_match_score": round(breakdown.skill_match_score, 3),
            "readiness_score": round(breakdown.readiness_score, 3),
            # Score breakdown for transparency
            "score_breakdown": breakdown.to_dict(),
            # Flags
            "is_best_match": is_best,
            # Career progression
            "next_role": next_role,
            "next_role_title": next_role_title,
            # Skill gap details
            "skill_gap": skill_gap,
            # Explanations
            "explanations": explanations,
        })

    return {
        "recommendations": results,
        "skills_analyzed": list(user_skills_upper),
        "total_roles_compared": len(role_ids),
        "mode": mode,
        "domain_filter_applied": bool(preferred_domain),
        "preferred_domain": preferred_domain,
        # Include user profile in response for frontend display
        "profile_used": {
            "experience_level": experience_level,
            "current_status": current_status,
            "education_level": education_level,
            "career_goal": career_goal,
            "preferred_domain": preferred_domain,
        },
    }


# ── private strategy implementations ────────────────────────────────

def _enhanced_recommend(
    user_skill_ids: list,
    experience_level: str | None,
    current_status: str | None,
    education_level: str | None,
    preferred_domain: str | None,
    preferred_job_type: str | None,
) -> tuple[np.ndarray, list]:
    """Enhanced 330-dim cosine similarity."""
    user_profile = {
        "user_skill_ids": user_skill_ids,
        "experience_level": experience_level or "",
        "current_status": current_status or "",
        "education_level": education_level or "",
        "preferred_domain": preferred_domain or "",
        "preferred_job_type": preferred_job_type or "full_time",
    }
    user_vector = DataStore.user_vectorizer.create_user_vector(user_profile)
    user_vector = user_vector.reshape(1, -1)

    role_matrix = DataStore.role_enhanced_profiles.values
    role_ids = list(DataStore.role_enhanced_profiles.index)

    scores = cosine_similarity(user_vector, role_matrix)[0]
    return scores, role_ids


def _legacy_recommend(user_skills_upper: set) -> tuple[np.ndarray, list]:
    """Legacy 300-dim skill-only cosine similarity."""
    user_vector = _build_legacy_user_vector(
        user_skills_upper, DataStore.role_skill_matrix.columns
    )
    role_vectors = DataStore.role_skill_matrix.values
    role_ids = list(DataStore.role_skill_matrix.index)
    scores = cosine_similarity(user_vector, role_vectors)[0]
    return scores, role_ids
