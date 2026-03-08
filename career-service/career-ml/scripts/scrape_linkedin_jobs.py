"""
scrape_linkedin_jobs.py
========================
Scrape LinkedIn Jobs (Sri Lanka + Remote) using Selenium with headless Chrome.

  - Multiple search keywords × locations
  - Experience-level and job-type filters
  - Handles lazy-loading / infinite scroll
  - Structured data extraction
  - Rate limiting & retry logic
  - Checkpoint / resume support

Target  : ~5,000 jobs
Output  : data/raw/jobs_linkedin_scraped.csv

Prerequisites:
    pip install selenium webdriver-manager pandas tqdm
    Chrome / Chromium must be installed.

Run:
    cd career-ml
    python scripts/scrape_linkedin_jobs.py [--resume] [--headless]
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

import pandas as pd
from tqdm import tqdm

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import (
        NoSuchElementException, TimeoutException,
        StaleElementReferenceException, WebDriverException,
    )
except ImportError:
    raise SystemExit(
        "selenium is required. Install with:\n  pip install selenium webdriver-manager"
    )

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
RAW_DIR        = BASE_DIR / "data" / "raw"
OUTPUT_CSV     = RAW_DIR / "jobs_linkedin_scraped.csv"
CHECKPOINT_DIR = RAW_DIR / "checkpoints"
CHECKPOINT_FILE = CHECKPOINT_DIR / "linkedin_checkpoint.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# ── Search Configuration ─────────────────────────────────────────────
SEARCH_KEYWORDS = [
    "Software Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "Cloud Engineer",
    "ML Engineer",
    "Product Manager",
    "QA Engineer",
    "Security Engineer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Business Analyst",
    "Scrum Master",
    "Technical Writer",
    "Mobile Developer",
    "Data Analyst",
    "Data Engineer",
    "Machine Learning Engineer",
    "Site Reliability Engineer",
    "Platform Engineer",
    "Solutions Architect",
    "UI UX Designer",
    "React Developer",
    "Python Developer",
    "Java Developer",
    "Node.js Developer",
    "Angular Developer",
    "Cybersecurity Analyst",
    "Project Manager IT",
    "Database Administrator",
]

LOCATIONS = [
    "Sri Lanka",
    "Colombo, Sri Lanka",
    "Remote",
    "Bangalore, India",
    "Pune, India",
]

# LinkedIn experience-level filter values (URL param f_E)
EXPERIENCE_LEVELS = {
    "entry":      "2",
    "associate":  "3",
    "mid_senior": "4",
    "director":   "5",
}

# Job type filter values (URL param f_JT)
JOB_TYPES = {
    "full_time":  "F",
    "contract":   "C",
    "remote":     "R",
}

# LinkedIn public jobs URL template (no login required)
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/search/"


# ── Helpers ───────────────────────────────────────────────────────────
def _random_delay(lo: float = 2.0, hi: float = 5.0) -> None:
    time.sleep(random.uniform(lo, hi))


def _fingerprint(title: str, company: str) -> str:
    key = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_experience(text: str) -> str:
    patterns = [
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def _detect_job_type(text: str) -> str:
    t = text.lower()
    if "remote" in t:
        return "remote"
    if "hybrid" in t:
        return "hybrid"
    if "contract" in t:
        return "contract"
    if "part-time" in t or "part time" in t:
        return "part-time"
    return "full-time"


def _detect_industry(text: str) -> str:
    t = text.lower()
    for industry, kws in [
        ("fintech",    ["fintech", "banking", "financial", "payment"]),
        ("healthtech", ["health", "medical", "pharma"]),
        ("ecommerce",  ["ecommerce", "e-commerce", "retail"]),
        ("edtech",     ["education", "edtech", "learning"]),
        ("enterprise", ["enterprise", "erp", "sap"]),
        ("telecom",    ["telecom", "telco"]),
        ("startup",    ["startup", "start-up"]),
    ]:
        if any(kw in t for kw in kws):
            return industry
    return ""


# ── Checkpoint ────────────────────────────────────────────────────────
def _load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {"seen_fingerprints": [], "completed_queries": [], "jobs_collected": 0}


def _save_checkpoint(state: dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(state, indent=2))


# ── Selenium Browser Setup ───────────────────────────────────────────
def _create_driver(headless: bool = True) -> webdriver.Chrome:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Rotate UA
    ua = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    ])
    options.add_argument(f"user-agent={ua}")

    if USE_WDM:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


# ── Scroll to Load All Jobs ──────────────────────────────────────────
def _scroll_to_load(driver: webdriver.Chrome, max_scrolls: int = 15) -> None:
    """Scroll down to trigger lazy-loading of job cards."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # Click "See more jobs" button if present
        try:
            see_more = driver.find_element(
                By.CSS_SELECTOR, "button.infinite-scroller__show-more-button"
            )
            see_more.click()
            time.sleep(2)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ── Parse Job Cards from Listing ─────────────────────────────────────
def _extract_job_cards(driver: webdriver.Chrome) -> list[dict]:
    """Extract basic info from LinkedIn job listing cards."""
    cards: list[dict] = []
    card_selectors = [
        "div.base-card",
        "li.jobs-search-results__list-item",
        "div.job-search-card",
        "ul.jobs-search__results-list li",
    ]

    elements = []
    for sel in card_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        if elements:
            break

    for el in elements:
        try:
            title = ""
            company = ""
            location = ""
            link = ""
            posted = ""

            # Title
            for t_sel in ["h3.base-search-card__title", "h3", ".job-card-list__title", "a.job-card-container__link"]:
                try:
                    title = el.find_element(By.CSS_SELECTOR, t_sel).text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    pass

            # Company
            for c_sel in ["h4.base-search-card__subtitle", "h4", ".job-card-container__primary-description"]:
                try:
                    company = el.find_element(By.CSS_SELECTOR, c_sel).text.strip()
                    if company:
                        break
                except NoSuchElementException:
                    pass

            # Location
            for l_sel in [".job-search-card__location", ".base-search-card__metadata span", ".job-card-container__metadata-item"]:
                try:
                    location = el.find_element(By.CSS_SELECTOR, l_sel).text.strip()
                    if location:
                        break
                except NoSuchElementException:
                    pass

            # Link
            try:
                a = el.find_element(By.CSS_SELECTOR, "a.base-card__full-link, a[href*='/jobs/view/']")
                link = a.get_attribute("href") or ""
            except NoSuchElementException:
                pass

            # Posted date
            try:
                time_el = el.find_element(By.CSS_SELECTOR, "time, .job-search-card__listdate")
                posted = time_el.get_attribute("datetime") or time_el.text.strip()
            except NoSuchElementException:
                pass

            if title:
                cards.append({
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "source_url": link,
                    "posted_date": posted,
                })
        except StaleElementReferenceException:
            continue

    return cards


# ── Parse Detail Page ────────────────────────────────────────────────
def _extract_job_detail(driver: webdriver.Chrome, url: str) -> dict:
    """Navigate to a job detail page and extract description."""
    details = {"description": "", "requirements_text": ""}

    try:
        driver.get(url)
        _random_delay(2, 4)

        # Click "Show more" if present
        try:
            show_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button.show-more-less-html__button, button[aria-label*='Show more']"
                ))
            )
            show_btn.click()
            time.sleep(1)
        except (TimeoutException, NoSuchElementException):
            pass

        # Main description
        for d_sel in [
            ".show-more-less-html__markup",
            ".description__text",
            ".jobs-description__content",
            "div[class*='description']",
            "section.description",
        ]:
            try:
                desc_el = driver.find_element(By.CSS_SELECTOR, d_sel)
                details["description"] = _clean_text(desc_el.text)
                if details["description"]:
                    break
            except NoSuchElementException:
                pass

        # Extract requirements from description
        full = details["description"]
        req_match = re.search(
            r"(?:requirements?|qualifications?|must.have|what.we.look.for)"
            r"[:\s]*(.{100,2000})",
            full, re.IGNORECASE
        )
        if req_match:
            details["requirements_text"] = req_match.group(1)[:1500]

        # Seniority / experience from criteria list
        try:
            criteria = driver.find_elements(
                By.CSS_SELECTOR,
                ".description__job-criteria-item, li.job-criteria__item"
            )
            for c in criteria:
                text = c.text.lower()
                if "seniority" in text or "experience" in text:
                    details["seniority"] = _clean_text(c.text)
        except NoSuchElementException:
            pass

    except WebDriverException as exc:
        print(f"    ⚠ detail fetch failed: {exc}")

    return details


# ── Main Scraping Loop ───────────────────────────────────────────────
def _build_search_url(keyword: str, location: str,
                      exp_filter: str = "", jtype_filter: str = "",
                      start: int = 0) -> str:
    """Build a LinkedIn public jobs search URL."""
    params = {
        "keywords": keyword,
        "location": location,
        "f_TPR": "r2592000",  # past month
        "start": str(start),
    }
    if exp_filter:
        params["f_E"] = exp_filter
    if jtype_filter:
        params["f_JT"] = jtype_filter

    qs = "&".join(f"{k}={v.replace(' ', '%20')}" for k, v in params.items())
    return f"{LINKEDIN_JOBS_URL}?{qs}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape LinkedIn Jobs")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Run browser headless (default)")
    parser.add_argument("--no-headless", dest="headless", action="store_false",
                        help="Show browser window")
    parser.add_argument("--max-jobs", type=int, default=5000)
    parser.add_argument("--max-detail", type=int, default=150,
                        help="Max detail pages per keyword-location combo")
    parser.add_argument("--dry-run", action="store_true",
                        help="Scrape only 1 page per query (testing)")
    args = parser.parse_args()

    print("=" * 70)
    print("  LinkedIn Jobs Scraper (Selenium)")
    print("=" * 70)

    state = _load_checkpoint() if args.resume else {
        "seen_fingerprints": [], "completed_queries": [],
        "jobs_collected": 0,
    }
    seen_fps = set(state.get("seen_fingerprints", []))
    completed_queries = set(state.get("completed_queries", []))

    all_jobs: list[dict] = []
    if args.resume and OUTPUT_CSV.exists():
        existing = pd.read_csv(OUTPUT_CSV)
        all_jobs = existing.to_dict("records")
        print(f"  Resuming with {len(all_jobs)} existing jobs")

    # Create browser
    print("  Starting Chrome …")
    driver = _create_driver(headless=args.headless)

    try:
        # Build query combos
        queries = []
        for kw in SEARCH_KEYWORDS:
            for loc in LOCATIONS:
                qid = f"{kw}|{loc}"
                if qid not in completed_queries:
                    queries.append((kw, loc))

        progress = tqdm(queries, desc="Queries", unit="query")
        for kw, loc in progress:
            if len(all_jobs) >= args.max_jobs:
                break

            qid = f"{kw}|{loc}"
            progress.set_postfix_str(f"{kw} @ {loc}")

            max_pages_kw = 1 if args.dry_run else 5
            detail_count = 0

            for page in range(max_pages_kw):
                start = page * 25
                url = _build_search_url(kw, loc, start=start)

                try:
                    driver.get(url)
                    _random_delay(3, 6)
                    _scroll_to_load(driver, max_scrolls=5 if not args.dry_run else 2)
                except WebDriverException:
                    break

                cards = _extract_job_cards(driver)
                if not cards:
                    break

                for card in cards:
                    if len(all_jobs) >= args.max_jobs:
                        break

                    fp = _fingerprint(card["job_title"], card["company_name"])
                    if fp in seen_fps:
                        continue
                    seen_fps.add(fp)

                    # Optionally fetch detail page
                    details = {}
                    if card.get("source_url") and detail_count < args.max_detail:
                        details = _extract_job_detail(driver, card["source_url"])
                        detail_count += 1
                        _random_delay(1, 3)

                    desc = details.get("description", "")
                    job = {
                        "job_title":         card["job_title"],
                        "company_name":      card["company_name"],
                        "description":       desc,
                        "requirements_text": details.get("requirements_text", ""),
                        "salary_raw":        "",
                        "experience_raw":    _extract_experience(desc) if desc else "",
                        "job_type":          _detect_job_type(desc or card.get("location", "")),
                        "location":          card.get("location", loc),
                        "industry":          _detect_industry(desc),
                        "posted_date":       card.get("posted_date", ""),
                        "source":            "linkedin.com",
                        "source_url":        card.get("source_url", ""),
                        "scrape_date":       datetime.now().isoformat(),
                    }
                    all_jobs.append(job)

                _random_delay(2, 5)

            completed_queries.add(qid)

            # Checkpoint every 5 queries
            if len(completed_queries) % 5 == 0:
                state["seen_fingerprints"] = list(seen_fps)
                state["completed_queries"] = list(completed_queries)
                state["jobs_collected"] = len(all_jobs)
                _save_checkpoint(state)

    finally:
        driver.quit()

    # Save
    df = pd.DataFrame(all_jobs)
    df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)

    # Final checkpoint
    state["seen_fingerprints"] = list(seen_fps)
    state["completed_queries"] = list(completed_queries)
    state["jobs_collected"] = len(all_jobs)
    _save_checkpoint(state)

    print(f"\n{'=' * 70}")
    print(f"  DONE — {len(df)} jobs saved to {OUTPUT_CSV}")
    print(f"  Unique fingerprints: {len(seen_fps)}")
    print(f"  Queries completed: {len(completed_queries)}/{len(SEARCH_KEYWORDS) * len(LOCATIONS)}")
    print(f"{'=' * 70}")

    if not df.empty:
        print(f"\n  Locations: {df['location'].value_counts().head(10).to_dict()}")
        print(f"  Job types: {df['job_type'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
