from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class MOHEScholarshipScraper:
    def __init__(self):
        self.data = []
        self.source = 'MOHE (Government)'
        self.url = "https://mohe.gov.lk/index.php?option=com_content&view=category&layout=blog&id=42&Itemid=210&lang=en"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    def scrape(self):
        """Main scraping method for MOHE scholarships"""
        logger.info(f"Starting MOHE Scholarship Scraping from {self.url}")

        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(self.url)
            time.sleep(7)  # Give more time for page load

            # Try to wait for article content
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.TAG_NAME, "article"))
                )
            except:
                logger.warning(
                    "Article content not found immediately, continuing...")

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find article or main content area
            article = soup.find('article')
            if not article:
                article = soup.find(
                    'div', class_=['item-page', 'content', 'main-content'])

            if not article:
                logger.warning("Could not find main content area")
                driver.quit()
                return

            # Strategy 1: Try to extract from list items
            list_items = article.find_all('li')
            logger.info(f"Found {len(list_items)} list items")

            if list_items:
                self._extract_from_list_items(list_items)

            # Strategy 2: If no results, try paragraphs
            if len(self.data) == 0:
                logger.info("No list items found, trying paragraphs...")
                paragraphs = article.find_all('p')
                self._extract_from_paragraphs(paragraphs)

            # Strategy 3: Try headings followed by text
            if len(self.data) == 0:
                logger.info("No paragraphs matched, trying headings...")
                self._extract_from_headings(article)

            driver.quit()
            logger.info(
                f"MOHE scraping completed. Found {len(self.data)} scholarships")

        except Exception as e:
            logger.error(f"Error scraping MOHE: {e}")
            try:
                driver.quit()
            except:
                pass

    def _extract_from_list_items(self, list_items):
        """Extract scholarships from list items"""
        for li in list_items:
            text = li.get_text(strip=True)

            # Skip very short items
            if len(text) < 10:
                continue

            # Check if it looks like a scholarship entry
            if any(keyword in text.lower() for keyword in
                   ['scholarship', 'grant', 'award', 'fund', 'assistance', 'loan', 'bursary']):

                scholarship = self._create_scholarship_entry(text)

                # Avoid duplicates
                if scholarship['name'] not in [s['name'] for s in self.data]:
                    self.data.append(scholarship)
                    logger.debug(
                        f"Extracted scholarship: {scholarship['name'][:50]}")

    def _extract_from_paragraphs(self, paragraphs):
        """Extract scholarships from paragraph elements"""
        for para in paragraphs:
            text = para.get_text(strip=True)

            if len(text) > 20 and any(keyword in text.lower() for keyword in
                                      ['scholarship', 'grant', 'award', 'fund', 'bursary']):

                scholarship = self._create_scholarship_entry(text)

                if scholarship['name'] not in [s['name'] for s in self.data]:
                    self.data.append(scholarship)
                    logger.debug(
                        f"Extracted scholarship: {scholarship['name'][:50]}")

    def _extract_from_headings(self, article):
        """Extract scholarships from heading elements"""
        headings = article.find_all(['h2', 'h3', 'h4', 'h5'])

        for heading in headings:
            text = heading.get_text(strip=True)

            if len(text) > 10 and any(keyword in text.lower() for keyword in
                                      ['scholarship', 'grant', 'award', 'fund']):

                scholarship = self._create_scholarship_entry(text)

                # Try to get description from next paragraph
                next_para = heading.find_next('p')
                if next_para:
                    scholarship['description'] = next_para.get_text(strip=True)[
                        :500]

                if scholarship['name'] not in [s['name'] for s in self.data]:
                    self.data.append(scholarship)
                    logger.debug(
                        f"Extracted scholarship from heading: {scholarship['name'][:50]}")

    def _create_scholarship_entry(self, text):
        """Create a standardized scholarship entry"""
        scholarship = {
            'name': text[:200],
            'description': '',
            'eligibility': 'N/A',
            'funding_amount': 'N/A',
            'deadline': 'N/A',
            'contact': 'N/A',
            'application_url': 'N/A',
            'source': self.source,
            'url': self.url,
            'scrape_date': datetime.now().isoformat()
        }

        # Extract funding amount
        if 'Rs.' in text or 'LKR' in text or '$' in text or 'USD' in text:
            amount_match = re.search(r'(Rs\.|LKR|USD|\$)\s*([\d,]+)', text)
            if amount_match:
                scholarship['funding_amount'] = amount_match.group(0)

        # Extract deadline/dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY format
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                scholarship['deadline'] = match.group(0)
                break

        return scholarship

    def save_to_csv(self, filename=None):
        """Save data to CSV format"""
        if not self.data:
            logger.warning("No data to save")
            return

        if filename is None:
            filename = f'data/mohe_scholarships_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Saved {len(self.data)} scholarships to {filename}")
        return filename

def _to_standard_scholarship(record: Dict) -> Dict[str, str]:
    return {
        "name": record.get("name"),
        "provider": record.get("source") or "MOHE",
        "scholarship_type": "government",
        "description": record.get("description"),
        "eligibility": record.get("eligibility"),
        "benefits": record.get("funding_amount"),
        "deadline": record.get("deadline") or "rolling",
        "url": record.get("application_url") or record.get("url"),
        "country": "Sri Lanka",
        "degree_level": record.get("degree_level") or "unspecified",
        "field_of_study": record.get("field_of_study") or "various",
        "financial_need_required": record.get("financial_need_required", "unknown"),
        "source": record.get("source") or "MOHE",
    }


def run_scraper() -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    scraper = MOHEScholarshipScraper()
    try:
        scraper.scrape()
        for record in scraper.data:
            results.append(_to_standard_scholarship(record))
    except Exception as exc:
        logger.exception("MOHE scholarship scraper failed: %s", exc)
    return results
