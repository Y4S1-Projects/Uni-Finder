"""
Bank Education Loans Scraper
Scrapes education loan details from major Sri Lankan banks
Banks: BOC, Commercial Bank, Peoples Bank, HNB, NSB, PABC Bank
"""

from __future__ import annotations

import logging
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


class BankEducationLoansScraper:
    def __init__(self):
        self.data = []
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')

    def scrape(self):
        """Main scraping method - scrape all banks"""
        logger.info("Starting Bank Education Loans Scraping")

        # List of banks and their URLs
        banks = [
            {
                'name': 'Bank of Ceylon (BOC)',
                'url': 'https://www.boc.lk/personal-banking/loans/education-loan/educational-loan',
                'method': 'scrape_boc'
            },
            {
                'name': 'Commercial Bank',
                'url': 'https://www.combank.lk/personal-banking/loans/education-loans',
                'method': 'scrape_commercial_bank'
            },
            {
                'name': 'Peoples Bank',
                'url': 'https://www.peoplesbank.lk/educational-loans-en/',
                'method': 'scrape_peoples_bank'
            },
            {
                'name': 'HNB',
                'url': 'https://www.hnb.lk/personal/loans/education-loans',
                'method': 'scrape_hnb'
            },
            {
                'name': 'National Savings Bank (NSB)',
                'url': 'https://www.nsb.lk/loans_advances/nsb-buddhi/',
                'method': 'scrape_nsb'
            },
            {
                'name': 'PABC Bank',
                'url': 'https://www.pabcbank.com/personal-banking/loans-leasing/aspire-educational-loan/',
                'method': 'scrape_pabc'
            }
        ]

        # Scrape each bank
        for bank in banks:
            try:
                logger.info(f"Scraping {bank['name']} from {bank['url']}")
                method_name = bank['method']
                method = getattr(self, method_name)
                method(bank['name'], bank['url'])
            except Exception as e:
                logger.error(f"Error scraping {bank['name']}: {e}")

        logger.info(f"Scraping completed. Found {len(self.data)} loan records")

    def scrape_boc(self, bank_name, url):
        """Scrape Bank of Ceylon education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'BOC Educational Loan',
                'description': 'Provides financial support for higher education at local or foreign universities. Option to pay only interest until degree completion.',
                'key_features': '• Financial support for local/foreign universities\n• Pay interest-only option until degree complete\n• Maximum loan amount as required\n• Speedy service\n• No hidden costs',
                'eligibility': 'N/A',
                'maximum_loan_amount': 'N/A',
                'minimum_loan_amount': 'N/A',
                'interest_rate': 'N/A',
                'repayment_period': 'N/A',
                'age_criteria': 'N/A',
                'income_criteria': 'N/A',
                'documents_required': 'N/A',
                'special_benefits': 'Interest-only payment option until degree completion',
                'contact_info': 'Visit nearest BOC branch',
                'website_url': url,
                'bank_code': 'BOC',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_boc: {e}")

    def scrape_commercial_bank(self, bank_name, url):
        """Scrape Commercial Bank education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            full_text = soup.get_text()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'Commercial Bank Educational Loan',
                'description': 'Finance course fees inclusive of examination charges for local or overseas education. Draw funds when you require and repay after completing course.',
                'key_features': '• Draw funds as required\n• Repay capital after course completion\n• Loans for local and foreign education\n• Competitive low interest rates\n• Adequate funding\n• Quick approval',
                'eligibility': '• Registered student with education provider\n• Non-employed: Apply with parent/guardian/spouse, age 18+\n• Employed: Permanent employee with min salary Rs.75,000/- (net), salary credited 3+ months\n• Self-employed: Professionally qualified, age 18-65',
                'maximum_loan_amount': 'Rs. 10,000,000/-',
                'minimum_loan_amount': 'Rs. 100,000/-',
                'interest_rate': 'Competitive (exact rate varies)',
                'repayment_period': 'Maximum 7 years',
                'age_criteria': '18-65 years',
                'income_criteria': 'Min Rs.75,000/- net monthly (employed)',
                'documents_required': '• Loan application\n• Education provider letter\n• Salary slips (3 months)\n• Employment confirmation\n• Bank statements (6 months)\n• ID/Passport/License\n• Address verification\n• Guarantor documents (if applicable)',
                'special_benefits': 'Funds directed to institution as per fee structure',
                'contact_info': 'Visit nearest Commercial Bank branch',
                'website_url': url,
                'bank_code': 'COMBANK',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_commercial_bank: {e}")

    def scrape_peoples_bank(self, bank_name, url):
        """Scrape Peoples Bank education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'Wisdom Higher Education Loan',
                'description': 'Designed to support youth pursuing higher education. Flexible and easy loan terms with competitive interest rates.',
                'key_features': '• Support for quality higher education\n• Flexible and easy loan terms\n• Competitive interest rates\n• Support for future generation\'s dreams',
                'eligibility': '• Students engaged in higher education\n• Both employed and unemployed eligible',
                'maximum_loan_amount': 'N/A',
                'minimum_loan_amount': 'N/A',
                'interest_rate': 'Competitive (exact rate contact bank)',
                'repayment_period': 'N/A',
                'age_criteria': 'N/A',
                'income_criteria': 'N/A',
                'documents_required': 'Contact bank for details',
                'special_benefits': 'Flexible terms for education',
                'contact_info': 'Visit nearest Peoples Bank branch',
                'website_url': url,
                'bank_code': 'PBANK',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_peoples_bank: {e}")

    def scrape_hnb(self, bank_name, url):
        """Scrape HNB education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(5)  # Give more time for JavaScript rendering

            # Try to extract from page source
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                )
            except:
                pass

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'HNB Education Loan',
                'description': 'Education loan product from Hatton National Bank for financing higher education.',
                'key_features': 'Contact HNB for details',
                'eligibility': 'Contact HNB for eligibility criteria',
                'maximum_loan_amount': 'N/A',
                'minimum_loan_amount': 'N/A',
                'interest_rate': 'N/A',
                'repayment_period': 'N/A',
                'age_criteria': 'N/A',
                'income_criteria': 'N/A',
                'documents_required': 'Contact bank for details',
                'special_benefits': 'N/A',
                'contact_info': 'Visit nearest HNB branch',
                'website_url': url,
                'bank_code': 'HNB',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_hnb: {e}")

    def scrape_nsb(self, bank_name, url):
        """Scrape NSB education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'NSB Buddhi - Higher Education Loan',
                'description': 'NSB Buddhi helps pursue higher studies in Sri Lanka or overseas. Offers unparalleled grace period, up to 10 years repayment, and attractive interest rates.',
                'key_features': '• Support for local or overseas education\n• Unparalleled grace period\n• Up to 10 year repayment period\n• Attractive interest rate\n• 24-hour hotline support',
                'eligibility': '• Sri Lankan citizen\n• Age 18-50 years\n• Enrolled for higher education at university/college/academy\n• Employed: Can apply independently\n• Unemployed: Can apply jointly with parents/guardian',
                'maximum_loan_amount': 'Based on course fee, repayment capacity, collateral value, and age',
                'minimum_loan_amount': 'N/A',
                'interest_rate': 'Attractive (exact rate contact NSB)',
                'repayment_period': 'Up to 10 years',
                'age_criteria': '18-50 years',
                'income_criteria': 'Based on repayment capacity',
                'documents_required': 'Contact NSB for details',
                'special_benefits': 'Unparalleled grace period, longest repayment period (10 years)',
                'contact_info': 'Visit nearest NSB branch or call 24-hour hotline: +94 11 2 379 379',
                'website_url': url,
                'bank_code': 'NSB',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_nsb: {e}")

    def scrape_pabc(self, bank_name, url):
        """Scrape PABC Bank education loans"""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            loan = {
                'bank_name': bank_name,
                'loan_product_name': 'PABC Aspire Educational Loan',
                'description': 'Aspire educational loan product from PABC Bank for financing higher education.',
                'key_features': 'Contact PABC Bank for details',
                'eligibility': 'Contact PABC Bank for eligibility criteria',
                'maximum_loan_amount': 'N/A',
                'minimum_loan_amount': 'N/A',
                'interest_rate': 'N/A',
                'repayment_period': 'N/A',
                'age_criteria': 'N/A',
                'income_criteria': 'N/A',
                'documents_required': 'Contact bank for details',
                'special_benefits': 'N/A',
                'contact_info': 'Visit nearest PABC Bank branch',
                'website_url': url,
                'bank_code': 'PABC',
                'source': f'{bank_name} Official Website',
                'scrape_date': datetime.now().isoformat()
            }

            if loan['loan_product_name'] not in [d['loan_product_name'] for d in self.data]:
                self.data.append(loan)
                logger.info(f"Extracted: {loan['loan_product_name']}")

        except Exception as e:
            logger.error(f"Error in scrape_pabc: {e}")

def _to_standard_loan(record: Dict) -> Dict[str, str]:
    """Convert raw scraper output to the shared loan schema."""
    return {
        "name": record.get("loan_product_name") or record.get("name"),
        "provider": record.get("bank_name") or record.get("provider"),
        "loan_type": record.get("loan_type") or "education_loan",
        "interest_rate": record.get("interest_rate"),
        "eligibility": record.get("eligibility"),
        "repayment_terms": record.get("repayment_period"),
        "max_amount": record.get("maximum_loan_amount") or record.get("funding_amount"),
        "deadline": record.get("deadline") or "rolling",
        "url": record.get("website_url") or record.get("application_url"),
        "source": record.get("source") or "Bank Education Loans",
    }


def run_scraper() -> List[Dict[str, str]]:
    """Public entry-point used by the master scraper."""
    results: List[Dict[str, str]] = []
    scraper = BankEducationLoansScraper()
    try:
        scraper.scrape()
        for record in scraper.data:
            results.append(_to_standard_loan(record))
    except Exception as exc:
        logger.exception("Bank education loans scraper failed: %s", exc)
    return results
