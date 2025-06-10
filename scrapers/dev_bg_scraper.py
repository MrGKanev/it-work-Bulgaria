from typing import Dict, Optional, List
from base_scraper import BaseScraper
import re


class DevBgScraper(BaseScraper):
    """Scraper for dev.bg job site with detailed category breakdown"""

    def __init__(self, config: Dict):
        super().__init__("dev.bg", config)

    def extract_all_categories(self, soup) -> Dict[str, int]:
        """Extract job counts for all categories from main page"""
        if not soup:
            return {}

        page_text = soup.get_text()
        categories = {}

        # Multiple patterns to handle encoding issues
        patterns = [
            r'(\d+)\s*обяви',  # Standard Bulgarian
            r'(\d+)\s*обява',  # Singular form
            r'(\d+)\s*obyavi',  # Transliterated
            r'(\d+)\s*obyava',  # Transliterated singular
        ]

        all_numbers = []

        for pattern in patterns:
            try:
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.UNICODE)
                if matches:
                    self.logger.debug(f"Pattern '{pattern}' found: {matches}")
                    for match in matches:
                        if match.isdigit():
                            num = int(match)
                            if num not in all_numbers:  # Avoid duplicates
                                all_numbers.append(num)
            except Exception as e:
                self.logger.debug(f"Pattern '{pattern}' failed: {e}")
                continue

        # If no patterns worked, look for job count numbers in a smarter way
        if not all_numbers:
            self.logger.warning("No job patterns found, looking for reasonable job count numbers")

            # Find all numbers and filter for reasonable job counts
            number_matches = re.findall(r'\b(\d+)\b', page_text)
            potential_numbers = []

            for n in number_matches:
                if n.isdigit():
                    num = int(n)
                    # Filter for reasonable job counts (between 10 and 5000)
                    if 10 <= num <= 5000:
                        potential_numbers.append(num)

            # Remove duplicates while preserving order
            seen = set()
            all_numbers = []
            for num in potential_numbers:
                if num not in seen:
                    seen.add(num)
                    all_numbers.append(num)

            self.logger.info(f"Found potential job count numbers: {all_numbers}")

        if all_numbers:
            # Store as categories
            for i, count in enumerate(all_numbers):
                categories[f'category_{i + 1}'] = count
            self.logger.info(f"Found {len(categories)} categories with job counts: {all_numbers}")
        else:
            self.logger.error("No reasonable job count numbers found")
            # Debug: show sample of page text
            sample_text = page_text[:500] if page_text else "No text found"
            self.logger.debug(f"Sample page text: {sample_text}")

        return categories

    def scrape_detailed_categories(self) -> Dict:
        """Scrape detailed breakdown of all job categories"""
        self.logger.info("Starting detailed dev.bg category scraping")

        # Scrape main page for all categories
        soup = self.fetch_page(self.urls.get('total'))
        if not soup:
            return {'error': 'Could not fetch main page'}

        # Extract all categories
        categories = self.extract_all_categories(soup)

        if not categories:
            self.logger.error("No categories found")
            return {'error': 'No categories found'}

        # Calculate total
        total_jobs = sum(categories.values())

        # Also get specific location data
        ruse_count = None
        remote_count = None

        # Scrape Ruse page
        if 'ruse' in self.urls:
            ruse_soup = self.fetch_page(self.urls['ruse'])
            if ruse_soup:
                ruse_count = self.extract_job_count(ruse_soup)

        # Scrape Remote page
        if 'remote' in self.urls:
            remote_soup = self.fetch_page(self.urls['remote'])
            if remote_soup:
                remote_count = self.extract_job_count(remote_soup)

        result = {
            'total': total_jobs,
            'ruse': ruse_count,
            'remote': remote_count,
            'categories': categories,
            'category_breakdown': f"Total categories: {len(categories)}, Jobs per category: {list(categories.values())}"
        }

        self.logger.info(f"dev.bg detailed results: Total={total_jobs}, Categories={len(categories)}")
        return result

    def scrape(self) -> Dict[str, Optional[int]]:
        """Main scrape method - now with detailed category breakdown"""
        detailed_results = self.scrape_detailed_categories()

        # Return in expected format but with additional data
        return {
            'total': detailed_results.get('total'),
            'ruse': detailed_results.get('ruse'),
            'remote': detailed_results.get('remote'),
            'categories_detail': detailed_results.get('category_breakdown', ''),
            'raw_categories': detailed_results.get('categories', {})
        }