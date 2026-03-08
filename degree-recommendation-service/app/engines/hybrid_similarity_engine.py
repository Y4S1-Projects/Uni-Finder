"""
Hybrid Search Engine - Dense (Semantic) + Sparse (TF-IDF) Scoring
Combines SentenceTransformers semantic understanding with traditional keyword matching
for improved ranking quality.
"""

import logging
from typing import List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity

from app.core.config import settings
from app.domain.course_recommendation import CourseRecommendation
from app.engines.career_mapper import CareerMapper


class HybridSimilarityEngine:
    """
    Hybrid retrieval engine combining:
    1. Dense vectors (SentenceTransformers) for semantic understanding
    2. Sparse vectors (TF-IDF) for exact keyword matching
    3. Career mapping layer for query expansion
    """

    def __init__(
        self,
        semantic_weight: float = 0.7,
        tfidf_weight: float = 0.3,
        use_career_mapping: bool = True,
    ):
        """
        Initialize hybrid engine.

        Args:
            semantic_weight: Weight for semantic similarity score (0-1)
            tfidf_weight: Weight for TF-IDF score (0-1)
            use_career_mapping: Whether to apply career expansion to queries
        """
        if abs(semantic_weight + tfidf_weight - 1.0) > 0.001:
            raise ValueError("Semantic and TF-IDF weights must sum to 1.0")

        self.semantic_weight = semantic_weight
        self.tfidf_weight = tfidf_weight
        self.use_career_mapping = use_career_mapping

        # Initialize components
        self.model = _get_model(settings.EMBEDDING_MODEL_NAME)
        self.career_mapper = CareerMapper() if use_career_mapping else None

        # TF-IDF components (initialized when courses are indexed)
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_course_vectors: Optional[np.ndarray] = None
        self.indexed_courses: List[CourseRecommendation] = []

    def index_courses(self, courses: List[CourseRecommendation]) -> None:
        """
        Build TF-IDF index for courses.
        Must be called before ranking queries.

        Args:
            courses: List of courses to index
        """
        self.indexed_courses = courses

        # Get weighted text corpus for each course
        course_texts = [course.get_weighted_text() for course in courses]

        # Build TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words="english",
            sublinear_tf=True,  # Use log(tf) instead of raw tf
        )

        # Fit and transform course texts
        self.tfidf_course_vectors = self.tfidf_vectorizer.fit_transform(course_texts)

        print(f"[OK] Indexed {len(courses)} courses with hybrid search")

    def encode_text(self, text: str) -> np.ndarray:
        """Encode text using SentenceTransformer model."""
        return self.model.encode(text, normalize_embeddings=True)

    def compute_semantic_similarity(
        self,
        student_vec: np.ndarray,
        course_vec: np.ndarray,
    ) -> float:
        """Compute cosine similarity between normalized vectors."""
        if student_vec is None or course_vec is None:
            return 0.0
        return float(np.dot(student_vec, course_vec))

    def compute_tfidf_similarity(self, query: str) -> np.ndarray:
        """
        Compute TF-IDF similarity scores for query against all indexed courses.

        Args:
            query: Student query text

        Returns:
            Array of similarity scores (one per course)
        """
        if self.tfidf_vectorizer is None or self.tfidf_course_vectors is None:
            raise RuntimeError(
                "Courses must be indexed before computing TF-IDF similarity"
            )

        # Transform query using fitted vectorizer
        query_vec = self.tfidf_vectorizer.transform([query])

        # Compute cosine similarity
        similarities = sklearn_cosine_similarity(query_vec, self.tfidf_course_vectors)

        return similarities.flatten()

    def rank_courses_by_interest(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
        return_scores: bool = False,
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Rank courses using hybrid scoring (semantic + TF-IDF).

        Args:
            student_input: Student's interests/skills description
            courses: List of CourseRecommendation objects to rank
            return_scores: If True, returns (semantic, tfidf, hybrid) score tuples

        Returns:
            Sorted list of (CourseRecommendation, hybrid_score) tuples
        """
        # Phase 1: Career mapping (query expansion)
        expanded_query = student_input
        if self.use_career_mapping and self.career_mapper:
            expanded_query = self.career_mapper.expand_query(student_input)
            # Log expansion for debugging
            if expanded_query != student_input:
                added_terms = expanded_query[len(student_input) :]
                logger.info(f"[OK] Query expanded with: {added_terms[:100]}...")

        # Check if we need to re-index (different course set)
        course_codes = [c.course_code for c in courses]
        indexed_codes = [c.course_code for c in self.indexed_courses]

        needs_reindex = (
            not self.indexed_courses
            or self.tfidf_vectorizer is None
            or len(course_codes) != len(indexed_codes)
            or set(course_codes) != set(indexed_codes)
        )

        if needs_reindex:
            self.index_courses(courses)

        # Phase 2a: Compute semantic similarities
        student_vec = self.encode_text(expanded_query)
        semantic_scores = []

        for course in courses:
            # Use weighted text for semantic encoding too
            course_text = course.get_weighted_text()
            course_vec = self.encode_text(course_text)
            semantic_sim = self.compute_semantic_similarity(student_vec, course_vec)
            semantic_scores.append(semantic_sim)

        semantic_scores = np.array(semantic_scores)

        # Phase 2b: Compute TF-IDF similarities
        tfidf_scores = self.compute_tfidf_similarity(expanded_query)

        # Phase 3: Combine scores (weighted average)
        hybrid_scores = (
            self.semantic_weight * semantic_scores + self.tfidf_weight * tfidf_scores
        )

        # Build result tuples
        if return_scores:
            # For debugging: return all three scores
            results = [
                (course, (semantic, tfidf, hybrid))
                for course, semantic, tfidf, hybrid in zip(
                    courses, semantic_scores, tfidf_scores, hybrid_scores
                )
            ]
        else:
            results = [
                (course, float(hybrid))
                for course, hybrid in zip(courses, hybrid_scores)
            ]

        # Sort by hybrid score (descending)
        ranked = sorted(
            results, key=lambda x: x[1] if not return_scores else x[1][2], reverse=True
        )

        return ranked

    def filter_courses_by_similarity(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
        threshold: float = 0.3,
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Filter courses based on hybrid similarity threshold.

        Args:
            student_input: Student's interests/skills description
            courses: List of CourseRecommendation objects
            threshold: Minimum hybrid score to include (0-1)

        Returns:
            Filtered and sorted list of (CourseRecommendation, hybrid_score) tuples
        """
        ranked = self.rank_courses_by_interest(student_input, courses)
        return [item for item in ranked if item[1] >= threshold]

    def get_ranking_explanation(
        self,
        student_input: str,
        course: CourseRecommendation,
    ) -> dict:
        """
        Get detailed scoring breakdown for a specific course.
        Useful for debugging and explainability.

        Args:
            student_input: Student's query
            course: Course to explain

        Returns:
            Dictionary with scoring details
        """
        # Expand query
        expanded_query = student_input
        if self.use_career_mapping and self.career_mapper:
            expanded_query = self.career_mapper.expand_query(student_input)

        # Compute individual scores
        student_vec = self.encode_text(expanded_query)
        course_vec = self.encode_text(course.get_weighted_text())
        semantic_score = self.compute_semantic_similarity(student_vec, course_vec)

        # TF-IDF (need to index single course)
        if self.tfidf_vectorizer is None:
            self.index_courses([course])
        tfidf_scores = self.compute_tfidf_similarity(expanded_query)
        tfidf_score = float(tfidf_scores[0])

        hybrid_score = (
            self.semantic_weight * semantic_score + self.tfidf_weight * tfidf_score
        )

        return {
            "original_query": student_input,
            "expanded_query": expanded_query,
            "course": course.course_name,
            "semantic_score": float(semantic_score),
            "tfidf_score": float(tfidf_score),
            "hybrid_score": float(hybrid_score),
            "weights": {
                "semantic": self.semantic_weight,
                "tfidf": self.tfidf_weight,
            },
            "career_keywords": (
                self.career_mapper.get_career_keywords(student_input)
                if self.career_mapper
                else []
            ),
        }


# Model cache (shared with existing SimilarityEngine)
_MODEL_CACHE: dict[str, SentenceTransformer] = {}


def _get_model(model_name: str) -> SentenceTransformer:
    """Get cached SentenceTransformer model."""
    model = _MODEL_CACHE.get(model_name)
    if model is None:
        model = SentenceTransformer(model_name)
        _MODEL_CACHE[model_name] = model
    return model
