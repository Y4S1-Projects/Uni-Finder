#!/usr/bin/env python
# test_api_live.py
"""
Quick test of the live API endpoint
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"


def test_api():
    print("\n" + "=" * 80)
    print("🌐 LIVE API ENDPOINT TEST")
    print("=" * 80)

    # Test health check first
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   ✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server not responding: {e}")
        return

    # Test the recommendation endpoint
    print("\n2️⃣ Testing /recommend/interests endpoint...")

    request_data = {
        "student_input": "I love creative writing, performing arts, storytelling, and expressing myself through media and journalism",
        "eligible_courses": ["19", "20", "41", "21", "68"],
        "max_results": 3,
        "explain": True,
    }

    print(f"\n📤 REQUEST:")
    print(json.dumps(request_data, indent=2))

    try:
        print(f"\n⏳ Sending request to API...")
        response = requests.post(
            f"{BASE_URL}/recommend/interests", json=request_data, timeout=30
        )

        print(f"\n✅ Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n📊 RESPONSE DATA:")
            print(f"   Student Input: {data['student_input'][:50]}...")
            print(f"   Eligible Courses: {data['eligible_courses_count']}")
            print(f"   Recommendations Returned: {len(data['recommendations'])}")

            print(f"\n📋 TOP 3 RECOMMENDATIONS:")
            for i, rec in enumerate(data["recommendations"], 1):
                print(f"\n   {i}. {rec['course_name']} (Code: {rec['course_code']})")
                print(f"      Match Score: {rec['match_score_percentage']}%")
                print(f"      Stream: {rec['stream']}")

                if rec.get("matched_interests"):
                    interests = ", ".join(rec["matched_interests"][:3])
                    print(f"      Matched: {interests}")

                if rec.get("job_roles"):
                    roles = ", ".join(rec["job_roles"][:2])
                    print(f"      Careers: {roles}")

                # Show AI explanation
                explanation = rec.get("explanation", "")
                if explanation:
                    print(f"      🤖 AI: {explanation[:120]}...")

            print("\n" + "=" * 80)
            print("✅ API TEST SUCCESSFUL - System working end-to-end!")
            print("=" * 80)
        else:
            print(f"❌ Error response:")
            print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("Waiting for API to be ready...")
    time.sleep(2)
    test_api()
