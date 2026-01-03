"""Career ladder and skill gap detection services"""
from typing import Optional
from data_loader import DataStore


def detect_skill_gap(user_skill_ids: set, target_role_id: str, importance_threshold: float = 0.02) -> dict:
    """
    Detect the skill gap between user's skills and target role requirements.
    
    Args:
        user_skill_ids: Set of skill IDs the user possesses
        target_role_id: The target role to analyze
        importance_threshold: Minimum importance score for required skills
        
    Returns:
        Dictionary with readiness score, matched and missing skills
    """
    role_df = DataStore.role_profiles_df[DataStore.role_profiles_df["role_id"] == target_role_id]
    if role_df.empty:
        raise ValueError(f"No role profile found for role_id={target_role_id}")

    required_skills = set(role_df[role_df["importance"] >= importance_threshold]["skill_id"].astype(str))
    missing_skills = sorted(required_skills - user_skill_ids)
    matched_skills = sorted(required_skills & user_skill_ids)
    readiness = (len(matched_skills) / len(required_skills)) if required_skills else 0.0

    return {
        "target_role": target_role_id,
        "readiness_score": round(readiness, 3),
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
    }


def get_next_role(domain: str, current_role: str) -> Optional[str]:
    """
    Get the next role in a career ladder.
    
    Args:
        domain: Career domain (e.g., 'SOFTWARE_ENGINEERING')
        current_role: Current role ID
        
    Returns:
        Next role ID or None if at top of ladder
    """
    ladder = DataStore.career_ladders.get(domain)
    if not ladder:
        raise ValueError(f"Unknown career domain: {domain}")
    if current_role not in ladder:
        raise ValueError(f"{current_role} not found in career ladder for {domain}")
    idx = ladder.index(current_role)
    if idx + 1 >= len(ladder):
        return None
    return ladder[idx + 1]


def get_domain_for_role(role_id: str) -> Optional[str]:
    """
    Find which domain a role belongs to.
    
    Args:
        role_id: The role ID to look up
        
    Returns:
        Domain name or None if not found
    """
    for domain, roles in DataStore.career_ladders.items():
        if role_id in roles:
            return domain
    return None
