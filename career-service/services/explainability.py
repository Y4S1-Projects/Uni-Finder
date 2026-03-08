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
    Generate profile-aware AI explanation using Gemini.
    
    Args:
        context: Dictionary with role, skills, match information, AND user profile
        
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
        
        # Profile context (NEW)
        experience_level = context.get('experience_level') or 'not specified'
        current_status = context.get('current_status') or 'not specified'
        education_level = context.get('education_level') or 'not specified'
        career_goal = context.get('career_goal') or 'not specified'
        preferred_domain = context.get('preferred_domain') or 'no preference'
        
        # Score breakdown (NEW)
        score_breakdown = context.get('score_breakdown', {})
        skill_match = score_breakdown.get('skill_match_score', match_score_val)
        domain_score = score_breakdown.get('domain_preference_score', 0.5)
        experience_fit = score_breakdown.get('experience_fit_score', 0.7)
        
        # Explanations from scoring engine (NEW)
        explanations = context.get('explanations', {})
        domain_impact = explanations.get('domain_impact', '')
        why_ranked = explanations.get('why_ranked_here', '')
        
        prompt = f"""You are a career guidance assistant helping a user understand why a specific role was recommended.

**Role Recommended:** {role_title} in {domain_str}

**User Profile:**
- Experience Level: {experience_level}
- Current Status: {current_status}
- Education: {education_level}
- Career Goal: {career_goal}
- Preferred Domain: {preferred_domain}

**Scoring Analysis:**
- Overall Match Score: {match_score_val:.0%}
- Skill Match: {skill_match:.0%}
- Domain Fit: {domain_score:.0%}
- Experience Fit: {experience_fit:.0%}
- Readiness: {readiness_val:.0%}

**Skills Assessment:**
- Skills you have: {', '.join(matched_names) if matched_names else 'None identified'}
- Skills to develop: {', '.join(missing_names) if missing_names else 'None - you have all required skills'}

**Domain Context:** {domain_impact}

**Next Career Step:** {next_role_str}

Generate a personalized, encouraging explanation (150-200 words) that:
1. Explains why this role specifically matches their profile (mention their experience level, career goal)
2. Addresses how their preferred domain preference influenced this recommendation
3. Highlights their strongest skill matches
4. Suggests 2-3 priority skills to develop based on their career goal
5. Provides encouragement based on their readiness level

Be specific to their situation. Do not mention skill IDs or technical score numbers."""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        explanation = response.text.strip()
        print(f"[explainability] Generated profile-aware Gemini explanation successfully")
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
