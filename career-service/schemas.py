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
