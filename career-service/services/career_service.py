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


def analyze_career_progression(
    user_skill_ids: List[str],
    current_role_id: str,
    target_domain: str
) -> dict:
    """
    Analyze user's progression path in a career ladder
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
    
    # Calculate readiness for next levels
    progression_path = []
    
    for level in ladder['levels']:
        if level['level'] <= current_level_num:
            continue
        
        if level['level'] > current_level_num + 3:
            break  # Only show next 3 levels
        
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
            
        progression_path.append({
            'level': level['level'],
            'role_id': level['role_id'],
            'role_title': level['role_title'],
            'experience_range': level['experience_range'],
            'readiness_score': readiness_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_skills_required': len(level['top_skills']),
            'estimated_time': f"{(level['level'] - current_level_num) * 12}-{(level['level'] - current_level_num) * 18} months",
            'difficulty': get_difficulty_level(readiness_score)
        })
    
    return {
        'domain': target_domain,
        'current_position': {
            'level': current_level_num,
            'role_id': current_position['role_id'],
            'role_title': current_position['role_title'],
            'match_score': calculate_role_match(user_skills_set, current_position['top_skills'])
        },
        'progression_path': progression_path,
        'alternate_paths': ladder.get('alternate_paths', []),
        'total_levels': len(ladder['levels'])
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
