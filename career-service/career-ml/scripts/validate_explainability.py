#!/usr/bin/env python3
import sys
import json
import logging
import csv
from pathlib import Path

# Add career-service to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from data_loader import load_all_data
from services.recommender import recommend_careers_for_user
from services.career_service import detect_skill_gap

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SCENARIOS = [
    {
        "name": "Frontend Heavy Profile",
        "description": "User has frontend web skills.",
        "skills": ["SK005", "SK006", "SK002", "SK351", "SK312"], # CSS, HTML, JS, React, TS
    },
    {
        "name": "Data Science Profile",
        "description": "User has data science and ML skills.",
        "skills": ["SK004", "SK124", "SK531", "SK031"], # Python, Statistics, Deep Learning, ML
    },
    {
        "name": "Backend Heavy Profile",
        "description": "Java Spring Developer",
        "skills": ["SK001", "SK018", "SK003"], # Java, Spring, SQL
    }
]

OUT_FILE = ROOT / "evaluation_results" / "recommendation_validation_report.csv"

def run_explainability_val():
    load_all_data()
    with open(OUT_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Scenario", "Role Recommended", "Provided Skills", "Missing Skills Reported", "Logic Check Passed"])
        
        for scenario in SCENARIOS:
            logging.info(f"Checking Explainability for: {scenario['name']}")
            res = recommend_careers_for_user(scenario["skills"], top_n=3)
            recs = res.get("recommendations", [])
            for rec in recs:
                role = rec.get("role_id")
                # We need to verify if missing_skills produced are not inside input_skills
                gap = detect_skill_gap(set(scenario["skills"]), role)
                missing = [s["id"] for s in gap.get("missing_skills", [])]
                
                # Validation logic: Ensure no "missing" skill is actually in the user's "provided" skills
                overlap = set(scenario["skills"]).intersection(set(missing))
                passed = len(overlap) == 0
                
                writer.writerow([
                    scenario['name'], role, 
                    "|".join(scenario["skills"]), 
                    "|".join(missing[:5]) + ("..." if len(missing) > 5 else ""), 
                    str(passed)
                ])
                logging.info(f" -> {role} overlap check: {'PASSED' if passed else ('FAILED. Overlap: ' + str(overlap))}")
    logging.info(f"Saved explainability validation report to {OUT_FILE}")

if __name__ == "__main__":
    run_explainability_val()
