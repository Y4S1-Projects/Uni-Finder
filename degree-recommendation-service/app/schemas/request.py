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
        valid_streams = [
            "Physical Science",
            "Biological Science",
            "Commerce",
            "Engineering Technology",
            "Bio-Systems Technology",
            "Arts",
            "Science",  # backward compatibility alias
            "Technology",  # backward compatibility alias
        ]
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


class InterestBasedRecommendationRequest(BaseModel):
    """Request model for interest-based course recommendation with 3-step pipeline."""

    student_input: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        example="I love working with data, solving complex problems, and developing software applications. I'm interested in machine learning and artificial intelligence.",
        description="Student's interests, skills, and career goals",
    )
    eligible_courses: List[str] = Field(
        ...,
        example=["19", "20", "41", "21"],
        description="List of course codes eligible from rules-based filtering",
    )
    max_results: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of recommendations to return",
    )
    explain: bool = Field(
        default=True,
        description="Whether to generate personalized explanations using Gemini API",
    )


class OLPathwayRequest(BaseModel):
    """Request model for O/L to A/L stream pathway recommendation."""

    student_input: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        example="I want to become a software engineer and work with computers",
        description="Student's interests, career goals, or job roles",
    )
    ol_marks: dict[str, str] = Field(
        ...,
        example={
            "Mathematics": "A",
            "Science": "B",
            "English": "B",
            "First Language": "A",
            "History": "C",
        },
        description="O/L subject marks (subject name to grade mapping). Valid grades: A, B, C, S, W, F",
    )
    max_degree_results: Optional[int] = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of target degrees to show",
    )
    explain: bool = Field(
        default=True,
        description="Whether to generate personalized explanations using Gemini API",
    )

    @field_validator("ol_marks")
    @classmethod
    def validate_ol_marks(cls, v):
        """Validate O/L marks are valid grades."""
        valid_grades = {"A", "B", "C", "S", "W", "F"}
        for subject, grade in v.items():
            if grade.upper() not in valid_grades:
                raise ValueError(
                    f"Invalid grade '{grade}' for subject '{subject}'. Valid grades: A, B, C, S, W, F"
                )
        return {k: v.upper() for k, v in v.items()}
