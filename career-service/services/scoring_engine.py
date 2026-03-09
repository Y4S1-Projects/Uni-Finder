"""
Career Recommendation Scoring Engine (Phase B)
================================================
Transparent, multi-component scoring for career recommendations.

Score Components (9 total):
  1. skill_match_score         — cosine similarity of user skills vs role profile
  2. core_skill_coverage_score — % of role's core/defining skills the user has
  3. domain_preference_score   — match between preferred domain and role domain
  4. experience_fit_score      — alignment of experience level with role seniority
  5. current_status_fit_score  — student / graduate / working alignment
  6. education_fit_score       — education level support signal
  7. career_goal_fit_score     — first_job / switch_career / get_promoted alignment
  8. seniority_fit_score       — numeric seniority level distance (1=intern → 6=lead)
  9. confidence_score          — confidence in the mapping quality (0.5–1.0)

Scoring Formula:
    base = Σ(weight_i × component_i)   for i in 1..8
    final_match_score = clamp(base × confidence + penalties + boosts, 0, 1)

Readiness Formula (separate from match):
    readiness = 0.50 × core_skill_coverage
              + 0.25 × supporting_skill_coverage
              + 0.15 × seniority_alignment_factor
              + 0.10 × education_factor

Penalties:
    - weak core coverage (<20%)                  → −0.15
    - soft-skill-dominated (>60% matched are soft) → −0.10
    - unrelated domain when preference set        → −0.12
    - severe seniority mismatch                   → −0.20

Boosts:
    - exact preferred-domain match                → +0.08
    - strong core coverage (>60%)                 → +0.08
    - perfect seniority alignment                 → +0.05
    - career-goal alignment                       → +0.04
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Score breakdown dataclass
# ---------------------------------------------------------------------------

@dataclass
class FullScoreBreakdown:
    """Complete breakdown of every scoring component."""
    # --- 9 component scores (each 0-1) ---
    skill_match_score: float = 0.0
    core_skill_coverage_score: float = 0.0
    domain_preference_score: float = 0.0
    experience_fit_score: float = 0.0
    current_status_fit_score: float = 0.0
    education_fit_score: float = 0.0
    career_goal_fit_score: float = 0.0
    seniority_fit_score: float = 0.0
    confidence_score: float = 1.0

    # --- aggregated ---
    final_match_score: float = 0.0
    readiness_score: float = 0.0

    # --- penalties / boosts applied ---
    penalty_total: float = 0.0
    boost_total: float = 0.0
    penalties_applied: List[str] = field(default_factory=list)
    boosts_applied: List[str] = field(default_factory=list)

    # --- skill detail ---
    matched_core_skills: List[str] = field(default_factory=list)
    matched_supporting_skills: List[str] = field(default_factory=list)
    missing_critical_skills: List[str] = field(default_factory=list)
    total_core_skills: int = 0
    total_supporting_skills: int = 0
    supporting_skill_coverage: float = 0.0

    # --- entry-level flag ---
    is_entry_level_user: bool = False
    entry_level_adjustment: float = 0.0

    # --- domain confidence ---
    profile_source: str = "data_backed"   # "data_backed", "synthetic_expert", "synthetic_repair"

    def to_dict(self) -> dict:
        return {
            "skill_match_score": round(self.skill_match_score, 4),
            "core_skill_coverage_score": round(self.core_skill_coverage_score, 4),
            "domain_preference_score": round(self.domain_preference_score, 4),
            "experience_fit_score": round(self.experience_fit_score, 4),
            "current_status_fit_score": round(self.current_status_fit_score, 4),
            "education_fit_score": round(self.education_fit_score, 4),
            "career_goal_fit_score": round(self.career_goal_fit_score, 4),
            "seniority_fit_score": round(self.seniority_fit_score, 4),
            "confidence_score": round(self.confidence_score, 4),
            "final_match_score": round(self.final_match_score, 4),
            "readiness_score": round(self.readiness_score, 4),
            "penalty_total": round(self.penalty_total, 4),
            "boost_total": round(self.boost_total, 4),
            "penalties_applied": self.penalties_applied,
            "boosts_applied": self.boosts_applied,
            "matched_core_skills": self.matched_core_skills,
            "matched_supporting_skills": self.matched_supporting_skills,
            "missing_critical_skills": self.missing_critical_skills,
            "total_core_skills": self.total_core_skills,
            "total_supporting_skills": self.total_supporting_skills,
            "supporting_skill_coverage": round(self.supporting_skill_coverage, 4),
            "is_entry_level_user": self.is_entry_level_user,
            "entry_level_adjustment": round(self.entry_level_adjustment, 4),
            "profile_source": self.profile_source,
        }


# ═══════════════════════════════════════════════════════════════════════
#  WEIGHT TABLES  (all sum to 1.0)
# ═══════════════════════════════════════════════════════════════════════

# Weights when user has specified a preferred domain
WEIGHTS_WITH_DOMAIN = {
    "skill_match":         0.22,
    "core_skill_coverage": 0.25,
    "domain_preference":   0.20,
    "seniority_fit":       0.12,
    "experience_fit":      0.08,
    "career_goal_fit":     0.05,
    "current_status_fit":  0.04,
    "education_fit":       0.04,
}

# Weights when no domain preference is set — skill & core dominate
WEIGHTS_NO_DOMAIN = {
    "skill_match":         0.28,
    "core_skill_coverage": 0.30,
    "domain_preference":   0.00,
    "seniority_fit":       0.15,
    "experience_fit":      0.10,
    "career_goal_fit":     0.07,
    "current_status_fit":  0.05,
    "education_fit":       0.05,
}

# Penalty magnitudes
PENALTY_WEAK_CORE          = -0.15   # core coverage < 20%
PENALTY_SOFT_DOMINANT      = -0.10   # >60% matched skills are soft
PENALTY_DOMAIN_MISMATCH    = -0.12   # unrelated domain when pref set
PENALTY_SENIORITY_EXTREME  = -0.20   # student → senior+, or 5+ → intern

# Boost magnitudes
BOOST_EXACT_DOMAIN         = 0.08
BOOST_STRONG_CORE          = 0.08    # core coverage > 60%
BOOST_PERFECT_SENIORITY    = 0.05
BOOST_CAREER_GOAL_ALIGN    = 0.04

# Entry-level adjustments
ENTRY_LEVEL_SENIOR_PENALTY = -0.25   # student matched to senior+
ENTRY_LEVEL_INTERN_BOOST   = 0.12    # student matched to intern/jr


# ═══════════════════════════════════════════════════════════════════════
#  DOMAIN RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════════

RELATED_DOMAINS: Dict[str, List[str]] = {
    "BACKEND_ENGINEERING":  ["FULLSTACK_ENGINEERING", "SOFTWARE_ENGINEERING", "CLOUD_ENGINEERING", "DEVOPS_SRE"],
    "FRONTEND_ENGINEERING": ["FULLSTACK_ENGINEERING", "SOFTWARE_ENGINEERING", "UI_UX_DESIGN", "MOBILE_ENGINEERING"],
    "FULLSTACK_ENGINEERING":["BACKEND_ENGINEERING", "FRONTEND_ENGINEERING", "SOFTWARE_ENGINEERING"],
    "SOFTWARE_ENGINEERING": ["BACKEND_ENGINEERING", "FRONTEND_ENGINEERING", "FULLSTACK_ENGINEERING"],
    "DATA_ENGINEERING":     ["DATA_SCIENCE", "BACKEND_ENGINEERING", "CLOUD_ENGINEERING"],
    "DATA_SCIENCE":         ["DATA_ENGINEERING", "AI_ML"],
    "AI_ML":                ["DATA_SCIENCE", "DATA_ENGINEERING", "SOFTWARE_ENGINEERING"],
    "DEVOPS_SRE":           ["CLOUD_ENGINEERING", "BACKEND_ENGINEERING", "SECURITY"],
    "CLOUD_ENGINEERING":    ["DEVOPS_SRE", "BACKEND_ENGINEERING", "SECURITY"],
    "SECURITY":             ["DEVOPS_SRE", "CLOUD_ENGINEERING", "BACKEND_ENGINEERING"],
    "QA_TESTING":           ["SOFTWARE_ENGINEERING", "DEVOPS_SRE"],
    "MOBILE_ENGINEERING":   ["FRONTEND_ENGINEERING", "SOFTWARE_ENGINEERING", "UI_UX_DESIGN"],
    "UI_UX_DESIGN":         ["FRONTEND_ENGINEERING", "PRODUCT_MANAGEMENT", "MOBILE_ENGINEERING"],
    "PRODUCT_MANAGEMENT":   ["BUSINESS_ANALYSIS", "PROJECT_MANAGEMENT", "UI_UX_DESIGN"],
    "BUSINESS_ANALYSIS":    ["PRODUCT_MANAGEMENT", "PROJECT_MANAGEMENT", "DATA_SCIENCE"],
    "PROJECT_MANAGEMENT":   ["PRODUCT_MANAGEMENT", "BUSINESS_ANALYSIS"],
    "TECHNICAL_WRITING":    ["SOFTWARE_ENGINEERING", "PRODUCT_MANAGEMENT"],
    "BLOCKCHAIN_WEB3":      ["BACKEND_ENGINEERING", "SECURITY", "SOFTWARE_ENGINEERING"],
    "GAME_DEVELOPMENT":     ["SOFTWARE_ENGINEERING", "FRONTEND_ENGINEERING", "MOBILE_ENGINEERING"],
    "EMBEDDED_SYSTEMS":     ["SOFTWARE_ENGINEERING", "SECURITY"],
}

# Frontend → normalized domain
DOMAIN_NORMALIZER: Dict[str, str] = {
    "software_engineering":  "SOFTWARE_ENGINEERING",
    "frontend_engineering":  "FRONTEND_ENGINEERING",
    "backend_engineering":   "BACKEND_ENGINEERING",
    "fullstack_engineering": "FULLSTACK_ENGINEERING",
    "data_engineering":      "DATA_ENGINEERING",
    "data_science":          "DATA_SCIENCE",
    "data":                  "DATA_SCIENCE",
    "ai_ml":                 "AI_ML",
    "devops":                "DEVOPS_SRE",
    "devops_sre":            "DEVOPS_SRE",
    "cloud_engineering":     "CLOUD_ENGINEERING",
    "security":              "SECURITY",
    "qa":                    "QA_TESTING",
    "qa_testing":            "QA_TESTING",
    "mobile_engineering":    "MOBILE_ENGINEERING",
    "mobile":                "MOBILE_ENGINEERING",
    "ui_ux":                 "UI_UX_DESIGN",
    "ui_ux_design":          "UI_UX_DESIGN",
    "product_management":    "PRODUCT_MANAGEMENT",
    "business_analysis":     "BUSINESS_ANALYSIS",
    "project_management":    "PROJECT_MANAGEMENT",
    "technical_writing":     "TECHNICAL_WRITING",
    "blockchain_web3":       "BLOCKCHAIN_WEB3",
    "game_development":      "GAME_DEVELOPMENT",
    "embedded_systems":      "EMBEDDED_SYSTEMS",
}


# ═══════════════════════════════════════════════════════════════════════
#  SENIORITY TABLES
# ═══════════════════════════════════════════════════════════════════════

# Numeric level (from role_metadata.json)
# 1=intern, 2=junior, 3=mid, 4=senior, 5=staff, 6=lead/principal
SENIORITY_LEVEL_NAMES = {
    1: "intern",
    2: "junior",
    3: "mid",
    4: "senior",
    5: "staff",
    6: "lead",
}

# User experience → ideal seniority level range [min, max]
EXPERIENCE_TO_LEVEL_RANGE = {
    "student": (1, 2),   # intern, junior
    "0-1":     (1, 2),   # intern, junior
    "1-3":     (2, 3),   # junior, mid
    "3-5":     (3, 4),   # mid, senior
    "5+":      (4, 6),   # senior, staff, lead
}

# Current status → ideal seniority levels
STATUS_TO_LEVELS = {
    "student":  (1, 2),
    "graduate": (1, 3),
    "working":  (2, 6),
}


# ═══════════════════════════════════════════════════════════════════════
#  SCORING CACHE  (lazy-initialized from DataStore)
# ═══════════════════════════════════════════════════════════════════════

class _ScoringCache:
    """
    Pre-computed data structures for fast scoring.
    Built once from DataStore on first use.
    """
    initialized: bool = False

    # role_id → set of core skill_ids (importance >= 0.3)
    role_core_skills: Dict[str, Set[str]] = {}
    # role_id → set of supporting skill_ids (0.1 <= importance < 0.3)
    role_supporting_skills: Dict[str, Set[str]] = {}
    # role_id → set of all required skill_ids (importance > 0.02)
    role_all_required: Dict[str, Set[str]] = {}

    # role_id → seniority_level (1-6)
    role_seniority: Dict[str, int] = {}
    # role_id → domain
    role_domain: Dict[str, str] = {}
    # role_id → job_count (how many jobs → confidence indicator)
    role_job_count: Dict[str, int] = {}
    # role_id → profile_source ("data_backed", "synthetic_expert", "synthetic_repair")
    role_profile_source: Dict[str, str] = {}

    # skill_id → skill_type ("technical", "soft", "credential")
    skill_types: Dict[str, str] = {}
    # set of all soft skill ids
    soft_skill_ids: Set[str] = set()

    # skill_id → name (for response)
    skill_names: Dict[str, str] = {}


_cache = _ScoringCache()


def _ensure_cache():
    """Build the scoring cache from DataStore if not yet initialized."""
    if _cache.initialized:
        return

    from data_loader import DataStore

    # ── Build role skill tiers from role_profiles_df ──
    if DataStore.role_profiles_df is not None and not DataStore.role_profiles_df.empty:
        rp = DataStore.role_profiles_df
        for role_id, group in rp.groupby("role_id"):
            core = set()
            supporting = set()
            all_req = set()
            for _, row in group.iterrows():
                sid = str(row["skill_id"]).strip().upper()
                imp = float(row.get("importance", 0))
                if imp >= 0.3:
                    core.add(sid)
                elif imp >= 0.1:
                    supporting.add(sid)
                if imp > 0.02:
                    all_req.add(sid)
            _cache.role_core_skills[role_id] = core
            _cache.role_supporting_skills[role_id] = supporting
            _cache.role_all_required[role_id] = all_req
        print(f"[scoring_engine] Built skill tier cache for {len(_cache.role_core_skills)} roles")

    # ── Build seniority + domain from role_metadata ──
    if DataStore.role_metadata:
        meta_list = DataStore.role_metadata
        # role_metadata could be list[dict] or dict[role_id -> dict]
        if isinstance(meta_list, list):
            for entry in meta_list:
                rid = entry["role_id"]
                _cache.role_seniority[rid] = entry.get("seniority_level", 3)
                _cache.role_domain[rid] = entry.get("domain", "")
        elif isinstance(meta_list, dict):
            for rid, entry in meta_list.items():
                if isinstance(entry, dict):
                    _cache.role_seniority[rid] = entry.get("seniority_level", 3)
                    _cache.role_domain[rid] = entry.get("domain", "")
        print(f"[scoring_engine] Loaded seniority for {len(_cache.role_seniority)} roles")

    # ── Fallback seniority from role_id patterns ──
    _fill_seniority_from_pattern()

    # ── Build job counts from v3 metadata if available ──
    _load_job_counts()

    # ── Build skill type sets ──
    if DataStore.skills_df is not None and not DataStore.skills_df.empty:
        for _, row in DataStore.skills_df.iterrows():
            sid = str(row["skill_id"]).strip().upper()
            stype = str(row.get("type", "technical")).lower()
            _cache.skill_types[sid] = stype
            _cache.skill_names[sid] = str(row.get("name", sid))
            if stype == "soft":
                _cache.soft_skill_ids.add(sid)
        print(f"[scoring_engine] {len(_cache.soft_skill_ids)} soft skills, "
              f"{len(_cache.skill_types)} total skill types cached")
    else:
        # Fallback: use skill_id_to_name from DataStore
        _cache.skill_names = dict(DataStore.skill_id_to_name)

    _cache.initialized = True
    print("[scoring_engine] Cache initialized successfully")


def _fill_seniority_from_pattern():
    """Fallback: infer seniority from role_id naming patterns."""
    from data_loader import DataStore

    PATTERN_TO_LEVEL = [
        (["INTERN", "_INT"], 1),
        (["TRAINEE"], 1),
        (["JR_", "JUNIOR"], 2),
        (["_II", "SE_II"], 3),
        (["SENIOR_"], 4),
        (["STAFF_"], 5),
        (["LEAD_", "_LEAD"], 6),
        (["PRINCIPAL_"], 6),
        (["ARCHITECT"], 6),
        (["DIRECTOR_"], 6),
        (["HEAD_OF_"], 6),
    ]

    # Apply patterns only to roles not already in cache
    all_role_ids = set()
    if DataStore.role_profiles_df is not None:
        all_role_ids.update(DataStore.role_profiles_df["role_id"].unique())
    all_role_ids.update(DataStore.role_id_to_title.keys())

    for rid in all_role_ids:
        if rid in _cache.role_seniority:
            continue
        rid_upper = rid.upper()
        matched = False
        for patterns, level in PATTERN_TO_LEVEL:
            for p in patterns:
                if p in rid_upper:
                    _cache.role_seniority[rid] = level
                    matched = True
                    break
            if matched:
                break
        if not matched:
            _cache.role_seniority[rid] = 3  # default mid


def _load_job_counts():
    """Load job counts from v3 metadata or estimate from profiles."""
    from config import ML_DIR
    v3_meta_path = ML_DIR / "data" / "processed" / "role_metadata_v3.json"
    if v3_meta_path.exists():
        try:
            with open(v3_meta_path) as f:
                v3 = json.load(f)
            for rid, info in v3.items():
                if isinstance(info, dict):
                    _cache.role_job_count[rid] = info.get("job_count", 0)
                    src = info.get("source", "")
                    if src.startswith("synthetic"):
                        _cache.role_profile_source[rid] = src
            return
        except Exception:
            pass

    # Fallback: estimate from role_profiles_df frequency column
    from data_loader import DataStore
    if DataStore.role_profiles_df is not None and "frequency" in DataStore.role_profiles_df.columns:
        for rid, group in DataStore.role_profiles_df.groupby("role_id"):
            # frequency is fraction; rough job count = 1/min_nonzero_freq
            freqs = group["frequency"]
            nonzero = freqs[freqs > 0]
            if len(nonzero) > 0:
                _cache.role_job_count[rid] = max(1, int(round(1.0 / nonzero.min())))
            else:
                _cache.role_job_count[rid] = 1


# ═══════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def normalize_domain(domain_raw: Optional[str]) -> Optional[str]:
    """Normalize domain value to uppercase canonical form."""
    if not domain_raw:
        return None
    return DOMAIN_NORMALIZER.get(domain_raw.strip().lower(), domain_raw.strip().upper())


def get_role_seniority(role_id: str) -> int:
    """Return seniority level (1-6) for a role."""
    _ensure_cache()
    return _cache.role_seniority.get(role_id, 3)


def classify_user_level(
    experience_level: Optional[str],
    current_status: Optional[str],
    career_goal: Optional[str],
    num_skills: int,
) -> Tuple[bool, int]:
    """
    Classify user as entry-level or not.

    Returns:
        (is_entry_level, estimated_seniority_target)
        estimated_seniority_target: 1=intern, 2=junior, 3=mid, etc.
    """
    is_entry = False
    target = 3  # default mid

    exp = (experience_level or "").lower()
    status = (current_status or "").lower()
    goal = (career_goal or "").lower()

    # Strong entry-level signals
    if exp in ("student", "0-1"):
        is_entry = True
        target = 1 if exp == "student" else 2
    elif status == "student":
        is_entry = True
        target = 1
    elif goal == "first_job":
        is_entry = True
        target = 2
    elif num_skills <= 4:
        is_entry = True
        target = 2

    # Moderate signals
    if exp == "1-3":
        target = 2 if is_entry else 3
    elif exp == "3-5":
        target = 4
    elif exp == "5+":
        target = 5

    return is_entry, target


# ═══════════════════════════════════════════════════════════════════════
#  COMPONENT SCORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def compute_core_skill_coverage(
    user_skill_ids: Set[str],
    role_id: str,
) -> Tuple[float, List[str], List[str], List[str], int, float, List[str], int]:
    """
    Compute core and supporting skill coverage for a role.

    Returns:
        (core_coverage, matched_core, matched_supporting, missing_critical,
         total_core, supporting_coverage, missing_supporting, total_supporting)
    """
    _ensure_cache()

    core_skills = _cache.role_core_skills.get(role_id, set())
    supporting_skills = _cache.role_supporting_skills.get(role_id, set())

    matched_core = sorted(user_skill_ids & core_skills)
    missing_core = sorted(core_skills - user_skill_ids)
    matched_supp = sorted(user_skill_ids & supporting_skills)
    missing_supp = sorted(supporting_skills - user_skill_ids)

    core_cov = len(matched_core) / len(core_skills) if core_skills else 0.5
    supp_cov = len(matched_supp) / len(supporting_skills) if supporting_skills else 0.5

    return (core_cov, matched_core, matched_supp, missing_core,
            len(core_skills), supp_cov, missing_supp, len(supporting_skills))


def compute_domain_preference_score(
    role_domain: Optional[str],
    preferred_domain: Optional[str],
) -> float:
    """
    Domain preference component.

    Returns:
        1.0  — exact match
        0.7  — related domain
        0.5  — no preference set (neutral)
        0.15 — unrelated domain
    """
    if not preferred_domain or preferred_domain.strip() == "":
        return 0.5  # neutral

    pref = normalize_domain(preferred_domain)
    role = normalize_domain(role_domain)

    if not role:
        return 0.3

    if role == pref:
        return 1.0

    if role in RELATED_DOMAINS.get(pref, []):
        return 0.7

    return 0.15


def compute_experience_fit_score(
    role_id: str,
    experience_level: Optional[str],
) -> float:
    """
    Experience → seniority alignment.

    Returns 1.0 for perfect match, decays with distance.
    """
    if not experience_level:
        return 0.6  # neutral-ish

    _ensure_cache()
    role_level = _cache.role_seniority.get(role_id, 3)
    level_range = EXPERIENCE_TO_LEVEL_RANGE.get(experience_level.lower(), (2, 4))
    low, high = level_range

    if low <= role_level <= high:
        return 1.0

    distance = min(abs(role_level - low), abs(role_level - high))
    # Decay: 1 step = 0.6, 2 steps = 0.35, 3+ steps = 0.15
    decay_map = {1: 0.6, 2: 0.35}
    return decay_map.get(distance, 0.15)


def compute_current_status_fit_score(
    role_id: str,
    current_status: Optional[str],
) -> float:
    """
    Student / graduate / working alignment with role level.
    """
    if not current_status:
        return 0.6

    _ensure_cache()
    role_level = _cache.role_seniority.get(role_id, 3)
    level_range = STATUS_TO_LEVELS.get(current_status.lower(), (1, 6))
    low, high = level_range

    if low <= role_level <= high:
        return 1.0

    distance = min(abs(role_level - low), abs(role_level - high))
    return max(0.1, 1.0 - distance * 0.25)


def compute_education_fit_score(education_level: Optional[str]) -> float:
    """
    Soft education signal.  Not a hard gate.
    """
    if not education_level:
        return 0.6

    scoring = {
        "masters": 0.95,
        "phd":     0.95,
        "bachelors": 0.85,
        "degree":    0.85,
        "hnd":       0.70,
        "diploma":   0.65,
        "al":        0.50,
    }
    return scoring.get(education_level.lower(), 0.55)


def compute_career_goal_fit_score(
    role_id: str,
    career_goal: Optional[str],
    experience_level: Optional[str],
) -> float:
    """
    Career goal alignment.

    - first_job  → entry-level roles score high
    - get_promoted → roles above current seniority
    - switch_career → accessible roles (junior-mid)
    """
    if not career_goal:
        return 0.6

    _ensure_cache()
    role_level = _cache.role_seniority.get(role_id, 3)
    goal = career_goal.lower()

    if goal == "first_job":
        if role_level <= 2:
            return 1.0
        elif role_level == 3:
            return 0.5
        else:
            return 0.2

    elif goal == "get_promoted":
        # Ideal: role is 1–2 levels above user's current
        user_range = EXPERIENCE_TO_LEVEL_RANGE.get(
            (experience_level or "1-3").lower(), (2, 4)
        )
        user_mid = (user_range[0] + user_range[1]) / 2
        gap = role_level - user_mid
        if 0.5 <= gap <= 2.0:
            return 1.0
        elif 0 <= gap <= 0.5:
            return 0.7
        elif gap > 2.0:
            return 0.4
        else:
            return 0.3

    elif goal == "switch_career":
        # Switchers need accessible roles
        if role_level <= 3:
            return 1.0
        elif role_level == 4:
            return 0.6
        else:
            return 0.3

    return 0.6


def compute_seniority_fit_score(
    role_id: str,
    experience_level: Optional[str],
    current_status: Optional[str],
) -> float:
    """
    Numeric seniority distance score.
    Tighter than experience_fit — directly compares level numbers.
    """
    _ensure_cache()
    role_level = _cache.role_seniority.get(role_id, 3)

    # Determine user's target level
    _, user_target = classify_user_level(
        experience_level, current_status, None, 10
    )

    distance = abs(role_level - user_target)
    if distance == 0:
        return 1.0
    elif distance == 1:
        return 0.75
    elif distance == 2:
        return 0.45
    elif distance == 3:
        return 0.20
    else:
        return 0.05


def compute_confidence_score(role_id: str) -> float:
    """
    Confidence in the mapping quality (0.5–1.0).

    Based on:
    - How many jobs back this role's profile (more jobs = higher confidence)
    - Whether the role has a real profile (core skills exist)
    """
    _ensure_cache()

    # Job count factor
    job_count = _cache.role_job_count.get(role_id, 0)
    if job_count >= 200:
        job_factor = 1.0
    elif job_count >= 50:
        job_factor = 0.9
    elif job_count >= 10:
        job_factor = 0.8
    elif job_count >= 3:
        job_factor = 0.7
    else:
        job_factor = 0.55

    # Profile quality factor
    core_count = len(_cache.role_core_skills.get(role_id, set()))
    if core_count >= 8:
        profile_factor = 1.0
    elif core_count >= 4:
        profile_factor = 0.9
    elif core_count >= 1:
        profile_factor = 0.75
    else:
        profile_factor = 0.5

    return min(1.0, max(0.5, 0.6 * job_factor + 0.4 * profile_factor))


# ═══════════════════════════════════════════════════════════════════════
#  PENALTIES & BOOSTS
# ═══════════════════════════════════════════════════════════════════════

def compute_penalties(
    core_coverage: float,
    user_skill_ids: Set[str],
    matched_core: List[str],
    matched_supporting: List[str],
    role_domain: Optional[str],
    preferred_domain: Optional[str],
    role_id: str,
    is_entry_level: bool,
    user_seniority_target: int,
) -> Tuple[float, List[str]]:
    """
    Compute all penalties.

    Returns (total_penalty, list_of_penalty_descriptions)
    """
    _ensure_cache()
    total = 0.0
    reasons = []

    # 1. Weak core skill coverage
    if core_coverage < 0.20 and len(_cache.role_core_skills.get(role_id, set())) >= 3:
        total += PENALTY_WEAK_CORE
        reasons.append(f"weak_core_coverage({core_coverage:.0%})")

    # 2. Soft-skill dominated
    all_matched = set(matched_core) | set(matched_supporting)
    if all_matched:
        soft_count = sum(1 for s in all_matched if s in _cache.soft_skill_ids)
        soft_ratio = soft_count / len(all_matched)
        if soft_ratio > 0.6:
            total += PENALTY_SOFT_DOMINANT
            reasons.append(f"soft_skill_dominated({soft_ratio:.0%})")

    # 3. Domain mismatch
    pref = normalize_domain(preferred_domain)
    role_norm = normalize_domain(role_domain)
    if pref and role_norm and pref != role_norm:
        if role_norm not in RELATED_DOMAINS.get(pref, []):
            total += PENALTY_DOMAIN_MISMATCH
            reasons.append(f"domain_mismatch({role_norm}!={pref})")

    # 4. Severe seniority mismatch
    role_level = _cache.role_seniority.get(role_id, 3)
    if is_entry_level and role_level >= 4:
        total += PENALTY_SENIORITY_EXTREME
        reasons.append(f"entry_user_senior_role(level={role_level})")
    elif user_seniority_target >= 5 and role_level <= 1:
        # Experienced user → intern role
        total += PENALTY_SENIORITY_EXTREME * 0.5  # lighter
        reasons.append(f"senior_user_intern_role(level={role_level})")

    return total, reasons


def compute_boosts(
    core_coverage: float,
    domain_score: float,
    seniority_fit: float,
    career_goal_fit: float,
    role_domain: Optional[str],
    preferred_domain: Optional[str],
) -> Tuple[float, List[str]]:
    """
    Compute all boosts.

    Returns (total_boost, list_of_boost_descriptions)
    """
    total = 0.0
    reasons = []

    # 1. Exact domain match
    pref = normalize_domain(preferred_domain)
    role_norm = normalize_domain(role_domain)
    if pref and role_norm == pref:
        total += BOOST_EXACT_DOMAIN
        reasons.append("exact_domain_match")

    # 2. Strong core coverage
    if core_coverage > 0.60:
        total += BOOST_STRONG_CORE
        reasons.append(f"strong_core({core_coverage:.0%})")

    # 3. Perfect seniority alignment
    if seniority_fit >= 0.95:
        total += BOOST_PERFECT_SENIORITY
        reasons.append("perfect_seniority")

    # 4. Career goal alignment
    if career_goal_fit >= 0.95:
        total += BOOST_CAREER_GOAL_ALIGN
        reasons.append("career_goal_aligned")

    return total, reasons


# ═══════════════════════════════════════════════════════════════════════
#  ENTRY-LEVEL ADJUSTMENTS
# ═══════════════════════════════════════════════════════════════════════

def apply_entry_level_adjustments(
    role_id: str,
    is_entry_level: bool,
    user_seniority_target: int,
    base_score: float,
) -> float:
    """
    Adjust scores for entry-level users.

    - Heavy boost for intern/junior roles
    - Heavy penalty for senior+ roles
    """
    if not is_entry_level:
        return 0.0

    _ensure_cache()
    role_level = _cache.role_seniority.get(role_id, 3)

    adjustment = 0.0

    # Boost intern/junior roles
    if role_level <= user_seniority_target:
        adjustment += ENTRY_LEVEL_INTERN_BOOST
    elif role_level == user_seniority_target + 1:
        adjustment += ENTRY_LEVEL_INTERN_BOOST * 0.4  # smaller boost for +1

    # Penalize senior+ roles for entry-level users
    if role_level >= 4:
        gap = role_level - user_seniority_target
        adjustment += ENTRY_LEVEL_SENIOR_PENALTY * min(gap / 3, 1.0)

    return adjustment


# ═══════════════════════════════════════════════════════════════════════
#  READINESS (independent of match score)
# ═══════════════════════════════════════════════════════════════════════

def compute_readiness(
    core_coverage: float,
    supporting_coverage: float,
    seniority_fit: float,
    education_fit: float,
) -> float:
    """
    How ready is the user *right now* for this role?
    Independent of match_score (which factors in preference/goal).

    Formula:
        readiness = 0.50 × core_skill_coverage
                  + 0.25 × supporting_skill_coverage
                  + 0.15 × seniority_alignment
                  + 0.10 × education_factor
    """
    readiness = (
        0.50 * core_coverage +
        0.25 * supporting_coverage +
        0.15 * seniority_fit +
        0.10 * education_fit
    )
    return max(0.0, min(1.0, readiness))


# ═══════════════════════════════════════════════════════════════════════
#  MAIN SCORING FUNCTION
# ═══════════════════════════════════════════════════════════════════════

def score_role_for_user(
    user_skill_ids: Set[str],
    role_id: str,
    role_domain: Optional[str],
    raw_similarity: float,
    *,
    preferred_domain: Optional[str] = None,
    experience_level: Optional[str] = None,
    current_status: Optional[str] = None,
    education_level: Optional[str] = None,
    career_goal: Optional[str] = None,
) -> FullScoreBreakdown:
    """
    Compute all score components for a single role/user pair.

    Args:
        user_skill_ids: Set of uppercase skill IDs the user selected
        role_id:        Target role identifier
        role_domain:    Domain of the role (may be None)
        raw_similarity: Cosine similarity from vector comparison (0-1)
        preferred_domain: User's preferred domain (frontend string)
        experience_level: "student", "0-1", "1-3", "3-5", "5+"
        current_status: "student", "graduate", "working"
        education_level: "al", "diploma", "hnd", "bachelors", "masters"
        career_goal: "first_job", "switch_career", "get_promoted"

    Returns:
        FullScoreBreakdown with all components, final score, and readiness
    """
    _ensure_cache()

    breakdown = FullScoreBreakdown()

    # ── 1. Skill match (cosine similarity) ──
    breakdown.skill_match_score = max(0.0, min(1.0, raw_similarity))

    # ── 2. Core & supporting skill coverage ──
    (core_cov, matched_core, matched_supp, missing_core,
     total_core, supp_cov, missing_supp, total_supp) = compute_core_skill_coverage(user_skill_ids, role_id)

    breakdown.core_skill_coverage_score = core_cov
    breakdown.supporting_skill_coverage = supp_cov
    breakdown.matched_core_skills = matched_core
    breakdown.matched_supporting_skills = matched_supp
    breakdown.missing_critical_skills = missing_core
    breakdown.total_core_skills = total_core
    breakdown.total_supporting_skills = total_supp

    # ── 3. Domain preference ──
    breakdown.domain_preference_score = compute_domain_preference_score(role_domain, preferred_domain)

    # ── 4. Experience fit ──
    breakdown.experience_fit_score = compute_experience_fit_score(role_id, experience_level)

    # ── 5. Current status fit ──
    breakdown.current_status_fit_score = compute_current_status_fit_score(role_id, current_status)

    # ── 6. Education fit ──
    breakdown.education_fit_score = compute_education_fit_score(education_level)

    # ── 7. Career goal fit ──
    breakdown.career_goal_fit_score = compute_career_goal_fit_score(role_id, career_goal, experience_level)

    # ── 8. Seniority fit ──
    breakdown.seniority_fit_score = compute_seniority_fit_score(role_id, experience_level, current_status)

    # ── 9. Confidence ──
    breakdown.confidence_score = compute_confidence_score(role_id)

    # ── Profile source (synthetic vs data-backed) ──
    breakdown.profile_source = _cache.role_profile_source.get(role_id, "data_backed")

    # ── Entry-level classification ──
    is_entry, user_target = classify_user_level(
        experience_level, current_status, career_goal, len(user_skill_ids)
    )
    breakdown.is_entry_level_user = is_entry

    # ── Weighted base score ──
    has_domain_pref = preferred_domain and preferred_domain.strip() != ""
    weights = WEIGHTS_WITH_DOMAIN if has_domain_pref else WEIGHTS_NO_DOMAIN

    base_score = (
        weights["skill_match"]         * breakdown.skill_match_score +
        weights["core_skill_coverage"] * breakdown.core_skill_coverage_score +
        weights["domain_preference"]   * breakdown.domain_preference_score +
        weights["seniority_fit"]       * breakdown.seniority_fit_score +
        weights["experience_fit"]      * breakdown.experience_fit_score +
        weights["career_goal_fit"]     * breakdown.career_goal_fit_score +
        weights["current_status_fit"]  * breakdown.current_status_fit_score +
        weights["education_fit"]       * breakdown.education_fit_score
    )

    # Apply confidence multiplier
    base_score *= breakdown.confidence_score

    # ── Penalties ──
    penalty, penalty_reasons = compute_penalties(
        core_cov, user_skill_ids, matched_core, matched_supp,
        role_domain, preferred_domain, role_id, is_entry, user_target,
    )
    breakdown.penalty_total = penalty
    breakdown.penalties_applied = penalty_reasons

    # ── Boosts ──
    boost, boost_reasons = compute_boosts(
        core_cov,
        breakdown.domain_preference_score,
        breakdown.seniority_fit_score,
        breakdown.career_goal_fit_score,
        role_domain, preferred_domain,
    )
    breakdown.boost_total = boost
    breakdown.boosts_applied = boost_reasons

    # ── Entry-level adjustment ──
    entry_adj = apply_entry_level_adjustments(role_id, is_entry, user_target, base_score)
    breakdown.entry_level_adjustment = entry_adj

    # ── Final match score ──
    final = base_score + penalty + boost + entry_adj
    breakdown.final_match_score = max(0.0, min(1.0, final))

    # ── Readiness (independent) ──
    breakdown.readiness_score = compute_readiness(
        core_cov, supp_cov,
        breakdown.seniority_fit_score,
        breakdown.education_fit_score,
    )

    return breakdown


# ═══════════════════════════════════════════════════════════════════════
#  BEST MATCH SELECTION
# ═══════════════════════════════════════════════════════════════════════

def select_best_match(scored_roles: List[dict]) -> int:
    """
    Select the Best Match index from scored roles.

    Best Match = highest final_match_score, with tie-breaking by:
        1. core_skill_coverage_score
        2. confidence_score
        3. readiness_score

    Returns the index into scored_roles.
    """
    if not scored_roles:
        return 0

    best_idx = 0
    best_key = _sort_key(scored_roles[0])
    for i, role in enumerate(scored_roles[1:], 1):
        key = _sort_key(role)
        if key > best_key:
            best_key = key
            best_idx = i
    return best_idx


def _sort_key(role_data: dict) -> tuple:
    """Multi-level sort key for ranking roles."""
    bd = role_data.get("score_breakdown")
    if bd is None:
        return (0, 0, 0, 0)
    if isinstance(bd, FullScoreBreakdown):
        return (
            bd.final_match_score,
            bd.core_skill_coverage_score,
            bd.confidence_score,
            bd.readiness_score,
        )
    # dict form
    return (
        bd.get("final_match_score", 0),
        bd.get("core_skill_coverage_score", 0),
        bd.get("confidence_score", 0),
        bd.get("readiness_score", 0),
    )


# ═══════════════════════════════════════════════════════════════════════
#  EXPLANATION GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def generate_ranking_explanation(
    breakdown: FullScoreBreakdown,
    role_title: str,
    role_domain: Optional[str],
    preferred_domain: Optional[str],
    is_best_match: bool,
    rank: int = 0,
    *,
    experience_level: Optional[str] = None,
    current_status: Optional[str] = None,
) -> dict:
    """Generate human-readable explanations for a recommendation."""
    explanations = {}

    # Domain impact
    pref = normalize_domain(preferred_domain) if preferred_domain else None
    role_norm = normalize_domain(role_domain) if role_domain else None

    if not pref:
        explanations["domain_impact"] = "No domain preference — ranking driven by skill fit and profile alignment."
    elif role_norm == pref:
        explanations["domain_impact"] = f"Exact match with your preferred domain ({role_domain})."
    elif role_norm in RELATED_DOMAINS.get(pref, []):
        explanations["domain_impact"] = f"Related to your preferred domain ({preferred_domain}). Moderate boost applied."
    else:
        explanations["domain_impact"] = f"Outside your preferred domain ({preferred_domain}). Ranked on skill fit alone."

    # Ranking explanation
    if is_best_match:
        factors = []
        if breakdown.core_skill_coverage_score >= 0.5:
            factors.append(f"{breakdown.core_skill_coverage_score:.0%} core skill coverage")
        if breakdown.domain_preference_score >= 0.9:
            factors.append("strong domain match")
        if breakdown.seniority_fit_score >= 0.9:
            factors.append("ideal seniority fit")
        factor_str = ", ".join(factors) if factors else "highest combined score"
        explanations["why_ranked_here"] = f"Best Match — {factor_str}."
        explanations["why_best_match"] = (
            f"Highest overall fit ({breakdown.final_match_score:.0%}) "
            f"with {len(breakdown.matched_core_skills)}/{breakdown.total_core_skills} "
            f"core skills matched."
        )
    else:
        explanations["why_ranked_here"] = f"Ranked #{rank + 1} — scored {breakdown.final_match_score:.0%} overall."
        explanations["why_best_match"] = None

    # Readiness
    r_pct = int(breakdown.readiness_score * 100)
    if r_pct >= 70:
        explanations["readiness"] = f"High readiness ({r_pct}%) — you have most core skills."
    elif r_pct >= 40:
        explanations["readiness"] = f"Moderate readiness ({r_pct}%) — some key skills to develop."
    else:
        explanations["readiness"] = f"Growth opportunity ({r_pct}%) — focus on building core skills first."

    # Why not more ready — specific, never generic
    why_not_ready_parts = []
    if breakdown.missing_critical_skills:
        n_miss = len(breakdown.missing_critical_skills)
        skill_names = [_cache.skill_names.get(s, s) for s in breakdown.missing_critical_skills[:3]]
        why_not_ready_parts.append(
            f"Missing {n_miss} core skill{'s' if n_miss > 1 else ''}: {', '.join(skill_names)}"
            + (f" and {n_miss - 3} more" if n_miss > 3 else "")
        )
    if breakdown.seniority_fit_score < 0.6:
        why_not_ready_parts.append("Seniority level mismatch — this role targets a different experience tier.")
    if breakdown.supporting_skill_coverage < 0.3 and breakdown.total_supporting_skills > 0:
        why_not_ready_parts.append(
            f"Only {breakdown.supporting_skill_coverage:.0%} of supporting skills covered "
            f"({breakdown.total_supporting_skills} expected)."
        )
    if breakdown.education_fit_score < 0.5:
        why_not_ready_parts.append("Education level may not fully align with typical requirements.")
    explanations["why_not_more_ready"] = " | ".join(why_not_ready_parts) if why_not_ready_parts else "No major gaps identified."

    # Seniority fit explanation
    sen_pct = int(breakdown.seniority_fit_score * 100)
    if sen_pct >= 90:
        explanations["seniority_fit"] = "Ideal seniority match for your experience level."
    elif sen_pct >= 60:
        explanations["seniority_fit"] = "Reasonable seniority fit — slight stretch or underlap."
    else:
        explanations["seniority_fit"] = "Significant seniority gap — this role targets a different career stage."

    # Entry-level note
    if breakdown.is_entry_level_user:
        explanations["entry_level_note"] = "Recommendations prioritize entry-level and junior roles for your profile."

    # Penalties / boosts
    if breakdown.penalties_applied:
        explanations["adjustments"] = f"Penalties: {', '.join(breakdown.penalties_applied)}"
    if breakdown.boosts_applied:
        boosts_str = f"Boosts: {', '.join(breakdown.boosts_applied)}"
        explanations["adjustments"] = explanations.get("adjustments", "") + (" | " if "adjustments" in explanations else "") + boosts_str

    # Synthetic profile warning
    if breakdown.profile_source.startswith("synthetic"):
        explanations["data_confidence"] = (
            "This role's profile is expert-defined (not derived from job-market data). "
            "Confidence is lower — treat as indicative, not definitive."
        )

    return explanations


# ═══════════════════════════════════════════════════════════════════════
#  BACKWARD COMPATIBILITY (old scoring.py interface)
# ═══════════════════════════════════════════════════════════════════════

# Re-export types used by old code
ScoreBreakdown = FullScoreBreakdown


def compute_final_score(
    skill_match_score: float,
    role_id: str,
    role_domain: Optional[str],
    preferred_domain: Optional[str],
    experience_level: Optional[str],
    career_goal: Optional[str],
    education_level: Optional[str],
    readiness_score: float = 0.5,
) -> FullScoreBreakdown:
    """
    Backward-compatible wrapper for old scoring.py interface.
    Delegates to score_role_for_user with empty skill set.
    """
    return score_role_for_user(
        user_skill_ids=set(),
        role_id=role_id,
        role_domain=role_domain,
        raw_similarity=skill_match_score,
        preferred_domain=preferred_domain,
        experience_level=experience_level,
        education_level=education_level,
        career_goal=career_goal,
    )
