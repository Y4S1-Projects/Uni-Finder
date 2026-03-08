"""
Career recommendation service using cosine similarity.

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
    Recommend best-fit career roles.

    When enhanced data is available the function uses a 330-dim vector
    (skills + experience + education + domain + status + job-type).
    Otherwise it falls back to the original 300-dim skill-only mode.
    """
    if not user_skill_ids:
        raise ValueError("No skills provided")

    user_skills_upper = set(s.strip().upper() for s in user_skill_ids if s)

    # ── choose enhanced vs legacy path ──
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

    # ── sort & pick top N ──
    recs = pd.DataFrame({"role_id": role_ids, "match_score": similarity_scores})
    recs = recs.sort_values("match_score", ascending=False).head(top_n)

    results = []
    for _, row in recs.iterrows():
        role_id = row["role_id"]
        match_score = round(float(row["match_score"]), 3)
        role_title = DataStore.role_id_to_title.get(role_id, role_id)
        domain = get_domain_for_role(role_id)

        # Career ladder
        next_role = None
        next_role_title = None
        if domain:
            try:
                next_role = get_next_role(domain, role_id)
                if next_role:
                    next_role_title = DataStore.role_id_to_title.get(next_role, next_role)
            except ValueError:
                pass

        # Skill gap + readiness
        skill_gap = None
        try:
            skill_gap = detect_skill_gap(user_skills_upper, role_id, importance_threshold=0.02)
        except Exception:
            pass

        results.append({
            "role_id": role_id,
            "role_title": role_title,
            "match_score": match_score,
            "domain": domain,
            "next_role": next_role,
            "next_role_title": next_role_title,
            "skill_gap": skill_gap,
        })

    return {
        "recommendations": results,
        "skills_analyzed": list(user_skills_upper),
        "total_roles_compared": len(role_ids),
        "mode": mode,
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
