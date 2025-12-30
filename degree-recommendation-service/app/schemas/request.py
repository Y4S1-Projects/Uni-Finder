# app/schemas/request.py
from typing import List
from pydantic import BaseModel, Field


class StudentRequest(BaseModel):
    stream: str
    subjects: List[str]
    zscore: float
    interests: str


class RecommendationRequest(BaseModel):
    student: StudentRequest
    district: str = Field(..., example="Colombo")
    max_results: int = Field(default=5, ge=1, le=20)
