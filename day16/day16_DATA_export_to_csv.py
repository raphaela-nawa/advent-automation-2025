"""
Day 16: Export SaaS metrics from SQLite to CSV for BigQuery upload
Exports all tables from Day 6 database to CSV format
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Configuration
DAY16_SOURCE_DB = "../day06/data/day06_saas_metrics.db"
DAY16_OUTPUT_DIR = "./data"

# Tables to export
DAY16_TABLES = [
    "day06_dashboard_kpis",
    "day06_mrr_summary",
    "day06_retention_curves",
    "day06_churn_by_cohort",
    "day06_customer_health",
    "day06_customers",
    "day06_subscriptions",
    "day06_mrr_movements"
]

def day16_export_table_to_csv(db_path: str, table_name: str, output_dir: str):
    """Export a single table to CSV"""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()

        # Save to CSV
        output_path = os.path.join(output_dir, f"{table_name}.csv")
        df.to_csv(output_path, index=False)

        print(f"✅ Exported {table_name}: {len(df)} rows → {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")
        return False

def day16_main():
    """Export all tables from Day 6 database"""
    print("=" * 60)
    print("Day 16: Exporting SaaS Metrics to CSV for BigQuery")
    print("=" * 60)

    # Create output directory
    Path(DAY16_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Check if source database exists
    if not os.path.exists(DAY16_SOURCE_DB):
        print(f"❌ Error: Database not found at {DAY16_SOURCE_DB}")
        return

    print(f"\n📂 Source: {DAY16_SOURCE_DB}")
    print(f"📂 Output: {DAY16_OUTPUT_DIR}\n")

    # Export each table
    success_count = 0
    for table in DAY16_TABLES:
        if day16_export_table_to_csv(DAY16_SOURCE_DB, table, DAY16_OUTPUT_DIR):
            success_count += 1

    print(f"\n{'=' * 60}")
    print(f"✅ Export complete: {success_count}/{len(DAY16_TABLES)} tables exported")
    print(f"{'=' * 60}")
    print("\nNext steps:")
    print("1. Upload CSV files to BigQuery")
    print("2. Use the SQL queries in day16_QUERIES_metabase.md")
    print("3. Connect Metabase Cloud to BigQuery")

if __name__ == "__main__":
    day16_main()
