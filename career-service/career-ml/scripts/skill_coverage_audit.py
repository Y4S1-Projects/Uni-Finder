#!/usr/bin/env python3
"""
skill_coverage_audit.py — Generate Detailed Skill Coverage Reports
====================================================================
Outputs:
  1. skill_coverage_report.json   — full machine-readable report
  2. skill_coverage_summary.txt   — human-readable summary
  3. orphan_skills.csv            — skills with zero job mappings
  4. weak_skills.csv              — skills mapped to < 5 jobs
  5. near_duplicates.csv          — potential near-duplicate skill pairs
  6. domain_coverage.csv          — domain coverage gaps

Run:
    cd career-service/career-ml
    python scripts/skill_coverage_audit.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np

# Add scripts dir to path for import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_normalizer import SkillNormalizer, DOMAIN_SKILL_CLUSTERS, GENERIC_SOFT_SKILLS

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # career-ml/
DATA_DIR = BASE_DIR / "data"
EXPANDED = DATA_DIR / "expanded"
PROCESSED = DATA_DIR / "processed"
REPORTS = DATA_DIR / "reports"
REPORTS.mkdir(exist_ok=True)

SKILLS_CSV = EXPANDED / "skills_v2.csv"
JSV_CSV = PROCESSED / "job_skill_vectors_v2_fixed.csv"
ROLE_PROFILES = PROCESSED / "role_skill_profiles_v2_fixed.csv"
ENHANCED_FEATURES = PROCESSED / "jobs_enhanced_features.csv"
ENHANCED_VECTORS = PROCESSED / "job_feature_vectors_enhanced.csv"
ENHANCED_COLUMNS = PROCESSED / "enhanced_feature_columns.json"


def run_audit():
    print("=" * 70)
    print("SKILL COVERAGE AUDIT")
    print("=" * 70)

    # Load data
    normalizer = SkillNormalizer(SKILLS_CSV)
    jsv = pd.read_csv(JSV_CSV)
    skill_cols = [c for c in jsv.columns if c.startswith("skill_")]
    print(f"\nLoaded: {len(jsv)} jobs, {len(skill_cols)} skill columns")

    report = {}

    # ─── 1. Orphan Skills (mapped to 0 jobs) ─────────────────────────
    print("\n--- 1. Orphan Skills ---")
    orphans = []
    weak_skills = []
    coverage = {}

    for col in skill_cols:
        sid = col.replace("skill_", "").upper()
        count = int(jsv[col].sum())
        name = normalizer.id_to_name.get(sid, "?")
        category = normalizer.id_to_category.get(sid, "?")
        stype = normalizer.id_to_type.get(sid, "?")
        domains = list(normalizer.get_domains_for_skill(sid))

        coverage[sid] = {
            "name": name,
            "job_count": count,
            "category": category,
            "type": stype,
            "domains": domains,
        }

        if count == 0:
            orphans.append({"skill_id": sid, "name": name, "category": category,
                            "type": stype, "domains": ", ".join(domains)})
        elif count <= 4:
            weak_skills.append({"skill_id": sid, "name": name, "category": category,
                                "type": stype, "job_count": count,
                                "domains": ", ".join(domains)})

    orphans_df = pd.DataFrame(orphans).sort_values("category") if orphans else pd.DataFrame()
    weak_df = pd.DataFrame(weak_skills).sort_values("job_count") if weak_skills else pd.DataFrame()

    orphans_df.to_csv(REPORTS / "orphan_skills.csv", index=False)
    weak_df.to_csv(REPORTS / "weak_skills.csv", index=False)

    print(f"  Orphan skills (0 jobs):  {len(orphans)}")
    print(f"  Weak skills (1-4 jobs):  {len(weak_skills)}")
    print(f"  Well-mapped (5+ jobs):   {len(skill_cols) - len(orphans) - len(weak_skills)}")

    report["orphan_count"] = len(orphans)
    report["weak_count"] = len(weak_skills)
    report["well_mapped_count"] = len(skill_cols) - len(orphans) - len(weak_skills)

    # ─── 2. Near Duplicates ──────────────────────────────────────────
    print("\n--- 2. Near Duplicates ---")
    dupes = normalizer.get_near_duplicates()
    dupes_df = pd.DataFrame(dupes) if dupes else pd.DataFrame()
    dupes_df.to_csv(REPORTS / "near_duplicates.csv", index=False)
    print(f"  Found {len(dupes)} near-duplicate pairs")
    for d in dupes[:10]:
        print(f"    {d['skill_1']}({d['name_1']}) ↔ {d['skill_2']}({d['name_2']})")
    report["near_duplicate_pairs"] = len(dupes)

    # ─── 3. Generic/Soft Skill Overlap Check ─────────────────────────
    print("\n--- 3. Generic/Soft Skill Check ---")
    generic_in_dataset = []
    for sid in normalizer.id_to_name:
        if normalizer.is_generic_soft_skill(sid):
            jcount = coverage.get(sid, {}).get("job_count", 0)
            generic_in_dataset.append({
                "skill_id": sid,
                "name": normalizer.id_to_name[sid],
                "job_count": jcount,
            })
    print(f"  {len(generic_in_dataset)} generic/soft skills in dataset")
    top_generic = sorted(generic_in_dataset, key=lambda x: x["job_count"], reverse=True)[:10]
    for g in top_generic:
        print(f"    {g['skill_id']} ({g['name']}): {g['job_count']} jobs")
    report["generic_soft_count"] = len(generic_in_dataset)

    # ─── 4. Domain Coverage Analysis ─────────────────────────────────
    print("\n--- 4. Domain Coverage Analysis ---")
    domain_cov = []

    for domain, cluster in DOMAIN_SKILL_CLUSTERS.items():
        core_names = cluster.get("core", [])
        supporting_names = cluster.get("supporting", [])
        all_names = core_names + supporting_names

        resolved_core = 0
        resolved_supporting = 0
        total_core_jobs = 0
        total_supporting_jobs = 0
        missing_core = []
        missing_supporting = []

        for sname in core_names:
            sid = normalizer.resolve_skill_name(sname)
            if sid:
                resolved_core += 1
                total_core_jobs += coverage.get(sid, {}).get("job_count", 0)
            else:
                missing_core.append(sname)

        for sname in supporting_names:
            sid = normalizer.resolve_skill_name(sname)
            if sid:
                resolved_supporting += 1
                total_supporting_jobs += coverage.get(sid, {}).get("job_count", 0)
            else:
                missing_supporting.append(sname)

        entry = {
            "domain": domain,
            "core_defined": len(core_names),
            "core_resolved": resolved_core,
            "core_missing": len(missing_core),
            "core_total_jobs": total_core_jobs,
            "supporting_defined": len(supporting_names),
            "supporting_resolved": resolved_supporting,
            "supporting_missing": len(missing_supporting),
            "supporting_total_jobs": total_supporting_jobs,
            "missing_core_skills": ", ".join(missing_core) if missing_core else "",
            "missing_supporting_skills": ", ".join(missing_supporting) if missing_supporting else "",
        }
        domain_cov.append(entry)
        print(f"\n  {domain}:")
        print(f"    Core: {resolved_core}/{len(core_names)} resolved, "
              f"{total_core_jobs} total job appearances")
        print(f"    Supporting: {resolved_supporting}/{len(supporting_names)} resolved, "
              f"{total_supporting_jobs} total job appearances")
        if missing_core:
            print(f"    Missing core: {missing_core}")
        if missing_supporting:
            print(f"    Missing supporting: {missing_supporting}")

    domain_cov_df = pd.DataFrame(domain_cov)
    domain_cov_df.to_csv(REPORTS / "domain_coverage.csv", index=False)
    report["domain_coverage"] = domain_cov

    # ─── 5. Enhanced Feature Staleness Check ─────────────────────────
    print("\n--- 5. Enhanced Feature Staleness ---")
    enhanced_stale = False
    if ENHANCED_COLUMNS.exists():
        with open(ENHANCED_COLUMNS) as f:
            meta = json.load(f)
        enh_skill_cols = meta.get("skill_columns", [])
        enh_domain_vals = meta.get("domain_values", [])
        print(f"  Enhanced skill dims: {len(enh_skill_cols)}")
        print(f"  Enhanced domain vals: {enh_domain_vals}")
        print(f"  Current skill cols:  {len(skill_cols)}")
        if len(enh_skill_cols) < len(skill_cols):
            print(f"  *** STALE: Enhanced uses {len(enh_skill_cols)}, "
                  f"current has {len(skill_cols)} skills ***")
            enhanced_stale = True
        report["enhanced_skill_dims"] = len(enh_skill_cols)
        report["enhanced_domain_vals"] = enh_domain_vals
    else:
        print("  Enhanced feature columns JSON not found!")
        enhanced_stale = True

    report["enhanced_stale"] = enhanced_stale

    # ─── 6. Role Profile Coverage ─────────────────────────────────────
    print("\n--- 6. Role Profile Coverage ---")
    if ROLE_PROFILES.exists():
        rp = pd.read_csv(ROLE_PROFILES)

        # Detect format: long (role_id, skill_id, ...) or wide (skill_sk001, ...)
        rp_skill_cols = [c for c in rp.columns if c.startswith("skill_")]
        is_wide = len(rp_skill_cols) > 10  # wide format has many skill_ columns

        if is_wide:
            roles_with_profiles = rp.shape[0]
            print(f"  Role profiles (wide): {roles_with_profiles} roles x {len(rp_skill_cols)} skill dims")
            # Check for role profiles with very few non-zero skills
            rp_numeric = rp[rp_skill_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            nonzero_per_role = rp_numeric.gt(0).sum(axis=1)
            thin_roles = rp[nonzero_per_role < 10]
            print(f"  Roles with < 10 non-zero skills: {len(thin_roles)}")
            if len(thin_roles) > 0:
                for _, tr in thin_roles.iterrows():
                    role = tr.get("role_id", "unknown")
                    nz = int(nonzero_per_role.loc[tr.name])
                    print(f"    {role}: {nz} non-zero skills")
            report["role_profile_count"] = roles_with_profiles
            report["role_profile_skill_dims"] = len(rp_skill_cols)
            report["thin_role_count"] = len(thin_roles)
        else:
            # Long format: role_id, skill_id, frequency, importance
            roles_unique = rp["role_id"].unique()
            skills_per_role = rp.groupby("role_id")["skill_id"].count()
            print(f"  Role profiles (long): {len(roles_unique)} unique roles")
            print(f"  Skills per role: mean={skills_per_role.mean():.1f}, "
                  f"min={skills_per_role.min()}, max={skills_per_role.max()}")
            thin_roles = skills_per_role[skills_per_role < 10]
            print(f"  Roles with < 10 skills: {len(thin_roles)}")
            if len(thin_roles) > 0:
                for role_id, count in thin_roles.items():
                    print(f"    {role_id}: {count} skills")
            report["role_profile_count"] = len(roles_unique)
            report["role_profile_format"] = "long"
            report["thin_role_count"] = len(thin_roles)
    else:
        print("  Role profiles file not found!")
        report["role_profile_count"] = 0

    # ─── 7. Skill Distribution Statistics ─────────────────────────────
    print("\n--- 7. Skill Distribution Statistics ---")
    job_counts = jsv[skill_cols].sum(axis=0)
    skills_per_job = jsv[skill_cols].sum(axis=1)

    stats = {
        "total_skills": len(skill_cols),
        "total_jobs": len(jsv),
        "avg_jobs_per_skill": round(float(job_counts.mean()), 1),
        "median_jobs_per_skill": round(float(job_counts.median()), 1),
        "max_jobs_per_skill": int(job_counts.max()),
        "min_jobs_per_skill": int(job_counts.min()),
        "avg_skills_per_job": round(float(skills_per_job.mean()), 1),
        "median_skills_per_job": round(float(skills_per_job.median()), 1),
        "max_skills_per_job": int(skills_per_job.max()),
        "min_skills_per_job": int(skills_per_job.min()),
    }
    for k, v in stats.items():
        print(f"  {k}: {v}")
    report["statistics"] = stats

    # ─── 8. Category Distribution ─────────────────────────────────────
    print("\n--- 8. Skill Category Distribution ---")
    cat_dist = Counter()
    type_dist = Counter()
    for sid in normalizer.id_to_name:
        cat_dist[normalizer.id_to_category.get(sid, "unknown")] += 1
        type_dist[normalizer.id_to_type.get(sid, "unknown")] += 1

    print("  Categories:")
    for cat, count in cat_dist.most_common():
        print(f"    {cat}: {count}")
    print(f"\n  Types: {dict(type_dist)}")
    report["category_distribution"] = dict(cat_dist)
    report["type_distribution"] = dict(type_dist)

    # ─── Save Full Report ─────────────────────────────────────────────
    report_json_path = REPORTS / "skill_coverage_report.json"
    with open(report_json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n\nSaved full report: {report_json_path}")

    # ─── Generate Summary Text ────────────────────────────────────────
    summary_path = REPORTS / "skill_coverage_summary.txt"
    with open(summary_path, "w") as f:
        f.write("SKILL COVERAGE AUDIT SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Skills: {len(skill_cols)}\n")
        f.write(f"Total Jobs:   {len(jsv)}\n\n")
        f.write(f"Orphan Skills (0 jobs):      {len(orphans)}\n")
        f.write(f"Weak Skills (1-4 jobs):      {len(weak_skills)}\n")
        f.write(f"Well-Mapped (5+ jobs):       {len(skill_cols) - len(orphans) - len(weak_skills)}\n")
        f.write(f"Near-Duplicate Pairs:        {len(dupes)}\n")
        f.write(f"Generic/Soft Skills:         {len(generic_in_dataset)}\n")
        f.write(f"Enhanced Features Stale:     {'YES' if enhanced_stale else 'NO'}\n\n")
        f.write("Domain Coverage:\n")
        f.write("-" * 50 + "\n")
        for dc in domain_cov:
            f.write(f"  {dc['domain']}:\n")
            f.write(f"    Core:       {dc['core_resolved']}/{dc['core_defined']} resolved, "
                    f"{dc['core_total_jobs']} job appearances\n")
            f.write(f"    Supporting: {dc['supporting_resolved']}/{dc['supporting_defined']} resolved, "
                    f"{dc['supporting_total_jobs']} job appearances\n")
            if dc['missing_core_skills']:
                f.write(f"    MISSING CORE: {dc['missing_core_skills']}\n")
            if dc['missing_supporting_skills']:
                f.write(f"    MISSING SUPPORTING: {dc['missing_supporting_skills']}\n")
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"Skills per job: mean={stats['avg_skills_per_job']}, "
                f"min={stats['min_skills_per_job']}, max={stats['max_skills_per_job']}\n")
        f.write(f"Jobs per skill: mean={stats['avg_jobs_per_skill']}, "
                f"min={stats['min_jobs_per_skill']}, max={stats['max_jobs_per_skill']}\n")

    print(f"Saved summary:  {summary_path}")
    print(f"\nAll audit reports written to: {REPORTS}")

    return report


if __name__ == "__main__":
    run_audit()
