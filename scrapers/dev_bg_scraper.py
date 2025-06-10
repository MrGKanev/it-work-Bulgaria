from typing import Dict, Optional
from base_scraper import BaseScraper


class DevBgScraper(BaseScraper):
    """Scraper for dev.bg job site"""

    def __init__(self, config: Dict):
        super().__init__("dev.bg", config)

    def scrape(self) -> Dict[str, Optional[int]]:
        """Scrape job counts from dev.bg"""
        self.logger.info("Starting dev.bg scraping")

        results = self.scrape_all_categories()

        # Return standardized format
        return {
            'total': results.get('total'),
            'ruse': results.get('ruse'),
            'remote': results.get('remote')
        }