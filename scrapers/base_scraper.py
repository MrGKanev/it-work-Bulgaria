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
REQUEST_DELAY = 2  # Increased delay to be more polite
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'bg,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage with proper encoding handling"""
        for attempt in range(REQUEST_RETRIES):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                # Set proper encoding to handle Bulgarian characters
                if response.encoding is None or response.encoding == 'ISO-8859-1':
                    response.encoding = 'utf-8'

                # Parse with proper encoding
                soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
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

        # First try regex patterns on full page text (more reliable for dev.bg)
        page_text = soup.get_text()
        all_numbers = []

        for pattern in self.selectors.get('fallback_patterns', []):
            try:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                self.logger.debug(f"Pattern '{pattern}' found matches: {matches}")
                for match in matches:
                    if isinstance(match, str) and match.isdigit():
                        all_numbers.append(int(match))
                        self.logger.debug(f"Added number: {match}")
            except Exception as e:
                self.logger.debug(f"Pattern '{pattern}' failed: {e}")
                continue

        # If we found numbers, return the largest one (most likely to be total)
        if all_numbers:
            count = max(all_numbers)
            self.logger.info(f"Found job count {count} from text patterns (max of {all_numbers})")
            return count

        # Try CSS selectors as fallback
        for selector in self.selectors.get('job_count', []):
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        count = int(numbers[0])
                        self.logger.info(f"Found job count {count} using selector '{selector}'")
                        return count
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
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