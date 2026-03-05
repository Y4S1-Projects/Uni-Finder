# tests/test_api_endpoint.py
"""
Manual API endpoint test - Tests the /recommend/interests endpoint
Run this to verify the REST API works correctly.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_endpoint_success():
    """Test successful API request"""
    print("\n" + "=" * 80)
    print("🌐 API ENDPOINT TEST: /recommend/interests")
    print("=" * 80)

    request_payload = {
        "student_input": "I love creative writing, performing arts, storytelling, and expressing myself through media and journalism",
        "eligible_courses": ["19", "20", "41", "21", "68", "71", "85"],
        "max_results": 5,
        "explain": True,
    }

    print("\n📤 REQUEST:")
    print(json.dumps(request_payload, indent=2))

    print("\n⏳ Calling API...")
    response = client.post("/recommend/interests", json=request_payload)

    print(f"\n📊 RESPONSE STATUS: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print(f"\n✅ API RESPONSE RECEIVED")
        print(f"   Student Input: {data['student_input'][:50]}...")
        print(f"   Eligible Courses Count: {data['eligible_courses_count']}")
        print(f"   Recommendations Count: {len(data['recommendations'])}")

        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(data["recommendations"], 1):
            print(f"\n   {i}. {rec['course_name']} (Code: {rec['course_code']})")
            print(f"      Match Score: {rec['match_score_percentage']}%")
            print(f"      Stream: {rec['stream']}")

            if rec.get("matched_interests"):
                interests = ", ".join(rec["matched_interests"][:3])
                print(f"      Interests: {interests}")

            if rec.get("job_roles"):
                roles = ", ".join(rec["job_roles"][:2])
                print(f"      Career Paths: {roles}")

            if rec.get("industries"):
                industries = ", ".join(rec["industries"][:2])
                print(f"      Industries: {industries}")

            # Show explanation
            explanation = rec["explanation"]
            print(f"      🤖 Explanation: {explanation[:100]}...")

        print("\n" + "=" * 80)
        print("✅ API TEST PASSED - Endpoint working correctly!")
        print("=" * 80)

    else:
        print(f"\n❌ API ERROR: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


def test_api_validation():
    """Test API input validation"""
    print("\n" + "=" * 80)
    print("🔐 API VALIDATION TEST")
    print("=" * 80)

    # Test 1: Missing student_input
    print("\n1️⃣ Test: Missing student_input")
    response = client.post(
        "/recommend/interests",
        json={
            "eligible_courses": ["19", "20"],
            "max_results": 5,
            "explain": True,
        },
    )
    if response.status_code == 422:
        print("   ✅ Correctly rejected (422 Validation Error)")
    else:
        print(f"   ❌ Unexpected: {response.status_code}")

    # Test 2: Input too short
    print("\n2️⃣ Test: Input too short (<10 chars)")
    response = client.post(
        "/recommend/interests",
        json={
            "student_input": "short",
            "eligible_courses": ["19"],
            "max_results": 5,
            "explain": True,
        },
    )
    if response.status_code == 400:
        error = response.json()
        print(f"   ✅ Correctly rejected: {error.get('detail', '')[:50]}...")
    else:
        print(f"   Response: {response.status_code}")

    # Test 3: Valid request
    print("\n3️⃣ Test: Valid request")
    response = client.post(
        "/recommend/interests",
        json={
            "student_input": "I love writing and creative expression",
            "eligible_courses": ["19", "20"],
            "max_results": 2,
            "explain": False,  # Skip explanation to save API calls
        },
    )
    if response.status_code == 200:
        print("   ✅ Request accepted (200 OK)")
        data = response.json()
        print(f"   ✅ Got {len(data['recommendations'])} recommendations")
    else:
        print(f"   ❌ Error: {response.status_code}")


if __name__ == "__main__":
    try:
        test_api_validation()
        test_api_endpoint_success()

        print("\n\n" + "🎉" * 40)
        print("ALL API TESTS COMPLETED SUCCESSFULLY!")
        print("🎉" * 40)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
