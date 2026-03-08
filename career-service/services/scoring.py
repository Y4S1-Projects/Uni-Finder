"""
Career Recommendation Scoring Engine
=====================================
Implements explicit weighted scoring for career recommendations.

The final ranking considers:
- skill_match_score: How well user's skills match role requirements
- domain_preference_score: Explicit domain preference from user
- experience_fit_score: Seniority alignment with experience level
- career_goal_fit_score: Whether role aligns with career goal
- education_fit_score: Soft education support signal

This replaces pure cosine similarity ranking with profile-aware weighted scoring.
"""
from typing import Optional
from dataclasses import dataclass


# =============================================================================
# Domain Relationship Mappings
# =============================================================================

# Granular domains (21 total) matching frontend options
ALL_DOMAINS = [
    "SOFTWARE_ENGINEERING",
    "FRONTEND_ENGINEERING",
    "BACKEND_ENGINEERING",
    "FULLSTACK_ENGINEERING",
    "DATA_ENGINEERING",
    "DATA_SCIENCE",
    "AI_ML",
    "DEVOPS_SRE",
    "CLOUD_ENGINEERING",
    "SECURITY",
    "QA_TESTING",
    "MOBILE_ENGINEERING",
    "UI_UX_DESIGN",
    "PRODUCT_MANAGEMENT",
    "BUSINESS_ANALYSIS",
    "PROJECT_MANAGEMENT",
    "TECHNICAL_WRITING",
    "BLOCKCHAIN_WEB3",
    "GAME_DEVELOPMENT",
    "EMBEDDED_SYSTEMS",
]

# Related domains (get smaller boost when preferred domain is set)
RELATED_DOMAINS = {
    "BACKEND_ENGINEERING": ["FULLSTACK_ENGINEERING", "SOFTWARE_ENGINEERING", "CLOUD_ENGINEERING", "DEVOPS_SRE"],
    "FRONTEND_ENGINEERING": ["FULLSTACK_ENGINEERING", "SOFTWARE_ENGINEERING", "UI_UX_DESIGN", "MOBILE_ENGINEERING"],
    "FULLSTACK_ENGINEERING": ["BACKEND_ENGINEERING", "FRONTEND_ENGINEERING", "SOFTWARE_ENGINEERING"],
    "SOFTWARE_ENGINEERING": ["BACKEND_ENGINEERING", "FRONTEND_ENGINEERING", "FULLSTACK_ENGINEERING"],
    "DATA_ENGINEERING": ["DATA_SCIENCE", "BACKEND_ENGINEERING", "CLOUD_ENGINEERING"],
    "DATA_SCIENCE": ["DATA_ENGINEERING", "AI_ML"],
    "AI_ML": ["DATA_SCIENCE", "DATA_ENGINEERING", "SOFTWARE_ENGINEERING"],
    "DEVOPS_SRE": ["CLOUD_ENGINEERING", "BACKEND_ENGINEERING", "SECURITY"],
    "CLOUD_ENGINEERING": ["DEVOPS_SRE", "BACKEND_ENGINEERING", "SECURITY"],
    "SECURITY": ["DEVOPS_SRE", "CLOUD_ENGINEERING", "BACKEND_ENGINEERING"],
    "QA_TESTING": ["SOFTWARE_ENGINEERING", "DEVOPS_SRE"],
    "MOBILE_ENGINEERING": ["FRONTEND_ENGINEERING", "SOFTWARE_ENGINEERING", "UI_UX_DESIGN"],
    "UI_UX_DESIGN": ["FRONTEND_ENGINEERING", "PRODUCT_MANAGEMENT", "MOBILE_ENGINEERING"],
    "PRODUCT_MANAGEMENT": ["BUSINESS_ANALYSIS", "PROJECT_MANAGEMENT", "UI_UX_DESIGN"],
    "BUSINESS_ANALYSIS": ["PRODUCT_MANAGEMENT", "PROJECT_MANAGEMENT", "DATA_SCIENCE"],
    "PROJECT_MANAGEMENT": ["PRODUCT_MANAGEMENT", "BUSINESS_ANALYSIS"],
    "TECHNICAL_WRITING": ["SOFTWARE_ENGINEERING", "PRODUCT_MANAGEMENT"],
    "BLOCKCHAIN_WEB3": ["BACKEND_ENGINEERING", "SECURITY", "SOFTWARE_ENGINEERING"],
    "GAME_DEVELOPMENT": ["SOFTWARE_ENGINEERING", "FRONTEND_ENGINEERING", "MOBILE_ENGINEERING"],
    "EMBEDDED_SYSTEMS": ["SOFTWARE_ENGINEERING", "HARDWARE_ENGINEERING"],
}

# Frontend domain value → normalized domain
DOMAIN_NORMALIZER = {
    "software_engineering": "SOFTWARE_ENGINEERING",
    "frontend_engineering": "FRONTEND_ENGINEERING",
    "backend_engineering": "BACKEND_ENGINEERING",
    "fullstack_engineering": "FULLSTACK_ENGINEERING",
    "data_engineering": "DATA_ENGINEERING",
    "data_science": "DATA_SCIENCE",
    "data": "DATA_SCIENCE",  # Legacy mapping
    "ai_ml": "AI_ML",
    "devops": "DEVOPS_SRE",
    "devops_sre": "DEVOPS_SRE",
    "cloud_engineering": "CLOUD_ENGINEERING",
    "security": "SECURITY",
    "qa": "QA_TESTING",
    "qa_testing": "QA_TESTING",
    "mobile_engineering": "MOBILE_ENGINEERING",
    "mobile": "MOBILE_ENGINEERING",
    "ui_ux": "UI_UX_DESIGN",
    "ui_ux_design": "UI_UX_DESIGN",
    "product_management": "PRODUCT_MANAGEMENT",
    "business_analysis": "BUSINESS_ANALYSIS",
    "project_management": "PROJECT_MANAGEMENT",
    "technical_writing": "TECHNICAL_WRITING",
    "blockchain_web3": "BLOCKCHAIN_WEB3",
    "game_development": "GAME_DEVELOPMENT",
    "embedded_systems": "EMBEDDED_SYSTEMS",
}


# =============================================================================
# Seniority Mappings
# =============================================================================

# Experience level → expected role seniorities
EXPERIENCE_TO_SENIORITY = {
    "student": ["INTERN", "INT", "JR", "TRAINEE"],
    "0-1": ["INTERN", "INT", "JR", "TRAINEE"],
    "1-3": ["JR", "MID", "II"],
    "3-5": ["MID", "SENIOR", "II", "III"],
    "5+": ["SENIOR", "LEAD", "STAFF", "PRINCIPAL", "ARCHITECT", "DIRECTOR", "HEAD"],
}

# Role ID patterns to seniority (used for detection)
SENIORITY_PATTERNS = {
    "INTERN": ["INTERN", "_INT", "TRAINEE"],
    "JR": ["JR_", "JUNIOR"],
    "MID": ["_II", "MID_", "SE_II"],
    "SENIOR": ["SENIOR_", "_SENIOR", "_III"],
    "LEAD": ["LEAD_", "_LEAD"],
    "STAFF": ["STAFF_"],
    "PRINCIPAL": ["PRINCIPAL_"],
    "ARCHITECT": ["ARCHITECT"],
    "DIRECTOR": ["DIRECTOR_"],
    "HEAD": ["HEAD_OF_"],
}


# =============================================================================
# Scoring Weights
# =============================================================================

# Default weights for final score calculation (sum to 1.0)
DEFAULT_WEIGHTS = {
    "skill_match": 0.40,       # Skills are important but not everything
    "domain_preference": 0.30, # Strong weight for explicit domain preference  
    "experience_fit": 0.15,    # Seniority alignment
    "career_goal_fit": 0.10,   # Intent alignment
    "education_fit": 0.05,     # Soft signal
}

# Weights when no domain preference is set (skills matter more)
NO_PREFERENCE_WEIGHTS = {
    "skill_match": 0.55,
    "domain_preference": 0.10,  # Reduced but still consider domain diversity
    "experience_fit": 0.20,
    "career_goal_fit": 0.10,
    "education_fit": 0.05,
}


# =============================================================================
# Score Calculation Functions
# =============================================================================

def normalize_domain(domain_raw: Optional[str]) -> Optional[str]:
    """Normalize domain value to uppercase canonical form."""
    if not domain_raw:
        return None
    domain_lower = domain_raw.strip().lower()
    return DOMAIN_NORMALIZER.get(domain_lower, domain_raw.upper())


def detect_role_seniority(role_id: str) -> str:
    """Detect seniority level from role_id pattern."""
    role_upper = role_id.upper()
    for seniority, patterns in SENIORITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in role_upper:
                return seniority
    return "MID"  # Default assumption


def compute_domain_preference_score(
    role_domain: Optional[str],
    preferred_domain: Optional[str],
) -> float:
    """
    Calculate domain preference score.
    
    Returns:
        1.0 - Exact domain match
        0.7 - Related domain
        0.5 - No preference set (neutral)
        0.2 - Unrelated domain
    """
    # No preference = neutral score
    if not preferred_domain or preferred_domain.strip() == "":
        return 0.5
    
    # Normalize domains
    pref_normalized = normalize_domain(preferred_domain)
    role_normalized = normalize_domain(role_domain)
    
    if not role_normalized:
        return 0.3  # Unknown domain gets low score
    
    # Exact match
    if role_normalized == pref_normalized:
        return 1.0
    
    # Related domain
    related_list = RELATED_DOMAINS.get(pref_normalized, [])
    if role_normalized in related_list:
        return 0.7
    
    # Unrelated domain
    return 0.2


def compute_experience_fit_score(
    role_id: str,
    experience_level: Optional[str],
) -> float:
    """
    Calculate experience fit score based on role seniority vs user experience.
    
    Returns:
        1.0 - Perfect seniority match
        0.7 - Adjacent seniority (one level off)
        0.4 - Far seniority mismatch
    """
    if not experience_level:
        return 0.7  # Neutral-ish when not specified
    
    role_seniority = detect_role_seniority(role_id)
    expected_seniorities = EXPERIENCE_TO_SENIORITY.get(experience_level.lower(), ["MID"])
    
    # Perfect match
    if role_seniority in expected_seniorities:
        return 1.0
    
    # Adjacent levels (one step away)
    seniority_order = ["INTERN", "JR", "MID", "SENIOR", "LEAD", "STAFF", "PRINCIPAL", "ARCHITECT", "DIRECTOR", "HEAD"]
    try:
        role_idx = seniority_order.index(role_seniority)
        for expected in expected_seniorities:
            if expected in seniority_order:
                expected_idx = seniority_order.index(expected)
                if abs(role_idx - expected_idx) <= 1:
                    return 0.7
    except ValueError:
        pass
    
    return 0.4


def compute_career_goal_fit_score(
    role_id: str,
    career_goal: Optional[str],
    experience_level: Optional[str],
) -> float:
    """
    Calculate career goal alignment score.
    
    Career goals:
    - first_job: Prefers entry-level roles
    - get_promoted: Prefers one level up from current
    - switch_career: Prefers accessible roles in new domain
    """
    if not career_goal:
        return 0.7  # Neutral when not specified
    
    role_seniority = detect_role_seniority(role_id)
    goal_lower = career_goal.lower()
    
    if goal_lower == "first_job":
        # Want entry-level roles
        if role_seniority in ["INTERN", "JR", "TRAINEE", "INT"]:
            return 1.0
        elif role_seniority == "MID":
            return 0.6
        else:
            return 0.3
    
    elif goal_lower == "get_promoted":
        # Want roles one level up from current experience
        exp_level = experience_level.lower() if experience_level else "1-3"
        expected_current = EXPERIENCE_TO_SENIORITY.get(exp_level, ["MID"])
        
        # Check if role is one level above current
        seniority_order = ["INTERN", "JR", "MID", "SENIOR", "LEAD", "STAFF", "PRINCIPAL"]
        try:
            role_idx = seniority_order.index(role_seniority)
            for current in expected_current:
                if current in seniority_order:
                    current_idx = seniority_order.index(current)
                    # Role is 1-2 levels above current = perfect
                    if 1 <= role_idx - current_idx <= 2:
                        return 1.0
                    # Role is at same level = okay
                    if role_idx == current_idx:
                        return 0.7
        except ValueError:
            pass
        return 0.5
    
    elif goal_lower == "switch_career":
        # Career switchers often need accessible entry/mid roles
        if role_seniority in ["JR", "MID", "INT"]:
            return 1.0
        elif role_seniority == "SENIOR":
            return 0.7
        else:
            return 0.5
    
    return 0.7


def compute_education_fit_score(
    education_level: Optional[str],
) -> float:
    """
    Soft education signal (not a hard blocker).
    Higher education gets slight boost for senior roles.
    """
    if not education_level:
        return 0.7
    
    edu_lower = education_level.lower()
    
    # Higher education = slightly better
    if edu_lower in ["masters", "phd"]:
        return 0.9
    elif edu_lower in ["bachelors", "degree"]:
        return 0.8
    elif edu_lower in ["hnd", "diploma"]:
        return 0.7
    else:
        return 0.6


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of all score components."""
    skill_match_score: float
    domain_preference_score: float
    experience_fit_score: float
    career_goal_fit_score: float
    education_fit_score: float
    final_match_score: float
    readiness_score: float
    
    def to_dict(self) -> dict:
        return {
            "skill_match_score": round(self.skill_match_score, 3),
            "domain_preference_score": round(self.domain_preference_score, 3),
            "experience_fit_score": round(self.experience_fit_score, 3),
            "career_goal_fit_score": round(self.career_goal_fit_score, 3),
            "education_fit_score": round(self.education_fit_score, 3),
            "final_match_score": round(self.final_match_score, 3),
            "readiness_score": round(self.readiness_score, 3),
        }


def compute_final_score(
    skill_match_score: float,
    role_id: str,
    role_domain: Optional[str],
    preferred_domain: Optional[str],
    experience_level: Optional[str],
    career_goal: Optional[str],
    education_level: Optional[str],
    readiness_score: float = 0.5,
) -> ScoreBreakdown:
    """
    Compute the final weighted score for ranking.
    
    Args:
        skill_match_score: Raw cosine similarity (0-1)
        role_id: Role identifier for seniority detection
        role_domain: Domain of the role
        preferred_domain: User's preferred domain (or None)
        experience_level: User's experience level
        career_goal: User's career goal
        education_level: User's education level
        readiness_score: Pre-computed readiness from skill gap (0-1)
    
    Returns:
        ScoreBreakdown with all component scores and final score
    """
    # Compute component scores
    domain_score = compute_domain_preference_score(role_domain, preferred_domain)
    experience_score = compute_experience_fit_score(role_id, experience_level)
    career_goal_score = compute_career_goal_fit_score(role_id, career_goal, experience_level)
    education_score = compute_education_fit_score(education_level)
    
    # Choose weights based on whether domain preference is set
    has_domain_pref = preferred_domain and preferred_domain.strip() != ""
    weights = DEFAULT_WEIGHTS if has_domain_pref else NO_PREFERENCE_WEIGHTS
    
    # Compute weighted final score
    final_score = (
        weights["skill_match"] * skill_match_score +
        weights["domain_preference"] * domain_score +
        weights["experience_fit"] * experience_score +
        weights["career_goal_fit"] * career_goal_score +
        weights["education_fit"] * education_score
    )
    
    return ScoreBreakdown(
        skill_match_score=skill_match_score,
        domain_preference_score=domain_score,
        experience_fit_score=experience_score,
        career_goal_fit_score=career_goal_score,
        education_fit_score=education_score,
        final_match_score=final_score,
        readiness_score=readiness_score,
    )


def generate_ranking_explanation(
    score_breakdown: ScoreBreakdown,
    role_title: str,
    role_domain: Optional[str],
    preferred_domain: Optional[str],
    is_best_match: bool,
) -> dict:
    """
    Generate human-readable explanations for why a role is ranked where it is.
    
    Returns a dict with:
    - why_ranked_here: Brief explanation of ranking
    - why_best_match: Why this is (or isn't) best match
    - domain_impact: How domain preference affected score
    """
    explanations = {}
    
    # Domain impact explanation
    pref_normalized = normalize_domain(preferred_domain) if preferred_domain else None
    role_normalized = normalize_domain(role_domain) if role_domain else None
    
    if not pref_normalized:
        explanations["domain_impact"] = "No domain preference set - ranking based primarily on skill match."
    elif role_normalized == pref_normalized:
        explanations["domain_impact"] = f"✓ Exact match with your preferred domain ({role_domain})."
    elif role_normalized in RELATED_DOMAINS.get(pref_normalized, []):
        explanations["domain_impact"] = f"Related to your preferred domain ({preferred_domain}). Received moderate boost."
    else:
        explanations["domain_impact"] = f"Different from your preferred domain ({preferred_domain}). Other factors drove this ranking."
    
    # Ranking explanation
    if is_best_match:
        explanations["why_ranked_here"] = "Ranked #1 - Highest combined score across skills, domain fit, and career alignment."
        explanations["why_best_match"] = f"Best overall fit considering your {int(score_breakdown.skill_match_score*100)}% skill match and profile preferences."
    else:
        top_factor = "skill match"
        if score_breakdown.domain_preference_score >= 0.8:
            top_factor = "domain alignment"
        elif score_breakdown.experience_fit_score >= 0.9:
            top_factor = "experience fit"
        explanations["why_ranked_here"] = f"Strong {top_factor} but another role scored higher overall."
        explanations["why_best_match"] = None
    
    # Readiness explanation
    readiness_pct = int(score_breakdown.readiness_score * 100)
    if readiness_pct >= 70:
        explanations["why_readiness"] = f"High readiness ({readiness_pct}%) - You have most required skills."
    elif readiness_pct >= 50:
        explanations["why_readiness"] = f"Moderate readiness ({readiness_pct}%) - Some skill gaps to address."
    else:
        explanations["why_readiness"] = f"Lower readiness ({readiness_pct}%) - Focus on building key missing skills."
    
    return explanations
