# app/services/recommendation_service.py
from typing import Dict

from app.domain.student import StudentProfile
from app.pipelines.recommendation_pipeline import RecommendationPipeline


class RecommendationService:
    def __init__(self):
        self.pipeline = RecommendationPipeline()

    def get_recommendations(
        self,
        student_data: Dict,
        district: str,
        max_results: int,
    ):
        student = StudentProfile(
            stream=student_data["stream"],
            subjects=student_data["subjects"],
            zscore=student_data["zscore"],
            interests=student_data["interests"],
        )

        return self.pipeline.recommend(
            student=student,
            district=district,
            max_results=max_results,
        )

    def get_recommendations_debug(
        self,
        student_data: Dict,
        district: str,
        max_results: int,
    ):
        student = StudentProfile(
            stream=student_data["stream"],
            subjects=student_data["subjects"],
            zscore=student_data["zscore"],
            interests=student_data["interests"],
        )

        return self.pipeline.recommend_debug(
            student=student,
            district=district,
            max_results=max_results,
        )
