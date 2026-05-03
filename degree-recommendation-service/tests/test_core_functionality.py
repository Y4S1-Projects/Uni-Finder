import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_basic_recommendation_flow():
    """Test complete recommendation flow with valid inputs"""
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
    assert response.status_code == 200
    data = response.json()
    assert "eligible_recommendations" in data


def test_validation_invalid_stream():
    """Test validation rejects invalid stream"""
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
    assert response.status_code == 422


def test_validation_subject_mismatch():
    """Test subject-stream mismatch validation"""
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
    # The API throws a 400 when subjects don't map to the specified stream
    assert response.status_code == 400
    assert "detail" in response.json()


def test_above_score_aspirational_recommendations():
    """Test aspirational recommendations above student score"""
    request_with_aspirational = {
        "student": {
            "stream": "Biological Science",
            "subjects": ["Biology", "Chemistry", "Physics"],
            "zscore": 0.5,  # Deliberately low to force aspirational courses like Medicine
            "interests": "Science, Medicine",
        },
        "district": "COLOMBO",
        "max_results": 10,
        "above_score_count": 5,
    }

    response = client.post("/recommend", json=request_with_aspirational)
    assert response.status_code == 200
    data = response.json()

    # Due to very low z-score, top courses like Medicine should be aspirational
    above_score = data.get("above_score_recommendations", [])
    assert len(above_score) > 0


def test_zero_matches_gibberish():
    """Test that zero semantic matches correctly yield the global explanation fallback."""
    payload = {
        "student": {
            "stream": "Biological Science",
            "subjects": ["Biology", "Chemistry", "Physics"],
            "zscore": 1.5,
            "interests": "asdfghjkl",
        },
        "district": "COLOMBO",
        "max_results": 5,
    }

    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "summary" in data
    assert "global_explanation" in data["summary"]
    assert (
        "diverges from the standard pathways" in data["summary"]["global_explanation"]
    )


def test_zero_matches_stream_mismatch():
    """Test that valid but mismatched interests yield the global explanation fallback."""
    payload = {
        "student": {
            "stream": "Physical Science",
            "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
            "zscore": 1.8,
            "interests": "doctor surgeon medical hospital healthcare",  # Mismatch for Physical Science
        },
        "district": "COLOMBO",
        "max_results": 5,
    }

    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "summary" in data
    assert "global_explanation" in data["summary"]
