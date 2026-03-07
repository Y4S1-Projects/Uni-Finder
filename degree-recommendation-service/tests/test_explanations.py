"""
Test script to verify explanations are generated for all recommendation scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.student import StudentProfile
from app.pipelines.recommendation_pipeline import RecommendationPipeline


def test_explanations_in_recommendations():
    """
    Test that all recommendations include explanations.
    Test various scenarios:
    1. A/L Physical Science stream
    2. A/L Biological Science stream
    3. A/L Commerce stream
    4. A/L Engineering Technology stream
    5. A/L Arts stream
    """
    pipeline = RecommendationPipeline()

    test_cases = [
        {
            "name": "Physical Science A/L Student",
            "stream": "Physical Science",
            "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
            "zscore": 2.0,
            "interests": "I love mathematics, physics, and technology. Want to study engineering or computer science.",
        },
        {
            "name": "Biological Science A/L Student",
            "stream": "Biological Science",
            "subjects": ["Biology", "Chemistry", "Physics"],
            "zscore": 1.8,
            "interests": "I'm passionate about medicine, biology, and helping people. Want to pursue healthcare.",
        },
        {
            "name": "Commerce A/L Student",
            "stream": "Commerce",
            "subjects": ["Accounting", "Business Studies", "Economics"],
            "zscore": 1.9,
            "interests": "I'm interested in business, finance, and entrepreneurship.",
        },
        {
            "name": "Engineering Technology A/L Student",
            "stream": "Engineering Technology",
            "subjects": ["Engineering Technology", "Science for Technology", "Physics"],
            "zscore": 2.1,
            "interests": "I love building things, technology, and practical engineering work.",
        },
        {
            "name": "Arts A/L Student",
            "stream": "Arts",
            "subjects": ["History", "Literature", "Geography"],
            "zscore": 1.7,
            "interests": "I'm interested in humanities, social sciences, and cultural studies.",
        },
    ]

    print("\n" + "=" * 80)
    print("EXPLANATION GENERATION TEST")
    print("=" * 80)

    for test_case in test_cases:
        print(f"\n[*] Testing: {test_case['name']}")
        print("-" * 80)

        student = StudentProfile(
            stream=test_case["stream"],
            subjects=test_case["subjects"],
            zscore=test_case["zscore"],
            interests=test_case["interests"],
        )

        try:
            recommendations = pipeline.recommend(
                student=student,
                district="Western",
                max_results=5,
                above_score_count=2,
            )

            print(f"[OK] Got {len(recommendations)} recommendations")

            # Check if explanations are present
            explanations_found = 0
            explanations_missing = 0

            for i, rec in enumerate(recommendations):
                has_explanation = "explanation" in rec and rec["explanation"]

                if has_explanation:
                    explanations_found += 1
                    print(f"\n  [{i+1}] {rec['course_name']}")
                    print(
                        f"      Status: {'[OK] Eligible' if rec.get('eligibility') else '[?] Aspirational'}"
                    )
                    print(f"      Explanation: {rec['explanation'][:100]}...")
                else:
                    explanations_missing += 1
                    print(f"\n  [{i+1}] {rec['course_name']}")
                    print(f"      [!] NO EXPLANATION FOUND")

            print(
                f"\n  Summary: {explanations_found}/{len(recommendations)} have explanations"
            )

            if explanations_missing > 0:
                print(
                    f"  [!] WARNING: {explanations_missing} recommendations missing explanations!"
                )

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_explanations_in_recommendations()
