# app/api/recommend.py
from fastapi import APIRouter

from app.schemas.request import (
    RecommendationRequest,
    InterestBasedRecommendationRequest,
)
from app.schemas.response import InterestRecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.services.interest_recommendation_service import InterestRecommendationService

router = APIRouter()
service = RecommendationService()
interest_service = InterestRecommendationService()


@router.post("/debug")
def recommend_debug(request: RecommendationRequest):
    return service.get_recommendations_debug(
        student_data=request.student.model_dump(),
        district=request.district,
        max_results=request.max_results,
        above_score_count=request.above_score_count,
    )


@router.post("")
def recommend(request: RecommendationRequest):
    return service.get_recommendations(
        student_data=request.student.model_dump(),
        district=request.district,
        max_results=request.max_results,
        above_score_count=request.above_score_count,
    )


@router.post("/interests")
def recommend_by_interests(
    request: InterestBasedRecommendationRequest,
) -> InterestRecommendationResponse:
    """
    Get course recommendations based on student interests using 3-step pipeline.

    **Pipeline Steps:**
    1. **Eligibility Filtering** - Validates courses from input list
    2. **Semantic Interest Matching** - Uses sentence embeddings for semantic similarity
    3. **Explainable AI** - Generates personalized explanations using Gemini API

    **Request:**
    - `student_input`: Description of student's interests, skills, and career goals (10-2000 chars)
    - `eligible_courses`: List of course codes from rules-based filtering
    - `max_results`: Maximum recommendations to return (default: 5)
    - `explain`: Enable/disable Gemini explanations (default: true)

    **Response:**
    - Ranked courses with match percentages, matched interests, and explanations
    - Includes job roles, industries, and core skills for each course
    - Optional program details (universities, duration, etc.)

    **Example Request:**
    ```json
    {
        "student_input": "I love data analysis, machine learning, and solving complex problems",
        "eligible_courses": ["19", "20", "41"],
        "max_results": 5,
        "explain": true
    }
    ```
    """
    # Validate input
    is_valid, error_msg = interest_service.validate_input(request.student_input)
    if not is_valid:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=error_msg)

    # Get recommendations
    recommendations = interest_service.get_interest_based_recommendations(
        student_input=request.student_input,
        eligible_course_codes=request.eligible_courses,
        max_results=request.max_results,
        explain=request.explain,
    )

    # Build response
    return InterestRecommendationResponse(
        student_input=request.student_input,
        eligible_courses_count=len(request.eligible_courses),
        recommendations=recommendations,
    )
