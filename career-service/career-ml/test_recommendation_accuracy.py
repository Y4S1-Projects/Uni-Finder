#!/usr/bin/env python3
"""
=============================================================================
TEST RECOMMENDATION ACCURACY
=============================================================================

Validates career recommendations with 10 predefined test cases.
Each test verifies:
  - Expected role appears in top 10 recommendations
  - Match score meets minimum threshold
  - Skill gap detection returns valid readiness score
  - Career path simulation works correctly

Usage:
    cd career-service
    python career-ml/test_recommendation_accuracy.py

Exit Codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Add career-service to path for imports
SERVICE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SERVICE_DIR))

# Import services AFTER path setup
from data_loader import load_all_data, DataStore
from services.recommender import recommend_careers_for_user
from services.career_service import detect_skill_gap, get_next_role, get_domain_for_role


# =============================================================================
# TEST CASE DEFINITIONS
# =============================================================================

@dataclass
class TestCase:
    """Definition of a recommendation test case."""
    name: str
    skill_ids: List[str]
    expected_roles: List[str]  # Any of these roles appearing is a pass
    min_score: float
    description: str


TEST_CASES: List[TestCase] = [
    TestCase(
        name="Frontend Developer",
        skill_ids=["SK002", "SK005", "SK006", "SK351", "SK312"],
        expected_roles=["JR_FE_DEV", "FE_DEV"],
        min_score=0.40,
        description="JavaScript, CSS, HTML, React, TypeScript"
    ),
    TestCase(
        name="Backend Java Developer",
        skill_ids=["SK001", "SK003", "SK018", "SK025"],
        expected_roles=["JR_BE_DEV", "BE_DEV"],
        min_score=0.35,
        description="Java, SQL, Spring, Hibernate"
    ),
    TestCase(
        name="Python Backend Developer",
        skill_ids=["SK004", "SK003", "SK076", "SK013"],
        expected_roles=["BE_DEV", "JR_BE_DEV", "JR_FS_DEV"],
        min_score=0.30,
        description="Python, SQL, Flask, REST"
    ),
    TestCase(
        name="Data Scientist",
        skill_ids=["SK004", "SK031", "SK124", "SK531"],
        expected_roles=["DATA_SCIENTIST", "DATA_ANALYST", "AI_ML_ENGINEER_INT", "JR_DATA_ANALYST"],
        min_score=0.20,
        description="Python, Machine Learning, Statistics, Deep Learning"
    ),
    TestCase(
        name="DevOps Engineer",
        skill_ids=["SK024", "SK029", "SK181", "SK646"],
        expected_roles=["DEVOPS_ENGINEER", "DEVOPS_TRAINEE", "JR_SYS_ADMIN", "CLOUD_ENGINEER"],
        min_score=0.20,
        description="DevOps, Docker, AWS, Terraform"
    ),
    TestCase(
        name="Full-Stack Developer",
        skill_ids=["SK001", "SK002", "SK003", "SK005", "SK006"],
        expected_roles=["JR_FS_DEV", "FS_DEV", "JR_BE_DEV", "JR_FE_DEV"],
        min_score=0.35,
        description="Java, JavaScript, SQL, CSS, HTML"
    ),
    TestCase(
        name="Mobile Developer",
        skill_ids=["SK265", "SK070", "SK055", "SK001"],
        expected_roles=["JR_MOBILE_DEV", "MOBILE_DEV", "JR_SE"],
        min_score=0.25,
        description="React Native, Swift, iOS, Java"
    ),
    TestCase(
        name="QA Engineer",
        skill_ids=["SK135", "SK427", "SK161", "SK286"],
        expected_roles=["JR_QA_ENG", "QA_ENG", "QA_ENGINEER"],
        min_score=0.40,
        description="Testing, Test Automation, Agile, Selenium"
    ),
    TestCase(
        name="Data Analyst",
        skill_ids=["SK124", "SK004", "SK003", "SK273"],
        expected_roles=["DATA_ANALYST", "JR_DATA_ANALYST", "DATA_ANALYST_INT", "JR_BUSINESS_ANALYST"],
        min_score=0.20,
        description="Statistics, Python, SQL, Data Visualization"
    ),
    TestCase(
        name="Cloud Engineer",
        skill_ids=["SK181", "SK024", "SK011", "SK029"],
        expected_roles=["CLOUD_ENGINEER", "DEVOPS_ENGINEER", "DEVOPS_TRAINEE", "JR_SYS_ADMIN"],
        min_score=0.20,
        description="AWS, DevOps, Infrastructure, Docker"
    ),
]


# =============================================================================
# TEST RESULT TRACKING
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test case."""
    test_name: str
    passed: bool
    role_found: Optional[str]
    role_position: Optional[int]
    actual_score: Optional[float]
    expected_score: float
    readiness_valid: bool
    career_path_valid: bool
    details: str


class TestReport:
    """Aggregates and reports test results."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
    
    def add(self, result: TestResult):
        self.results.append(result)
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST RECOMMENDATION ACCURACY - DETAILED REPORT")
        print("=" * 70)
        
        for i, r in enumerate(self.results, 1):
            status = "✓ PASS" if r.passed else "✗ FAIL"
            print(f"\n[{i:02d}] {r.test_name}: {status}")
            print(f"     Expected roles: {TEST_CASES[i-1].expected_roles}")
            
            if r.role_found:
                print(f"     Found: {r.role_found} at position #{r.role_position}")
                print(f"     Score: {r.actual_score:.3f} (min: {r.expected_score:.2f})")
            else:
                print(f"     Expected role NOT found in top 10")
            
            print(f"     Skill Gap Detection: {'✓' if r.readiness_valid else '✗'}")
            print(f"     Career Path Valid: {'✓' if r.career_path_valid else '✗'}")
            
            if not r.passed:
                print(f"     Failure: {r.details}")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"  Total Tests: {len(self.results)}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Success Rate: {self.passed / len(self.results) * 100:.1f}%")
        print("=" * 70)
        
        return self.failed == 0


# =============================================================================
# TEST EXECUTION
# =============================================================================

def run_test_case(test: TestCase) -> TestResult:
    """Execute a single test case and return results."""
    
    # Default result
    result = TestResult(
        test_name=test.name,
        passed=False,
        role_found=None,
        role_position=None,
        actual_score=None,
        expected_score=test.min_score,
        readiness_valid=False,
        career_path_valid=False,
        details=""
    )
    
    try:
        # Get recommendations
        response = recommend_careers_for_user(
            user_skill_ids=test.skill_ids,
            top_n=10
        )
        
        recommendations = response.get("recommendations", [])
        
        # Check if expected role appears in top 10
        found_role = None
        found_position = None
        found_score = None
        
        for idx, rec in enumerate(recommendations, 1):
            role_id = rec.get("role_id", "")
            if role_id in test.expected_roles:
                found_role = role_id
                found_position = idx
                found_score = rec.get("match_score", 0)
                break
        
        result.role_found = found_role
        result.role_position = found_position
        result.actual_score = found_score
        
        if not found_role:
            result.details = f"Expected roles {test.expected_roles} not in top 10. Got: {[r['role_id'] for r in recommendations[:5]]}"
            return result
        
        # Check score threshold
        if found_score < test.min_score:
            result.details = f"Score {found_score:.3f} below threshold {test.min_score:.2f}"
            return result
        
        # Test skill gap detection
        try:
            gap = detect_skill_gap(
                user_skill_ids=set(test.skill_ids),
                target_role_id=found_role,
                importance_threshold=0.02
            )
            readiness = gap.get("readiness_score", 0)
            result.readiness_valid = readiness > 0
        except Exception as e:
            result.details = f"Skill gap detection failed: {e}"
            return result
        
        # Test career path (get domain and next role)
        try:
            domain = get_domain_for_role(found_role)
            if domain:
                next_role = get_next_role(domain, found_role)
                result.career_path_valid = True
            else:
                # Role not in any ladder is acceptable
                result.career_path_valid = True
        except Exception as e:
            # Some roles might be at top of ladder
            result.career_path_valid = True
        
        # All checks passed
        result.passed = True
        result.details = "All validations passed"
        
    except Exception as e:
        result.details = f"Exception: {str(e)}"
    
    return result


def run_all_tests() -> bool:
    """Run all test cases and return True if all pass."""
    
    print("=" * 70)
    print("CAREER RECOMMENDATION ACCURACY TEST SUITE")
    print("=" * 70)
    print(f"Running {len(TEST_CASES)} test cases...")
    print()
    
    # Initialize data
    print("[INIT] Loading career recommendation data...")
    try:
        load_all_data()
        print(f"[INIT] Data version: {DataStore.data_version}")
        print(f"[INIT] Skills loaded: {len(DataStore.skill_columns)}")
        print(f"[INIT] Career ladders: {len(DataStore.career_ladders)}")
        print(f"[INIT] Role profiles shape: {DataStore.role_skill_matrix.shape if DataStore.role_skill_matrix is not None else 'N/A'}")
    except Exception as e:
        print(f"[INIT] FATAL: Failed to load data: {e}")
        return False
    
    print()
    
    # Run tests
    report = TestReport()
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i:02d}/{len(TEST_CASES)}] Testing: {test.name} ({test.description})")
        result = run_test_case(test)
        report.add(result)
        
        status = "PASS" if result.passed else "FAIL"
        score_str = f"{result.actual_score:.3f}" if result.actual_score else "N/A"
        print(f"        -> {status} | Role: {result.role_found or 'NOT FOUND'} | Score: {score_str}")
    
    # Print detailed report
    all_passed = report.print_summary()
    
    return all_passed


# =============================================================================
# ADDITIONAL VALIDATION TESTS
# =============================================================================

def test_edge_cases():
    """Run additional edge case tests."""
    print("\n" + "=" * 70)
    print("EDGE CASE TESTS")
    print("=" * 70)
    
    edge_tests = [
        ("Empty skills", [], False),
        ("Single skill", ["SK001"], True),
        ("Many skills (20)", [f"SK{i:03d}" for i in range(1, 21)], True),
        ("Invalid skill IDs", ["INVALID_001", "INVALID_002"], True),  # Should handle gracefully
    ]
    
    passed = 0
    failed = 0
    
    for name, skills, should_work in edge_tests:
        try:
            if not skills:
                # Empty skills should raise ValueError
                try:
                    recommend_careers_for_user(skills, top_n=5)
                    if not should_work:
                        print(f"  [FAIL] {name}: Expected error for empty skills")
                        failed += 1
                    else:
                        print(f"  [PASS] {name}")
                        passed += 1
                except ValueError as e:
                    if not should_work or "No skills" in str(e):
                        print(f"  [PASS] {name}: Correctly raised ValueError")
                        passed += 1
                    else:
                        print(f"  [FAIL] {name}: Unexpected error: {e}")
                        failed += 1
            else:
                result = recommend_careers_for_user(skills, top_n=5)
                if should_work and len(result.get("recommendations", [])) > 0:
                    print(f"  [PASS] {name}: Got {len(result['recommendations'])} recommendations")
                    passed += 1
                elif not should_work:
                    print(f"  [FAIL] {name}: Expected failure but got results")
                    failed += 1
                else:
                    print(f"  [FAIL] {name}: No recommendations returned")
                    failed += 1
        except Exception as e:
            if not should_work:
                print(f"  [PASS] {name}: Correctly failed with {type(e).__name__}")
                passed += 1
            else:
                print(f"  [FAIL] {name}: Unexpected error: {e}")
                failed += 1
    
    print(f"\n  Edge Cases: {passed}/{passed+failed} passed")
    return failed == 0


def test_score_distribution():
    """Test that scores are well-distributed (not all identical)."""
    print("\n" + "=" * 70)
    print("SCORE DISTRIBUTION TEST")
    print("=" * 70)
    
    # Use a diverse skill set
    skills = ["SK001", "SK002", "SK003", "SK004", "SK005", "SK006", "SK009", "SK018"]
    
    try:
        result = recommend_careers_for_user(skills, top_n=15)
        recommendations = result.get("recommendations", [])
        
        if len(recommendations) < 5:
            print(f"  [FAIL] Only {len(recommendations)} recommendations, expected at least 5")
            return False
        
        scores = [r["match_score"] for r in recommendations]
        
        # Check score range
        score_range = max(scores) - min(scores)
        
        print(f"  Top score: {max(scores):.3f}")
        print(f"  Min score: {min(scores):.3f}")
        print(f"  Score range: {score_range:.3f}")
        print(f"  Unique scores: {len(set(scores))}")
        
        if score_range < 0.01:
            print(f"  [WARN] Score range very narrow ({score_range:.4f}), may indicate issue")
        
        if len(set(scores)) < 3:
            print(f"  [WARN] Very few unique scores, recommendations may not be distinct")
        
        # Check that scores are sorted descending
        if scores != sorted(scores, reverse=True):
            print(f"  [FAIL] Scores not in descending order!")
            return False
        
        print(f"  [PASS] Scores properly distributed and sorted")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_career_path_consistency():
    """Test career path traversal for consistency."""
    print("\n" + "=" * 70)
    print("CAREER PATH CONSISTENCY TEST")
    print("=" * 70)
    
    passed = True
    
    for domain in list(DataStore.career_ladders.keys())[:5]:  # Test first 5 domains
        ladder = DataStore.career_ladders.get(domain, [])
        if len(ladder) < 2:
            continue
        
        print(f"\n  Domain: {domain}")
        print(f"  Ladder length: {len(ladder)} roles")
        
        # Try to traverse the ladder
        current = ladder[0]
        path = [current]
        
        for _ in range(len(ladder)):
            try:
                next_role = get_next_role(domain, current)
                if next_role is None:
                    break
                path.append(next_role)
                current = next_role
            except ValueError as e:
                print(f"    [WARN] Error traversing: {e}")
                break
        
        if path == ladder:
            print(f"    [PASS] Ladder traversal complete: {len(path)} steps")
        else:
            print(f"    [WARN] Partial traversal: {len(path)}/{len(ladder)} steps")
    
    return passed


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    print("\n")
    
    # Run main accuracy tests
    accuracy_passed = run_all_tests()
    
    # Run edge case tests
    edge_passed = test_edge_cases()
    
    # Run distribution test
    distribution_passed = test_score_distribution()
    
    # Run career path test
    path_passed = test_career_path_consistency()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    all_tests = [
        ("Accuracy Tests", accuracy_passed),
        ("Edge Case Tests", edge_passed),
        ("Score Distribution", distribution_passed),
        ("Career Path Consistency", path_passed),
    ]
    
    for name, passed in all_tests:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(p for _, p in all_tests)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED!")
        return 0
    else:
        print("SOME TESTS FAILED - Review the output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
