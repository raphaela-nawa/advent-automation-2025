"""
Day 16: Generate retention curves from subscription data
Calculates cohort retention rates for visualization
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

# Configuration
DAY16_SOURCE_DB = "../day06/data/day06_saas_metrics.db"
DAY16_OUTPUT_CSV = "./data/day06_retention_curves.csv"

def day16_generate_retention_curves():
    """Generate cohort retention curves from subscription data"""
    print("=" * 60)
    print("Day 16: Generating Cohort Retention Curves")
    print("=" * 60)

    # Connect to database
    conn = sqlite3.connect(DAY16_SOURCE_DB)

    # Get subscriptions data
    query = """
    SELECT
        s.customer_id,
        s.start_date,
        s.end_date,
        s.plan_tier,
        c.signup_date,
        strftime('%Y-%m', c.signup_date) as cohort_month
    FROM day06_subscriptions s
    JOIN day06_customers c ON s.customer_id = c.customer_id
    WHERE s.start_date IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"\n📊 Loaded {len(df)} subscription records")

    # Convert dates
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])

    # Calculate months since signup for each subscription
    df['months_since_signup'] = ((df['start_date'].dt.year - df['signup_date'].dt.year) * 12 +
                                   (df['start_date'].dt.month - df['signup_date'].dt.month))

    # Group by cohort and month to calculate retention
    retention_data = []

    cohorts = df['cohort_month'].unique()
    print(f"\n📅 Processing {len(cohorts)} cohorts...")

    for cohort in sorted(cohorts):
        cohort_df = df[df['cohort_month'] == cohort]
        initial_customers = cohort_df['customer_id'].nunique()

        # For each month (0-12)
        for month in range(0, 13):
            # Count customers who had active subscription at this month
            active_at_month = cohort_df[
                (cohort_df['months_since_signup'] <= month) &
                ((cohort_df['end_date'].isna()) | (cohort_df['months_since_signup'] >= month))
            ]['customer_id'].nunique()

            retention_rate = (active_at_month / initial_customers * 100) if initial_customers > 0 else 0

            retention_data.append({
                'cohort_month': cohort,
                'months_since_signup': month,
                'customers_remaining': active_at_month,
                'cohort_size': initial_customers,
                'retention_rate_pct': round(retention_rate, 2)
            })

    # Create retention curves dataframe
    retention_df = pd.DataFrame(retention_data)

    print(f"\n✅ Generated {len(retention_df)} retention data points")

    # Save to CSV
    retention_df.to_csv(DAY16_OUTPUT_CSV, index=False)
    print(f"✅ Saved to: {DAY16_OUTPUT_CSV}")

    # Show sample
    print("\n📊 Sample retention curves:")
    print(retention_df.head(15))

    print("\n" + "=" * 60)
    print("✅ Retention curves generation complete!")
    print("=" * 60)

if __name__ == "__main__":
    day16_generate_retention_curves()
