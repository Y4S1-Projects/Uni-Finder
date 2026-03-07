#!/usr/bin/env python3
"""
build_job_skill_vectors_v2.py
─────────────────────────────
Create binary skill-vector matrix for every job using the expanded skill set.

Inputs
------
  data/processed/jobs_tagged_v2.csv   – jobs with matched_skill_ids (;-separated)
  data/expanded/skills_v2.csv         – master skill catalogue (SK001-SK1147)

Outputs
-------
  data/processed/job_skill_vectors_v2.csv           – full matrix (N×(7+S))
  data/reports/skill_vector_analytics_v2.txt        – analytics report

Dimensions
----------
  ~15 000 rows  ×  (7 metadata + 1 147 skill columns)  =  ~1 154 columns

Usage
-----
  python scripts/build_job_skill_vectors_v2.py                 # full run
  python scripts/build_job_skill_vectors_v2.py --dry-run 100   # quick test on 100 rows
  python scripts/build_job_skill_vectors_v2.py --sparse         # use pandas Sparse dtype
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
import textwrap
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent          # career-ml/
JOBS_PATH = ROOT / "data" / "processed" / "jobs_tagged_v2.csv"
SKILLS_PATH = ROOT / "data" / "expanded" / "skills_v2.csv"
OUT_VECTORS = ROOT / "data" / "processed" / "job_skill_vectors_v2.csv"
OUT_REPORT = ROOT / "data" / "reports" / "skill_vector_analytics_v2.txt"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── Metadata columns to keep ────────────────────────────────────────────────
META_COLS = [
    "job_uid",
    "job_title",
    "job_title_clean",
    "role_id",
    "role_title",
    "job_category",
    "seniority_level",
]


# ═════════════════════════════════════════════════════════════════════════════
#  Helpers
# ═════════════════════════════════════════════════════════════════════════════

def clean_title(title: str) -> str:
    """Normalise a job title: lowercase, strip brackets / special chars,
    collapse whitespace."""
    if not isinstance(title, str):
        return ""
    t = title.lower().strip()
    # remove content in parentheses / brackets
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    # strip non-alpha except spaces and hyphens
    t = re.sub(r"[^a-z0-9 \-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_skill_ids(raw: str) -> set[str]:
    """Parse 'SK001;SK015;SK234' → {'SK001', 'SK015', 'SK234'}."""
    if not isinstance(raw, str) or raw.strip() == "":
        return set()
    # Accept both ; and , separators
    return {tok.strip().upper() for tok in re.split(r"[;,]", raw) if tok.strip()}


# ═════════════════════════════════════════════════════════════════════════════
#  Core builder
# ═════════════════════════════════════════════════════════════════════════════

def build_vectors(
    jobs: pd.DataFrame,
    skills: pd.DataFrame,
    use_sparse: bool = False,
) -> pd.DataFrame:
    """Build the binary skill-vector matrix."""

    # --- 1. Skill catalogue: sorted list of all skill IDs ─────────────────
    all_skill_ids: list[str] = sorted(skills["skill_id"].unique())
    n_skills = len(all_skill_ids)
    log.info("Skill catalogue: %d unique IDs", n_skills)

    # Map SK??? → positional index for fast lookup
    sid_to_idx: dict[str, int] = {sid: i for i, sid in enumerate(all_skill_ids)}

    # Column names: skill_sk001, skill_sk002, …
    skill_col_names = [f"skill_{sid.lower()}" for sid in all_skill_ids]

    # --- 2. Parse matched_skill_ids per job ───────────────────────────────
    log.info("Parsing matched_skill_ids …")
    parsed_ids: list[set[str]] = [
        parse_skill_ids(val) for val in jobs["matched_skill_ids"].values
    ]

    # --- 3. Build the binary matrix ───────────────────────────────────────
    n_jobs = len(jobs)
    log.info("Building %d × %d binary matrix …", n_jobs, n_skills)

    t0 = time.perf_counter()
    # Allocate a dense uint8 matrix (15k × 1.2k ≈ 17 MB — very manageable)
    mat = np.zeros((n_jobs, n_skills), dtype=np.uint8)

    unknown_ids: set[str] = set()
    for row_i, sids in enumerate(parsed_ids):
        for sid in sids:
            idx = sid_to_idx.get(sid)
            if idx is not None:
                mat[row_i, idx] = 1
            else:
                unknown_ids.add(sid)

    elapsed = time.perf_counter() - t0
    log.info("Matrix built in %.2fs", elapsed)

    if unknown_ids:
        log.warning(
            "%d unknown skill IDs encountered (not in skills_v2): %s",
            len(unknown_ids),
            ", ".join(sorted(unknown_ids)[:20]),
        )

    # --- 4. Convert to DataFrame ──────────────────────────────────────────
    if use_sparse:
        log.info("Converting to Sparse[uint8] dtype …")
        skill_df = pd.DataFrame.sparse.from_spmatrix(
            __import__("scipy").sparse.csr_matrix(mat),
            columns=skill_col_names,
        )
        # Sparse dtype keeps ~98% zeros compressed in memory
    else:
        skill_df = pd.DataFrame(mat, columns=skill_col_names)

    # --- 5. Build job_title_clean if not present ──────────────────────────
    if "job_title_clean" not in jobs.columns:
        log.info("Generating job_title_clean …")
        jobs = jobs.copy()
        jobs["job_title_clean"] = jobs["job_title"].apply(clean_title)

    # --- 6. Assemble final output ─────────────────────────────────────────
    meta_df = jobs[META_COLS].reset_index(drop=True)
    result = pd.concat([meta_df, skill_df], axis=1)

    return result, all_skill_ids, skill_col_names, unknown_ids


# ═════════════════════════════════════════════════════════════════════════════
#  Validation
# ═════════════════════════════════════════════════════════════════════════════

def validate(df: pd.DataFrame, skill_cols: list[str], n_input_jobs: int) -> list[str]:
    """Run validation checks; return list of issues (empty = all good)."""
    issues: list[str] = []

    # 1. All skill columns present
    missing_cols = [c for c in skill_cols if c not in df.columns]
    if missing_cols:
        issues.append(f"MISSING {len(missing_cols)} skill columns: {missing_cols[:5]}")
    else:
        log.info("✓ All %d skill columns present", len(skill_cols))

    # 2. No missing values in skill columns
    n_na = df[skill_cols].isna().sum().sum()
    if n_na > 0:
        issues.append(f"FOUND {n_na} NaN values in skill columns")
    else:
        log.info("✓ Zero NaN values in skill matrix")

    # 3. Binary values only
    uniq_vals = set()
    for c in skill_cols:
        uniq_vals.update(df[c].unique())
    non_binary = uniq_vals - {0, 1}
    if non_binary:
        issues.append(f"NON-BINARY values found: {non_binary}")
    else:
        log.info("✓ All skill values are binary (0/1)")

    # 4. Row count matches input
    if len(df) != n_input_jobs:
        issues.append(f"ROW MISMATCH: output {len(df)} vs input {n_input_jobs}")
    else:
        log.info("✓ Row count matches input: %d", len(df))

    # 5. At least 1 skill per job (sanity)
    row_sums = df[skill_cols].sum(axis=1)
    zero_skill_jobs = (row_sums == 0).sum()
    if zero_skill_jobs > 0:
        issues.append(f"{zero_skill_jobs} jobs have ZERO skills tagged")
    else:
        log.info("✓ Every job has ≥1 skill")

    return issues


# ═════════════════════════════════════════════════════════════════════════════
#  Analytics
# ═════════════════════════════════════════════════════════════════════════════

def generate_analytics(
    df: pd.DataFrame,
    skill_cols: list[str],
    all_skill_ids: list[str],
    skills_meta: pd.DataFrame,
) -> str:
    """Return a multi-section analytics report as a string."""

    lines: list[str] = []
    sep = "=" * 78

    lines.append(sep)
    lines.append("  JOB-SKILL VECTOR ANALYTICS  (v2)")
    lines.append(sep)
    lines.append("")

    n_jobs, n_skills = len(df), len(skill_cols)
    total_cells = n_jobs * n_skills
    ones = df[skill_cols].values.sum()
    zeros = total_cells - ones

    # ── 1. Overview ───────────────────────────────────────────────────────
    lines.append("─── 1. OVERVIEW ──────────────────────────────────────────────")
    lines.append(f"  Jobs:              {n_jobs:,}")
    lines.append(f"  Skills:            {n_skills:,}")
    lines.append(f"  Total matrix cells:{total_cells:,}")
    lines.append(f"  Ones (1):          {ones:,}")
    lines.append(f"  Zeros (0):         {zeros:,}")
    lines.append("")

    # ── 2. Sparsity ──────────────────────────────────────────────────────
    sparsity = zeros / total_cells * 100
    density = ones / total_cells * 100
    lines.append("─── 2. SPARSITY ─────────────────────────────────────────────")
    lines.append(f"  Sparsity (% zeros): {sparsity:.2f}%")
    lines.append(f"  Density  (% ones):  {density:.2f}%")
    lines.append("")

    # ── 3. Skills per job ────────────────────────────────────────────────
    row_sums = df[skill_cols].sum(axis=1)
    lines.append("─── 3. SKILLS PER JOB ───────────────────────────────────────")
    lines.append(f"  Min:    {row_sums.min()}")
    lines.append(f"  Max:    {row_sums.max()}")
    lines.append(f"  Mean:   {row_sums.mean():.1f}")
    lines.append(f"  Median: {row_sums.median():.0f}")
    lines.append(f"  Std:    {row_sums.std():.1f}")
    lines.append("")

    # ── 4. Most common skills (top 30) ───────────────────────────────────
    col_sums = df[skill_cols].sum(axis=0).sort_values(ascending=False)
    sid_name_map = dict(zip(
        skills_meta["skill_id"].str.lower().apply(lambda x: f"skill_{x}"),
        skills_meta["name"],
    ))

    lines.append("─── 4. MOST COMMON SKILLS (top 30) ─────────────────────────")
    lines.append(f"  {'Rank':<5} {'Skill ID':<12} {'Name':<35} {'Jobs':>7} {'%':>7}")
    lines.append(f"  {'─'*5} {'─'*12} {'─'*35} {'─'*7} {'─'*7}")
    for rank, (col, count) in enumerate(col_sums.head(30).items(), 1):
        pct = count / n_jobs * 100
        name = sid_name_map.get(col, "?")
        sid = col.replace("skill_", "").upper()
        lines.append(f"  {rank:<5} {sid:<12} {name:<35} {count:>7,} {pct:>6.1f}%")
    lines.append("")

    # ── 5. Least common skills (bottom 30) ───────────────────────────────
    lines.append("─── 5. LEAST COMMON SKILLS (bottom 30) ────────────────────")
    lines.append(f"  {'Rank':<5} {'Skill ID':<12} {'Name':<35} {'Jobs':>7} {'%':>7}")
    lines.append(f"  {'─'*5} {'─'*12} {'─'*35} {'─'*7} {'─'*7}")
    bottom = col_sums.tail(30).sort_values(ascending=True)
    for rank, (col, count) in enumerate(bottom.items(), 1):
        pct = count / n_jobs * 100
        name = sid_name_map.get(col, "?")
        sid = col.replace("skill_", "").upper()
        lines.append(f"  {rank:<5} {sid:<12} {name:<35} {count:>7,} {pct:>6.1f}%")
    lines.append("")

    # ── 6. Zero-frequency skills ─────────────────────────────────────────
    zero_skills = (col_sums == 0).sum()
    lines.append("─── 6. ZERO-FREQUENCY SKILLS ─────────────────────────────")
    lines.append(f"  Skills with ZERO jobs: {zero_skills}")
    if zero_skills > 0 and zero_skills <= 50:
        for col in col_sums[col_sums == 0].index:
            name = sid_name_map.get(col, "?")
            sid = col.replace("skill_", "").upper()
            lines.append(f"    {sid}: {name}")
    elif zero_skills > 50:
        lines.append(f"  (showing first 50)")
        for col in list(col_sums[col_sums == 0].index)[:50]:
            name = sid_name_map.get(col, "?")
            sid = col.replace("skill_", "").upper()
            lines.append(f"    {sid}: {name}")
    lines.append("")

    # ── 7. Skill distribution by job category ────────────────────────────
    lines.append("─── 7. SKILL DISTRIBUTION BY JOB CATEGORY ────────────────")
    if "job_category" in df.columns:
        cat_groups = df.groupby("job_category")[skill_cols].mean()
        lines.append(f"  {'Category':<16} {'Avg Skills':>11} {'Density':>9}")
        lines.append(f"  {'─'*16} {'─'*11} {'─'*9}")
        for cat in sorted(cat_groups.index):
            avg_skills = cat_groups.loc[cat].sum()            # sum of means = avg skills per job
            dens = cat_groups.loc[cat].mean() * 100           # mean across all skill cols
            lines.append(f"  {cat:<16} {avg_skills:>11.1f} {dens:>8.2f}%")
    else:
        lines.append("  (job_category column not found)")
    lines.append("")

    # ── 8. Skill distribution by seniority level ─────────────────────────
    lines.append("─── 8. SKILL DISTRIBUTION BY SENIORITY LEVEL ─────────────")
    if "seniority_level" in df.columns:
        sen_groups = df.groupby("seniority_level")[skill_cols].mean()
        lines.append(f"  {'Level':<14} {'Avg Skills':>11} {'Density':>9}")
        lines.append(f"  {'─'*14} {'─'*11} {'─'*9}")
        for lvl in sorted(sen_groups.index):
            avg_skills = sen_groups.loc[lvl].sum()
            dens = sen_groups.loc[lvl].mean() * 100
            lines.append(f"  {lvl:<14} {avg_skills:>11.1f} {dens:>8.2f}%")
    else:
        lines.append("  (seniority_level column not found)")
    lines.append("")

    # ── 9. Top skills per category (top 5 each) ─────────────────────────
    lines.append("─── 9. TOP 5 SKILLS PER JOB CATEGORY ─────────────────────")
    if "job_category" in df.columns:
        for cat in sorted(df["job_category"].unique()):
            subset = df[df["job_category"] == cat][skill_cols]
            top5 = subset.sum().sort_values(ascending=False).head(5)
            skill_list = ", ".join(
                f"{sid_name_map.get(c, c.replace('skill_','').upper())} ({int(v)})"
                for c, v in top5.items()
            )
            lines.append(f"  {cat:<16} → {skill_list}")
        lines.append("")

    lines.append(sep)
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Build job-skill binary vectors v2")
    parser.add_argument(
        "--dry-run",
        type=int,
        default=0,
        metavar="N",
        help="Process only N rows (for testing)",
    )
    parser.add_argument(
        "--sparse",
        action="store_true",
        help="Use pandas Sparse dtype to reduce memory",
    )
    args = parser.parse_args()

    t_start = time.perf_counter()

    # ── Load data ─────────────────────────────────────────────────────────
    log.info("Loading skills catalogue: %s", SKILLS_PATH)
    skills = pd.read_csv(SKILLS_PATH)
    log.info("  → %d skills loaded", len(skills))

    log.info("Loading tagged jobs: %s", JOBS_PATH)
    if args.dry_run > 0:
        jobs = pd.read_csv(JOBS_PATH, nrows=args.dry_run)
        log.info("  → DRY-RUN: %d / ? jobs loaded", len(jobs))
    else:
        jobs = pd.read_csv(JOBS_PATH)
        log.info("  → %d jobs loaded", len(jobs))

    n_input = len(jobs)

    # ── Build vectors ─────────────────────────────────────────────────────
    result, all_ids, skill_cols, unknowns = build_vectors(
        jobs, skills, use_sparse=args.sparse
    )

    # ── Validate ──────────────────────────────────────────────────────────
    log.info("Running validation checks …")
    issues = validate(result, skill_cols, n_input)
    if issues:
        for iss in issues:
            log.error("VALIDATION FAIL: %s", iss)
        log.error("Fix the issues above before using the output.")
    else:
        log.info("All validation checks PASSED ✓")

    # ── Save vectors ──────────────────────────────────────────────────────
    OUT_VECTORS.parent.mkdir(parents=True, exist_ok=True)
    log.info("Saving vectors → %s", OUT_VECTORS)
    result.to_csv(OUT_VECTORS, index=False)
    size_mb = OUT_VECTORS.stat().st_size / 1024 / 1024
    log.info("  → saved (%.1f MB)", size_mb)

    # ── Analytics ─────────────────────────────────────────────────────────
    log.info("Generating analytics report …")
    report = generate_analytics(result, skill_cols, all_ids, skills)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(report, encoding="utf-8")
    log.info("Report saved → %s", OUT_REPORT)

    # ── Print summary ─────────────────────────────────────────────────────
    elapsed = time.perf_counter() - t_start
    print()
    print("=" * 78)
    summary = textwrap.dedent(f"""\
        COMPLETE — Job-Skill Vectors v2
          Jobs:       {n_input:,}
          Skills:     {len(skill_cols):,}
          Dimensions: {result.shape[0]:,} × {result.shape[1]:,}
          File size:  {size_mb:.1f} MB
          Elapsed:    {elapsed:.1f}s
          Output:     {OUT_VECTORS}
          Report:     {OUT_REPORT}
    """)
    print(summary)
    print("=" * 78)

    # Also print key analytics to console
    print(report)


if __name__ == "__main__":
    main()
