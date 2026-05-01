"""Phase D: Test script for sample payloads"""
import requests
import json

BASE = "http://localhost:5013"

def test_recommend(label, skills, top_n=3, **kwargs):
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"{'='*60}")
    payload = {"user_skill_ids": skills, "top_n": top_n}
    payload.update(kwargs)
    r = requests.post(f"{BASE}/recommend_careers", json=payload)
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text[:300]}")
        return None
    data = r.json()
    print(f"Mode: {data['mode']} | Compared: {data['total_roles_compared']} | Entry: {data.get('is_entry_level_user')}")
    for i, rec in enumerate(data["recommendations"]):
        print(f"\n  [{i+1}] {rec['role_title']} ({rec['domain']})")
        print(f"      Match: {rec['match_score']:.4f} | Ready: {rec['readiness_score']:.4f} | Confidence: {rec.get('confidence_score', 'N/A')}")
        print(f"      Seniority: {rec.get('seniority')} | Ladder: {rec.get('ladder_position')}/{rec.get('ladder_length')}")
        print(f"      Next: {rec.get('next_role_title')} | Best: {rec.get('is_best_match')} | Source: {rec.get('profile_source')}")
        print(f"      Core skills: {len(rec.get('matched_core_skills', []))} | Supporting: {len(rec.get('matched_supporting_skills', []))} | Missing critical: {len(rec.get('missing_critical_skills', []))}")
        if rec.get('matched_core_skills'):
            names = [s['name'] for s in rec['matched_core_skills'][:5]]
            print(f"      Core: {', '.join(names)}")
        if rec.get('missing_critical_skills'):
            names = [s['name'] for s in rec['missing_critical_skills'][:5]]
            print(f"      Missing: {', '.join(names)}")
        expl = rec.get('explanations', {})
        if expl.get('why_ranked_here'):
            print(f"      Why ranked: {expl['why_ranked_here'][:120]}")
        if expl.get('why_not_more_ready'):
            print(f"      Why not ready: {expl['why_not_more_ready'][:120]}")
        if expl.get('seniority_fit'):
            print(f"      Seniority fit: {expl['seniority_fit'][:120]}")
    return data

def test_explain(label, rec_data, user_skills, profile={}):
    print(f"\n{'='*60}")
    print(f"EXPLAIN: {label}")
    print(f"{'='*60}")
    rec = rec_data["recommendations"][0]
    payload = {
        "role_id": rec["role_id"],
        "role_title": rec["role_title"],
        "domain": rec["domain"],
        "match_score": rec["match_score"],
        "user_skill_ids": user_skills,
        "matched_skills": [s["id"] for s in rec["skill_gap"]["matched_skills"]],
        "missing_skills": [s["id"] for s in rec["skill_gap"]["missing_skills"]],
        "readiness_score": rec["skill_gap"]["readiness_score"],
        "next_role": rec.get("next_role"),
        "next_role_title": rec.get("next_role_title"),
        # Phase D
        "score_breakdown": rec.get("score_breakdown"),
        "explanations": rec.get("explanations"),
        "seniority": rec.get("seniority"),
        "ladder_position": rec.get("ladder_position"),
        "ladder_length": rec.get("ladder_length"),
        "confidence_score": rec.get("confidence_score"),
        "matched_core_skills": rec.get("matched_core_skills"),
        "matched_supporting_skills": rec.get("matched_supporting_skills"),
        "missing_critical_skills": rec.get("missing_critical_skills"),
        "is_best_match": rec.get("is_best_match"),
        "profile_source": rec.get("profile_source"),
    }
    payload.update(profile)
    r = requests.post(f"{BASE}/explain_career", json=payload)
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text[:300]}")
        return None
    data = r.json()
    print(f"Role: {data['role_title']} | Match: {data['match_score']} | Ready: {data['readiness_score']}")
    print(f"Seniority: {data.get('seniority')} | Ladder: {data.get('ladder_position')}/{data.get('ladder_length')}")
    print(f"Best: {data.get('is_best_match')} | Source: {data.get('profile_source')}")
    print(f"Core: {len(data.get('matched_core_skills') or [])} | Support: {len(data.get('matched_supporting_skills') or [])} | Missing: {len(data.get('missing_critical_skills') or [])}")
    expl_text = data.get('explanation', '')
    if expl_text:
        print(f"\nExplanation (first 500 chars):\n{expl_text[:500]}")
    return data

if __name__ == "__main__":
    # 1. Entry-level user
    entry_skills = ["SK0001", "SK0002", "SK0003", "SK0010", "SK0015"]
    d1 = test_recommend("Entry-level Student", entry_skills, top_n=3,
                        experience_level="student", current_status="student",
                        education_level="bachelors", career_goal="first_job")
    if d1:
        with open("sample_entry_level.json", "w") as f:
            json.dump(d1, f, indent=2)
        e1 = test_explain("Entry-level Modal", d1, entry_skills,
                          {"experience_level": "student", "current_status": "student",
                           "education_level": "bachelors", "career_goal": "first_job"})
        if e1:
            with open("sample_entry_level_modal.json", "w") as f:
                json.dump(e1, f, indent=2)

    # 2. AI/ML user
    aiml_skills = ["SK0001", "SK0003", "SK0045", "SK0046", "SK0047", "SK0048",
                   "SK0050", "SK0055", "SK0060", "SK0010", "SK0015", "SK0020"]
    d2 = test_recommend("AI/ML User", aiml_skills, top_n=3,
                        experience_level="1-3", current_status="working",
                        education_level="masters", career_goal="get_promoted",
                        preferred_domain="AI_ML")
    if d2:
        with open("sample_aiml.json", "w") as f:
            json.dump(d2, f, indent=2)
        e2 = test_explain("AI/ML Modal", d2, aiml_skills,
                          {"experience_level": "1-3", "current_status": "working",
                           "education_level": "masters", "career_goal": "get_promoted",
                           "preferred_domain": "AI_ML"})
        if e2:
            with open("sample_aiml_modal.json", "w") as f:
                json.dump(e2, f, indent=2)

    # 3. Backend-heavy user
    be_skills = ["SK0001", "SK0002", "SK0003", "SK0004", "SK0010", "SK0015",
                 "SK0020", "SK0025", "SK0030", "SK0035", "SK0040", "SK0100",
                 "SK0105", "SK0110"]
    d3 = test_recommend("Backend-heavy User", be_skills, top_n=3,
                        experience_level="3-5", current_status="working",
                        education_level="bachelors", career_goal="switch_career",
                        preferred_domain="BACKEND_ENGINEERING")
    if d3:
        with open("sample_backend.json", "w") as f:
            json.dump(d3, f, indent=2)
        e3 = test_explain("Backend Modal", d3, be_skills,
                          {"experience_level": "3-5", "current_status": "working",
                           "education_level": "bachelors", "career_goal": "switch_career",
                           "preferred_domain": "BACKEND_ENGINEERING"})
        if e3:
            with open("sample_backend_modal.json", "w") as f:
                json.dump(e3, f, indent=2)

    print("\n\nDone! Sample JSONs saved.")
