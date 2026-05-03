"""
Career Recommendation Accuracy Test
====================================
Tests the four key scenarios to verify the scoring pipeline
produces correct results for different user profiles.

Usage:
    python test_recommendation_accuracy_audit.py
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests

CAREER_API = "http://localhost:5004"

# ── Test profiles ─────────────────────────────────────────────────

PROFILES = {
    "student_frontend": {
        "description": "Student with frontend skills, seeking first job",
        "user_skill_ids": ["SK002", "SK006", "SK005", "SK026", "SK041", "SK122"],
        "experience_level": "0",        # Student / No experience
        "current_status": "student",
        "education_level": "bachelors",
        "career_goal": "first_job",
        "preferred_domain": "frontend_engineering",
        "expected": {
            "top_domains": ["SOFTWARE_ENGINEERING", "FRONTEND_ENGINEERING"],
            "max_seniority": 2,  # Should get intern/junior roles only
            "min_match": 0.20,
        },
    },
    "experienced_backend": {
        "description": "5+ years backend developer seeking promotion",
        "user_skill_ids": [
            "SK001", "SK003", "SK004", "SK007", "SK012", "SK016",
            "SK018", "SK024", "SK026", "SK041", "SK117", "SK122",
        ],
        "experience_level": "5+",
        "current_status": "working",
        "education_level": "masters",
        "career_goal": "get_promoted",
        "preferred_domain": "backend_engineering",
        "expected": {
            "top_domains": ["SOFTWARE_ENGINEERING", "BACKEND_ENGINEERING"],
            "min_seniority": 3,  # Should get mid+ roles
            "min_match": 0.30,
        },
    },
    "data_science_switcher": {
        "description": "Working professional switching to data science",
        "user_skill_ids": [
            "SK004", "SK120", "SK124", "SK044", "SK039", "SK003",
            "SK041", "SK028", "SK067",
        ],
        "experience_level": "1-3",
        "current_status": "working",
        "education_level": "bachelors",
        "career_goal": "switch_career",
        "preferred_domain": "data_science",
        "expected": {
            "top_domains": ["DATA", "DATA_SCIENCE", "AI_ML"],
            "max_seniority": 4,
            "min_match": 0.15,
        },
    },
    "no_domain_preference": {
        "description": "Graduate with general skills, no domain preference",
        "user_skill_ids": [
            "SK001", "SK002", "SK003", "SK004", "SK041",
            "SK026", "SK028", "SK067", "SK122",
        ],
        "experience_level": "0-1",
        "current_status": "graduate",
        "education_level": "bachelors",
        "career_goal": "first_job",
        "preferred_domain": "",  # No preference
        "expected": {
            "max_seniority": 3,
            "min_match": 0.15,
        },
    },
    "devops_engineer": {
        "description": "DevOps engineer (tests DEVOPS domain mapping fix)",
        "user_skill_ids": [
            "SK024", "SK029", "SK181", "SK166", "SK075",
            "SK132", "SK016", "SK041", "SK004",
        ],
        "experience_level": "3-5",
        "current_status": "working",
        "education_level": "bachelors",
        "career_goal": "get_promoted",
        "preferred_domain": "devops",  # This was mapping to wrong label
        "expected": {
            "top_domains": ["DEVOPS", "DEVOPS_SRE", "CLOUD_ENGINEERING"],
            "min_match": 0.15,
        },
    },
    "qa_engineer": {
        "description": "QA engineer (tests QA domain mapping fix)",
        "user_skill_ids": [
            "SK135", "SK041", "SK122", "SK028", "SK067",
            "SK161", "SK102",
        ],
        "experience_level": "1-3",
        "current_status": "working",
        "education_level": "bachelors",
        "career_goal": "get_promoted",
        "preferred_domain": "qa",  # This was mapping to wrong label
        "expected": {
            "top_domains": ["QA", "QA_TESTING"],
            "min_match": 0.10,
        },
    },
}


def test_profile(name, profile):
    """Test a single profile and check expectations."""
    print(f"\n{'='*70}")
    print(f"  TEST: {name}")
    print(f"  {profile['description']}")
    print(f"{'='*70}")

    payload = {
        "user_skill_ids": profile["user_skill_ids"],
        "top_n": 5,
        "experience_level": profile["experience_level"],
        "current_status": profile["current_status"],
        "education_level": profile["education_level"],
        "career_goal": profile["career_goal"],
        "preferred_domain": profile["preferred_domain"] or None,
    }

    try:
        resp = requests.post(f"{CAREER_API}/recommend_careers", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

    recs = data.get("recommendations", [])
    mode = data.get("mode", "?")
    profile_used = data.get("profile_used", {})

    print(f"  Mode: {mode}")
    print(f"  Profile used: {json.dumps(profile_used, indent=4)}")
    print(f"  Entry level: {data.get('is_entry_level_user')}")
    print()

    if not recs:
        print(f"  ❌ No recommendations returned!")
        return False

    # Print results
    all_pass = True
    expected = profile["expected"]

    for i, rec in enumerate(recs):
        sb = rec.get("score_breakdown", {})
        print(
            f"  #{i+1} {rec['role_id']:25s} "
            f"match={rec.get('match_score', 0):.3f}  "
            f"ready={rec.get('readiness_score', 0):.3f}  "
            f"skill={sb.get('skill_match_score', 0):.3f}  "
            f"core={sb.get('core_skill_coverage_score', 0):.3f}  "
            f"domain={sb.get('domain_preference_score', 0):.3f}  "
            f"exp={sb.get('experience_fit_score', 0):.3f}  "
            f"sen={sb.get('seniority_fit_score', 0):.3f}  "
            f"edu={sb.get('education_fit_score', 0):.3f}  "
            f"goal={sb.get('career_goal_fit_score', 0):.3f}  "
            f"seniority={rec.get('seniority', '?')}  "
            f"domain={rec.get('domain', '?')}"
        )

    # Validate expectations
    print()

    # Check match score minimum
    if "min_match" in expected:
        top_match = recs[0].get("match_score", 0)
        if top_match >= expected["min_match"]:
            print(f"  ✅ Top match score ({top_match:.3f}) >= {expected['min_match']}")
        else:
            print(f"  ❌ Top match score ({top_match:.3f}) < {expected['min_match']}")
            all_pass = False

    # Check seniority constraints
    if "max_seniority" in expected:
        top_seniority = recs[0].get("seniority", 3)
        if top_seniority <= expected["max_seniority"]:
            print(f"  ✅ Top role seniority ({top_seniority}) <= max {expected['max_seniority']}")
        else:
            print(f"  ⚠️  Top role seniority ({top_seniority}) > max {expected['max_seniority']} (warning)")

    if "min_seniority" in expected:
        top_seniority = recs[0].get("seniority", 3)
        if top_seniority >= expected["min_seniority"]:
            print(f"  ✅ Top role seniority ({top_seniority}) >= min {expected['min_seniority']}")
        else:
            print(f"  ⚠️  Top role seniority ({top_seniority}) < min {expected['min_seniority']} (warning)")

    # Check readiness differs from legacy
    legacy_ready = recs[0].get("skill_gap", {}).get("readiness_score", None)
    weighted_ready = recs[0].get("readiness_score", None)
    if legacy_ready is not None and weighted_ready is not None:
        if abs(legacy_ready - weighted_ready) > 0.01:
            print(f"  ℹ️  Readiness sources differ: weighted={weighted_ready:.3f} vs legacy={legacy_ready:.3f} (expected)")
        else:
            print(f"  ℹ️  Readiness sources match: {weighted_ready:.3f}")

    # Check domain preference score is non-zero for domain-specific tests
    if profile["preferred_domain"]:
        top_domain_score = recs[0].get("score_breakdown", {}).get("domain_preference_score", 0)
        if top_domain_score > 0.1:
            print(f"  ✅ Domain preference active: {top_domain_score:.3f}")
        else:
            print(f"  ❌ Domain preference score too low: {top_domain_score:.3f} (domain may not be mapped correctly)")
            all_pass = False

    return all_pass


def main():
    print("=" * 70)
    print("  CAREER RECOMMENDATION ACCURACY AUDIT")
    print("=" * 70)

    # Health check
    try:
        resp = requests.get(f"{CAREER_API}/health", timeout=5)
        print(f"\n  Service health: {resp.json()}")
    except Exception as e:
        print(f"\n  ❌ Service not reachable: {e}")
        print("  Make sure uvicorn is running: uvicorn app:app --reload --port 5004")
        return

    results = {}
    for name, profile in PROFILES.items():
        results[name] = test_profile(name, profile)

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {name}")
    print(f"\n  {passed}/{total} tests passed")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
