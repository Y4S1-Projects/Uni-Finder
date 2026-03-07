#!/usr/bin/env python3
"""
expand_career_ladders_v2.py
───────────────────────────
Expand career ladders from 7 domains / 15 roles → 20 domains / 150+ roles.

Creates two primary outputs:
  1. career_ladders_v2.json   – domain → ordered role list (progression)
  2. role_metadata.json       – extended metadata per role (salary, certs, …)

Also generates a validation report and backwards-compatibility mapping.

Usage
-----
  python scripts/expand_career_ladders_v2.py                  # full run
  python scripts/expand_career_ladders_v2.py --validate-only  # check existing files
"""
from __future__ import annotations

import argparse
import json
import logging
import textwrap
import time
from collections import OrderedDict
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent               # career-ml/
OLD_LADDERS    = ROOT / "career_path" / "career_ladders.json"
OUT_LADDERS    = ROOT / "data" / "processed" / "career_ladders_v2.json"
OUT_METADATA   = ROOT / "data" / "processed" / "role_metadata.json"
OUT_REPORT     = ROOT / "data" / "reports" / "career_ladders_v2_report.txt"
PROFILES_PATH  = ROOT / "data" / "processed" / "role_skill_profiles_v2.csv"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
#  1. EXPANDED CAREER LADDERS  (20 domains, 150+ roles)
# ═════════════════════════════════════════════════════════════════════════════
#  Each list is ORDERED from entry-level → most senior.
#  Roles marked with (*) match existing 15 data-backed roles.

CAREER_LADDERS_V2: dict[str, list[str]] = OrderedDict({

    # ─ 1. Software Engineering (general IC + management track) ───────────
    "SOFTWARE_ENGINEERING": [
        "INTERN_SE",            # (*) L1 intern
        "JR_SE",                # (*) L2 junior
        "SE_I",                 # L3 mid
        "SE_II",                # L3 mid
        "SENIOR_SE",            # L4 senior
        "STAFF_ENGINEER",       # L5 staff
        "TECH_LEAD",            # L6 lead
        "PRINCIPAL_ENGINEER",   # L6 lead
        "DISTINGUISHED_ENGINEER", # L7 architect
        "ENGINEERING_MANAGER",  # L8 management
        "SR_ENGINEERING_MANAGER", # L8 management
        "DIRECTOR_ENGINEERING", # L9 executive
        "VP_ENGINEERING",       # L9 executive
        "CTO",                  # L9 executive
    ],

    # ─ 2. Frontend Engineering ───────────────────────────────────────────
    "FRONTEND_ENGINEERING": [
        "JR_FE_DEV",           # (*)
        "FE_DEV",
        "SENIOR_FE_DEV",
        "STAFF_FE_DEV",
        "LEAD_FE_DEV",
        "FRONTEND_ARCHITECT",
        "DIRECTOR_FRONTEND",
    ],

    # ─ 3. Backend Engineering ────────────────────────────────────────────
    "BACKEND_ENGINEERING": [
        "JR_BE_DEV",           # (*)
        "BE_DEV",
        "SENIOR_BE_DEV",
        "STAFF_BE_DEV",
        "LEAD_BE_DEV",
        "BACKEND_ARCHITECT",
        "SYSTEMS_ARCHITECT",
        "DIRECTOR_BACKEND",
    ],

    # ─ 4. Full-Stack Engineering ─────────────────────────────────────────
    "FULLSTACK_ENGINEERING": [
        "JR_FS_DEV",           # (*)
        "FS_DEV",
        "SENIOR_FS_DEV",
        "STAFF_FS_DEV",
        "LEAD_FS_DEV",
        "FULLSTACK_ARCHITECT",
    ],

    # ─ 5. Data Engineering & Analytics ───────────────────────────────────
    "DATA_ENGINEERING": [
        "DATA_ANALYST_INT",     # (*) L1 intern
        "DATA_ENGINEER_INT",    # (*) L1 intern
        "JR_DATA_ANALYST",      # L2 junior
        "JR_DATA_ENGINEER",     # L2 junior
        "DATA_ANALYST",         # L3 mid
        "DATA_ENGINEER",        # L3 mid
        "SENIOR_DATA_ANALYST",  # L4 senior
        "SENIOR_DATA_ENGINEER", # L4 senior
        "STAFF_DATA_ENGINEER",  # L5 staff
        "LEAD_DATA_ANALYST",    # L6 lead
        "PRINCIPAL_DATA_ENGINEER", # L6 lead
        "DATA_ARCHITECT",       # L7 architect
        "DIRECTOR_DATA",        # L9 executive
    ],

    # ─ 6. Data Science ──────────────────────────────────────────────────
    "DATA_SCIENCE": [
        "DATA_SCIENTIST_INT",   # L1 intern
        "JR_DATA_SCIENTIST",    # L2 junior
        "DATA_SCIENTIST",       # L3 mid
        "RESEARCH_SCIENTIST",   # L3 mid
        "SENIOR_DATA_SCIENTIST", # L4 senior
        "STAFF_DATA_SCIENTIST", # L5 staff
        "PRINCIPAL_DATA_SCIENTIST", # L6 lead
        "DIRECTOR_DATA_SCIENCE", # L9 executive
        "HEAD_OF_DATA_SCIENCE", # L9 executive
    ],

    # ─ 7. AI / ML ───────────────────────────────────────────────────────
    "AI_ML": [
        "AI_ML_ENGINEER_INT",  # (*) L1 intern
        "JR_ML_ENGINEER",      # L2 junior
        "ML_ENGINEER",          # L3 mid
        "ML_RESEARCH_SCIENTIST", # L3 mid
        "SENIOR_ML_ENGINEER",   # L4 senior
        "STAFF_ML_ENGINEER",    # L5 staff
        "PRINCIPAL_ML_ENGINEER", # L6 lead
        "AI_ARCHITECT",         # L7 architect
        "DIRECTOR_AI_ML",       # L9 executive
        "HEAD_OF_AI",           # L9 executive
    ],

    # ─ 8. DevOps / SRE ──────────────────────────────────────────────────
    "DEVOPS_SRE": [
        "DEVOPS_TRAINEE",      # (*) L1 intern
        "JR_DEVOPS_ENG",       # L2 junior
        "JR_SRE",              # L2 junior
        "DEVOPS_ENGINEER",     # L3 mid
        "SRE",                 # L3 mid
        "SENIOR_DEVOPS_ENG",   # L4 senior
        "SENIOR_SRE",          # L4 senior
        "STAFF_DEVOPS_ENG",    # L5 staff
        "STAFF_SRE",           # L5 staff
        "LEAD_DEVOPS_ENG",     # L6 lead
        "PRINCIPAL_SRE",       # L6 lead
        "DEVOPS_ARCHITECT",    # L7 architect
        "DIRECTOR_INFRASTRUCTURE", # L9 executive
    ],

    # ─ 9. Cloud Engineering ──────────────────────────────────────────────
    "CLOUD_ENGINEERING": [
        "JR_CLOUD_ENG",          # L2 junior
        "CLOUD_ENGINEER",        # L3 mid
        "SENIOR_CLOUD_ENG",      # L4 senior
        "STAFF_CLOUD_ENG",       # L5 staff
        "PRINCIPAL_CLOUD_ARCHITECT", # L6 lead
        "CLOUD_PLATFORM_LEAD",   # L6 lead
        "CLOUD_ARCHITECT",       # L7 architect
        "DIRECTOR_CLOUD",        # L9 executive
    ],

    # ─ 10. Security ─────────────────────────────────────────────────────
    "SECURITY": [
        "SECURITY_ANALYST_INT",  # L1 intern
        "JR_SECURITY_ANALYST",   # L2 junior
        "SECURITY_ANALYST",      # L3 mid
        "SECURITY_ENGINEER",     # L3 mid
        "SENIOR_SECURITY_ENG",   # L4 senior
        "STAFF_SECURITY_ENG",    # L5 staff
        "LEAD_SECURITY_ENG",     # L6 lead
        "PRINCIPAL_SECURITY_ARCHITECT", # L6 lead
        "SECURITY_ARCHITECT",    # L7 architect
        "DIRECTOR_SECURITY",     # L9 executive
        "CISO",                  # L9 executive
    ],

    # ─ 11. QA / Testing ─────────────────────────────────────────────────
    "QA_TESTING": [
        "JR_QA_ENG",           # (*) L2 junior
        "QA_ENGINEER",          # L3 mid
        "QA_AUTOMATION_ENG",    # L3 mid
        "SENIOR_QA_ENG",        # L4 senior
        "SENIOR_QA_AUTOMATION", # L4 senior
        "LEAD_QA_ENG",          # L6 lead
        "QA_ARCHITECT",         # L7 architect
        "DIRECTOR_QA",          # L9 executive
    ],

    # ─ 12. Mobile Engineering ────────────────────────────────────────────
    "MOBILE_ENGINEERING": [
        "JR_MOBILE_DEV",      # (*)
        "MOBILE_DEV",
        "SENIOR_MOBILE_DEV",
        "STAFF_MOBILE_DEV",
        "LEAD_MOBILE_DEV",
        "MOBILE_ARCHITECT",
        "DIRECTOR_MOBILE",
    ],

    # ─ 13. UI/UX Design ─────────────────────────────────────────────────
    "UI_UX_DESIGN": [
        "JR_UI_UX_DESIGNER",  # (*)
        "UI_UX_DESIGNER",
        "SENIOR_UI_UX_DESIGNER",
        "LEAD_UI_UX_DESIGNER",
        "PRINCIPAL_DESIGNER",
        "DESIGN_MANAGER",
        "DIRECTOR_DESIGN",
        "HEAD_OF_DESIGN",
    ],

    # ─ 14. Product Management ────────────────────────────────────────────
    "PRODUCT_MANAGEMENT": [
        "ASSOCIATE_PM",
        "PRODUCT_MANAGER",
        "SENIOR_PM",
        "LEAD_PM",
        "PRINCIPAL_PM",
        "GROUP_PM",
        "DIRECTOR_PRODUCT",
        "VP_PRODUCT",
        "CPO",
    ],

    # ─ 15. Business Analysis ────────────────────────────────────────────
    "BUSINESS_ANALYSIS": [
        "JR_BUSINESS_ANALYST", # (*)
        "BUSINESS_ANALYST",
        "SENIOR_BA",
        "LEAD_BA",
        "PRINCIPAL_BA",
        "BUSINESS_ARCHITECT",
        "DIRECTOR_BUSINESS_ANALYSIS",
    ],

    # ─ 16. Project / Program Management ──────────────────────────────────
    "PROJECT_MANAGEMENT": [
        "JR_PROJECT_MANAGER",    # L2 junior
        "PROJECT_MANAGER",       # L3 mid
        "PROGRAM_MANAGER",       # L3 mid
        "SENIOR_PROJECT_MANAGER", # L4 senior
        "SENIOR_PROGRAM_MANAGER", # L4 senior
        "DIRECTOR_PMO",          # L9 executive
        "VP_PROJECT_MANAGEMENT", # L9 executive
    ],

    # ─ 17. Technical Writing ─────────────────────────────────────────────
    "TECHNICAL_WRITING": [
        "JR_TECH_WRITER",
        "TECH_WRITER",
        "SENIOR_TECH_WRITER",
        "LEAD_TECH_WRITER",
        "DOCUMENTATION_MANAGER",
        "DIRECTOR_DOCUMENTATION",
    ],

    # ─ 18. Blockchain / Web3 ─────────────────────────────────────────────
    "BLOCKCHAIN_WEB3": [
        "BLOCKCHAIN_DEV_INT",    # L1 intern
        "BLOCKCHAIN_DEVELOPER",  # L3 mid
        "WEB3_ENGINEER",         # L3 mid
        "SENIOR_BLOCKCHAIN_DEV", # L4 senior
        "LEAD_BLOCKCHAIN",       # L6 lead
        "BLOCKCHAIN_ARCHITECT",  # L7 architect
        "DIRECTOR_BLOCKCHAIN",   # L9 executive
    ],

    # ─ 19. Game Development ──────────────────────────────────────────────
    "GAME_DEVELOPMENT": [
        "JR_GAME_DEV",           # L2 junior
        "GAME_DEVELOPER",        # L3 mid
        "GAME_DESIGNER",         # L3 mid
        "SENIOR_GAME_DEV",       # L4 senior
        "LEAD_GAME_DEV",         # L6 lead
        "TECHNICAL_GAME_DESIGNER", # L6 lead
        "GAME_ARCHITECT",        # L7 architect
        "GAME_DIRECTOR",         # L9 executive
    ],

    # ─ 20. Embedded Systems / IoT ────────────────────────────────────────
    "EMBEDDED_SYSTEMS": [
        "EMBEDDED_ENG_INT",      # L1 intern
        "EMBEDDED_ENGINEER",     # L3 mid
        "FIRMWARE_ENGINEER",     # L3 mid
        "SENIOR_EMBEDDED_ENG",   # L4 senior
        "STAFF_EMBEDDED_ENG",    # L5 staff
        "EMBEDDED_ARCHITECT",    # L7 architect
        "DIRECTOR_EMBEDDED",     # L9 executive
    ],
})


# ═════════════════════════════════════════════════════════════════════════════
#  2. SENIORITY ASSIGNMENT  (explicit per-role mapping)
# ═════════════════════════════════════════════════════════════════════════════


def _assign_seniority(role_id: str) -> tuple[int, str]:
    """Determine seniority level + label for a role ID.

    Uses an explicit override table first, then falls back to pattern matching.
    The override table handles roles whose names confuse the generic patterns
    (e.g. TECH_LEAD has "LEAD" but also needs to be above PRINCIPAL).
    """
    # ── Explicit overrides for ambiguous roles ────────────────────────────
    _OVERRIDES: dict[str, tuple[int, str]] = {
        # Software Engineering management/IC senior track
        "TECH_LEAD":                (6, "lead"),
        "ENGINEERING_MANAGER":      (8, "management"),
        "SR_ENGINEERING_MANAGER":   (8, "management"),
        "DIRECTOR_ENGINEERING":     (9, "executive"),
        "DIRECTOR_FRONTEND":        (9, "executive"),
        "DIRECTOR_BACKEND":         (9, "executive"),
        "DIRECTOR_MOBILE":          (9, "executive"),
        "DIRECTOR_QA":              (9, "executive"),
        "DIRECTOR_DATA":            (9, "executive"),
        "DIRECTOR_DATA_SCIENCE":    (9, "executive"),
        "DIRECTOR_AI_ML":           (9, "executive"),
        "DIRECTOR_INFRASTRUCTURE":  (9, "executive"),
        "DIRECTOR_CLOUD":           (9, "executive"),
        "DIRECTOR_SECURITY":        (9, "executive"),
        "DIRECTOR_DESIGN":          (9, "executive"),
        "DIRECTOR_PRODUCT":         (9, "executive"),
        "DIRECTOR_BUSINESS_ANALYSIS": (9, "executive"),
        "DIRECTOR_PMO":             (9, "executive"),
        "DIRECTOR_DOCUMENTATION":   (9, "executive"),
        "DIRECTOR_BLOCKCHAIN":      (9, "executive"),
        "DIRECTOR_EMBEDDED":        (9, "executive"),
        "VP_ENGINEERING":           (9, "executive"),
        "VP_PRODUCT":               (9, "executive"),
        "VP_PROJECT_MANAGEMENT":    (9, "executive"),
        "CTO":                      (9, "executive"),
        "CPO":                      (9, "executive"),
        "CISO":                     (9, "executive"),
        # HEAD_OF variants — executive level
        "HEAD_OF_DATA_SCIENCE":     (9, "executive"),
        "HEAD_OF_AI":               (9, "executive"),
        "HEAD_OF_DESIGN":           (9, "executive"),
        # GAME_DIRECTOR — executive
        "GAME_DIRECTOR":            (9, "executive"),
        # Interns / trainees
        "INTERN_SE":                (1, "intern"),
        "DATA_ANALYST_INT":         (1, "intern"),
        "DATA_ENGINEER_INT":        (1, "intern"),
        "AI_ML_ENGINEER_INT":       (1, "intern"),
        "DATA_SCIENTIST_INT":       (1, "intern"),
        "DEVOPS_TRAINEE":           (1, "intern"),
        "SECURITY_ANALYST_INT":     (1, "intern"),
        "BLOCKCHAIN_DEV_INT":       (1, "intern"),
        "EMBEDDED_ENG_INT":         (1, "intern"),
        # Juniors
        "JR_SE":                    (2, "junior"),
        "JR_FE_DEV":               (2, "junior"),
        "JR_BE_DEV":               (2, "junior"),
        "JR_FS_DEV":               (2, "junior"),
        "JR_MOBILE_DEV":           (2, "junior"),
        "JR_QA_ENG":               (2, "junior"),
        "JR_UI_UX_DESIGNER":       (2, "junior"),
        "JR_BUSINESS_ANALYST":     (2, "junior"),
        "JR_SYS_ADMIN":            (2, "junior"),
        "JR_IT_SUPPORT":           (2, "junior"),
        "JR_DATA_ANALYST":         (2, "junior"),
        "JR_DATA_ENGINEER":        (2, "junior"),
        "JR_DATA_SCIENTIST":       (2, "junior"),
        "JR_ML_ENGINEER":          (2, "junior"),
        "JR_DEVOPS_ENG":           (2, "junior"),
        "JR_SRE":                  (2, "junior"),
        "JR_CLOUD_ENG":            (2, "junior"),
        "JR_SECURITY_ANALYST":     (2, "junior"),
        "JR_PROJECT_MANAGER":      (2, "junior"),
        "JR_TECH_WRITER":          (2, "junior"),
        "JR_GAME_DEV":             (2, "junior"),
        "ASSOCIATE_PM":            (2, "junior"),
        # Mid-level (simple title, no prefix)
        "SE_I":                     (3, "mid"),
        "SE_II":                    (3, "mid"),
        "FE_DEV":                  (3, "mid"),
        "BE_DEV":                  (3, "mid"),
        "FS_DEV":                  (3, "mid"),
        "MOBILE_DEV":              (3, "mid"),
        "QA_ENGINEER":             (3, "mid"),
        "QA_AUTOMATION_ENG":       (3, "mid"),
        "UI_UX_DESIGNER":         (3, "mid"),
        "DATA_ANALYST":            (3, "mid"),
        "DATA_ENGINEER":           (3, "mid"),
        "DATA_SCIENTIST":          (3, "mid"),
        "ML_ENGINEER":             (3, "mid"),
        "DEVOPS_ENGINEER":         (3, "mid"),
        "SRE":                     (3, "mid"),
        "CLOUD_ENGINEER":          (3, "mid"),
        "SECURITY_ANALYST":        (3, "mid"),
        "SECURITY_ENGINEER":       (3, "mid"),
        "BUSINESS_ANALYST":        (3, "mid"),
        "PROJECT_MANAGER":         (3, "mid"),
        "PRODUCT_MANAGER":         (3, "mid"),
        "PROGRAM_MANAGER":         (3, "mid"),
        "TECH_WRITER":             (3, "mid"),
        "BLOCKCHAIN_DEVELOPER":    (3, "mid"),
        "WEB3_ENGINEER":           (3, "mid"),
        "GAME_DEVELOPER":          (3, "mid"),
        "GAME_DESIGNER":           (3, "mid"),
        "EMBEDDED_ENGINEER":       (3, "mid"),
        "FIRMWARE_ENGINEER":       (3, "mid"),
        "RESEARCH_SCIENTIST":      (3, "mid"),
        "ML_RESEARCH_SCIENTIST":   (3, "mid"),
        # Senior
        "SENIOR_SE":               (4, "senior"),
        "SENIOR_FE_DEV":           (4, "senior"),
        "SENIOR_BE_DEV":           (4, "senior"),
        "SENIOR_FS_DEV":           (4, "senior"),
        "SENIOR_MOBILE_DEV":       (4, "senior"),
        "SENIOR_QA_ENG":           (4, "senior"),
        "SENIOR_QA_AUTOMATION":    (4, "senior"),
        "SENIOR_UI_UX_DESIGNER":   (4, "senior"),
        "SENIOR_DATA_ANALYST":     (4, "senior"),
        "SENIOR_DATA_ENGINEER":    (4, "senior"),
        "SENIOR_DATA_SCIENTIST":   (4, "senior"),
        "SENIOR_ML_ENGINEER":      (4, "senior"),
        "SENIOR_DEVOPS_ENG":       (4, "senior"),
        "SENIOR_SRE":              (4, "senior"),
        "SENIOR_CLOUD_ENG":        (4, "senior"),
        "SENIOR_SECURITY_ENG":     (4, "senior"),
        "SENIOR_BA":               (4, "senior"),
        "SENIOR_PM":               (4, "senior"),
        "SENIOR_PROJECT_MANAGER":  (4, "senior"),
        "SENIOR_PROGRAM_MANAGER":  (4, "senior"),
        "SENIOR_TECH_WRITER":      (4, "senior"),
        "SENIOR_BLOCKCHAIN_DEV":   (4, "senior"),
        "SENIOR_GAME_DEV":         (4, "senior"),
        "SENIOR_EMBEDDED_ENG":     (4, "senior"),
        # Staff
        "STAFF_ENGINEER":          (5, "staff"),
        "STAFF_FE_DEV":            (5, "staff"),
        "STAFF_BE_DEV":            (5, "staff"),
        "STAFF_FS_DEV":            (5, "staff"),
        "STAFF_MOBILE_DEV":        (5, "staff"),
        "STAFF_DATA_ENGINEER":     (5, "staff"),
        "STAFF_DATA_SCIENTIST":    (5, "staff"),
        "STAFF_ML_ENGINEER":       (5, "staff"),
        "STAFF_DEVOPS_ENG":        (5, "staff"),
        "STAFF_SRE":               (5, "staff"),
        "STAFF_CLOUD_ENG":         (5, "staff"),
        "STAFF_SECURITY_ENG":      (5, "staff"),
        "STAFF_EMBEDDED_ENG":      (5, "staff"),
        # Lead / Principal
        "LEAD_FE_DEV":             (6, "lead"),
        "LEAD_BE_DEV":             (6, "lead"),
        "LEAD_FS_DEV":             (6, "lead"),
        "LEAD_MOBILE_DEV":         (6, "lead"),
        "LEAD_DATA_ANALYST":       (6, "lead"),
        "LEAD_QA_ENG":             (6, "lead"),
        "LEAD_UI_UX_DESIGNER":     (6, "lead"),
        "LEAD_DEVOPS_ENG":         (6, "lead"),
        "LEAD_BA":                 (6, "lead"),
        "LEAD_PM":                 (6, "lead"),
        "LEAD_TECH_WRITER":        (6, "lead"),
        "LEAD_SECURITY_ENG":       (6, "lead"),
        "LEAD_BLOCKCHAIN":         (6, "lead"),
        "LEAD_GAME_DEV":           (6, "lead"),
        "PRINCIPAL_ENGINEER":      (6, "lead"),
        "PRINCIPAL_DATA_ENGINEER": (6, "lead"),
        "PRINCIPAL_DATA_SCIENTIST":(6, "lead"),
        "PRINCIPAL_ML_ENGINEER":   (6, "lead"),
        "PRINCIPAL_SRE":           (6, "lead"),
        "PRINCIPAL_DESIGNER":      (6, "lead"),
        "PRINCIPAL_PM":            (6, "lead"),
        "PRINCIPAL_BA":            (6, "lead"),
        "PRINCIPAL_CLOUD_ARCHITECT":(6, "lead"),
        "PRINCIPAL_SECURITY_ARCHITECT": (6, "lead"),
        "GROUP_PM":                (6, "lead"),
        "CLOUD_PLATFORM_LEAD":     (6, "lead"),
        "TECHNICAL_GAME_DESIGNER": (6, "lead"),
        # Architect / Distinguished
        "DISTINGUISHED_ENGINEER":  (7, "architect"),
        "FRONTEND_ARCHITECT":      (7, "architect"),
        "BACKEND_ARCHITECT":       (7, "architect"),
        "SYSTEMS_ARCHITECT":       (7, "architect"),
        "FULLSTACK_ARCHITECT":     (7, "architect"),
        "DATA_ARCHITECT":          (7, "architect"),
        "AI_ARCHITECT":            (7, "architect"),
        "DEVOPS_ARCHITECT":        (7, "architect"),
        "CLOUD_ARCHITECT":         (7, "architect"),
        "SECURITY_ARCHITECT":      (7, "architect"),
        "QA_ARCHITECT":            (7, "architect"),
        "MOBILE_ARCHITECT":        (7, "architect"),
        "BUSINESS_ARCHITECT":      (7, "architect"),
        "BLOCKCHAIN_ARCHITECT":    (7, "architect"),
        "GAME_ARCHITECT":          (7, "architect"),
        "EMBEDDED_ARCHITECT":      (7, "architect"),
        # Management
        "DESIGN_MANAGER":          (8, "management"),
        "DOCUMENTATION_MANAGER":   (8, "management"),
    }

    if role_id in _OVERRIDES:
        return _OVERRIDES[role_id]

    # Fallback — shouldn't happen if all roles are in override table
    log.warning("No explicit seniority override for %s — using default mid(3)", role_id)
    return 3, "mid"


# ═════════════════════════════════════════════════════════════════════════════
#  3. ROLE METADATA  (extended info per role)
# ═════════════════════════════════════════════════════════════════════════════

def _nice_title(role_id: str) -> str:
    """SENIOR_FE_DEV → Senior Frontend Developer."""
    _TITLE_MAP: dict[str, str] = {
        # ── Software Engineering ────────────────────────────
        "INTERN_SE":                "Software Engineering Intern",
        "JR_SE":                    "Junior Software Engineer",
        "SE_I":                     "Software Engineer I",
        "SE_II":                    "Software Engineer II",
        "SENIOR_SE":                "Senior Software Engineer",
        "STAFF_ENGINEER":           "Staff Engineer",
        "PRINCIPAL_ENGINEER":       "Principal Engineer",
        "DISTINGUISHED_ENGINEER":   "Distinguished Engineer",
        "TECH_LEAD":                "Tech Lead",
        "ENGINEERING_MANAGER":      "Engineering Manager",
        "SR_ENGINEERING_MANAGER":   "Senior Engineering Manager",
        "DIRECTOR_ENGINEERING":     "Director of Engineering",
        "VP_ENGINEERING":           "VP of Engineering",
        "CTO":                      "Chief Technology Officer",
        # ── Frontend ────────────────────────────────────────
        "JR_FE_DEV":               "Junior Frontend Developer",
        "FE_DEV":                  "Frontend Developer",
        "SENIOR_FE_DEV":           "Senior Frontend Developer",
        "STAFF_FE_DEV":            "Staff Frontend Developer",
        "LEAD_FE_DEV":             "Lead Frontend Developer",
        "FRONTEND_ARCHITECT":      "Frontend Architect",
        "DIRECTOR_FRONTEND":       "Director of Frontend Engineering",
        # ── Backend ─────────────────────────────────────────
        "JR_BE_DEV":               "Junior Backend Developer",
        "BE_DEV":                  "Backend Developer",
        "SENIOR_BE_DEV":           "Senior Backend Developer",
        "STAFF_BE_DEV":            "Staff Backend Developer",
        "LEAD_BE_DEV":             "Lead Backend Developer",
        "BACKEND_ARCHITECT":       "Backend Architect",
        "SYSTEMS_ARCHITECT":       "Systems Architect",
        "DIRECTOR_BACKEND":        "Director of Backend Engineering",
        # ── Full-Stack ──────────────────────────────────────
        "JR_FS_DEV":               "Junior Full-Stack Developer",
        "FS_DEV":                  "Full-Stack Developer",
        "SENIOR_FS_DEV":           "Senior Full-Stack Developer",
        "STAFF_FS_DEV":            "Staff Full-Stack Developer",
        "LEAD_FS_DEV":             "Lead Full-Stack Developer",
        "FULLSTACK_ARCHITECT":     "Full-Stack Architect",
        # ── Data Engineering ────────────────────────────────
        "DATA_ANALYST_INT":        "Data Analyst (Entry Level)",
        "JR_DATA_ANALYST":         "Junior Data Analyst",
        "DATA_ANALYST":            "Data Analyst",
        "SENIOR_DATA_ANALYST":     "Senior Data Analyst",
        "LEAD_DATA_ANALYST":       "Lead Data Analyst",
        "DATA_ENGINEER_INT":       "Data Engineer (Entry Level)",
        "JR_DATA_ENGINEER":        "Junior Data Engineer",
        "DATA_ENGINEER":           "Data Engineer",
        "SENIOR_DATA_ENGINEER":    "Senior Data Engineer",
        "STAFF_DATA_ENGINEER":     "Staff Data Engineer",
        "PRINCIPAL_DATA_ENGINEER": "Principal Data Engineer",
        "DATA_ARCHITECT":          "Data Architect",
        "DIRECTOR_DATA":           "Director of Data Engineering",
        # ── Data Science ────────────────────────────────────
        "DATA_SCIENTIST_INT":      "Data Scientist (Entry Level)",
        "JR_DATA_SCIENTIST":       "Junior Data Scientist",
        "DATA_SCIENTIST":          "Data Scientist",
        "SENIOR_DATA_SCIENTIST":   "Senior Data Scientist",
        "STAFF_DATA_SCIENTIST":    "Staff Data Scientist",
        "PRINCIPAL_DATA_SCIENTIST":"Principal Data Scientist",
        "RESEARCH_SCIENTIST":      "Research Scientist",
        "DIRECTOR_DATA_SCIENCE":   "Director of Data Science",
        "HEAD_OF_DATA_SCIENCE":    "Head of Data Science",
        # ── AI / ML ─────────────────────────────────────────
        "AI_ML_ENGINEER_INT":      "AI / ML Engineer (Entry Level)",
        "JR_ML_ENGINEER":          "Junior ML Engineer",
        "ML_ENGINEER":             "ML Engineer",
        "SENIOR_ML_ENGINEER":      "Senior ML Engineer",
        "STAFF_ML_ENGINEER":       "Staff ML Engineer",
        "PRINCIPAL_ML_ENGINEER":   "Principal ML Engineer",
        "ML_RESEARCH_SCIENTIST":   "ML Research Scientist",
        "AI_ARCHITECT":            "AI Architect",
        "DIRECTOR_AI_ML":          "Director of AI / ML",
        "HEAD_OF_AI":              "Head of AI",
        # ── DevOps / SRE ────────────────────────────────────
        "DEVOPS_TRAINEE":          "DevOps Trainee",
        "JR_DEVOPS_ENG":           "Junior DevOps Engineer",
        "DEVOPS_ENGINEER":         "DevOps Engineer",
        "SENIOR_DEVOPS_ENG":       "Senior DevOps Engineer",
        "STAFF_DEVOPS_ENG":        "Staff DevOps Engineer",
        "LEAD_DEVOPS_ENG":         "Lead DevOps Engineer",
        "DEVOPS_ARCHITECT":        "DevOps Architect",
        "JR_SRE":                  "Junior Site Reliability Engineer",
        "SRE":                     "Site Reliability Engineer",
        "SENIOR_SRE":              "Senior SRE",
        "STAFF_SRE":               "Staff SRE",
        "PRINCIPAL_SRE":           "Principal SRE",
        "DIRECTOR_INFRASTRUCTURE": "Director of Infrastructure",
        # ── Cloud Engineering ───────────────────────────────
        "JR_CLOUD_ENG":            "Junior Cloud Engineer",
        "CLOUD_ENGINEER":          "Cloud Engineer",
        "SENIOR_CLOUD_ENG":        "Senior Cloud Engineer",
        "STAFF_CLOUD_ENG":         "Staff Cloud Engineer",
        "CLOUD_ARCHITECT":         "Cloud Architect",
        "PRINCIPAL_CLOUD_ARCHITECT":"Principal Cloud Architect",
        "CLOUD_PLATFORM_LEAD":     "Cloud Platform Lead",
        "DIRECTOR_CLOUD":          "Director of Cloud Engineering",
        # ── Security ────────────────────────────────────────
        "SECURITY_ANALYST_INT":    "Security Analyst (Entry Level)",
        "JR_SECURITY_ANALYST":     "Junior Security Analyst",
        "SECURITY_ANALYST":        "Security Analyst",
        "SECURITY_ENGINEER":       "Security Engineer",
        "SENIOR_SECURITY_ENG":     "Senior Security Engineer",
        "STAFF_SECURITY_ENG":      "Staff Security Engineer",
        "LEAD_SECURITY_ENG":       "Lead Security Engineer",
        "SECURITY_ARCHITECT":      "Security Architect",
        "PRINCIPAL_SECURITY_ARCHITECT": "Principal Security Architect",
        "DIRECTOR_SECURITY":       "Director of Security",
        "CISO":                    "Chief Information Security Officer",
        # ── QA / Testing ────────────────────────────────────
        "JR_QA_ENG":               "QA Engineer (Entry Level)",
        "QA_ENGINEER":             "QA Engineer",
        "SENIOR_QA_ENG":           "Senior QA Engineer",
        "LEAD_QA_ENG":             "Lead QA Engineer",
        "QA_AUTOMATION_ENG":       "QA Automation Engineer",
        "SENIOR_QA_AUTOMATION":    "Senior QA Automation Engineer",
        "QA_ARCHITECT":            "QA Architect",
        "DIRECTOR_QA":             "Director of QA",
        # ── Mobile Engineering ──────────────────────────────
        "JR_MOBILE_DEV":           "Junior Mobile Developer",
        "MOBILE_DEV":              "Mobile Developer",
        "SENIOR_MOBILE_DEV":       "Senior Mobile Developer",
        "STAFF_MOBILE_DEV":        "Staff Mobile Developer",
        "LEAD_MOBILE_DEV":         "Lead Mobile Developer",
        "MOBILE_ARCHITECT":        "Mobile Architect",
        "DIRECTOR_MOBILE":         "Director of Mobile Engineering",
        # ── UI/UX Design ────────────────────────────────────
        "JR_UI_UX_DESIGNER":       "UI/UX Designer (Entry Level)",
        "UI_UX_DESIGNER":          "UI/UX Designer",
        "SENIOR_UI_UX_DESIGNER":   "Senior UI/UX Designer",
        "LEAD_UI_UX_DESIGNER":     "Lead UI/UX Designer",
        "PRINCIPAL_DESIGNER":      "Principal Designer",
        "DESIGN_MANAGER":          "Design Manager",
        "DIRECTOR_DESIGN":         "Director of Design",
        "HEAD_OF_DESIGN":          "Head of Design",
        # ── Product Management ──────────────────────────────
        "ASSOCIATE_PM":            "Associate Product Manager",
        "PRODUCT_MANAGER":         "Product Manager",
        "SENIOR_PM":               "Senior Product Manager",
        "LEAD_PM":                 "Lead Product Manager",
        "PRINCIPAL_PM":            "Principal Product Manager",
        "GROUP_PM":                "Group Product Manager",
        "DIRECTOR_PRODUCT":        "Director of Product",
        "VP_PRODUCT":              "VP of Product",
        "CPO":                     "Chief Product Officer",
        # ── Business Analysis ───────────────────────────────
        "JR_BUSINESS_ANALYST":     "Business Analyst (Entry Level)",
        "BUSINESS_ANALYST":        "Business Analyst",
        "SENIOR_BA":               "Senior Business Analyst",
        "LEAD_BA":                 "Lead Business Analyst",
        "PRINCIPAL_BA":            "Principal Business Analyst",
        "BUSINESS_ARCHITECT":      "Business Architect",
        "DIRECTOR_BUSINESS_ANALYSIS": "Director of Business Analysis",
        # ── Project / Program Management ────────────────────
        "JR_PROJECT_MANAGER":      "Junior Project Manager",
        "PROJECT_MANAGER":         "Project Manager",
        "SENIOR_PROJECT_MANAGER":  "Senior Project Manager",
        "PROGRAM_MANAGER":         "Program Manager",
        "SENIOR_PROGRAM_MANAGER":  "Senior Program Manager",
        "DIRECTOR_PMO":            "Director of PMO",
        "VP_PROJECT_MANAGEMENT":   "VP of Project Management",
        # ── Technical Writing ───────────────────────────────
        "JR_TECH_WRITER":          "Junior Technical Writer",
        "TECH_WRITER":             "Technical Writer",
        "SENIOR_TECH_WRITER":      "Senior Technical Writer",
        "LEAD_TECH_WRITER":        "Lead Technical Writer",
        "DOCUMENTATION_MANAGER":   "Documentation Manager",
        "DIRECTOR_DOCUMENTATION":  "Director of Documentation",
        # ── Blockchain / Web3 ───────────────────────────────
        "BLOCKCHAIN_DEV_INT":      "Blockchain Developer (Entry Level)",
        "BLOCKCHAIN_DEVELOPER":    "Blockchain Developer",
        "SENIOR_BLOCKCHAIN_DEV":   "Senior Blockchain Developer",
        "BLOCKCHAIN_ARCHITECT":    "Blockchain Architect",
        "WEB3_ENGINEER":           "Web3 Engineer",
        "LEAD_BLOCKCHAIN":         "Lead Blockchain Engineer",
        "DIRECTOR_BLOCKCHAIN":     "Director of Blockchain",
        # ── Game Development ────────────────────────────────
        "JR_GAME_DEV":             "Junior Game Developer",
        "GAME_DEVELOPER":          "Game Developer",
        "SENIOR_GAME_DEV":         "Senior Game Developer",
        "LEAD_GAME_DEV":           "Lead Game Developer",
        "GAME_DESIGNER":           "Game Designer",
        "TECHNICAL_GAME_DESIGNER": "Technical Game Designer",
        "GAME_ARCHITECT":          "Game Architect",
        "GAME_DIRECTOR":           "Game Director",
        # ── Embedded Systems ────────────────────────────────
        "EMBEDDED_ENG_INT":        "Embedded Engineer (Entry Level)",
        "EMBEDDED_ENGINEER":       "Embedded Engineer",
        "SENIOR_EMBEDDED_ENG":     "Senior Embedded Engineer",
        "STAFF_EMBEDDED_ENG":      "Staff Embedded Engineer",
        "EMBEDDED_ARCHITECT":      "Embedded Architect",
        "FIRMWARE_ENGINEER":       "Firmware Engineer",
        "DIRECTOR_EMBEDDED":       "Director of Embedded Systems",
        # ── Orphan roles from existing data ─────────────────
        "JR_SYS_ADMIN":            "Junior System Administrator",
        "JR_IT_SUPPORT":           "Junior IT Support",
    }
    return _TITLE_MAP.get(role_id, role_id.replace("_", " ").title())


# ── Experience ranges per seniority ──────────────────────────────────────────
_EXP_RANGES: dict[int, str] = {
    1: "0-1 years",
    2: "0-2 years",
    3: "2-4 years",
    4: "4-7 years",
    5: "6-9 years",
    6: "7-12 years",
    7: "10-15 years",
    8: "10-18 years",
    9: "15+ years",
}

# ── Progression months (avg months to next level) ───────────────────────────
_PROGRESSION_MONTHS: dict[int, int] = {
    1: 12,    # intern → junior
    2: 18,    # junior → mid
    3: 24,    # mid → senior
    4: 30,    # senior → staff
    5: 36,    # staff → lead/principal
    6: 36,    # lead → architect/mgr
    7: 48,    # architect → director
    8: 48,    # director → VP
    9: 0,     # executive (terminal)
}

# ── Salary ranges (LKR per year — Sri Lanka market) ─────────────────────────
_SALARY_LKR: dict[int, tuple[int, int]] = {
    1: (300_000,    600_000),
    2: (480_000,  1_200_000),
    3: (900_000,  2_400_000),
    4: (1_500_000, 3_600_000),
    5: (2_400_000, 5_400_000),
    6: (3_000_000, 7_200_000),
    7: (4_200_000, 9_600_000),
    8: (5_400_000, 14_400_000),
    9: (9_600_000, 30_000_000),
}

# ── Common industries per domain ────────────────────────────────────────────
_DOMAIN_INDUSTRIES: dict[str, list[str]] = {
    "SOFTWARE_ENGINEERING":  ["enterprise", "fintech", "healthtech", "saas", "e-commerce"],
    "FRONTEND_ENGINEERING":  ["e-commerce", "saas", "media", "adtech", "fintech"],
    "BACKEND_ENGINEERING":   ["fintech", "enterprise", "cloud_services", "saas", "healthtech"],
    "FULLSTACK_ENGINEERING": ["startups", "saas", "e-commerce", "consulting", "fintech"],
    "DATA_ENGINEERING":      ["fintech", "banking", "telecom", "insurance", "e-commerce"],
    "DATA_SCIENCE":          ["banking", "insurance", "healthtech", "telecom", "retail"],
    "AI_ML":                 ["fintech", "healthtech", "autonomous_systems", "adtech", "research"],
    "DEVOPS_SRE":            ["cloud_services", "fintech", "enterprise", "telecom", "saas"],
    "CLOUD_ENGINEERING":     ["cloud_services", "enterprise", "fintech", "telecom", "saas"],
    "SECURITY":              ["banking", "government", "defense", "fintech", "enterprise"],
    "QA_TESTING":            ["enterprise", "fintech", "gaming", "e-commerce", "saas"],
    "MOBILE_ENGINEERING":    ["e-commerce", "fintech", "media", "healthtech", "transport"],
    "UI_UX_DESIGN":          ["e-commerce", "media", "saas", "fintech", "healthtech"],
    "PRODUCT_MANAGEMENT":    ["saas", "e-commerce", "fintech", "media", "enterprise"],
    "BUSINESS_ANALYSIS":     ["banking", "insurance", "enterprise", "consulting", "telecom"],
    "PROJECT_MANAGEMENT":    ["enterprise", "consulting", "government", "banking", "telecom"],
    "TECHNICAL_WRITING":     ["saas", "enterprise", "cloud_services", "open_source", "developer_tools"],
    "BLOCKCHAIN_WEB3":       ["defi", "nft", "cryptocurrency", "supply_chain", "fintech"],
    "GAME_DEVELOPMENT":      ["gaming", "vr_ar", "simulation", "education", "entertainment"],
    "EMBEDDED_SYSTEMS":      ["automotive", "iot", "consumer_electronics", "industrial", "aerospace"],
}

# ── Certifications per domain ───────────────────────────────────────────────
_DOMAIN_CERTS_REQUIRED: dict[str, list[str]] = {
    "SECURITY": ["CompTIA Security+"],
    "CLOUD_ENGINEERING": [],
    "DEVOPS_SRE": [],
}
_DOMAIN_CERTS_NICE: dict[str, list[str]] = {
    "SOFTWARE_ENGINEERING":  ["AWS Solutions Architect", "Kubernetes CKA"],
    "FRONTEND_ENGINEERING":  ["Meta Front-End Developer", "AWS Cloud Practitioner"],
    "BACKEND_ENGINEERING":   ["AWS Solutions Architect", "Oracle Certified Java"],
    "FULLSTACK_ENGINEERING": ["AWS Solutions Architect", "MongoDB Developer"],
    "DATA_ENGINEERING":      ["Google Data Engineer", "Databricks Data Engineer", "AWS Data Analytics"],
    "DATA_SCIENCE":          ["IBM Data Science", "Google Data Analytics", "Coursera ML Specialization"],
    "AI_ML":                 ["TensorFlow Developer Certificate", "AWS ML Specialty", "Databricks ML Professional"],
    "DEVOPS_SRE":            ["Kubernetes CKA", "AWS DevOps Engineer", "HashiCorp Terraform Associate"],
    "CLOUD_ENGINEERING":     ["AWS Solutions Architect", "Azure Solutions Architect", "GCP Cloud Engineer"],
    "SECURITY":              ["CISSP", "CEH", "CompTIA Security+", "OSCP"],
    "QA_TESTING":            ["ISTQB Foundation", "Selenium Certification", "Cypress Certification"],
    "MOBILE_ENGINEERING":    ["Google Android Developer", "Apple Swift Certification"],
    "UI_UX_DESIGN":          ["Google UX Design Certificate", "Nielsen Norman UX"],
    "PRODUCT_MANAGEMENT":    ["CSPO", "Pragmatic Marketing", "AIPMM"],
    "BUSINESS_ANALYSIS":     ["CBAP", "CCBA", "PMI-PBA"],
    "PROJECT_MANAGEMENT":    ["PMP", "PRINCE2", "CSM"],
    "TECHNICAL_WRITING":     ["Society for Technical Communication (STC)"],
    "BLOCKCHAIN_WEB3":       ["Certified Blockchain Developer", "Ethereum Developer"],
    "GAME_DEVELOPMENT":      ["Unity Certified Developer", "Unreal Authorized Instructor"],
    "EMBEDDED_SYSTEMS":      ["ARM Accredited Engineer", "Certified LabVIEW Developer"],
}


# ═════════════════════════════════════════════════════════════════════════════
#  4. BACKWARDS-COMPATIBILITY MAPPING  (old domain → new domain)
# ═════════════════════════════════════════════════════════════════════════════

OLD_TO_NEW_DOMAIN: dict[str, str] = {
    "SOFTWARE_ENGINEERING": "SOFTWARE_ENGINEERING",
    "DATA":                "DATA_ENGINEERING",
    "AI_ML":               "AI_ML",
    "DEVOPS":              "DEVOPS_SRE",
    "QA":                  "QA_TESTING",
    "MOBILE":              "MOBILE_ENGINEERING",
    "UI_UX":               "UI_UX_DESIGN",
}

# Extra existing roles that need domain placement
_EXTRA_ROLE_DOMAINS: dict[str, str] = {
    "JR_SYS_ADMIN":    "DEVOPS_SRE",
    "JR_IT_SUPPORT":   "SOFTWARE_ENGINEERING",     # general IT catch-all
    "JR_BE_DEV":       "BACKEND_ENGINEERING",       # was under SOFTWARE_ENGINEERING
}


# ═════════════════════════════════════════════════════════════════════════════
#  5. BUILD FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def build_ladders() -> dict:
    """Build the career_ladders_v2 structure."""
    return dict(CAREER_LADDERS_V2)


def build_role_metadata() -> list[dict]:
    """Build extended metadata for every role across all domains."""
    metadata: list[dict] = []
    seen_roles: set[str] = set()

    for domain, roles in CAREER_LADDERS_V2.items():
        for idx, role_id in enumerate(roles):
            if role_id in seen_roles:
                # Role appears in multiple domains — skip duplicate
                continue
            seen_roles.add(role_id)

            level, seniority = _assign_seniority(role_id)
            sal_min, sal_max = _SALARY_LKR.get(level, (0, 0))

            # Next role in this ladder (if any)
            next_role = roles[idx + 1] if idx + 1 < len(roles) else None

            metadata.append({
                "role_id":                          role_id,
                "role_title":                       _nice_title(role_id),
                "domain":                           domain,
                "ladder_position":                  idx + 1,
                "ladder_length":                    len(roles),
                "seniority_level":                  level,
                "seniority_label":                  seniority,
                "typical_experience_years":         _EXP_RANGES.get(level, "varies"),
                "avg_progression_months_to_next":   _PROGRESSION_MONTHS.get(level, 0),
                "next_role_in_ladder":              next_role,
                "typical_salary_lkr_min":           sal_min,
                "typical_salary_lkr_max":           sal_max,
                "common_industries":                _DOMAIN_INDUSTRIES.get(domain, []),
                "required_certifications":          _DOMAIN_CERTS_REQUIRED.get(domain, []),
                "nice_to_have_certifications":      _DOMAIN_CERTS_NICE.get(domain, []),
            })

    # Add orphan roles not in any ladder but existing in job data
    for role_id, domain in _EXTRA_ROLE_DOMAINS.items():
        if role_id not in seen_roles:
            level, seniority = _assign_seniority(role_id)
            sal_min, sal_max = _SALARY_LKR.get(level, (0, 0))
            metadata.append({
                "role_id":                          role_id,
                "role_title":                       _nice_title(role_id),
                "domain":                           domain,
                "ladder_position":                  0,
                "ladder_length":                    0,
                "seniority_level":                  level,
                "seniority_label":                  seniority,
                "typical_experience_years":         _EXP_RANGES.get(level, "varies"),
                "avg_progression_months_to_next":   _PROGRESSION_MONTHS.get(level, 0),
                "next_role_in_ladder":              None,
                "typical_salary_lkr_min":           sal_min,
                "typical_salary_lkr_max":           sal_max,
                "common_industries":                _DOMAIN_INDUSTRIES.get(domain, []),
                "required_certifications":          _DOMAIN_CERTS_REQUIRED.get(domain, []),
                "nice_to_have_certifications":      _DOMAIN_CERTS_NICE.get(domain, []),
            })
            seen_roles.add(role_id)

    return metadata


# ═════════════════════════════════════════════════════════════════════════════
#  6. VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

def validate(
    ladders: dict,
    metadata: list[dict],
    existing_roles: set[str] | None = None,
) -> list[str]:
    """Run validation checks, return list of issues."""
    issues: list[str] = []

    # 1. Count domains and roles
    all_roles = set()
    for domain, roles in ladders.items():
        all_roles.update(roles)
    n_domains = len(ladders)
    n_roles = len(all_roles)
    log.info("Ladders: %d domains, %d unique roles", n_domains, n_roles)

    if n_domains < 20:
        issues.append(f"Only {n_domains} domains (expected ≥20)")
    else:
        log.info("✓ %d domains (≥20)", n_domains)

    if n_roles < 150:
        issues.append(f"Only {n_roles} unique roles (expected ≥150)")
    else:
        log.info("✓ %d unique roles (≥150)", n_roles)

    # 2. All metadata roles accounted for
    meta_roles = {m["role_id"] for m in metadata}
    missing_meta = all_roles - meta_roles
    if missing_meta:
        issues.append(f"Roles in ladders but not in metadata: {missing_meta}")
    else:
        log.info("✓ All ladder roles have metadata (%d entries)", len(metadata))

    # 3. Check existing job-data roles are present
    if existing_roles:
        missing_existing = existing_roles - meta_roles
        if missing_existing:
            issues.append(f"Existing job-data roles missing from metadata: {missing_existing}")
        else:
            log.info("✓ All %d existing data-backed roles preserved", len(existing_roles))

    # 4. No duplicate role IDs across ladders (warn if shared)
    seen: dict[str, list[str]] = {}
    for domain, roles in ladders.items():
        for r in roles:
            seen.setdefault(r, []).append(domain)
    shared = {r: doms for r, doms in seen.items() if len(doms) > 1}
    if shared:
        log.warning("Roles in multiple domains (shared): %s", shared)
    else:
        log.info("✓ No duplicate roles across domains")

    # 5. Each ladder is ordered (position increases)
    for domain, roles in ladders.items():
        levels = [_assign_seniority(r)[0] for r in roles]
        for i in range(1, len(levels)):
            if levels[i] < levels[i - 1]:
                issues.append(
                    f"Non-monotonic seniority in {domain}: "
                    f"{roles[i-1]}(L{levels[i-1]}) → {roles[i]}(L{levels[i]})"
                )
    if not any("Non-monotonic" in i for i in issues):
        log.info("✓ All ladders have non-decreasing seniority order")

    # 6. Salary ranges are positive and min < max
    for m in metadata:
        if m["typical_salary_lkr_min"] > m["typical_salary_lkr_max"]:
            issues.append(f"Salary min > max for {m['role_id']}")
    if not any("Salary" in i for i in issues):
        log.info("✓ All salary ranges valid (min ≤ max)")

    # 7. Old ladders backward-compatible
    if existing_roles:
        try:
            with open(OLD_LADDERS, "r") as f:
                old = json.load(f)
            old_roles: set[str] = set()
            for roles in old.values():
                old_roles.update(roles)
            missing_old = old_roles - meta_roles
            if missing_old:
                issues.append(f"Original ladder roles missing: {missing_old}")
            else:
                log.info("✓ All original career_ladders.json roles preserved")
        except FileNotFoundError:
            log.warning("Original career_ladders.json not found — skipping backward-compat check")

    return issues


# ═════════════════════════════════════════════════════════════════════════════
#  7. ANALYTICS REPORT
# ═════════════════════════════════════════════════════════════════════════════

def generate_report(
    ladders: dict,
    metadata: list[dict],
    existing_roles: set[str] | None = None,
) -> str:
    lines: list[str] = []
    sep = "=" * 78

    lines.append(sep)
    lines.append("  EXPANDED CAREER LADDERS v2 — REPORT")
    lines.append(sep)
    lines.append("")

    # 1. Summary
    all_roles = set()
    for roles in ladders.values():
        all_roles.update(roles)

    lines.append("─── 1. SUMMARY ──────────────────────────────────────────────")
    lines.append(f"  Domains:             {len(ladders)}")
    lines.append(f"  Unique roles:        {len(all_roles)}")
    lines.append(f"  Metadata entries:    {len(metadata)}")
    if existing_roles:
        data_backed = all_roles & existing_roles
        lines.append(f"  Data-backed roles:   {len(data_backed)} / {len(existing_roles)} existing")
    lines.append("")

    # 2. Domain breakdown
    lines.append("─── 2. DOMAIN BREAKDOWN ─────────────────────────────────────")
    lines.append(f"  {'#':<3} {'Domain':<28} {'Roles':>6}  Ladder")
    lines.append(f"  {'─'*3} {'─'*28} {'─'*6}  {'─'*50}")
    for i, (domain, roles) in enumerate(ladders.items(), 1):
        short = " → ".join(roles[:3]) + (" → …" if len(roles) > 3 else "")
        lines.append(f"  {i:<3} {domain:<28} {len(roles):>6}  {short}")
    lines.append("")

    # 3. Seniority distribution
    lines.append("─── 3. SENIORITY DISTRIBUTION ───────────────────────────────")
    from collections import Counter
    sen_counts = Counter(m["seniority_label"] for m in metadata)
    for label in ["intern", "junior", "mid", "senior", "staff", "lead", "architect", "management", "executive"]:
        cnt = sen_counts.get(label, 0)
        pct = cnt / len(metadata) * 100
        lines.append(f"  {label:<14} {cnt:>5}  ({pct:>5.1f}%)")
    lines.append("")

    # 4. Salary ranges overview
    lines.append("─── 4. SALARY RANGES (LKR/year) ─────────────────────────────")
    lines.append(f"  {'Level':<14} {'Min':>14} {'Max':>14}")
    lines.append(f"  {'─'*14} {'─'*14} {'─'*14}")
    for lvl in sorted(_SALARY_LKR.keys()):
        smin, smax = _SALARY_LKR[lvl]
        # Find the label for this level
        lbl = {1:"intern",2:"junior",3:"mid",4:"senior",5:"staff",
               6:"lead",7:"architect",8:"management",9:"executive"}.get(lvl, "?")
        lines.append(f"  {lbl:<14} {smin:>14,} {smax:>14,}")
    lines.append("")

    # 5. Data-backed roles detail
    if existing_roles:
        lines.append("─── 5. EXISTING DATA-BACKED ROLES ───────────────────────────")
        for m in sorted(metadata, key=lambda x: x["role_id"]):
            if m["role_id"] in existing_roles:
                lines.append(
                    f"  {m['role_id']:<24} → {m['domain']:<25} "
                    f"L{m['seniority_level']} ({m['seniority_label']})"
                )
        lines.append("")

    # 6. Backward compatibility map
    lines.append("─── 6. DOMAIN MIGRATION MAP (old → new) ─────────────────────")
    for old_d, new_d in OLD_TO_NEW_DOMAIN.items():
        lines.append(f"  {old_d:<25} → {new_d}")
    lines.append("")

    # 7. Certifications overview
    lines.append("─── 7. CERTIFICATIONS PER DOMAIN (nice-to-have) ─────────────")
    for domain, certs in sorted(_DOMAIN_CERTS_NICE.items()):
        cert_str = ", ".join(certs[:3]) + ("…" if len(certs) > 3 else "")
        lines.append(f"  {domain:<28} → {cert_str}")
    lines.append("")

    lines.append(sep)
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  8. MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Expand career ladders to v2")
    parser.add_argument("--validate-only", action="store_true",
                        help="Only validate existing output files")
    args = parser.parse_args()

    t_start = time.perf_counter()

    # ── Load existing role set from profiles (if available) ───────────────
    existing_roles: set[str] | None = None
    if PROFILES_PATH.exists():
        try:
            import pandas as pd
            rp = pd.read_csv(PROFILES_PATH, usecols=["role_id"])
            existing_roles = set(rp["role_id"].unique())
            log.info("Loaded %d existing data-backed roles from profiles", len(existing_roles))
        except Exception as e:
            log.warning("Could not load profiles: %s", e)

    if args.validate_only:
        log.info("Validate-only mode")
        if OUT_LADDERS.exists() and OUT_METADATA.exists():
            with open(OUT_LADDERS) as f:
                ladders = json.load(f)
            with open(OUT_METADATA) as f:
                metadata = json.load(f)
            issues = validate(ladders, metadata, existing_roles)
            if issues:
                for i in issues:
                    log.error("FAIL: %s", i)
            else:
                log.info("All checks passed ✓")
        else:
            log.error("Output files not found. Run without --validate-only first.")
        return

    # ── Build ─────────────────────────────────────────────────────────────
    log.info("Building expanded career ladders v2 …")
    ladders = build_ladders()
    metadata = build_role_metadata()

    all_roles = set()
    for roles in ladders.values():
        all_roles.update(roles)
    log.info("  → %d domains, %d unique roles, %d metadata entries",
             len(ladders), len(all_roles), len(metadata))

    # ── Validate ──────────────────────────────────────────────────────────
    log.info("Running validation …")
    issues = validate(ladders, metadata, existing_roles)
    if issues:
        for i in issues:
            log.error("VALIDATION FAIL: %s", i)
    else:
        log.info("All validation checks PASSED ✓")

    # ── Save ladders JSON ─────────────────────────────────────────────────
    OUT_LADDERS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_LADDERS, "w", encoding="utf-8") as f:
        json.dump(ladders, f, indent=2, ensure_ascii=False)
    log.info("Saved ladders → %s", OUT_LADDERS)

    # ── Save metadata JSON ────────────────────────────────────────────────
    OUT_METADATA.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    log.info("Saved metadata → %s  (%d roles)", OUT_METADATA, len(metadata))

    # ── Report ────────────────────────────────────────────────────────────
    report = generate_report(ladders, metadata, existing_roles)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(report, encoding="utf-8")
    log.info("Report → %s", OUT_REPORT)

    # ── Console summary ──────────────────────────────────────────────────
    elapsed = time.perf_counter() - t_start
    print()
    print("=" * 78)
    print(textwrap.dedent(f"""\
        COMPLETE — Career Ladders v2
          Domains:         {len(ladders)}
          Unique roles:    {len(all_roles)}
          Metadata entries:{len(metadata)}
          Elapsed:         {elapsed:.1f}s
          Ladders:         {OUT_LADDERS}
          Metadata:        {OUT_METADATA}
          Report:          {OUT_REPORT}
    """))
    print("=" * 78)
    print(report)


if __name__ == "__main__":
    main()
