#!/usr/bin/env python3
"""
Test script for detailed dev.bg category scraping
"""

import sys
from pathlib import Path

# Add scrapers directory to path
current_dir = Path(__file__).parent
scrapers_dir = current_dir / "scrapers"
sys.path.insert(0, str(scrapers_dir))


def test_detailed_dev_bg():
    """Test detailed dev.bg category scraping"""
    print("=== Testing detailed dev.bg category scraping ===")

    try:
        from utils import load_sites_config, setup_logging
        from dev_bg_scraper import DevBgScraper
        import re

        setup_logging("INFO")
        config = load_sites_config()

        if 'dev.bg' not in config:
            print("❌ No dev.bg config found")
            return False

        scraper = DevBgScraper(config['dev.bg'])

        # Test main page scraping
        print("Testing dev.bg main page for all categories...")
        soup = scraper.fetch_page("https://dev.bg/")
        if soup:
            print("✅ Page fetched successfully")

            # Test category extraction
            categories = scraper.extract_all_categories(soup)
            print(f"\n📊 Found {len(categories)} categories:")
            for cat, count in categories.items():
                print(f"  {cat}: {count} обяви")

            if categories:
                total = sum(categories.values())
                print(f"\n✅ Total jobs calculated: {total}")

                # Show the raw numbers we found
                numbers = list(categories.values())
                print(f"Raw numbers found: {numbers}")

            else:
                print("❌ No categories found")

            # Test full scraping method
            print("\n--- Testing full scrape method ---")
            results = scraper.scrape()
            print(f"Full scrape results:")
            for key, value in results.items():
                print(f"  {key}: {value}")

        else:
            print("❌ Failed to fetch page")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_manual_regex():
    """Manual test of regex pattern on dev.bg"""
    print("\n=== Manual regex test ===")

    try:
        import requests
        from bs4 import BeautifulSoup
        import re

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get('https://dev.bg/', headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()

            # Look for all numbers followed by "обяви"
            pattern = r'(\d+)\s*обяви?'
            matches = re.findall(pattern, text, re.IGNORECASE)

            print(f"All matches found: {matches}")

            if matches:
                numbers = [int(m) for m in matches if m.isdigit()]
                print(f"Numbers: {numbers}")
                print(f"Total: {sum(numbers)}")

        else:
            print(f"❌ Request failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ Manual test failed: {e}")


if __name__ == "__main__":
    print("=== Detailed Dev.BG Category Test ===")

    # Manual regex test first
    test_manual_regex()

    # Full detailed test
    test_detailed_dev_bg()

    print("\n=== Test completed ===")