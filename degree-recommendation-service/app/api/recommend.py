# app/api/recommend.py
from fastapi import APIRouter, HTTPException

from app.schemas.request import (
    RecommendationRequest,
    InterestBasedRecommendationRequest,
    OLPathwayRequest,
)
from app.schemas.response import (
    InterestRecommendationResponse,
    OLPathwayResponse,
)
from app.services.recommendation_service import RecommendationService
from app.services.interest_recommendation_service import InterestRecommendationService
from app.services.ol_pathway_service import OLPathwayService

# Initialize services
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine

router = APIRouter()
service = RecommendationService()
interest_service = InterestRecommendationService()

# Initialize O/L pathway service
course_repo = CourseRecommendationRepository()
similarity_engine = SimilarityEngine()
explanation_engine = ExplanationEngine()
ol_pathway_service = OLPathwayService(
    course_repo, similarity_engine, explanation_engine
)


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


@router.post("/ol-pathway")
def recommend_ol_pathway(request: OLPathwayRequest) -> OLPathwayResponse:
    """
    Get O/L to A/L stream pathway recommendation with target degrees and mark analysis.

    **For O/L students seeking guidance on:**
    - Which A/L stream to choose
    - Target university degrees aligned with their interests
    - Whether their O/L marks are sufficient
    - How to prepare for their chosen A/L stream

    **Pipeline Steps:**
    1. **Semantic Career/Interest Matching** - Finds target degrees using NLP
    2. **A/L Stream Extraction** - Identifies required A/L stream
    3. **O/L Marks Analysis** - Compares marks against stream requirements
    4. **Explainable AI Guidance** - Generates personalized action plan

    **Request:**
    - `student_input`: Student's interests, career goals, or job roles (10-2000 chars)
    - `ol_marks`: Dictionary of O/L subject marks (e.g., {"Mathematics": "A", "Science": "B"})
    - `max_degree_results`: Number of target degrees to show (default: 5)
    - `explain`: Enable/disable Gemini explanations (default: true)

    **Valid Grades:** A, B, C, S, W, F

    **Response:**
    - Recommended A/L stream with confidence percentage
    - Target degrees ranked by match score
    - Subject-by-subject analysis (strengths/weaknesses)
    - Overall readiness assessment
    - Personalized explanation and action plan

    **Example Request:**
    ```json
    {
        "student_input": "I want to become a software engineer and work with computers",
        "ol_marks": {
            "Mathematics": "A",
            "Science": "B",
            "English": "B",
            "First Language": "A",
            "History": "C"
        },
        "max_degree_results": 5,
        "explain": true
    }
    ```

    **Example Response:**
    ```json
    {
        "recommended_al_stream": "Physical Science",
        "stream_match_confidence": 85.5,
        "target_degrees": [
            {
                "course_name": "Computer Science",
                "match_score_percentage": 87.3,
                "job_roles": ["Software Engineer", "Data Scientist"]
            }
        ],
        "subject_analysis": [
            {
                "subject": "Mathematics",
                "student_grade": "A",
                "status": "excellent",
                "feedback": "Outstanding! Your Mathematics grade is at the ideal level."
            }
        ],
        "overall_readiness": "excellent",
        "explanation": "Based on your passion for software engineering...",
        "action_plan": [
            "Continue excelling in Mathematics",
            "Research A/L Combined Maths syllabus"
        ]
    }
    ```
    """
    try:
        # Get pathway recommendation
        response = ol_pathway_service.get_ol_pathway_recommendation(request)
        return response
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}. Please ensure ol_stream_rules.json exists.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating O/L pathway recommendation: {str(e)}",
        )
