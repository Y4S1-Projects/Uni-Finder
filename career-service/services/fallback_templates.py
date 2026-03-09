"""
Fallback explanation templates for the career recommendation explainability service.
Phase D: All templates now use structured Phase D data — matched_core_skills,
matched_supporting_skills, missing_critical_skills, seniority_fit, why_not_more_ready,
domain_impact, ladder position, profile_source, and full score breakdown.
No template produces generic text; every section references the user's actual data.
"""
from .skill_service import get_skill_name


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _names_from_structured(skill_list: list) -> list:
    """Extract human-readable names from [{id, name}] dicts."""
    return [s.get("name", s.get("id", "")) for s in (skill_list or []) if s]


def _generate_base_explanation(context: dict) -> dict:
    """Builds a rich base dict that every template can draw from."""
    # Legacy flat skill lists (IDs -> names)
    matched_names = [get_skill_name(s) for s in context.get("matched_skills", [])]
    missing_names = [get_skill_name(s) for s in context.get("missing_skills", [])]

    # Phase D structured skill lists (already contain names)
    core_skills    = _names_from_structured(context.get("matched_core_skills", []))
    support_skills = _names_from_structured(context.get("matched_supporting_skills", []))
    missing_crit   = _names_from_structured(context.get("missing_critical_skills", []))

    # Score breakdown
    sb = context.get("score_breakdown", {})
    explanations = context.get("explanations", {})

    # Profile
    experience_level = context.get("experience_level") or "not specified"
    current_status   = context.get("current_status") or "not specified"
    education_level  = context.get("education_level") or "not specified"
    career_goal      = context.get("career_goal") or "not specified"
    preferred_domain = context.get("preferred_domain") or ""

    return {
        # Role basics
        "role_title": context.get("role_title", "this role"),
        "domain": (context.get("domain") or "Technology").replace("_", " "),
        "match_score": (context.get("match_score") or 0) * 100,
        "readiness": (context.get("readiness_score") or 0) * 100,
        "next_role": context.get("next_role_title"),
        # Legacy skill names (flat)
        "matched_names": matched_names,
        "missing_names": missing_names,
        # Phase D structured skills
        "core_skills": core_skills,
        "support_skills": support_skills,
        "missing_critical": missing_crit,
        "priority_skills": missing_crit[:3] if missing_crit else missing_names[:3],
        # Scoring
        "core_coverage": sb.get("core_skill_coverage_score", 0),
        "domain_fit": sb.get("domain_preference_score", 0.5),
        "experience_fit": sb.get("experience_fit_score", 0.7),
        "seniority_fit_score": sb.get("seniority_fit_score", 0.7),
        "confidence": sb.get("confidence_score", 1.0),
        # Explanations from scoring engine
        "why_ranked": explanations.get("why_ranked_here", ""),
        "why_best": explanations.get("why_best_match", ""),
        "why_not_ready": explanations.get("why_not_more_ready", ""),
        "seniority_fit": explanations.get("seniority_fit", ""),
        "domain_impact": explanations.get("domain_impact", ""),
        "entry_level_note": explanations.get("entry_level_note", ""),
        "data_confidence": explanations.get("data_confidence", ""),
        # Ladder
        "seniority": context.get("seniority"),
        "ladder_position": context.get("ladder_position"),
        "ladder_length": context.get("ladder_length"),
        "is_best_match": context.get("is_best_match", False),
        "profile_source": context.get("profile_source", "data_backed"),
        # Profile
        "experience_level": experience_level,
        "current_status": current_status,
        "education_level": education_level,
        "career_goal": career_goal,
        "preferred_domain": preferred_domain.replace("_", " ") if preferred_domain else "",
    }


def _render_core_skills(core_skills: list, role_title: str) -> str:
    """Render matched core skills section."""
    if not core_skills:
        return "You don't currently match any of the core skills expected for this role.\n"
    out = f"You match **{len(core_skills)}** core skill(s) that {role_title} requires:\n"
    for s in core_skills[:6]:
        out += f"- **{s.title()}** — directly required for this role\n"
    if len(core_skills) > 6:
        out += f"- ...and {len(core_skills) - 6} more core skills\n"
    return out


def _render_supporting_skills(support_skills: list) -> str:
    """Render matched supporting skills section."""
    if not support_skills:
        return ""
    out = f"You also have **{len(support_skills)}** supporting skill(s):\n"
    for s in support_skills[:4]:
        out += f"- **{s.title()}**\n"
    if len(support_skills) > 4:
        out += f"- ...plus {len(support_skills) - 4} more\n"
    return out


def _render_missing_critical(missing_crit: list, role_title: str) -> str:
    """Render missing critical skills section."""
    if not missing_crit:
        return f"You have all the critical skills for {role_title}. Focus on deepening your expertise.\n"
    out = f"These **{len(missing_crit)}** critical skill(s) are expected but missing:\n"
    for s in missing_crit[:5]:
        out += f"- **{s.title()}** — required by employers for this role\n"
    if len(missing_crit) > 5:
        out += f"- ...and {len(missing_crit) - 5} more critical gaps\n"
    return out


def _render_why_not_ready(why_not_ready: str, missing_crit: list) -> str:
    """Render readiness limitations from scoring engine explanation."""
    if why_not_ready:
        return why_not_ready + "\n"
    if missing_crit:
        return f"Readiness is limited because you are missing {len(missing_crit)} critical skill(s): {', '.join(s.title() for s in missing_crit[:4])}.\n"
    return "Your readiness is strong — no critical gaps detected.\n"


def _render_ranking_reason(base: dict) -> str:
    """Render why this role ranked where it did."""
    parts = []
    if base["why_ranked"]:
        parts.append(base["why_ranked"])
    if base["is_best_match"] and base["why_best"]:
        parts.append(f"**Best match reason:** {base['why_best']}")
    elif not base["is_best_match"] and base["why_best"]:
        parts.append(base["why_best"])
    if base["domain_impact"]:
        parts.append(f"**Domain alignment:** {base['domain_impact']}")
    if base["seniority_fit"]:
        parts.append(f"**Seniority fit:** {base['seniority_fit']}")
    return "\n".join(parts) if parts else "Ranking is based on overall skill match and domain alignment."


def _render_ladder(base: dict) -> str:
    """Render career ladder context."""
    lp = base["ladder_position"]
    ll = base["ladder_length"]
    domain = base["domain"]
    next_role = base["next_role"]
    if lp and ll:
        out = f"This role sits at position **{lp} of {ll}** in the {domain} career ladder."
        if next_role:
            out += f" Your next step would be **{next_role}**."
        return out
    if next_role:
        return f"Your next career step from this role would be **{next_role}**."
    return ""


def _render_profile_context(base: dict) -> str:
    """Render a brief profile context block."""
    parts = []
    if base["preferred_domain"] and base["preferred_domain"] != "not specified":
        parts.append(f"**Domain preference:** {base['preferred_domain']}")
    if base["career_goal"] and base["career_goal"] != "not specified":
        parts.append(f"**Career goal:** {base['career_goal'].replace('_', ' ')}")
    if base["experience_level"] and base["experience_level"] != "not specified":
        parts.append(f"**Experience level:** {base['experience_level'].replace('_', ' ')}")
    if base["profile_source"] == "synthetic":
        parts.append("Note: This role uses a synthetic profile — data confidence is lower.")
    if base["entry_level_note"]:
        parts.append(base["entry_level_note"])
    return "\n".join(parts) if parts else ""


def _render_actionable_steps(missing_crit: list, role_title: str) -> str:
    """Generate specific improvement steps tied to missing critical skills."""
    if not missing_crit:
        return (
            f"- Build a portfolio project showcasing your {role_title} skills.\n"
            "- Contribute to open-source projects in this domain.\n"
            "- Prepare for technical interviews targeting this role.\n"
        )
    steps = []
    for i, skill in enumerate(missing_crit[:3]):
        s = skill.lower()
        if any(kw in s for kw in ("python", "java", "javascript", "typescript", "c++", "c#", "go", "rust")):
            steps.append(f"{i+1}. **Learn {skill.title()}** — Complete an online course and build a small project using it.")
        elif any(kw in s for kw in ("machine learning", "deep learning", "neural", "ai")):
            steps.append(f"{i+1}. **Study {skill.title()}** — Take a structured ML course (e.g., Andrew Ng's), then implement a project end-to-end.")
        elif any(kw in s for kw in ("docker", "kubernetes", "devops", "ci/cd", "cloud")):
            steps.append(f"{i+1}. **Practice {skill.title()}** — Containerize an existing project or deploy to a cloud provider.")
        elif any(kw in s for kw in ("sql", "database", "postgres", "mongo")):
            steps.append(f"{i+1}. **Master {skill.title()}** — Design a database schema for a real-world scenario and practice queries.")
        elif any(kw in s for kw in ("react", "angular", "vue", "frontend", "ui", "ux")):
            steps.append(f"{i+1}. **Build with {skill.title()}** — Create a responsive web app to demonstrate proficiency.")
        elif any(kw in s for kw in ("api", "rest", "graphql", "microservice")):
            steps.append(f"{i+1}. **Implement {skill.title()}** — Build a RESTful API with auth, testing, and documentation.")
        elif any(kw in s for kw in ("git", "version control")):
            steps.append(f"{i+1}. **Use {skill.title()} daily** — Contribute to a collaborative repo; learn branching, rebasing, and PR workflows.")
        elif any(kw in s for kw in ("testing", "unit test", "qa", "automation")):
            steps.append(f"{i+1}. **Practice {skill.title()}** — Write unit and integration tests for an existing project.")
        elif any(kw in s for kw in ("agile", "scrum", "project management")):
            steps.append(f"{i+1}. **Apply {skill.title()}** — Use agile practices in your next project; try sprint planning and retrospectives.")
        else:
            steps.append(f"{i+1}. **Develop {skill.title()}** — Find a focused tutorial or course, then apply it in a hands-on project.")
    return "\n".join(steps) + "\n"


# ---------------------------------------------------------------------------
# Template 1: The Direct Analyst
# ---------------------------------------------------------------------------
def get_analyst_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    rt = base["role_title"]

    explanation = f"""**Analysis: Why {rt} Was Recommended**

"""
    # Profile snapshot
    profile = _render_profile_context(base)
    if profile:
        explanation += profile + "\n\n"

    # Why this role matches
    explanation += f"**Why This Role Matches**\n"
    explanation += _render_core_skills(base["core_skills"], rt)
    supp = _render_supporting_skills(base["support_skills"])
    if supp:
        explanation += "\n" + supp

    # Ranking explanation
    explanation += f"\n**What Determines the Ranking**\n"
    explanation += _render_ranking_reason(base) + "\n"

    # What lowers readiness
    explanation += f"\n**What Lowers Your Readiness**\n"
    explanation += _render_missing_critical(base["missing_critical"], rt)
    explanation += _render_why_not_ready(base["why_not_ready"], base["missing_critical"])

    # Career ladder
    ladder = _render_ladder(base)
    if ladder:
        explanation += f"\n**Career Ladder**\n{ladder}\n"

    # Actionable steps
    explanation += f"\n**How to Improve**\n"
    explanation += _render_actionable_steps(base["missing_critical"], rt)

    return explanation


# ---------------------------------------------------------------------------
# Template 2: The Encouraging Coach
# ---------------------------------------------------------------------------
def get_coach_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    rt = base["role_title"]
    domain = base["domain"]

    explanation = f"""**Your Path Toward {rt}**

"""
    profile = _render_profile_context(base)
    if profile:
        explanation += profile + "\n\n"

    # Strengths
    explanation += f"**What You Bring to This Role**\n"
    explanation += _render_core_skills(base["core_skills"], rt)
    supp = _render_supporting_skills(base["support_skills"])
    if supp:
        explanation += "\n" + supp

    # Ranking
    explanation += f"\n**How This Role Ranks for You**\n"
    explanation += _render_ranking_reason(base) + "\n"

    # Gaps
    explanation += f"\n**Where to Focus Next**\n"
    explanation += _render_missing_critical(base["missing_critical"], rt)
    explanation += _render_why_not_ready(base["why_not_ready"], base["missing_critical"])

    # Ladder
    ladder = _render_ladder(base)
    if ladder:
        explanation += f"\n**Your Journey Ahead**\n{ladder}\n"

    # Steps
    explanation += f"\n**Concrete Next Steps**\n"
    explanation += _render_actionable_steps(base["missing_critical"], rt)

    return explanation


# ---------------------------------------------------------------------------
# Template 3: The Strategic Advisor
# ---------------------------------------------------------------------------
def get_strategist_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    rt = base["role_title"]
    domain = base["domain"]

    explanation = f"""**Strategic Assessment: {rt} in {domain}**

"""
    profile = _render_profile_context(base)
    if profile:
        explanation += profile + "\n\n"

    # Assets
    explanation += f"**Your Current Assets**\n"
    explanation += _render_core_skills(base["core_skills"], rt)
    supp = _render_supporting_skills(base["support_skills"])
    if supp:
        explanation += "\n" + supp

    # Strategy — ranking
    explanation += f"\n**Ranking Strategy**\n"
    explanation += _render_ranking_reason(base) + "\n"

    # Gaps
    explanation += f"\n**Critical Gaps to Close**\n"
    explanation += _render_missing_critical(base["missing_critical"], rt)
    explanation += _render_why_not_ready(base["why_not_ready"], base["missing_critical"])

    # Ladder
    ladder = _render_ladder(base)
    if ladder:
        explanation += f"\n**Career Progression**\n{ladder}\n"

    # Action plan
    explanation += f"\n**Action Plan**\n"
    explanation += _render_actionable_steps(base["missing_critical"], rt)

    return explanation


# ---------------------------------------------------------------------------
# Template 4: The Recruiter's Perspective
# ---------------------------------------------------------------------------
def get_recruiter_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    rt = base["role_title"]
    domain = base["domain"]

    explanation = f"""**Recruiter's View: Your Fit for {rt}**

"""
    profile = _render_profile_context(base)
    if profile:
        explanation += profile + "\n\n"

    # Marketable skills
    explanation += f"**Your Marketable Skills**\n"
    explanation += _render_core_skills(base["core_skills"], rt)
    supp = _render_supporting_skills(base["support_skills"])
    if supp:
        explanation += "\n" + supp

    # What hiring managers see
    explanation += f"\n**What Hiring Managers See**\n"
    explanation += _render_ranking_reason(base) + "\n"

    # What's missing
    explanation += f"\n**How to Strengthen Your Application**\n"
    explanation += _render_missing_critical(base["missing_critical"], rt)
    explanation += _render_why_not_ready(base["why_not_ready"], base["missing_critical"])

    # Ladder
    ladder = _render_ladder(base)
    if ladder:
        explanation += f"\n**Career Advancement**\n{ladder}\n"

    # Professional advice
    explanation += f"\n**Professional Development**\n"
    explanation += _render_actionable_steps(base["missing_critical"], rt)

    return explanation


# ---------------------------------------------------------------------------
# Template 5: The Clear Breakdown
# ---------------------------------------------------------------------------
def get_visual_explanation(context: dict) -> str:
    base = _generate_base_explanation(context)
    rt = base["role_title"]
    domain = base["domain"]

    explanation = f"""**Breakdown: {rt} ({domain})**

"""
    profile = _render_profile_context(base)
    if profile:
        explanation += profile + "\n\n"

    # What you have
    explanation += f"**Skills You Already Have**\n"
    explanation += _render_core_skills(base["core_skills"], rt)
    supp = _render_supporting_skills(base["support_skills"])
    if supp:
        explanation += "\n" + supp

    # Why this rank
    explanation += f"\n**Why This Ranking**\n"
    explanation += _render_ranking_reason(base) + "\n"

    # What's missing
    explanation += f"\n**Skills to Acquire**\n"
    explanation += _render_missing_critical(base["missing_critical"], rt)
    explanation += _render_why_not_ready(base["why_not_ready"], base["missing_critical"])

    # Ladder
    ladder = _render_ladder(base)
    if ladder:
        explanation += f"\n**What Comes Next**\n{ladder}\n"

    # Steps
    explanation += f"\n**Your Next Moves**\n"
    explanation += _render_actionable_steps(base["missing_critical"], rt)

    return explanation
