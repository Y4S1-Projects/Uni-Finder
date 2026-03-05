# app/services/recommendation_service.py
from typing import Dict, Optional
from fastapi import HTTPException

from app.domain.student import StudentProfile
from app.pipelines.recommendation_pipeline import RecommendationPipeline
from app.utils.validators import validate_student_profile


class RecommendationService:
    def __init__(self):
        self.pipeline = RecommendationPipeline()

    def get_recommendations(
        self,
        student_data: Dict,
        district: str,
        max_results: Optional[int],
        above_score_count: int = 0,
    ):
        # Validate student profile
        is_valid, error_msg = validate_student_profile(
            student_data["stream"], student_data["subjects"], student_data.get("zscore")
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        student = StudentProfile(
            stream=student_data["stream"],
            subjects=student_data["subjects"],
            zscore=student_data.get("zscore"),
            interests=student_data["interests"],
        )

        return self.pipeline.recommend(
            student=student,
            district=district,
            max_results=max_results,
            above_score_count=above_score_count,
        )

    def get_recommendations_debug(
        self,
        student_data: Dict,
        district: str,
        max_results: Optional[int],
        above_score_count: int = 0,
    ):
        # Validate student profile
        is_valid, error_msg = validate_student_profile(
            student_data["stream"], student_data["subjects"], student_data.get("zscore")
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        student = StudentProfile(
            stream=student_data["stream"],
            subjects=student_data["subjects"],
            zscore=student_data.get("zscore"),
            interests=student_data["interests"],
        )

        return self.pipeline.recommend_debug(
            student=student,
            district=district,
            max_results=max_results,
            above_score_count=above_score_count,
        )
