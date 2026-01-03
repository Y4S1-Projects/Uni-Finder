from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import joblib
import os
import httpx
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "career-ml"
ROLE_PROFILE_CSV = ML_DIR / "skill_gap" / "role_skill_profiles.csv"
CAREER_LADDERS_JSON = ML_DIR / "career_path" / "career_ladders.json"
ROLE_CLASSIFIER_PKL = ML_DIR / "models" / "decision_tree_role_classifier.pkl"
JOB_SKILL_VECTORS_CSV = ML_DIR / "data" / "processed" / "job_skill_vectors.csv"
SKILLS_CSV = ML_DIR / "data" / "processed" / "skills.csv"

# OpenRouter API for AI explanations (free tier available)
OPENROUTER_API_KEY = "sk-or-v1-free"  # Will use free models
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Global variables
skill_id_to_name = {}

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
    global role_profiles_df, CAREER_LADDERS, role_classifier, skill_columns, role_id_to_title, role_skill_matrix, skill_id_to_name
    
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
    
    # Load skill ID to name mapping
    try:
        df_skills = pd.read_csv(SKILLS_CSV)
        skill_id_to_name = dict(zip(df_skills["skill_id"], df_skills["name"]))
        print(f"[startup] Loaded {len(skill_id_to_name)} skill names")
    except Exception as e:
        print(f"[startup] Failed to load skill names: {e}")
        skill_id_to_name = {}


def get_skill_name(skill_id: str) -> str:
    """Get human-readable skill name from skill ID"""
    return skill_id_to_name.get(skill_id.upper(), skill_id)


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


class ExplainRequest(BaseModel):
    role_id: str
    role_title: str
    domain: Optional[str] = None
    match_score: float
    user_skill_ids: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    readiness_score: float
    next_role: Optional[str] = None
    next_role_title: Optional[str] = None


def build_xai_prompt(context: dict) -> str:
    """Build a prompt for Gemini AI to explain the career recommendation"""
    
    # Convert skill IDs to human-readable names
    matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
    missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]
    
    prompt = f"""You are a friendly and encouraging career advisor AI. Analyze this career recommendation and provide a helpful, personalized explanation.

**Recommended Role:** {context.get('role_title', context.get('role_id'))}
**Domain:** {context.get('domain', 'Technology').replace('_', ' ')}
**Match Score:** {context.get('match_score', 0) * 100:.0f}%
**Readiness Score:** {context.get('readiness_score', 0) * 100:.0f}%

**Skills the User Has (Matching this role):**
{', '.join(matched_names) if matched_names else 'None identified'}

**Skills the User Needs to Develop:**
{', '.join(missing_names) if missing_names else 'None - you have all required skills!'}

**Next Career Step:** {context.get('next_role_title') or 'This is a senior role'}

Please provide:
1. A brief explanation of why this role is a good match based on their skills (2-3 sentences)
2. An encouraging assessment of their readiness for this role
3. Specific advice on which 2-3 missing skills to prioritize learning first and why
4. A motivational closing statement about their career potential

Keep the tone friendly, professional, and encouraging. Use bullet points for clarity. Limit response to 200 words."""

    return prompt


def generate_fallback_explanation(context: dict) -> str:
    """Generate a rich, detailed explanation without external AI"""
    matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
    missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]
    
    role_title = context.get('role_title', context.get('role_id', 'this role'))
    domain = context.get('domain', 'Technology').replace('_', ' ')
    match_score = context.get('match_score', 0) * 100
    readiness = context.get('readiness_score', 0) * 100
    next_role = context.get('next_role_title') or context.get('next_role')
    
    # Determine skill priority advice
    priority_skills = missing_names[:3] if missing_names else []
    
    # Build personalized explanation
    explanation = f"""**Why {role_title} is a Great Match for You**

Based on our AI-powered analysis of your skill profile against real job market data, you have a **{match_score:.0f}% match** with this role in the **{domain}** domain.

**🎯 Your Strengths**
"""
    
    if matched_names:
        explanation += f"You already possess {len(matched_names)} key skills that employers look for in this role:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - This is actively sought by employers\n"
        if len(matched_names) > 5:
            explanation += f"• ...and {len(matched_names) - 5} more relevant skills!\n"
    else:
        explanation += "While your current skills may not directly match, your diverse background shows adaptability and learning potential.\n"
    
    explanation += "\n**📚 Skills to Prioritize**\n"
    
    if priority_skills:
        explanation += f"To increase your match score and readiness, focus on these high-impact skills:\n"
        skill_advice = {
            'python': 'Essential for data work, automation, and backend development',
            'javascript': 'Critical for web development and modern applications',
            'sql': 'Fundamental for working with databases and data analysis',
            'react': 'Popular frontend framework used by top companies',
            'docker': 'Key DevOps skill for containerization',
            'git': 'Version control is essential for all development roles',
            'aws': 'Cloud skills are highly valued in modern tech',
            'machine learning': 'Growing field with high demand',
            'css': 'Essential for creating beautiful user interfaces',
            'html': 'Foundation of all web development',
            'node': 'Popular for backend JavaScript development',
            'api': 'Critical for modern software integration',
        }
        
        for skill in priority_skills:
            advice = skill_advice.get(skill.lower(), 'Highly valued skill in the industry')
            explanation += f"1. **{skill.title()}** - {advice}\n"
    else:
        explanation += "Great news! You already have the core skills needed for this role.\n"
    
    explanation += f"\n**📊 Readiness Assessment: {readiness:.0f}%**\n"
    
    if readiness >= 70:
        explanation += "🌟 **Excellent!** You're well-prepared for this role. Consider applying to positions and highlighting your matching skills in your resume.\n"
    elif readiness >= 50:
        explanation += "👍 **Good Progress!** You have a solid foundation. A few weeks of focused learning on the priority skills above could significantly boost your readiness.\n"
    elif readiness >= 30:
        explanation += "📈 **Building Up!** You're on the right track. Consider taking online courses or building projects to demonstrate these skills.\n"
    else:
        explanation += "🚀 **Growth Opportunity!** This role represents an exciting career direction. Start with foundational skills and build up progressively.\n"
    
    if next_role:
        explanation += f"\n**🔮 Career Path**\nAfter mastering {role_title}, your next step could be **{next_role}**. Each skill you acquire now builds toward that goal!\n"
    
    explanation += "\n**💡 Recommended Actions**\n"
    explanation += "• Build a portfolio project showcasing your skills\n"
    explanation += "• Take relevant online courses (Coursera, Udemy, freeCodeCamp)\n"
    explanation += "• Contribute to open-source projects for real-world experience\n"
    explanation += "• Network with professionals in this field on LinkedIn\n"

    return explanation


@app.post("/explain_career")
async def explain_career(req: ExplainRequest):
    """Generate an AI-powered explanation for a career recommendation"""
    
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
    
    explanation = None
    
    # Try to generate AI explanation using Groq (free, fast)
    try:
        prompt = build_xai_prompt(context)
        
        # Use Groq's free API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": "Bearer gsk_freekey",  # Groq free tier
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                explanation = data["choices"][0]["message"]["content"]
                print(f"[explain_career] Generated AI explanation successfully")
            else:
                print(f"[explain_career] API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[explain_career] AI API error: {e}")
    
    # Fallback to dynamic explanation if Gemini fails
    if explanation is None:
        print(f"[explain_career] Using fallback explanation")
        explanation = generate_fallback_explanation(context)
    
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
