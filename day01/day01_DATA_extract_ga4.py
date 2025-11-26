"""
Day 01 - GA4 Data Extraction
Attempts to extract from GA4 Demo Account, falls back to synthetic data.

PIVOT RULE: If GA4 API doesn't work within reasonable attempts, use synthetic data.

Usage:
    python day01_DATA_extract_ga4.py

    # Force synthetic data:
    python day01_DATA_extract_ga4.py --synthetic
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import argparse

# Import day01 configuration
import day01_CONFIG_settings as config


def day01_extract_ga4_real():
    """
    Attempt to extract real GA4 data from Demo Account.

    Returns:
        pd.DataFrame or None: GA4 data if successful, None if failed
    """
    print("🔄 Attempting to connect to GA4 Demo Account...")
    print(f"   Property ID: {config.day01_GA4_PROPERTY_ID}")

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.oauth2 import service_account

        # Check if credentials file exists
        if not os.path.exists(config.day01_GA4_CREDENTIALS_PATH):
            print(f"⚠️  Credentials file not found: {config.day01_GA4_CREDENTIALS_PATH}")
            print("   Pivoting to synthetic data...")
            return None

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            config.day01_GA4_CREDENTIALS_PATH
        )

        client = BetaAnalyticsDataClient(credentials=credentials)

        # Build request for last 30 days
        request = RunReportRequest(
            property=f"properties/{config.day01_GA4_PROPERTY_ID}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSource"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="conversions"),
                Metric(name="bounceRate"),
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        )

        response = client.run_report(request)

        # Parse response
        data = []
        for row in response.rows:
            data.append({
                'date': row.dimension_values[0].value,
                'source': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value),
                'conversions': int(row.metric_values[1].value),
                'bounce_rate': float(row.metric_values[2].value),
            })

        df = pd.DataFrame(data)

        # Format date
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        print(f"✅ Successfully extracted {len(df)} rows from GA4")
        return df

    except ImportError:
        print("⚠️  Google Analytics Data API library not installed")
        print("   Run: pip install google-analytics-data")
        print("   Pivoting to synthetic data...")
        return None
    except Exception as e:
        print(f"⚠️  Failed to extract GA4 data: {str(e)}")
        print("   Pivoting to synthetic data...")
        return None


def day01_generate_ga4_synthetic_data(days=None):
    """
    Generate synthetic GA4 session data.

    Args:
        days (int): Number of days of historical data to generate

    Returns:
        pd.DataFrame: Synthetic GA4 data with realistic metrics
    """
    if days is None:
        days = config.day01_SYNTHETIC_DAYS

    print(f"🔄 Generating {days} days of synthetic GA4 data...")

    data = []
    start_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = start_date + timedelta(days=i)

        # Generate data for each traffic source
        for source in config.day01_TRAFFIC_SOURCES:
            # Generate realistic session counts (varies by source)
            base_sessions = np.random.uniform(
                config.day01_GA4_SESSIONS_MIN,
                config.day01_GA4_SESSIONS_MAX
            )

            # Adjust by source (Google gets more traffic)
            if source == 'google':
                sessions = int(base_sessions * 1.5)
            elif source == 'direct':
                sessions = int(base_sessions * 1.2)
            elif source == 'facebook':
                sessions = int(base_sessions * 0.8)
            else:
                sessions = int(base_sessions * 0.5)

            # Conversion rate: 2-5% of sessions
            conversion_rate = np.random.uniform(
                config.day01_GA4_CONVERSION_RATE_MIN,
                config.day01_GA4_CONVERSION_RATE_MAX
            )
            conversions = int(sessions * conversion_rate)

            # Bounce rate: 35-55%
            bounce_rate = np.random.uniform(
                config.day01_GA4_BOUNCE_RATE_MIN,
                config.day01_GA4_BOUNCE_RATE_MAX
            )

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sessions': sessions,
                'conversions': conversions,
                'bounce_rate': round(bounce_rate, 4),
                'source': source
            })

    df = pd.DataFrame(data)
    print(f"✅ Generated {len(df)} rows of synthetic GA4 data")
    return df


def day01_save_ga4_data(df, file_path=None, is_synthetic=True):
    """
    Save GA4 data to CSV.

    Args:
        df (pd.DataFrame): GA4 data to save
        file_path (str): Path to save CSV file
        is_synthetic (bool): Whether data is synthetic or real
    """
    if file_path is None:
        file_path = config.day01_GA4_SYNTHETIC_FILE if is_synthetic else config.day01_RAW_DATA_DIR + '/ga4_real.csv'

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df.to_csv(file_path, index=False)
    print(f"💾 Saved {'synthetic' if is_synthetic else 'real'} GA4 data to: {file_path}")

    # Also save to processed directory
    processed_path = config.day01_GA4_PROCESSED_FILE
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"💾 Saved processed data to: {processed_path}")


def day01_show_ga4_summary(df):
    """Display summary statistics of the extracted/generated data."""
    print("\n" + "="*60)
    print("📊 GA4 DATA SUMMARY")
    print("="*60)
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Traffic sources: {df['source'].nunique()}")
    print(f"\nSources list:")
    for source in df['source'].unique():
        source_data = df[df['source'] == source]
        print(f"  - {source}: {source_data['sessions'].sum():,} sessions")
    print(f"\nMetrics summary:")
    print(f"  Total Sessions: {df['sessions'].sum():,}")
    print(f"  Total Conversions: {df['conversions'].sum():,}")
    print(f"  Avg Conversion Rate: {(df['conversions'].sum() / df['sessions'].sum() * 100):.2f}%")
    print(f"  Avg Bounce Rate: {df['bounce_rate'].mean():.2%}")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract GA4 data')
    parser.add_argument('--synthetic', action='store_true',
                       help='Force use of synthetic data (skip GA4 API attempt)')
    args = parser.parse_args()

    try:
        print("\n" + "="*60)
        print("🚀 DAY 01 - GA4 DATA EXTRACTION")
        print("="*60 + "\n")

        df_ga4 = None
        is_synthetic = False

        # Check config flag or command line argument
        if config.day01_USE_SYNTHETIC_DATA or args.synthetic:
            print("📋 Using synthetic data (configured or forced)")
            df_ga4 = day01_generate_ga4_synthetic_data()
            is_synthetic = True
        else:
            # Try real GA4 first
            df_ga4 = day01_extract_ga4_real()

            if df_ga4 is None:
                # Fall back to synthetic
                print("\n⚠️  PIVOT: Switching to synthetic data generation")
                df_ga4 = day01_generate_ga4_synthetic_data()
                is_synthetic = True

        # Save data
        day01_save_ga4_data(df_ga4, is_synthetic=is_synthetic)

        # Show summary
        day01_show_ga4_summary(df_ga4)

        print("✅ GA4 data extraction completed successfully!\n")
        print("Next steps:")
        if is_synthetic:
            print("  ℹ️  Note: Using synthetic data")
        print("  1. Run: python day01_DATA_load_bigquery.py")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
