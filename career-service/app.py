from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import joblib
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "career-ml"
ROLE_PROFILE_CSV = ML_DIR / "skill_gap" / "role_skill_profiles.csv"
CAREER_LADDERS_JSON = ML_DIR / "career_path" / "career_ladders.json"
ROLE_CLASSIFIER_PKL = ML_DIR / "models" / "decision_tree_role_classifier.pkl"
JOB_SKILL_VECTORS_CSV = ML_DIR / "data" / "processed" / "job_skill_vectors.csv"

app = FastAPI(title="Career Service")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    domain: str
    current_role: str
    user_skill_ids: List[str]
    importance_threshold: Optional[float] = 0.02


class PredictRoleRequest(BaseModel):
    user_skill_ids: List[str]


@app.on_event("startup")
def load_data():
    global role_profiles_df, CAREER_LADDERS, role_classifier, skill_columns, role_id_to_title, role_skill_matrix
    
    print(f"[startup] BASE_DIR: {BASE_DIR}")
    print(f"[startup] ML_DIR: {ML_DIR}")
    print(f"[startup] ROLE_CLASSIFIER_PKL: {ROLE_CLASSIFIER_PKL}")
    print(f"[startup] Model file exists: {ROLE_CLASSIFIER_PKL.exists()}")
    
    try:
        role_profiles_df = pd.read_csv(ROLE_PROFILE_CSV)
        print(f"[startup] Loaded role_profiles_df: {len(role_profiles_df)} rows")
        
        # Build role-skill matrix for cosine similarity recommender
        role_skill_matrix = role_profiles_df.pivot_table(
            index="role_id",
            columns="skill_id",
            values="importance",
            fill_value=0
        )
        print(f"[startup] Built role_skill_matrix: {role_skill_matrix.shape}")
    except Exception as e:
        print(f"[startup] Failed to load role_profiles: {e}")
        role_profiles_df = pd.DataFrame(columns=["role_id", "skill_id", "frequency", "importance"])
        role_skill_matrix = pd.DataFrame()
    except Exception as e:
        print(f"[startup] Failed to load role_profiles: {e}")
        role_profiles_df = pd.DataFrame(columns=["role_id", "skill_id", "frequency", "importance"])
    
    try:
        with open(CAREER_LADDERS_JSON, "r") as f:
            CAREER_LADDERS = json.load(f)
        print(f"[startup] Loaded CAREER_LADDERS: {list(CAREER_LADDERS.keys())}")
    except Exception as e:
        print(f"[startup] Failed to load career ladders: {e}")
        CAREER_LADDERS = {}
    
    # Load the decision tree role classifier
    try:
        role_classifier = joblib.load(ROLE_CLASSIFIER_PKL)
        print(f"[startup] Loaded role_classifier: {type(role_classifier)}")
    except Exception as e:
        print(f"[startup] Failed to load role classifier: {e}")
        role_classifier = None
    
    # Load skill columns from the training data to ensure correct feature order
    try:
        df = pd.read_csv(JOB_SKILL_VECTORS_CSV, nrows=1)
        skill_columns = [c for c in df.columns if c.startswith("skill_")]
        print(f"[startup] Loaded {len(skill_columns)} skill columns")
    except Exception as e:
        print(f"[startup] Failed to load skill columns: {e}")
        skill_columns = []
    
    # Build role_id to role_title mapping
    try:
        df_roles = pd.read_csv(JOB_SKILL_VECTORS_CSV, usecols=["role_id", "role_title"])
        role_id_to_title = dict(zip(df_roles["role_id"], df_roles["role_title"]))
        print(f"[startup] Loaded {len(role_id_to_title)} role titles")
    except Exception as e:
        print(f"[startup] Failed to load role titles: {e}")
        role_id_to_title = {}


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


def get_domain_for_role(role_id: str) -> Optional[str]:
    """Find which domain a role belongs to"""
    for domain, roles in CAREER_LADDERS.items():
        if role_id in roles:
            return domain
    return None


@app.post("/predict_role")
def predict_role(req: PredictRoleRequest):
    """Predict the user's current role based on their skills using the decision tree model"""
    if role_classifier is None:
        raise HTTPException(status_code=500, detail="Role classifier model not loaded")
    
    if not skill_columns:
        raise HTTPException(status_code=500, detail="Skill columns not initialized")
    
    if not req.user_skill_ids:
        raise HTTPException(status_code=400, detail="No skills provided")
    
    # Create a feature vector with all skills set to 0
    feature_vector = np.zeros(len(skill_columns))
    
    # Set 1 for skills the user has
    # Skills come as SK001, SK002, etc. - convert to skill_sk001, skill_sk002
    user_skills_lower = set(s.strip().lower() for s in req.user_skill_ids if s)
    
    for i, col in enumerate(skill_columns):
        # col is like "skill_sk001", extract "sk001" and check
        skill_id = col.replace("skill_", "")  # "sk001"
        if skill_id in user_skills_lower:
            feature_vector[i] = 1
    
    # Predict the role
    predicted_role = role_classifier.predict([feature_vector])[0]
    
    # Get prediction probabilities if available
    try:
        probabilities = role_classifier.predict_proba([feature_vector])[0]
        max_prob = float(max(probabilities))
        confidence = round(max_prob, 3)
    except Exception:
        confidence = None
    
    # Get the role title
    role_title = role_id_to_title.get(predicted_role, predicted_role)
    
    # Determine the domain
    domain = get_domain_for_role(predicted_role)
    
    # Get next role in career ladder
    next_role = None
    next_role_title = None
    if domain:
        try:
            next_role = get_next_role(domain, predicted_role)
            if next_role:
                next_role_title = role_id_to_title.get(next_role, next_role)
        except ValueError:
            pass
    
    # Get skill gap for next role if available
    skill_gap = None
    if next_role:
        try:
            user_skills_upper = set(s.strip().upper() for s in req.user_skill_ids if s)
            skill_gap = detect_skill_gap(user_skills_upper, next_role)
        except Exception:
            pass
    
    return {
        "predicted_role": predicted_role,
        "predicted_role_title": role_title,
        "confidence": confidence,
        "domain": domain,
        "next_role": next_role,
        "next_role_title": next_role_title,
        "skill_gap": skill_gap,
        "skills_used": list(user_skills_lower),
    }


class RecommendRequest(BaseModel):
    user_skill_ids: List[str]
    top_n: Optional[int] = 5


def build_user_vector(user_skill_ids: set, skill_columns: pd.Index) -> np.ndarray:
    """Convert user's skill IDs into a vector aligned with role_skill_matrix columns."""
    vector = np.zeros(len(skill_columns))
    skill_index = {skill: idx for idx, skill in enumerate(skill_columns)}
    
    for skill_id in user_skill_ids:
        if skill_id in skill_index:
            vector[skill_index[skill_id]] = 1.0
    
    return vector.reshape(1, -1)


@app.post("/recommend_careers")
def recommend_careers(req: RecommendRequest):
    """Recommend best-fit career roles based on cosine similarity between user skills and role profiles."""
    if role_skill_matrix.empty:
        raise HTTPException(status_code=500, detail="Role skill matrix not loaded")
    
    if not req.user_skill_ids:
        raise HTTPException(status_code=400, detail="No skills provided")
    
    # Normalize user skills to uppercase (matching role_profiles format)
    user_skills_upper = set(s.strip().upper() for s in req.user_skill_ids if s)
    
    # Build user vector aligned with role_skill_matrix columns
    user_vector = build_user_vector(user_skills_upper, role_skill_matrix.columns)
    
    # Calculate cosine similarity between user and all roles
    role_vectors = role_skill_matrix.values
    similarity_scores = cosine_similarity(user_vector, role_vectors)[0]
    
    # Create recommendations dataframe
    recommendations = pd.DataFrame({
        "role_id": role_skill_matrix.index,
        "match_score": similarity_scores
    }).sort_values("match_score", ascending=False)
    
    # Get top N recommendations
    top_recommendations = recommendations.head(req.top_n)
    
    # Build detailed response
    results = []
    for _, row in top_recommendations.iterrows():
        role_id = row["role_id"]
        match_score = round(float(row["match_score"]), 3)
        
        # Get role title
        role_title = role_id_to_title.get(role_id, role_id)
        
        # Get domain
        domain = get_domain_for_role(role_id)
        
        # Get next role in career path
        next_role = None
        next_role_title = None
        if domain:
            try:
                next_role = get_next_role(domain, role_id)
                if next_role:
                    next_role_title = role_id_to_title.get(next_role, next_role)
            except ValueError:
                pass
        
        # Get skill gap for this role
        try:
            skill_gap = detect_skill_gap(user_skills_upper, role_id, importance_threshold=0.02)
        except Exception:
            skill_gap = None
        
        results.append({
            "role_id": role_id,
            "role_title": role_title,
            "match_score": match_score,
            "domain": domain,
            "next_role": next_role,
            "next_role_title": next_role_title,
            "skill_gap": skill_gap,
        })
    
    return {
        "recommendations": results,
        "skills_analyzed": list(user_skills_upper),
        "total_roles_compared": len(role_skill_matrix),
    }
