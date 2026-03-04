# app/schemas/request.py
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class StudentRequest(BaseModel):
    stream: str
    subjects: List[str]
    # Optional: if omitted, the service will not filter by z-score cutoff.
    zscore: Optional[float] = Field(default=None, ge=-3, le=3)
    interests: str

    @field_validator("stream")
    @classmethod
    def validate_stream(cls, v):
        valid_streams = ["Science", "Arts", "Commerce", "Technology"]
        if v not in valid_streams:
            raise ValueError(f"Stream must be one of: {', '.join(valid_streams)}")
        return v


class RecommendationRequest(BaseModel):
    student: StudentRequest
    district: str = Field(..., example="Colombo")
    # If omitted, return all eligible recommendations.
    max_results: Optional[int] = Field(default=None, ge=1)
    # Number of courses to show above student's z-score (for aspirational viewing)
    above_score_count: Optional[int] = Field(
        default=0,
        ge=0,
        le=50,
        description="Number of courses above student's z-score to include",
    )
