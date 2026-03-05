"""Role prediction service using decision tree classifier"""
import numpy as np
from data_loader import DataStore
from .career_service import detect_skill_gap, get_next_role, get_domain_for_role


def predict_user_role(user_skill_ids: list) -> dict:
    """
    Predict the user's current role based on their skills using the decision tree model.
    
    Args:
        user_skill_ids: List of skill IDs the user possesses
        
    Returns:
        Dictionary with predicted role, confidence, and career path info
    """
    if DataStore.role_classifier is None:
        raise ValueError("Role classifier model not loaded")
    
    if not DataStore.skill_columns:
        raise ValueError("Skill columns not initialized")
    
    if not user_skill_ids:
        raise ValueError("No skills provided")
    
    # Create a feature vector with all skills set to 0
    feature_vector = np.zeros(len(DataStore.skill_columns))
    
    # Set 1 for skills the user has
    # Skills come as SK001, SK002, etc. - convert to skill_sk001, skill_sk002
    user_skills_lower = set(s.strip().lower() for s in user_skill_ids if s)
    
    for i, col in enumerate(DataStore.skill_columns):
        # col is like "skill_sk001", extract "sk001" and check
        skill_id = col.replace("skill_", "")  # "sk001"
        if skill_id in user_skills_lower:
            feature_vector[i] = 1
    
    # Predict the role
    predicted_role = DataStore.role_classifier.predict([feature_vector])[0]
    
    # Get prediction probabilities if available
    try:
        probabilities = DataStore.role_classifier.predict_proba([feature_vector])[0]
        max_prob = float(max(probabilities))
        confidence = round(max_prob, 3)
    except Exception:
        confidence = None
    
    # Get the role title
    role_title = DataStore.role_id_to_title.get(predicted_role, predicted_role)
    
    # Determine the domain
    domain = get_domain_for_role(predicted_role)
    
    # Get next role in career ladder
    next_role = None
    next_role_title = None
    if domain:
        try:
            next_role = get_next_role(domain, predicted_role)
            if next_role:
                next_role_title = DataStore.role_id_to_title.get(next_role, next_role)
        except ValueError:
            pass
    
    # Get skill gap for next role if available
    skill_gap = None
    if next_role:
        try:
            user_skills_upper = set(s.strip().upper() for s in user_skill_ids if s)
            skill_gap = detect_skill_gap(user_skills_upper, next_role)
        except Exception:
            pass
    
    return {
        "predicted_role": predicted_role,
        "predicted_role_title": role_title,
        "confidence": confidence,
        "domain": domain,
        "next_role": next_role,
        "next_role_title": next_role_title,
        "skill_gap": skill_gap,
        "skills_used": list(user_skills_lower),
    }
