"""
Day 14: Querido Diário API Helper
Andrea - Policy & Transport Analytics

Helper functions for interacting with Querido Diário public API
and calculating transport regulatory KPIs.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from day14_CONFIG_settings import (
    DAY14_API_GAZETTES_ENDPOINT,
    DAY14_TERRITORY_IDS,
    DAY14_SEARCH_KEYWORDS,
    DAY14_EXCERPT_SIZE,
    DAY14_NUMBER_OF_EXCERPTS,
    DAY14_RESULTS_SIZE,
    DAY14_API_RATE_LIMIT,
    DAY14_KPI_DEFINITIONS
)


class Day14QueridoDiarioClient:
    """Client for Querido Diário API interactions."""

    def __init__(self):
        self.base_url = DAY14_API_GAZETTES_ENDPOINT
        self.rate_limit_delay = 60 / DAY14_API_RATE_LIMIT  # seconds between requests
        self.last_request_time = 0

    def _respect_rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def query_gazettes(
        self,
        territory_id: str,
        query_string: str,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None
    ) -> Dict:
        """
        Query Querido Diário API for gazette publications.

        Args:
            territory_id: IBGE municipality code
            query_string: Search keywords
            since_date: Start date (YYYY-MM-DD format)
            until_date: End date (YYYY-MM-DD format)

        Returns:
            API response as dictionary
        """
        self._respect_rate_limit()

        params = {
            'territory_ids': territory_id,
            'querystring': query_string,
            'excerpt_size': DAY14_EXCERPT_SIZE,
            'number_of_excerpts': DAY14_NUMBER_OF_EXCERPTS,
            'size': DAY14_RESULTS_SIZE
        }

        if since_date:
            params['published_since'] = since_date
        if until_date:
            params['published_until'] = until_date

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {'total_gazettes': 0, 'gazettes': []}

    def query_multiple_cities(
        self,
        keyword: str,
        cities: Optional[List[str]] = None,
        since_date: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Query multiple cities for a specific keyword.

        Args:
            keyword: Search keyword
            cities: List of city names (keys from DAY14_TERRITORY_IDS)
            since_date: Start date for search

        Returns:
            Dictionary mapping city names to API responses
        """
        if cities is None:
            cities = list(DAY14_TERRITORY_IDS.keys())

        results = {}
        for city in cities:
            territory_id = DAY14_TERRITORY_IDS.get(city)
            if territory_id:
                print(f"Querying {city} for '{keyword}'...")
                results[city] = self.query_gazettes(
                    territory_id=territory_id,
                    query_string=keyword,
                    since_date=since_date
                )

        return results


class Day14KPICalculator:
    """Calculate transport regulatory KPIs from Querido Diário data."""

    @staticmethod
    def calculate_new_regulations_count(api_results: Dict[str, Dict]) -> int:
        """Count total new regulations across all cities."""
        total = 0
        for city_data in api_results.values():
            total += city_data.get('total_gazettes', 0)
        return total

    @staticmethod
    def calculate_active_municipalities(api_results: Dict[str, Dict]) -> int:
        """Count municipalities with at least one transport update."""
        active = 0
        for city_data in api_results.values():
            if city_data.get('total_gazettes', 0) > 0:
                active += 1
        return active

    @staticmethod
    def calculate_keyword_mentions(api_results: Dict[str, Dict], keywords: List[str]) -> int:
        """Count mentions of specific keywords in gazette excerpts."""
        mentions = 0
        for city_data in api_results.values():
            for gazette in city_data.get('gazettes', []):
                for excerpt in gazette.get('excerpts', []):
                    text = excerpt.lower()
                    for keyword in keywords:
                        mentions += text.count(keyword.lower())
        return mentions

    @staticmethod
    def generate_kpi_summary(
        transport_results: Dict[str, Dict],
        compliance_results: Optional[Dict[str, Dict]] = None,
        safety_results: Optional[Dict[str, Dict]] = None
    ) -> Dict:
        """
        Generate comprehensive KPI summary.

        Args:
            transport_results: Results from transport keyword queries
            compliance_results: Results from compliance keyword queries
            safety_results: Results from safety keyword queries

        Returns:
            Dictionary with all calculated KPIs
        """
        calculator = Day14KPICalculator()

        kpis = {
            'new_regulations': calculator.calculate_new_regulations_count(transport_results),
            'active_municipalities': calculator.calculate_active_municipalities(transport_results),
            'compliance_mentions': 0,
            'safety_incidents': 0,
            'timestamp': datetime.now().isoformat(),
            'cities_monitored': len(transport_results)
        }

        if compliance_results:
            kpis['compliance_mentions'] = calculator.calculate_keyword_mentions(
                compliance_results,
                DAY14_KPI_DEFINITIONS['compliance_mentions']['keywords']
            )

        if safety_results:
            kpis['safety_incidents'] = calculator.calculate_keyword_mentions(
                safety_results,
                DAY14_KPI_DEFINITIONS['safety_incidents']['keywords']
            )

        return kpis


def day14_fetch_daily_kpis(days_back: int = 1) -> Dict:
    """
    Fetch and calculate daily transport regulatory KPIs.

    Args:
        days_back: Number of days to look back (default: 1 for daily report)

    Returns:
        Dictionary with KPIs and supporting data
    """
    client = Day14QueridoDiarioClient()

    # Calculate date range
    until_date = datetime.now().strftime('%Y-%m-%d')
    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    print(f"Fetching transport data from {since_date} to {until_date}...")

    # Query for transport regulations
    transport_results = client.query_multiple_cities(
        keyword='transporte OR mobilidade',
        since_date=since_date
    )

    # Query for compliance mentions
    compliance_results = client.query_multiple_cities(
        keyword='prazo OR cumprimento OR fiscalização',
        since_date=since_date
    )

    # Query for safety incidents
    safety_results = client.query_multiple_cities(
        keyword='acidente OR segurança viária',
        since_date=since_date
    )

    # Calculate KPIs
    calculator = Day14KPICalculator()
    kpis = calculator.generate_kpi_summary(
        transport_results=transport_results,
        compliance_results=compliance_results,
        safety_results=safety_results
    )

    return {
        'kpis': kpis,
        'date_range': {'since': since_date, 'until': until_date},
        'raw_data': {
            'transport': transport_results,
            'compliance': compliance_results,
            'safety': safety_results
        }
    }


if __name__ == '__main__':
    """Test the API integration."""
    print("Testing Querido Diário API integration...")
    print("-" * 50)

    # Test single city query
    client = Day14QueridoDiarioClient()
    test_result = client.query_gazettes(
        territory_id=DAY14_TERRITORY_IDS['Sao_Paulo'],
        query_string='transporte',
        since_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    )

    print(f"São Paulo transport gazettes (last 7 days): {test_result.get('total_gazettes', 0)}")

    # Test KPI calculation
    print("\nFetching daily KPIs...")
    daily_kpis = day14_fetch_daily_kpis(days_back=1)

    print("\nKPI Summary:")
    print(json.dumps(daily_kpis['kpis'], indent=2))

    # Save sample data
    with open('./data/day14_querido_diario_cache.json', 'w', encoding='utf-8') as f:
        json.dump(daily_kpis, f, indent=2, ensure_ascii=False)

    print("\n✅ Sample data saved to ./data/day14_querido_diario_cache.json")
