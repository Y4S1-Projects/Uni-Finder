#!/usr/bin/env python3
"""
Simplified Comprehensive Testing Suite for updated test payloads
Runs selected tests from each scenario to validate UGC-compliant validator
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:5001"
RECOMMEND_ENDPOINT = f"{BACKEND_URL}/recommend"


def test_batch(scenario_name, tests):
    """Test a batch of scenarios"""
    print(f"\n{'='*70}")
    print(f"Testing: {scenario_name}")
    print(f"{'='*70}")

    passed = 0
    failed = 0

    for test_name, payload, expect_success in tests:
        try:
            response = requests.post(RECOMMEND_ENDPOINT, json=payload, timeout=10)

            if expect_success:
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    print(f"  ✅ {test_name}: Got {count} results")
                    passed += 1
                else:
                    error = response.json().get("detail", response.text)[:100]
                    print(
                        f"  ❌ {test_name}: Expected 200, got {response.status_code} - {error}"
                    )
                    failed += 1
            else:
                if response.status_code != 200:
                    print(
                        f"  ✅ {test_name}: Correctly rejected ({response.status_code})"
                    )
                    passed += 1
                else:
                    print(f"  ❌ {test_name}: Should have failed but got 200")
                    failed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: ERROR - {str(e)[:80]}")
            failed += 1

    return passed, failed


def main():
    print(f"🚀 Quick Comprehensive Test Suite")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now()}")

    total_passed = 0
    total_failed = 0

    # S1: Stream + Subjects + District
    s1_tests = [
        (
            "Physical Science (CMath, Physics, Chem)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
        (
            "Arts (History, Geo, Econ)",
            {
                "student": {
                    "stream": "Arts",
                    "subjects": ["History", "Geography", "Economics"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Kandy",
                "max_results": 3,
            },
            True,
        ),
        (
            "Commerce (Acct, BS, Econ)",
            {
                "student": {
                    "stream": "Commerce",
                    "subjects": ["Accounting", "Business Studies", "Economics"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Galle",
                "max_results": 3,
            },
            True,
        ),
    ]
    p, f = test_batch("S1: Stream + Subjects + District", s1_tests)
    total_passed += p
    total_failed += f

    # S2: With Z-Score
    s2_tests = [
        (
            "Physical Science (Z=2.5)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": 2.5,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
        (
            "Biological Science (Z=1.5)",
            {
                "student": {
                    "stream": "Biological Science",
                    "subjects": ["Biology", "Chemistry", "Physics"],
                    "zscore": 1.5,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
    ]
    p, f = test_batch("S2: With Z-Score", s2_tests)
    total_passed += p
    total_failed += f

    # S4: With Interests (no Z-Score)
    s4_tests = [
        (
            "Physical Science + Interests",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": [
                        "Combined Mathematics",
                        "Physics",
                        "Information & Communication Technology",
                    ],
                    "zscore": None,
                    "interests": "AI and programming",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
        (
            "Biological Science + Interests",
            {
                "student": {
                    "stream": "Biological Science",
                    "subjects": ["Biology", "Chemistry", "Agricultural Science"],
                    "zscore": None,
                    "interests": "Medicine and healthcare",
                },
                "district": "Kandy",
                "max_results": 3,
            },
            True,
        ),
    ]
    p, f = test_batch("S4: With Interests (no Z-Score)", s4_tests)
    total_passed += p
    total_failed += f

    # S5: All Fields
    s5_tests = [
        (
            "Physical Science (All fields)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": 2.0,
                    "interests": "Engineering",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
        (
            "Commerce (All fields)",
            {
                "student": {
                    "stream": "Commerce",
                    "subjects": ["Accounting", "Business Studies", "Economics"],
                    "zscore": 1.8,
                    "interests": "Entrepreneurship",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
    ]
    p, f = test_batch("S5: All Fields", s5_tests)
    total_passed += p
    total_failed += f

    # Edge Cases
    edge_tests = [
        (
            "Invalid Stream",
            {
                "student": {
                    "stream": "InvalidStream",
                    "subjects": ["Physics", "Chemistry", "Math"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            False,
        ),
        (
            "Z-Score too high (3.5)",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                    "zscore": 3.5,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            False,
        ),
        (
            "Invalid subjects for Physical Science",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": ["Accounting", "Business Studies", "Economics"],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            False,
        ),
        (
            "Empty subjects list",
            {
                "student": {
                    "stream": "Physical Science",
                    "subjects": [],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            False,
        ),
    ]
    p, f = test_batch("Edge Cases", edge_tests)
    total_passed += p
    total_failed += f

    # Technology Streams
    tech_tests = [
        (
            "Engineering Technology",
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
                "max_results": 3,
            },
            True,
        ),
        (
            "Bio-Systems Technology",
            {
                "student": {
                    "stream": "Bio-Systems Technology",
                    "subjects": [
                        "Bio-Systems Technology",
                        "Science for Technology",
                        "Agricultural Science",
                    ],
                    "zscore": None,
                    "interests": "",
                },
                "district": "Colombo",
                "max_results": 3,
            },
            True,
        ),
    ]
    p, f = test_batch("Technology Streams", tech_tests)
    total_passed += p
    total_failed += f

    # Summary
    print(f"\n{'='*70}")
    print(f"📊 OVERALL SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    if total_passed + total_failed > 0:
        print(f"Pass Rate: {total_passed * 100 // (total_passed + total_failed)}%")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    exit(main())
