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


class OLPathwayDegree(BaseModel):
    """Individual degree within a stream pathway."""

    course_code: str
    course_name: str
    universities: List[str]
    match_score_percentage: float


class OLStreamPathway(BaseModel):
    """A single A/L stream pathway with degrees and careers."""

    stream_name: str
    ol_readiness: str  # e.g., "On Track (Maths: A, Science: B)"
    readiness_status: str  # "excellent", "good", "needs_improvement"
    match_score: float  # Average match score for this stream
    potential_degrees: List[OLPathwayDegree]
    target_careers: List[str]  # Top career paths for this stream


class OLCareerTreeResponse(BaseModel):
    """Hierarchical career tree response for O/L students."""

    student_goal: str  # Their interest/aspiration
    pathways: List[OLStreamPathway]  # Stream-grouped pathways
    ai_counselor_advice: str  # Overall guidance
    total_streams: int
    total_degrees: int


class SubjectAnalysis(BaseModel):
    """Analysis of a single O/L subject."""

    subject: str
    student_grade: str
    required_grade: Optional[str] = None
    ideal_grade: Optional[str] = None
    meets_requirement: bool
    status: str  # "excellent", "good", "adequate", "needs_improvement", "critical"
    feedback: str


class TargetDegree(BaseModel):
    """Target degree information with match score."""

    course_code: str
    course_name: str
    stream: str
    match_score_percentage: float
    job_roles: List[str]
    industries: List[str]


class OLPathwayResponse(BaseModel):
    """Response model for O/L to A/L stream pathway recommendation."""

    student_input: str
    recommended_al_stream: str
    stream_description: str
    stream_match_confidence: float  # 0-100 percentage
    target_degrees: List[TargetDegree]
    subject_analysis: List[SubjectAnalysis]
    overall_readiness: str  # "excellent", "good", "adequate", "needs_improvement"
    explanation: str
    action_plan: List[str]
    pipeline_steps: Optional[dict] = {
        "step_1": "Semantic Career/Interest Matching",
        "step_2": "A/L Stream Extraction",
        "step_3": "O/L Marks Analysis",
        "step_4": "Explainable AI Guidance",
    }
