"""Pydantic models for request/response schemas"""
from pydantic import BaseModel
from typing import List, Optional


class SimulateRequest(BaseModel):
    domain: str
    current_role: str
    user_skill_ids: List[str]
    importance_threshold: Optional[float] = 0.02


class PredictRoleRequest(BaseModel):
    user_skill_ids: List[str]


class RecommendRequest(BaseModel):
    user_skill_ids: List[str]
    top_n: Optional[int] = 5
    # Enhanced profile fields (optional for backward compatibility)
    experience_level: Optional[str] = None   # "student", "0-1", "1-3", "3-5", "5+"
    current_status: Optional[str] = None     # "student", "graduate", "working"
    education_level: Optional[str] = None    # "al", "diploma", "hnd", "bachelors", "masters"
    career_goal: Optional[str] = None        # "first_job", "switch_career", "get_promoted"
    preferred_domain: Optional[str] = None   # "software_engineering", "data", "ai_ml", etc.
    preferred_job_type: Optional[str] = None # "full_time", "part_time", etc.


class ExplainRequest(BaseModel):
    role_id: str
    role_title: str
    domain: Optional[str] = None
    match_score: float
    user_skill_ids: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    readiness_score: float
    next_role: Optional[str] = None
    next_role_title: Optional[str] = None
    # Profile context for personalized explanations
    score_breakdown: Optional[dict] = None
    explanations: Optional[dict] = None
    experience_level: Optional[str] = None
    current_status: Optional[str] = None
    education_level: Optional[str] = None
    career_goal: Optional[str] = None
    preferred_domain: Optional[str] = None
    # Phase D additions
    seniority: Optional[int] = None
    ladder_position: Optional[int] = None
    ladder_length: Optional[int] = None
    confidence_score: Optional[float] = None
    matched_core_skills: Optional[List[dict]] = None
    matched_supporting_skills: Optional[List[dict]] = None
    missing_critical_skills: Optional[List[dict]] = None
    is_best_match: Optional[bool] = None
    profile_source: Optional[str] = None
