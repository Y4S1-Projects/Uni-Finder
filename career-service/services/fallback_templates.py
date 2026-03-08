"""
Fallback explanation templates for the career recommendation explainability service.
These templates are structured to be direct and informative, similar to the original design.
"""
from .skill_service import get_skill_name

def _get_readiness_text(readiness: float) -> str:
    """Returns a descriptive string based on the readiness score."""
    if readiness >= 70:
        return "🌟 **Excellent!** You're well-prepared. Focus on applying to roles and highlighting your skills."
    elif readiness >= 50:
        return "👍 **Good Progress!** You have a solid foundation. A bit of focused learning will make you a strong candidate."
    elif readiness >= 30:
        return "📈 **Building Up!** You're on the right track. Prioritize skill-building to boost your confidence."
    else:
        return "🚀 **Growth Opportunity!** This is an exciting career direction. Start with foundational skills and build up."

def _get_skill_advice(skill: str) -> str:
    """Returns a brief, encouraging piece of advice for a given skill."""
    skill_advice = {
        'python': 'Essential for data work, automation, and backend development.',
        'javascript': 'Critical for web development and modern applications.',
        'sql': 'Fundamental for working with databases and data analysis.',
        'react': 'A popular frontend framework used by top companies.',
        'docker': 'A key DevOps skill for building and deploying applications.',
        'git': 'Version control is a must-have for all development roles.',
        'aws': 'Cloud skills are highly valued across the tech industry.',
        'machine learning': 'A rapidly growing field with high demand for skilled professionals.',
        'css': 'Essential for creating beautiful and responsive user interfaces.',
        'html': 'The foundation of all web development and a great place to start.',
        'node': 'A popular choice for building fast and scalable backend services.',
        'api': 'Critical for connecting modern software applications.',
    }
    return skill_advice.get(skill.lower(), 'A highly valued skill in the industry.')

def _generate_base_explanation(context: dict) -> dict:
    """Generates the common components for all explanations."""
    matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
    missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]
    
    return {
        "role_title": context.get('role_title', 'this role'),
        "domain": (context.get('domain') or 'Technology').replace('_', ' '),
        "match_score": (context.get('match_score') or 0) * 100,
        "readiness": (context.get('readiness_score') or 0) * 100,
        "next_role": context.get('next_role_title'),
        "matched_names": matched_names,
        "missing_names": missing_names,
        "priority_skills": missing_names[:3]
    }

# --- Template 1: The Direct Analyst ---
def get_analyst_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    role_title, domain, match_score, readiness, next_role = base["role_title"], base["domain"], base["match_score"], base["readiness"], base["next_role"]
    matched_names, priority_skills = base["matched_names"], base["priority_skills"]

    explanation = f"""**Why {role_title} is a Great Match for You**

Based on our AI-powered analysis of your skill profile against real job market data, you have a **{match_score:.0f}% match** with this role in the **{domain}** domain.

**🎯 Your Strengths**
"""
    if matched_names:
        explanation += f"You already possess {len(matched_names)} key skills that employers look for:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - This is actively sought by employers.\n"
        if len(matched_names) > 5:
            explanation += f"• ...and {len(matched_names) - 5} more relevant skills!\n"
    else:
        explanation += "Your background shows strong adaptability, a great starting point for this career path.\n"

    explanation += "\n**📚 Skills to Prioritize**\n"
    if priority_skills:
        explanation += "To increase your match score and readiness, focus on these high-impact skills:\n"
        for i, skill in enumerate(priority_skills):
            explanation += f"{i+1}. **{skill.title()}** - {_get_skill_advice(skill)}\n"
    else:
        explanation += "Excellent! You have all the core skills for this role.\n"

    explanation += f"\n**📊 Readiness Assessment: {readiness:.0f}%**\n"
    explanation += _get_readiness_text(readiness)

    if next_role:
        explanation += f"\n\n**🔮 Career Path**\nAfter mastering {role_title}, your next logical step could be **{next_role}**. The skills you build now are an investment in that future."

    explanation += "\n\n**💡 Recommended Actions**\n"
    explanation += "• Build a portfolio project to showcase your abilities.\n"
    explanation += "• Take relevant online courses (e.g., Coursera, Udemy).\n"
    explanation += "• Network with professionals in this field on LinkedIn."
    return explanation

# --- Template 2: The Encouraging Mentor ---
def get_coach_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    role_title, domain, match_score, readiness, next_role = base["role_title"], base["domain"], base["match_score"], base["readiness"], base["next_role"]
    matched_names, priority_skills = base["matched_names"], base["priority_skills"]

    explanation = f"""**Your Potential as a {role_title}**

Our analysis indicates a **{match_score:.0f}% alignment** between your profile and the **{role_title}** role. This is a promising starting point for a career in the **{domain}** field.

**🌟 Your Foundational Skills**
"""
    if matched_names:
        explanation += f"You're off to a great start with {len(matched_names)} relevant skills, including:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - A great asset for this role.\n"
        if len(matched_names) > 5:
            explanation += f"• ...plus {len(matched_names) - 5} other foundational skills!\n"
    else:
        explanation += "Your unique experience provides a solid foundation for learning the technical skills required.\n"

    explanation += "\n**🚀 Your Growth Areas**\n"
    if priority_skills:
        explanation += "Embrace the challenge of learning these valuable skills to become a stronger candidate:\n"
        for i, skill in enumerate(priority_skills):
            explanation += f"{i+1}. **{skill.title()}** - {_get_skill_advice(skill)}\n"
    else:
        explanation += "Fantastic! Your current skillset is already well-aligned.\n"

    explanation += f"\n**📈 Readiness Check: {readiness:.0f}%**\n"
    explanation += _get_readiness_text(readiness)

    if next_role:
        explanation += f"\n\n**🛤️ Your Journey Ahead**\nSuccessfully growing in the {role_title} role can open the door to future opportunities like **{next_role}**."

    explanation += "\n\n**🎯 Next Steps**\n"
    explanation += "• Start a personal project to apply what you know.\n"
    explanation += "• Explore free tutorials on platforms like freeCodeCamp.\n"
    explanation += "• Follow industry leaders and companies on social media."
    return explanation

# --- Template 3: The Strategic Advisor ---
def get_strategist_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    role_title, domain, match_score, readiness, next_role = base["role_title"], base["domain"], base["match_score"], base["readiness"], base["next_role"]
    matched_names, priority_skills = base["matched_names"], base["priority_skills"]

    explanation = f"""**Strategic Fit for the {role_title} Role**

A strategic review of your profile shows a **{match_score:.0f}% match** for the **{role_title}** position within the **{domain}** industry. Let's outline a plan for success.

**✅ Your Current Assets**
"""
    if matched_names:
        explanation += f"You have a competitive advantage with {len(matched_names)} existing skills:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - Directly applicable to this role's duties.\n"
        if len(matched_names) > 5:
            explanation += f"• ...and {len(matched_names) - 5} more skills that give you an edge.\n"
    else:
        explanation += "Your professional background suggests you are a quick learner, which is a key asset.\n"

    explanation += "\n**🔧 Key Skills to Develop**\n"
    if priority_skills:
        explanation += "To strategically position yourself, focus on developing these key competencies:\n"
        for i, skill in enumerate(priority_skills):
            explanation += f"{i+1}. **{skill.title()}** - {_get_skill_advice(skill)}\n"
    else:
        explanation += "Your skill set is already comprehensive for this role.\n"

    explanation += f"\n**📊 Readiness Analysis: {readiness:.0f}%**\n"
    explanation += _get_readiness_text(readiness)

    if next_role:
        explanation += f"\n\n**🔮 Future Outlook**\nThis role is a stepping stone. With dedication, you can progress to roles such as **{next_role}**."

    explanation += "\n\n**💡 Action Plan**\n"
    explanation += "• Contribute to an open-source project to gain practical experience.\n"
    explanation += "• Earn certifications to validate your knowledge.\n"
    explanation += "• Update your resume to highlight your most relevant skills."
    return explanation

# --- Template 4: The Recruiter's Perspective ---
def get_recruiter_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    role_title, domain, match_score, readiness, next_role = base["role_title"], base["domain"], base["match_score"], base["readiness"], base["next_role"]
    matched_names, priority_skills = base["matched_names"], base["priority_skills"]

    explanation = f"""**Why You're a Candidate to Watch for {role_title}**

From a recruitment perspective, your profile has a **{match_score:.0f}%** alignment with what hiring managers are seeking for a **{role_title}** in the **{domain}** space.

**돋 Your Marketable Skills**
"""
    if matched_names:
        explanation += f"You're already equipped with {len(matched_names)} skills that are in high demand:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - A keyword that recruiters look for.\n"
        if len(matched_names) > 5:
            explanation += f"• ...and {len(matched_names) - 5} other valuable skills!\n"
    else:
        explanation += "Your resume shows a pattern of growth and learning, which is attractive to employers.\n"

    explanation += "\n**📈 How to Boost Your Profile**\n"
    if priority_skills:
        explanation += "To become a top-tier applicant, we recommend mastering these skills:\n"
        for i, skill in enumerate(priority_skills):
            explanation += f"{i+1}. **{skill.title()}** - {_get_skill_advice(skill)}\n"
    else:
        explanation += "Your skill set is what the market wants. Focus on showcasing it.\n"

    explanation += f"\n**📊 Candidate Readiness: {readiness:.0f}%**\n"
    explanation += _get_readiness_text(readiness)

    if next_role:
        explanation += f"\n\n**🔮 Career Advancement**\nThe {role_title} role is a gateway to more senior positions, such as **{next_role}**."

    explanation += "\n\n**💡 Professional Advice**\n"
    explanation += "• Tailor your resume for each job application.\n"
    explanation += "• Practice technical interview questions for this role.\n"
    explanation += "• Prepare a portfolio that tells a story about your skills."
    return explanation

# --- Template 5: The Simple & Clear Guide ---
def get_visual_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    role_title, domain, match_score, readiness, next_role = base["role_title"], base["domain"], base["match_score"], base["readiness"], base["next_role"]
    matched_names, priority_skills = base["matched_names"], base["priority_skills"]

    explanation = f"""**Your Guide to Becoming a {role_title}**

Our system shows a **{match_score:.0f}%** match between you and this role in the **{domain}** field. Here’s a simple breakdown of what that means.

**✅ What You've Got**
"""
    if matched_names:
        explanation += f"You have {len(matched_names)} skills that are a great fit:\n"
        for skill in matched_names[:5]:
            explanation += f"• **{skill.title()}** - A solid skill for this job.\n"
        if len(matched_names) > 5:
            explanation += f"• ...and {len(matched_names) - 5} more!\n"
    else:
        explanation += "You have a great foundation to build upon.\n"

    explanation += "\n**🚀 What to Learn Next**\n"
    if priority_skills:
        explanation += "Focus on these skills to get ready for your next step:\n"
        for i, skill in enumerate(priority_skills):
            explanation += f"{i+1}. **{skill.title()}** - {_get_skill_advice(skill)}\n"
    else:
        explanation += "You've got the key skills covered! Now it's time to apply them.\n"

    explanation += f"\n**📊 How Ready Are You? ({readiness:.0f}%)**\n"
    explanation += _get_readiness_text(readiness)

    if next_role:
        explanation += f"\n\n**🔮 The Next Chapter**\nAfter gaining experience as a {role_title}, you could advance to a **{next_role}** role."

    explanation += "\n\n**💡 Simple Next Steps**\n"
    explanation += "• Build something small to practice your skills.\n"
    explanation += "• Watch tutorials and read articles about this field.\n"
    explanation += "• Talk to people who are already in this role."
    return explanation
