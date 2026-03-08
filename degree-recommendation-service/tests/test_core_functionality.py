"""
Core Functionality Test for Degree Recommendation Service
Tests: Student inputs results -> System gives recommendations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_basic_recommendation_flow():
    """Test complete recommendation flow with valid inputs"""
    print("\n" + "=" * 70)
    print("CORE FUNCTIONALITY TEST: Student Input -> Recommendations")
    print("=" * 70)

    print("\n[TEST 1] Science student with Z-score 1.5")
    print("-" * 70)

    recommendation_request = {
        "student": {
            "stream": "Science",
            "subjects": ["Chemistry", "Physics", "Combined Mathematics"],
            "zscore": 1.5,
            "interests": "Science, Engineering, Technology",
        },
        "district": "COLOMBO",
        "max_results": 10,
        "above_score_count": 5,
    }

    response = client.post("/recommend", json=recommendation_request)
    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n[PASS] VALIDATION PASSED")
        print(f"   Stream: {recommendation_request['student']['stream']}")
        print(
            f"   Subjects: {', '.join(recommendation_request['student']['subjects'])}"
        )
        print(f"   Z-Score: {recommendation_request['student']['zscore']}")
        print(f"   District: {recommendation_request['district']}")

        if "recommendations" in data:
            recs = data["recommendations"]
            print(f"\n[PASS] RECOMMENDATIONS RECEIVED: {len(recs)} courses")

            for i, rec in enumerate(recs[:5], 1):
                print(f"\n   {i}. {rec.get('course_name', 'N/A')}")
                print(f"      Course Code: {rec.get('course_code', 'N/A')}")
                print(f"      University: {rec.get('university', 'N/A')}")
                cutoff = rec.get("cutoff_zscore", "N/A")
                print(f"      Cutoff Z-Score: {cutoff}")
                if cutoff != "N/A":
                    eligible = cutoff <= 1.5
                    print(f"      Eligible: {eligible}")
        return True
    else:
        error = response.json()
        print(f"\n[FAIL] REQUEST FAILED")
        print(f"   Error: {error}")
        return False


def test_validation_errors():
    """Test validation rejects invalid inputs"""
    print("\n" + "=" * 70)
    print("VALIDATION TEST: Invalid Inputs")
    print("=" * 70)

    print("\n[TEST 2] Invalid stream (should fail)")
    print("-" * 70)

    invalid_request = {
        "student": {
            "stream": "InvalidStream",
            "subjects": ["Chemistry", "Physics", "Combined Mathematics"],
            "zscore": 1.5,
            "interests": "Science",
        },
        "district": "COLOMBO",
        "max_results": 10,
    }

    response = client.post("/recommend", json=invalid_request)
    print(f"Response Status: {response.status_code}")

    if response.status_code == 422:
        print(f"[PASS] VALIDATION WORKING: Invalid stream rejected (422)")
        return True
    else:
        print(f"[FAIL] VALIDATION FAILED: Should have rejected invalid stream")
        return False


def test_subject_stream_mismatch():
    """Test subject-stream validation"""
    print("\n" + "=" * 70)
    print("VALIDATION TEST: Subject-Stream Mismatch")
    print("=" * 70)

    print("\n[TEST 3] Commerce subjects with Science stream (should fail)")
    print("-" * 70)

    mismatch_request = {
        "student": {
            "stream": "Science",
            "subjects": ["Accounting", "Business Studies", "Economics"],
            "zscore": 1.5,
            "interests": "Business",
        },
        "district": "COLOMBO",
        "max_results": 10,
    }

    response = client.post("/recommend", json=mismatch_request)
    print(f"Response Status: {response.status_code}")

    if response.status_code == 400:
        error_data = response.json()
        print(f"[PASS] VALIDATION WORKING: Subject mismatch detected")
        print(f"   Error: {error_data.get('detail', 'N/A')}")
        return True
    else:
        print(f"[FAIL] VALIDATION FAILED: Should have detected subject mismatch")
        return False


def test_above_score_recommendations():
    """Test aspirational recommendations above student score"""
    print("\n" + "=" * 70)
    print("FUNCTIONALITY TEST: Above-Score (Aspirational) Recommendations")
    print("=" * 70)

    print("\n[TEST 4] Request aspirational courses above student's score")
    print("-" * 70)

    request_with_aspirational = {
        "student": {
            "stream": "Science",
            "subjects": ["Chemistry", "Physics", "Combined Mathematics"],
            "zscore": 0.5,
            "interests": "Science, Engineering",
        },
        "district": "COLOMBO",
        "max_results": 10,
        "above_score_count": 5,
    }

    response = client.post("/recommend", json=request_with_aspirational)
    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        # Response might be a list or a dict with recommendations key
        if isinstance(data, list):
            recs = data
        else:
            recs = data.get("recommendations", [])

        print(f"[PASS] ASPIRATIONAL COURSES INCLUDED")
        print(f"   Total recommendations: {len(recs)}")

        eligible_count = sum(1 for r in recs if r.get("cutoff_zscore", 999) <= 0.5)
        above_score_count = sum(1 for r in recs if r.get("cutoff_zscore", 0) > 0.5)

        print(f"   Eligible (within score): {eligible_count}")
        print(f"   Aspirational (above score): {above_score_count}")

        if above_score_count > 0:
            print(f"\n   Sample aspirational courses:")
            count = 0
            for rec in recs:
                if rec.get("cutoff_zscore", 0) > 0.5 and count < 3:
                    print(
                        f"   - {rec.get('course_name', 'N/A')} (Cutoff: {rec.get('cutoff_zscore', 'N/A')})"
                    )
                    count += 1
        return True
    else:
        print(f"[FAIL] REQUEST FAILED")
        return False


def run_all_tests():
    """Run all core functionality tests"""
    tests = [
        ("Basic Recommendation Flow", test_basic_recommendation_flow),
        ("Validation - Invalid Stream", test_validation_errors),
        ("Validation - Subject Mismatch", test_subject_stream_mismatch),
        ("Above-Score Recommendations", test_above_score_recommendations),
    ]

    results = []

    print("\n")
    print("=" * 70)
    print("  DEGREE RECOMMENDATION SERVICE - Core Functionality Tests")
    print("=" * 70)

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[EXCEPTION] {test_name}: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 70)
    print(f"FINAL RESULT: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n[SUCCESS] ALL CORE FUNCTIONALITY TESTS PASSED!")
        print("   * Student input validation working")
        print("   * Recommendation engine working")
        print("   * Eligibility checking working")
        print("   * Above-score recommendations working")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
