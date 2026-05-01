import os
import sys
import math
import json
import logging
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app.engines.similarity_engine as se
from app.engines.similarity_engine import SimilarityEngine
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)

logging.disable(logging.CRITICAL)


def dcg_at_k(r, k):
    r = np.asarray(r, dtype=float)[:k]
    if r.size:
        return np.sum((2**r - 1) / np.log2(np.arange(2, r.size + 2)))
    return 0.0


def ndcg_at_k(r, k):
    dcg_max = dcg_at_k(sorted(r, reverse=True), k)
    if not dcg_max:
        return 0.0
    return dcg_at_k(r, k) / dcg_max


# Using verified course codes from ground_truth_validated_v2.json
GROUND_TRUTH = [
    {
        "query": "I want to be a doctor and save lives. Medicine is my passion.",
        "ideal": ["001"],
    },  # Medicine
    {
        "query": "I love building structures, designing systems, and engineering.",
        "ideal": ["008"],
    },  # Engineering
    {
        "query": "I love programming, building software systems, and AI.",
        "ideal": ["012"],
    },  # Computer Science
    {
        "query": "I love managing teams, business strategy, and entrepreneurship.",
        "ideal": ["016"],
    },  # Management
    {
        "query": "I'm skilled with numbers and want to be a chartered accountant.",
        "ideal": ["017"],
    },  # Accounting
    {
        "query": "I love literature, history, philosophy, and human culture.",
        "ideal": ["019", "020", "041"],
    },  # Arts
    {
        "query": "I love working with plants, sustainable farming, agriculture.",
        "ideal": ["004"],
    },  # Agriculture
    {
        "query": "I'm passionate about food science, nutrition, food safety.",
        "ideal": ["005"],
    },  # Food Science
]

encode_cache = {}


def run_evaluation(config_name, combined_w, multi_w, max_bonus):
    se.COMBINED_FIELD_WEIGHT = combined_w
    se.MULTI_FIELD_WEIGHT = multi_w
    se.KEYWORD_BONUS_MAX = max_bonus

    engine = SimilarityEngine()
    original_encode_text = engine.encode_text

    def cached_encode_text(text):
        if text not in encode_cache:
            encode_cache[text] = original_encode_text(text)
        return encode_cache[text]

    engine.encode_text = cached_encode_text

    repo = CourseRecommendationRepository()
    all_courses = repo.get_all_courses()

    total_p5 = 0.0
    total_ndcg5 = 0.0
    valid_queries = 0

    for item in GROUND_TRUTH:
        query = item["query"]
        ideal_codes = item["ideal"]
        valid_queries += 1

        ranked = engine.rank_courses_by_interest(query, all_courses)
        top_5 = [str(course.course_code).zfill(3) for course, score in ranked[:5]]

        # print(f"Query: {query[:20]} | Ideal: {ideal_codes} | Top5: {top_5}")

        hits = sum(1 for code in top_5 if code in ideal_codes)
        p5 = hits / 5.0
        total_p5 += p5

        relevance = [1 if code in ideal_codes else 0 for code in top_5]
        ndcg5 = ndcg_at_k(relevance, 5)
        total_ndcg5 += ndcg5

    avg_p5 = total_p5 / valid_queries
    avg_ndcg5 = total_ndcg5 / valid_queries

    print(f"| {config_name} | {avg_p5:.4f} | {avg_ndcg5:.4f} |")


if __name__ == "__main__":
    print("Starting Ablation Study Evaluation...\n")
    print("| Configuration | Precision@5 | nDCG@5 |")
    print("|---------------|-------------|--------|")

    run_evaluation("Config A (1.0 / 0.0)", combined_w=1.0, multi_w=0.0, max_bonus=0.0)
    run_evaluation("Config B (0.0 / 1.0)", combined_w=0.0, multi_w=1.0, max_bonus=0.20)
    run_evaluation("Config C (0.3 / 0.7)", combined_w=0.3, multi_w=0.7, max_bonus=0.15)
    run_evaluation("Config D (0.7 / 0.3)", combined_w=0.7, multi_w=0.3, max_bonus=0.08)
