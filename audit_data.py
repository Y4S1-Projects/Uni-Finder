import json
import pandas as pd
from pathlib import Path

ML_DIR = Path("d:/SLIIT/Uni-Finder/career-service/career-ml")
DATA_DIR = ML_DIR / "data"

# File paths
ROLE_PROFILE_CSV = DATA_DIR / "processed" / "role_skill_profiles_v2_fixed.csv"
CAREER_LADDERS_JSON = DATA_DIR / "processed" / "career_ladders_v2.json"
JOB_SKILLS_CSV = DATA_DIR / "processed" / "job_skill_vectors_v2_fixed.csv"
SKILLS_CSV = DATA_DIR / "expanded" / "skills_v2.csv"
ROLE_METADATA_JSON = DATA_DIR / "processed" / "role_metadata.json"

print("--- Data Loading ---")
try:
    role_profiles = pd.read_csv(ROLE_PROFILE_CSV)
    job_skills = pd.read_csv(JOB_SKILLS_CSV)
    skills_df = pd.read_csv(SKILLS_CSV)
    with open(CAREER_LADDERS_JSON, "r") as f:
        ladders = json.load(f)
    with open(ROLE_METADATA_JSON, "r") as f:
        metadata = json.load(f)
except Exception as e:
    print(f"Error loading files: {e}")
    exit(1)

print("\n--- 1. Skill Coverage ---")
total_skills = len(skills_df)
print(f"Total skills: {total_skills}")
skill_cols = [c for c in job_skills.columns if c.startswith("skill_")]

job_skills_sum = job_skills[skill_cols].sum()
mapped_to_jobs = (job_skills_sum > 0).sum()
orphaned_skills = (job_skills_sum == 0).sum()

print(f"Skills mapped to jobs: {mapped_to_jobs} / {len(skill_cols)}")
print(f"Orphaned/unused skills: {orphaned_skills} / {len(skill_cols)}")

weakly_mapped = ((job_skills_sum > 0) & (job_skills_sum <= 2)).sum()
print(f"Skills mapped to <= 2 jobs (weak): {weakly_mapped}")

print("\n--- 2. Job Coverage ---")
total_jobs = len(job_skills)
print(f"Total jobs in vector data: {total_jobs}")
job_skill_counts = job_skills[skill_cols].sum(axis=1)
print(f"Jobs with < 5 skills: {(job_skill_counts < 5).sum()}")
print(f"Jobs with < 3 skills: {(job_skill_counts < 3).sum()}")
if "experience_level" in job_skills.columns:
    print(f"Jobs missing experience mapping: {job_skills['experience_level'].isna().sum()}")

print("\n--- 3. Role Coverage ---")
roles_in_metadata = len(metadata)
roles_in_profile = role_profiles['role_id'].nunique() if 'role_id' in role_profiles.columns else 0
print(f"Roles in metadata.json: {roles_in_metadata}")
print(f"Roles in role_profiles: {roles_in_profile}")

missing_in_profiles = [r['role_id'] for r in metadata if r['role_id'] not in role_profiles['role_id'].unique()]
print(f"Roles in metadata but missing from profiles: {len(missing_in_profiles)}")
if len(missing_in_profiles) > 0:
    print(f"Sample missing: {missing_in_profiles[:5]}")

print("\n--- 4. Ladder Coverage ---")
roles_in_ladders = set()
for dom, d_data in ladders.items():
    for track, tk_data in d_data.get("tracks", {}).items():
        for r in tk_data.get("roles", []):
            roles_in_ladders.add(r.get("role_id"))

print(f"Unique roles in career ladders: {len(roles_in_ladders)}")
missing_from_ladders = [r['role_id'] for r in metadata if r['role_id'] not in roles_in_ladders]
print(f"Roles in metadata but not in any ladder: {len(missing_from_ladders)}")

ai_roles = [r for r in metadata if r.get('domain_id') == 'AI_ML']
print(f"\nAI/ML roles in metadata: {len(ai_roles)}")
game_roles = [r for r in metadata if r.get('domain_id') == 'GAME_DEVELOPMENT']
print(f"Game Dev roles in metadata: {len(game_roles)}")

print("\nChecking role mapping counts in job_skills...")
role_counts = job_skills['role_id'].value_counts()
print(f"Total Unique Mapped Roles in Jobs CSV: {len(role_counts)}")
print(f"Roles mapped to < 10 jobs: {(role_counts < 10).sum()}")
