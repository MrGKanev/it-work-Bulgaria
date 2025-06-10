#!/usr/bin/env python3
"""
Job Tracker - Daily scraping of Bulgarian IT job sites
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add scrapers directory to path so we can import scrapers
current_dir = Path(__file__).parent
scrapers_dir = current_dir / "scrapers"
sys.path.insert(0, str(scrapers_dir))

# Import scrapers
from dev_bg_scraper import DevBgScraper
from jobs_bg_scraper import JobsBgScraper

# Import utilities
from utils import (
    load_sites_config,
    save_job_data,
    commit_and_push_changes,
    setup_logging,
    format_job_data_row
)

# Configuration
LOG_LEVEL = "INFO"


def main():
    """Main scraping function"""
    setup_logging(LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.info("=== Starting Job Tracker ===")

    # Load configuration
    sites_config = load_sites_config()
    if not sites_config:
        logger.error("No sites configuration found")
        return False

    # Current date
    current_date = datetime.now()
    logger.info(f"Scraping for date: {current_date.strftime('%Y-%m-%d')}")

    # Store all data rows
    all_data_rows = []

    # Scrape each site
    scrapers = {
        'dev.bg': DevBgScraper,
        'jobs.bg': JobsBgScraper
    }

    for site_name, scraper_class in scrapers.items():
        if site_name not in sites_config:
            logger.warning(f"No configuration found for {site_name}")
            continue

        logger.info(f"\n--- Scraping {site_name} ---")

        try:
            # Initialize scraper
            scraper = scraper_class(sites_config[site_name])

            # Perform scraping
            results = scraper.scrape()

            # Format and store results
            data_row = format_job_data_row(site_name, results, current_date)
            all_data_rows.append(data_row)

            # Log results
            logger.info(f"Results for {site_name}:")
            logger.info(f"  Total: {results.get('total', 'N/A')}")
            logger.info(f"  Ruse: {results.get('ruse', 'N/A')}")
            logger.info(f"  Remote: {results.get('remote', 'N/A')}")

        except Exception as e:
            logger.error(f"Error scraping {site_name}: {e}")
            # Add error row
            error_row = format_job_data_row(
                site_name,
                {'total': None, 'ruse': None, 'remote': None},
                current_date,
                f"Error: {str(e)}"
            )
            all_data_rows.append(error_row)

    # Save data to CSV
    if all_data_rows:
        try:
            csv_path = save_job_data(all_data_rows, current_date)
            logger.info(f"Data saved successfully to {csv_path}")

            # Commit and push to git
            if commit_and_push_changes(csv_path, current_date):
                logger.info("Changes committed and pushed to repository")
            else:
                logger.warning("Failed to commit/push changes")

        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    else:
        logger.error("No data to save")
        return False

    logger.info("=== Job Tracker completed successfully ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)