#!/usr/bin/env python3
import sys
import json
import logging
from pathlib import Path

# Add career-service to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from data_loader import load_all_data
from services.recommender import recommend_careers_for_user

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SCENARIOS = [
    {
        "name": "Frontend Heavy Profile",
        "description": "User has frontend web skills.",
        "skills": ["SK005", "SK006", "SK002", "SK351", "SK312"], # CSS, HTML, JS, React, TS
        "expected_roles": ["FE_DEV", "JR_FE_DEV", "SENIOR_FE_DEV"],
        "min_score": 0.40
    },
    {
        "name": "Data Science Profile",
        "description": "User has data science and ML skills.",
        "skills": ["SK004", "SK124", "SK531", "SK031"], # Python, Statistics, Deep Learning, ML
        "expected_roles": ["DATA_SCIENTIST", "JR_DATA_ANALYST", "ML_RESEARCH_SCIENTIST", "DATA_ANALYST"],
        "min_score": 0.20
    },
    {
        "name": "Backend Heavy Profile",
        "description": "Java Spring Developer",
        "skills": ["SK001", "SK018", "SK003"], # Java, Spring, SQL
        "expected_roles": ["BE_DEV", "JR_BE_DEV", "FS_DEV", "JR_FS_DEV"],
        "min_score": 0.35
    }
]

OUT_FILE = ROOT / "evaluation_results" / "scenario_test_results.json"

def run_scenarios():
    load_all_data()
    results = []
    
    for scenario in SCENARIOS:
        logging.info(f"Running Scenario: {scenario['name']}")
        res = recommend_careers_for_user(scenario["skills"], top_n=5)
        recs = res.get("recommendations", [])
        
        passed = False
        actual_roles = []
        for rank, rec in enumerate(recs):
            role = rec.get("role_id")
            actual_roles.append(role)
            if role in scenario["expected_roles"] and rec.get("match_score", 0) >= scenario["min_score"]:
                passed = True
                
        scenario_res = {
            "scenario": scenario["name"],
            "description": scenario["description"],
            "input_skills": scenario["skills"],
            "expected_any_of": scenario["expected_roles"],
            "actual_top_roles": actual_roles,
            "passed": passed
        }
        results.append(scenario_res)
        logging.info(f" -> Passed: {passed}")
        
    OUT_FILE.write_text(json.dumps(results, indent=2))
    logging.info(f"Saved scenario validation report to {OUT_FILE}")

if __name__ == "__main__":
    run_scenarios()
