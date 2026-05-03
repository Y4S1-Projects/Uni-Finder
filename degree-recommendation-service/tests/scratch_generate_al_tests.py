import os
import time
import random
from fastapi.testclient import TestClient

# We must change directory to load models correctly
os.chdir(r"d:\My GitHub\Uni-Finder\degree-recommendation-service")

import google.generativeai as genai

from main import app

client = TestClient(app)

STREAMS = {
    "Physical Science": [
        ["Combined Mathematics", "Physics", "Chemistry"],
        ["Combined Mathematics", "Physics", "ICT"],
    ],
    "Biological Science": [
        ["Biology", "Chemistry", "Physics"],
        ["Biology", "Chemistry", "Agricultural Science"],
    ],
    "Commerce": [
        ["Accounting", "Business Studies", "Economics"],
        ["Accounting", "Economics", "ICT"],
        ["Business Studies", "Economics", "Business Statistics"],
    ],
    "Arts": [
        ["Sinhala", "Buddhist Civilization", "History"],
        ["Logic", "Political Science", "Geography"],
        ["English", "French", "German"],
    ],
    "Engineering Technology": [
        ["Engineering Technology", "Science for Technology", "ICT"],
    ],
    "Bio-Systems Technology": [
        ["Bio-Systems Technology", "Science for Technology", "Agriculture"],
    ]
}

DISTRICTS = ["COLOMBO", "KANDY", "GALLE", "JAFFNA", "MATARA", "GAMPAHA", "KURUNEGALA", "NUWARA ELIYA", "BATTICALOA", "BADULLA"]

INTERESTS = [
    "I want to build software and be a software engineer",
    "I love biology and want to be a doctor or medical researcher",
    "Business management, finance, and accounting",
    "Teaching, education, and language studies",
    "Agriculture, farming, and food technology",
    "Construction, civil engineering, and infrastructure",
    "Data science, AI, and machine learning",
    "Creative writing, journalism, and media",
    "Law, political science, and diplomacy"
]

def generate_test_cases(stream_name, subjects_list):
    cases = []
    
    # 1. 5 Without Interests (Low to High Z-Scores)
    z_scores_5 = [-1.5, -0.2, 0.8, 1.6, 2.5]
    for i in range(5):
        cases.append({
            "test_type": "No Interests (Varying Z-Scores)",
            "subjects": random.choice(subjects_list),
            "zscore": z_scores_5[i],
            "district": random.choice(DISTRICTS),
            "interests": ""
        })
        
    # 2. 3 With Interests (High Z-Scores)
    for i in range(3):
        cases.append({
            "test_type": "With Interests (High Z-Score)",
            "subjects": random.choice(subjects_list),
            "zscore": round(random.uniform(2.0, 2.8), 4),
            "district": random.choice(DISTRICTS),
            "interests": random.choice(INTERESTS)
        })
        
    # 3. 2 Edge Cases
    cases.append({
        "test_type": "Edge Case (Extreme Negative Z-Score with Ambitious Interest)",
        "subjects": random.choice(subjects_list),
        "zscore": -2.5,
        "district": "COLOMBO",
        "interests": "I want to be a top surgeon or software CEO"
    })
    
    cases.append({
        "test_type": "Edge Case (Gibberish Input to test Semantic Hallucination Prevention)",
        "subjects": random.choice(subjects_list),
        "zscore": 1.5,
        "district": "JAFFNA",
        "interests": "qwertyuiop asdfghjkl zxcvbnm 123456"
    })
    
    return cases

def run_tests():
    output_path = r"d:\My GitHub\Uni-Finder\degree-recommendation-service\al_pathway_comprehensive_tests.md"
    
    artifact_md = "# Comprehensive A/L Pathway Test Analysis\n\n"
    artifact_md += "This document contains 60 programmatically generated test cases (10 per stream) to manually verify the system. It includes AI explanations for every recommended degree and omits match scores as requested.\n\n"
    
    print("Starting comprehensive test suite (60 tests)...")
    
    for stream_name, subjects_list in STREAMS.items():
        artifact_md += f"## Stream: {stream_name}\n\n"
        print(f"Processing Stream: {stream_name}")
        
        test_cases = generate_test_cases(stream_name, subjects_list)
        
        for i, tc in enumerate(test_cases):
            print(f"  Running Test {i+1}/10...")
            payload = {
                "student": {
                    "stream": stream_name,
                    "subjects": tc["subjects"],
                    "zscore": tc["zscore"],
                    "interests": tc["interests"]
                },
                "district": tc["district"],
                "max_results": 3,
                "above_score_count": 2
            }
            
            response = client.post("/recommend", json=payload)
            
            artifact_md += f"### Test {i+1} - {tc['test_type']}\n"
            artifact_md += f"**Inputs:**\n"
            artifact_md += f"- **Subjects**: {', '.join(tc['subjects'])}\n"
            artifact_md += f"- **Z-Score**: `{tc['zscore']}`\n"
            artifact_md += f"- **District**: {tc['district']}\n"
            artifact_md += f"- **Interests**: *\"{tc['interests']}\"*\n\n"
            
            if response.status_code == 200:
                data = response.json()
                eligible = data.get("eligible_recommendations", [])
                aspirational = data.get("above_score_recommendations", [])
                
                artifact_md += f"#### Eligible Results ({len(eligible)})\n"
                if eligible:
                    for rec in eligible:
                        explanation = rec.get("explanation", "No explanation provided.")
                        artifact_md += f"- `{rec.get('course_code', 'Unknown')}`: **{rec.get('course_name', 'Unknown')}**\n"
                        artifact_md += f"  - *AI Explanation*: {explanation}\n"
                else:
                    artifact_md += "- *None found.*\n"
                    
                artifact_md += f"\n#### Aspirational/Dream Results ({len(aspirational)})\n"
                if aspirational:
                    for rec in aspirational:
                        gap = rec.get("zscore_gap", "N/A")
                        explanation = rec.get("explanation", "No explanation provided.")
                        artifact_md += f"- `{rec.get('course_code', 'Unknown')}`: **{rec.get('course_name', 'Unknown')}** (Z-Score Gap: {gap})\n"
                        artifact_md += f"  - *AI Explanation*: {explanation}\n"
                else:
                    artifact_md += "- *None found.*\n"
                    
            else:
                artifact_md += f"**ERROR**: Status {response.status_code} - {response.text}\n"
                
            artifact_md += "\n---\n\n"
            
            # Sleep briefly to not overwhelm local system (no need for 5s anymore)
            time.sleep(0.5)
            
            # Write to file progressively so we don't lose data if it crashes
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(artifact_md)

    print(f"Finished generating tests. Saved to {output_path}")

if __name__ == "__main__":
    run_tests()
