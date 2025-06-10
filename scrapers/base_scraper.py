from abc import ABC, abstractmethod
import requests
import time
import re
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional, List

# Simple configuration constants (avoiding complex imports)
REQUEST_TIMEOUT = 30
REQUEST_RETRIES = 3
REQUEST_DELAY = 1
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


class BaseScraper(ABC):
    """Base scraper class for job sites"""

    def __init__(self, site_name: str, config: Dict):
        self.site_name = site_name
        self.config = config
        self.urls = config.get('urls', {})
        self.selectors = config.get('selectors', {})
        self.logger = logging.getLogger(f"{__name__}.{site_name}")

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'bg,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        for attempt in range(REQUEST_RETRIES):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                time.sleep(REQUEST_DELAY)  # Be nice to the server
                return soup

            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < REQUEST_RETRIES - 1:
                    time.sleep(REQUEST_DELAY * (attempt + 1))
                else:
                    self.logger.error(f"Failed to fetch {url} after {REQUEST_RETRIES} attempts")
                    return None

    def extract_job_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract job count from page using selectors and patterns"""
        if not soup:
            return None

        # Try CSS selectors first
        for selector in self.selectors.get('job_count', []):
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        count = int(numbers[0])
                        self.logger.info(f"Found job count {count} using selector '{selector}'")
                        return count
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        # Try fallback regex patterns on full page text
        page_text = soup.get_text()
        for pattern in self.selectors.get('fallback_patterns', []):
            try:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    self.logger.info(f"Found job count {count} using pattern '{pattern}'")
                    return count
            except Exception as e:
                self.logger.debug(f"Pattern '{pattern}' failed: {e}")
                continue

        self.logger.warning("Could not extract job count from page")
        return None

    def scrape_all_categories(self) -> Dict[str, Optional[int]]:
        """Scrape job counts for all categories"""
        results = {}

        for category, url in self.urls.items():
            self.logger.info(f"Scraping {category} jobs from {url}")
            soup = self.fetch_page(url)
            count = self.extract_job_count(soup)
            results[category] = count

            if count is not None:
                self.logger.info(f"{self.site_name} - {category}: {count} jobs")
            else:
                self.logger.error(f"Failed to get {category} job count from {self.site_name}")

        return results

    @abstractmethod
    def scrape(self) -> Dict[str, Optional[int]]:
        """Main scraping method - must be implemented by subclasses"""
        pass