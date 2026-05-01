"""Phase B scoring engine test — 4 user profiles"""
import json
import requests

BASE = "http://127.0.0.1:5013/recommend_careers"

profiles = {
    "1_LOW_SKILL_STUDENT": {
        "user_skill_ids": ["SK004", "SK006", "SK005"],  # python, html, css
        "top_n": 5,
        "experience_level": "student",
        "current_status": "student",
        "education_level": "bachelors",
        "career_goal": "first_job",
        "preferred_domain": None,
    },
    "2_BACKEND_HEAVY": {
        "user_skill_ids": [
            "SK001", "SK003", "SK013", "SK021", "SK002",
            "SK018", "SK008", "SK009", "SK029", "SK020",
            "SK047", "SK161", "SK041",
        ],  # java, sql, rest, api, javascript, spring, mysql, git, docker, linux, mongodb, agile, software engineer
        "top_n": 5,
        "experience_level": "1-3",
        "current_status": "working",
        "education_level": "bachelors",
        "career_goal": "get_promoted",
        "preferred_domain": "backend_engineering",
    },
    "3_AI_ML_HEAVY": {
        "user_skill_ids": [
            "SK004", "SK003", "SK031", "SK194", "SK177",
            "SK020", "SK009", "SK021",
        ],  # python, sql, machine learning, NLP, data analysis, linux, git, api
        "top_n": 5,
        "experience_level": "3-5",
        "current_status": "working",
        "education_level": "masters",
        "career_goal": "get_promoted",
        "preferred_domain": "ai_ml",
    },
    "4_GAME_DEV": {
        "user_skill_ids": [
            "SK002", "SK006", "SK005", "SK004", "SK211", "SK009",
        ],  # javascript, html, css, python, games, git
        "top_n": 5,
        "experience_level": "0-1",
        "current_status": "graduate",
        "education_level": "bachelors",
        "career_goal": "first_job",
        "preferred_domain": "game_development",
    },
}

for name, payload in profiles.items():
    r = requests.post(BASE, json=payload)
    data = r.json()
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")
    print(f"  Mode: {data['mode']} | Entry: {data['is_entry_level_user']} | Roles compared: {data['total_roles_compared']}")
    print(f"  Skills: {data['skills_analyzed']}")
    print()
    for i, rec in enumerate(data["recommendations"]):
        bd = rec["score_breakdown"]
        print(f"  #{i+1} {rec['role_title']:40s}")
        print(f"     domain={rec['domain']}  best_match={rec['is_best_match']}")
        print(f"     match={rec['match_score']:.4f}  readiness={rec['readiness_score']:.4f}  skill_sim={rec['skill_match_score']:.4f}")
        print(f"     core_cov={bd['core_skill_coverage_score']:.2f} ({len(bd['matched_core_skills'])}/{bd['total_core_skills']})")
        print(f"     domain_pref={bd['domain_preference_score']:.2f}  seniority={bd['seniority_fit_score']:.2f}  exp_fit={bd['experience_fit_score']:.2f}")
        print(f"     goal_fit={bd['career_goal_fit_score']:.2f}  status_fit={bd['current_status_fit_score']:.2f}  edu_fit={bd['education_fit_score']:.2f}")
        print(f"     confidence={bd['confidence_score']:.2f}")
        print(f"     penalty={bd['penalty_total']:.3f} [{', '.join(bd['penalties_applied']) or 'none'}]")
        print(f"     boost={bd['boost_total']:.3f}  [{', '.join(bd['boosts_applied']) or 'none'}]")
        print(f"     entry_adj={bd['entry_level_adjustment']:.3f}  is_entry={bd['is_entry_level_user']}")
        print(f"     core_matched={bd['matched_core_skills']}")
        print(f"     missing_critical={bd['missing_critical_skills'][:5]}{'...' if len(bd['missing_critical_skills']) > 5 else ''}")
        expl = rec["explanations"]
        print(f"     explain: {expl.get('why_ranked_here', '-')}")
        print(f"     readiness_note: {expl.get('readiness', '-')}")
        if expl.get("entry_level_note"):
            print(f"     entry_note: {expl['entry_level_note']}")
        print()
