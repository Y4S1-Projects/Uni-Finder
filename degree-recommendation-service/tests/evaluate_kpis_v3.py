"""
KPI Evaluation Pipeline V3 - Dream vs. Reality Architecture

This script evaluates the IMPROVED recommendation engine using:
- Phase 1-3: All V2 improvements (Career Mapping, Hybrid Search, Weighted Corpus)
- Phase 4: **HARD ELIGIBILITY FILTERING** for A/L students (NEW)
- Phase 5: **DREAM VS REALITY** separation (NEW)

Key Innovation:
- For A/L students: FIRST filter by strict eligibility, THEN rank within eligible courses
- This prevents recommending ineligible courses (e.g., CS to Arts students)

Usage:
    python evaluate_kpis_v3.py --output results/kpi_evaluation_report_v3.csv --summary results/kpi_summary_v3.json
"""

import json
import sys
import csv
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
import argparse

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.pipelines.dream_reality_pipeline import DreamRealityPipeline
from app.domain.student import StudentProfile

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def normalize_course_code(code: str) -> str:
    """Normalize course code to 3-digit format with zero-padding."""
    if not code:
        return code
    code = str(code).strip()
    try:
        num = int(code)
        return f"{num:03d}"
    except ValueError:
        return code


class KPIEvaluatorV3:
    """Evaluates DREAM VS REALITY recommendation system with hard eligibility filtering."""

    def __init__(
        self,
        ground_truth_path: str,
        semantic_weight: float = 0.7,
        tfidf_weight: float = 0.3,
        use_career_mapping: bool = True,
    ):
        """
        Initialize evaluator with Dream vs. Reality pipeline.

        Args:
            ground_truth_path: Path to ground truth JSON file
            semantic_weight: Weight for semantic similarity (0-1)
            tfidf_weight: Weight for TF-IDF similarity (0-1)
            use_career_mapping: Whether to use career query expansion
        """
        self.ground_truth_path = Path(ground_truth_path)
        self.course_repo = CourseRecommendationRepository()

        # Use DREAM VS REALITY pipeline
        logger.info("🚀 Initializing DREAM VS REALITY Pipeline (v3)")
        logger.info(f"   - Semantic weight: {semantic_weight}")
        logger.info(f"   - TF-IDF weight: {tfidf_weight}")
        logger.info(
            f"   - Career mapping: {'ENABLED' if use_career_mapping else 'DISABLED'}"
        )
        logger.info(f"   - Hard eligibility filtering: ENABLED ✅")

        self.pipeline = DreamRealityPipeline(
            semantic_weight=semantic_weight,
            tfidf_weight=tfidf_weight,
            use_career_mapping=use_career_mapping,
        )

        self.test_cases = []
        self.results = []

    def load_ground_truth(self):
        """Load ground truth test cases from JSON file."""
        logger.info(f"Loading ground truth from {self.ground_truth_path}")

        with open(self.ground_truth_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.test_cases = data["test_cases"]
        logger.info(f"Loaded {len(self.test_cases)} test cases")

        # Validate that all test cases have student_profile
        for i, test_case in enumerate(self.test_cases):
            if "student_profile" not in test_case:
                raise ValueError(
                    f"Test case {test_case.get('test_id', i)} missing required field: student_profile"
                )

            profile = test_case["student_profile"]
            required_profile_fields = ["stream", "subjects", "z_score", "district"]
            for field in required_profile_fields:
                if field not in profile:
                    raise ValueError(
                        f"Test case {test_case['test_id']} student_profile missing: {field}"
                    )

        logger.info("[OK] All test cases validated with explicit student profiles")

    def get_recommendations(
        self, student_input: str, student_profile: Dict, top_k: int = 5
    ) -> Tuple[List[str], List[str]]:
        """
        Get course recommendations using DREAM VS REALITY pipeline.

        Returns both:
        1. All eligible courses (results-based ranking)
        2. Interest-filtered courses (interest-based ranking)

        Args:
            student_input: Student's interest description
            student_profile: Dict with stream, subjects, z_score, district
            top_k: Number of recommendations to return

        Returns:
            Tuple of (all_eligible_codes, interest_filtered_codes)
        """
        # Create StudentProfile object from validated ground truth profile
        profile = StudentProfile(
            stream=student_profile["stream"],
            subjects=student_profile["subjects"],
            zscore=student_profile["z_score"],
            interests=student_input,
        )

        # Get recommendations using Dream vs. Reality pipeline
        # For evaluation, assume all are A/L students (reality-first with interest filtering)
        result = self.pipeline.recommend(
            student=profile,
            district=student_profile["district"],
            is_al_student=True,  # A/L students get hard filtering first
            max_results=top_k,
        )

        # Extract recommendations from the new two-tier output
        all_eligible = result.get("all_eligible_courses", [])
        interest_filtered = result.get("recommendations", [])

        # Convert to course code lists
        all_eligible_codes = [rec["course_code"] for rec in all_eligible]
        interest_filtered_codes = [rec["course_code"] for rec in interest_filtered]

        return interest_filtered_codes, all_eligible_codes

    def calculate_precision_at_k(
        self, predicted: List[str], expected: List[str], k: int = 5
    ) -> float:
        """
        Calculate Precision at K.

        P@K = (Number of relevant items in top-K) / K

        Args:
            predicted: List of predicted course codes
            expected: List of expected/relevant course codes
            k: Number of top predictions to consider

        Returns:
            Precision@K score (0 to 1)
        """
        if not predicted or not expected:
            return 0.0

        # Normalize codes to 3-digit format for comparison
        expected_set = set(normalize_course_code(str(code)) for code in expected)
        top_k_predicted = [normalize_course_code(str(code)) for code in predicted[:k]]

        # Count relevant items in top-K
        relevant_count = sum(1 for code in top_k_predicted if code in expected_set)

        return relevant_count / k

    def calculate_mrr(self, predicted: List[str], expected: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank.

        MRR = 1 / rank_of_first_relevant_item

        Args:
            predicted: List of predicted course codes
            expected: List of expected/relevant course codes

        Returns:
            MRR score (0 to 1)
        """
        if not predicted or not expected:
            return 0.0

        # Normalize codes to 3-digit format for comparison
        expected_set = set(normalize_course_code(str(code)) for code in expected)

        # Find rank of first relevant item (1-indexed)
        for rank, code in enumerate(predicted, start=1):
            if normalize_course_code(str(code)) in expected_set:
                return 1.0 / rank

        return 0.0  # No relevant items found

    def calculate_dcg_at_k(
        self,
        predicted: List[str],
        expected: List[str],
        relevance_scores: List[int],
        k: int = 5,
    ) -> float:
        """
        Calculate Discounted Cumulative Gain at K.

        DCG@K = Σ(rel_i / log2(i+1)) for i=1 to K

        Args:
            predicted: List of predicted course codes
            expected: List of expected course codes
            relevance_scores: List of relevance scores (same order as expected)
            k: Number of top predictions to consider

        Returns:
            DCG@K score
        """
        if not predicted or not expected:
            return 0.0

        # Create relevance lookup dict with normalized course codes
        relevance_dict = {}
        for code, score in zip(expected, relevance_scores):
            relevance_dict[normalize_course_code(str(code))] = int(score)

        dcg = 0.0
        for i, code in enumerate(predicted[:k], start=1):
            rel = relevance_dict.get(normalize_course_code(str(code)), 0)
            dcg += rel / np.log2(i + 1)

        return dcg

    def calculate_idcg_at_k(self, relevance_scores: List[int], k: int = 5) -> float:
        """
        Calculate Ideal DCG at K (best possible ranking).

        IDCG@K = DCG@K with perfect ranking

        Args:
            relevance_scores: List of relevance scores
            k: Number of top positions

        Returns:
            IDCG@K score
        """
        if not relevance_scores:
            return 0.0

        # Sort relevance scores in descending order (ideal ranking)
        sorted_relevance = sorted([int(s) for s in relevance_scores], reverse=True)

        idcg = 0.0
        for i, rel in enumerate(sorted_relevance[:k], start=1):
            idcg += rel / np.log2(i + 1)

        return idcg

    def calculate_ndcg_at_k(
        self,
        predicted: List[str],
        expected: List[str],
        relevance_scores: List[int],
        k: int = 5,
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at K.

        NDCG@K = DCG@K / IDCG@K

        Args:
            predicted: List of predicted course codes
            expected: List of expected course codes
            relevance_scores: List of relevance scores
            k: Number of top predictions to consider

        Returns:
            NDCG@K score (0 to 1)
        """
        dcg = self.calculate_dcg_at_k(predicted, expected, relevance_scores, k)
        idcg = self.calculate_idcg_at_k(relevance_scores, k)

        if idcg == 0.0:
            return 0.0

        return dcg / idcg

    def evaluate_single_test_case(self, test_case: Dict) -> Dict:
        """
        Evaluate a single test case against BOTH:
        1. All eligible courses (results-based)
        2. Interest-filtered courses (interest-based)

        Args:
            test_case: Test case dictionary with student_interest and expected_top_courses

        Returns:
            Evaluation results dictionary
        """
        test_id = test_case["test_id"]
        student_interest = test_case["student_interest"]
        expected_courses = test_case["expected_top_courses"]
        relevance_scores = test_case["relevance_scores"]
        student_profile = test_case["student_profile"]

        # Get predictions from DREAM VS REALITY pipeline
        # Returns (interest_filtered, all_eligible)
        interest_filtered, all_eligible = self.get_recommendations(
            student_interest, student_profile, top_k=5
        )

        # Evaluate against INTEREST-FILTERED recommendations (primary metric)
        p_at_5 = self.calculate_precision_at_k(interest_filtered, expected_courses, k=5)
        mrr = self.calculate_mrr(interest_filtered, expected_courses)
        ndcg_at_5 = self.calculate_ndcg_at_k(
            interest_filtered, expected_courses, relevance_scores, k=5
        )

        # Also check if expected courses are in ALL ELIGIBLE (for diagnosis)
        eligible_p_at_5 = self.calculate_precision_at_k(
            all_eligible, expected_courses, k=5
        )

        return {
            "test_id": test_id,
            "student_interest": student_interest,
            "student_stream": student_profile["stream"],
            "predicted_interest_filtered": ",".join(interest_filtered[:5]),
            "predicted_all_eligible": (
                ",".join(all_eligible[:5]) if all_eligible else ""
            ),
            "expected_top_5": ",".join(str(c) for c in expected_courses[:5]),
            "relevant_in_interest_filtered": int(
                sum(
                    1
                    for c in interest_filtered[:5]
                    if normalize_course_code(str(c))
                    in set(normalize_course_code(str(ec)) for ec in expected_courses)
                )
            ),
            "relevant_in_all_eligible": int(
                sum(
                    1
                    for c in all_eligible[:5]
                    if normalize_course_code(str(c))
                    in set(normalize_course_code(str(ec)) for ec in expected_courses)
                )
            ),
            "p_at_5": p_at_5,
            "mrr": mrr,
            "ndcg_at_5": ndcg_at_5,
            "eligible_p_at_5": eligible_p_at_5,  # For diagnostics
            "notes": test_case.get("notes", ""),
        }

    def run_evaluation(self) -> List[Dict]:
        """
        Run evaluation on all test cases.

        Returns:
            List of evaluation results
        """
        logger.info("=" * 60)
        logger.info("STARTING KPI EVALUATION V3 (DREAM VS REALITY)")
        logger.info("=" * 60)

        total_cases = len(self.test_cases)

        for i, test_case in enumerate(self.test_cases, start=1):
            logger.info(
                f"Evaluating test case {i}/{total_cases}: {test_case['test_id']}"
            )

            try:
                result = self.evaluate_single_test_case(test_case)
                self.results.append(result)

                # Log metrics for this test case
                logger.info(
                    f"  P@5={result['p_at_5']:.3f}, MRR={result['mrr']:.3f}, NDCG@5={result['ndcg_at_5']:.3f}"
                )

            except Exception as e:
                logger.error(f"  [FAIL] Error evaluating {test_case['test_id']}: {e}")
                import traceback

                traceback.print_exc()
                # Store error result with all required fields
                self.results.append(
                    {
                        "test_id": test_case["test_id"],
                        "category": test_case.get("category", "Unknown"),
                        "student_interest": test_case["student_interest"][:70],
                        "student_stream": test_case.get("student_profile", {}).get(
                            "stream", "N/A"
                        ),
                        "predicted_top_5": "",
                        "expected_top_5": "",
                        "relevant_in_top_5": 0,
                        "p_at_5": 0.0,
                        "mrr": 0.0,
                        "ndcg_at_5": 0.0,
                        "notes": f"ERROR: {str(e)}",
                    }
                )

        return self.results

    def calculate_summary_statistics(self) -> Dict:
        """
        Calculate summary statistics across all test cases.

        Returns:
            Dictionary with average metrics and interpretation
        """
        # Filter out error results
        valid_results = [r for r in self.results if "error" not in r]

        if not valid_results:
            return {
                "error": "No valid results to summarize",
                "total_test_cases": len(self.results),
                "valid_test_cases": 0,
            }

        # Calculate averages
        avg_p_at_5 = np.mean([r["p_at_5"] for r in valid_results])
        avg_mrr = np.mean([r["mrr"] for r in valid_results])
        avg_ndcg_at_5 = np.mean([r["ndcg_at_5"] for r in valid_results])

        # Performance interpretation
        def interpret_metric(metric_name, value):
            if value >= 0.7:
                return f"[EXCELLENT] {metric_name} of {value:.1%} is excellent"
            elif value >= 0.5:
                return f"[GOOD] {metric_name} of {value:.1%} is good"
            elif value >= 0.3:
                return f"⚠ FAIR: {metric_name} of {value:.1%} needs improvement"
            else:
                return f"[POOR] {metric_name} of {value:.1%} is below target"

        summary = {
            "engine_version": "v3_dream_vs_reality",
            "total_test_cases": len(self.results),
            "valid_test_cases": len(valid_results),
            "failed_test_cases": len(self.results) - len(valid_results),
            "avg_p_at_5": round(avg_p_at_5, 4),
            "avg_mrr": round(avg_mrr, 4),
            "avg_ndcg_at_5": round(avg_ndcg_at_5, 4),
            "interpretation": {
                "p_at_5": interpret_metric("P@5", avg_p_at_5),
                "mrr": interpret_metric("MRR", avg_mrr),
                "ndcg_at_5": interpret_metric("NDCG@5", avg_ndcg_at_5),
            },
            "improvements": [
                "Career-to-Degree Mapping (query expansion)",
                "Hybrid Search (Dense 70% + Sparse 30%)",
                "Weighted Corpus Construction (3x job roles, 2x skills)",
                "HARD ELIGIBILITY FILTERING (NEW in V3)",
                "Dream vs. Reality Separation (NEW in V3)",
            ],
            "evaluated_at": datetime.now().isoformat(),
        }

        return summary

    def export_results(self, output_path: str, summary_path: str):
        """
        Export evaluation results to CSV and JSON.

        Args:
            output_path: Path to save detailed CSV results
            summary_path: Path to save summary JSON
        """
        output_path = Path(output_path)
        summary_path = Path(summary_path)

        # Create output directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        # Export detailed results to CSV
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "test_id",
                "student_interest",
                "student_stream",
                "predicted_interest_filtered",
                "predicted_all_eligible",
                "expected_top_5",
                "relevant_in_interest_filtered",
                "relevant_in_all_eligible",
                "p_at_5",
                "mrr",
                "ndcg_at_5",
                "eligible_p_at_5",
                "notes",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        logger.info(f"[OK] Detailed results exported to: {output_path}")

        # Export summary to JSON
        summary = self.calculate_summary_statistics()
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[OK] Summary statistics exported to: {summary_path}")

        # Print summary to console
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY (V3 - DREAM VS REALITY)")
        print("=" * 60)
        print(f"Total Test Cases: {summary['total_test_cases']}")
        print(f"Valid Results: {summary['valid_test_cases']}")
        print(f"Failed Cases: {summary['failed_test_cases']}")
        print()
        print(
            f"Average P@5:    {summary['avg_p_at_5']:.4f} ({summary['avg_p_at_5']*100:.1f}%)"
        )
        print(
            f"Average MRR:    {summary['avg_mrr']:.4f} ({summary['avg_mrr']*100:.1f}%)"
        )
        print(
            f"Average NDCG@5: {summary['avg_ndcg_at_5']:.4f} ({summary['avg_ndcg_at_5']*100:.1f}%)"
        )
        print()
        print("Performance Interpretation:")
        print(f"  {summary['interpretation']['p_at_5']}")
        print(f"  {summary['interpretation']['mrr']}")
        print(f"  {summary['interpretation']['ndcg_at_5']}")
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate recommendation system with Dream vs. Reality pipeline (V3)"
    )
    parser.add_argument(
        "--ground-truth",
        default="data/ground_truth_validated_v2.json",
        help="Path to PROPERLY VALIDATED ground truth test cases with verified Z-score cutoffs",
    )
    parser.add_argument(
        "--output",
        default="results/kpi_evaluation_report_v3_fixed.csv",
        help="Path to save detailed results CSV",
    )
    parser.add_argument(
        "--summary",
        default="results/kpi_summary_v3_fixed.json",
        help="Path to save summary JSON",
    )
    parser.add_argument(
        "--semantic-weight",
        type=float,
        default=0.7,
        help="Weight for semantic similarity (0-1)",
    )
    parser.add_argument(
        "--tfidf-weight",
        type=float,
        default=0.3,
        help="Weight for TF-IDF similarity (0-1)",
    )
    parser.add_argument(
        "--disable-career-mapping",
        action="store_true",
        help="Disable career-to-degree query expansion",
    )

    args = parser.parse_args()

    # Validate weights
    if abs(args.semantic_weight + args.tfidf_weight - 1.0) > 0.001:
        logger.error("Error: --semantic-weight and --tfidf-weight must sum to 1.0")
        sys.exit(1)

    # Initialize evaluator
    evaluator = KPIEvaluatorV3(
        ground_truth_path=args.ground_truth,
        semantic_weight=args.semantic_weight,
        tfidf_weight=args.tfidf_weight,
        use_career_mapping=not args.disable_career_mapping,
    )

    # Load test cases
    evaluator.load_ground_truth()

    # Run evaluation
    evaluator.run_evaluation()

    # Export results
    evaluator.export_results(args.output, args.summary)

    logger.info("\n[OK] Evaluation complete!")


if __name__ == "__main__":
    main()
