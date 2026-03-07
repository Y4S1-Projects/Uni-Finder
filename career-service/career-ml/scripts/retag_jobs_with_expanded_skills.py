#!/usr/bin/env python3
"""
retag_jobs_with_expanded_skills.py
===================================
Re-tag ALL jobs (original 5,470 + new scraped) with the expanded 1,200
skills using intelligent multi-pass matching.

Six-pass matching with confidence scoring:
  Pass 1  Exact match            conf 1.0
  Pass 2  Alias match            conf 0.9
  Pass 3  Context-aware NLP      conf 0.7
  Pass 4  Skill co-occurrence    conf 0.4
  Pass 5  Implicit skills        conf 0.5
  Pass 6  Technology stack infer  conf 0.5

Inputs:
  data/processed/jobs_cleaned.csv   (all jobs)
  -- OR fallback: data/processed/jobs_labeled.csv
  data/expanded/skills_v2.csv       (1,200 skills)
  career_path/career_ladders.json   (role definitions)

Outputs:
  data/processed/jobs_tagged_v2.csv
  data/reports/skill_tagging_report.txt
  data/reports/skill_cooccurrence_top100.csv

Prerequisites:
    pip install pandas tqdm spacy rapidfuzz
    python -m spacy download en_core_web_sm        # or en_core_web_lg

Run:
    cd career-ml
    python scripts/retag_jobs_with_expanded_skills.py [--workers 4]
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

# ── Optional deps ────────────────────────────────────────────────────
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPANDED_DIR  = BASE_DIR / "data" / "expanded"
REPORTS_DIR   = BASE_DIR / "data" / "reports"
CAREER_DIR    = BASE_DIR / "career_path"

SKILLS_CSV    = EXPANDED_DIR / "skills_v2.csv"
LADDERS_JSON  = CAREER_DIR  / "career_ladders.json"
OUTPUT_CSV    = PROCESSED_DIR / "jobs_tagged_v2.csv"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Input: prefer jobs_cleaned.csv, fall back to jobs_labeled.csv
_FALLBACK_INPUTS = [
    PROCESSED_DIR / "jobs_cleaned.csv",
    PROCESSED_DIR / "jobs_unified.csv",
    PROCESSED_DIR / "jobs_labeled.csv",
]

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("retag")


# ══════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Skill:
    skill_id:  str
    name:      str
    aliases:   list[str]
    category:  str
    stype:     str          # technical / soft / credential

    # Pre-compiled regex for matching (built once)
    _patterns: list[re.Pattern] = field(default_factory=list, repr=False)

    def compile_patterns(self) -> None:
        """Build word-boundary regex for name + each alias."""
        terms = [self.name] + self.aliases
        self._patterns = []
        for t in terms:
            t = t.strip()
            if not t:
                continue
            # Escape regex-special chars in the term
            escaped = re.escape(t)
            # Word boundaries, case-insensitive
            try:
                pat = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                self._patterns.append(pat)
            except re.error:
                pass  # skip malformed

    def search(self, text: str) -> Optional[str]:
        """Return the matched term string, or None."""
        for pat in self._patterns:
            if pat.search(text):
                return pat.pattern  # the term used
        return None


@dataclass
class SkillMatch:
    skill_id:   str
    confidence: float
    source:     str          # "exact", "alias", "context", "cooccurrence", "implicit", "stack"


# ══════════════════════════════════════════════════════════════════════
#  SKILL INDEX
# ══════════════════════════════════════════════════════════════════════

class SkillIndex:
    """Pre-processed in-memory skill lookup optimised for speed.

    Builds two fast-lookup structures:
      • `_term_to_sids` : lowered_term → [(skill_id, is_name_not_alias), …]
      • `_precompiled`  : lowered_term → compiled re.Pattern(\bterm\b)

    Pass 1 & 2 use a SINGLE scan through all terms with a fast `in`
    pre-filter before falling back to the regex boundary check, making
    the overall complexity much closer to O(T × avg_match_terms) instead
    of O(T × total_skills) per job.
    """

    # Short / ambiguous terms that produce excessive false positives
    _SKIP_TERMS: set[str] = {
        "c", "r", "go", "it", "ai", "bi", "qa", "os", "e",
        "coffee", "office", "key", "mat", "sol", "ml", "ex",
        "hs", "kt", "pm", "sa", "se", "ds", "de", "ux", "ui",
    }

    def __init__(self, skills_df: pd.DataFrame) -> None:
        self.skills: dict[str, Skill] = {}
        self.name_to_id: dict[str, str] = {}
        self.alias_to_id: dict[str, str] = {}
        self.category_skills: dict[str, list[str]] = defaultdict(list)

        # Fast-match indexes
        self._term_to_sids: dict[str, list[tuple[str, bool]]] = defaultdict(list)
        self._precompiled: dict[str, re.Pattern] = {}

        for _, row in skills_df.iterrows():
            sid  = str(row["skill_id"]).strip()
            name = str(row["name"]).strip()
            raw_aliases = str(row.get("aliases", ""))
            aliases = [a.strip() for a in raw_aliases.split(",")
                       if a.strip() and a.strip().lower() != name.lower()]
            cat  = str(row.get("category", "other"))
            st   = str(row.get("type", "technical"))

            sk = Skill(skill_id=sid, name=name, aliases=aliases,
                       category=cat, stype=st)
            sk.compile_patterns()
            self.skills[sid] = sk
            self.name_to_id[name.lower()] = sid
            for a in aliases:
                self.alias_to_id[a.lower()] = sid
            self.category_skills[cat].append(sid)

            # Register terms for fast scan
            name_lower = name.lower()
            if len(name_lower) >= 3 and name_lower not in self._SKIP_TERMS:
                self._term_to_sids[name_lower].append((sid, True))
                self._ensure_compiled(name_lower)
            for a in aliases:
                al = a.lower()
                if len(al) >= 3 and al not in self._SKIP_TERMS:
                    self._term_to_sids[al].append((sid, False))
                    self._ensure_compiled(al)

        log.info("SkillIndex built: %d skills, %d aliases, %d unique terms",
                 len(self.skills), len(self.alias_to_id), len(self._term_to_sids))

    # ── helpers ──

    def _ensure_compiled(self, term: str) -> None:
        if term not in self._precompiled:
            try:
                self._precompiled[term] = re.compile(
                    rf"\b{re.escape(term)}\b", re.IGNORECASE)
            except re.error:
                pass

    def get_skill(self, sid: str) -> Optional[Skill]:
        return self.skills.get(sid)

    def fast_scan(self, text: str) -> list[tuple[str, float, str]]:
        """Return [(skill_id, confidence, source), …] for all terms
        found in *text* using fast `in` pre-filter + regex verify.

        Confidence: 1.0 for name match, 0.9 for alias match.
        """
        hits: list[tuple[str, float, str]] = []
        text_lower = text.lower()
        seen: set[str] = set()
        for term, entries in self._term_to_sids.items():
            if term not in text_lower:
                continue  # fast rejection
            pat = self._precompiled.get(term)
            if pat is None or not pat.search(text_lower):
                continue  # whole-word check
            for sid, is_name in entries:
                if sid in seen:
                    continue
                seen.add(sid)
                hits.append((sid, 1.0 if is_name else 0.9,
                             "exact" if is_name else "alias"))
        return hits


# ══════════════════════════════════════════════════════════════════════
#  CO-OCCURRENCE RULES  (Pass 4)
# ══════════════════════════════════════════════════════════════════════
# If skill A matched → also infer skill B
# Format: { trigger_skill_name_lower : [ implied_skill_name_lower, … ] }

COOCCURRENCE_RULES: dict[str, list[str]] = {
    "react":          ["javascript", "html", "css"],
    "angular":        ["javascript", "typescript", "html", "css"],
    "vue.js":         ["javascript", "html", "css"],
    "next.js":        ["react", "javascript", "typescript"],
    "nuxt.js":        ["vue.js", "javascript"],
    "svelte":         ["javascript", "html", "css"],
    "django":         ["python", "rest"],
    "flask":          ["python", "rest"],
    "fastapi":        ["python", "rest"],
    "spring":         ["java"],
    "spring boot":    ["java", "rest", "spring"],
    "express":        ["javascript", "node.js", "rest"],
    "nest.js":        ["typescript", "node.js", "rest"],
    "ruby on rails":  ["ruby"],
    "laravel":        ["php"],
    "asp.net":        ["c#", ".net"],
    "machine learning": ["python", "statistics"],
    "deep learning":  ["python", "machine learning", "tensorflow"],
    "tensorflow":     ["python", "deep learning"],
    "pytorch":        ["python", "deep learning"],
    "scikit-learn":   ["python", "machine learning", "statistics"],
    "pandas":         ["python", "data"],
    "numpy":          ["python"],
    "kubernetes":     ["docker", "containerization"],
    "docker":         ["containerization", "linux"],
    "terraform":      ["infrastructure as code", "cloud"],
    "ansible":        ["infrastructure as code", "automation"],
    "jenkins":        ["ci/cd", "automation"],
    "github actions": ["ci/cd", "git"],
    "aws lambda":     ["aws", "serverless"],
    "azure functions": ["azure", "serverless"],
    "react native":   ["react", "javascript", "mobile"],
    "flutter":        ["dart", "mobile"],
    "swift":          ["ios", "mobile"],
    "kotlin":         ["android", "mobile"],
    "graphql":        ["api", "rest"],
    "mongodb":        ["nosql", "database"],
    "postgresql":     ["sql", "database"],
    "mysql":          ["sql", "database"],
    "redis":          ["caching", "database"],
    "elasticsearch":  ["search", "database"],
    "kafka":          ["streaming", "event-driven"],
    "rabbitmq":       ["messaging", "event-driven"],
    "typescript":     ["javascript"],
}


# ══════════════════════════════════════════════════════════════════════
#  TECHNOLOGY STACK INFERENCE  (Pass 6)
# ══════════════════════════════════════════════════════════════════════
# Mention of a specific technology → infer underlying skills

STACK_INFERENCE: dict[str, list[str]] = {
    "aws lambda":     ["python", "aws", "serverless"],
    "aws ec2":        ["aws", "linux", "cloud"],
    "aws s3":         ["aws", "cloud"],
    "aws sagemaker":  ["aws", "machine learning", "python"],
    "aws ecs":        ["aws", "docker", "containerization"],
    "aws eks":        ["aws", "kubernetes", "docker"],
    "azure devops":   ["azure", "ci/cd", "git"],
    "azure ml":       ["azure", "machine learning", "python"],
    "gcp bigquery":   ["gcp", "sql", "data"],
    "google cloud":   ["gcp", "cloud"],
    "react":          ["javascript", "html", "css"],
    "react native":   ["javascript", "mobile", "react"],
    "angular":        ["typescript", "javascript", "html", "css"],
    "vue.js":         ["javascript", "html", "css"],
    "django":         ["python", "rest"],
    "flask":          ["python", "rest"],
    "fastapi":        ["python", "rest"],
    "spring boot":    ["java", "rest", "spring"],
    "express.js":     ["javascript", "node.js", "rest"],
    ".net core":      ["c#", ".net", "rest"],
    "blazor":         ["c#", ".net", "html"],
    "hadoop":         ["java", "big data", "data"],
    "spark":          ["python", "big data", "data"],
    "airflow":        ["python", "data", "etl"],
    "dbt":            ["sql", "data", "analytics"],
    "tableau":        ["data", "analytics", "data visualization"],
    "power bi":       ["data", "analytics", "data visualization"],
    "figma":          ["ui/ux", "design"],
    "sketch":         ["ui/ux", "design"],
    "jira":           ["agile", "project"],
    "confluence":     ["documentation"],
    "selenium":       ["testing", "automation"],
    "cypress":        ["testing", "javascript"],
    "jest":           ["testing", "javascript"],
    "junit":          ["testing", "java"],
    "pytest":         ["testing", "python"],
}


# ══════════════════════════════════════════════════════════════════════
#  CONTEXT-AWARE PATTERNS  (Pass 3)
# ══════════════════════════════════════════════════════════════════════
# Contextual phrases → skill names they imply

CONTEXT_PATTERNS: list[tuple[re.Pattern, list[str]]] = [
    # Cloud / infra
    (re.compile(r"\b(?:cloud\s+(?:deployment|infrastructure|migration))\b", re.I),
     ["aws", "azure", "gcp", "cloud"]),
    (re.compile(r"\bcontaineriz(?:ation|ed?)\b", re.I),
     ["docker", "kubernetes"]),
    (re.compile(r"\borchestrat(?:ion|e)\b.*\bcontainer", re.I),
     ["kubernetes", "docker"]),
    (re.compile(r"\bserverless\s+(?:architecture|computing|framework)\b", re.I),
     ["aws lambda", "serverless", "cloud"]),
    (re.compile(r"\bmicroservices?\s+architecture\b", re.I),
     ["docker", "kubernetes", "rest", "api"]),
    (re.compile(r"\binfrastructure\s+as\s+code\b", re.I),
     ["terraform", "ansible", "infrastructure as code"]),
    (re.compile(r"\bcontinuous\s+(?:integration|delivery|deployment)\b", re.I),
     ["ci/cd", "jenkins", "git"]),
    (re.compile(r"\bCI\s*/?\s*CD\b", re.I),
     ["ci/cd", "jenkins", "git"]),

    # Data / AI
    (re.compile(r"\bdata\s+(?:pipeline|warehouse|lake|engineering)\b", re.I),
     ["etl", "sql", "data", "python"]),
    (re.compile(r"\b(?:natural\s+language\s+processing|NLP)\b", re.I),
     ["nlp", "python", "machine learning"]),
    (re.compile(r"\bcomputer\s+vision\b", re.I),
     ["deep learning", "python", "machine learning"]),
    (re.compile(r"\bpredictive\s+(?:modelling|analytics?)\b", re.I),
     ["machine learning", "statistics", "python"]),
    (re.compile(r"\bbig\s+data\b", re.I),
     ["big data", "hadoop", "spark", "data"]),
    (re.compile(r"\bETL\b", re.I),
     ["etl", "sql", "data"]),

    # Dev methodologies
    (re.compile(r"\btest[- ]driven\s+development\b", re.I),
     ["testing", "tdd"]),
    (re.compile(r"\bbehaviou?r[- ]driven\s+development\b", re.I),
     ["testing", "bdd"]),
    (re.compile(r"\bagile\s+(?:methodology|environment|team)\b", re.I),
     ["agile", "scrum"]),
    (re.compile(r"\bscrum\s+master\b", re.I),
     ["scrum", "agile", "project"]),
    (re.compile(r"\bdevops\s+(?:culture|practices?|pipeline)\b", re.I),
     ["devops", "ci/cd", "docker"]),

    # Web
    (re.compile(r"\bfull[- ]?stack\s+(?:developer|engineer|development)\b", re.I),
     ["javascript", "html", "css", "rest", "sql"]),
    (re.compile(r"\bfront[- ]?end\s+(?:developer|engineer|development)\b", re.I),
     ["javascript", "html", "css", "react"]),
    (re.compile(r"\bback[- ]?end\s+(?:developer|engineer|development)\b", re.I),
     ["rest", "sql", "api"]),
    (re.compile(r"\bsingle\s+page\s+application\b", re.I),
     ["javascript", "react", "html", "css"]),
    (re.compile(r"\bRESTful\s+(?:API|services?|web)\b", re.I),
     ["rest", "api"]),

    # Security
    (re.compile(r"\bpenetration\s+test(?:ing)?\b", re.I),
     ["security", "penetration testing"]),
    (re.compile(r"\bsecurity\s+audit(?:ing)?\b", re.I),
     ["security", "compliance"]),

    # Mobile
    (re.compile(r"\bcross[- ]?platform\s+(?:mobile|app|development)\b", re.I),
     ["mobile", "react native", "flutter"]),
    (re.compile(r"\bnative\s+(?:iOS|Android)\s+(?:development|app)\b", re.I),
     ["mobile", "swift", "kotlin"]),

    # Architecture
    (re.compile(r"\bsystem\s+design\b", re.I),
     ["system design", "architecture"]),
    (re.compile(r"\bdesign\s+patterns?\b", re.I),
     ["design patterns", "oop"]),
    (re.compile(r"\bevent[- ]?driven\s+(?:architecture|system)\b", re.I),
     ["kafka", "messaging", "event-driven"]),
]


# ══════════════════════════════════════════════════════════════════════
#  IMPLICIT SKILLS  (Pass 5)
# ══════════════════════════════════════════════════════════════════════

# Seniority keywords → implied soft skills
SENIORITY_IMPLICIT: dict[str, list[str]] = {
    "senior":    ["mentoring", "code review", "leadership", "technical requirements"],
    "lead":      ["leadership", "mentoring", "people management", "project", "code review"],
    "principal": ["leadership", "mentoring", "architecture", "system design", "strategy"],
    "director":  ["leadership", "strategy", "people management", "stakeholder management"],
    "manager":   ["leadership", "people management", "project", "stakeholder management"],
    "staff":     ["leadership", "mentoring", "architecture", "system design"],
    "architect": ["system design", "architecture", "leadership", "technical requirements"],
    "head":      ["leadership", "strategy", "people management"],
    "vp":        ["leadership", "strategy", "people management", "stakeholder management"],
}

# Experience thresholds → implied skills
EXPERIENCE_IMPLICIT: list[tuple[int, list[str]]] = [
    (5, ["mentoring", "code review", "leadership"]),
    (3, ["code review", "problem solving"]),
    (0, ["teamwork", "communication"]),
]

# Job title category keywords → fallback generic skills
TITLE_CATEGORY_FALLBACKS: dict[str, list[str]] = {
    "software":   ["git", "agile", "problem solving", "communication", "teamwork"],
    "developer":  ["git", "agile", "problem solving", "communication", "teamwork"],
    "engineer":   ["git", "agile", "problem solving", "communication", "testing"],
    "data":       ["python", "sql", "statistics", "data", "communication"],
    "analyst":    ["sql", "data", "communication", "problem solving", "excel"],
    "designer":   ["design", "communication", "creativity", "teamwork"],
    "devops":     ["linux", "docker", "ci/cd", "git", "cloud"],
    "qa":         ["testing", "problem solving", "communication", "software"],
    "tester":     ["testing", "problem solving", "communication", "software"],
    "security":   ["security", "linux", "networking", "problem solving"],
    "mobile":     ["mobile", "git", "agile", "testing", "communication"],
    "cloud":      ["cloud", "linux", "docker", "networking", "security"],
    "machine learning": ["python", "machine learning", "statistics", "data"],
    "ai":         ["python", "machine learning", "deep learning", "data"],
    "intern":     ["teamwork", "communication", "problem solving", "git"],
}


# ══════════════════════════════════════════════════════════════════════
#  JOB CATEGORY DETECTION
# ══════════════════════════════════════════════════════════════════════

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "frontend":   ["frontend", "front-end", "react", "angular", "vue", "css",
                   "html", "ui developer", "web developer"],
    "backend":    ["backend", "back-end", "java", "python", ".net", "node",
                   "spring", "django", "flask", "express", "api developer",
                   "server-side"],
    "fullstack":  ["fullstack", "full-stack", "full stack"],
    "data":       ["data engineer", "data analyst", "data scientist",
                   "business intelligence", "etl", "data warehouse",
                   "data pipeline", "analytics"],
    "ai_ml":      ["machine learning", "deep learning", "ai ", "artificial intelligence",
                   "nlp", "computer vision", "ml engineer", "data science"],
    "devops":     ["devops", "sre", "site reliability", "infrastructure",
                   "cloud engineer", "platform engineer", "ci/cd"],
    "qa":         ["qa ", "quality assurance", "test engineer", "tester",
                   "automation test", "sdet", "quality engineer"],
    "mobile":     ["mobile", "android", "ios", "react native", "flutter",
                   "swift developer", "kotlin developer"],
    "ui_ux":      ["ui/ux", "ux design", "ui design", "user experience",
                   "user interface", "interaction design", "product design"],
    "security":   ["security", "cybersecurity", "soc analyst", "penetration",
                   "infosec", "security engineer"],
    "cloud":      ["cloud architect", "cloud engineer", "aws", "azure", "gcp",
                   "cloud solution"],
    "database":   ["dba", "database admin", "database engineer", "sql developer"],
    "management": ["project manager", "scrum master", "product manager",
                   "engineering manager", "tech lead", "team lead",
                   "technical lead", "cto"],
}


def detect_job_category(title: str, skills_matched: set[str],
                        skill_index: SkillIndex) -> str:
    """Return best-matching job category based on title + matched skills."""
    text = title.lower()
    scores: dict[str, float] = defaultdict(float)

    # Score from title keywords
    for cat, kwds in CATEGORY_KEYWORDS.items():
        for kw in kwds:
            if kw in text:
                scores[cat] += 2.0

    # Score from matched skills' categories
    for sid in skills_matched:
        sk = skill_index.get_skill(sid)
        if sk:
            cat_map = {
                "frontend": "frontend", "backend": "backend",
                "fullstack": "fullstack", "ml_ai": "ai_ml",
                "ai_ml": "ai_ml", "data": "data", "devops": "devops",
                "cloud": "cloud", "security": "security",
                "mobile": "mobile", "database": "database",
                "analytics": "data",
            }
            mapped = cat_map.get(sk.category)
            if mapped:
                scores[mapped] += 0.5

    if not scores:
        return "general"
    return max(scores, key=scores.get)


# ══════════════════════════════════════════════════════════════════════
#  SENIORITY LEVEL DETECTION
# ══════════════════════════════════════════════════════════════════════

SENIORITY_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bintern(?:ship)?\b", re.I), "intern"),
    (re.compile(r"\btrainee\b", re.I), "intern"),
    (re.compile(r"\bjunior\b|(?:^|\s)jr[\.\s]", re.I), "junior"),
    (re.compile(r"\bentry[- ]level\b", re.I), "junior"),
    (re.compile(r"\bsenior\b|(?:^|\s)sr[\.\s]", re.I), "senior"),
    (re.compile(r"\bstaff\b", re.I), "staff"),
    (re.compile(r"\bprincipal\b", re.I), "principal"),
    (re.compile(r"\blead\b|\bteam\s+lead\b|\btech\s+lead\b", re.I), "lead"),
    (re.compile(r"\bmanager\b|\bdirector\b|\bhead\b|\bvp\b", re.I), "director"),
    (re.compile(r"\barchitect\b", re.I), "senior"),
]


def detect_seniority(title: str, experience_raw: str = "") -> str:
    t = str(title)
    for pat, level in SENIORITY_PATTERNS:
        if pat.search(t):
            return level
    # Fallback from experience
    try:
        m = re.search(r"(\d+)", str(experience_raw))
        if m:
            yrs = int(m.group(1))
            if yrs >= 8:
                return "senior"
            elif yrs >= 4:
                return "mid"
            elif yrs >= 1:
                return "junior"
            else:
                return "intern"
    except (ValueError, TypeError):
        pass
    return "mid"  # default


# ══════════════════════════════════════════════════════════════════════
#  ROLE ID ASSIGNMENT
# ══════════════════════════════════════════════════════════════════════

def load_career_ladders() -> dict:
    if LADDERS_JSON.exists():
        with open(LADDERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


CATEGORY_TO_ROLES: dict[str, list[str]] = {
    "frontend":   ["JR_FE_DEV", "JR_FS_DEV"],
    "backend":    ["JR_BE_DEV", "JR_SE", "JR_FS_DEV"],
    "fullstack":  ["JR_FS_DEV", "JR_SE"],
    "data":       ["DATA_ANALYST_INT", "DATA_ENGINEER_INT"],
    "ai_ml":      ["AI_ML_ENGINEER_INT", "DATA_ENGINEER_INT"],
    "devops":     ["DEVOPS_TRAINEE", "JR_SYS_ADMIN"],
    "qa":         ["JR_QA_ENG"],
    "mobile":     ["JR_MOBILE_DEV"],
    "ui_ux":      ["JR_UI_UX_DESIGNER"],
    "security":   ["JR_SYS_ADMIN"],
    "cloud":      ["DEVOPS_TRAINEE", "JR_SYS_ADMIN"],
    "database":   ["DATA_ENGINEER_INT", "JR_SYS_ADMIN"],
    "management": ["JR_SE"],
    "general":    ["JR_SE"],
}

ROLE_TITLES: dict[str, str] = {
    "INTERN_SE":          "Software Engineering Intern",
    "JR_SE":              "Junior Software Engineer",
    "JR_FE_DEV":          "Junior Frontend Developer",
    "JR_FS_DEV":          "Junior Full-Stack Developer",
    "JR_BE_DEV":          "Junior Backend Developer",
    "DATA_ANALYST_INT":   "Data Analyst (Entry Level)",
    "DATA_ENGINEER_INT":  "Data Engineer (Entry Level)",
    "AI_ML_ENGINEER_INT": "AI / ML Engineer (Entry Level)",
    "DEVOPS_TRAINEE":     "DevOps Trainee",
    "JR_SYS_ADMIN":       "Junior System Administrator",
    "JR_QA_ENG":          "QA Engineer (Entry Level)",
    "JR_MOBILE_DEV":      "Junior Mobile Developer",
    "JR_UI_UX_DESIGNER":  "UI/UX Designer (Entry Level)",
    "JR_IT_SUPPORT":      "Junior IT Support",
    "JR_BUSINESS_ANALYST":"Business Analyst (Entry Level)",
}


def assign_role(category: str, seniority: str, title: str) -> tuple[str, str]:
    """Return (role_id, role_title) based on category + seniority."""
    title_lower = title.lower()

    # Direct title matches first
    if "business analyst" in title_lower:
        return "JR_BUSINESS_ANALYST", ROLE_TITLES["JR_BUSINESS_ANALYST"]
    if "it support" in title_lower or "help desk" in title_lower:
        return "JR_IT_SUPPORT", ROLE_TITLES["JR_IT_SUPPORT"]
    if seniority == "intern":
        return "INTERN_SE", ROLE_TITLES["INTERN_SE"]

    candidates = CATEGORY_TO_ROLES.get(category, ["JR_SE"])
    role_id = candidates[0]
    return role_id, ROLE_TITLES.get(role_id, role_id)


# ══════════════════════════════════════════════════════════════════════
#  THE 6-PASS MATCHER
# ══════════════════════════════════════════════════════════════════════

def match_skills_for_job(
    job_title: str,
    description: str,
    requirements: str,
    job_text: str,
    experience_raw: str,
    existing_skill_ids: set[str],
    skill_index: SkillIndex,
) -> dict[str, SkillMatch]:
    """
    Run 6-pass matching for a single job.
    Returns { skill_id: SkillMatch } — best confidence per skill.
    """
    matches: dict[str, SkillMatch] = {}

    def _add(sid: str, conf: float, src: str):
        if sid and sid in skill_index.skills:
            if sid not in matches or matches[sid].confidence < conf:
                matches[sid] = SkillMatch(skill_id=sid, confidence=conf, source=src)

    # Combine text fields
    req_text  = f"{requirements} {job_text}"
    desc_text = f"{description}"
    all_text  = f"{job_title} {description} {requirements} {job_text}"

    # ── PASS 1 + 2: Fast combined scan (exact + alias) ───────────
    # Scan requirements first (highest confidence zone)
    for sid, conf, src in skill_index.fast_scan(req_text):
        _add(sid, conf, src)          # 1.0 exact / 0.9 alias

    # Scan description (slightly lower for name matches)
    for sid, conf, src in skill_index.fast_scan(desc_text):
        adj_conf = conf if conf <= 0.9 else 0.85  # name in desc → 0.85
        _add(sid, adj_conf, src)

    # Scan title (boost back to 1.0 for name matches)
    for sid, conf, src in skill_index.fast_scan(job_title):
        _add(sid, 1.0 if conf >= 0.9 else conf, src)

    # ── PASS 3: Context-aware NLP patterns ───────────────────────
    all_text_lower = all_text.lower()
    for ctx_pat, implied_names in CONTEXT_PATTERNS:
        if ctx_pat.search(all_text_lower):
            for iname in implied_names:
                # Resolve name → skill_id
                sid = skill_index.name_to_id.get(iname.lower())
                if not sid:
                    sid = skill_index.alias_to_id.get(iname.lower())
                if sid:
                    _add(sid, 0.7, "context")

    # ── PASS 4: Skill co-occurrence ──────────────────────────────
    # Collect names of already-matched skills
    matched_names = set()
    for sid in matches:
        sk = skill_index.get_skill(sid)
        if sk:
            matched_names.add(sk.name.lower())

    for trigger, implied_list in COOCCURRENCE_RULES.items():
        if trigger in matched_names:
            for iname in implied_list:
                sid = skill_index.name_to_id.get(iname.lower())
                if not sid:
                    sid = skill_index.alias_to_id.get(iname.lower())
                if sid:
                    _add(sid, 0.4, "cooccurrence")

    # ── PASS 5: Implicit skills (seniority / experience) ────────
    title_lower = job_title.lower()
    for keyword, implied_skills in SENIORITY_IMPLICIT.items():
        if keyword in title_lower:
            for iname in implied_skills:
                sid = skill_index.name_to_id.get(iname.lower())
                if not sid:
                    sid = skill_index.alias_to_id.get(iname.lower())
                if sid:
                    _add(sid, 0.5, "implicit")

    # Experience-based
    try:
        exp_m = re.search(r"(\d+)", str(experience_raw))
        if exp_m:
            yrs = int(exp_m.group(1))
            for threshold, imp_skills in EXPERIENCE_IMPLICIT:
                if yrs >= threshold:
                    for iname in imp_skills:
                        sid = skill_index.name_to_id.get(iname.lower())
                        if not sid:
                            sid = skill_index.alias_to_id.get(iname.lower())
                        if sid:
                            _add(sid, 0.5, "implicit")
                    break  # only first matching threshold
    except (ValueError, TypeError):
        pass

    # ── PASS 6: Technology stack inference ────────────────────────
    for tech, implied_skills in STACK_INFERENCE.items():
        tech_lower = tech.lower()
        try:
            if re.search(rf"\b{re.escape(tech_lower)}\b", all_text_lower, re.I):
                for iname in implied_skills:
                    sid = skill_index.name_to_id.get(iname.lower())
                    if not sid:
                        sid = skill_index.alias_to_id.get(iname.lower())
                    if sid:
                        _add(sid, 0.5, "stack")
        except re.error:
            pass

    # ── Preserve original tags ───────────────────────────────────
    for sid in existing_skill_ids:
        if sid in skill_index.skills:
            _add(sid, 1.0, "original")  # keep originals at max confidence

    return matches


# ══════════════════════════════════════════════════════════════════════
#  QUALITY CONTROLS
# ══════════════════════════════════════════════════════════════════════

MIN_SKILLS = 5
MAX_SKILLS = 50
MIN_CONFIDENCE = 0.5


def apply_quality_controls(
    matches: dict[str, SkillMatch],
    job_title: str,
    skill_index: SkillIndex,
) -> dict[str, SkillMatch]:
    """Apply confidence threshold, min/max limits, fallback."""

    # 1. Filter by min confidence
    filtered = {sid: m for sid, m in matches.items()
                if m.confidence >= MIN_CONFIDENCE}

    # 2. If below minimum, add fallback skills
    if len(filtered) < MIN_SKILLS:
        title_lower = job_title.lower()
        for keyword, fallback_names in TITLE_CATEGORY_FALLBACKS.items():
            if keyword in title_lower:
                for fname in fallback_names:
                    sid = skill_index.name_to_id.get(fname.lower())
                    if not sid:
                        sid = skill_index.alias_to_id.get(fname.lower())
                    if sid and sid not in filtered:
                        filtered[sid] = SkillMatch(
                            skill_id=sid, confidence=0.5, source="fallback"
                        )
                break  # only first category match

        # Still short? Add universal fallback
        if len(filtered) < MIN_SKILLS:
            for fname in ["communication", "teamwork", "problem solving",
                          "critical thinking", "time management"]:
                sid = skill_index.name_to_id.get(fname.lower())
                if not sid:
                    sid = skill_index.alias_to_id.get(fname.lower())
                if sid and sid not in filtered:
                    filtered[sid] = SkillMatch(
                        skill_id=sid, confidence=0.5, source="fallback"
                    )
                if len(filtered) >= MIN_SKILLS:
                    break

    # 3. If above maximum, keep top by confidence
    if len(filtered) > MAX_SKILLS:
        sorted_items = sorted(filtered.items(),
                              key=lambda x: x[1].confidence, reverse=True)
        filtered = dict(sorted_items[:MAX_SKILLS])

    return filtered


# ══════════════════════════════════════════════════════════════════════
#  PROCESS SINGLE JOB (for multiprocessing)
# ══════════════════════════════════════════════════════════════════════

def _process_job_row(args: tuple) -> dict:
    """Process a single row. Designed for use with ProcessPoolExecutor."""
    (idx, row_dict, skills_data, skill_name_map, skill_alias_map,
     skill_category_map) = args

    # Reconstruct a lightweight skill index in worker
    # (We pass pre-computed data to avoid pickling the full SkillIndex)
    job_title    = str(row_dict.get("job_title", ""))
    description  = str(row_dict.get("description", ""))
    requirements = str(row_dict.get("requirements_text", ""))
    job_text     = str(row_dict.get("job_text", ""))
    exp_raw      = str(row_dict.get("experience_raw", ""))

    # Parse existing skill IDs (semicolon-separated)
    existing_raw = str(row_dict.get("matched_skill_ids", ""))
    existing_ids = set()
    if existing_raw and existing_raw != "nan":
        existing_ids = {s.strip() for s in existing_raw.split(";") if s.strip()}

    return {
        "idx": idx,
        "job_title": job_title,
        "description": description,
        "requirements_text": requirements,
        "job_text": job_text,
        "experience_raw": exp_raw,
        "existing_skill_ids": existing_ids,
    }


# ══════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════

def find_input_csv() -> Optional[Path]:
    for p in _FALLBACK_INPUTS:
        if p.exists():
            return p
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-tag all jobs with expanded skills (6-pass matching)")
    parser.add_argument("--input", type=str, default=None,
                        help="Input CSV path (auto-detected if omitted)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_CSV))
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of parallel workers (default 1, use >1 for speed)")
    parser.add_argument("--sample", type=int, default=100,
                        help="Number of validation samples to print (default 100)")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Disable spaCy NER augmentation")
    parser.add_argument("--dry-run", action="store_true",
                        help="Process only first 50 rows for testing")
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 78)
    print("  RETAG JOBS WITH EXPANDED SKILLS — v2.0")
    print("  Multi-pass intelligent skill matching")
    print("=" * 78)

    # ── 1. Load skills ───────────────────────────────────────────
    log.info("Loading skills from %s …", SKILLS_CSV)
    if not SKILLS_CSV.exists():
        log.error("Skills file not found: %s", SKILLS_CSV)
        sys.exit(1)
    skills_df = pd.read_csv(SKILLS_CSV, dtype=str, keep_default_na=False)
    skill_index = SkillIndex(skills_df)
    log.info("Loaded %d skills", len(skill_index.skills))

    # ── 2. Load jobs ─────────────────────────────────────────────
    input_path = Path(args.input) if args.input else find_input_csv()
    if input_path is None or not input_path.exists():
        log.error("No input CSV found. Expected one of: %s",
                  [str(p) for p in _FALLBACK_INPUTS])
        sys.exit(1)
    log.info("Loading jobs from %s …", input_path)
    jobs_df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    total_jobs = len(jobs_df)
    log.info("Loaded %d jobs", total_jobs)

    if args.dry_run:
        jobs_df = jobs_df.head(50).copy()
        log.info("DRY RUN: processing first 50 rows")
        total_jobs = len(jobs_df)

    # ── 3. Load career ladders for role assignment ───────────────
    career_ladders = load_career_ladders()
    log.info("Career ladders loaded: %d domains", len(career_ladders))

    # ── 4. Optional spaCy model ──────────────────────────────────
    nlp = None
    if not args.no_spacy and HAS_SPACY:
        for model_name in ["en_core_web_lg", "en_core_web_sm"]:
            try:
                nlp = spacy.load(model_name, disable=["parser", "lemmatizer"])
                log.info("spaCy model loaded: %s", model_name)
                break
            except OSError:
                continue
        if nlp is None:
            log.warning("No spaCy model found; context Pass 3 uses regex only")

    # ── 5. Process all jobs ──────────────────────────────────────
    log.info("Starting 6-pass skill matching for %d jobs …", total_jobs)

    results: list[dict] = []
    all_skill_counts: list[int] = []
    all_confidences: list[float] = []
    skill_frequency: Counter = Counter()
    cooccurrence: Counter = Counter()
    low_skill_jobs: list[dict] = []

    # Stats for original vs new
    original_jobs_count = 0
    original_skills_added = 0
    original_skills_kept = 0

    for idx in tqdm(range(total_jobs), desc="  Matching skills", unit="job"):
        row = jobs_df.iloc[idx]

        job_title    = str(row.get("job_title", ""))
        description  = str(row.get("description", ""))
        requirements = str(row.get("requirements_text", ""))
        job_text     = str(row.get("job_text", ""))
        exp_raw      = str(row.get("experience_raw", ""))

        # Parse existing skill IDs
        existing_raw = str(row.get("matched_skill_ids", ""))
        existing_ids = set()
        if existing_raw and existing_raw != "nan" and existing_raw.strip():
            existing_ids = {s.strip() for s in existing_raw.split(";")
                           if s.strip()}

        is_original = bool(existing_ids)
        if is_original:
            original_jobs_count += 1

        # ── Run 6-pass matching ──────────────────────────────────
        matches = match_skills_for_job(
            job_title=job_title,
            description=description,
            requirements=requirements,
            job_text=job_text,
            experience_raw=exp_raw,
            existing_skill_ids=existing_ids,
            skill_index=skill_index,
        )

        # ── Quality controls ─────────────────────────────────────
        matches = apply_quality_controls(matches, job_title, skill_index)

        # ── Stats tracking ───────────────────────────────────────
        if is_original:
            new_sids = set(matches.keys()) - existing_ids
            original_skills_added += len(new_sids)
            original_skills_kept += len(existing_ids & set(matches.keys()))

        # Sorted by confidence desc
        sorted_matches = sorted(matches.values(),
                                key=lambda m: m.confidence, reverse=True)
        skill_ids = [m.skill_id for m in sorted_matches]
        skill_names = []
        for sid in skill_ids:
            sk = skill_index.get_skill(sid)
            skill_names.append(sk.name if sk else sid)

        avg_conf = (sum(m.confidence for m in sorted_matches) /
                    len(sorted_matches)) if sorted_matches else 0.0

        all_skill_counts.append(len(skill_ids))
        all_confidences.append(avg_conf)
        skill_frequency.update(skill_ids)

        # Co-occurrence pairs (top skills only for performance)
        top_sids = skill_ids[:20]
        for a, b in combinations(sorted(top_sids), 2):
            cooccurrence[(a, b)] += 1

        # Flag low-skill jobs
        if len(skill_ids) < MIN_SKILLS:
            low_skill_jobs.append({
                "idx": idx, "job_title": job_title,
                "skill_count": len(skill_ids),
            })

        # ── Detect category, seniority, role ─────────────────────
        category  = detect_job_category(job_title, set(skill_ids), skill_index)
        seniority = detect_seniority(job_title, exp_raw)
        role_id, role_title = assign_role(category, seniority, job_title)

        # ── Build result row ─────────────────────────────────────
        results.append({
            "matched_skill_ids":       ";".join(skill_ids),
            "matched_skills":          ";".join(skill_names),
            "matched_skill_count":     len(skill_ids),
            "matching_confidence_avg": round(avg_conf, 4),
            "skill_extraction_version": "v2.0",
            "job_category":            category,
            "seniority_level":         seniority,
            "role_id":                 role_id,
            "role_title":              role_title,
        })

    # ── 6. Merge results into DataFrame ──────────────────────────
    log.info("Merging results …")
    results_df = pd.DataFrame(results)

    # Drop old columns that we're replacing
    cols_to_replace = [
        "matched_skill_ids", "matched_skills", "matched_skill_count",
        "role_id", "role_title", "job_category", "seniority_level",
    ]
    for col in cols_to_replace:
        if col in jobs_df.columns:
            jobs_df = jobs_df.drop(columns=[col])

    # Concatenate
    final_df = pd.concat([jobs_df.reset_index(drop=True),
                          results_df.reset_index(drop=True)], axis=1)

    # ── 7. Save output ───────────────────────────────────────────
    output_path = Path(args.output)
    final_df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
    log.info("Saved %d tagged jobs → %s", len(final_df), output_path)

    # ── 8. Generate statistics & report ──────────────────────────
    elapsed = time.time() - start_time
    import numpy as np

    counts_arr = all_skill_counts
    report_lines = [
        "=" * 78,
        "  SKILL TAGGING REPORT — v2.0",
        f"  Generated: {datetime.now().isoformat()}",
        f"  Elapsed:   {elapsed:.1f}s  ({elapsed/total_jobs:.3f}s per job)",
        "=" * 78,
        "",
        f"  Input:  {input_path}  ({total_jobs} jobs)",
        f"  Skills: {SKILLS_CSV}  ({len(skill_index.skills)} skills)",
        f"  Output: {output_path}",
        "",
        "  ── Skills per Job ──",
        f"    Min:    {min(counts_arr) if counts_arr else 0}",
        f"    Max:    {max(counts_arr) if counts_arr else 0}",
        f"    Mean:   {sum(counts_arr)/len(counts_arr):.1f}" if counts_arr else "    Mean: 0",
        f"    Median: {sorted(counts_arr)[len(counts_arr)//2]}" if counts_arr else "    Median: 0",
        "",
        "  ── Confidence ──",
        f"    Avg confidence (all jobs): {sum(all_confidences)/len(all_confidences):.3f}" if all_confidences else "    N/A",
        "",
        "  ── Original Jobs ──",
        f"    Original jobs processed:    {original_jobs_count}",
        f"    Original skills preserved:  {original_skills_kept}",
        f"    NEW skills added to originals: {original_skills_added}",
        "",
        f"  ── Low-Skill Jobs (<{MIN_SKILLS}) ──",
        f"    Count: {len(low_skill_jobs)}",
    ]

    if low_skill_jobs:
        for lj in low_skill_jobs[:20]:
            report_lines.append(
                f"    [{lj['idx']:>5d}] {lj['skill_count']} skills — {lj['job_title'][:60]}")

    # Top 30 most common skills
    report_lines += [
        "",
        "  ── Top 30 Most Common Skills ──",
    ]
    for sid, cnt in skill_frequency.most_common(30):
        sk = skill_index.get_skill(sid)
        name = sk.name if sk else sid
        pct = cnt / total_jobs * 100
        report_lines.append(f"    {sid:>8s}  {name:35s}  {cnt:>6d}  ({pct:5.1f}%)")

    # Category distribution
    if "job_category" in final_df.columns:
        report_lines += ["", "  ── Job Category Distribution ──"]
        for cat, cnt in final_df["job_category"].value_counts().items():
            report_lines.append(f"    {cat:20s}  {cnt:>6d}")

    # Seniority distribution
    if "seniority_level" in final_df.columns:
        report_lines += ["", "  ── Seniority Level Distribution ──"]
        for lvl, cnt in final_df["seniority_level"].value_counts().items():
            report_lines.append(f"    {lvl:15s}  {cnt:>6d}")

    # Role distribution
    if "role_id" in final_df.columns:
        report_lines += ["", "  ── Role Assignment Distribution ──"]
        for r, cnt in final_df["role_id"].value_counts().items():
            report_lines.append(f"    {r:25s}  {cnt:>6d}")

    report_lines += ["", "=" * 78]
    report_text = "\n".join(report_lines)
    report_path = REPORTS_DIR / "skill_tagging_report.txt"
    report_path.write_text(report_text, encoding="utf-8")
    print(report_text)

    # ── 9. Co-occurrence matrix ──────────────────────────────────
    log.info("Saving skill co-occurrence top 100 pairs …")
    top_pairs = cooccurrence.most_common(100)
    cooc_rows = []
    for (a, b), cnt in top_pairs:
        sk_a = skill_index.get_skill(a)
        sk_b = skill_index.get_skill(b)
        cooc_rows.append({
            "skill_a_id": a,
            "skill_a_name": sk_a.name if sk_a else a,
            "skill_b_id": b,
            "skill_b_name": sk_b.name if sk_b else b,
            "co_occurrence_count": cnt,
        })
    cooc_df = pd.DataFrame(cooc_rows)
    cooc_path = REPORTS_DIR / "skill_cooccurrence_top100.csv"
    cooc_df.to_csv(cooc_path, index=False)
    log.info("Co-occurrence saved → %s", cooc_path)

    # ── 10. Validation sample ────────────────────────────────────
    n_sample = min(args.sample, total_jobs)
    sample_indices = sorted(
        pd.Series(range(total_jobs)).sample(n=n_sample, random_state=42).tolist()
    )

    print(f"\n{'=' * 78}")
    print(f"  VALIDATION SAMPLE ({n_sample} random jobs)")
    print(f"{'=' * 78}")

    for i, si in enumerate(sample_indices[:20]):  # print first 20
        r = final_df.iloc[si]
        title   = str(r.get("job_title", ""))[:60]
        skills  = str(r.get("matched_skills", ""))[:100]
        count   = r.get("matched_skill_count", 0)
        conf    = r.get("matching_confidence_avg", 0)
        cat     = r.get("job_category", "")
        senior  = r.get("seniority_level", "")
        role    = r.get("role_id", "")

        print(f"\n  [{si:>5d}] {title}")
        print(f"         Skills ({count}): {skills}…")
        print(f"         Conf: {conf:.3f} | Cat: {cat} | "
              f"Seniority: {senior} | Role: {role}")

    # Full validation (all samples) → save to file
    val_rows = []
    for si in sample_indices:
        r = final_df.iloc[si]
        # Build skill-confidence breakdown
        sids = str(r.get("matched_skill_ids", "")).split(";")
        val_rows.append({
            "job_index": si,
            "job_title": r.get("job_title", ""),
            "skill_count": r.get("matched_skill_count", 0),
            "avg_confidence": r.get("matching_confidence_avg", 0),
            "top_10_skills": ";".join(str(r.get("matched_skills", "")).split(";")[:10]),
            "job_category": r.get("job_category", ""),
            "seniority_level": r.get("seniority_level", ""),
            "role_id": r.get("role_id", ""),
            "role_title": r.get("role_title", ""),
        })
    val_df = pd.DataFrame(val_rows)
    val_path = REPORTS_DIR / "validation_sample.csv"
    val_df.to_csv(val_path, index=False)
    log.info("Validation sample saved → %s", val_path)

    print(f"\n{'=' * 78}")
    print(f"  COMPLETE — {len(final_df)} jobs tagged, "
          f"{elapsed:.1f}s elapsed")
    print(f"  Output:     {output_path}")
    print(f"  Report:     {report_path}")
    print(f"  Co-occur:   {cooc_path}")
    print(f"  Validation: {val_path}")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
