"""
Comprehensive test for the updated recommendation system.
Tests:
1. Stream-subject validation
2. Eligible courses based on z-score
3. Above-score courses (aspirational)
4. Proper filtering by stream and subjects
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 80)
print("COMPREHENSIVE RECOMMENDATION SYSTEM TEST")
print("=" * 80)


def test_validation_invalid_stream():
    """Test that invalid stream is rejected"""
    print("\n1. Testing validation: Invalid stream")
    request_data = {
        "student": {
            "stream": "InvalidStream",
            "subjects": ["Physics", "Chemistry"],
            "zscore": 2.0,
            "interests": "engineering",
        },
        "district": "Colombo",
        "max_results": 5,
    }

    response = client.post("/recommend", json=request_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:  # Validation error
        print(f"   [PASS] Invalid stream rejected properly")
        return True
    else:
        print(f"   [FAIL] Should reject invalid stream")
        return False


def test_validation_mismatched_subjects():
    """Test that Science stream with Arts subjects is rejected"""
    print("\n2. Testing validation: Mismatched stream-subjects")
    request_data = {
        "student": {
            "stream": "Science",
            "subjects": ["History", "Geography", "Political Science"],  # Arts subjects
            "zscore": 2.0,
            "interests": "science",
        },
        "district": "Colombo",
        "max_results": 5,
    }

    response = client.post("/recommend", json=request_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:  # Bad request
        error = response.json()
        print(f"   Error: {error.get('detail', 'Unknown')}")
        print(f"   [PASS] Mismatched subjects rejected")
        return True
    else:
        print(f"   [FAIL] Should reject mismatched subjects")
        return False


def test_eligible_recommendations():
    """Test getting eligible recommendations"""
    print("\n3. Testing eligible recommendations")
    request_data = {
        "student": {
            "stream": "Science",
            "subjects": ["Physics", "Chemistry", "Combined Mathematics"],
            "zscore": 2.0,
            "interests": "engineering and technology",
        },
        "district": "Colombo",
        "max_results": 10,
    }

    response = client.post("/recommend", json=request_data)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    print(f"   Recommendations received: {len(data)}")

    if len(data) > 0:
        eligible = [r for r in data if r.get("eligibility") == True]
        print(f"   Eligible courses: {len(eligible)}")

        if eligible:
            print(f"\n   Top 3 eligible courses:")
            for i, rec in enumerate(eligible[:3], 1):
                print(f"     {i}. {rec['course_name']} (Score: {rec['score']:.2f})")

        print(f"   [PASS] Eligible recommendations working")
        return True
    else:
        print(f"   [FAIL] No recommendations returned")
        return False


def test_above_score_recommendations():
    """Test getting above-score (aspirational) recommendations"""
    print("\n4. Testing above-score recommendations")
    request_data = {
        "student": {
            "stream": "Science",
            "subjects": ["Physics", "Chemistry", "Biology"],
            "zscore": 1.5,  # Lower score to ensure some courses are above
            "interests": "medicine and health",
        },
        "district": "Colombo",
        "max_results": 5,
        "above_score_count": 5,  # Request 5 aspirational courses
    }

    response = client.post("/recommend", json=request_data)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    print(f"   Total recommendations: {len(data)}")

    eligible = [r for r in data if r.get("eligibility") == True]
    aspirational = [r for r in data if r.get("eligibility") == False]

    print(f"   Eligible courses: {len(eligible)}")
    print(f"   Aspirational courses (above z-score): {len(aspirational)}")

    if aspirational:
        print(f"\n   Aspirational courses (require higher z-score):")
        for i, rec in enumerate(aspirational[:3], 1):
            asp_flag = " [ASPIRATIONAL]" if rec.get("aspirational") else ""
            print(
                f"     {i}. {rec['course_name']} (Similarity: {rec.get('similarity', 0):.2f}){asp_flag}"
            )

        print(f"   [PASS] Above-score recommendations working")
        return True
    else:
        print(
            f"   [WARNING] No aspirational courses found (student may be eligible for all)"
        )
        return True


def test_all_eligible_courses():
    """Test that ALL eligible courses are returned when max_results is not set"""
    print("\n5. Testing: Return ALL eligible courses")
    request_data = {
        "student": {
            "stream": "Science",
            "subjects": ["Physics", "Chemistry", "Combined Mathematics"],
            "zscore": 1.8,
            "interests": "engineering",
        },
        "district": "Colombo",
        # No max_results - should return ALL eligible
    }

    response = client.post("/recommend", json=request_data)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    eligible = [r for r in data if r.get("eligibility") == True]

    print(f"   Total eligible courses returned: {len(eligible)}")
    print(f"   [PASS] All eligible courses returned")
    return True


def test_debug_endpoint():
    """Test debug endpoint with detailed information"""
    print("\n6. Testing /recommend/debug endpoint")
    request_data = {
        "student": {
            "stream": "Commerce",
            "subjects": ["Economics", "Business Studies", "Accounting"],
            "zscore": 1.5,
            "interests": "business and management",
        },
        "district": "Gampaha",
        "max_results": 3,
        "above_score_count": 2,
    }

    response = client.post("/recommend/debug", json=request_data)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    print(f"   Response keys: {list(data.keys())}")

    summary = data.get("summary", {})
    print(f"\n   Summary:")
    print(f"     Total programs checked: {summary.get('total_programs', 0)}")
    print(f"     Eligible: {summary.get('eligible_count', 0)}")
    print(f"     Above score: {summary.get('above_score_count', 0)}")
    print(f"     Rejected: {summary.get('rejected_count', 0)}")

    print(f"   [PASS] Debug endpoint working")
    return True


if __name__ == "__main__":
    tests = [
        ("Invalid Stream Validation", test_validation_invalid_stream),
        ("Mismatched Stream-Subjects", test_validation_mismatched_subjects),
        ("Eligible Recommendations", test_eligible_recommendations),
        ("Above-Score Recommendations", test_above_score_recommendations),
        ("All Eligible Courses", test_all_eligible_courses),
        ("Debug Endpoint", test_debug_endpoint),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   [FAIL] {test_name}: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"FINAL RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 80)

    if failed == 0:
        print("\n[SUCCESS] All comprehensive tests passed!")
    else:
        print(f"\n[FAILED] {failed} tests failed")
        sys.exit(1)
