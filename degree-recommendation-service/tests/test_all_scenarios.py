"""
Comprehensive Testing Suite for A/L Degree Recommendation Engine
Tests all possible scenarios students can trigger through the wizard
"""

import requests
import json
from typing import Dict, List, Tuple, Any
import time
from datetime import datetime

# Backend API configuration
BACKEND_URL = "http://127.0.0.1:5001"
RECOMMEND_ENDPOINT = f"{BACKEND_URL}/recommend"
INTERESTS_ENDPOINT = f"{BACKEND_URL}/interests"

# Test data
test_results = []
test_start_time = datetime.now()

# Valid data pools (aligned with UGC flexible stream rules)
VALID_STREAMS = [
    "Physical Science",
    "Biological Science",
    "Commerce",
    "Engineering Technology",
    "Bio-Systems Technology",
    "Arts",
]
VALID_SUBJECTS = {
    "Physical Science": [
        "Combined Mathematics",
        "Physics",
        "Chemistry",
        "Information & Communication Technology",
        "Higher Mathematics",
    ],
    "Biological Science": [
        "Biology",
        "Chemistry",
        "Physics",
        "Agricultural Science",
        "Information & Communication Technology",
    ],
    "Commerce": [
        "Accounting",
        "Business Studies",
        "Economics",
        "Business Statistics",
        "Geography",
        "Political Science",
        "History",
        "Logic & Scientific Method",
        "English",
        "Information & Communication Technology",
        "Agricultural Science",
        "Combined Mathematics",
        "Physics",
        "French",
        "German",
    ],
    "Engineering Technology": [
        "Engineering Technology",
        "Science for Technology",
        "Information & Communication Technology",
        "Economics",
        "Geography",
        "Home Economics",
        "English",
        "Communication & Media Studies",
        "Art",
        "Business Studies",
        "Accounting",
        "Mathematics",
        "Agricultural Science",
    ],
    "Bio-Systems Technology": [
        "Bio-Systems Technology",
        "Science for Technology",
        "Information & Communication Technology",
        "Economics",
        "Geography",
        "Home Economics",
        "English",
        "Communication & Media Studies",
        "Art",
        "Business Studies",
        "Accounting",
        "Mathematics",
        "Agricultural Science",
    ],
    "Arts": [
        "History",
        "Geography",
        "Economics",
        "Political Science",
        "Logic",
        "English",
        "Sinhala",
        "Tamil",
        "Arabic",
        "French",
        "German",
        "Buddhism",
        "Hinduism",
        "Christianity",
        "Islam",
        "Art",
        "Dance",
        "Music",
        "Drama",
        "Home Economics",
        "Communication & Media Studies",
        "Information & Communication Technology",
        "Agricultural Science",
    ],
}
VALID_DISTRICTS = [
    "Colombo",
    "Gampaha",
    "Kalutara",
    "Matara",
    "Galle",
    "Hambantota",
    "Jaffna",
    "Mullaitivu",
    "Batticaloa",
    "Ampara",
    "Trincomalee",
    "Kurunegala",
    "Puttalum",
    "Anuradhapura",
    "Polonnaruwa",
    "Matale",
    "Kandy",
    "Nuwara Eliya",
    "Badulla",
    "Monaragala",
    "Ratnapura",
    "Kegalle",
]


class TestResult:
    """Store individual test result"""

    def __init__(
        self,
        test_name: str,
        scenario: str,
        status: str,
        response_code: int = None,
        response_data: Dict = None,
        error: str = None,
        request_payload: Dict = None,
    ):
        self.test_name = test_name
        self.scenario = scenario
        self.status = status  # "PASS", "FAIL", "ERROR"
        self.response_code = response_code
        self.response_data = response_data
        self.error = error
        self.request_payload = request_payload
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "scenario": self.scenario,
            "status": self.status,
            "response_code": self.response_code,
            "has_results": bool(self.response_data and "courses" in self.response_data),
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self):
        return f"[{self.status}] {self.test_name} (Scenario: {self.scenario}) - Code: {self.response_code}"


def make_request(
    endpoint: str, payload: Dict, test_name: str, scenario: str
) -> TestResult:
    """Make HTTP request and capture result"""
    try:
        print(f"\n📤 Testing: {test_name}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(endpoint, json=payload, timeout=10)

        print(f"   Response Code: {response.status_code}")

        # Try to parse JSON
        try:
            response_json = response.json()
        except:
            response_json = {"raw": response.text}

        print(f"   Response: {json.dumps(response_json, indent=2)[:200]}...")

        # Determine if test passed
        if response.status_code == 200:
            status = "PASS"
            error = None
        else:
            status = "FAIL"
            error = response_json.get("detail", response.text)

        result = TestResult(
            test_name=test_name,
            scenario=scenario,
            status=status,
            response_code=response.status_code,
            response_data=response_json,
            error=error,
            request_payload=payload,
        )
        test_results.append(result)
        return result

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        result = TestResult(
            test_name=test_name,
            scenario=scenario,
            status="ERROR",
            error=str(e),
            request_payload=payload,
        )
        test_results.append(result)
        return result


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================


class ScenarioTester:
    """Test each scenario with various input combinations"""

    @staticmethod
    def test_s1_stream_only():
        """
        Scenario S1: Stream + Subjects + District only (NO Z-Score, NO Interests)
        This is when student skips Steps 1 and 2
        """
        print("\n" + "=" * 80)
        print("SCENARIO S1: Stream + Subjects + District (No Z-Score, No Interests)")
        print("=" * 80)

        tests = [
            {
                "name": "S1.1 - Physical Science with Combined Mathematics, Physics, Chemistry",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S1.2 - Arts Stream with History, Geography, Economics",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": ["History", "Geography", "Economics"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Kandy",
                    "max_results": 5,
                },
            },
            {
                "name": "S1.3 - Commerce Stream with Accounting, Business Studies, Economics",
                "payload": {
                    "student": {
                        "stream": "Commerce",
                        "subjects": ["Accounting", "Business Studies", "Economics"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Galle",
                    "max_results": 8,
                },
            },
            {
                "name": "S1.4 - Physical Science with Combined Mathematics, Physics, Higher Mathematics",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [
                            "Combined Mathematics",
                            "Physics",
                            "Higher Mathematics",
                        ],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S1.5 - Arts with Logic, Geography, English (Jaffna)",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": [
                            "Logic",
                            "Geography",
                            "English",
                        ],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Jaffna",
                    "max_results": 10,
                },
            },
        ]

        for test in tests:
            make_request(RECOMMEND_ENDPOINT, test["payload"], test["name"], "S1")

    @staticmethod
    def test_s2_stream_zscore():
        """
        Scenario S2: Stream + Subjects + Z-Score (NO Interests)
        This is when student provides stream+subjects+zscore but skips interests
        """
        print("\n" + "=" * 80)
        print("SCENARIO S2: Stream + Subjects + Z-Score (No Interests)")
        print("=" * 80)

        tests = [
            {
                "name": "S2.1 - Physical Science with High Z-Score (2.5)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": 2.5,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S2.2 - Physical Science with Medium Z-Score (1.5)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": 1.5,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S2.3 - Biological Science with Low Z-Score (0.5)",
                "payload": {
                    "student": {
                        "stream": "Biological Science",
                        "subjects": ["Biology", "Chemistry", "Physics"],
                        "zscore": 0.5,
                        "interests": "",
                    },
                    "district": "Kandy",
                    "max_results": 10,
                },
            },
            {
                "name": "S2.4 - Arts with Z-Score (1.8)",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": ["History", "Geography", "Economics"],
                        "zscore": 1.8,
                        "interests": "",
                    },
                    "district": "Galle",
                    "max_results": 10,
                },
            },
            {
                "name": "S2.5 - Commerce with Negative Z-Score (-0.5)",
                "payload": {
                    "student": {
                        "stream": "Commerce",
                        "subjects": ["Accounting", "Business Studies", "Economics"],
                        "zscore": -0.5,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S2.6 - Physical Science with Z-Score = 0",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": 0,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
        ]

        for test in tests:
            make_request(RECOMMEND_ENDPOINT, test["payload"], test["name"], "S2")

    @staticmethod
    def test_s4_stream_interests():
        """
        Scenario S4: Stream + Subjects + Interests (NO Z-Score)
        This is when student provides interests but skips Z-Score
        """
        print("\n" + "=" * 80)
        print("SCENARIO S4: Stream + Subjects + Interests (No Z-Score)")
        print("=" * 80)

        tests = [
            {
                "name": "S4.1 - Physical Science with Engineering Interests",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": None,
                        "interests": "I am passionate about engineering, especially civil and structural design. I love solving complex problems and building infrastructure.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S4.2 - Biological Science with Medicine Interests",
                "payload": {
                    "student": {
                        "stream": "Biological Science",
                        "subjects": ["Biology", "Chemistry", "Physics"],
                        "zscore": None,
                        "interests": "Interested in medical field, healthcare, becoming a doctor. I love helping people and saving lives through medicine.",
                    },
                    "district": "Kandy",
                    "max_results": 10,
                },
            },
            {
                "name": "S4.3 - Arts with Literature and Language Interests",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": ["English", "History", "Economics"],
                        "zscore": None,
                        "interests": "I love literature, writing, and languages. Interested in academic research and teaching English at university level.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S4.4 - Commerce with Business Management Interests",
                "payload": {
                    "student": {
                        "stream": "Commerce",
                        "subjects": ["Accounting", "Business Studies", "Economics"],
                        "zscore": None,
                        "interests": "I want to start my own business. Interested in entrepreneurship, business management, and financial planning.",
                    },
                    "district": "Galle",
                    "max_results": 10,
                },
            },
            {
                "name": "S4.5 - Physical Science with IT/CS Interests",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [
                            "Combined Mathematics",
                            "Physics",
                            "Information & Communication Technology",
                        ],
                        "zscore": None,
                        "interests": "Passionate about computer science, programming, and software development. Want to work in AI and machine learning.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
        ]

        for test in tests:
            make_request(RECOMMEND_ENDPOINT, test["payload"], test["name"], "S4")

    @staticmethod
    def test_s5_all_fields():
        """
        Scenario S5: Stream + Subjects + Z-Score + Interests (ALL FIELDS)
        This is when student completes all 3 steps
        """
        print("\n" + "=" * 80)
        print("SCENARIO S5: Stream + Subjects + Z-Score + Interests (All Fields)")
        print("=" * 80)

        tests = [
            {
                "name": "S5.1 - Physical Science High Z-Score with Engineering Interests",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": 2.8,
                        "interests": "I am passionate about engineering, especially civil and structural design. I love solving complex problems and building infrastructure.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S5.2 - Biological Science Medium Z-Score with Medicine Interests",
                "payload": {
                    "student": {
                        "stream": "Biological Science",
                        "subjects": ["Biology", "Chemistry", "Physics"],
                        "zscore": 1.5,
                        "interests": "Interested in medical field, healthcare, becoming a doctor. I love helping people and saving lives through medicine.",
                    },
                    "district": "Kandy",
                    "max_results": 10,
                },
            },
            {
                "name": "S5.3 - Physical Science Low Z-Score with IT Interests",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [
                            "Combined Mathematics",
                            "Physics",
                            "Information & Communication Technology",
                        ],
                        "zscore": 0.3,
                        "interests": "Want to pursue computer science and information technology. Interested in software development and web applications.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S5.4 - Arts High Z-Score with Social Studies Interests",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": ["History", "Geography", "Economics"],
                        "zscore": 2.5,
                        "interests": "Deeply interested in sociology, social sciences, and international relations. Want to work for NGOs or government.",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "S5.5 - Commerce Medium Z-Score with Accounting Interests",
                "payload": {
                    "student": {
                        "stream": "Commerce",
                        "subjects": ["Accounting", "Business Studies", "Economics"],
                        "zscore": 1.6,
                        "interests": "Interested in accounting, auditing, and becoming a chartered accountant. Love numbers and financial analysis.",
                    },
                    "district": "Galle",
                    "max_results": 10,
                },
            },
        ]

        for test in tests:
            make_request(RECOMMEND_ENDPOINT, test["payload"], test["name"], "S5")

    @staticmethod
    def test_edge_cases():
        """Test edge cases and error conditions"""
        print("\n" + "=" * 80)
        print("EDGE CASES & VALIDATION TESTS")
        print("=" * 80)

        tests = [
            {
                "name": "EC1 - Invalid Stream",
                "payload": {
                    "student": {
                        "stream": "InvalidStream",
                        "subjects": ["Physics", "Chemistry", "Mathematics"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": True,
            },
            {
                "name": "EC2 - Invalid District",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "InvalidDistrict",
                    "max_results": 10,
                },
                "expect_fail": False,  # District might not be validated strictly
            },
            {
                "name": "EC3 - Z-Score out of range (3.5)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": 3.5,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": True,
            },
            {
                "name": "EC4 - Z-Score out of range (-3.5)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": -3.5,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": True,
            },
            {
                "name": "EC5 - Invalid Subject for Stream",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [
                            "Accounting",
                            "Business Studies",
                            "Economics",
                        ],  # Commerce subjects
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": True,  # Now should fail with rule-based validator
            },
            {
                "name": "EC6 - Only 2 Subjects (should fail in frontend but test backend)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": False,
            },
            {
                "name": "EC7 - Empty Subjects List",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
                "expect_fail": True,
            },
            {
                "name": "EC8 - Negative max_results",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": -5,
                },
                "expect_fail": True,
            },
            {
                "name": "EC9 - Very high max_results (100)",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": ["Combined Mathematics", "Physics", "Chemistry"],
                        "zscore": None,
                        "interests": "",
                    },
                    "district": "Colombo",
                    "max_results": 100,
                },
                "expect_fail": False,
            },
        ]

        for test in tests:
            result = make_request(
                RECOMMEND_ENDPOINT, test["payload"], test["name"], "EDGE_CASE"
            )
            # Verify expectation
            if "expect_fail" in test:
                if test["expect_fail"] and result.status != "FAIL":
                    print(
                        f"⚠️  UNEXPECTED: Expected this to fail but got {result.status}"
                    )

    @staticmethod
    def test_cross_stream_comparisons():
        """Compare results across different streams"""
        print("\n" + "=" * 80)
        print("CROSS-STREAM COMPARISON TESTS")
        print("=" * 80)

        # Same interests, all streams
        interests_text = "I am passionate about technology, programming, software development, and AI applications."

        tests = [
            {
                "name": "CROSS1.1 - Physical Science + Tech Interests",
                "payload": {
                    "student": {
                        "stream": "Physical Science",
                        "subjects": [
                            "Combined Mathematics",
                            "Physics",
                            "Information & Communication Technology",
                        ],
                        "zscore": 2.0,
                        "interests": interests_text,
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "CROSS1.2 - Commerce + Same Tech Interests",
                "payload": {
                    "student": {
                        "stream": "Commerce",
                        "subjects": ["Accounting", "Business Studies", "Economics"],
                        "zscore": 2.0,
                        "interests": interests_text,
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
            {
                "name": "CROSS1.3 - Arts + Same Tech Interests",
                "payload": {
                    "student": {
                        "stream": "Arts",
                        "subjects": [
                            "History",
                            "Geography",
                            "Information & Communication Technology",
                        ],
                        "zscore": 2.0,
                        "interests": interests_text,
                    },
                    "district": "Colombo",
                    "max_results": 10,
                },
            },
        ]

        for test in tests:
            make_request(
                RECOMMEND_ENDPOINT, test["payload"], test["name"], "CROSS_STREAM"
            )


# ============================================================================
# RESULT REPORTING
# ============================================================================


def generate_report():
    """Generate comprehensive test report"""

    print("\n\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)

    # Summary stats
    total_tests = len(test_results)
    passed = sum(1 for r in test_results if r.status == "PASS")
    failed = sum(1 for r in test_results if r.status == "FAIL")
    errors = sum(1 for r in test_results if r.status == "ERROR")

    print(f"\n📊 TOTAL TESTS: {total_tests}")
    print(f"✅ PASSED: {passed} ({passed*100//total_tests}%)")
    print(f"❌ FAILED: {failed} ({failed*100//total_tests}%)")
    print(f"⚠️  ERRORS: {errors} ({errors*100//total_tests}%)")

    # Group by scenario
    print(f"\n📋 BREAKDOWN BY SCENARIO:")
    scenarios = {}
    for result in test_results:
        if result.scenario not in scenarios:
            scenarios[result.scenario] = {"PASS": 0, "FAIL": 0, "ERROR": 0}
        scenarios[result.scenario][result.status] += 1

    for scenario, stats in sorted(scenarios.items()):
        total = sum(stats.values())
        print(f"\n  {scenario}:")
        print(f"    ✅ {stats['PASS']}/{total} passed")
        if stats["FAIL"] > 0:
            print(f"    ❌ {stats['FAIL']} failed")
        if stats["ERROR"] > 0:
            print(f"    ⚠️  {stats['ERROR']} errors")

    # Detailed failure report
    if failed + errors > 0:
        print(f"\n⚠️  FAILURES AND ERRORS:")
        for result in test_results:
            if result.status != "PASS":
                print(f"\n  {result.test_name}")
                print(f"    Status: {result.status}")
                print(f"    Response Code: {result.response_code}")
                print(f"    Error: {result.error}")

    # Sample passing test output
    print(f"\n📄 SAMPLE PASSING TEST DETAILS:")
    for result in test_results[:3]:
        if result.status == "PASS":
            print(f"\n  ✅ {result.test_name}")
            if result.response_data and "courses" in result.response_data:
                courses = result.response_data.get("courses", [])
                print(f"    Found {len(courses)} courses")
                if courses:
                    print(
                        f"    Top match: {courses[0].get('code')} - {courses[0].get('name')}"
                    )
                    print(
                        f"    Match percentage: {courses[0].get('match_percentage', 'N/A')}%"
                    )

    # Time stats
    duration = (datetime.now() - test_start_time).total_seconds()
    print(f"\n⏱️  Test Duration: {duration:.2f} seconds")
    print(f"   Average per test: {duration/total_tests:.2f} seconds")

    # Save JSON report
    report_data = {
        "timestamp": test_start_time.isoformat(),
        "duration_seconds": duration,
        "summary": {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "scenarios": scenarios,
        "detailed_results": [r.to_dict() for r in test_results],
    }

    with open("test_report.json", "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📁 Full report saved to: test_report.json")


def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive A/L Degree Recommendation Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {test_start_time}")

    # Check backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is online")
        else:
            print("⚠️  Backend responded but with unexpected status")
    except Exception as e:
        print(f"❌ Backend is not reachable: {e}")
        print("Make sure to run: python main.py in degree-recommendation-service")
        return

    # Run all scenarios
    tester = ScenarioTester()

    tester.test_s1_stream_only()
    time.sleep(2)

    tester.test_s2_stream_zscore()
    time.sleep(2)

    tester.test_s4_stream_interests()
    time.sleep(2)

    tester.test_s5_all_fields()
    time.sleep(2)

    tester.test_edge_cases()
    time.sleep(2)

    tester.test_cross_stream_comparisons()

    # Generate report
    generate_report()

    print("\n✨ Testing complete!")


if __name__ == "__main__":
    main()
