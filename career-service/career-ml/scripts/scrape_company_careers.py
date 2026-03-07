"""
scrape_company_careers.py
==========================
Scrape career pages of top Sri Lankan IT companies.

  - 30+ companies with company-specific selectors
  - Handles various page structures (React SPAs, static HTML, iframes)
  - Tags each job with company metadata (size, industry)
  - Rate limiting, retries, progress tracking

Target  : ~2,000 jobs
Output  : data/raw/jobs_companies_scraped.csv

Prerequisites:
    pip install requests beautifulsoup4 selenium webdriver-manager pandas tqdm

Run:
    cd career-ml
    python scripts/scrape_company_careers.py [--headless] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        NoSuchElementException, TimeoutException, WebDriverException,
    )
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw"
OUTPUT_CSV = RAW_DIR / "jobs_companies_scraped.csv"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── Shared Helpers ───────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def _random_delay(lo: float = 2.0, hi: float = 5.0):
    time.sleep(random.uniform(lo, hi))


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _fingerprint(title: str, company: str) -> str:
    key = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()


def _extract_experience(text: str) -> str:
    for pat in [
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)",
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def _detect_job_type(text: str) -> str:
    t = text.lower()
    for keyword, jt in [("remote", "remote"), ("hybrid", "hybrid"),
                        ("contract", "contract"), ("part-time", "part-time")]:
        if keyword in t:
            return jt
    return "full-time"


# ── Session for static pages ────────────────────────────────────────
def _build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def _get(session: requests.Session, url: str, retries: int = 3
         ) -> Optional[requests.Response]:
    for attempt in range(1, retries + 1):
        try:
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            r = session.get(url, timeout=30)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            print(f"    attempt {attempt}: {e}")
            time.sleep(3 * attempt)
    return None


# ── Selenium Driver (lazy) ──────────────────────────────────────────
_driver_instance: Optional[webdriver.Chrome] = None


def _get_driver(headless: bool = True) -> webdriver.Chrome:
    global _driver_instance
    if _driver_instance is not None:
        return _driver_instance
    if not HAS_SELENIUM:
        raise RuntimeError("selenium is required for SPA company pages")
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    if USE_WDM:
        service = Service(ChromeDriverManager().install())
        _driver_instance = webdriver.Chrome(service=service, options=opts)
    else:
        _driver_instance = webdriver.Chrome(options=opts)
    return _driver_instance


def _close_driver():
    global _driver_instance
    if _driver_instance:
        _driver_instance.quit()
        _driver_instance = None


# ══════════════════════════════════════════════════════════════════════
#  COMPANY DEFINITIONS
# ══════════════════════════════════════════════════════════════════════
@dataclass
class Company:
    name: str
    careers_url: str
    size: str                        # "startup", "mid", "large", "enterprise"
    industry: str                    # "enterprise", "fintech", "telecom", etc.
    location: str = "Colombo, Sri Lanka"
    needs_selenium: bool = False     # SPA / JS-rendered page
    # CSS selectors — set what works per company
    job_card_sel: str = ""           # outer card/row wrapping each job
    title_sel: str = ""              # title element inside card
    link_sel: str = ""               # <a> for detail page (inside card)
    location_sel: str = ""           # location element inside card
    api_url: str = ""                # REST API if the company exposes one
    pagination_sel: str = ""         # "next page" button
    extra_tags: dict = field(default_factory=dict)


COMPANIES: list[Company] = [
    # ── Large / Enterprise ────────────────────────────────────────
    Company(
        name="WSO2",
        careers_url="https://wso2.com/careers/",
        size="large", industry="enterprise",
        job_card_sel="div.career-card, div.job-card, tr.job-row",
        title_sel="h3, a.job-title, .position-title",
        link_sel="a[href*='career'], a[href*='job']",
        needs_selenium=True,
    ),
    Company(
        name="Virtusa",
        careers_url="https://www.virtusa.com/careers",
        size="enterprise", industry="enterprise",
        api_url="https://careers.virtusa.com/api/jobs?location=Sri+Lanka",
        job_card_sel=".job-listing, .job-card, tr",
        title_sel="h3, .job-title, a",
        link_sel="a[href*='job']",
        needs_selenium=True,
    ),
    Company(
        name="IFS",
        careers_url="https://www.ifs.com/careers",
        size="enterprise", industry="enterprise",
        job_card_sel=".career-listing, .job-item",
        title_sel="h3, .job-title",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="hSenid",
        careers_url="https://www.hsenidmobile.com/careers/",
        size="large", industry="enterprise",
        job_card_sel=".career-card, .job-listing, article",
        title_sel="h3, h2, .title",
        link_sel="a",
    ),
    Company(
        name="CodeGen",
        careers_url="https://www.codegen.co.uk/careers/",
        size="large", industry="enterprise",
        job_card_sel=".vacancy, .job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Zone24x7",
        careers_url="https://zone24x7.com/careers/",
        size="large", industry="enterprise",
        job_card_sel=".job-card, .career-item, article",
        title_sel="h3, h2, .title",
        link_sel="a",
    ),
    Company(
        name="99X",
        careers_url="https://99x.io/careers",
        size="large", industry="enterprise",
        job_card_sel=".job-card, .career, article",
        title_sel="h3, h2",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="Sysco LABS",
        careers_url="https://syscolabs.lk/careers/",
        size="large", industry="enterprise",
        job_card_sel=".career-card, .position, article",
        title_sel="h3, h2, .title",
        link_sel="a",
    ),
    Company(
        name="Brandix I.T",
        careers_url="https://www.brandix.com/careers",
        size="enterprise", industry="enterprise",
        job_card_sel=".job-card, .vacancy, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Pearson Lanka",
        careers_url="https://pearson.jobs/sri-lanka/jobs/",
        size="enterprise", industry="edtech",
        job_card_sel=".job-result, .job-card, li.job",
        title_sel="h3, a.job-title",
        link_sel="a[href*='job']",
    ),
    Company(
        name="John Keells IT",
        careers_url="https://www.keells.com/careers",
        size="enterprise", industry="enterprise",
        job_card_sel=".vacancy, .job-item, article",
        title_sel="h3, h2",
        link_sel="a",
        needs_selenium=True,
    ),

    # ── Telecom ───────────────────────────────────────────────────
    Company(
        name="Dialog Axiata",
        careers_url="https://www.dialog.lk/careers",
        size="enterprise", industry="telecom",
        job_card_sel=".job-card, .vacancy, article",
        title_sel="h3, h2, .title",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="SLT Digital",
        careers_url="https://www.slt.lk/en/careers",
        size="enterprise", industry="telecom",
        job_card_sel=".job-card, .vacancy",
        title_sel="h3, h2",
        link_sel="a",
    ),

    # ── Mid-size / Growth ─────────────────────────────────────────
    Company(
        name="Cambio Software",
        careers_url="https://www.cambio.lk/careers",
        size="mid", industry="healthtech",
        job_card_sel=".job-card, article, .career-item",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Seylan Bank IT",
        careers_url="https://www.seylan.lk/careers",
        size="large", industry="fintech",
        job_card_sel=".vacancy, .job-card",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Calcey Technologies",
        careers_url="https://calcey.com/careers/",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, .career-listing, article",
        title_sel="h3, h2, .title",
        link_sel="a",
    ),
    Company(
        name="Embla Software",
        careers_url="https://www.embla.is/careers",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Rootcode Labs",
        careers_url="https://rootcodelabs.com/careers",
        size="mid", industry="startup",
        job_card_sel=".job-card, article, .position",
        title_sel="h3, h2",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="Arimac",
        careers_url="https://www.arimac.digital/careers",
        size="mid", industry="startup",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="Vesess",
        careers_url="https://vesess.com/careers",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Creative Software",
        careers_url="https://creativesoftware.com/careers/",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, .vacancy, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Mitra Innovation",
        careers_url="https://mitrais.com/careers/",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Wavenet",
        careers_url="https://www.wavenet.lk/careers",
        size="mid", industry="enterprise",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="DirectFN",
        careers_url="https://www.directfn.com/careers/",
        size="mid", industry="fintech",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),

    # ── Startups ──────────────────────────────────────────────────
    Company(
        name="PickMe",
        careers_url="https://pickme.lk/careers",
        size="startup", industry="startup",
        job_card_sel=".job-card, article, .career-item",
        title_sel="h3, h2, .title",
        link_sel="a",
        needs_selenium=True,
    ),
    Company(
        name="Takas.lk",
        careers_url="https://takas.lk/careers",
        size="startup", industry="ecommerce",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="ShoutOUT Labs",
        careers_url="https://shoutout.global/careers",
        size="startup", industry="startup",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Insighture",
        careers_url="https://insighture.com/careers",
        size="startup", industry="enterprise",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Enactor",
        careers_url="https://enactor.co/careers/",
        size="mid", industry="ecommerce",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Platformer",
        careers_url="https://platformer.com/careers",
        size="startup", industry="startup",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="GTN Technologies",
        careers_url="https://gtn.lk/careers/",
        size="mid", industry="fintech",
        job_card_sel=".job-card, article",
        title_sel="h3, h2",
        link_sel="a",
    ),
    Company(
        name="Axiata Digital Labs",
        careers_url="https://www.axiatadigitallabs.com/careers",
        size="large", industry="telecom",
        job_card_sel=".job-card, article, .position",
        title_sel="h3, h2",
        link_sel="a",
        needs_selenium=True,
    ),
]


# ══════════════════════════════════════════════════════════════════════
#  GENERIC SCRAPER LOGIC
# ══════════════════════════════════════════════════════════════════════

def _scrape_static(company: Company, session: requests.Session,
                   seen_fps: set) -> list[dict]:
    """Scrape a static-HTML careers page with requests + BS4."""
    resp = _get(session, company.careers_url)
    if resp is None:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs: list[dict] = []

    # Try structured card selectors first
    cards = []
    for sel in company.job_card_sel.split(","):
        sel = sel.strip()
        if sel:
            cards = soup.select(sel)
            if cards:
                break

    if cards:
        for card in cards:
            title = ""
            for t_sel in company.title_sel.split(","):
                t_el = card.select_one(t_sel.strip())
                if t_el:
                    title = _clean(t_el.get_text())
                    if title:
                        break

            link = ""
            for l_sel in company.link_sel.split(","):
                a_el = card.select_one(l_sel.strip())
                if a_el and a_el.get("href"):
                    href = a_el["href"]
                    if href.startswith("/"):
                        # Make absolute
                        from urllib.parse import urljoin
                        href = urljoin(company.careers_url, href)
                    link = href
                    break

            loc = company.location
            if company.location_sel:
                loc_el = card.select_one(company.location_sel)
                if loc_el:
                    loc = _clean(loc_el.get_text()) or company.location

            if title and len(title) > 3:
                fp = _fingerprint(title, company.name)
                if fp not in seen_fps:
                    seen_fps.add(fp)
                    jobs.append({
                        "job_title":   title,
                        "company_name": company.name,
                        "location":    loc,
                        "source_url":  link,
                    })
    else:
        # Fallback: look for any links that look job-related
        all_links = soup.find_all("a", href=True)
        for a in all_links:
            text = _clean(a.get_text())
            href = a["href"].lower()
            if (len(text) > 5 and
                any(kw in text.lower() for kw in
                    ["engineer", "developer", "analyst", "manager", "designer",
                     "architect", "lead", "senior", "junior", "intern",
                     "devops", "qa", "test", "data", "cloud", "security"])):
                fp = _fingerprint(text, company.name)
                if fp not in seen_fps:
                    seen_fps.add(fp)
                    from urllib.parse import urljoin
                    jobs.append({
                        "job_title":   text,
                        "company_name": company.name,
                        "location":    company.location,
                        "source_url":  urljoin(company.careers_url, a["href"]),
                    })

    return jobs


def _scrape_selenium(company: Company, headless: bool,
                     seen_fps: set) -> list[dict]:
    """Scrape a JS-rendered / SPA careers page with Selenium."""
    driver = _get_driver(headless)
    jobs: list[dict] = []

    try:
        driver.get(company.careers_url)
        _random_delay(3, 6)

        # Let page render
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            pass

        # Scroll to trigger lazy-load
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

        # Try card selectors
        cards = []
        for sel in company.job_card_sel.split(","):
            sel = sel.strip()
            if sel:
                cards = driver.find_elements(By.CSS_SELECTOR, sel)
                if cards:
                    break

        if cards:
            for card in cards:
                title = ""
                for t_sel in company.title_sel.split(","):
                    try:
                        t_el = card.find_element(By.CSS_SELECTOR, t_sel.strip())
                        title = _clean(t_el.text)
                        if title:
                            break
                    except NoSuchElementException:
                        pass

                link = ""
                for l_sel in company.link_sel.split(","):
                    try:
                        a_el = card.find_element(By.CSS_SELECTOR, l_sel.strip())
                        link = a_el.get_attribute("href") or ""
                        if link:
                            break
                    except NoSuchElementException:
                        pass

                if title and len(title) > 3:
                    fp = _fingerprint(title, company.name)
                    if fp not in seen_fps:
                        seen_fps.add(fp)
                        jobs.append({
                            "job_title":   title,
                            "company_name": company.name,
                            "location":    company.location,
                            "source_url":  link,
                        })
        else:
            # Fallback: scan all links on page
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for a in all_links:
                try:
                    text = _clean(a.text)
                    href = a.get_attribute("href") or ""
                    if (len(text) > 5 and
                        any(kw in text.lower() for kw in
                            ["engineer", "developer", "analyst", "manager",
                             "designer", "architect", "lead", "senior",
                             "junior", "intern", "devops", "qa",
                             "data", "cloud", "security"])):
                        fp = _fingerprint(text, company.name)
                        if fp not in seen_fps:
                            seen_fps.add(fp)
                            jobs.append({
                                "job_title":   text,
                                "company_name": company.name,
                                "location":    company.location,
                                "source_url":  href,
                            })
                except Exception:
                    continue

    except WebDriverException as exc:
        print(f"    ⚠ Selenium error for {company.name}: {exc}")

    return jobs


def _fetch_detail_static(session: requests.Session, url: str) -> dict:
    """Fetch a job detail page and extract description / requirements."""
    resp = _get(session, url)
    if resp is None:
        return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    body = _clean(soup.get_text(separator=" "))
    desc = body[:3000]
    reqs = ""
    m = re.search(
        r"(?:requirements?|qualifications?|must.have)[:\s]*(.{100,2000})",
        body, re.IGNORECASE
    )
    if m:
        reqs = m.group(1)[:1500]
    return {
        "description": desc,
        "requirements_text": reqs,
        "experience_raw": _extract_experience(body),
        "job_type": _detect_job_type(body),
    }


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape SL company career pages")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip detail page fetching for speed")
    parser.add_argument("--max-detail", type=int, default=20,
                        help="Max detail pages per company")
    args = parser.parse_args()

    print("=" * 70)
    print("  Company Careers Page Scraper")
    print(f"  Companies: {len(COMPANIES)}")
    print("=" * 70)

    session = _build_session()
    seen_fps: set = set()
    all_jobs: list[dict] = []

    for company in tqdm(COMPANIES, desc="Companies", unit="co"):
        print(f"\n  ▸ {company.name} ({company.careers_url})")

        if company.needs_selenium and HAS_SELENIUM:
            cards = _scrape_selenium(company, args.headless, seen_fps)
        else:
            cards = _scrape_static(company, session, seen_fps)

        print(f"    → found {len(cards)} positions")

        # Enrich with detail pages (sampled)
        detail_count = 0
        for job in cards:
            # Base fields
            job["industry"]    = company.industry
            job["source"]      = f"careers:{company.name}"
            job["scrape_date"] = datetime.now().isoformat()

            # Fetch detail if URL available and budget permits
            if (not args.dry_run and job.get("source_url")
                    and detail_count < args.max_detail):
                _random_delay(1, 3)
                details = _fetch_detail_static(session, job["source_url"])
                job["description"]      = details.get("description", "")
                job["requirements_text"] = details.get("requirements_text", "")
                job["experience_raw"]   = details.get("experience_raw", "")
                job["job_type"]         = details.get("job_type", "full-time")
                detail_count += 1
            else:
                job.setdefault("description", "")
                job.setdefault("requirements_text", "")
                job.setdefault("experience_raw", "")
                job.setdefault("job_type", "full-time")

            job.setdefault("salary_raw", "")
            job.setdefault("posted_date", "")

        all_jobs.extend(cards)
        _random_delay(1, 2)

    _close_driver()

    # Save
    df = pd.DataFrame(all_jobs)
    cols_order = [
        "job_title", "company_name", "description", "requirements_text",
        "salary_raw", "experience_raw", "job_type", "location", "industry",
        "posted_date", "source", "source_url", "scrape_date",
    ]
    for c in cols_order:
        if c not in df.columns:
            df[c] = ""
    df = df[cols_order]
    df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)

    print(f"\n{'=' * 70}")
    print(f"  DONE — {len(df)} jobs saved to {OUTPUT_CSV}")
    print(f"  Companies scraped: {len(COMPANIES)}")
    print(f"{'=' * 70}")

    if not df.empty:
        print(f"\n  By company:\n{df['company_name'].value_counts().to_string()}")
        print(f"\n  By industry:\n{df['industry'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
