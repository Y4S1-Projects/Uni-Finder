#!/usr/bin/env python3
"""
repair_job_skill_mappings.py — Fix Job-Skill Vectors & Domain Mappings
=======================================================================
Phase A, Steps 3-5: Repair job-skill vectors using the normalizer.

This script:
1. Loads the normalizer's domain clusters & tier classification.
2. For each job, classifies skills into core/supporting/optional/generic/domain_signal
   based on the job's detected domain.
3. Applies skill-weight corrections to job-skill vectors:
   - Core skills get weight 1.0
   - Supporting skills get 0.7
   - Generic/soft skills get 0.1 (downweighted from 1.0!)
   - Optional skills get 0.4
4. Enhances domain detection using skill clusters (much better than text heuristics).
5. Repairs underrepresented domains by ensuring domain-defining skills are present.
6. Writes corrected files:
   - job_skill_vectors_v3.csv          (skill-tier-weighted vectors)
   - job_skill_classification.json     (per-job skill tier breakdown)
   - job_domain_corrections.csv        (domain re-assignments)

Run:
    cd career-service/career-ml
    python scripts/repair_job_skill_mappings.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_normalizer import (
    SkillNormalizer,
    DOMAIN_SKILL_CLUSTERS,
    GENERIC_SOFT_SKILLS,
    SKILL_TIER_WEIGHTS,
    SENIORITY_DEFINING_SKILLS,
)

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # career-ml/
DATA_DIR = BASE_DIR / "data"
EXPANDED = DATA_DIR / "expanded"
PROCESSED = DATA_DIR / "processed"
REPORTS = DATA_DIR / "reports"
REPORTS.mkdir(exist_ok=True)

SKILLS_CSV = EXPANDED / "skills_v2.csv"
JSV_CSV = PROCESSED / "job_skill_vectors_v2_fixed.csv"

OUTPUT_JSV = PROCESSED / "job_skill_vectors_v3.csv"
OUTPUT_CLASSIFICATION = REPORTS / "job_skill_classification.json"
OUTPUT_DOMAIN_CORRECTIONS = REPORTS / "job_domain_corrections.csv"
OUTPUT_REPAIR_SUMMARY = REPORTS / "repair_summary.txt"


# ─── Extended Domain Mapping from role_id ─────────────────────────────

ROLE_ID_DOMAIN_MAP = {
    # Frontend
    "FRONTEND_DEVELOPER": "FRONTEND_ENGINEERING",
    "UI_DEVELOPER": "FRONTEND_ENGINEERING",
    "WEB_DESIGNER": "FRONTEND_ENGINEERING",

    # Backend
    "BACKEND_DEVELOPER": "BACKEND_ENGINEERING",
    "API_DEVELOPER": "BACKEND_ENGINEERING",
    "JAVA_DEVELOPER": "BACKEND_ENGINEERING",
    "PYTHON_DEVELOPER": "BACKEND_ENGINEERING",
    "PHP_DEVELOPER": "BACKEND_ENGINEERING",
    "DOTNET_DEVELOPER": "BACKEND_ENGINEERING",

    # Fullstack
    "FULLSTACK_DEVELOPER": "FULLSTACK_ENGINEERING",
    "SOFTWARE_ENGINEER": "FULLSTACK_ENGINEERING",
    "WEB_DEVELOPER": "FULLSTACK_ENGINEERING",

    # AI/ML
    "ML_ENGINEER": "AI_ML",
    "AI_ENGINEER": "AI_ML",
    "AI_ML_ENGINEER": "AI_ML",
    "DATA_SCIENTIST": "DATA_SCIENCE",
    "NLP_ENGINEER": "AI_ML",
    "COMPUTER_VISION_ENGINEER": "AI_ML",
    "DEEP_LEARNING_ENGINEER": "AI_ML",
    "LLM_ENGINEER": "AI_ML",
    "AI_RESEARCH_SCIENTIST": "AI_ML",

    # Data
    "DATA_ANALYST": "DATA_SCIENCE",
    "DATA_ENGINEER": "DATA_ENGINEERING",
    "BI_ANALYST": "DATA_SCIENCE",
    "DATABASE_ADMINISTRATOR": "DATA_ENGINEERING",
    "ETL_DEVELOPER": "DATA_ENGINEERING",

    # DevOps / Cloud
    "DEVOPS_ENGINEER": "DEVOPS_SRE",
    "SRE_ENGINEER": "DEVOPS_SRE",
    "SITE_RELIABILITY_ENGINEER": "DEVOPS_SRE",
    "CLOUD_ARCHITECT": "CLOUD_ENGINEERING",
    "CLOUD_ENGINEER": "CLOUD_ENGINEERING",
    "PLATFORM_ENGINEER": "DEVOPS_SRE",
    "INFRASTRUCTURE_ENGINEER": "CLOUD_ENGINEERING",

    # Security
    "SECURITY_ENGINEER": "SECURITY",
    "SECURITY_ANALYST": "SECURITY",
    "PENETRATION_TESTER": "SECURITY",
    "SOC_ANALYST": "SECURITY",
    "CYBERSECURITY_ENGINEER": "SECURITY",

    # Mobile
    "MOBILE_DEVELOPER": "MOBILE_ENGINEERING",
    "ANDROID_DEVELOPER": "MOBILE_ENGINEERING",
    "IOS_DEVELOPER": "MOBILE_ENGINEERING",
    "FLUTTER_DEVELOPER": "MOBILE_ENGINEERING",

    # QA
    "QA_ENGINEER": "QA_TESTING",
    "QA_ANALYST": "QA_TESTING",
    "TEST_AUTOMATION_ENGINEER": "QA_TESTING",
    "SDET": "QA_TESTING",

    # UI/UX
    "UX_DESIGNER": "UI_UX_DESIGN",
    "UI_DESIGNER": "UI_UX_DESIGN",
    "PRODUCT_DESIGNER": "UI_UX_DESIGN",
    "UX_RESEARCHER": "UI_UX_DESIGN",

    # Game Dev
    "GAME_DEVELOPER": "GAME_DEVELOPMENT",
    "GAME_DESIGNER": "GAME_DEVELOPMENT",
    "GAME_PROGRAMMER": "GAME_DEVELOPMENT",
    "GRAPHICS_PROGRAMMER": "GAME_DEVELOPMENT",

    # Blockchain
    "BLOCKCHAIN_DEVELOPER": "BLOCKCHAIN_WEB3",
    "SMART_CONTRACT_DEVELOPER": "BLOCKCHAIN_WEB3",
    "WEB3_DEVELOPER": "BLOCKCHAIN_WEB3",

    # Embedded
    "EMBEDDED_ENGINEER": "EMBEDDED_SYSTEMS",
    "FIRMWARE_ENGINEER": "EMBEDDED_SYSTEMS",
    "IOT_ENGINEER": "EMBEDDED_SYSTEMS",

    # Management
    "PROJECT_MANAGER": "PROJECT_MANAGEMENT",
    "PRODUCT_MANAGER": "PRODUCT_MANAGEMENT",
    "SCRUM_MASTER": "PROJECT_MANAGEMENT",
    "TECH_LEAD": "FULLSTACK_ENGINEERING",
    "ENGINEERING_MANAGER": "FULLSTACK_ENGINEERING",

    # Business Analysis
    "BUSINESS_ANALYST": "BUSINESS_ANALYSIS",
    "SYSTEMS_ANALYST": "BUSINESS_ANALYSIS",

    # Technical Writing
    "TECHNICAL_WRITER": "TECHNICAL_WRITING",
}


def get_role_domain(role_id: str) -> str:
    """Resolve a role_id (with or without seniority suffix) to a domain."""
    rid = role_id.upper().strip()
    # Direct lookup
    if rid in ROLE_ID_DOMAIN_MAP:
        return ROLE_ID_DOMAIN_MAP[rid]

    # Strip seniority suffix: FRONTEND_DEVELOPER_INT → FRONTEND_DEVELOPER
    for suffix in ["_INT", "_JR", "_MID", "_SR", "_LEAD", "_PRINCIPAL", "_STAFF",
                   "_INTERN", "_ENTRY", "_SENIOR"]:
        if rid.endswith(suffix):
            base = rid[:-len(suffix)]
            if base in ROLE_ID_DOMAIN_MAP:
                return ROLE_ID_DOMAIN_MAP[base]

    # Keyword heuristics on role_id
    if "FRONTEND" in rid or "UI_DEV" in rid:
        return "FRONTEND_ENGINEERING"
    if "BACKEND" in rid:
        return "BACKEND_ENGINEERING"
    if "FULLSTACK" in rid or "SOFTWARE" in rid:
        return "FULLSTACK_ENGINEERING"
    if "AI" in rid or "ML" in rid or "MACHINE_LEARNING" in rid or "NLP" in rid or "DEEP_LEARNING" in rid:
        return "AI_ML"
    if "DATA_SCI" in rid:
        return "DATA_SCIENCE"
    if "DATA_ENG" in rid or "ETL" in rid or "DATABASE" in rid:
        return "DATA_ENGINEERING"
    if "DATA" in rid:
        return "DATA_SCIENCE"
    if "DEVOPS" in rid or "SRE" in rid or "PLATFORM" in rid:
        return "DEVOPS_SRE"
    if "CLOUD" in rid or "INFRASTRUCTURE" in rid:
        return "CLOUD_ENGINEERING"
    if "SECURITY" in rid or "CYBER" in rid or "PENETRATION" in rid or "SOC" in rid:
        return "SECURITY"
    if "MOBILE" in rid or "ANDROID" in rid or "IOS" in rid or "FLUTTER" in rid:
        return "MOBILE_ENGINEERING"
    if "QA" in rid or "TEST" in rid or "SDET" in rid:
        return "QA_TESTING"
    if "UX" in rid or "UI_DESIGN" in rid or "PRODUCT_DESIGN" in rid:
        return "UI_UX_DESIGN"
    if "GAME" in rid or "GRAPHICS" in rid:
        return "GAME_DEVELOPMENT"
    if "BLOCKCHAIN" in rid or "WEB3" in rid or "SMART_CONTRACT" in rid:
        return "BLOCKCHAIN_WEB3"
    if "EMBEDDED" in rid or "FIRMWARE" in rid or "IOT" in rid:
        return "EMBEDDED_SYSTEMS"
    if "PROJECT_MANAG" in rid or "SCRUM" in rid:
        return "PROJECT_MANAGEMENT"
    if "PRODUCT_MANAG" in rid:
        return "PRODUCT_MANAGEMENT"
    if "BUSINESS_ANAL" in rid or "SYSTEM_ANAL" in rid:
        return "BUSINESS_ANALYSIS"
    if "TECHNICAL_WRIT" in rid:
        return "TECHNICAL_WRITING"

    return "FULLSTACK_ENGINEERING"  # safe default


def repair_job_skill_mappings():
    """Main repair pipeline."""
    print("=" * 70)
    print("REPAIR JOB-SKILL MAPPINGS")
    print("=" * 70)

    # Load
    normalizer = SkillNormalizer(SKILLS_CSV)
    jsv = pd.read_csv(JSV_CSV)
    skill_cols = [c for c in jsv.columns if c.startswith("skill_")]
    meta_cols = [c for c in jsv.columns if not c.startswith("skill_")]
    print(f"Loaded: {len(jsv)} jobs, {len(skill_cols)} skill columns")

    # 1. Assign domain to each job using role_id
    print("\n--- Step 1: Assign Domains ---")
    jsv["detected_domain"] = jsv["role_id"].apply(get_role_domain)
    domain_dist = jsv["detected_domain"].value_counts()
    print("Domain distribution:")
    for domain, count in domain_dist.items():
        print(f"  {domain}: {count}")

    # Compare with existing domain (if available from enhanced features)
    if "domain" in jsv.columns:
        changed = (jsv["domain"] != jsv["detected_domain"]).sum()
        print(f"\nDomain re-assignments from old: {changed}/{len(jsv)}")

    # 2. Classify skills per job
    print("\n--- Step 2: Classify Skills Per Job ---")
    job_classifications = []
    tier_stats = Counter()

    # Build weight matrix: for each (skill, domain) compute the weight
    # We precompute a domain→skill_col→weight lookup
    print("  Precomputing skill weights per domain...")
    domain_weight_map = {}
    for domain in jsv["detected_domain"].unique():
        weights = {}
        for col in skill_cols:
            sid = col.replace("skill_", "").upper()
            weights[col] = normalizer.get_skill_weight(sid, domain)
        domain_weight_map[domain] = weights

    # Apply weights vectorially per-domain group
    print("  Applying tier-weighted vectors per domain group...")
    jsv_skill_data = jsv[skill_cols].values.astype(float)
    weighted_data = np.zeros_like(jsv_skill_data)

    for domain in jsv["detected_domain"].unique():
        mask = (jsv["detected_domain"] == domain).values
        weight_array = np.array([domain_weight_map[domain][col] for col in skill_cols])
        weighted_data[mask] = jsv_skill_data[mask] * weight_array[np.newaxis, :]

    jsv_weighted = jsv[meta_cols].copy()
    weighted_df = pd.DataFrame(weighted_data, columns=skill_cols, index=jsv.index)
    jsv_weighted = pd.concat([jsv_weighted, weighted_df], axis=1)
    print(f"  Weighted vectors computed: {jsv_weighted.shape}")

    # Per-job classification stats (sampled for speed, full for output)
    print("  Computing per-job tier classifications...")
    for idx, row in jsv.iterrows():
        role_domain = row["detected_domain"]
        active_skills = []
        for col in skill_cols:
            if row[col] > 0:
                sid = col.replace("skill_", "").upper()
                active_skills.append(sid)

        classification = normalizer.classify_job_skills(active_skills, role_domain)

        job_classifications.append({
            "job_uid": row.get("job_uid", idx),
            "role_id": row.get("role_id", ""),
            "detected_domain": role_domain,
            "core_count": len(classification["core_required"]),
            "supporting_count": len(classification["supporting"]),
            "optional_count": len(classification["optional"]),
            "generic_soft_count": len(classification["generic_soft"]),
            "domain_signal_count": len(classification["domain_signal"]),
            "total_skills": len(active_skills),
        })

        for tier, sids in classification.items():
            tier_stats[tier] += len(sids)

        if idx % 2000 == 0 and idx > 0:
            print(f"  Processed {idx}/{len(jsv)} jobs...")

    print(f"\nTier assignment totals:")
    for tier, count in tier_stats.most_common():
        print(f"  {tier}: {count}")

    # 3. Detect problematic jobs (no core skills for their domain)
    print("\n--- Step 3: Identify Problem Jobs ---")
    problem_jobs = []
    for jc in job_classifications:
        if jc["core_count"] == 0 and jc["total_skills"] > 0:
            problem_jobs.append(jc)

    print(f"Jobs with 0 core skills for their domain: {len(problem_jobs)}")

    # Break down by domain
    problem_by_domain = Counter(pj["detected_domain"] for pj in problem_jobs)
    for domain, count in problem_by_domain.most_common(10):
        total_in_domain = domain_dist.get(domain, 0)
        pct = round(100 * count / max(total_in_domain, 1), 1)
        print(f"  {domain}: {count}/{total_in_domain} ({pct}%) have 0 core skills")

    # 4. Domain-based skill-vector enrichment for underrepresented domains
    print("\n--- Step 4: Skill Vector Domain Enrichment ---")
    enrichment_count = 0
    enrichment_details = []

    # For each domain, verify that skill-level coverage is adequate
    for domain in DOMAIN_SKILL_CLUSTERS:
        domain_skills = normalizer.get_skills_for_domain(domain)
        domain_jobs = jsv_weighted[jsv_weighted["detected_domain"] == domain] if "detected_domain" in jsv_weighted.columns else pd.DataFrame()

        if domain_jobs.empty:
            # Get from original jsv
            domain_jobs_mask = jsv["detected_domain"] == domain
            if domain_jobs_mask.sum() == 0:
                enrichment_details.append({
                    "domain": domain,
                    "job_count": 0,
                    "action": "NO_JOBS_IN_DOMAIN",
                })
                continue

        domain_mask = jsv["detected_domain"] == domain
        domain_job_count = domain_mask.sum()

        if domain_job_count == 0:
            enrichment_details.append({
                "domain": domain,
                "job_count": 0,
                "action": "NO_JOBS_IN_DOMAIN",
            })
            continue

        # Check core skill coverage in domain jobs
        core_coverage = {}
        cluster = DOMAIN_SKILL_CLUSTERS[domain]
        core_names = cluster.get("core", [])

        for sname in core_names:
            sid = normalizer.resolve_skill_name(sname)
            if sid:
                col = f"skill_{sid.lower()}"
                if col in jsv.columns:
                    has_skill = jsv.loc[domain_mask, col].gt(0).sum()
                    core_coverage[sname] = {
                        "sid": sid, "col": col,
                        "count": int(has_skill),
                        "pct": round(100 * has_skill / domain_job_count, 1),
                    }

        enrichment_details.append({
            "domain": domain,
            "job_count": domain_job_count,
            "core_skill_coverage": core_coverage,
        })

        # Report domains with low core coverage
        low_coverage_skills = {
            k: v for k, v in core_coverage.items()
            if v["pct"] < 20
        }
        if low_coverage_skills:
            print(f"\n  {domain} ({domain_job_count} jobs) — low core-skill coverage:")
            for sname, info in low_coverage_skills.items():
                print(f"    {sname} ({info['sid']}): {info['count']}/{domain_job_count} "
                      f"({info['pct']}%)")

    # 5. Save outputs
    print("\n--- Step 5: Save Outputs ---")

    # Add detected_domain to weighted vectors
    jsv_weighted["detected_domain"] = jsv["detected_domain"]

    # Ensure all skill columns are present
    for col in skill_cols:
        if col not in jsv_weighted.columns:
            jsv_weighted[col] = 0.0

    # Save weighted vectors
    output_cols = meta_cols + ["detected_domain"] + skill_cols
    jsv_weighted[output_cols].to_csv(OUTPUT_JSV, index=False)
    print(f"Saved weighted vectors: {OUTPUT_JSV} ({jsv_weighted.shape})")

    # Save classification details
    with open(OUTPUT_CLASSIFICATION, "w") as f:
        json.dump({
            "tier_totals": dict(tier_stats),
            "problem_jobs_count": len(problem_jobs),
            "problem_by_domain": dict(problem_by_domain),
            "enrichment_details": enrichment_details,
        }, f, indent=2, default=str)
    print(f"Saved classification: {OUTPUT_CLASSIFICATION}")

    # Save domain corrections
    domain_corr_df = pd.DataFrame(job_classifications)
    domain_corr_df.to_csv(OUTPUT_DOMAIN_CORRECTIONS, index=False)
    print(f"Saved domain corrections: {OUTPUT_DOMAIN_CORRECTIONS}")

    # Generate summary
    with open(OUTPUT_REPAIR_SUMMARY, "w", encoding="utf-8") as f:
        f.write("JOB-SKILL MAPPING REPAIR SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total jobs: {len(jsv)}\n")
        f.write(f"Total skill columns: {len(skill_cols)}\n\n")
        f.write("Domain Distribution:\n")
        for domain, count in domain_dist.items():
            f.write(f"  {domain}: {count}\n")
        f.write(f"\nTier Assignments:\n")
        for tier, count in tier_stats.most_common():
            f.write(f"  {tier}: {count}\n")
        f.write(f"\nProblem Jobs (0 core skills): {len(problem_jobs)}\n")
        for domain, count in problem_by_domain.most_common():
            f.write(f"  {domain}: {count}\n")
        f.write(f"\nWeighted Vectors → {OUTPUT_JSV}\n")
        f.write(f"Classification → {OUTPUT_CLASSIFICATION}\n")
        f.write(f"Domain corrections → {OUTPUT_DOMAIN_CORRECTIONS}\n")
    print(f"Saved summary: {OUTPUT_REPAIR_SUMMARY}")

    return jsv_weighted


if __name__ == "__main__":
    repair_job_skill_mappings()
