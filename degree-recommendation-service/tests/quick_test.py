#!/usr/bin/env python3
"""
Quick smoke test to validate updated test scenarios
Tests the main scenarios with new UGC-compliant streams and subjects
"""

import requests
import json
import sys
from datetime import datetime

RECOMMEND_ENDPOINT = "http://127.0.0.1:5001/recommend"


def test_scenario(name, payload, should_pass=True):
    """Test a single scenario"""
    try:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"Stream: {payload['student']['stream']}")
        print(f"Subjects: {payload['student']['subjects']}")

        response = requests.post(RECOMMEND_ENDPOINT, json=payload, timeout=15)

        print(f"Response: {response.status_code}")

        if should_pass:
            if response.status_code == 200:
                data = response.json()
                num_results = len(data) if isinstance(data, list) else 0
                print(f"✅ PASS - Got {num_results} recommendations")
                return True
            else:
                error = response.json().get("detail", response.text)
                print(f"❌ FAIL - Expected 200 but got {response.status_code}")
                print(f"Error: {error}")
                return False
        else:
            if response.status_code != 200:
                error = response.json().get("detail", response.text)
                print(
                    f"✅ PASS - Correctly rejected (expected 400, got {response.status_code})"
                )
                print(f"Error: {error}")
                return True
            else:
                print(f"❌ FAIL - Expected failure but got 200")
                return False

    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    print("🚀 Quick Smoke Test for Updated Scenarios")
    print(f"Backend: {RECOMMEND_ENDPOINT}")
    print(f"Time: {datetime.now()}")

    # Test valid scenarios
    tests = [
        # S1: Basic stream + subjects + district
        (
            "S1.1 - Physical Science (Core: Math+Physics+Chemistry)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            True,
        ),
        # S1: Arts
        (
            "S1.2 - Arts (3 valid subjects)",
            {
                "student": {
                    "stream": "Arts",
                    "subjects": ["History", "Geography", "Economics"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Kandy",
                "max_results": 5,
            },
            True,
        ),
        # S2: With Z-Score
        (
            "S2.1 - Biological Science with Z-Score",
            {
                "student": {
                    "stream": "Biological Science",
                    "subjects": ["Biology", "Chemistry", "Physics"],
                    "zscore": 1.5,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            True,
        ),
        # S4: With Interests (no Z-Score)
        (
            "S4.1 - Physical Science with Interests",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": [
                        "Combined Mathematics",
                        "Physics",
                        "Information & Communication Technology",
                    ],
                    "zscore": None,
                    "interests": "Interested in AI and machine learning",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            True,
        ),
        # S5: All fields
        (
            "S5.1 - Commerce (all fields)",
            {
                "student": {
                    "stream": "Commerce",
                    "subjects": ["Accounting", "Business Studies", "Economics"],
                    "zscore": 2.0,
                    "interests": "Interested in business and entrepreneurship",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            True,
        ),
        # Edge case: Invalid stream-subject combo
        (
            "EC5 - Invalid subjects for Physical Science (should fail)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Accounting", "Business Studies", "Economics"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            False,
        ),
        # Edge case: Z-Score out of range
        (
            "EC3 - Z-Score out of range 3.5 (should fail)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": 3.5,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            False,
        ),
        # Engineering Technology
        (
            "S1 - Engineering Technology",
            {
                "student": {
                    "stream": "Engineering Technology",
                    "subjects": [
                        "Engineering Technology",
                        "Science for Technology",
                        "English",
                    ],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 5,
            },
            True,
        ),
    ]

    passed = 0
    failed = 0

    for test_name, payload, should_pass in tests:
        if test_scenario(test_name, payload, should_pass):
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Pass Rate: {passed * 100 // (passed + failed)}%")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
