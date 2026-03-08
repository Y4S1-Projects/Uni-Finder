# tests/test_interest_recommendation_pipeline.py
"""
Comprehensive test suite for 3-step recommendation pipeline.
Tests:
1. Similarity Matching (Step 2)
2. Keyword Extraction (Step 3)
3. Full Pipeline with various student inputs
4. Explainable AI integration
"""

import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine
from app.services.interest_recommendation_service import InterestRecommendationService


class TestSimilarityMatching:
    """Test Step 2: Semantic Interest Matching"""

    @pytest.fixture
    def setup(self):
        self.similarity_engine = SimilarityEngine()
        self.course_repo = CourseRecommendationRepository()
        self.courses = self.course_repo.get_all_courses()
        return self

    def test_ranking_by_similarity(self, setup):
        """Test that courses are ranked by similarity score"""
        student_input = "I love writing, literature, and creative storytelling"
        ranked = setup.similarity_engine.rank_courses_by_interest(
            student_input, setup.courses
        )

        # Should return all courses
        assert len(ranked) > 0
        print(f"\n✅ Found {len(ranked)} ranked courses")

        # Check ranking order (should be descending)
        scores = [score for _, score in ranked]
        assert scores == sorted(scores, reverse=True)
        print(f"✅ Courses ranked in descending order: {scores[:3]} ... ")

        return ranked[:5]

    def test_courses_with_threshold(self, setup):
        """Test filtering courses by similarity threshold"""
        student_input = "data science, machine learning, artificial intelligence"
        filtered = setup.similarity_engine.filter_courses_by_similarity(
            student_input, setup.courses, threshold=0.3
        )

        print(f"\n✅ Filtered {len(filtered)} courses above threshold 0.3")
        for course, score in filtered[:3]:
            print(f"   - {course.course_name}: {score:.2%} match")

    def test_various_student_inputs(self, setup):
        """Test matching works with various input formats"""
        test_inputs = [
            ("I'm interested in coding and software development", "Technical"),
            ("arts and history fascinates me", "Humanistic"),
            ("business management team leadership", "Business-focused"),
            ("healthcare medical science biology", "Science"),
            ("creative writing storytelling literature", "Creative"),
        ]

        print("\n📊 Testing various student inputs:")
        for student_input, category in test_inputs:
            ranked = setup.similarity_engine.rank_courses_by_interest(
                student_input, setup.courses[:10]
            )
            top_course = ranked[0] if ranked else None
            if top_course:
                print(
                    f"   {category:15} → {top_course[0].course_name} ({top_course[1]:.1%})"
                )


class TestKeywordExtraction:
    """Test keyword extraction and overlap detection"""

    @pytest.fixture
    def setup(self):
        self.explanation_engine = ExplanationEngine()
        self.course_repo = CourseRecommendationRepository()
        return self

    def test_keyword_extraction(self, setup):
        """Test extracting overlapping keywords"""
        student_input = "I love writing, creative thinking, and public speaking"
        course = setup.course_repo.get_course_by_code("19")  # Arts course

        keywords = setup.explanation_engine.extract_overlapping_keywords(
            student_input, course, max_keywords=5
        )

        print(f"\n📝 Keyword Extraction Test:")
        print(f"   Student input: '{student_input}'")
        print(f"   Course: {course.course_name}")
        print(f"   ✅ Extracted keywords: {keywords}")

        assert len(keywords) > 0
        return keywords

    def test_multiple_courses_keyword_extraction(self, setup):
        """Test keyword extraction for multiple courses"""
        student_input = (
            "data analysis, problem solving, business decision making, leadership"
        )
        courses = setup.course_repo.get_all_courses()[:5]

        print(f"\n🔍 Multiple Courses Keyword Extraction:")
        print(f"   Student input: '{student_input}'")
        print(f"   Courses tested:")

        for course in courses:
            keywords = setup.explanation_engine.extract_overlapping_keywords(
                student_input, course, max_keywords=3
            )
            if keywords:
                print(f"   ✅ {course.course_name:30} → {keywords}")


class TestFullPipeline:
    """Test complete 3-step pipeline (eligibility → matching → explanation)"""

    @pytest.fixture
    def setup(self):
        self.service = InterestRecommendationService()
        self.course_repo = CourseRecommendationRepository()
        return self

    def test_input_validation(self, setup):
        """Test input validation rules"""
        test_cases = [
            ("", False),  # Empty
            ("too short", False),  # Less than 10 chars
            ("I love learning", True),  # Valid
            ("x" * 2001, False),  # Over 2000 chars
        ]

        print("\n✓ Input Validation:")
        for input_text, expected_valid in test_cases:
            is_valid, error = setup.service.validate_input(input_text)
            status = "✅" if is_valid == expected_valid else "❌"
            print(f"   {status} '{input_text[:30]}...' → Valid: {is_valid}")

    def test_pipeline_with_real_input(self, setup):
        """Test full pipeline with realistic student input"""
        student_input = "I'm passionate about analyzing data, solving complex problems, and understanding business trends. I enjoy working with numbers and making data-driven decisions."

        # Get all course codes for testing
        all_courses = setup.course_repo.get_all_courses()
        eligible_codes = [c.course_code for c in all_courses[:10]]

        print(f"\n🎯 Full Pipeline Test:")
        print(f"   Student Input: '{student_input}'")
        print(f"   Eligible Courses: {eligible_codes}")
        print(f"   Running 3-step pipeline...")

        recommendations = setup.service.get_interest_based_recommendations(
            student_input=student_input,
            eligible_course_codes=eligible_codes,
            max_results=5,
            explain=True,
        )

        print(f"\n   ✅ Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   {i}. {rec['course_name']} (Code: {rec['course_code']})")
            print(f"      Match Score: {rec['match_score_percentage']}%")
            print(f"      Matched Interests: {', '.join(rec['matched_interests'][:3])}")
            print(f"      Top Job Roles: {', '.join(rec['job_roles'][:2])}")
            print(f"      Industries: {', '.join(rec['industries'][:2])}")
            print(f"      🤖 AI Explanation: {rec['explanation'][:150]}...")

        return recommendations

    def test_various_student_profiles(self, setup):
        """Test pipeline with different student profiles"""
        profiles = [
            {
                "name": "Creative Student",
                "input": "I love music, performing arts, creative expression, and storytelling. I want to pursue a career in entertainment or media.",
            },
            {
                "name": "Tech-Minded Student",
                "input": "Python programming, AI, machine learning, software development fascinate me. I want to build innovative solutions.",
            },
            {
                "name": "Business Student",
                "input": "Marketing, business management, finance, and entrepreneurship are my passions. I want to run my own company.",
            },
            {
                "name": "Science Student",
                "input": "Biology, chemistry, problem-solving, research methodologies. I'm interested in medical or scientific careers.",
            },
        ]

        all_courses = setup.course_repo.get_all_courses()
        eligible_codes = [c.course_code for c in all_courses]

        print("\n\n📚 Testing Various Student Profiles:\n" + "=" * 80)

        for profile in profiles:
            print(f"\n🎓 {profile['name']}")
            print(f"   Input: {profile['input']}")

            is_valid, error = setup.service.validate_input(profile["input"])
            print(f"   Validation: {'✅ PASS' if is_valid else f'❌ FAIL: {error}'}")

            if is_valid:
                recommendations = setup.service.get_interest_based_recommendations(
                    student_input=profile["input"],
                    eligible_course_codes=eligible_codes,
                    max_results=3,
                    explain=True,
                )

                print(f"   Top 3 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(
                        f"      {i}. {rec['course_name']} - {rec['match_score_percentage']}%"
                    )
                    print(f"         Explanation: {rec['explanation'][:120]}...")

            print("-" * 80)


class TestExplanationQuality:
    """Test that explanations are meaningful and personalized"""

    @pytest.fixture
    def setup(self):
        self.explanation_engine = ExplanationEngine()
        self.course_repo = CourseRecommendationRepository()
        self.similarity_engine = SimilarityEngine()
        return self

    def test_explanation_generation(self, setup):
        """Test that explanations are generated properly"""
        student_input = "I love writing, critical thinking, and exploring human behavior through social sciences"

        courses = setup.course_repo.get_all_courses()
        ranked = setup.similarity_engine.rank_courses_by_interest(
            student_input, courses
        )

        print(f"\n📖 Explanation Quality Test:")
        print(f"   Student Input: {student_input}")

        # Generate explanations for top 3
        explanations = setup.explanation_engine.generate_explanations(
            student_input, ranked, max_courses=3
        )

        print(f"   ✅ Generated {len(explanations)} explanations:")
        for i, (course_code, explanation) in enumerate(explanations.items(), 1):
            course = setup.course_repo.get_course_by_code(course_code)
            print(f"\n      {i}. {course.course_name}")
            print(f"         {explanation}")

            # Verify explanation is meaningful
            assert len(explanation) > 20
            assert len(explanation) < 500  # Should be reasonably sized (not too long)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 TESTING 3-STEP RECOMMENDATION PIPELINE")
    print("=" * 80)
    print("Testing: Eligibility → Semantic Matching → Explainable AI")
    print("=" * 80)

    # Run tests with pytest
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
        ]
    )
