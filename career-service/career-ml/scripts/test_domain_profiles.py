#!/usr/bin/env python3
"""
Phase C Validation: Test AI/ML and Game Dev domain recommendations
Run with: python career-ml/scripts/test_domain_profiles.py
"""
import requests, json, sys

BASE = "http://localhost:5013"

TEST_PROFILES = [
    {
        "name": "Strong AI/ML Engineer",
        "payload": {
            "user_skill_ids": [
                "SK001",   # python
                "SK1200",  # tensorflow
                "SK1201",  # pytorch
                "SK1202",  # deep learning
                "SK1204",  # scikit-learn
                "SK1205",  # computer vision
                "SK1208",  # numpy
                "SK1209",  # pandas
                "SK1211",  # model deployment
                "SK031",   # machine learning
                "SK091",   # artificial intelligence
                "SK1215",  # statistics
            ],
            "experience_level": "3-5",
            "current_status": "working",
            "education_level": "masters",
            "career_goal": "get_promoted",
            "preferred_domain": "AI_ML",
        },
        "expect_domains": ["AI_ML", "DATA_SCIENCE"],
    },
    {
        "name": "Beginner AI/ML (Student)",
        "payload": {
            "user_skill_ids": [
                "SK001",   # python
                "SK1215",  # statistics
                "SK1217",  # jupyter
                "SK1209",  # pandas
                "SK031",   # machine learning
            ],
            "experience_level": "0-1",
            "current_status": "student",
            "education_level": "bachelors",
            "career_goal": "first_job",
            "preferred_domain": "AI_ML",
        },
        "expect_domains": ["AI_ML", "DATA_SCIENCE"],
    },
    {
        "name": "Strong Game Developer",
        "payload": {
            "user_skill_ids": [
                "SK1226",  # c++
                "SK1225",  # c#
                "SK1224",  # unity
                "SK1249",  # unreal engine
                "SK1234",  # gameplay programming
                "SK1228",  # shader programming
                "SK1231",  # game physics
                "SK1229",  # opengl
                "SK1227",  # game design
                "SK1237",  # multiplayer networking
                "SK1239",  # game engine architecture
            ],
            "experience_level": "3-5",
            "current_status": "working",
            "education_level": "bachelors",
            "career_goal": "get_promoted",
            "preferred_domain": "GAME_DEVELOPMENT",
        },
        "expect_domains": ["GAME_DEVELOPMENT"],
    },
    {
        "name": "Beginner Game Dev (Student)",
        "payload": {
            "user_skill_ids": [
                "SK1225",  # c#
                "SK1224",  # unity
                "SK1227",  # game design
            ],
            "experience_level": "0-1",
            "current_status": "student",
            "education_level": "bachelors",
            "career_goal": "first_job",
            "preferred_domain": "GAME_DEVELOPMENT",
        },
        "expect_domains": ["GAME_DEVELOPMENT"],
    },
]


def run_test(profile: dict):
    print(f"\n{'='*70}")
    print(f"  TEST: {profile['name']}")
    print(f"{'='*70}")
    print(f"  Skills: {len(profile['payload']['user_skill_ids'])} | Domain: {profile['payload'].get('preferred_domain','(none)')}")
    print(f"  Exp: {profile['payload'].get('experience_level')} | Status: {profile['payload'].get('current_status')}")
    print()
    
    try:
        payload = {**profile['payload'], 'top_n': 10}
        resp = requests.post(f"{BASE}/recommend_careers", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  *** REQUEST FAILED: {e}")
        return False
    
    recs = data.get("recommendations", [])
    mode = data.get("mode", "?")
    total = data.get("total_roles_compared", 0)
    print(f"  Mode: {mode} | Total roles compared: {total}")
    print(f"  Top {len(recs)} results:")
    print()
    
    expected = set(profile["expect_domains"])
    found_in_top5 = False
    
    for i, r in enumerate(recs[:10]):
        bd = r.get("score_breakdown", {})
        domain = r.get("domain") or "UNKNOWN"
        source = bd.get("profile_source") or "?"
        conf = bd.get("confidence_score", 0)
        match = r.get("match_score", 0)
        readiness = r.get("readiness_score", 0)
        core_matched = len(bd.get("matched_core_skills", []))
        total_core = bd.get("total_core_skills", 0)
        missing = bd.get("missing_critical_skills", [])
        explanations = r.get("explanations", {})
        
        marker = " ***" if domain in expected else ""
        synth_tag = f" [SYN]" if source.startswith("synthetic") else ""
        best_tag = " [BEST]" if r.get("is_best_match") else ""
        
        print(f"  #{i+1:2d}  {r['role_title']:<35s}  domain={domain:<20s}  "
              f"match={match:.3f}  ready={readiness:.3f}  "
              f"core={core_matched}/{total_core}  conf={conf:.3f}"
              f"{synth_tag}{best_tag}{marker}")
        
        if missing:
            miss_names = missing[:5]
            print(f"       missing: {', '.join(miss_names)}")
        
        if "data_confidence" in explanations:
            print(f"       >> {explanations['data_confidence'][:80]}")
        
        if i < 5 and domain in expected:
            found_in_top5 = True
    
    print()
    if found_in_top5:
        print(f"  PASS: Expected domain(s) {expected} found in top 5")
    else:
        print(f"  FAIL: Expected domain(s) {expected} NOT in top 5")
    
    return found_in_top5


def main():
    # Quick health check
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        print(f"Server health: {r.status_code}")
    except:
        print("ERROR: Server not reachable at", BASE)
        sys.exit(1)
    
    passed = 0
    total = len(TEST_PROFILES)
    
    for profile in TEST_PROFILES:
        if run_test(profile):
            passed += 1
    
    print(f"\n{'='*70}")
    print(f"  RESULTS: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
