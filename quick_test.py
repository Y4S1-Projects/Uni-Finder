"""
Quick Test Script — Enhanced Career Recommendation System
==========================================================
Tests legacy mode, enhanced mode, and personalization difference.
"""
import json
import requests
import sys

API = "http://localhost:5004"

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"

results = {}

# ─── TEST 1: Legacy Mode (skills only) ──────────────────────────────
print("=" * 60)
print("TEST 1: Legacy Mode (skills only)")
print("=" * 60)
try:
    resp = requests.post(f"{API}/recommend_careers", json={
        "user_skill_ids": ["SK001", "SK002", "SK010", "SK015", "SK020"],
        "top_n": 5,
    }, timeout=10)
    data = resp.json()
    mode = data.get("mode")
    recs = data.get("recommendations", [])
    print(f"  Status: {resp.status_code}")
    print(f"  Mode:   {mode}")
    print(f"  Recs:   {len(recs)}")
    for r in recs:
        print(f"    - {r['role_title']} (match={r['match_score']}, domain={r['domain']})")

    ok = resp.status_code == 200 and mode == "legacy" and len(recs) == 5
    print(f"\n  Result: {PASS if ok else FAIL}")
    results["TEST 1 Legacy"] = ok
except Exception as e:
    print(f"  ERROR: {e}")
    results["TEST 1 Legacy"] = False

# ─── TEST 2: Enhanced Mode (skills + context) ───────────────────────
print("\n" + "=" * 60)
print("TEST 2: Enhanced Mode (skills + context)")
print("=" * 60)
try:
    resp = requests.post(f"{API}/recommend_careers", json={
        "user_skill_ids": ["SK001", "SK002", "SK010", "SK015", "SK020"],
        "top_n": 5,
        "experience_level": "1-3",
        "current_status": "graduate",
        "education_level": "bachelors",
        "career_goal": "first_job",
        "preferred_domain": "software_engineering",
    }, timeout=10)
    data = resp.json()
    mode = data.get("mode")
    recs = data.get("recommendations", [])
    print(f"  Status: {resp.status_code}")
    print(f"  Mode:   {mode}")
    print(f"  Recs:   {len(recs)}")
    has_readiness = False
    for r in recs:
        readiness = r.get("skill_gap", {}).get("readiness_score", "N/A") if r.get("skill_gap") else "N/A"
        if readiness != "N/A":
            has_readiness = True
        print(f"    - {r['role_title']} (match={r['match_score']}, readiness={readiness}, domain={r['domain']})")

    ok = resp.status_code == 200 and mode == "enhanced" and len(recs) == 5 and has_readiness
    print(f"\n  Result: {PASS if ok else FAIL}")
    results["TEST 2 Enhanced"] = ok
except Exception as e:
    print(f"  ERROR: {e}")
    results["TEST 2 Enhanced"] = False

# ─── TEST 3: Personalization (same skills, different context) ────────
print("\n" + "=" * 60)
print("TEST 3: Personalization (same skills, different context)")
print("=" * 60)
try:
    common_skills = ["SK001", "SK002", "SK010", "SK015", "SK020"]

    # Student profile
    resp1 = requests.post(f"{API}/recommend_careers", json={
        "user_skill_ids": common_skills,
        "top_n": 5,
        "experience_level": "student",
        "current_status": "student",
        "education_level": "bachelors",
        "preferred_domain": "software_engineering",
    }, timeout=10)
    student_recs = [r["role_id"] for r in resp1.json()["recommendations"]]

    # Professional profile
    resp2 = requests.post(f"{API}/recommend_careers", json={
        "user_skill_ids": common_skills,
        "top_n": 5,
        "experience_level": "5+",
        "current_status": "working",
        "education_level": "masters",
        "preferred_domain": "software_engineering",
    }, timeout=10)
    prof_recs = [r["role_id"] for r in resp2.json()["recommendations"]]

    overlap = set(student_recs) & set(prof_recs)
    overlap_pct = len(overlap) / max(len(student_recs), 1) * 100

    print(f"  Student Top-5:      {student_recs}")
    print(f"  Professional Top-5: {prof_recs}")
    print(f"  Overlap:            {len(overlap)}/{len(student_recs)} ({overlap_pct:.0f}%)")

    # Check if ranking changed even if same roles (since all 15 roles might all appear)
    same_order = student_recs == prof_recs
    print(f"  Same order?:        {'YES (bad)' if same_order else 'NO (good — ranking differs)'}")

    ok = not same_order  # Rankings should differ
    print(f"\n  Result: {PASS if ok else FAIL}")
    results["TEST 3 Personalization"] = ok
except Exception as e:
    print(f"  ERROR: {e}")
    results["TEST 3 Personalization"] = False

# ─── SUMMARY ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
all_pass = True
for name, passed in results.items():
    print(f"  {PASS if passed else FAIL}  {name}")
    if not passed:
        all_pass = False

if all_pass:
    print("\n  All tests passed!")
    sys.exit(0)
else:
    print("\n  Some tests failed. See output above.")
    sys.exit(1)
