"""
Explainability service for career recommendations.
Uses Gemini AI (from explainability_engine.ipynb) with fallback to template-based explanations.
"""
from typing import Optional
from .skill_service import get_skill_name

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
    Generate a rich, detailed explanation without external AI.
    
    Args:
        context: Dictionary with role, skills, and match information
        
    Returns:
        Template-based explanation string
    """
    matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
    missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]
    
    role_title = context.get('role_title') or context.get('role_id') or 'this role'
    domain_raw = context.get('domain') or 'Technology'
    domain = domain_raw.replace('_', ' ') if domain_raw else 'Technology'
    match_score = (context.get('match_score') or 0) * 100
    readiness = (context.get('readiness_score') or 0) * 100
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
