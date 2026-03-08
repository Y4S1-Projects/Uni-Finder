"""
scrape_topjobs_advanced.py
===========================
Scrape TopJobs.lk for IT / tech job listings with advanced features:

  - Rate limiting (2-5 s random delay)
  - Rotating user agents
  - Session management with retries
  - Progress tracking (tqdm)
  - Resume / checkpoint capability
  - Duplicate detection during scraping

Target  : ~8,000 new jobs
Output  : data/raw/jobs_topjobs_scraped.csv

Run:
    cd career-ml
    python scripts/scrape_topjobs_advanced.py [--resume]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
RAW_DIR        = BASE_DIR / "data" / "raw"
OUTPUT_CSV     = RAW_DIR / "jobs_topjobs_scraped.csv"
CHECKPOINT_DIR = RAW_DIR / "checkpoints"
CHECKPOINT_FILE = CHECKPOINT_DIR / "topjobs_checkpoint.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# ── TopJobs Config ───────────────────────────────────────────────────
BASE_URL = "https://www.topjobs.lk"

# Category IDs / slugs on TopJobs (IT & Software categories)
# These are the functional-area codes TopJobs uses in its URL scheme.
TARGET_CATEGORIES = {
    "KAJ": "Software Development",
    "KAK": "Software QA & Testing",
    "KAH": "Database / Data Science",
    "K8F": "IT / Network Administration",
    "KAI": "Business Analysis",
    "KAL": "Project Management",
    "KAM": "UI/UX Design",
    "K8G": "Security / Compliance",
    "KAN": "Cloud / DevOps",
    "K8E": "Technical Writing",
    "KAO": "Product Management",
}

# Search keywords we will cycle through (supplementary to categories)
SEARCH_KEYWORDS = [
    "software engineer", "data scientist", "devops engineer",
    "cloud engineer", "ml engineer", "product manager",
    "qa engineer", "security engineer", "full stack developer",
    "frontend developer", "backend developer", "business analyst",
    "scrum master", "technical writer", "mobile developer",
    "react developer", "python developer", "java developer",
    "node.js developer", "angular developer", "data analyst",
    "machine learning", "artificial intelligence", "kubernetes",
    "aws", "azure", "project manager", "ux designer",
    "ui designer", "database administrator",
]

# ── User-Agent Rotation ──────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/103.0.0.0",
]


# ── Helpers ───────────────────────────────────────────────────────────
def _random_delay(lo: float = 2.0, hi: float = 5.0) -> None:
    time.sleep(random.uniform(lo, hi))


def _pick_ua() -> str:
    return random.choice(USER_AGENTS)


def _fingerprint(title: str, company: str) -> str:
    """Hash to detect duplicates during scrape."""
    key = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML tags
    text = re.sub(r"&[a-zA-Z]+;", " ", text)      # HTML entities
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_experience(text: str) -> str:
    """Try to pull an experience requirement from text."""
    patterns = [
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)",
        r"experience\s*[:\-]?\s*(\d+)\s*\+?\s*(?:years?|yrs?)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def _detect_job_type(text: str) -> str:
    text_lower = text.lower()
    if "remote" in text_lower:
        return "remote"
    if "hybrid" in text_lower:
        return "hybrid"
    if "contract" in text_lower or "freelance" in text_lower:
        return "contract"
    if "part-time" in text_lower or "part time" in text_lower:
        return "part-time"
    return "full-time"


def _detect_industry(text: str) -> str:
    text_lower = text.lower()
    mapping = [
        ("fintech",    ["fintech", "banking", "financial", "payment"]),
        ("healthtech", ["health", "medical", "pharma", "biotech"]),
        ("ecommerce",  ["ecommerce", "e-commerce", "retail", "marketplace"]),
        ("edtech",     ["education", "edtech", "learning", "lms"]),
        ("enterprise", ["enterprise", "erp", "sap", "oracle"]),
        ("telecom",    ["telecom", "telco", "mobile operator"]),
        ("logistics",  ["logistics", "supply chain", "shipping"]),
        ("startup",    ["startup", "start-up"]),
    ]
    for industry, keywords in mapping:
        if any(kw in text_lower for kw in keywords):
            return industry
    return ""


# ── Session Builder ──────────────────────────────────────────────────
def _build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": _pick_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": BASE_URL,
    })
    return s


def _get_with_retries(session: requests.Session, url: str,
                      max_retries: int = 3) -> Optional[requests.Response]:
    for attempt in range(1, max_retries + 1):
        try:
            session.headers["User-Agent"] = _pick_ua()
            resp = session.get(url, timeout=30)
            if resp.status_code == 429:
                wait = 10 * attempt
                print(f"  Rate limited – waiting {wait}s …")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            print(f"  Attempt {attempt}/{max_retries} failed: {exc}")
            time.sleep(5 * attempt)
    return None


# ── Checkpoint I/O ───────────────────────────────────────────────────
def _load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {"scraped_urls": [], "seen_fingerprints": [], "last_keyword_idx": 0,
            "last_category_idx": 0, "jobs_collected": 0}


def _save_checkpoint(state: dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(state, indent=2))


# ── Page Parsers ─────────────────────────────────────────────────────
def _parse_listing_page(html: str) -> list[dict]:
    """Parse a TopJobs listing page and return partial job dicts with links."""
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    # TopJobs uses table-based layout – job rows are typically in
    # <tr> tags inside a results table. We look for links to job detail pages.
    links = soup.find_all("a", href=True)
    for a_tag in links:
        href = a_tag["href"]
        # Job detail links on TopJobs look like /employer/JobDiv*.jsp?...
        # or /applicant/ViewJob?...  or similar patterns
        if any(kw in href.lower() for kw in
               ["viewjob", "jobdiv", "job_summary", "vacancy"]):
            title_text = _clean_text(a_tag.get_text())
            if title_text and len(title_text) > 3:
                full_url = urljoin(BASE_URL, href)
                jobs.append({
                    "url": full_url,
                    "job_title": title_text,
                })

    # Alternate: TopJobs also embeds structured job blocks in <div class="...">
    for div in soup.select("div.job-row, div.position-row, tr.job"):
        title_el = div.select_one("a, .job-title, .position-title")
        company_el = div.select_one(".company-name, .employer-name, td:nth-child(2)")
        if title_el:
            href = title_el.get("href", "")
            jobs.append({
                "url": urljoin(BASE_URL, href) if href else "",
                "job_title": _clean_text(title_el.get_text()),
                "company_name": _clean_text(company_el.get_text()) if company_el else "",
            })

    # Deduplicate by URL
    seen = set()
    unique = []
    for j in jobs:
        if j["url"] and j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)
    return unique


def _parse_detail_page(html: str) -> dict:
    """Extract structured fields from a job detail page."""
    soup = BeautifulSoup(html, "html.parser")
    body_text = _clean_text(soup.get_text(separator=" "))

    # Try to find structured sections
    desc = ""
    reqs = ""

    # TopJobs often has description in a main content div
    content_div = soup.select_one(
        "#content, .job-detail, .vacancy-detail, .jobdescription, "
        "div[class*='description'], div[class*='vacancy']"
    )
    if content_div:
        desc = _clean_text(content_div.get_text(separator=" "))
    else:
        desc = body_text[:3000]

    # Requirements often follow keywords
    req_match = re.search(
        r"(?:requirements?|qualifications?|must.have|what.we.look.for)"
        r"[:\s]*(.{100,2000})",
        body_text, re.IGNORECASE
    )
    if req_match:
        reqs = req_match.group(1)[:1500]

    # Company name
    company = ""
    co_el = soup.select_one(
        ".company-name, .employer-name, span[class*='company'], "
        "div[class*='company'], h2.company"
    )
    if co_el:
        company = _clean_text(co_el.get_text())

    # Salary
    salary = ""
    sal_match = re.search(
        r"(?:salary|remuneration|compensation)[:\s]*([\w\s,.\-/]+?)(?:\.|$)",
        body_text, re.IGNORECASE
    )
    if sal_match:
        salary = sal_match.group(1).strip()[:150]

    # Location
    location = ""
    loc_el = soup.select_one(
        ".location, span[class*='location'], div[class*='location']"
    )
    if loc_el:
        location = _clean_text(loc_el.get_text())
    else:
        loc_match = re.search(
            r"(?:location|based\s+in)[:\s]*([\w\s,]+?)(?:\.|$)",
            body_text, re.IGNORECASE
        )
        if loc_match:
            location = loc_match.group(1).strip()[:100]
    # Default to Sri Lanka since TopJobs.lk is SL-focused
    if not location:
        location = "Sri Lanka"

    # Posted date
    posted = ""
    date_el = soup.select_one(
        ".posted-date, span[class*='date'], div[class*='date']"
    )
    if date_el:
        posted = _clean_text(date_el.get_text())

    return {
        "company_name":    company,
        "description":     desc,
        "requirements_text": reqs,
        "salary_raw":      salary,
        "experience_raw":  _extract_experience(body_text),
        "job_type":        _detect_job_type(body_text),
        "location":        location,
        "industry":        _detect_industry(body_text),
        "posted_date":     posted,
    }


# ── Scraping Strategies ──────────────────────────────────────────────

def _scrape_by_category(session: requests.Session, cat_code: str,
                        cat_name: str, seen_fps: set,
                        max_pages: int = 50) -> list[dict]:
    """Scrape job listings for a given TopJobs category."""
    jobs_out: list[dict] = []
    print(f"\n  ▸ Category: {cat_name} ({cat_code})")

    for page in tqdm(range(1, max_pages + 1), desc=f"   {cat_name}", leave=False):
        url = f"{BASE_URL}/employer/JobList.jsp?FA={cat_code}&page={page}"
        resp = _get_with_retries(session, url)
        if resp is None:
            break

        listings = _parse_listing_page(resp.text)
        if not listings:
            break  # no more pages

        for listing in listings:
            fp = _fingerprint(listing.get("job_title", ""),
                              listing.get("company_name", ""))
            if fp in seen_fps:
                continue
            seen_fps.add(fp)

            # Fetch detail page
            if listing.get("url"):
                _random_delay()
                detail_resp = _get_with_retries(session, listing["url"])
                if detail_resp:
                    details = _parse_detail_page(detail_resp.text)
                else:
                    details = {}
            else:
                details = {}

            job = {
                "job_title":        listing.get("job_title", ""),
                "company_name":     details.get("company_name") or listing.get("company_name", ""),
                "description":      details.get("description", ""),
                "requirements_text": details.get("requirements_text", ""),
                "salary_raw":       details.get("salary_raw", ""),
                "experience_raw":   details.get("experience_raw", ""),
                "job_type":         details.get("job_type", "full-time"),
                "location":         details.get("location", "Sri Lanka"),
                "industry":         details.get("industry", ""),
                "posted_date":      details.get("posted_date", ""),
                "source":           "topjobs.lk",
                "source_url":       listing.get("url", ""),
                "scrape_date":      datetime.now().isoformat(),
            }
            jobs_out.append(job)

        _random_delay(1.5, 3.5)

    print(f"    → collected {len(jobs_out)} jobs from {cat_name}")
    return jobs_out


def _scrape_by_keyword(session: requests.Session, keyword: str,
                       seen_fps: set, max_pages: int = 20) -> list[dict]:
    """Scrape TopJobs search results for a keyword."""
    jobs_out: list[dict] = []

    for page in range(1, max_pages + 1):
        url = (f"{BASE_URL}/employer/JobList.jsp?"
               f"kw={keyword.replace(' ', '+')}&page={page}")
        resp = _get_with_retries(session, url)
        if resp is None:
            break

        listings = _parse_listing_page(resp.text)
        if not listings:
            break

        for listing in listings:
            fp = _fingerprint(listing.get("job_title", ""),
                              listing.get("company_name", ""))
            if fp in seen_fps:
                continue
            seen_fps.add(fp)

            if listing.get("url"):
                _random_delay()
                detail_resp = _get_with_retries(session, listing["url"])
                if detail_resp:
                    details = _parse_detail_page(detail_resp.text)
                else:
                    details = {}
            else:
                details = {}

            job = {
                "job_title":        listing.get("job_title", ""),
                "company_name":     details.get("company_name") or listing.get("company_name", ""),
                "description":      details.get("description", ""),
                "requirements_text": details.get("requirements_text", ""),
                "salary_raw":       details.get("salary_raw", ""),
                "experience_raw":   details.get("experience_raw", ""),
                "job_type":         details.get("job_type", "full-time"),
                "location":         details.get("location", "Sri Lanka"),
                "industry":         details.get("industry", ""),
                "posted_date":      details.get("posted_date", ""),
                "source":           "topjobs.lk",
                "source_url":       listing.get("url", ""),
                "scrape_date":      datetime.now().isoformat(),
            }
            jobs_out.append(job)

        _random_delay(1.5, 3.0)

    return jobs_out


# ── Main ─────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape TopJobs.lk IT jobs")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--max-jobs", type=int, default=8000,
                        help="Maximum jobs to collect (default 8000)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse only 2 pages per source (for testing)")
    args = parser.parse_args()

    print("=" * 70)
    print("  TopJobs.lk Advanced Scraper")
    print("=" * 70)

    # Load checkpoint
    state = _load_checkpoint() if args.resume else {
        "scraped_urls": [], "seen_fingerprints": [],
        "last_keyword_idx": 0, "last_category_idx": 0,
        "jobs_collected": 0,
    }
    seen_fps = set(state.get("seen_fingerprints", []))

    # Load existing output if resuming
    all_jobs: list[dict] = []
    if args.resume and OUTPUT_CSV.exists():
        existing = pd.read_csv(OUTPUT_CSV)
        all_jobs = existing.to_dict("records")
        print(f"  Resuming with {len(all_jobs)} existing jobs")

    session = _build_session()
    max_pages = 2 if args.dry_run else 50
    target = args.max_jobs

    # Phase 1: Scrape by category
    cat_codes = list(TARGET_CATEGORIES.keys())
    start_cat = state.get("last_category_idx", 0)
    for i, code in enumerate(cat_codes[start_cat:], start=start_cat):
        if len(all_jobs) >= target:
            break
        cat_name = TARGET_CATEGORIES[code]
        new_jobs = _scrape_by_category(session, code, cat_name, seen_fps,
                                       max_pages=max_pages)
        all_jobs.extend(new_jobs)

        # Checkpoint
        state["last_category_idx"] = i + 1
        state["seen_fingerprints"] = list(seen_fps)
        state["jobs_collected"] = len(all_jobs)
        _save_checkpoint(state)

    # Phase 2: Scrape by keyword
    start_kw = state.get("last_keyword_idx", 0)
    for i, kw in enumerate(
        tqdm(SEARCH_KEYWORDS[start_kw:], desc="Keyword search"),
        start=start_kw
    ):
        if len(all_jobs) >= target:
            break
        new_jobs = _scrape_by_keyword(session, kw, seen_fps,
                                      max_pages=max_pages)
        all_jobs.extend(new_jobs)
        print(f"    keyword '{kw}' → {len(new_jobs)} new")

        state["last_keyword_idx"] = i + 1
        state["seen_fingerprints"] = list(seen_fps)
        state["jobs_collected"] = len(all_jobs)
        _save_checkpoint(state)

    # Save results
    df = pd.DataFrame(all_jobs)
    df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)

    print(f"\n{'=' * 70}")
    print(f"  DONE — {len(df)} jobs saved to {OUTPUT_CSV}")
    print(f"  Unique fingerprints: {len(seen_fps)}")
    print(f"{'=' * 70}")

    # Summary stats
    if not df.empty:
        print(f"\n  Job types:  {df['job_type'].value_counts().to_dict()}")
        print(f"  With salary: {df['salary_raw'].astype(bool).sum()}")
        print(f"  With experience: {df['experience_raw'].astype(bool).sum()}")


if __name__ == "__main__":
    main()
