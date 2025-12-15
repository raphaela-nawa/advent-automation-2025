"""
Day 14: Querido Diário API Helper with CloudScraper
Alternative implementation using cloudscraper library to bypass Cloudflare

Install: pip install cloudscraper
"""

import cloudscraper
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import time
from day14_CONFIG_settings import (
    DAY14_API_GAZETTES_ENDPOINT,
    DAY14_TERRITORY_IDS,
    DAY14_EXCERPT_SIZE,
    DAY14_NUMBER_OF_EXCERPTS,
    DAY14_RESULTS_SIZE,
)


class Day14CloudscraperClient:
    """Client using cloudscraper to bypass Cloudflare protection."""

    def __init__(self):
        # Create scraper with browser profile
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10  # Delay to solve challenges
        )
        self.base_url = DAY14_API_GAZETTES_ENDPOINT

    def query_gazettes(
        self,
        territory_id: str,
        query_string: str,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None
    ) -> Dict:
        """
        Query Querido Diário API using cloudscraper.

        Args:
            territory_id: IBGE municipality code
            query_string: Search keywords
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)

        Returns:
            API response as dictionary
        """
        params = {
            'territory_ids': territory_id,
            'querystring': query_string,
            'excerpt_size': DAY14_EXCERPT_SIZE,
            'number_of_excerpts': DAY14_NUMBER_OF_EXCERPTS,
            'size': DAY14_RESULTS_SIZE
        }

        if since_date:
            params['since'] = since_date
        if until_date:
            params['until'] = until_date

        try:
            print(f"  Querying {territory_id} with cloudscraper...")
            response = self.scraper.get(self.base_url, params=params, timeout=30)

            # Check if we got HTML (Cloudflare challenge page)
            if 'text/html' in response.headers.get('Content-Type', ''):
                print(f"  ⚠️  Got HTML response (possible Cloudflare block)")
                return {'total_gazettes': 0, 'gazettes': []}

            response.raise_for_status()
            data = response.json()
            print(f"  ✅ Success! Found {data.get('total_gazettes', 0)} gazettes")
            return data

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {'total_gazettes': 0, 'gazettes': []}

    def test_single_city(self, city_name: str = 'Sao_Paulo', days_back: int = 7) -> Dict:
        """
        Test API access with a single city.

        Args:
            city_name: City to test
            days_back: Days to look back

        Returns:
            API response
        """
        territory_id = DAY14_TERRITORY_IDS[city_name]
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        print(f"\nTesting cloudscraper with {city_name}...")
        print(f"Date range: {since_date} to today")

        result = self.query_gazettes(
            territory_id=territory_id,
            query_string='transporte',
            since_date=since_date
        )

        return result


def day14_test_cloudscraper():
    """Test if cloudscraper can bypass Cloudflare."""
    print("=" * 60)
    print("Testing Querido Diário API with CloudScraper")
    print("=" * 60)
    print()
    print("This attempts to bypass Cloudflare protection using:")
    print("- Real browser TLS fingerprint")
    print("- Automatic challenge solving")
    print("- Proper cookie management")
    print()
    print("=" * 60)
    print()

    client = Day14CloudscraperClient()

    # Test single query
    result = client.test_single_city('Sao_Paulo', days_back=7)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    if result.get('total_gazettes', 0) > 0:
        print("✅ SUCCESS! CloudScraper bypassed Cloudflare!")
        print(f"Found {result['total_gazettes']} gazettes")
        print("\nYou can now update day14_API_PROXY.py to use this client!")
    else:
        print("❌ Still blocked by Cloudflare")
        print("\nNext steps:")
        print("1. Try: pip install --upgrade cloudscraper")
        print("2. Try: curl_cffi (see CLOUDFLARE_WORKAROUND.md)")
        print("3. Try: undetected-chromedriver (slowest but most reliable)")
        print("4. Use: Synthetic data (current solution)")

    return result


if __name__ == '__main__':
    day14_test_cloudscraper()
