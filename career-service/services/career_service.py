"""Career ladder and skill gap detection services"""
from typing import Optional
from data_loader import DataStore
from .skill_service import get_skill_name


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
    missing_skill_ids = sorted(required_skills - user_skill_ids)
    matched_skill_ids = sorted(required_skills & user_skill_ids)
    readiness = (len(matched_skill_ids) / len(required_skills)) if required_skills else 0.0

    # Convert to objects with id and name
    missing_skills = [{"id": sid, "name": get_skill_name(sid)} for sid in missing_skill_ids]
    matched_skills = [{"id": sid, "name": get_skill_name(sid)} for sid in matched_skill_ids]

    return {
        "target_role": target_role_id,
        "readiness_score": round(readiness, 3),
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
    }


def get_next_role(domain: str, current_role: str, current_seniority: int = None) -> Optional[str]:
    """
    Get the next role in a career ladder with graceful fallback.
    
    Phase D improvements:
    - If role is not in ladder, attempts nearest-seniority placement
    - Ensures entry-level roles don't jump more than 2 seniority levels
    - Returns None gracefully instead of raising for missing roles
    
    Args:
        domain: Career domain (e.g., 'SOFTWARE_ENGINEERING')
        current_role: Current role ID
        current_seniority: Optional seniority level (1-7) for fallback placement
        
    Returns:
        Next role ID or None if at top of ladder or not found
    """
    ladder = DataStore.career_ladders.get(domain)
    if not ladder:
        # Try alternate domain lookup
        alt_domain = get_domain_for_role(current_role)
        if alt_domain and alt_domain != domain:
            ladder = DataStore.career_ladders.get(alt_domain)
        if not ladder:
            return None  # Graceful: no crash

    if current_role in ladder:
        idx = ladder.index(current_role)
        if idx + 1 >= len(ladder):
            return None  # At top of ladder
        return ladder[idx + 1]

    # Fallback: role not in ladder — try nearest placement by seniority
    if current_seniority is not None and len(ladder) > 0:
        # Approximate position: map seniority (1-7) to ladder index
        approx_idx = min(
            int((current_seniority - 1) / 7.0 * len(ladder)),
            len(ladder) - 1
        )
        # Next role is one above the approximate position
        next_idx = min(approx_idx + 1, len(ladder) - 1)
        if next_idx > approx_idx:
            return ladder[next_idx]
        return None  # Already at/near top

    return None


def get_domain_for_role(role_id: str) -> Optional[str]:
    """
    Find which domain a role belongs to.
    
    Phase D improvements:
    - First checks career_ladders
    - Falls back to role_metadata domain field
    - Falls back to role_id prefix pattern matching
    
    Args:
        role_id: The role ID to look up
        
    Returns:
        Domain name or None if not found
    """
    # Primary: check career ladders
    for domain, roles in DataStore.career_ladders.items():
        if role_id in roles:
            return domain

    # Fallback: check role_metadata if loaded
    if hasattr(DataStore, 'role_metadata') and DataStore.role_metadata:
        # role_metadata may be a list of dicts or a dict keyed by role_id
        if isinstance(DataStore.role_metadata, dict):
            meta = DataStore.role_metadata.get(role_id, {})
            if meta.get("domain"):
                return meta["domain"]
        elif isinstance(DataStore.role_metadata, list):
            for entry in DataStore.role_metadata:
                if isinstance(entry, dict) and entry.get("role_id") == role_id:
                    if entry.get("domain"):
                        return entry["domain"]
                    break

    # Fallback: check role_profiles_df for domain column
    if DataStore.role_profiles_df is not None and "domain" in DataStore.role_profiles_df.columns:
        role_rows = DataStore.role_profiles_df[DataStore.role_profiles_df["role_id"] == role_id]
        if not role_rows.empty:
            domain_val = role_rows.iloc[0].get("domain")
            if domain_val:
                return str(domain_val)

    # Fallback: infer from role_id prefix patterns
    rid_upper = role_id.upper()
    domain_prefixes = {
        "SE_": "SOFTWARE_ENGINEERING",
        "BE_": "BACKEND_ENGINEERING",
        "FE_": "FRONTEND_ENGINEERING",
        "FS_": "FULLSTACK_DEVELOPMENT",
        "DS_": "DATA_SCIENCE",
        "ML_": "AI_ML",
        "AI_": "AI_ML",
        "DE_": "DATA_ENGINEERING",
        "DO_": "DEVOPS",
        "CS_": "CYBERSECURITY",
        "QA_": "QA_TESTING",
        "GD_": "GAME_DEVELOPMENT",
        "MD_": "MOBILE_DEVELOPMENT",
        "PM_": "PROJECT_MANAGEMENT",
        "UI_": "UI_UX_DESIGN",
        "UX_": "UI_UX_DESIGN",
        "BA_": "BUSINESS_ANALYSIS",
        "CL_": "CLOUD_ENGINEERING",
        "BD_": "BLOCKCHAIN",
        "EM_": "EMBEDDED_SYSTEMS",
    }
    for prefix, domain in domain_prefixes.items():
        if rid_upper.startswith(prefix):
            return domain

    return None

import json
from typing import List, Set, Tuple

def get_career_ladder(domain: str) -> dict:
    """
    Load and return complete career ladder for a domain
    """
    from config import ML_DIR
    import os
    
    # Path to enhanced ladders
    enhanced_path = ML_DIR / 'career_path' / 'career_ladders_enhanced.json'
    
    with open(enhanced_path, 'r') as f:
        ladders = json.load(f)
    
    if domain not in ladders:
        raise ValueError(f"Domain {domain} not found")
    
    return ladders[domain]


def is_user_eligible_for_level(
    user_skill_ids: set,
    level_data: dict,
    min_match_threshold: float = 0.15,
    current_user_level: int = 1
) -> bool:
    """
    Check if user is eligible to see this career level
    
    Rules:
    1. Must have at least 15% skill match (matched_skills / required_skills)
    2. Can only view current level and next 3 levels (level_gap <= 3)
    3. Cannot view levels below current (level_gap >= 0)
    
    Returns True if eligible, False otherwise
    """
    target_level = level_data.get('level', 1)
    level_gap = target_level - current_user_level
    
    if level_gap < 0 or level_gap > 3:
        return False
        
    match_score = calculate_role_match(user_skill_ids, level_data.get('top_skills', []))
    if match_score < min_match_threshold:
        return False
        
    return True


def analyze_career_progression(
    user_skill_ids: List[str],
    current_role_id: str,
    target_domain: str,
    show_all_levels: bool = False
) -> dict:
    """
    Analyze user's progression path in a career ladder
    
    Args:
        user_skill_ids: User's skill IDs
        current_role_id: Current role ID (optional)
        target_domain: Target career domain
        show_all_levels: If True, returns ALL levels in the ladder (for network/ecosystem view)
                        If False, only returns eligible levels based on user's current position
    """
    ladder = get_career_ladder(target_domain)
    user_skills_set = set(user_skill_ids)
    
    # Find current position
    current_position = None
    current_level_num = 0
    
    for level in ladder['levels']:
        if level['role_id'] == current_role_id:
            current_position = level
            current_level_num = level['level']
            break
    
    # If not found, predict current level based on skills
    if not current_position:
        current_level_num, current_position = predict_current_level(user_skills_set, ladder)
    
    # Calculate readiness for levels
    eligible_levels = []
    
    for level in ladder['levels']:
        # Skip levels below current unless showing all
        if not show_all_levels and level['level'] < current_level_num:
            continue
        
        # Apply eligibility filter only when not showing all levels
        if not show_all_levels:
            if not is_user_eligible_for_level(user_skills_set, level, current_user_level=current_level_num):
                continue
        
        # Get skill gap
        try:
            gap_analysis = detect_skill_gap(
                user_skill_ids=user_skills_set,
                target_role_id=level['role_id'],
                importance_threshold=0.05
            )
            # detect_skill_gap returns dicts for matched/missing skills, extract IDs for frontend
            matched_skills = [s['id'] for s in gap_analysis['matched_skills']]
            missing_skills = [s['id'] for s in gap_analysis['missing_skills']]
            readiness_score = gap_analysis['readiness_score']
        except Exception as e:
            # target role might not be in role_profiles_df
            matched_skills = []
            missing_skills = []
            readiness_score = 0.0
        
        # Skip zero readiness only when filtering (not in show_all mode)
        if not show_all_levels and readiness_score <= 0:
            continue
            
        is_current = (level['level'] == current_level_num)
        
        # Calculate match_score separately (skill coverage ratio based on top skills)
        top_skills = set(level.get('top_skills', []))
        if top_skills:
            match_score = len(user_skills_set & top_skills) / len(top_skills)
        else:
            match_score = readiness_score  # Fallback to readiness if no top_skills
            
        eligible_levels.append({
            'level': level['level'],
            'role_id': level['role_id'],
            'role_title': level['role_title'],
            'experience_range': level.get('experience_range', ''),
            'readiness_score': readiness_score,
            'match_score': round(match_score, 3),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'is_current': is_current
        })
    
    return {
        'domain': target_domain,
        'current_position': {
            'level': current_level_num,
            'role_id': current_position['role_id'],
            'role_title': current_position['role_title']
        },
        'eligible_levels': eligible_levels,
        'total_levels_in_domain': len(ladder['levels'])
    }


def compare_career_paths(
    user_skill_ids: List[str],
    domains: List[str]
) -> dict:
    """
    Compare user's fit across multiple career domains
    """
    comparisons = []
    
    for domain in domains:
        try:
            ladder = get_career_ladder(domain)
            
            # Calculate best fit level in this domain
            best_level = None
            best_match = 0
            
            for level in ladder['levels']:
                match = calculate_role_match(set(user_skill_ids), level['top_skills'])
                if match >= best_match:
                    best_match = match
                    best_level = level
            
            if best_level:
                comparisons.append({
                    'domain': domain,
                    'domain_name': ladder['domain_name'],
                    'best_fit_level': best_level['level'],
                    'best_fit_role': best_level['role_title'],
                    'match_score': best_match,
                    'total_levels': len(ladder['levels']),
                    'jobs_available': ladder['total_jobs_in_domain']
                })
        except Exception as e:
            continue
    
    # Sort by match score
    comparisons.sort(key=lambda x: x['match_score'], reverse=True)
    
    return {
        'comparisons': comparisons,
        'recommended_domain': comparisons[0]['domain'] if comparisons else None
    }


def predict_current_level(user_skills: set, ladder: dict) -> Tuple[int, dict]:
    """
    Predict which level user is currently at based on skills
    """
    best_match = -1
    best_level = ladder['levels'][0]
    best_level_num = 1
    
    for level in ladder['levels']:
        match = calculate_role_match(user_skills, level['top_skills'])
        if match > best_match:
            best_match = match
            best_level = level
            best_level_num = level['level']
    
    return best_level_num, best_level


def calculate_role_match(user_skills: set, required_skills: list) -> float:
    """
    Calculate match percentage between user skills and role requirements
    """
    if not required_skills:
        return 0.0
    
    matched = len(user_skills.intersection(set(required_skills)))
    return matched / len(required_skills)


def get_difficulty_level(readiness_score: float) -> str:
    """
    Convert readiness score to difficulty label
    """
    if readiness_score >= 0.7:
        return "Easy"
    elif readiness_score >= 0.4:
        return "Medium"
    else:
        return "Hard"
