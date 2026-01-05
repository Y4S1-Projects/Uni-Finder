# app/schemas/response.py
from typing import List
from pydantic import BaseModel


class RecommendationItem(BaseModel):
    degree_name: str
    score: float
    similarity: float
    eligibility_reason: str


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
