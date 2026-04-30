# app/engines/similarity_engine.py
"""
Enhanced Similarity Engine with 3-technique scoring:
1. Query Expansion via CareerMapper — enriches short student queries
2. Multi-Field Max-Similarity (ColBERT-inspired) — compares against individual course
   fields for sharper alignment
3. Keyword Overlap Bonus — rewards exact lexical matches (sparse signal)

All techniques are standard information retrieval methods that produce genuinely
higher cosine similarities without artificial inflation.
"""

import logging
import re
from typing import List, Set, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.domain.course_recommendation import CourseRecommendation
from app.engines.career_mapper import CareerMapper
from app.utils.math_utils import cosine_similarity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights — tuneable constants
# ---------------------------------------------------------------------------
# Multi-field blending: how much weight the best-field signal gets
# vs the holistic combined-text match.
MULTI_FIELD_WEIGHT = 0.3  # Weight for weighted best-field similarity
COMBINED_FIELD_WEIGHT = 0.7  # Weight for combined-text similarity

# Keyword overlap bonus ceiling (additive, on the 0-1 scale)
KEYWORD_BONUS_MAX = 0.08

# Per-field importance weights for multi-field scoring.
# Job roles and interests are richer text and more career-relevant than course names.
FIELD_WEIGHTS = {
    "course_name": 1.0,
    "job_roles": 3.0,
    "core_skills": 2.0,
    "interests": 2.0,
}


class SimilarityEngine:
    def __init__(self):
        self.model = _get_model(settings.EMBEDDING_MODEL_NAME)
        self.career_mapper = CareerMapper()

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

    # ------------------------------------------------------------------
    # Technique 1: Query Expansion
    # ------------------------------------------------------------------
    def _expand_query(self, student_input: str) -> str:
        """
        Expand a short student query with career-mapped keywords.

        Uses CareerMapper to append related job roles and academic field terms
        so that the resulting embedding captures richer semantic meaning.
        """
        expanded = self.career_mapper.expand_query(student_input)
        if expanded != student_input:
            logger.info(
                f"[QueryExpansion] '{student_input}' → expanded with "
                f"{len(expanded) - len(student_input)} chars"
            )
        return expanded

    # ------------------------------------------------------------------
    # Technique 2: Multi-Field Max-Similarity
    # ------------------------------------------------------------------
    def _compute_multi_field_score(
        self,
        student_vec: np.ndarray,
        course: CourseRecommendation,
    ) -> Tuple[float, float]:
        """
        Compute similarity against individual course fields and return
        (best_field_score, combined_score).

        Uses weighted field scoring: career-relevant fields (job_roles, skills)
        are weighted higher than short course names to prevent noisy single-word
        matches from dominating the score.
        """
        # Build per-field texts with their importance weights
        fields = []  # List of (text, weight) tuples
        if course.course_name:
            fields.append((course.course_name, FIELD_WEIGHTS["course_name"]))
        if course.job_roles:
            fields.append((", ".join(course.job_roles), FIELD_WEIGHTS["job_roles"]))
        if course.core_skills:
            fields.append((", ".join(course.core_skills), FIELD_WEIGHTS["core_skills"]))
        if course.interests:
            fields.append((", ".join(course.interests), FIELD_WEIGHTS["interests"]))

        # Compute per-field similarities with importance weighting
        weighted_scores = []
        for text, weight in fields:
            vec = self.encode_text(text)
            sim = self.compute_similarity_vectors(student_vec, vec)
            weighted_scores.append((sim * weight, weight))

        # Weighted average of all field scores (not raw max)
        if weighted_scores:
            total_weighted = sum(ws for ws, _ in weighted_scores)
            total_weight = sum(w for _, w in weighted_scores)
            best_field_score = total_weighted / total_weight
        else:
            best_field_score = 0.0

        # Also compute combined-text similarity (original approach)
        combined_text = course.get_combined_text()
        combined_vec = self.encode_text(combined_text)
        combined_score = self.compute_similarity_vectors(student_vec, combined_vec)

        return best_field_score, combined_score

    # ------------------------------------------------------------------
    # Technique 3: Keyword Overlap Bonus
    # ------------------------------------------------------------------
    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Simple lowercase tokenization with stopword filtering."""
        stopwords = {
            "i",
            "me",
            "my",
            "we",
            "our",
            "you",
            "your",
            "he",
            "she",
            "it",
            "they",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "shall",
            "should",
            "may",
            "might",
            "can",
            "could",
            "not",
            "no",
            "so",
            "if",
            "that",
            "this",
            "these",
            "those",
            "as",
            "from",
            "into",
            "about",
            "up",
            "out",
            "than",
            "then",
            "also",
            "want",
            "like",
            "love",
            "enjoy",
            "interested",
            "interest",
        }
        tokens = set(re.findall(r"[a-z]{2,}", text.lower()))
        return tokens - stopwords

    def _compute_keyword_bonus(
        self,
        student_input: str,
        course: CourseRecommendation,
    ) -> float:
        """
        Compute a Jaccard-style keyword overlap bonus between student tokens
        and course metadata tokens.

        Returns a value in [0, KEYWORD_BONUS_MAX].
        """
        student_tokens = self._tokenize(student_input)
        if not student_tokens:
            return 0.0

        # Build course token set from all fields
        course_parts = [
            course.course_name,
            ", ".join(course.job_roles),
            ", ".join(course.core_skills),
            ", ".join(course.interests),
            ", ".join(course.industries),
        ]
        course_tokens = self._tokenize(" ".join(course_parts))

        # Fraction of student tokens found in course metadata
        if not student_tokens:
            return 0.0

        overlap = len(student_tokens & course_tokens)
        coverage = overlap / len(student_tokens)

        return coverage * KEYWORD_BONUS_MAX

    # ------------------------------------------------------------------
    # Main ranking method (enhanced)
    # ------------------------------------------------------------------
    def rank_courses_by_interest(
        self,
        student_input: str,
        courses: List[CourseRecommendation],
    ) -> List[Tuple[CourseRecommendation, float]]:
        """
        Rank courses based on semantic similarity to student interests.

        Uses a 3-technique scoring pipeline:
        1. Query expansion via CareerMapper
        2. Multi-field max-similarity (ColBERT-inspired)
        3. Keyword overlap bonus (sparse signal)

        Args:
            student_input: Student's interests/skills description
            courses: List of CourseRecommendation objects to rank

        Returns:
            Sorted list of (CourseRecommendation, similarity_score) tuples
            where score is in [0.0, 1.0]
        """
        # Technique 1: Expand the query for a richer embedding
        expanded_query = self._expand_query(student_input)

        # Encode expanded student input once
        student_vec = self.encode_text(expanded_query)

        # Calculate enhanced similarity for each course
        scores = []
        for course in courses:
            # Technique 2: Multi-field scoring
            max_field_score, combined_score = self._compute_multi_field_score(
                student_vec, course
            )
            semantic_score = (
                MULTI_FIELD_WEIGHT * max_field_score
                + COMBINED_FIELD_WEIGHT * combined_score
            )

            # Technique 3: Keyword overlap bonus (uses original input, not expanded)
            keyword_bonus = self._compute_keyword_bonus(student_input, course)

            # Final score: semantic + keyword bonus, clamped to [0, 1]
            final_score = min(1.0, max(0.0, semantic_score + keyword_bonus))

            scores.append((course, final_score))

            logger.debug(
                f"[Score] {course.course_code} {course.course_name}: "
                f"best_field={max_field_score:.3f} combined={combined_score:.3f} "
                f"semantic={semantic_score:.3f} keyword_bonus={keyword_bonus:.3f} "
                f"FINAL={final_score:.3f}"
            )

        # Sort by similarity score (descending)
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)

        # Log top 5 for monitoring
        if ranked:
            logger.info(
                f"[Ranking] Top 5 for '{student_input[:40]}...': "
                + ", ".join(f"{c.course_code}={s:.1%}" for c, s in ranked[:5])
            )

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
