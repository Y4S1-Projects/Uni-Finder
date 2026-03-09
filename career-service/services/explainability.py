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
        
        # Core/supporting skill names from Phase D structured data
        core_skill_names = [s.get("name", s.get("id", "")) for s in context.get("matched_core_skills", [])]
        missing_critical_names = [s.get("name", s.get("id", "")) for s in context.get("missing_critical_skills", [])]
        supporting_skill_names = [s.get("name", s.get("id", "")) for s in context.get("matched_supporting_skills", [])]
        
        role_title = context.get('role_title') or context.get('role_id') or 'this role'
        domain_raw = context.get('domain') or 'Technology'
        domain_str = domain_raw.replace('_', ' ') if domain_raw else 'Technology'
        match_score_val = context.get('match_score') or 0
        readiness_val = context.get('readiness_score') or 0
        next_role_str = context.get('next_role_title') or 'This is a senior role'
        
        # Profile context
        experience_level = context.get('experience_level') or 'not specified'
        current_status = context.get('current_status') or 'not specified'
        education_level = context.get('education_level') or 'not specified'
        career_goal = context.get('career_goal') or 'not specified'
        preferred_domain = context.get('preferred_domain') or 'no preference'
        
        # Score breakdown
        score_breakdown = context.get('score_breakdown', {})
        skill_match = score_breakdown.get('skill_match_score', match_score_val)
        core_cov = score_breakdown.get('core_skill_coverage_score', 0)
        domain_score = score_breakdown.get('domain_preference_score', 0.5)
        experience_fit = score_breakdown.get('experience_fit_score', 0.7)
        seniority_fit = score_breakdown.get('seniority_fit_score', 0.7)
        confidence = score_breakdown.get('confidence_score', 1.0)
        
        # Explanation context from scoring engine
        explanations = context.get('explanations', {})
        domain_impact = explanations.get('domain_impact', '')
        why_ranked = explanations.get('why_ranked_here', '')
        why_best = explanations.get('why_best_match', '')
        why_not_ready = explanations.get('why_not_more_ready', '')
        seniority_note = explanations.get('seniority_fit', '')
        
        # Ladder info
        seniority = context.get('seniority') or 'unknown'
        ladder_pos = context.get('ladder_position')
        ladder_len = context.get('ladder_length')
        ladder_str = f"Position {ladder_pos} of {ladder_len} in the {domain_str} ladder" if ladder_pos and ladder_len else "Not mapped to a career ladder"
        is_best_match = context.get('is_best_match', False)
        profile_source = context.get('profile_source', 'data_backed')
        
        prompt = f"""You are a career guidance assistant. Provide a clear, specific, evidence-based explanation for why a role was recommended. Do NOT use vague language. Reference the actual scores, skills, and profile data below.

**Role:** {role_title} ({domain_str})
**Career Ladder:** {ladder_str}
**Seniority Level:** {seniority}
**Profile Source:** {profile_source}

**User Profile:**
- Selected Skills: {', '.join(matched_names[:15]) if matched_names else 'None'}
- Experience: {experience_level}
- Status: {current_status}
- Education: {education_level}
- Career Goal: {career_goal}
- Preferred Domain: {preferred_domain}

**Score Breakdown:**
- Overall Match: {match_score_val:.0%}
- Skill Match: {skill_match:.0%}
- Core Skill Coverage: {core_cov:.0%}
- Domain Fit: {domain_score:.0%}
- Experience Fit: {experience_fit:.0%}
- Seniority Fit: {seniority_fit:.0%}
- Confidence: {confidence:.0%}
- Readiness: {readiness_val:.0%}

**Matched Core Skills:** {', '.join(core_skill_names[:10]) if core_skill_names else 'None'}
**Matched Supporting Skills:** {', '.join(supporting_skill_names[:10]) if supporting_skill_names else 'None'}
**Missing Critical Skills:** {', '.join(missing_critical_names[:8]) if missing_critical_names else 'None — all core skills matched'}

**Why Ranked Here:** {why_ranked}
**Why {'Best Match' if is_best_match else 'Not Best Match'}:** {why_best or 'Other roles scored higher overall.'}
**Domain Impact:** {domain_impact}
**Seniority Fit:** {seniority_note}
**Why Not More Ready:** {why_not_ready}

**Next Career Step:** {next_role_str}

Write a personalized explanation (150–200 words) that covers EXACTLY these 4 sections:

1. **Why This Role Matches** — Reference their specific matched core skills, their career goal ({career_goal}), and domain fit. Explain why this role specifically suits their profile.

2. **What Determines the Ranking** — Explain why this role ranked where it did. Reference the specific score factors (core coverage, domain fit, seniority fit). If it's best match, say why. If not, explain what the top role does better.

3. **What Lowers Readiness** — Name the specific missing critical skills. Explain how each missing skill area affects their readiness for this role. Do not say "you're on the right track" without specifics.

4. **How to Improve** — Suggest 2–3 specific, actionable steps tied to the missing critical skills. Include concrete resources or project ideas.

Do NOT mention score numbers, skill IDs, or percentages. Use skill names only. Be direct and specific, not generic."""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        explanation = response.text.strip()
        print(f"[explainability] Generated Phase D profile-aware Gemini explanation")
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
