"""
Test API endpoints for the updated degree recommendation service
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("[PASS] Health check passed")
    return True


def test_courses_endpoint():
    """Test courses list endpoint"""
    print("\nTesting /api/courses endpoint...")
    response = client.post("/api/courses", json={})
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "courses" in data
    assert data["total_count"] > 0
    print(f"[PASS] Courses endpoint returned {data['total_count']} courses")
    return True


def test_streams_endpoint():
    """Test streams list endpoint"""
    print("\nTesting /api/streams endpoint...")
    response = client.post("/api/streams", json={})
    assert response.status_code == 200
    data = response.json()
    assert "streams" in data
    assert len(data["streams"]) > 0
    print(f"[PASS] Streams endpoint returned {len(data['streams'])} streams")
    print(f"   Streams: {', '.join(data['streams'][:5])}...")
    return True


def test_districts_endpoint():
    """Test districts list endpoint"""
    print("\nTesting /api/districts endpoint...")
    response = client.post("/api/districts", json={})
    assert response.status_code == 200
    data = response.json()
    assert "districts" in data
    assert len(data["districts"]) == 25  # Should have 25 districts
    print(f"[PASS] Districts endpoint returned {len(data['districts'])} districts")
    return True


def test_universities_endpoint():
    """Test universities list endpoint"""
    print("\nTesting /api/universities endpoint...")
    response = client.post("/api/universities", json={})
    assert response.status_code == 200
    data = response.json()
    assert "universities" in data
    assert len(data["universities"]) > 0
    print(
        f"[PASS] Universities endpoint returned {len(data['universities'])} universities"
    )
    return True


def test_course_by_code():
    """Test getting course by code"""
    print("\nTesting /api/courses/by-code endpoint...")
    # Using course code 001 (Medicine) - normalized to 3-digit format
    response = client.post("/api/courses/by-code", json={"course_code": "001"})
    assert response.status_code == 200
    data = response.json()
    assert data["course_code"] == "001"
    assert data["course_name"] == "Medicine"
    print(f"[PASS] Course by code endpoint returned: {data['course_name']}")
    return True


def test_course_cutoffs():
    """Test getting cutoffs for a course"""
    print("\nTesting /api/courses/cutoffs endpoint...")
    # Using course code 001 (Medicine) in Colombo district
    response = client.post(
        "/api/courses/cutoffs",
        json={"course_code": "001", "district": "COLOMBO"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "offerings" in data
    assert len(data["offerings"]) > 0
    print(f"[PASS] Course cutoffs endpoint returned {len(data['offerings'])} offerings")
    for offering in data["offerings"][:2]:
        print(f"   - {offering['university']}: {offering['cutoff_zscore']}")
    return True


def test_stream_filter():
    """Test filtering courses by stream"""
    print("\nTesting /api/courses/by-stream endpoint...")
    response = client.post("/api/courses/by-stream", json={"stream": "Science"})
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    print(
        f"[PASS] Stream filter endpoint returned {data['total_count']} Science courses"
    )
    return True


def test_search_endpoint():
    """Test searching courses using body parameters"""
    print("\nTesting /api/search endpoint...")
    response = client.post(
        "/api/search",
        json={"q": "engineering", "stream": "Science"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    assert "total_count" in data
    print(f"[PASS] Search endpoint returned {data['total_count']} matching courses")
    return True


def test_recommendation_endpoint():
    """Test the recommendation endpoint"""
    print("\nTesting /recommend endpoint...")

    request_data = {
        "student": {
            "stream": "Science",
            "subjects": ["Physics", "Chemistry", "Combined Mathematics"],
            "zscore": 2.0,
            "interests": "medicine and health",
        },
        "district": "Colombo",
        "max_results": 5,
    }

    response = client.post("/recommend", json=request_data)
    assert response.status_code == 200
    data = response.json()
    # The endpoint returns a list directly (not wrapped in a dict)
    assert isinstance(data, list), f"Expected list but got {type(data)}"
    assert len(data) > 0, "No recommendations returned"
    print(f"[PASS] Recommendation endpoint returned {len(data)} eligible courses")

    if data:
        first = data[0]
        print(f"   Top match: {first['course_name']} (score: {first['score']:.2f})")

    return True


if __name__ == "__main__":
    print("\n>>> Testing API Endpoints\n")

    tests = [
        ("Health Check", test_health_endpoint),
        ("Courses List", test_courses_endpoint),
        ("Streams", test_streams_endpoint),
        ("Districts", test_districts_endpoint),
        ("Universities", test_universities_endpoint),
        ("Course By Code", test_course_by_code),
        ("Course Cutoffs", test_course_cutoffs),
        ("Stream Filter", test_stream_filter),
        ("Search", test_search_endpoint),
        ("Recommendations", test_recommendation_endpoint),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_name} failed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    if failed == 0:
        print("[SUCCESS] All API tests passed!\n")
    else:
        print(f"[FAILED] {failed} tests failed\n")
        sys.exit(1)
