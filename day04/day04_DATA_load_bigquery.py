"""
Day 04 - BigQuery Loader for Cardano Transparency Metrics
Loads on-chain transparency data into BigQuery for analysis

This script creates the BigQuery infrastructure and loads Cardano blockchain
transparency metrics, making them queryable for educational and analytical purposes.
"""

import pandas as pd
import sys
import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from day04_CONFIG_settings import (
    day04_GCP_PROJECT_ID,
    day04_BQ_DATASET,
    day04_BQ_TABLE,
    day04_BQ_TABLE_FULL,
    day04_BQ_LOCATION,
    day04_CSV_OUTPUT_PATH,
    day04_validate_config
)


class day04_BigQueryLoader:
    """
    Handles BigQuery dataset/table creation and data loading for Cardano metrics.
    """

    def __init__(self):
        """Initialize BigQuery client."""
        self.client = bigquery.Client(project=day04_GCP_PROJECT_ID)
        self.dataset_id = day04_BQ_DATASET
        self.table_id = day04_BQ_TABLE
        self.table_ref = day04_BQ_TABLE_FULL

    def day04_create_dataset_if_not_exists(self):
        """
        Create BigQuery dataset if it doesn't exist.

        Returns:
            google.cloud.bigquery.Dataset: The dataset object
        """
        dataset_full_id = f"{day04_GCP_PROJECT_ID}.{self.dataset_id}"

        try:
            dataset = self.client.get_dataset(dataset_full_id)
            print(f"✓ Dataset {dataset_full_id} already exists")
            return dataset

        except NotFound:
            print(f"📦 Creating dataset {dataset_full_id}...")

            dataset = bigquery.Dataset(dataset_full_id)
            dataset.location = day04_BQ_LOCATION
            dataset.description = (
                "Cardano blockchain transparency metrics - "
                "demonstrating on-chain visibility and decentralization"
            )

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"   ✓ Dataset created successfully")

            return dataset

    def day04_get_table_schema(self):
        """
        Define BigQuery table schema for Cardano transparency metrics.

        Returns:
            list: Schema definition for BigQuery table
        """
        return [
            bigquery.SchemaField(
                "timestamp",
                "TIMESTAMP",
                mode="REQUIRED",
                description="Timestamp when metrics were collected"
            ),
            bigquery.SchemaField(
                "total_transactions",
                "INTEGER",
                mode="REQUIRED",
                description="Total transactions in the epoch (demonstrates network usage)"
            ),
            bigquery.SchemaField(
                "active_addresses",
                "INTEGER",
                mode="NULLABLE",
                description="Estimated active addresses (demonstrates adoption)"
            ),
            bigquery.SchemaField(
                "block_count",
                "INTEGER",
                mode="REQUIRED",
                description="Number of blocks produced in the epoch"
            ),
            bigquery.SchemaField(
                "epoch",
                "INTEGER",
                mode="REQUIRED",
                description="Cardano epoch number (5-day periods)"
            ),
            bigquery.SchemaField(
                "stake_pools_active",
                "INTEGER",
                mode="REQUIRED",
                description="Number of active stake pools (demonstrates decentralization - typically 3000+)"
            ),
            bigquery.SchemaField(
                "total_ada_staked",
                "FLOAT64",
                mode="REQUIRED",
                description="Total ADA staked in the network (demonstrates trust/participation)"
            ),
            bigquery.SchemaField(
                "avg_transaction_fee",
                "FLOAT64",
                mode="REQUIRED",
                description="Average transaction fee in USD (demonstrates accessibility - typically ~$0.17)"
            ),
        ]

    def day04_create_table_if_not_exists(self):
        """
        Create BigQuery table with transparency metrics schema if it doesn't exist.

        Returns:
            google.cloud.bigquery.Table: The table object
        """
        try:
            table = self.client.get_table(self.table_ref)
            print(f"✓ Table {self.table_ref} already exists")
            return table

        except NotFound:
            print(f"📊 Creating table {self.table_ref}...")

            schema = self.day04_get_table_schema()

            table = bigquery.Table(self.table_ref, schema=schema)
            table.description = (
                "Cardano blockchain transparency metrics extracted via Blockfrost API. "
                "Demonstrates: (1) Network transparency - all transactions visible, "
                "(2) Decentralization - 3000+ stake pools, "
                "(3) Accessibility - low fees (~$0.17/tx)"
            )

            table = self.client.create_table(table)
            print(f"   ✓ Table created with {len(schema)} columns")

            return table

    def day04_load_csv_to_bigquery(self):
        """
        Load CSV data into BigQuery table.

        Returns:
            google.cloud.bigquery.job.LoadJob: The completed load job
        """
        print(f"\n📤 Loading data from {day04_CSV_OUTPUT_PATH}...")

        # Check if CSV exists
        if not os.path.exists(day04_CSV_OUTPUT_PATH):
            raise FileNotFoundError(
                f"CSV file not found: {day04_CSV_OUTPUT_PATH}\n"
                "   → Run day04_DATA_extract_blockfrost.py first"
            )

        # Read CSV to validate
        df = pd.read_csv(day04_CSV_OUTPUT_PATH)
        print(f"   ✓ Found {len(df)} rows to load")
        print(f"   ✓ Columns: {', '.join(df.columns.tolist())}")

        # Configure load job
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Skip header
            autodetect=False,
            schema=self.day04_get_table_schema(),
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        # Load data
        with open(day04_CSV_OUTPUT_PATH, "rb") as source_file:
            load_job = self.client.load_table_from_file(
                source_file,
                self.table_ref,
                job_config=job_config
            )

        # Wait for job to complete
        print(f"   ⏳ Loading to BigQuery...")
        load_job.result()  # Waits for job to complete

        # Get destination table
        destination_table = self.client.get_table(self.table_ref)

        print(f"   ✓ Loaded {load_job.output_rows} rows")
        print(f"   ✓ Total rows in table: {destination_table.num_rows}")

        return load_job

    def day04_display_sample_data(self, limit=5):
        """
        Query and display sample data from the table.

        Args:
            limit (int): Number of rows to display
        """
        print(f"\n📋 Sample data from {self.table_ref}:")
        print("-" * 80)

        query = f"""
            SELECT
                timestamp,
                epoch,
                total_transactions,
                stake_pools_active,
                ROUND(total_ada_staked, 0) as total_ada_staked,
                avg_transaction_fee
            FROM `{self.table_ref}`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """

        query_job = self.client.query(query)
        results = query_job.result()

        for row in results:
            print(f"  Epoch {row.epoch} | {row.timestamp}")
            print(f"    Transactions: {row.total_transactions:,}")
            print(f"    Stake Pools: {row.stake_pools_active:,} (decentralization)")
            print(f"    ADA Staked: {row.total_ada_staked:,.0f}")
            print(f"    Avg Fee: ${row.avg_transaction_fee:.2f}")
            print()

    def day04_display_analysis_queries(self):
        """
        Display example SQL queries for analyzing transparency metrics.
        """
        print("\n" + "="*80)
        print("📊 EXAMPLE ANALYSIS QUERIES")
        print("="*80)

        queries = [
            {
                "title": "Prove Decentralization",
                "query": f"""
SELECT
  AVG(stake_pools_active) as avg_active_pools,
  MIN(stake_pools_active) as min_pools,
  MAX(stake_pools_active) as max_pools
FROM `{self.table_ref}`
-- Cardano: ~3000 pools vs Bitcoin: ~5 mining pools control 51%
                """.strip()
            },
            {
                "title": "Prove Low Fees",
                "query": f"""
SELECT
  AVG(avg_transaction_fee) as avg_fee_usd
FROM `{self.table_ref}`
-- Cardano: ~$0.17/tx vs Ethereum: $5-50/tx
                """.strip()
            },
            {
                "title": "Network Growth Over Time",
                "query": f"""
SELECT
  DATE(timestamp) as date,
  SUM(total_transactions) as daily_transactions,
  AVG(total_ada_staked) as avg_ada_staked
FROM `{self.table_ref}`
GROUP BY date
ORDER BY date DESC
LIMIT 30
                """.strip()
            }
        ]

        for i, q in enumerate(queries, 1):
            print(f"\n{i}. {q['title']}:")
            print("-" * 80)
            print(q['query'])
            print()


def main():
    """Main execution function."""
    try:
        print("="*80)
        print("🔗 CARDANO TRANSPARENCY METRICS → BIGQUERY LOADER")
        print("="*80 + "\n")

        # Validate configuration
        print("🔧 Validating configuration...")
        day04_validate_config()
        print()

        # Initialize loader
        loader = day04_BigQueryLoader()

        # Create dataset
        print("📦 Setting up BigQuery infrastructure...")
        loader.day04_create_dataset_if_not_exists()

        # Create table
        loader.day04_create_table_if_not_exists()
        print()

        # Load data
        loader.day04_load_csv_to_bigquery()

        # Display sample
        loader.day04_display_sample_data()

        # Show analysis queries
        loader.day04_display_analysis_queries()

        print("="*80)
        print("✅ SUCCESS! Cardano transparency metrics loaded to BigQuery")
        print("="*80)
        print(f"\n🔍 View in BigQuery Console:")
        print(f"   https://console.cloud.google.com/bigquery?project={day04_GCP_PROJECT_ID}&d={day04_BQ_DATASET}&t={day04_BQ_TABLE}\n")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}\n")
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Troubleshooting:")
        print("   → Ensure you have run 'gcloud auth application-default login'")
        print("   → Verify GCP_PROJECT_ID is correct")
        print("   → Check you have BigQuery permissions\n")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
