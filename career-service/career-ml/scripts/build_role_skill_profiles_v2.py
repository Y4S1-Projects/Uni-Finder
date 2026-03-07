#!/usr/bin/env python3
"""
build_role_skill_profiles_v2.py
───────────────────────────────
Generate comprehensive skill profiles for every career role using
the binary job-skill vector matrix.

Inputs
------
  data/processed/job_skill_vectors_v2.csv   – binary matrix (N × 1 154)
  data/expanded/skills_v2.csv               – skill catalogue (1 147 skills)

Outputs
-------
  data/processed/role_skill_profiles_v2.csv – per-role skill rows (~15 000+)
  data/processed/role_summaries.json        – role summary cards (JSON)
  data/reports/role_profile_analytics_v2.txt– analytics report

Usage
-----
  python scripts/build_role_skill_profiles_v2.py                   # full run
  python scripts/build_role_skill_profiles_v2.py --dry-run 500     # first 500 jobs
  python scripts/build_role_skill_profiles_v2.py --min-freq 0.01   # custom freq floor
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
import textwrap
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent          # career-ml/
VECTORS_PATH   = ROOT / "data" / "processed" / "job_skill_vectors_v2.csv"
SKILLS_PATH    = ROOT / "data" / "expanded" / "skills_v2.csv"
OUT_PROFILES   = ROOT / "data" / "processed" / "role_skill_profiles_v2.csv"
OUT_SUMMARIES  = ROOT / "data" / "processed" / "role_summaries.json"
OUT_REPORT     = ROOT / "data" / "reports" / "role_profile_analytics_v2.txt"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
#  Proficiency / category thresholds
# ═════════════════════════════════════════════════════════════════════════════

def proficiency_level(freq: float) -> str:
    """Map frequency → proficiency label."""
    if freq > 0.80:
        return "expert"
    if freq > 0.60:
        return "advanced"
    if freq > 0.40:
        return "intermediate"
    if freq > 0.20:
        return "beginner"
    return "optional"


def skill_category_label(freq: float) -> str:
    """Map frequency → skill-category label for the role."""
    if freq > 0.70:
        return "core"
    if freq > 0.40:
        return "important"
    if freq > 0.20:
        return "nice_to_have"
    return "optional"


# ═════════════════════════════════════════════════════════════════════════════
#  TF-IDF importance
# ═════════════════════════════════════════════════════════════════════════════

def compute_importance(
    role_freq: pd.DataFrame,
    role_ids: list[str],
    skill_cols: list[str],
) -> pd.DataFrame:
    """
    Compute TF-IDF–style importance for every (role, skill) pair.

    TF  = jobs_with_skill_in_role / total_jobs_in_role   (= frequency)
    IDF = log( total_roles / roles_with_this_skill )
    importance = TF * IDF   (normalised to 0-1)
    """
    total_roles = len(role_ids)

    # roles_with_skill: for each skill col, count how many roles have freq > 0
    roles_with_skill = (role_freq > 0).sum(axis=0)          # Series len=n_skills
    # Avoid log(0): clamp minimum to 1
    roles_with_skill = roles_with_skill.clip(lower=1)

    idf = np.log(total_roles / roles_with_skill)            # Series

    # importance = TF * IDF  (element-wise across roles × skills)
    importance = role_freq.multiply(idf, axis=1)

    # Normalise to [0, 1] globally
    imp_max = importance.values.max()
    if imp_max > 0:
        importance = importance / imp_max

    return importance


# ═════════════════════════════════════════════════════════════════════════════
#  Core builder
# ═════════════════════════════════════════════════════════════════════════════

def build_profiles(
    vectors: pd.DataFrame,
    skills_meta: pd.DataFrame,
    min_freq: float = 0.0,
) -> tuple[pd.DataFrame, list[dict], list[str]]:
    """
    Build role-skill profiles + role summary cards.

    Returns:
        profiles_df  – long-form (role × skill) DataFrame
        summaries    – list of role-card dicts
        skill_cols   – skill column names used
    """
    skill_cols = sorted([c for c in vectors.columns if c.startswith("skill_")])
    n_skills = len(skill_cols)
    log.info("Skill columns: %d", n_skills)

    # ── 1. Group by role_id → compute frequency (mean of binary cols) ────
    log.info("Computing per-role skill frequencies …")
    grouped = vectors.groupby("role_id")
    role_freq = grouped[skill_cols].mean()                   # shape: (n_roles, n_skills)
    role_counts = grouped.size().rename("job_count")         # jobs per role
    role_titles = (
        vectors.groupby("role_id")["role_title"]
        .first()
        .to_dict()
    )
    role_ids = sorted(role_freq.index.tolist())
    n_roles = len(role_ids)
    log.info("Roles: %d  |  Jobs per role: %s",
             n_roles,
             ", ".join(f"{r}={role_counts[r]}" for r in role_ids))

    # ── 2. TF-IDF importance ─────────────────────────────────────────────
    log.info("Computing TF-IDF importance scores …")
    importance = compute_importance(role_freq, role_ids, skill_cols)

    # ── 3. Build skill name / category lookup ────────────────────────────
    sid_to_name = dict(zip(skills_meta["skill_id"], skills_meta["name"]))
    sid_to_cat  = dict(zip(skills_meta["skill_id"], skills_meta["category"]))

    def col_to_sid(col: str) -> str:
        """skill_sk001 → SK001"""
        return col.replace("skill_", "").upper()

    # ── 4. Assemble long-form profiles ───────────────────────────────────
    log.info("Assembling long-form profiles …")
    rows: list[dict] = []

    for role in role_ids:
        freqs = role_freq.loc[role]
        imps  = importance.loc[role]
        for col in skill_cols:
            f = float(freqs[col])
            if f < min_freq:
                continue                                     # skip ultra-rare
            sid = col_to_sid(col)
            rows.append({
                "role_id":           role,
                "role_title":        role_titles.get(role, ""),
                "skill_id":          sid,
                "skill_name":        sid_to_name.get(sid, ""),
                "skill_meta_cat":    sid_to_cat.get(sid, ""),
                "frequency":         round(f, 6),
                "importance":        round(float(imps[col]), 6),
                "proficiency_level": proficiency_level(f),
                "skill_category":    skill_category_label(f),
            })

    profiles_df = pd.DataFrame(rows)
    log.info("Profile rows: %d", len(profiles_df))

    # ── 5. Build role summary cards ──────────────────────────────────────
    log.info("Building role summary cards …")
    summaries: list[dict] = []

    # Avg skills per job per role: sum binary cols across each row, then mean per role
    vectors = vectors.copy()
    vectors["_total_skills"] = vectors[skill_cols].sum(axis=1)
    role_avg_skills = vectors.groupby("role_id")["_total_skills"].mean()

    # Top skill categories per role (from the core+important skills)
    for role in role_ids:
        rp = profiles_df[profiles_df["role_id"] == role].copy()
        n_jobs = int(role_counts[role])

        core    = rp[rp["skill_category"] == "core"].sort_values("frequency", ascending=False)
        imp     = rp[rp["skill_category"] == "important"].sort_values("frequency", ascending=False)
        nice    = rp[rp["skill_category"] == "nice_to_have"].sort_values("frequency", ascending=False)

        def skill_labels(subset: pd.DataFrame, limit: int = 30) -> list[str]:
            return [
                f"{r.skill_id}:{r.skill_name}"
                for _, r in subset.head(limit).iterrows()
            ]

        # Top skill meta-categories from core+important skills
        top_cats_pool = pd.concat([core, imp])
        if len(top_cats_pool) > 0:
            top_cats = (
                top_cats_pool["skill_meta_cat"]
                .value_counts()
                .head(5)
                .index.tolist()
            )
        else:
            top_cats = []

        summaries.append({
            "role_id":              role,
            "role_title":           role_titles.get(role, ""),
            "total_jobs_analyzed":  n_jobs,
            "total_skills":         len(rp),
            "core_skills":          skill_labels(core),
            "important_skills":     skill_labels(imp),
            "nice_to_have":         skill_labels(nice, limit=20),
            "core_count":           len(core),
            "important_count":      len(imp),
            "nice_to_have_count":   len(nice),
            "optional_count":       len(rp[rp["skill_category"] == "optional"]),
            "avg_skill_count":      round(float(role_avg_skills.get(role, 0)), 1),
            "top_skill_categories": top_cats,
        })

    # Clean up temp column
    vectors.drop(columns=["_total_skills"], inplace=True, errors="ignore")

    return profiles_df, summaries, skill_cols


# ═════════════════════════════════════════════════════════════════════════════
#  Validation
# ═════════════════════════════════════════════════════════════════════════════

def validate(
    profiles: pd.DataFrame,
    summaries: list[dict],
    input_roles: set[str],
) -> list[str]:
    """Run validation checks; return list of issues."""
    issues: list[str] = []

    # 1. All roles present
    profile_roles = set(profiles["role_id"].unique())
    missing = input_roles - profile_roles
    if missing:
        issues.append(f"MISSING roles in profiles: {missing}")
    else:
        log.info("✓ All %d roles present in profiles", len(input_roles))

    summary_roles = {s["role_id"] for s in summaries}
    missing_s = input_roles - summary_roles
    if missing_s:
        issues.append(f"MISSING roles in summaries: {missing_s}")
    else:
        log.info("✓ All %d roles present in summaries", len(input_roles))

    # 2. Each role has ≥10 skills
    skills_per_role = profiles.groupby("role_id")["skill_id"].count()
    low_roles = skills_per_role[skills_per_role < 10]
    if len(low_roles) > 0:
        issues.append(f"Roles with <10 skills: {dict(low_roles)}")
    else:
        log.info("✓ Every role has ≥10 skills (min=%d)", skills_per_role.min())

    # 3. Importance scores in [0, 1]
    imp_min = profiles["importance"].min()
    imp_max = profiles["importance"].max()
    if imp_min < -0.001 or imp_max > 1.001:
        issues.append(f"Importance out of range: [{imp_min:.4f}, {imp_max:.4f}]")
    else:
        log.info("✓ Importance scores in [0, 1] (range: %.4f–%.4f)", imp_min, imp_max)

    # 4. Frequency in [0, 1]
    f_min = profiles["frequency"].min()
    f_max = profiles["frequency"].max()
    if f_min < -0.001 or f_max > 1.001:
        issues.append(f"Frequency out of range: [{f_min:.4f}, {f_max:.4f}]")
    else:
        log.info("✓ Frequency values in [0, 1] (range: %.6f–%.6f)", f_min, f_max)

    # 5. No NaN in key columns
    for col in ["frequency", "importance", "proficiency_level", "skill_category"]:
        n_na = profiles[col].isna().sum()
        if n_na > 0:
            issues.append(f"NaN in {col}: {n_na}")
    if not any("NaN" in i for i in issues):
        log.info("✓ No NaN in key columns")

    return issues


# ═════════════════════════════════════════════════════════════════════════════
#  Analytics report
# ═════════════════════════════════════════════════════════════════════════════

def generate_report(
    profiles: pd.DataFrame,
    summaries: list[dict],
    skill_cols: list[str],
) -> str:
    """Build a multi-section analytics report string."""
    lines: list[str] = []
    sep = "=" * 78

    lines.append(sep)
    lines.append("  ROLE SKILL PROFILE ANALYTICS  (v2)")
    lines.append(sep)
    lines.append("")

    n_roles = profiles["role_id"].nunique()
    n_rows  = len(profiles)
    n_skills_used = profiles["skill_id"].nunique()

    # ── 1. Overview ───────────────────────────────────────────────────────
    lines.append("─── 1. OVERVIEW ──────────────────────────────────────────────")
    lines.append(f"  Roles:              {n_roles}")
    lines.append(f"  Total profile rows: {n_rows:,}")
    lines.append(f"  Unique skills used: {n_skills_used:,}")
    lines.append(f"  Skill columns:      {len(skill_cols):,}")
    lines.append("")

    # ── 2. Role breakdown ────────────────────────────────────────────────
    lines.append("─── 2. ROLE BREAKDOWN ───────────────────────────────────────")
    lines.append(f"  {'Role ID':<22} {'Title':<35} {'Jobs':>6} {'Skills':>7} "
                 f"{'Core':>5} {'Imp':>5} {'Nice':>5} {'Opt':>5} {'AvgSk':>6}")
    lines.append(f"  {'─'*22} {'─'*35} {'─'*6} {'─'*7} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*6}")
    for s in sorted(summaries, key=lambda x: x["total_jobs_analyzed"], reverse=True):
        lines.append(
            f"  {s['role_id']:<22} {s['role_title']:<35} "
            f"{s['total_jobs_analyzed']:>6} {s['total_skills']:>7} "
            f"{s['core_count']:>5} {s['important_count']:>5} "
            f"{s['nice_to_have_count']:>5} {s['optional_count']:>5} "
            f"{s['avg_skill_count']:>6.1f}"
        )
    lines.append("")

    # ── 3. Proficiency distribution ──────────────────────────────────────
    lines.append("─── 3. PROFICIENCY LEVEL DISTRIBUTION ───────────────────────")
    prof_dist = profiles["proficiency_level"].value_counts()
    for lvl in ["expert", "advanced", "intermediate", "beginner", "optional"]:
        cnt = prof_dist.get(lvl, 0)
        pct = cnt / n_rows * 100
        lines.append(f"  {lvl:<15} {cnt:>7,}  ({pct:>5.1f}%)")
    lines.append("")

    # ── 4. Skill category distribution ───────────────────────────────────
    lines.append("─── 4. SKILL CATEGORY DISTRIBUTION ────────────────────────")
    cat_dist = profiles["skill_category"].value_counts()
    for cat in ["core", "important", "nice_to_have", "optional"]:
        cnt = cat_dist.get(cat, 0)
        pct = cnt / n_rows * 100
        lines.append(f"  {cat:<15} {cnt:>7,}  ({pct:>5.1f}%)")
    lines.append("")

    # ── 5. Top importance skills (global) ────────────────────────────────
    lines.append("─── 5. HIGHEST IMPORTANCE SKILLS (top 20 globally) ─────────")
    top_imp = profiles.nlargest(20, "importance")
    lines.append(f"  {'Role':<22} {'Skill':<30} {'Freq':>6} {'Imp':>6} {'Prof':<13}")
    lines.append(f"  {'─'*22} {'─'*30} {'─'*6} {'─'*6} {'─'*13}")
    for _, r in top_imp.iterrows():
        lines.append(
            f"  {r.role_id:<22} {r.skill_name:<30} "
            f"{r.frequency:>6.3f} {r.importance:>6.3f} {r.proficiency_level:<13}"
        )
    lines.append("")

    # ── 6. Core skills per role (top 10 each) ────────────────────────────
    lines.append("─── 6. CORE SKILLS PER ROLE (top 10 by frequency) ──────────")
    for role in sorted(profiles["role_id"].unique()):
        rp = profiles[(profiles["role_id"] == role) & (profiles["skill_category"] == "core")]
        rp = rp.sort_values("frequency", ascending=False).head(10)
        if len(rp) == 0:
            skill_str = "(no core skills)"
        else:
            skill_str = ", ".join(
                f"{r.skill_name} ({r.frequency:.0%})"
                for _, r in rp.iterrows()
            )
        lines.append(f"  {role:<22} → {skill_str}")
    lines.append("")

    # ── 7. Importance distribution stats ─────────────────────────────────
    lines.append("─── 7. IMPORTANCE SCORE STATISTICS ──────────────────────────")
    imp = profiles["importance"]
    lines.append(f"  Min:    {imp.min():.6f}")
    lines.append(f"  Max:    {imp.max():.6f}")
    lines.append(f"  Mean:   {imp.mean():.6f}")
    lines.append(f"  Median: {imp.median():.6f}")
    lines.append(f"  Std:    {imp.std():.6f}")
    lines.append("")

    # ── 8. Frequency distribution stats ──────────────────────────────────
    lines.append("─── 8. FREQUENCY STATISTICS ────────────────────────────────")
    freq = profiles["frequency"]
    lines.append(f"  Min:    {freq.min():.6f}")
    lines.append(f"  Max:    {freq.max():.6f}")
    lines.append(f"  Mean:   {freq.mean():.6f}")
    lines.append(f"  Median: {freq.median():.6f}")
    lines.append(f"  Std:    {freq.std():.6f}")
    lines.append("")

    # ── 9. Skill meta-category representation per role ───────────────────
    lines.append("─── 9. TOP SKILL CATEGORIES PER ROLE ──────────────────────")
    for s in sorted(summaries, key=lambda x: x["role_id"]):
        cats = ", ".join(s["top_skill_categories"]) if s["top_skill_categories"] else "(none)"
        lines.append(f"  {s['role_id']:<22} → {cats}")
    lines.append("")

    lines.append(sep)
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Build role skill profiles v2")
    parser.add_argument(
        "--dry-run", type=int, default=0, metavar="N",
        help="Process only first N jobs (for testing)",
    )
    parser.add_argument(
        "--min-freq", type=float, default=0.0, metavar="F",
        help="Minimum frequency threshold to include a skill (default: 0.0 = keep all)",
    )
    args = parser.parse_args()

    t_start = time.perf_counter()

    # ── Load data ─────────────────────────────────────────────────────────
    log.info("Loading skill catalogue: %s", SKILLS_PATH)
    skills_meta = pd.read_csv(SKILLS_PATH)
    log.info("  → %d skills loaded", len(skills_meta))

    log.info("Loading job-skill vectors: %s", VECTORS_PATH)
    if args.dry_run > 0:
        vectors = pd.read_csv(VECTORS_PATH, nrows=args.dry_run)
        log.info("  → DRY-RUN: %d jobs loaded", len(vectors))
    else:
        vectors = pd.read_csv(VECTORS_PATH)
        log.info("  → %d jobs loaded", len(vectors))

    input_roles = set(vectors["role_id"].unique())

    # ── Build profiles ────────────────────────────────────────────────────
    profiles, summaries, skill_cols = build_profiles(
        vectors, skills_meta, min_freq=args.min_freq
    )

    # ── Validate ──────────────────────────────────────────────────────────
    log.info("Running validation …")
    issues = validate(profiles, summaries, input_roles)
    if issues:
        for iss in issues:
            log.error("VALIDATION FAIL: %s", iss)
    else:
        log.info("All validation checks PASSED ✓")

    # ── Save profiles CSV ─────────────────────────────────────────────────
    OUT_PROFILES.parent.mkdir(parents=True, exist_ok=True)
    log.info("Saving profiles → %s", OUT_PROFILES)
    profiles.to_csv(OUT_PROFILES, index=False)
    size_mb = OUT_PROFILES.stat().st_size / 1024 / 1024
    log.info("  → saved (%.1f MB, %d rows)", size_mb, len(profiles))

    # ── Save summaries JSON ───────────────────────────────────────────────
    OUT_SUMMARIES.parent.mkdir(parents=True, exist_ok=True)
    log.info("Saving role summaries → %s", OUT_SUMMARIES)
    with open(OUT_SUMMARIES, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    log.info("  → %d role cards saved", len(summaries))

    # ── Analytics report ──────────────────────────────────────────────────
    log.info("Generating analytics report …")
    report = generate_report(profiles, summaries, skill_cols)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(report, encoding="utf-8")
    log.info("Report saved → %s", OUT_REPORT)

    # ── Summary ───────────────────────────────────────────────────────────
    elapsed = time.perf_counter() - t_start
    print()
    print("=" * 78)
    print(textwrap.dedent(f"""\
        COMPLETE — Role Skill Profiles v2
          Roles:          {len(summaries)}
          Profile rows:   {len(profiles):,}
          Unique skills:  {profiles['skill_id'].nunique():,}
          File size:      {size_mb:.1f} MB
          Elapsed:        {elapsed:.1f}s
          Profiles:       {OUT_PROFILES}
          Summaries:      {OUT_SUMMARIES}
          Report:         {OUT_REPORT}
    """))
    print("=" * 78)

    # Print report to console too
    print(report)


if __name__ == "__main__":
    main()
