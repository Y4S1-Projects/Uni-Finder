# app/schemas/request.py
from typing import List, Optional
from pydantic import BaseModel, Field


class StudentRequest(BaseModel):
    stream: str
    subjects: List[str]
    # Optional: if omitted, the service will not filter by z-score cutoff.
    zscore: Optional[float] = Field(default=None, ge=-3, le=3)
    interests: str


class RecommendationRequest(BaseModel):
    student: StudentRequest
    district: str = Field(..., example="Colombo")
    # If omitted, return all eligible recommendations.
    max_results: Optional[int] = Field(default=None, ge=1)
