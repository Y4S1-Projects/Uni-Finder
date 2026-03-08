"""
Explainability service for career recommendations.
Uses Gemini AI (from explainability_engine.ipynb) with fallback to template-based explanations.
"""
from typing import Optional
from .skill_service import get_skill_name
from .fallback_templates import (
    get_analyst_explanation,
    get_coach_explanation,
    get_strategist_explanation,
    get_recruiter_explanation,
    get_visual_explanation,
)

# Initialize Gemini client
gemini_client = None
GEMINI_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
    try:
        gemini_client = genai.Client()
        print("[explainability] Gemini AI client initialized")
    except Exception as e:
        print(f"[explainability] Failed to initialize Gemini client: {e}")
except ImportError:
    print("[explainability] google-genai not installed, AI explanations will use fallback")


# List of fallback explanation templates
FALLBACK_TEMPLATES = [
    get_analyst_explanation,
    get_coach_explanation,
    get_strategist_explanation,
    get_recruiter_explanation,
    get_visual_explanation,
]
# Index to track the last used fallback template
last_fallback_index = -1


def generate_ai_explanation(context: dict) -> Optional[str]:
    """
    Generate AI explanation using Gemini (from explainability_engine.ipynb).
    
    Args:
        context: Dictionary with role, skills, and match information
        
    Returns:
        AI-generated explanation string or None if failed
    """
    if gemini_client is None or not GEMINI_AVAILABLE:
        return None
    
    try:
        # Build prompt using matched and missing skill names
        matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
        missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]
        
        role_title = context.get('role_title') or context.get('role_id') or 'this role'
        domain_raw = context.get('domain') or 'Technology'
        domain_str = domain_raw.replace('_', ' ') if domain_raw else 'Technology'
        match_score_val = context.get('match_score') or 0
        readiness_val = context.get('readiness_score') or 0
        next_role_str = context.get('next_role_title') or 'This is a senior role'
        
        prompt = f"""You are a career guidance assistant.

Explain why a user should consider the role of {role_title} in the {domain_str} domain.

Match score: {match_score_val:.2f}
Readiness score: {readiness_val:.2f}

Skills already possessed:
{', '.join(matched_names) if matched_names else 'None identified'}

Skills to improve:
{', '.join(missing_names) if missing_names else 'None - user has all required skills'}

Next career step: {next_role_str}

Generate a clear, supportive, human-friendly explanation that:
1. Explains why this role is a good fit based on their current skills
2. Provides encouragement about their readiness level
3. Suggests which 2-3 missing skills to prioritize and why
4. Ends with a motivational statement about their career potential

Do not mention skill IDs. Keep the response under 200 words."""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        explanation = response.text.strip()
        print(f"[explainability] Generated Gemini AI explanation successfully")
        return explanation
        
    except Exception as e:
        print(f"[explainability] Gemini API error: {e}")
        return None


def generate_fallback_explanation(context: dict) -> str:
    """
    Generate a rich, detailed explanation from a rotating set of templates.
    
    Args:
        context: Dictionary with role, skills, and match information
        
    Returns:
        Template-based explanation string
    """
    global last_fallback_index
    
    # Cycle to the next template
    last_fallback_index = (last_fallback_index + 1) % len(FALLBACK_TEMPLATES)
    
    print(f"[explainability] Using fallback template #{last_fallback_index + 1}")
    
    # Get the explanation from the selected template
    template_function = FALLBACK_TEMPLATES[last_fallback_index]
    return template_function(context)


def generate_explanation(context: dict) -> str:
    """
    Generate career explanation using AI with fallback.
    
    This is the main entry point that tries Gemini AI first,
    then falls back to template-based explanation.
    
    Args:
        context: Dictionary with role, skills, and match information
        
    Returns:
        Explanation string (AI-generated or template-based)
    """
    # Try AI explanation first
    explanation = generate_ai_explanation(context)
    
    # Fallback to template if AI fails
    if explanation is None:
        print(f"[explainability] Using fallback explanation")
        explanation = generate_fallback_explanation(context)
    
    return explanation
