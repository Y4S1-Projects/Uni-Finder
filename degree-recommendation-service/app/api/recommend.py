# app/api/recommend.py
from fastapi import APIRouter

from app.schemas.request import RecommendationRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter()
service = RecommendationService()


@router.post("/debug")
def recommend_debug(request: RecommendationRequest):
    return service.get_recommendations_debug(
        student_data=request.student.model_dump(),
        district=request.district,
        max_results=request.max_results,
    )


@router.post("")
def recommend(request: RecommendationRequest):
    return service.get_recommendations(
        student_data=request.student.model_dump(),
        district=request.district,
        max_results=request.max_results,
    )
