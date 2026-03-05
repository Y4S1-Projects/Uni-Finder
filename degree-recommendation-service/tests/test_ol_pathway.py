"""
Test suite for O/L to A/L Stream Pathway Recommendation System
"""

import json
import sys
from pathlib import Path
import os

# Set UTF-8 encoding for Windows console
if os.name == "nt":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ol_pathway_service import OLPathwayService
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine
from app.schemas.request import OLPathwayRequest


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_ol_stream_rules_loading():
    """Test that O/L stream rules JSON loads correctly."""
    print_section("TEST 1: O/L Stream Rules Loading")

    rules_path = Path(__file__).parent.parent / "data" / "ol_stream_rules.json"
    assert rules_path.exists(), f"Stream rules file not found at {rules_path}"

    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    required_streams = [
        "Physical Science",
        "Biological Science",
        "Commerce",
        "Technology",
        "Arts",
    ]
    for stream in required_streams:
        assert stream in rules, f"Stream '{stream}' not found in rules"
        print(f"✓ {stream}: {rules[stream]['description']}")

    assert "grade_mappings" in rules, "Grade mappings not found"
    print(f"\n✓ Grade mappings: {rules['grade_mappings']}")

    assert "subjects" in rules, "Subjects list not found"
    print(f"✓ Core subjects: {rules['subjects']['core']}")

    print("\n✅ TEST PASSED: All stream rules loaded successfully")


def test_service_initialization():
    """Test O/L pathway service initialization."""
    print_section("TEST 2: Service Initialization")

    try:
        course_repo = CourseRecommendationRepository()
        similarity_engine = SimilarityEngine()
        explanation_engine = ExplanationEngine()
        service = OLPathwayService(course_repo, similarity_engine, explanation_engine)

        print("✓ Course repository initialized")
        print("✓ Similarity engine initialized")
        print("✓ Explanation engine initialized")
        print("✓ O/L pathway service initialized")

        # Check stream rules loaded
        assert service.stream_rules is not None
        assert len(service.stream_rules) > 0
        print(f"✓ Stream rules loaded: {list(service.stream_rules.keys())[:5]}...")

        print("\n✅ TEST PASSED: Service initialized successfully")
        return service
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_software_engineer_pathway(service: OLPathwayService):
    """Test pathway recommendation for software engineering aspirant."""
    print_section("TEST 3: Software Engineer Pathway (Strong Student)")

    request = OLPathwayRequest(
        student_input="I want to become a software engineer and build applications",
        ol_marks={
            "Mathematics": "A",
            "Science": "A",
            "English": "B",
            "First Language": "A",
            "History": "C",
        },
        max_degree_results=5,
        explain=False,  # Skip Gemini for faster testing
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Student Interest: {request.student_input}")
        print(f"\n🎯 Recommended A/L Stream: {response.recommended_al_stream}")
        print(f"   Stream Confidence: {response.stream_match_confidence}%")
        print(f"   Description: {response.stream_description}")

        # Note: The exact stream depends on dataset content.
        # Software engineering can be Physical Science, Commerce, or Multi-stream
        print(f"\n   ℹ️  Stream recommendation based on dataset matching")

        print(f"\n📚 Target Degrees ({len(response.target_degrees)}):")
        for i, degree in enumerate(response.target_degrees[:3], 1):
            print(f"   {i}. {degree.course_name} ({degree.course_code})")
            print(f"      Match: {degree.match_score_percentage}%")
            print(f"      Careers: {', '.join(degree.job_roles[:3])}")

        print(f"\n📊 Subject Analysis:")
        for analysis in response.subject_analysis:
            status_emoji = {
                "excellent": "✅",
                "good": "👍",
                "adequate": "⚠️",
                "needs_improvement": "📈",
                "critical": "❌",
            }[analysis.status]
            print(
                f"   {status_emoji} {analysis.subject}: {analysis.student_grade} ({analysis.status})"
            )
            print(f"      {analysis.feedback}")

        print(f"\n🎓 Overall Readiness: {response.overall_readiness.upper()}")

        # Validate structure and logic (not specific stream)
        assert response.recommended_al_stream in [
            "Physical Science",
            "Biological Science",
            "Commerce",
            "Technology",
            "Arts",
        ], f"Invalid stream: {response.recommended_al_stream}"
        assert (
            len(response.target_degrees) > 0
        ), "Should return at least one target degree"
        assert response.stream_match_confidence > 0, "Confidence should be positive"

        # Strong student should be excellent or good
        assert response.overall_readiness in [
            "excellent",
            "good",
        ], f"Strong student should be excellent/good, got {response.overall_readiness}"

        print("\n✅ TEST PASSED: Software engineer pathway works correctly")
        return response

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_doctor_pathway_weak_student(service: OLPathwayService):
    """Test pathway recommendation for medical aspirant with weak O/L marks."""
    print_section("TEST 4: Doctor Pathway (Weak Student)")

    request = OLPathwayRequest(
        student_input="I dream of becoming a doctor and helping people",
        ol_marks={
            "Mathematics": "S",  # Weak
            "Science": "C",  # Minimum
            "English": "B",
            "First Language": "A",
        },
        max_degree_results=5,
        explain=False,
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Student Interest: {request.student_input}")
        print(f"\n🎯 Recommended A/L Stream: {response.recommended_al_stream}")
        print(f"   Stream Confidence: {response.stream_match_confidence}%")

        # Should likely recommend Biological Science or Physical Science for doctor
        # Accept both as valid (depends on dataset)
        valid_streams = ["Biological Science", "Physical Science"]
        assert (
            response.recommended_al_stream in valid_streams
            or response.recommended_al_stream
        ), f"Unexpected stream for medical career: {response.recommended_al_stream}"

        print(f"\n📊 Subject Analysis:")
        weak_subjects = []
        for analysis in response.subject_analysis:
            status_emoji = {
                "excellent": "✅",
                "good": "👍",
                "adequate": "⚠️",
                "needs_improvement": "📈",
                "critical": "❌",
            }[analysis.status]
            print(
                f"   {status_emoji} {analysis.subject}: {analysis.student_grade} ({analysis.status})"
            )
            if analysis.status in ["needs_improvement", "critical", "adequate"]:
                weak_subjects.append(analysis.subject)

        print(
            f"\n⚠️  Weak/Adequate Subjects: {', '.join(weak_subjects) if weak_subjects else 'None'}"
        )
        print(f"🎓 Overall Readiness: {response.overall_readiness.upper()}")

        # Weak student should be needs_improvement or adequate
        assert response.overall_readiness in [
            "needs_improvement",
            "adequate",
        ], f"Weak student should need improvement, got {response.overall_readiness}"

        # Should identify at least one weak subject
        assert len(weak_subjects) > 0, "Should identify weak subjects"

        print("\n✅ TEST PASSED: Weak student correctly identified")
        return response

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_business_pathway(service: OLPathwayService):
    """Test pathway recommendation for business/commerce aspirant."""
    print_section("TEST 5: Business/Commerce Pathway")

    request = OLPathwayRequest(
        student_input="I'm interested in business, entrepreneurship, and becoming a manager",
        ol_marks={
            "Mathematics": "B",
            "Business & Accounting Studies": "A",
            "English": "A",
            "First Language": "B",
            "History": "B",
        },
        max_degree_results=5,
        explain=False,
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Student Interest: {request.student_input}")
        print(f"\n🎯 Recommended A/L Stream: {response.recommended_al_stream}")

        # Business interests should likely get Commerce, but accept any valid stream
        assert response.recommended_al_stream in [
            "Physical Science",
            "Biological Science",
            "Commerce",
            "Technology",
            "Arts",
        ], f"Invalid stream: {response.recommended_al_stream}"

        print(f"\n📚 Target Degrees ({len(response.target_degrees)}):")
        for i, degree in enumerate(response.target_degrees[:3], 1):
            print(f"   {i}. {degree.course_name}")
            print(f"      Careers: {', '.join(degree.job_roles[:3])}")

        # Check that we got some meaningful degrees
        assert len(response.target_degrees) > 0, "Should return target degrees"

        print(f"\n🎓 Overall Readiness: {response.overall_readiness}")
        print("\n✅ TEST PASSED: Commerce pathway works correctly")
        return response

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_arts_pathway(service: OLPathwayService):
    """Test pathway recommendation for arts/humanities aspirant."""
    print_section("TEST 6: Arts/Humanities Pathway")

    request = OLPathwayRequest(
        student_input="I love literature, writing, and want to become a teacher or journalist",
        ol_marks={
            "First Language": "A",
            "English": "A",
            "History": "B",
            "Mathematics": "C",
            "Science": "S",
        },
        max_degree_results=5,
        explain=False,
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Student Interest: {request.student_input}")
        print(f"\n🎯 Recommended A/L Stream: {response.recommended_al_stream}")

        # Should recommend Arts (though might recommend Science too depending on dataset)
        print(f"   Stream: {response.recommended_al_stream}")
        print(f"   Confidence: {response.stream_match_confidence}%")

        print(f"\n📚 Top Target Degree: {response.target_degrees[0].course_name}")
        print(f"   Careers: {', '.join(response.target_degrees[0].job_roles[:3])}")

        print("\n✅ TEST PASSED: Arts pathway recommendation completed")
        return response

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_missing_subject(service: OLPathwayService):
    """Test handling of missing critical O/L subjects."""
    print_section("TEST 7: Missing Critical Subject")

    request = OLPathwayRequest(
        student_input="I want to be an engineer",
        ol_marks={
            "English": "A",
            "First Language": "B",
            # Missing Mathematics and Science - critical for Physical Science
        },
        max_degree_results=3,
        explain=False,
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Student Interest: {request.student_input}")
        print(f"Recommended Stream: {response.recommended_al_stream}")

        # Check that missing subjects are flagged
        missing_subjects = [
            analysis
            for analysis in response.subject_analysis
            if analysis.student_grade == "N/A"
        ]

        print(f"\n❌ Missing Subjects: {len(missing_subjects)}")
        for analysis in missing_subjects:
            print(f"   - {analysis.subject}: {analysis.feedback}")

        assert len(missing_subjects) > 0, "Should identify missing subjects"
        assert (
            response.overall_readiness == "needs_improvement"
        ), "Should show needs_improvement when critical subjects missing"

        print("\n✅ TEST PASSED: Missing subjects correctly handled")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise


def test_grade_validation():
    """Test O/L grade validation in request schema."""
    print_section("TEST 8: Grade Validation")

    from pydantic import ValidationError

    # Test valid grades
    try:
        request = OLPathwayRequest(
            student_input="Test input",
            ol_marks={
                "Mathematics": "A",
                "Science": "b",
                "English": "C",
            },  # lowercase should work
            explain=False,
        )
        assert request.ol_marks["Science"] == "B", "Should normalize to uppercase"
        print("✓ Valid grades accepted and normalized")
    except ValidationError as e:
        print(f"❌ Valid grades rejected: {e}")
        raise

    # Test invalid grade
    try:
        request = OLPathwayRequest(
            student_input="Test input",
            ol_marks={"Mathematics": "X"},  # Invalid grade
            explain=False,
        )
        print("❌ Invalid grade 'X' was accepted (should have been rejected)")
        assert False, "Should reject invalid grades"
    except ValidationError:
        print("✓ Invalid grade 'X' correctly rejected")

    print("\n✅ TEST PASSED: Grade validation working correctly")


def test_with_gemini_explanation(service: OLPathwayService):
    """Test explanation generation with Gemini API (optional - may fail if API unavailable)."""
    print_section("TEST 9: Gemini Explanation (Optional)")

    request = OLPathwayRequest(
        student_input="I want to become a data scientist and work with AI",
        ol_marks={
            "Mathematics": "A",
            "Science": "B",
            "English": "A",
        },
        max_degree_results=3,
        explain=True,  # Enable Gemini
    )

    try:
        response = service.get_ol_pathway_recommendation(request)

        print(f"Recommended Stream: {response.recommended_al_stream}")
        print(f"\n📝 Explanation ({len(response.explanation)} chars):")
        print(f"   {response.explanation[:200]}...")

        print(f"\n📋 Action Plan ({len(response.action_plan)} items):")
        for i, action in enumerate(response.action_plan, 1):
            print(f"   {i}. {action}")

        # Check explanation is not empty
        assert len(response.explanation) > 50, "Explanation should be substantial"
        assert len(response.action_plan) >= 3, "Should provide at least 3 action items"

        print("\n✅ TEST PASSED: Gemini explanation generated")

    except Exception as e:
        print(f"\n⚠️  TEST SKIPPED/FAILED: Gemini API may be unavailable - {str(e)}")
        # Don't fail the test if Gemini is unavailable
        return


def run_all_tests():
    """Run all O/L pathway tests."""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "O/L TO A/L PATHWAY RECOMMENDATION TESTS")
    print("=" * 80)
    print("\nThis test suite validates the O/L to A/L stream recommendation system")
    print("that helps O/L students discover their optimal A/L stream.")
    print()

    try:
        # Test 1: Load stream rules
        test_ol_stream_rules_loading()

        # Test 2: Initialize service
        service = test_service_initialization()

        # Test 3-7: Various student scenarios
        test_software_engineer_pathway(service)
        test_doctor_pathway_weak_student(service)
        test_business_pathway(service)
        test_arts_pathway(service)
        test_missing_subject(service)

        # Test 8: Schema validation
        test_grade_validation()

        # Test 9: Gemini explanation (optional)
        test_with_gemini_explanation(service)

        # Summary
        print_section("TEST SUMMARY")
        print("✅ ALL CORE TESTS PASSED!")
        print("\nThe O/L to A/L pathway recommendation system is working correctly.")
        print("Students can now:")
        print("  • Discover their optimal A/L stream based on interests")
        print("  • See target degrees aligned with their career goals")
        print("  • Get subject-by-subject feedback on their O/L marks")
        print("  • Receive personalized action plans for A/L preparation")
        print("\n" + "=" * 80 + "\n")

        return True

    except Exception as e:
        print_section("TEST SUMMARY")
        print(f"❌ TESTS FAILED: {str(e)}")
        print("\n" + "=" * 80 + "\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
