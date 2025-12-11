"""
Day 11 Data Fetcher
Fetches GA4 and Google Ads data from Day 01 sources (BigQuery or local CSV)

This module handles data retrieval with fallback logic:
1. Try BigQuery first (if enabled)
2. Fall back to local CSV files from Day 01
3. Generate synthetic data as last resort

Author: Gleyson - Retail Marketing Automation Specialist
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional
import sys

# Import Day 11 configuration
from day11_CONFIG_settings import (
    DAY11_USE_BIGQUERY,
    DAY11_USE_LOCAL_CSV,
    DAY11_GCP_PROJECT_ID,
    DAY11_BQ_DATASET,
    DAY11_BQ_GA4_TABLE,
    DAY11_BQ_ADS_TABLE,
    DAY11_DAY01_DATA_DIR,
    DAY11_REPORT_DAYS_BACK,
    DAY11_DATA_DIR,
    DAY11_RETRY_ATTEMPTS,
    DAY11_RETRY_DELAY_SECONDS,
)

# Set up logging
logger = logging.getLogger(__name__)


class Day11DataFetcher:
    """Fetches marketing data from Day 01 sources with fallback logic."""

    def __init__(self):
        self.bq_client = None
        self.data_source_used = None

    def day11_fetch_all_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], str]:
        """
        Fetch both GA4 and Google Ads data using fallback strategy.

        Returns:
            Tuple of (ga4_df, ads_df, source_message)
        """
        ga4_df = None
        ads_df = None
        source_message = ""

        # Strategy 1: Try BigQuery
        if DAY11_USE_BIGQUERY and DAY11_GCP_PROJECT_ID:
            logger.info("Attempting to fetch data from BigQuery...")
            try:
                ga4_df, ads_df = self._day11_fetch_from_bigquery()
                if ga4_df is not None and ads_df is not None:
                    source_message = "✓ Data fetched from BigQuery"
                    self.data_source_used = "BigQuery"
                    logger.info(source_message)
                    return ga4_df, ads_df, source_message
            except Exception as e:
                logger.warning(f"BigQuery fetch failed: {e}")

        # Strategy 2: Try local CSV files from Day 01
        if DAY11_USE_LOCAL_CSV:
            logger.info("Attempting to fetch data from local CSV files...")
            try:
                ga4_df, ads_df = self._day11_fetch_from_csv()
                if ga4_df is not None and ads_df is not None:
                    source_message = "✓ Data fetched from local CSV files (Day 01)"
                    self.data_source_used = "Local CSV"
                    logger.info(source_message)
                    return ga4_df, ads_df, source_message
            except Exception as e:
                logger.warning(f"CSV fetch failed: {e}")

        # Strategy 3: Generate synthetic data as fallback
        logger.warning("All data sources failed. Generating synthetic data...")
        ga4_df, ads_df = self._day11_generate_synthetic_data()
        source_message = "⚠️ Using synthetic data (no real data sources available)"
        self.data_source_used = "Synthetic"
        logger.info(source_message)

        return ga4_df, ads_df, source_message

    def _day11_fetch_from_bigquery(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch data from BigQuery tables."""
        from google.cloud import bigquery

        if self.bq_client is None:
            self.bq_client = bigquery.Client(project=DAY11_GCP_PROJECT_ID)

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=DAY11_REPORT_DAYS_BACK)

        # Fetch GA4 data
        ga4_query = f"""
        SELECT
            date,
            source,
            SUM(sessions) as sessions,
            SUM(conversions) as conversions,
            AVG(bounce_rate) as bounce_rate
        FROM `{DAY11_GCP_PROJECT_ID}.{DAY11_BQ_DATASET}.{DAY11_BQ_GA4_TABLE}`
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date, source
        ORDER BY date DESC
        """
        ga4_df = self.bq_client.query(ga4_query).to_dataframe()

        # Fetch Google Ads data
        ads_query = f"""
        SELECT
            date,
            campaign_name,
            SUM(spend) as spend,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            SUM(conversions) as conversions
        FROM `{DAY11_GCP_PROJECT_ID}.{DAY11_BQ_DATASET}.{DAY11_BQ_ADS_TABLE}`
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date, campaign_name
        ORDER BY date DESC
        """
        ads_df = self.bq_client.query(ads_query).to_dataframe()

        logger.info(f"Fetched {len(ga4_df)} GA4 rows and {len(ads_df)} Ads rows from BigQuery")
        return ga4_df, ads_df

    def _day11_fetch_from_csv(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch data from local CSV files (Day 01 output)."""
        ga4_csv_path = DAY11_DAY01_DATA_DIR / "ga4_sessions.csv"
        ads_csv_path = DAY11_DAY01_DATA_DIR / "ads_campaigns.csv"

        if not ga4_csv_path.exists() or not ads_csv_path.exists():
            raise FileNotFoundError(f"CSV files not found in {DAY11_DAY01_DATA_DIR}")

        ga4_df = pd.read_csv(ga4_csv_path)
        ads_df = pd.read_csv(ads_csv_path)

        # Convert date columns to datetime
        ga4_df['date'] = pd.to_datetime(ga4_df['date'])
        ads_df['date'] = pd.to_datetime(ads_df['date'])

        # Filter to last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DAY11_REPORT_DAYS_BACK)

        ga4_df = ga4_df[ga4_df['date'] >= start_date]
        ads_df = ads_df[ads_df['date'] >= start_date]

        logger.info(f"Loaded {len(ga4_df)} GA4 rows and {len(ads_df)} Ads rows from CSV")
        return ga4_df, ads_df

    def _day11_generate_synthetic_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate synthetic data for testing/demo purposes."""
        import random

        end_date = datetime.now().date()
        dates = [end_date - timedelta(days=i) for i in range(DAY11_REPORT_DAYS_BACK)]
        dates.reverse()

        # Generate GA4 synthetic data
        ga4_data = []
        sources = ['google', 'facebook', 'direct', 'email', 'linkedin']
        for date in dates:
            for source in sources:
                ga4_data.append({
                    'date': date,
                    'source': source,
                    'sessions': random.randint(500, 2000),
                    'conversions': random.randint(10, 60),
                    'bounce_rate': round(random.uniform(0.35, 0.55), 2)
                })

        ga4_df = pd.DataFrame(ga4_data)

        # Generate Google Ads synthetic data
        ads_data = []
        campaigns = ['Brand Campaign', 'Product Launch', 'Retargeting', 'Black Friday Special']
        for date in dates:
            for campaign in campaigns:
                ads_data.append({
                    'date': date,
                    'campaign_name': campaign,
                    'spend': round(random.uniform(300, 800), 2),
                    'clicks': random.randint(200, 600),
                    'impressions': random.randint(8000, 20000),
                    'conversions': random.randint(10, 35)
                })

        ads_df = pd.DataFrame(ads_data)

        logger.info(f"Generated {len(ga4_df)} synthetic GA4 rows and {len(ads_df)} synthetic Ads rows")
        return ga4_df, ads_df


def day11_calculate_metrics(ga4_df: pd.DataFrame, ads_df: pd.DataFrame) -> Dict:
    """
    Calculate key metrics for the performance report.

    Args:
        ga4_df: GA4 sessions dataframe
        ads_df: Google Ads campaigns dataframe

    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}

    # GA4 Metrics
    metrics['total_sessions'] = int(ga4_df['sessions'].sum())
    metrics['total_conversions_ga4'] = int(ga4_df['conversions'].sum())
    metrics['avg_bounce_rate'] = round(ga4_df['bounce_rate'].mean(), 2)

    # Top traffic source
    source_sessions = ga4_df.groupby('source')['sessions'].sum().sort_values(ascending=False)
    metrics['top_source'] = source_sessions.index[0] if len(source_sessions) > 0 else 'N/A'
    metrics['top_source_sessions'] = int(source_sessions.iloc[0]) if len(source_sessions) > 0 else 0

    # Google Ads Metrics
    metrics['total_spend'] = round(ads_df['spend'].sum(), 2)
    metrics['total_clicks'] = int(ads_df['clicks'].sum())
    metrics['total_impressions'] = int(ads_df['impressions'].sum())
    metrics['total_conversions_ads'] = int(ads_df['conversions'].sum())

    # Calculated metrics
    metrics['avg_ctr'] = round((metrics['total_clicks'] / metrics['total_impressions'] * 100), 2) if metrics['total_impressions'] > 0 else 0
    metrics['avg_cpc'] = round(metrics['total_spend'] / metrics['total_clicks'], 2) if metrics['total_clicks'] > 0 else 0
    metrics['cost_per_conversion'] = round(metrics['total_spend'] / metrics['total_conversions_ads'], 2) if metrics['total_conversions_ads'] > 0 else 0

    # Top campaign
    if len(ads_df) > 0:
        campaign_performance = ads_df.groupby('campaign_name').agg({
            'conversions': 'sum',
            'spend': 'sum'
        }).reset_index()
        campaign_performance['roas'] = campaign_performance['conversions'] / campaign_performance['spend']
        top_campaign = campaign_performance.sort_values('roas', ascending=False).iloc[0]
        metrics['top_campaign'] = top_campaign['campaign_name']
        metrics['top_campaign_conversions'] = int(top_campaign['conversions'])
        metrics['top_campaign_spend'] = round(top_campaign['spend'], 2)
    else:
        metrics['top_campaign'] = 'N/A'
        metrics['top_campaign_conversions'] = 0
        metrics['top_campaign_spend'] = 0.0

    # Date range
    if len(ga4_df) > 0:
        metrics['start_date'] = ga4_df['date'].min().strftime('%Y-%m-%d')
        metrics['end_date'] = ga4_df['date'].max().strftime('%Y-%m-%d')
        metrics['days_in_period'] = len(ga4_df['date'].unique())
    else:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        metrics['start_date'] = today
        metrics['end_date'] = today
        metrics['days_in_period'] = 0

    return metrics


if __name__ == "__main__":
    # Test the data fetcher
    logging.basicConfig(level=logging.INFO)

    print("Day 11 Data Fetcher Test")
    print("=" * 60)

    fetcher = Day11DataFetcher()
    ga4_df, ads_df, source_msg = fetcher.day11_fetch_all_data()

    print(f"\n{source_msg}")
    print(f"\nGA4 Data Shape: {ga4_df.shape if ga4_df is not None else 'N/A'}")
    print(f"Ads Data Shape: {ads_df.shape if ads_df is not None else 'N/A'}")

    if ga4_df is not None and ads_df is not None:
        print("\n--- Sample GA4 Data ---")
        print(ga4_df.head())

        print("\n--- Sample Ads Data ---")
        print(ads_df.head())

        print("\n--- Calculated Metrics ---")
        metrics = day11_calculate_metrics(ga4_df, ads_df)
        for key, value in metrics.items():
            print(f"{key}: {value}")

    print("=" * 60)
