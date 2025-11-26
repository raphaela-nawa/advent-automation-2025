"""
Day 01 - Google Ads Synthetic Data Generator
Generates realistic synthetic Google Ads campaign data since no free sandbox exists.

Usage:
    python day01_DATA_extract_ads.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Import day01 configuration
import day01_CONFIG_settings as config


def day01_generate_ads_synthetic_data(days=None, num_campaigns=None):
    """
    Generate synthetic Google Ads campaign data.

    Args:
        days (int): Number of days of historical data to generate
        num_campaigns (int): Number of campaigns to simulate

    Returns:
        pd.DataFrame: Synthetic Google Ads data with realistic metrics
    """
    if days is None:
        days = config.day01_SYNTHETIC_DAYS
    if num_campaigns is None:
        num_campaigns = config.day01_NUM_CAMPAIGNS

    print(f"🔄 Generating {days} days of synthetic Google Ads data for {num_campaigns} campaigns...")

    # Select campaigns
    campaigns = config.day01_CAMPAIGN_NAMES[:num_campaigns]

    data = []
    start_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = start_date + timedelta(days=i)

        for campaign in campaigns:
            # Generate realistic metrics
            spend = np.random.uniform(
                config.day01_ADS_SPEND_MIN,
                config.day01_ADS_SPEND_MAX
            )

            impressions = int(np.random.uniform(
                config.day01_ADS_IMPRESSIONS_MIN,
                config.day01_ADS_IMPRESSIONS_MAX
            ))

            # CTR (Click-Through Rate): 2-4%
            ctr = np.random.uniform(
                config.day01_ADS_CTR_MIN,
                config.day01_ADS_CTR_MAX
            )
            clicks = int(impressions * ctr)

            # Conversion rate: 3-8% of clicks
            conversion_rate = np.random.uniform(
                config.day01_ADS_CONVERSION_RATE_MIN,
                config.day01_ADS_CONVERSION_RATE_MAX
            )
            conversions = int(clicks * conversion_rate)

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'campaign_name': campaign,
                'spend': round(spend, 2),
                'clicks': clicks,
                'impressions': impressions,
                'conversions': conversions
            })

    df = pd.DataFrame(data)
    print(f"✅ Generated {len(df)} rows of synthetic Google Ads data")
    return df


def day01_save_ads_data(df, file_path=None):
    """
    Save Google Ads data to CSV.

    Args:
        df (pd.DataFrame): Ads data to save
        file_path (str): Path to save CSV file
    """
    if file_path is None:
        file_path = config.day01_ADS_SYNTHETIC_FILE

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df.to_csv(file_path, index=False)
    print(f"💾 Saved synthetic Google Ads data to: {file_path}")

    # Also save to processed directory
    processed_path = config.day01_ADS_PROCESSED_FILE
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"💾 Saved processed data to: {processed_path}")


def day01_show_ads_summary(df):
    """Display summary statistics of the generated data."""
    print("\n" + "="*60)
    print("📊 GOOGLE ADS SYNTHETIC DATA SUMMARY")
    print("="*60)
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Campaigns: {df['campaign_name'].nunique()}")
    print(f"\nCampaigns list:")
    for campaign in df['campaign_name'].unique():
        print(f"  - {campaign}")
    print(f"\nMetrics summary:")
    print(f"  Total Spend: ${df['spend'].sum():,.2f}")
    print(f"  Total Impressions: {df['impressions'].sum():,}")
    print(f"  Total Clicks: {df['clicks'].sum():,}")
    print(f"  Total Conversions: {df['conversions'].sum():,}")
    print(f"  Avg CTR: {(df['clicks'].sum() / df['impressions'].sum() * 100):.2f}%")
    print(f"  Avg Conversion Rate: {(df['conversions'].sum() / df['clicks'].sum() * 100):.2f}%")
    print(f"  Cost per Click: ${df['spend'].sum() / df['clicks'].sum():.2f}")
    print(f"  Cost per Conversion: ${df['spend'].sum() / df['conversions'].sum():.2f}")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("🚀 DAY 01 - GOOGLE ADS DATA EXTRACTION (SYNTHETIC)")
        print("="*60 + "\n")

        # Generate synthetic data
        df_ads = day01_generate_ads_synthetic_data()

        # Save to files
        day01_save_ads_data(df_ads)

        # Show summary
        day01_show_ads_summary(df_ads)

        print("✅ Google Ads data extraction completed successfully!\n")
        print("Next steps:")
        print("  1. Run: python day01_DATA_extract_ga4.py")
        print("  2. Run: python day01_DATA_load_bigquery.py")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
