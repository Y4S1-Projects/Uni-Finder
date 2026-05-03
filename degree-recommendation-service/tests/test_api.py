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
    print("[PASS] Health check passed")


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
    print(f"[PASS] Courses endpoint returned {data['total_count']} courses")


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
    print(f"   Streams: {', '.join(data['streams'][:5])}...")


def test_districts_endpoint():
    """Test districts list endpoint"""
    print("\nTesting /api/districts endpoint...")
    response = client.post("/api/districts", json={})
    assert response.status_code == 200
    data = response.json()
    assert "districts" in data
    assert len(data["districts"]) == 25  # Should have 25 districts
    print(f"[PASS] Districts endpoint returned {len(data['districts'])} districts")
    print(f"[PASS] Districts endpoint returned {len(data['districts'])} districts")


def test_universities_endpoint():
    """Test universities list endpoint"""
    print("\nTesting /api/universities endpoint...")
    response = client.post("/api/universities", json={})
    assert response.status_code == 200
    data = response.json()
    assert "universities" in data
    print(
        f"[PASS] Universities endpoint returned {len(data['universities'])} universities"
    )


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
    print(f"[PASS] Course by code endpoint returned: {data['course_name']}")


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
        print(f"   - {offering['university']}: {offering['cutoff_zscore']}")


def test_stream_filter():
    """Test filtering courses by stream"""
    print("\nTesting /api/courses/by-stream endpoint...")
    response = client.post("/api/courses/by-stream", json={"stream": "Science"})
    assert response.status_code == 200
    data = response.json()
    print(
        f"[PASS] Stream filter endpoint returned {data['total_count']} Science courses"
    )


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
    print(f"[PASS] Search endpoint returned {data['total_count']} matching courses")


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
    assert isinstance(data, dict), f"Expected dict but got {type(data)}"
    assert "eligible_recommendations" in data, "No recommendations returned"

    recs = data["eligible_recommendations"]
    print(f"[PASS] Recommendation endpoint returned {len(recs)} eligible courses")

    if recs:
        first = recs[0]
        print(
            f"   Top match: {first.get('course_name')} (score: {first.get('score', 0):.2f})"
        )

    return None


def test_ol_recommendation_missing_input():
    """Test O/L endpoint validation for missing student input"""
    response = client.post(
        "/recommend/interests",
        json={
            "eligible_courses": ["19", "20"],
            "max_results": 5,
            "explain": True,
        },
    )
    assert response.status_code == 422


def test_ol_recommendation_short_input():
    """Test O/L endpoint validation for input that is too short"""
    response = client.post(
        "/recommend/interests",
        json={
            "student_input": "short",
            "eligible_courses": ["19"],
            "max_results": 5,
            "explain": True,
        },
    )
    assert response.status_code == 422


def test_ol_recommendation_success():
    """Test O/L endpoint success"""
    response = client.post(
        "/recommend/interests",
        json={
            "student_input": "I love writing and creative expression",
            "eligible_courses": ["19", "20"],
            "max_results": 2,
            "explain": False,  # Skip explanation to save Gemini API calls during tests
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
