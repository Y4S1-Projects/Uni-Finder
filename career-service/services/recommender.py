"""
Career recommendation service (Phase B rewrite)
=================================================
Uses the new scoring_engine for transparent multi-component scoring.

Flow:
  1. Build user skill vector → cosine similarity against every role profile
  2. For each role: compute all 9 score components via scoring_engine
  3. Apply penalties, boosts, entry-level adjustments
  4. Rank by final_match_score
  5. Select Best Match from top of final ranking
  6. Return structured breakdowns for every recommendation

Supports two similarity modes:
  - Enhanced (330+ dim)  — skill + categorical features (when assets available)
  - Legacy (skill-only)  — binary skill vectors
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from data_loader import DataStore
from .career_service import detect_skill_gap, get_next_role, get_domain_for_role
from .skill_service import get_skill_name
from .scoring_engine import (
    score_role_for_user,
    select_best_match,
    generate_ranking_explanation,
    normalize_domain,
    classify_user_level,
    FullScoreBreakdown,
    _ensure_cache,
    _cache,
)


# ── helpers ──────────────────────────────────────────────────────────

def _build_legacy_user_vector(user_skill_ids: set, skill_columns: pd.Index) -> np.ndarray:
    """Build a binary skill vector for legacy mode."""
    vector = np.zeros(len(skill_columns))
    skill_index = {skill: idx for idx, skill in enumerate(skill_columns)}
    for skill_id in user_skill_ids:
        col = f"skill_{skill_id.lower()}" if not skill_id.startswith("skill_") else skill_id
        if col in skill_index:
            vector[skill_index[col]] = 1.0
        elif skill_id in skill_index:
            vector[skill_index[skill_id]] = 1.0
    return vector.reshape(1, -1)


def _enhanced_available() -> bool:
    """Check whether all enhanced-mode assets are ready."""
    return (
        DataStore.role_enhanced_profiles is not None
        and not DataStore.role_enhanced_profiles.empty
        and DataStore.user_vectorizer is not None
    )


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
    Recommend career roles using multi-component weighted scoring.

    Scoring (9 components):
        skill_match_score         — cosine similarity
        core_skill_coverage_score — % of core skills matched
        domain_preference_score   — domain alignment
        experience_fit_score      — experience-seniority fit
        current_status_fit_score  — student/graduate/working
        education_fit_score       — education level signal
        career_goal_fit_score     — first_job/switch/promote
        seniority_fit_score       — numeric level distance
        confidence_score          — mapping confidence

    Plus penalties, boosts, and entry-level adjustments.
    """
    if not user_skill_ids:
        raise ValueError("No skills provided")

    user_skills_upper = set(s.strip().upper() for s in user_skill_ids if s)

    # ── classify user ──
    is_entry, user_target = classify_user_level(
        experience_level, current_status, career_goal, len(user_skills_upper)
    )

    # ── cosine similarity baseline ──
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

        # Merge in roles only present in the legacy matrix (e.g. new synthetic roles)
        if DataStore.role_skill_matrix is not None and not DataStore.role_skill_matrix.empty:
            enhanced_set = set(role_ids)
            legacy_scores, legacy_ids = _legacy_recommend(user_skills_upper)
            for j, lid in enumerate(legacy_ids):
                if lid not in enhanced_set:
                    role_ids.append(lid)
                    similarity_scores = np.append(similarity_scores, legacy_scores[j])
            if len(role_ids) > len(enhanced_set):
                mode = "enhanced+legacy"
    else:
        if DataStore.role_skill_matrix is None or DataStore.role_skill_matrix.empty:
            raise ValueError("Role skill matrix not loaded")
        similarity_scores, role_ids = _legacy_recommend(user_skills_upper)
        mode = "legacy"

    # ── score every role through the new engine ──
    scored_roles = []
    for i, role_id in enumerate(role_ids):
        raw_sim = float(similarity_scores[i])
        role_domain = get_domain_for_role(role_id)

        breakdown = score_role_for_user(
            user_skill_ids=user_skills_upper,
            role_id=role_id,
            role_domain=role_domain,
            raw_similarity=raw_sim,
            preferred_domain=preferred_domain,
            experience_level=experience_level,
            current_status=current_status,
            education_level=education_level,
            career_goal=career_goal,
        )

        # Fetch skill gap for detailed missing/matched skill info
        skill_gap = None
        try:
            skill_gap = detect_skill_gap(
                user_skills_upper, role_id, importance_threshold=0.02
            )
        except Exception:
            pass

        scored_roles.append({
            "role_id": role_id,
            "role_title": DataStore.role_id_to_title.get(role_id, role_id),
            "domain": role_domain,
            "skill_gap": skill_gap,
            "score_breakdown": breakdown,
        })

    # ── rank by final_match_score (with tie-breaking) ──
    scored_roles.sort(
        key=lambda x: (
            x["score_breakdown"].final_match_score,
            x["score_breakdown"].core_skill_coverage_score,
            x["score_breakdown"].confidence_score,
        ),
        reverse=True,
    )

    # ── pick top N ──
    top_roles = scored_roles[:top_n]

    # ── select best match ──
    best_idx = select_best_match(top_roles)

    # ── build response ──
    results = []
    for rank, role_data in enumerate(top_roles):
        role_id = role_data["role_id"]
        role_title = role_data["role_title"]
        domain = role_data["domain"]
        skill_gap = role_data["skill_gap"]
        bd: FullScoreBreakdown = role_data["score_breakdown"]
        is_best = (rank == best_idx)

        # Seniority & ladder position (compute before get_next_role needs it)
        _ensure_cache()
        seniority = _cache.role_seniority.get(role_id, 3)
        ladder = DataStore.career_ladders.get(domain, [])
        ladder_position = (ladder.index(role_id) + 1) if role_id in ladder else None
        ladder_length = len(ladder) if ladder else None

        # Career ladder info — uses seniority for fallback placement
        next_role = None
        next_role_title = None
        if domain:
            try:
                next_role = get_next_role(domain, role_id, current_seniority=seniority)
                if next_role:
                    next_role_title = DataStore.role_id_to_title.get(next_role, next_role)
                    # Phase D: entry-level guard — don't let intern/junior jump > 2 seniority levels
                    if seniority <= 2 and next_role:
                        next_seniority = _cache.role_seniority.get(next_role, 3)
                        if next_seniority - seniority > 2:
                            # Find a closer role in the ladder
                            for lr in ladder:
                                lr_sen = _cache.role_seniority.get(lr, 3)
                                if lr_sen > seniority and lr_sen - seniority <= 2:
                                    next_role = lr
                                    next_role_title = DataStore.role_id_to_title.get(lr, lr)
                                    break
            except (ValueError, Exception):
                pass

        # Explanation — now includes why_not_more_ready, seniority_fit
        explanations = generate_ranking_explanation(
            breakdown=bd,
            role_title=role_title,
            role_domain=domain,
            preferred_domain=preferred_domain,
            is_best_match=is_best,
            rank=rank,
            experience_level=experience_level,
            current_status=current_status,
        )

        # Convert skill IDs to {id, name} for matched/missing core/supporting
        def _skill_objs(ids):
            return [{"id": s, "name": get_skill_name(s)} for s in ids]

        results.append({
            # Identity
            "role_id": role_id,
            "role_title": role_title,
            "domain": domain,
            "seniority": seniority,
            # Ladder
            "ladder_position": ladder_position,
            "ladder_length": ladder_length,
            "next_role": next_role,
            "next_role_title": next_role_title,
            # Primary scores
            "match_score": round(bd.final_match_score, 4),
            "readiness_score": round(bd.readiness_score, 4),
            "skill_match_score": round(bd.skill_match_score, 4),
            "confidence_score": round(bd.confidence_score, 4),
            # Full structured breakdown
            "score_breakdown": bd.to_dict(),
            # Skill details
            "matched_core_skills": _skill_objs(bd.matched_core_skills),
            "matched_supporting_skills": _skill_objs(bd.matched_supporting_skills),
            "missing_critical_skills": _skill_objs(bd.missing_critical_skills),
            # Flags
            "is_best_match": is_best,
            "profile_source": bd.profile_source,
            # Career progression
            # Skill gap details (legacy compat)
            "skill_gap": skill_gap,
            # Explanations
            "explanations": explanations,
        })

    return {
        "recommendations": results,
        "skills_analyzed": sorted(user_skills_upper),
        "total_roles_compared": len(role_ids),
        "mode": mode,
        "domain_filter_applied": bool(preferred_domain),
        "preferred_domain": preferred_domain,
        "is_entry_level_user": is_entry,
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
    """Enhanced cosine similarity (full vector)."""
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
    """Legacy skill-only cosine similarity."""
    user_vector = _build_legacy_user_vector(
        user_skills_upper, DataStore.role_skill_matrix.columns
    )
    role_vectors = DataStore.role_skill_matrix.values
    role_ids = list(DataStore.role_skill_matrix.index)
    scores = cosine_similarity(user_vector, role_vectors)[0]
    return scores, role_ids
