# app/schemas/response.py
from typing import List, Optional
from pydantic import BaseModel


class RecommendationItem(BaseModel):
    degree_name: str
    score: float
    similarity: float
    eligibility_reason: str


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]


class InterestBasedRecommendationItem(BaseModel):
    """Response model for interest-based course recommendation with explanations."""

    course_code: str
    course_name: str
    stream: str
    match_score_percentage: float
    matched_interests: List[str]
    job_roles: List[str]
    industries: List[str]
    core_skills: List[str]
    explanation: str
    universities: Optional[List[str]] = None
    duration: Optional[str] = None
    degree_programme: Optional[str] = None
    medium_of_instruction: Optional[str] = None


class InterestRecommendationResponse(BaseModel):
    """Response model for 3-step interest-based recommendation pipeline."""

    student_input: str
    eligible_courses_count: int
    recommendations: List[InterestBasedRecommendationItem]
    pipeline_steps: Optional[dict] = {
        "step_1": "Eligibility Filtering",
        "step_2": "Semantic Interest Matching",
        "step_3": "Explainable AI (Gemini)",
    }
