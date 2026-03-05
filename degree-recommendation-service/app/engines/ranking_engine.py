# app/engines/ranking_engine.py
from typing import Dict


class RankingEngine:
    """
    Combines eligibility, similarity, and optional Z-score buffer
    into a final ranking score.
    """

    def __init__(
        self,
        w_eligibility: float = 0.5,
        w_similarity: float = 0.5,
    ):
        self.w_eligibility = w_eligibility
        self.w_similarity = w_similarity

    def score(
        self,
        eligible: bool,
        similarity_score: float,
    ) -> float:
        eligibility_score = 1.0 if eligible else 0.0

        final_score = (
            self.w_eligibility * eligibility_score
            + self.w_similarity * similarity_score
        )

        return round(final_score, 4)
