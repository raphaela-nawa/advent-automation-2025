"""
Day 05: BigQuery Data Loading Script
Loads matched museum items and podcast mentions to BigQuery

Usage:
    python day05_DATA_load_bigquery.py
"""

import csv
from pathlib import Path
from google.cloud import bigquery
from google.api_core import exceptions
import sys
from datetime import datetime

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_GCP_PROJECT_ID,
    day05_BQ_DATASET,
    day05_BQ_TABLE,
    day05_BQ_LOCATION,
    day05_PROCESSED_DIR,
    day05_ensure_directories
)


class day05_BigQueryLoader:
    """Handles loading data to BigQuery"""

    def __init__(self):
        """Initialize BigQuery client"""
        print(f"🔄 Initializing BigQuery client...")
        print(f"   Project: {day05_GCP_PROJECT_ID}")
        print(f"   Dataset: {day05_BQ_DATASET}")
        print(f"   Table: {day05_BQ_TABLE}")

        self.client = bigquery.Client(project=day05_GCP_PROJECT_ID)
        self.dataset_id = f"{day05_GCP_PROJECT_ID}.{day05_BQ_DATASET}"
        self.table_id = f"{self.dataset_id}.{day05_BQ_TABLE}"

        print(f"✅ BigQuery client initialized")

    def day05_create_dataset_if_not_exists(self):
        """Create BigQuery dataset if it doesn't exist"""
        print(f"\n📦 Checking dataset: {day05_BQ_DATASET}")

        try:
            self.client.get_dataset(self.dataset_id)
            print(f"   ✅ Dataset already exists")
        except exceptions.NotFound:
            print(f"   🔄 Creating dataset...")

            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = day05_BQ_LOCATION
            dataset.description = "Day 05: Museu Ipiranga cultural data - podcast mentions and museum artifacts"

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"   ✅ Dataset created: {dataset.dataset_id}")

    def day05_create_table_schema(self) -> list:
        """Define BigQuery table schema"""
        return [
            bigquery.SchemaField("episode_id", "STRING", mode="REQUIRED", description="Episode identifier"),
            bigquery.SchemaField("item_mention", "STRING", mode="REQUIRED", description="How item was mentioned in podcast"),
            bigquery.SchemaField("timestamp", "STRING", mode="NULLABLE", description="Timestamp of mention (HH:MM:SS)"),
            bigquery.SchemaField("context", "STRING", mode="NULLABLE", description="Additional context from podcast"),
            bigquery.SchemaField("confidence", "STRING", mode="NULLABLE", description="GPT extraction confidence (high/medium/low)"),
            bigquery.SchemaField("matched", "BOOLEAN", mode="REQUIRED", description="Whether item was matched in Tainacan API"),
            bigquery.SchemaField("match_confidence", "FLOAT", mode="NULLABLE", description="Similarity score for match (0.0-1.0)"),
            bigquery.SchemaField("match_type", "STRING", mode="NULLABLE", description="Type of match (fuzzy_match/no_match)"),
            bigquery.SchemaField("tainacan_item_id", "STRING", mode="NULLABLE", description="Tainacan item ID"),
            bigquery.SchemaField("tainacan_title", "STRING", mode="NULLABLE", description="Official museum item title"),
            bigquery.SchemaField("tainacan_description", "STRING", mode="NULLABLE", description="Museum item description"),
            bigquery.SchemaField("tainacan_url", "STRING", mode="NULLABLE", description="URL to item in museum catalog"),
            bigquery.SchemaField("tainacan_metadata", "STRING", mode="NULLABLE", description="Additional metadata from Tainacan (JSON)"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED", description="When record was loaded to BigQuery"),
        ]

    def day05_create_or_replace_table(self):
        """Create or replace BigQuery table with schema"""
        print(f"\n📋 Creating table: {day05_BQ_TABLE}")

        schema = self.day05_create_table_schema()

        table = bigquery.Table(self.table_id, schema=schema)
        table.description = "Podcast museum item mentions matched with Tainacan API metadata"

        try:
            # Delete table if exists
            self.client.delete_table(self.table_id, not_found_ok=True)
            print(f"   🗑️  Deleted existing table (if any)")
        except Exception as e:
            print(f"   ⚠️  Error deleting table: {str(e)}")

        # Create new table
        table = self.client.create_table(table)
        print(f"   ✅ Table created: {table.table_id}")
        print(f"   📊 Schema: {len(schema)} columns")

    def day05_load_data_from_csv(self, csv_path: Path):
        """
        Load data from CSV to BigQuery using a LOAD job (batch), not streaming.
        This avoids streaming limits on the free tier.
        """
        print(f"\n📤 Loading data from: {csv_path.name} via LOAD job")

        job_config = bigquery.LoadJobConfig(
            autodetect=True,  # infer schema from CSV header
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        try:
            with open(csv_path, "rb") as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    self.table_id,
                    job_config=job_config,
                    location=day05_BQ_LOCATION,
                )

            print("   ⏳ Waiting for load job to finish...")
            load_job.result()

            destination_table = self.client.get_table(self.table_id)
            print(f"   ✅ Loaded {destination_table.num_rows} rows into {destination_table.full_table_id}")
            return destination_table.num_rows

        except Exception as e:
            print(f"   ❌ Load job failed: {str(e)}")
            return 0

    def day05_verify_data(self):
        """Verify loaded data with sample query"""
        print(f"\n🔍 Verifying loaded data...")

        query = f"""
        SELECT
            COUNT(*) as total_mentions,
            COUNTIF(matched) as matched_items,
            COUNTIF(NOT matched) as unmatched_items,
            ROUND(AVG(IF(matched, match_confidence, NULL)), 3) as avg_confidence
        FROM `{self.table_id}`
        """

        try:
            results = self.client.query(query).result()

            for row in results:
                print(f"   Total mentions: {row.total_mentions}")
                print(f"   ✅ Matched: {row.matched_items}")
                print(f"   ❌ Unmatched: {row.unmatched_items}")
                print(f"   📊 Avg confidence: {row.avg_confidence}")

        except Exception as e:
            print(f"   ⚠️  Verification query failed: {str(e)}")


def day05_main():
    """Main BigQuery loading pipeline"""
    print("=" * 80)
    print("Day 05: BigQuery Data Loading Pipeline")
    print("Museu Ipiranga Cultural Data")
    print("=" * 80)

    # Ensure directories
    day05_ensure_directories()

    # Check for matched items CSV
    csv_path = day05_PROCESSED_DIR / "matched_items.csv"

    if not csv_path.exists():
        print(f"\n❌ ERROR: Matched items CSV not found: {csv_path}")
        print("\n⚠️  Make sure you've run:")
        print("   1. python day05_DATA_transcribe_whisper.py")
        print("   2. python day05_PIPELINE_extract_items.py")
        print("   3. Manually validated items in items_to_validate.csv")
        print("   4. python day05_DATA_search_tainacan.py")
        sys.exit(1)

    # Initialize loader
    try:
        loader = day05_BigQueryLoader()
    except Exception as e:
        print(f"\n❌ ERROR initializing BigQuery client: {str(e)}")
        print("\n⚠️  Make sure:")
        print("   1. You have Google Cloud credentials configured")
        print("   2. DAY05_GCP_PROJECT_ID is set correctly in config/.env")
        print("   3. You have BigQuery permissions on the project")
        sys.exit(1)

    # Create dataset
    loader.day05_create_dataset_if_not_exists()

    # Load data
    rows_loaded = loader.day05_load_data_from_csv(csv_path)

    # Verify
    if rows_loaded > 0:
        loader.day05_verify_data()

    # Summary
    print("\n" + "=" * 80)
    print("✅ BigQuery Loading Complete!")
    print("=" * 80)
    print(f"📊 Table: {loader.table_id}")
    print(f"📈 Rows loaded: {rows_loaded}")
    print("\n🔍 Query your data:")
    print(f"   https://console.cloud.google.com/bigquery?project={day05_GCP_PROJECT_ID}")
    print("\n📝 Example query:")
    print(f"""
    SELECT
        episode_id,
        item_mention,
        timestamp,
        tainacan_title,
        match_confidence
    FROM `{loader.table_id}`
    WHERE matched = TRUE
    ORDER BY match_confidence DESC
    LIMIT 10;
    """)


if __name__ == "__main__":
    day05_main()
