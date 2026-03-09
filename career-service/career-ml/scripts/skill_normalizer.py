#!/usr/bin/env python3
"""
skill_normalizer.py — Centralized Skill Normalization Module
==============================================================
Provides:

1. Alias & near-duplicate merging
   - react / react.js / reactjs → SK_REACT
   - js / javascript / java script → SK002
   - node / node.js / nodejs → SK_NODE
   - c# / c sharp / csharp → SK_CSHARP

2. Domain-skill cluster definitions — maps skill IDs to domains:
   frontend, backend, fullstack, ai_ml, data_science, data_engineering,
   devops, cloud, cybersecurity, mobile, ui_ux, game_development,
   blockchain, embedded, qa_testing, project_management, etc.

3. Skill tier classification for every skill:
   - core_defining: must-have for a role (weight=1.0)
   - supporting:    commonly required alongside core (weight=0.7)
   - optional:      nice-to-have (weight=0.4)
   - generic_soft:  communication / teamwork / etc. (weight=0.1)
   - domain_signal: skill strongly signals a domain (weight=0.6)

4. Generic-skill downweighting table

This module does NOT depend on any recommendation code. It is imported
by data pipeline scripts AND optionally by the live recommender.

Run standalone to validate & print diagnostics:
    python scripts/skill_normalizer.py
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd


# ═══════════════════════════════════════════════════════════════════════
#  1. ALIAS / NEAR-DUPLICATE MERGE TABLE
# ═══════════════════════════════════════════════════════════════════════

# canonical_name → list of known aliases / variants
# The first entry is the canonical form; the rest are merged into it.
ALIAS_MERGE_TABLE: Dict[str, List[str]] = {
    # === Languages ===
    "javascript":       ["javascript", "java script", "js", "ecmascript", "es6", "es2015", "es2017"],  # SK002=javascript, SK293=java script
    "typescript":       ["typescript", "type script", "ts"],
    "python":           ["python", "python3", "python 3", "py"],
    "java":             ["java"],
    "c":                ["c"],
    "c ++":             ["c ++", "c++", "cpp", "c plus plus"],
    ".net":             [".net", "dotnet", "dot net", ".net core", "asp.net", "aspnet", "c#", "c sharp", "csharp", "c-sharp"],
    "ruby":             ["ruby"],
    "go":               ["go", "golang", "go lang"],
    "rust":             ["rust", "rust-lang", "rustlang"],
    "swift":            ["swift"],
    "kotlin":           ["kotlin"],
    "php":              ["php"],
    "r":                ["r", "r language", "r programming"],
    "scala":            ["scala"],
    "dart":             ["dart"],
    "lua":              ["lua"],
    "perl":             ["perl"],
    "haskell":          ["haskell"],
    "elixir":           ["elixir"],
    "clojure":          ["clojure"],
    "julia":            ["julia"],
    "solidity":         ["solidity"],
    "gdscript":         ["gdscript", "gd script"],
    "mojo":             ["mojo"],
    "sql":              ["sql", "structured query language"],

    # === Frontend Frameworks ===
    "react":            ["react", "react.js", "reactjs", "react js"],  # SK351=react, SK113=react.js → both hit
    "angular":          ["angular", "angularjs", "angular.js", "angular js"],
    "vue":              ["vue", "vue.js", "vuejs", "vue js"],
    "svelte":           ["svelte", "sveltejs", "svelte.js"],
    "next.js":          ["next.js", "nextjs", "next js", "next"],
    "nuxt.js":          ["nuxt.js", "nuxtjs", "nuxt js", "nuxt"],
    "jquery":           ["jquery", "j query"],

    # === Backend Frameworks ===
    "node.js":          ["node.js", "nodejs", "node js", "node"],
    "express":          ["express", "express.js", "expressjs"],
    "django":           ["django"],
    "flask":            ["flask"],
    "fastapi":          ["fastapi", "fast api", "fast-api"],
    "spring":           ["spring", "spring boot", "springboot", "spring framework"],
    # .net already defined in Languages section (with c# aliases)
    "rails":            ["rails", "ruby on rails", "ror"],
    "laravel":          ["laravel"],

    # === Databases ===
    "mysql":            ["mysql", "my sql"],
    "postgresql":       ["postgresql", "postgres", "pgsql", "pg"],
    "mongodb":          ["mongodb", "mongo", "mongo db"],
    "redis":            ["redis"],
    "elasticsearch":    ["elasticsearch", "elastic search", "es", "elastic"],
    "cassandra":        ["cassandra", "apache cassandra"],
    "dynamodb":         ["dynamodb", "dynamo db", "dynamo"],
    "sqlite":           ["sqlite", "sqlite3"],
    "oracle db":        ["oracle db", "oracle database", "oracle"],
    "sql server":       ["sql server", "mssql", "ms sql", "microsoft sql server"],

    # === DevOps / Cloud ===
    "docker":           ["docker", "containerization"],
    "kubernetes":       ["kubernetes", "k8s"],
    "terraform":        ["terraform"],
    "ansible":          ["ansible"],
    "jenkins":          ["jenkins"],
    "aws":              ["aws", "amazon web services", "amazon aws"],
    "azure":            ["azure", "microsoft azure", "ms azure"],
    "gcp":              ["gcp", "google cloud", "google cloud platform"],
    "linux":            ["linux", "unix", "linux/unix"],
    "nginx":            ["nginx"],
    "ci/cd":            ["ci/cd", "ci cd", "cicd", "continuous integration", "continuous delivery"],

    # === AI/ML ===
    "tensorflow":       ["tensorflow", "tf", "tensor flow"],
    "pytorch":          ["pytorch", "py torch", "torch"],
    "scikit-learn":     ["scikit-learn", "sklearn", "scikit learn"],
    "keras":            ["keras"],
    "pandas":           ["pandas"],
    "numpy":            ["numpy", "num py"],
    "opencv":           ["opencv", "open cv", "cv2"],
    "machine learning": ["machine learning", "ml", "machine-learning"],
    "deep learning":    ["deep learning", "dl", "deep-learning"],
    "nlp":              ["nlp", "natural language processing", "natural-language-processing"],
    "computer vision":  ["computer vision", "cv"],
    "langchain":        ["langchain", "lang chain"],
    "llamaindex":       ["llamaindex", "llama index", "llama_index"],
    "hugging face":     ["hugging face", "huggingface", "hf transformers", "hugging face transformers"],

    # === Mobile ===
    "react native":     ["react native", "react-native", "reactnative"],
    "flutter":          ["flutter"],
    "android":          ["android", "android sdk"],
    "ios":              ["ios", "apple ios"],
    "swiftui":          ["swiftui", "swift ui"],

    # === Game Dev ===
    "unity":            ["unity", "unity3d", "unity 3d", "unity engine"],
    "unreal engine":    ["unreal engine", "unreal", "ue4", "ue5", "unrealengine"],
    "godot":            ["godot", "godot engine"],

    # === Data ===
    "apache spark":     ["apache spark", "spark", "pyspark"],
    "hadoop":           ["hadoop", "apache hadoop"],
    "kafka":            ["kafka", "apache kafka"],
    "airflow":          ["airflow", "apache airflow"],
    "tableau":          ["tableau"],
    "power bi":         ["power bi", "powerbi", "power-bi"],

    # === Security ===
    "penetration testing": ["penetration testing", "pen testing", "pentest", "pen-testing"],
    "siem":             ["siem", "security information and event management"],
    "oauth":            ["oauth", "oauth2", "oauth 2.0"],

    # === Version Control ===
    "git":              ["git", "git/github", "git/gitlab"],
    "github":           ["github", "git hub"],
    "gitlab":           ["gitlab", "git lab"],

    # === Misc ===
    "rest api":         ["rest api", "restful api", "rest", "restful"],
    "graphql":          ["graphql", "graph ql"],
    "grpc":             ["grpc", "g-rpc"],
    "html":             ["html", "html5"],
    "css":              ["css", "css3"],
    "sass":             ["sass", "scss"],
    "webpack":          ["webpack", "web pack"],
    "agile":            ["agile", "agile methodology", "agile/scrum"],
    "scrum":            ["scrum", "scrum master"],
    "jira":             ["jira", "atlassian jira"],
    "figma":            ["figma"],
    "photoshop":        ["photoshop", "adobe photoshop"],
    "security+":        ["security+", "comptia security+", "comptia security"],
}


# ═══════════════════════════════════════════════════════════════════════
#  2. DOMAIN → SKILL CLUSTERS
# ═══════════════════════════════════════════════════════════════════════

# Maps domain names to sets of canonical skill names (lowercase).
# Used for: domain detection, domain-defining skill identification.
DOMAIN_SKILL_CLUSTERS: Dict[str, Dict[str, List[str]]] = {
    "FRONTEND_ENGINEERING": {
        "core": ["javascript", "typescript", "react", "angular", "vue", "html", "css",
                 "next.js", "svelte", "sass", "webpack", "jquery"],
        "supporting": ["node.js", "graphql", "rest api", "figma", "git",
                       "tailwind css", "bootstrap", "responsive design"],
    },
    "BACKEND_ENGINEERING": {
        "core": ["java", "python", "node.js", ".net", "go", "ruby", "php",
                 "spring", "django", "flask", "fastapi", "express", "rails", "laravel"],
        "supporting": ["sql", "postgresql", "mysql", "mongodb", "redis",
                       "rest api", "graphql", "docker", "git", "kafka", "grpc"],
    },
    "FULLSTACK_ENGINEERING": {
        "core": ["javascript", "typescript", "python", "react", "angular", "vue",
                 "node.js", "express", "django", "next.js"],
        "supporting": ["sql", "mongodb", "postgresql", "docker", "git", "html", "css",
                       "rest api", "graphql", "redis"],
    },
    "AI_ML": {
        "core": ["python", "machine learning", "deep learning", "tensorflow", "pytorch",
                 "scikit-learn", "keras", "nlp", "computer vision", "pandas", "numpy",
                 "hugging face", "langchain", "llamaindex", "opencv"],
        "supporting": ["r", "sql", "apache spark", "docker", "linux", "git",
                       "mojo", "cuda programming", "statistics", "data visualization",
                       "large language models", "gpt models", "bert",
                       "retrieval augmented generation", "prompt engineering",
                       "fine tuning llms", "vector databases", "embeddings",
                       "xgboost", "lightgbm", "catboost", "fastai", "onnx", "jax",
                       "mlflow", "model deployment", "feature engineering"],
    },
    "DATA_SCIENCE": {
        "core": ["python", "r", "sql", "pandas", "numpy", "scikit-learn",
                 "machine learning", "statistics", "data visualization",
                 "tableau", "power bi", "jupyter"],
        "supporting": ["tensorflow", "pytorch", "deep learning",
                       "apache spark", "excel", "matplotlib", "seaborn"],
    },
    "DATA_ENGINEERING": {
        "core": ["sql", "python", "apache spark", "hadoop", "kafka",
                 "airflow", "postgresql", "data modeling", "etl",
                 "data warehousing", "data pipeline"],
        "supporting": ["aws", "azure", "gcp", "docker", "linux",
                       "mongodb", "redis", "elasticsearch", "cassandra",
                       "dynamodb", "snowflake", "databricks"],
    },
    "DEVOPS_SRE": {
        "core": ["docker", "kubernetes", "terraform", "ansible", "jenkins",
                 "ci/cd", "linux", "aws", "azure", "gcp", "nginx",
                 "monitoring", "prometheus", "grafana"],
        "supporting": ["python", "go", "git", "bash", "shell scripting",
                       "helm", "argocd", "istio", "vault"],
    },
    "CLOUD_ENGINEERING": {
        "core": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker",
                 "cloud architecture", "cloud security", "serverless",
                 "infrastructure as code"],
        "supporting": ["linux", "python", "networking", "ci/cd", "ansible",
                       "cost optimization", "vpc", "iam"],
    },
    "SECURITY": {
        "core": ["security", "penetration testing", "siem", "network security",
                 "vulnerability assessment", "incident response", "firewall",
                 "encryption", "oauth", "identity management", "security+",
                 "cissp", "ceh", "soc"],
        "supporting": ["linux", "python", "aws", "azure", "docker",
                       "compliance", "risk assessment", "forensics"],
    },
    "MOBILE_ENGINEERING": {
        "core": ["android", "ios", "swift", "kotlin", "react native", "flutter",
                 "dart", "swiftui", "objective-c", "mobile development"],
        "supporting": ["java", "javascript", "rest api", "firebase", "git",
                       "xcode", "android studio", "ui/ux", "figma"],
    },
    "UI_UX_DESIGN": {
        "core": ["figma", "sketch", "adobe xd", "ui design", "ux design",
                 "user research", "wireframing", "prototyping", "usability testing",
                 "design systems", "interaction design"],
        "supporting": ["html", "css", "photoshop", "illustrator", "invision",
                       "typography", "color theory", "accessibility"],
    },
    "QA_TESTING": {
        "core": ["testing", "test automation", "selenium", "cypress",
                 "jest", "junit", "pytest", "qa methodology",
                 "manual testing", "performance testing", "load testing"],
        "supporting": ["python", "java", "javascript", "jira", "agile",
                       "ci/cd", "docker", "api testing", "postman"],
    },
    "GAME_DEVELOPMENT": {
        "core": ["unity", "unreal engine", "godot", "game design", "game ai",
                 "game physics", "shader programming", "3d modeling",
                 "multiplayer networking", "procedural generation",
                 "directx", "vulkan", "opengl", "xr development",
                 "game optimization", "gdscript", "glsl", "hlsl"],
        "supporting": ["c ++", ".net", "python", "lua", "git",
                       "blender", "maya", "photoshop", "agile"],
    },
    "BLOCKCHAIN_WEB3": {
        "core": ["solidity", "ethereum", "smart contracts", "web3",
                 "blockchain", "defi", "nft", "cryptocurrency",
                 "hyperledger", "consensus algorithms", "tokenomics"],
        "supporting": ["javascript", "python", "rust", "go", "node.js",
                       "docker", "security", "cryptography"],
    },
    "EMBEDDED_SYSTEMS": {
        "core": ["embedded systems", "firmware", "rtos", "microcontroller",
                 "arm", "fpga", "vhdl", "verilog", "pcb design",
                 "iot", "sensor integration", "embedded linux",
                 "device drivers", "hardware debugging"],
        "supporting": ["c", "c ++", "python", "linux", "assembly",
                       "oscilloscope", "uart", "spi", "i2c", "can bus"],
    },
    "PRODUCT_MANAGEMENT": {
        "core": ["product management", "product strategy", "roadmap planning",
                 "user stories", "market research", "competitive analysis",
                 "product analytics", "a/b testing", "stakeholder management"],
        "supporting": ["agile", "scrum", "jira", "data analysis", "sql",
                       "figma", "presentation skills"],
    },
    "BUSINESS_ANALYSIS": {
        "core": ["business analysis", "requirements gathering",
                 "process mapping", "use cases", "bpmn",
                 "data analysis", "sql", "excel", "stakeholder management"],
        "supporting": ["agile", "scrum", "jira", "power bi", "tableau",
                       "visio", "uml"],
    },
    "PROJECT_MANAGEMENT": {
        "core": ["project management", "pmp", "prince2", "agile", "scrum",
                 "risk management", "budget management", "resource planning",
                 "stakeholder management", "scheduling"],
        "supporting": ["jira", "ms project", "confluence", "trello",
                       "communication", "leadership"],
    },
    "TECHNICAL_WRITING": {
        "core": ["technical writing", "documentation", "api documentation",
                 "content strategy", "markdown", "information architecture",
                 "style guides", "docs-as-code"],
        "supporting": ["git", "html", "css", "jira", "confluence",
                       "diagrams", "dita", "swagger", "openapi"],
    },
}


# ═══════════════════════════════════════════════════════════════════════
#  3. GENERIC / SOFT SKILLS — downweighted during role matching
# ═══════════════════════════════════════════════════════════════════════

GENERIC_SOFT_SKILLS: Set[str] = {
    # Communication / Soft Skills
    "communication", "teamwork", "problem solving", "critical thinking",
    "time management", "leadership", "interpersonal skills",
    "collaboration", "adaptability", "creativity", "attention to detail",
    "self-motivated", "work ethic", "multitasking", "organizational skills",
    "analytical thinking", "decision making", "conflict resolution",
    "negotiation", "presentation skills", "mentoring", "coaching",
    "strategic thinking", "emotional intelligence", "cultural awareness",
    "customer service", "public speaking",

    # Very Generic Tech
    "software development", "coding", "programming",
    "web development", "web developer", "software engineer",
    "developer", "engineer", "technical skills",
    "it support", "troubleshooting", "debugging",
    "research", "documentation", "reporting",
    "infrastructure", "networking", "system administration",
    "database", "database management",
}


# Skill tier: maps canonical skill name → tier for weighting
SKILL_TIER_WEIGHTS = {
    "core_defining":  1.0,
    "supporting":     0.7,
    "optional":       0.4,
    "generic_soft":   0.1,
    "domain_signal":  0.6,
}


# ═══════════════════════════════════════════════════════════════════════
#  4. SENIORITY SIGNAL SKILLS
# ═══════════════════════════════════════════════════════════════════════

SENIORITY_DEFINING_SKILLS: Dict[str, List[str]] = {
    "intern_entry": [
        "html", "css", "javascript", "python", "java", "sql",
        "git", "linux", "data structures", "algorithms",
    ],
    "junior": [
        "react", "angular", "vue", "node.js", "django", "flask",
        "spring", "mysql", "postgresql", "mongodb", "docker",
        "rest api", "agile", "jira",
    ],
    "mid": [
        "kubernetes", "ci/cd", "terraform", "aws", "azure",
        "graphql", "redis", "elasticsearch", "testing",
        "code review", "design patterns", "microservices",
    ],
    "senior": [
        "system design", "architecture", "cloud architecture",
        "technical leadership", "mentoring", "performance optimization",
        "distributed systems", "high availability", "scalability",
    ],
    "staff_principal": [
        "strategic planning", "cross-team collaboration", "roadmap planning",
        "organizational leadership", "innovation", "technical strategy",
    ],
}


# ═══════════════════════════════════════════════════════════════════════
#  NORMALIZER CLASS
# ═══════════════════════════════════════════════════════════════════════

class SkillNormalizer:
    """
    Centralized skill normalization engine.

    Usage:
        normalizer = SkillNormalizer(skills_csv_path)
        canonical_id = normalizer.normalize_skill_name("react.js")
        cluster = normalizer.get_domain_for_skill("SK531")
        tier = normalizer.get_skill_tier("SK028", "BACKEND_ENGINEERING")
        weight = normalizer.get_skill_weight("SK028", "BACKEND_ENGINEERING")
    """

    def __init__(self, skills_csv_path: Optional[Path] = None):
        self.skills_df: Optional[pd.DataFrame] = None
        self.id_to_name: Dict[str, str] = {}
        self.name_to_id: Dict[str, str] = {}          # lowercase name → skill_id
        self.id_to_category: Dict[str, str] = {}
        self.id_to_type: Dict[str, str] = {}

        # Alias index: any alias (lowercase) → canonical skill_id
        self.alias_to_id: Dict[str, str] = {}

        # Domain membership: skill_id → set of domains
        self.skill_to_domains: Dict[str, Set[str]] = {}

        # Reverse: domain → set of skill_ids
        self.domain_to_skills: Dict[str, Set[str]] = {}

        # Tier cache: (skill_id, domain) → tier
        self._tier_cache: Dict[Tuple[str, str], str] = {}

        if skills_csv_path:
            self.load_skills(skills_csv_path)

    def load_skills(self, path: Path):
        """Load skills CSV and build all indexes."""
        self.skills_df = pd.read_csv(path)
        for _, row in self.skills_df.iterrows():
            sid = str(row["skill_id"]).strip().upper()
            name = str(row["name"]).strip().lower()
            category = str(row.get("category", "other")).strip().lower()
            stype = str(row.get("type", "technical")).strip().lower()

            self.id_to_name[sid] = name
            self.name_to_id[name] = sid
            self.id_to_category[sid] = category
            self.id_to_type[sid] = stype

        # Build alias → ID index from ALIAS_MERGE_TABLE
        self._build_alias_index()
        # Build domain cluster index
        self._build_domain_index()

        print(f"[SkillNormalizer] Loaded {len(self.id_to_name)} skills, "
              f"{len(self.alias_to_id)} alias entries, "
              f"{len(self.domain_to_skills)} domain clusters")

    def _build_alias_index(self):
        """Build alias → skill_id mapping using ALIAS_MERGE_TABLE."""
        for canonical, aliases in ALIAS_MERGE_TABLE.items():
            # Find the skill_id for the canonical name
            canonical_lower = canonical.lower().strip()
            canonical_id = self.name_to_id.get(canonical_lower)

            if not canonical_id:
                # Try to find via any alias
                for alias in aliases:
                    alias_lower = alias.lower().strip()
                    cid = self.name_to_id.get(alias_lower)
                    if cid:
                        canonical_id = cid
                        break

            if canonical_id:
                for alias in aliases:
                    self.alias_to_id[alias.lower().strip()] = canonical_id
                # Also map the canonical name itself
                self.alias_to_id[canonical_lower] = canonical_id

    def _build_domain_index(self):
        """Build skill_id ↔ domain mappings from DOMAIN_SKILL_CLUSTERS."""
        for domain, tiers in DOMAIN_SKILL_CLUSTERS.items():
            domain_ids: Set[str] = set()
            for tier_name, skill_names in tiers.items():
                for sname in skill_names:
                    sid = self.resolve_skill_name(sname)
                    if sid:
                        domain_ids.add(sid)
                        if sid not in self.skill_to_domains:
                            self.skill_to_domains[sid] = set()
                        self.skill_to_domains[sid].add(domain)
            self.domain_to_skills[domain] = domain_ids

    def resolve_skill_name(self, name: str) -> Optional[str]:
        """
        Resolve a skill name (or alias) to its canonical skill_id.
        Returns None if no match found.
        """
        name_lower = name.lower().strip()

        # 1. Direct name match
        if name_lower in self.name_to_id:
            return self.name_to_id[name_lower]

        # 2. Alias match
        if name_lower in self.alias_to_id:
            return self.alias_to_id[name_lower]

        # 3. Fuzzy: strip .js, remove spaces/hyphens
        cleaned = re.sub(r'[.\-_/]', '', name_lower).strip()
        if cleaned in self.name_to_id:
            return self.name_to_id[cleaned]
        if cleaned in self.alias_to_id:
            return self.alias_to_id[cleaned]

        return None

    def normalize_skill_id(self, skill_id: str) -> str:
        """
        Given a skill_id, return its canonical form (handles near-dupes).
        For now, just uppercases. Can be extended for merge logic.
        """
        return skill_id.strip().upper()

    def is_generic_soft_skill(self, skill_id: str) -> bool:
        """Check if a skill is in the generic/soft skill list."""
        name = self.id_to_name.get(skill_id.upper(), "").lower()
        return name in GENERIC_SOFT_SKILLS

    def get_skill_tier(self, skill_id: str, domain: Optional[str] = None) -> str:
        """
        Classify a skill's tier relative to a domain.
        Returns: 'core_defining', 'supporting', 'optional', 'generic_soft', 'domain_signal'
        """
        sid = skill_id.upper()
        cache_key = (sid, domain or "")
        if cache_key in self._tier_cache:
            return self._tier_cache[cache_key]

        # Check generic soft first
        if self.is_generic_soft_skill(sid):
            tier = "generic_soft"
        elif domain and domain.upper() in DOMAIN_SKILL_CLUSTERS:
            cluster = DOMAIN_SKILL_CLUSTERS[domain.upper()]
            name = self.id_to_name.get(sid, "").lower()

            if name in [s.lower() for s in cluster.get("core", [])]:
                tier = "core_defining"
            elif name in [s.lower() for s in cluster.get("supporting", [])]:
                tier = "supporting"
            elif self.skill_to_domains.get(sid):
                tier = "domain_signal"
            else:
                tier = "optional"
        elif self.skill_to_domains.get(sid):
            tier = "domain_signal"
        else:
            tier = "optional"

        self._tier_cache[cache_key] = tier
        return tier

    def get_skill_weight(self, skill_id: str, domain: Optional[str] = None) -> float:
        """Get the numeric weight for a skill based on its tier."""
        tier = self.get_skill_tier(skill_id, domain)
        return SKILL_TIER_WEIGHTS.get(tier, 0.4)

    def get_domains_for_skill(self, skill_id: str) -> Set[str]:
        """Return all domains that claim this skill."""
        return self.skill_to_domains.get(skill_id.upper(), set())

    def get_skills_for_domain(self, domain: str) -> Set[str]:
        """Return all skill_ids associated with a domain."""
        return self.domain_to_skills.get(domain.upper(), set())

    def detect_domain_from_skills(self, skill_ids: List[str]) -> List[Tuple[str, float]]:
        """
        Given a set of skill IDs, detect which domains they signal.
        Returns list of (domain, score) sorted by score descending.
        """
        skill_set = set(s.upper() for s in skill_ids)
        domain_scores = []

        for domain, domain_skills in self.domain_to_skills.items():
            if not domain_skills:
                continue
            overlap = len(skill_set & domain_skills)
            # Weight core skills more
            cluster = DOMAIN_SKILL_CLUSTERS.get(domain, {})
            core_names = set(s.lower() for s in cluster.get("core", []))
            core_overlap = sum(
                1 for sid in skill_set
                if self.id_to_name.get(sid, "").lower() in core_names
            )
            score = (core_overlap * 1.5 + (overlap - core_overlap) * 0.5) / max(len(domain_skills), 1)
            if score > 0:
                domain_scores.append((domain, round(score, 3)))

        domain_scores.sort(key=lambda x: x[1], reverse=True)
        return domain_scores

    def get_near_duplicates(self) -> List[Dict]:
        """Find potential near-duplicate skills in the dataset."""
        dupes = []
        seen = {}
        for sid, name in self.id_to_name.items():
            # Normalize for comparison: remove spaces, hyphens, dots
            cleaned = re.sub(r'[\s.\-_/]+', '', name.lower())
            if cleaned in seen:
                dupes.append({
                    "skill_1": seen[cleaned],
                    "name_1": self.id_to_name[seen[cleaned]],
                    "skill_2": sid,
                    "name_2": name,
                    "cleaned": cleaned,
                })
            else:
                seen[cleaned] = sid
        return dupes

    def get_orphan_skills(self, jsv_df: pd.DataFrame) -> List[Dict]:
        """
        Find skills that are not mapped to any job.
        jsv_df: DataFrame of job-skill vectors (skill_sk001, etc.)
        """
        skill_cols = [c for c in jsv_df.columns if c.startswith("skill_")]
        orphans = []
        for col in skill_cols:
            if jsv_df[col].sum() == 0:
                sid = col.replace("skill_", "").upper()
                name = self.id_to_name.get(sid, "unknown")
                category = self.id_to_category.get(sid, "unknown")
                orphans.append({"skill_id": sid, "name": name, "category": category})
        return orphans

    def classify_job_skills(
        self, skill_ids: List[str], role_domain: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        For a given set of skills attached to a job, classify each into a tier.
        Returns dict with keys: core_required, supporting, optional, generic_soft, domain_signal
        """
        result = {
            "core_required": [],
            "supporting": [],
            "optional": [],
            "generic_soft": [],
            "domain_signal": [],
        }

        for sid in skill_ids:
            tier = self.get_skill_tier(sid, role_domain)
            tier_map = {
                "core_defining": "core_required",
                "supporting": "supporting",
                "optional": "optional",
                "generic_soft": "generic_soft",
                "domain_signal": "domain_signal",
            }
            bucket = tier_map.get(tier, "optional")
            result[bucket].append(sid)

        return result


# ═══════════════════════════════════════════════════════════════════════
#  5. MODULE-LEVEL HELPERS
# ═══════════════════════════════════════════════════════════════════════

def get_default_normalizer() -> SkillNormalizer:
    """Create a normalizer loaded with the standard skills_v2.csv."""
    base = Path(__file__).resolve().parent.parent
    skills_path = base / "data" / "expanded" / "skills_v2.csv"
    if not skills_path.exists():
        raise FileNotFoundError(f"Skills CSV not found: {skills_path}")
    return SkillNormalizer(skills_path)


# ═══════════════════════════════════════════════════════════════════════
#  STANDALONE DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("SKILL NORMALIZER — DIAGNOSTICS")
    print("=" * 70)

    normalizer = get_default_normalizer()

    # Test alias resolution
    test_names = [
        "react.js", "reactjs", "React", "react",
        "node.js", "nodejs", "node",
        "java script", "javascript", "js",
        "c sharp", "c#", "csharp",
        "tensorflow", "tf", "tensor flow",
        "unity", "unity3d",
        "kubernetes", "k8s",
    ]
    print("\n--- Alias Resolution ---")
    for name in test_names:
        sid = normalizer.resolve_skill_name(name)
        actual_name = normalizer.id_to_name.get(sid, "?") if sid else "NOT FOUND"
        print(f"  '{name}' → {sid} ({actual_name})")

    # Near duplicates
    print("\n--- Near Duplicates ---")
    dupes = normalizer.get_near_duplicates()
    if dupes:
        for d in dupes:
            print(f"  {d['skill_1']} ({d['name_1']}) ↔ {d['skill_2']} ({d['name_2']})")
    else:
        print("  None found")

    # Domain cluster coverage
    print("\n--- Domain Skill Cluster Coverage ---")
    for domain, skills in normalizer.domain_to_skills.items():
        resolved = len(skills)
        cluster = DOMAIN_SKILL_CLUSTERS.get(domain, {})
        total_defined = len(cluster.get("core", [])) + len(cluster.get("supporting", []))
        print(f"  {domain}: {resolved}/{total_defined} resolved to skill IDs")

    # Test domain detection
    print("\n--- Domain Detection Test ---")
    test_profiles = {
        "Frontend Dev": ["SK002", "SK006", "SK005", "SK019"],   # js, html, css, json
        "AI/ML Engineer": ["SK004", "SK031", "SK531", "SK532"],  # python, ml, tf, pytorch
        "Game Developer": ["SK848", "SK849", "SK851"],           # unity, unreal, game design
    }
    for label, skills in test_profiles.items():
        domains = normalizer.detect_domain_from_skills(skills)
        print(f"  {label} → {domains[:3]}")

    print("\n--- Generic Soft Skill Examples ---")
    soft_count = sum(1 for sid in normalizer.id_to_name if normalizer.is_generic_soft_skill(sid))
    print(f"  {soft_count} skills classified as generic/soft")

    print("\nDone.")
