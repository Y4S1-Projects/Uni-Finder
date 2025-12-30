# tests/test_similarity_engine.py
from app.engines.similarity_engine import SimilarityEngine


def test_similarity_score_range():
    engine = SimilarityEngine()

    score = engine.compute_similarity(
        "I like artificial intelligence and programming",
        "This degree focuses on computer science and software engineering"
    )

    assert 0.0 <= score <= 1.0
