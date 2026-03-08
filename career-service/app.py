"""
Career Service - Main FastAPI Application

This is the central entry point that orchestrates all career-related services:
- Career recommendations (cosine similarity)
- Role prediction (decision tree)
- Career path simulation
- AI-powered explainability (Gemini)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from config import CORS_ORIGINS

# Request/Response schemas
from schemas import (
    SimulateRequest,
    PredictRoleRequest,
    RecommendRequest,
    ExplainRequest,
)

# Data loading
from data_loader import load_all_data, DataStore

# Services
from services import (
    get_skill_name,
    detect_skill_gap,
    get_next_role,
    get_domain_for_role,
    recommend_careers_for_user,
    predict_user_role,
    generate_explanation,
)

# Initialize FastAPI app
app = FastAPI(
    title="Career Service",
    description="AI-powered career recommendation and guidance service",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Load all data and models on startup"""
    load_all_data()


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "career-service"}


# =============================================================================
# Career Path Simulation
# =============================================================================

@app.post("/simulate_path")
def simulate_path(req: SimulateRequest):
    """
    Simulate career path progression and analyze skill gaps.
    """
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


# =============================================================================
# Role Prediction (Decision Tree)
# =============================================================================

@app.post("/predict_role")
def predict_role(req: PredictRoleRequest):
    """
    Predict user's current role based on their skills using decision tree model.
    """
    try:
        result = predict_user_role(req.user_skill_ids)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Career Recommendations (Cosine Similarity)
# =============================================================================

@app.post("/recommend_careers")
def recommend_careers(req: RecommendRequest):
    """
    Recommend best-fit career roles based on cosine similarity.
    Uses enhanced 330-dim vectors when extra profile fields are provided,
    otherwise falls back to legacy 300-dim skill-only mode.
    """
    try:
        result = recommend_careers_for_user(
            req.user_skill_ids,
            req.top_n,
            experience_level=req.experience_level,
            current_status=req.current_status,
            education_level=req.education_level,
            career_goal=req.career_goal,
            preferred_domain=req.preferred_domain,
            preferred_job_type=req.preferred_job_type,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AI Explainability (Gemini)
# =============================================================================

@app.post("/explain_career")
async def explain_career(req: ExplainRequest):
    """
    Generate AI-powered explanation for a career recommendation.
    """
    context = {
        "role_id": req.role_id,
        "role_title": req.role_title,
        "domain": req.domain,
        "match_score": req.match_score,
        "readiness_score": req.readiness_score,
        "matched_skills": req.matched_skills,
        "missing_skills": req.missing_skills,
        "next_role": req.next_role,
        "next_role_title": req.next_role_title,
    }
    
    # Convert skill IDs to names for response
    matched_skill_names = [{"id": s, "name": get_skill_name(s)} for s in req.matched_skills]
    missing_skill_names = [{"id": s, "name": get_skill_name(s)} for s in req.missing_skills]
    
    # Generate explanation (AI with fallback)
    explanation = generate_explanation(context)
    
    return {
        "role_id": req.role_id,
        "role_title": req.role_title,
        "domain": req.domain,
        "match_score": req.match_score,
        "readiness_score": req.readiness_score,
        "matched_skills": matched_skill_names,
        "missing_skills": missing_skill_names,
        "next_role": req.next_role,
        "next_role_title": req.next_role_title,
        "explanation": explanation,
    }

# =============================================================================
# Enhanced Career Ladder Additions
# =============================================================================

from pydantic import BaseModel
from typing import List
import json
import pandas as pd
from config import ML_DIR
from services import (
    get_career_ladder,
    analyze_career_progression,
    compare_career_paths
)

# Request schemas
class CareerProgressionRequest(BaseModel):
    user_skill_ids: List[str]
    current_role_id: str = None
    target_domain: str
    show_all_levels: bool = False  # If True, returns ALL levels in ladder (for network view)

class ComparePathsRequest(BaseModel):
    user_skill_ids: List[str]
    domains: List[str]


# Endpoints
@app.get("/career_ladder/{domain}")
def get_career_ladder_endpoint(domain: str):
    """
    Get complete career ladder structure for a domain
    """
    try:
        ladder = get_career_ladder(domain.upper())
        return ladder
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/career_ladders/list")
def list_all_career_ladders():
    """
    List all available career domains
    """
    try:
        enhanced_path = ML_DIR / 'career_path' / 'career_ladders_enhanced.json'
        with open(enhanced_path, 'r') as f:
            ladders = json.load(f)
        
        return {
            'domains': [
                {
                    'domain_id': domain_id,
                    'domain_name': ladder['domain_name'],
                    'total_jobs': ladder['total_jobs_in_domain'],
                    'total_levels': len(ladder['levels'])
                }
                for domain_id, ladder in ladders.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_career_progression")
def analyze_progression_endpoint(req: CareerProgressionRequest):
    """
    Analyze user's career progression in a specific domain
    """
    try:
        result = analyze_career_progression(
            user_skill_ids=req.user_skill_ids,
            current_role_id=req.current_role_id,
            target_domain=req.target_domain.upper(),
            show_all_levels=req.show_all_levels
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare_career_paths")
def compare_paths_endpoint(req: ComparePathsRequest):
    """
    Compare user's fit across multiple career paths
    """
    try:
        result = compare_career_paths(
            user_skill_ids=req.user_skill_ids,
            domains=[d.upper() for d in req.domains]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/skill_details/{skill_id}")
def get_skill_details(skill_id: str):
    """
    Get detailed information about a skill
    """
    try:
        skills_csv = ML_DIR / 'data' / 'processed' / 'skills_cleaned.csv'
        skills_df = pd.read_csv(skills_csv)
        skill = skills_df[skills_df['skill_id'] == skill_id.upper()]
        
        if skill.empty:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return {
            'skill_id': skill.iloc[0]['skill_id'],
            'name': skill.iloc[0]['name'],
            'category': skill.iloc[0]['category'] if 'category' in skill.columns else 'Unknown',
            'type': skill.iloc[0]['type'] if 'type' in skill.columns else 'Unknown',
            'aliases': skill.iloc[0]['aliases'].split('|') if ('aliases' in skill.columns and pd.notna(skill.iloc[0]['aliases'])) else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
