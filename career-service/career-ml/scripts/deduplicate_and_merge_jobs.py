"""
deduplicate_and_merge_jobs.py
=============================
Merge all scraped job CSVs + the original jobs_labeled.csv into one
unified dataset, removing duplicates.

Inputs:
  • data/raw/jobs_topjobs_scraped.csv
  • data/raw/jobs_linkedin_scraped.csv
  • data/raw/jobs_companies_scraped.csv
  • data/jobs_labeled.csv   (original 5,470 rows — ALL preserved)

Deduplication strategy:
  1. Exact  : MD5 fingerprint of (title_lower + company_lower)
  2. Fuzzy  : rapidfuzz token_sort_ratio
       title > 85, company > 90, description > 70  →  mark as dup
  3. Quality scoring to pick the richer record when duplicates found

Target  : 18,000 – 20,000 unique jobs
Outputs :
  • data/processed/jobs_unified.csv
  • data/reports/deduplication_report.txt

Prerequisites:
    pip install pandas rapidfuzz tqdm

Run:
    cd career-ml
    python scripts/deduplicate_and_merge_jobs.py [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR   = BASE_DIR / "data" / "reports"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

ORIGINAL_CSV = BASE_DIR / "data" / "jobs_labeled.csv"
OUTPUT_CSV   = PROCESSED_DIR / "jobs_unified.csv"
REPORT_FILE  = REPORTS_DIR / "deduplication_report.txt"

# Scraped CSV sources (in priority order — earliest = higher priority)
SCRAPED_CSVS = [
    RAW_DIR / "jobs_topjobs_scraped.csv",
    RAW_DIR / "jobs_linkedin_scraped.csv",
    RAW_DIR / "jobs_companies_scraped.csv",
]

# ── Column mapping: scraped → unified schema ─────────────────────────
UNIFIED_COLS = [
    "job_uid", "source", "job_title", "company_name",
    "description", "requirements_text", "job_text",
    "matched_skill_ids", "matched_skills", "matched_skill_count",
    "experience_raw", "salary_raw", "job_type", "industry",
    "location", "posted_date", "source_url", "scrape_date",
    "title_clean_for_role", "role_id", "role_title", "job_title_clean",
]


# ══════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════

def _fingerprint(title: str, company: str) -> str:
    key = f"{str(title).strip().lower()}|{str(company).strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()


def _quality_score(row: pd.Series) -> float:
    """Higher = richer record.  Used to pick 'best' among fuzzy dups."""
    score = 0.0
    for col in ["description", "requirements_text", "job_text"]:
        val = str(row.get(col, ""))
        if val and val != "nan":
            score += min(len(val) / 500, 3.0)  # up to 3 pts per field
    for col in ["experience_raw", "salary_raw", "industry", "location",
                "posted_date", "source_url"]:
        val = str(row.get(col, ""))
        if val and val != "nan" and val != "":
            score += 1.0
    # Bonus for matched skills
    try:
        msc = float(row.get("matched_skill_count", 0) or 0)
        score += min(msc / 5, 2.0)
    except (ValueError, TypeError):
        pass
    return score


def _load_original() -> pd.DataFrame:
    """Load original jobs_labeled.csv — these rows are ALWAYS kept."""
    if not ORIGINAL_CSV.exists():
        print(f"  ⚠ Original CSV not found at {ORIGINAL_CSV}")
        return pd.DataFrame()
    df = pd.read_csv(ORIGINAL_CSV, dtype=str, keep_default_na=False)
    df["_source_priority"] = 0   # highest priority (never removed)
    df["_origin"] = "original"
    print(f"  ✓ Original: {len(df)} rows from {ORIGINAL_CSV.name}")
    return df


def _load_scraped() -> pd.DataFrame:
    """Load & concatenate all scraped CSVs that exist."""
    frames = []
    for idx, csvpath in enumerate(SCRAPED_CSVS, start=1):
        if csvpath.exists():
            df = pd.read_csv(csvpath, dtype=str, keep_default_na=False)
            df["_source_priority"] = idx
            df["_origin"] = csvpath.stem
            frames.append(df)
            print(f"  ✓ Scraped:  {len(df)} rows from {csvpath.name}")
        else:
            print(f"  ○ Skipped (not found): {csvpath.name}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════
#  EXACT DEDUP
# ══════════════════════════════════════════════════════════════════════

def exact_dedup(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove rows with identical (title, company) fingerprint.
    Keep the row with the lowest _source_priority (= original first)."""
    df["_fp"] = df.apply(
        lambda r: _fingerprint(r.get("job_title", ""), r.get("company_name", "")),
        axis=1,
    )
    before = len(df)
    # Sort so originals come first, then by quality
    df["_quality"] = df.apply(_quality_score, axis=1)
    df.sort_values(["_source_priority", "_quality"],
                   ascending=[True, False], inplace=True)
    df.drop_duplicates(subset="_fp", keep="first", inplace=True)
    removed = before - len(df)
    df.drop(columns=["_fp", "_quality"], inplace=True)
    return df, removed


# ══════════════════════════════════════════════════════════════════════
#  FUZZY DEDUP
# ══════════════════════════════════════════════════════════════════════

def fuzzy_dedup(df: pd.DataFrame,
                title_thresh: float = 85.0,
                company_thresh: float = 90.0,
                desc_thresh: float = 70.0,
                ) -> tuple[pd.DataFrame, int]:
    """Remove near-duplicates using rapidfuzz token_sort_ratio.

    Only scraped rows can be removed (originals are protected).
    """
    if not HAS_RAPIDFUZZ:
        print("  ⚠ rapidfuzz not installed — skipping fuzzy dedup")
        return df, 0

    df = df.reset_index(drop=True)
    protected = set(df.index[df["_origin"] == "original"])
    to_remove: set[int] = set()

    titles     = df["job_title"].fillna("").str.lower().tolist()
    companies  = df["company_name"].fillna("").str.lower().tolist()
    descs      = df["description"].fillna("").str.lower().tolist()
    origins    = df["_origin"].tolist()

    n = len(df)
    # Compare each scraped row against all previous rows
    # (O(n^2) but tolerable for ~20K rows with early-exit)
    print(f"  Fuzzy dedup: checking {n} rows …")
    for i in tqdm(range(n), desc="  Fuzzy scan", unit="row"):
        if i in to_remove or i in protected:
            continue
        for j in range(i + 1, n):
            if j in to_remove:
                continue
            # Title similarity (fast gate)
            t_sim = fuzz.token_sort_ratio(titles[i], titles[j])
            if t_sim < title_thresh:
                continue
            # Company similarity
            c_sim = fuzz.token_sort_ratio(companies[i], companies[j])
            if c_sim < company_thresh:
                continue
            # Description similarity (only if both non-empty)
            if descs[i] and descs[j]:
                d_sim = fuzz.token_sort_ratio(descs[i][:500], descs[j][:500])
                if d_sim < desc_thresh:
                    continue

            # These are duplicates — remove the lower-quality / lower-priority one
            if j in protected:
                # j is original — remove i (if not protected)
                if i not in protected:
                    to_remove.add(i)
                    break
            elif i in protected:
                to_remove.add(j)
            else:
                # Both scraped — remove the one with lower quality
                qi = _quality_score(df.iloc[i])
                qj = _quality_score(df.iloc[j])
                if qj > qi:
                    to_remove.add(i)
                    break
                else:
                    to_remove.add(j)

    df = df.drop(index=list(to_remove)).reset_index(drop=True)
    return df, len(to_remove)


# ══════════════════════════════════════════════════════════════════════
#  NORMALIZE COLUMNS
# ══════════════════════════════════════════════════════════════════════

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all UNIFIED_COLS exist and fill missing with empty string."""
    for col in UNIFIED_COLS:
        if col not in df.columns:
            df[col] = ""

    # Generate job_uid where missing
    mask = df["job_uid"].isin(["", "nan"]) | df["job_uid"].isna()
    for idx in df.index[mask]:
        title   = str(df.at[idx, "job_title"])
        company = str(df.at[idx, "company_name"])
        origin  = str(df.at[idx, "_origin"]) if "_origin" in df.columns else "scraped"
        uid = hashlib.md5(f"{title}|{company}|{origin}|{idx}".encode()).hexdigest()[:12]
        df.at[idx, "job_uid"] = f"scr_{uid}"

    return df


# ══════════════════════════════════════════════════════════════════════
#  REPORT
# ══════════════════════════════════════════════════════════════════════

def _write_report(stats: dict) -> None:
    lines = [
        "=" * 70,
        "  DEDUPLICATION & MERGE REPORT",
        f"  Generated: {datetime.now().isoformat()}",
        "=" * 70,
        "",
        f"  Original rows (always kept) : {stats['original']}",
        f"  Scraped rows loaded          : {stats['scraped']}",
        f"  Total before dedup           : {stats['total_before']}",
        "",
        f"  Exact duplicates removed     : {stats['exact_removed']}",
        f"  Fuzzy duplicates removed     : {stats['fuzzy_removed']}",
        f"  Total duplicates removed     : {stats['exact_removed'] + stats['fuzzy_removed']}",
        "",
        f"  Final unified rows           : {stats['final']}",
        f"  Output file                  : {OUTPUT_CSV}",
        "",
        "  Source breakdown:",
    ]
    for src, cnt in stats.get("source_counts", {}).items():
        lines.append(f"    {src:40s} : {cnt:>6}")
    lines += ["", "=" * 70]
    text = "\n".join(lines)
    REPORT_FILE.write_text(text, encoding="utf-8")
    print(text)


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deduplicate and merge all job CSVs into jobs_unified.csv")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show counts without writing output")
    parser.add_argument("--skip-fuzzy", action="store_true",
                        help="Skip the (slower) fuzzy dedup step")
    parser.add_argument("--title-thresh", type=float, default=85,
                        help="Fuzzy title threshold (default 85)")
    parser.add_argument("--company-thresh", type=float, default=90,
                        help="Fuzzy company threshold (default 90)")
    parser.add_argument("--desc-thresh", type=float, default=70,
                        help="Fuzzy description threshold (default 70)")
    args = parser.parse_args()

    print("=" * 70)
    print("  Deduplicate & Merge Jobs")
    print("=" * 70)

    # 1. Load all data
    df_orig    = _load_original()
    df_scraped = _load_scraped()

    if df_orig.empty and df_scraped.empty:
        print("  ✗ No data found. Exiting.")
        return

    df_all = pd.concat([df_orig, df_scraped], ignore_index=True)
    total_before = len(df_all)
    print(f"\n  Total rows before dedup: {total_before}")

    # 2. Exact dedup
    print("\n  ── Exact Dedup ──")
    df_all, exact_removed = exact_dedup(df_all)
    print(f"  Removed {exact_removed} exact duplicates → {len(df_all)} rows")

    # 3. Fuzzy dedup
    fuzzy_removed = 0
    if not args.skip_fuzzy:
        print("\n  ── Fuzzy Dedup ──")
        df_all, fuzzy_removed = fuzzy_dedup(
            df_all,
            title_thresh=args.title_thresh,
            company_thresh=args.company_thresh,
            desc_thresh=args.desc_thresh,
        )
        print(f"  Removed {fuzzy_removed} fuzzy duplicates → {len(df_all)} rows")
    else:
        print("  (fuzzy dedup skipped)")

    # 4. Normalize columns
    df_all = _normalize_columns(df_all)

    # 5. Source breakdown
    src_counts = {}
    if "_origin" in df_all.columns:
        src_counts = df_all["_origin"].value_counts().to_dict()

    # 6. Clean up internal columns
    internal_cols = [c for c in df_all.columns if c.startswith("_")]
    df_all.drop(columns=internal_cols, inplace=True, errors="ignore")

    # 7. Reorder columns
    cols = [c for c in UNIFIED_COLS if c in df_all.columns]
    extra = [c for c in df_all.columns if c not in UNIFIED_COLS]
    df_all = df_all[cols + extra]

    # 8. Write outputs
    stats = {
        "original":      len(df_orig),
        "scraped":       len(df_scraped),
        "total_before":  total_before,
        "exact_removed": exact_removed,
        "fuzzy_removed": fuzzy_removed,
        "final":         len(df_all),
        "source_counts": src_counts,
    }

    if not args.dry_run:
        df_all.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)
        print(f"\n  ✓ Saved {len(df_all)} rows → {OUTPUT_CSV}")
    else:
        print(f"\n  [DRY RUN] Would save {len(df_all)} rows → {OUTPUT_CSV}")

    _write_report(stats)


if __name__ == "__main__":
    main()
