# app/engines/similarity_engine.py
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.math_utils import cosine_similarity
from app.domain.course_recommendation import CourseRecommendation


class SimilarityEngine:
    def __init__(self):
        self.model = _get_model(settings.EMBEDDING_MODEL_NAME)

    def encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)

    def compute_similarity_vectors(
        self,
        student_vec: np.ndarray,
        program_vec: np.ndarray,
    ) -> float:
        # When embeddings are normalized, cosine similarity == dot product.
        if student_vec is None or program_vec is None:
            return 0.0
        return float(np.dot(student_vec, program_vec))

    def compute_similarity(self, student_interests: str, program_text: str) -> float:
        student_vec = self.encode_text(student_interests)
        program_vec = self.encode_text(program_text)

        return cosine_similarity(student_vec, program_vec)

    def rank_courses_by_interest(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Rank courses based on semantic similarity to student interests.

        Args:
            student_input: Student's interests/skills description
            courses: List of CourseRecommendation objects to rank

        Returns:
            Sorted list of (CourseRecommendation, similarity_score) tuples
        """
        # Encode student input once
        student_vec = self.encode_text(student_input)

        # Calculate similarity for each course
        scores = []
        for course in courses:
            # Combine all course metadata for better semantic matching
            course_text = course.get_combined_text()
            course_vec = self.encode_text(course_text)

            # Calculate cosine similarity
            similarity = self.compute_similarity_vectors(student_vec, course_vec)
            scores.append((course, similarity))

        # Sort by similarity score (descending)
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)
        return ranked

    def filter_courses_by_similarity(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
        threshold: float = 0.3,
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Filter courses based on similarity threshold.

        Args:
            student_input: Student's interests/skills description
            courses: List of CourseRecommendation objects
            threshold: Minimum similarity score to include (0-1)

        Returns:
            Filtered and sorted list of (CourseRecommendation, similarity_score) tuples
        """
        ranked = self.rank_courses_by_interest(student_input, courses)
        return [item for item in ranked if item[1] >= threshold]


_MODEL_CACHE: dict[str, SentenceTransformer] = {}


def _get_model(model_name: str) -> SentenceTransformer:
    model = _MODEL_CACHE.get(model_name)
    if model is None:
        model = SentenceTransformer(model_name)
        _MODEL_CACHE[model_name] = model
    return model
