"""Career recommendation service using cosine similarity"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from data_loader import DataStore
from .career_service import detect_skill_gap, get_next_role, get_domain_for_role


def build_user_vector(user_skill_ids: set, skill_columns: pd.Index) -> np.ndarray:
    """
    Convert user's skill IDs into a vector aligned with role_skill_matrix columns.
    
    Args:
        user_skill_ids: Set of skill IDs the user possesses
        skill_columns: Index of skill columns from role_skill_matrix
        
    Returns:
        Numpy array representing user's skill vector
    """
    vector = np.zeros(len(skill_columns))
    skill_index = {skill: idx for idx, skill in enumerate(skill_columns)}
    
    for skill_id in user_skill_ids:
        if skill_id in skill_index:
            vector[skill_index[skill_id]] = 1.0
    
    return vector.reshape(1, -1)


def recommend_careers_for_user(user_skill_ids: list, top_n: int = 5) -> dict:
    """
    Recommend best-fit career roles based on cosine similarity.
    
    Args:
        user_skill_ids: List of skill IDs the user possesses
        top_n: Number of recommendations to return
        
    Returns:
        Dictionary with recommendations and analysis details
    """
    if DataStore.role_skill_matrix.empty:
        raise ValueError("Role skill matrix not loaded")
    
    if not user_skill_ids:
        raise ValueError("No skills provided")
    
    # Normalize user skills to uppercase (matching role_profiles format)
    user_skills_upper = set(s.strip().upper() for s in user_skill_ids if s)
    
    # Build user vector aligned with role_skill_matrix columns
    user_vector = build_user_vector(user_skills_upper, DataStore.role_skill_matrix.columns)
    
    # Calculate cosine similarity between user and all roles
    role_vectors = DataStore.role_skill_matrix.values
    similarity_scores = cosine_similarity(user_vector, role_vectors)[0]
    
    # Create recommendations dataframe
    recommendations = pd.DataFrame({
        "role_id": DataStore.role_skill_matrix.index,
        "match_score": similarity_scores
    }).sort_values("match_score", ascending=False)
    
    # Get top N recommendations
    top_recommendations = recommendations.head(top_n)
    
    # Build detailed response
    results = []
    for _, row in top_recommendations.iterrows():
        role_id = row["role_id"]
        match_score = round(float(row["match_score"]), 3)
        
        # Get role title
        role_title = DataStore.role_id_to_title.get(role_id, role_id)
        
        # Get domain
        domain = get_domain_for_role(role_id)
        
        # Get next role in career path
        next_role = None
        next_role_title = None
        if domain:
            try:
                next_role = get_next_role(domain, role_id)
                if next_role:
                    next_role_title = DataStore.role_id_to_title.get(next_role, next_role)
            except ValueError:
                pass
        
        # Get skill gap for this role
        try:
            skill_gap = detect_skill_gap(user_skills_upper, role_id, importance_threshold=0.02)
        except Exception:
            skill_gap = None
        
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
        "total_roles_compared": len(DataStore.role_skill_matrix),
    }
