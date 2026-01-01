from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import json
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "career-ml"
ROLE_PROFILE_CSV = ML_DIR / "skill_gap" / "role_skill_profiles.csv"
CAREER_LADDERS_JSON = ML_DIR / "career_path" / "career_ladders.json"

app = FastAPI(title="Career Service")


class SimulateRequest(BaseModel):
    domain: str
    current_role: str
    user_skill_ids: List[str]
    importance_threshold: Optional[float] = 0.02


@app.on_event("startup")
def load_data():
    global role_profiles_df, CAREER_LADDERS
    try:
        role_profiles_df = pd.read_csv(ROLE_PROFILE_CSV)
    except Exception:
        role_profiles_df = pd.DataFrame(columns=["role_id", "skill_id", "frequency", "importance"])
    try:
        with open(CAREER_LADDERS_JSON, "r") as f:
            CAREER_LADDERS = json.load(f)
    except Exception:
        CAREER_LADDERS = {}


def detect_skill_gap(user_skill_ids: set, target_role_id: str, importance_threshold: float = 0.02):
    role_df = role_profiles_df[role_profiles_df["role_id"] == target_role_id]
    if role_df.empty:
        raise ValueError(f"No role profile found for role_id={target_role_id}")

    required_skills = set(role_df[role_df["importance"] >= importance_threshold]["skill_id"].astype(str))
    missing_skills = sorted(required_skills - user_skill_ids)
    matched_skills = sorted(required_skills & user_skill_ids)
    readiness = (len(matched_skills) / len(required_skills)) if required_skills else 0.0

    return {
        "target_role": target_role_id,
        "readiness_score": round(readiness, 3),
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
    }


def get_next_role(domain: str, current_role: str):
    ladder = CAREER_LADDERS.get(domain)
    if not ladder:
        raise ValueError(f"Unknown career domain: {domain}")
    if current_role not in ladder:
        raise ValueError(f"{current_role} not found in career ladder for {domain}")
    idx = ladder.index(current_role)
    if idx + 1 >= len(ladder):
        return None
    return ladder[idx + 1]


@app.get("/health")
def health():
    return {"status": "ok", "service": "career-service"}


@app.post("/simulate_path")
def simulate_path(req: SimulateRequest):
    try:
        next_role = get_next_role(req.domain, req.current_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if next_role is None:
        return {
            "domain": req.domain,
            "current_role": req.current_role,
            "message": "You are already at the highest role supported by current job market data.",
        }

    try:
        user_skills = set(s.strip().upper() for s in req.user_skill_ids if s)
        gap_result = detect_skill_gap(user_skills, next_role, req.importance_threshold)
    except ValueError:
        raise HTTPException(status_code=400, detail="Insufficient job data to evaluate skill gaps for this role.")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while evaluating skill gaps")

    return {
        "domain": req.domain,
        "current_role": req.current_role,
        "next_role": next_role,
        "readiness_score": gap_result["readiness_score"],
        "missing_skills": gap_result["missing_skills"],
        "matched_skills": gap_result["matched_skills"],
    }
