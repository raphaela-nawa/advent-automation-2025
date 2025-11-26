"""
Day 01 - BigQuery Data Loader
Loads GA4 and Google Ads data into BigQuery tables.

Usage:
    python day01_DATA_load_bigquery.py

    # Load specific table only:
    python day01_DATA_load_bigquery.py --table ga4
    python day01_DATA_load_bigquery.py --table ads
"""

import pandas as pd
import os
import sys
import argparse

# Import day01 configuration
import day01_CONFIG_settings as config


def day01_check_bigquery_available():
    """
    Check if BigQuery library is available.

    Returns:
        bool: True if available, False otherwise
    """
    try:
        from google.cloud import bigquery
        return True
    except ImportError:
        print("⚠️  Google Cloud BigQuery library not installed")
        print("   Run: pip install google-cloud-bigquery")
        return False


def day01_create_bigquery_client():
    """
    Create BigQuery client.

    Returns:
        bigquery.Client or None: Client if successful, None if failed
    """
    try:
        from google.cloud import bigquery

        # Check if project ID is configured
        if config.day01_GCP_PROJECT_ID == 'your-project-id':
            print("⚠️  BigQuery project ID not configured!")
            print("   Please set DAY01_GCP_PROJECT_ID in config/.env")
            return None

        client = bigquery.Client(project=config.day01_GCP_PROJECT_ID)
        print(f"✅ Connected to BigQuery project: {config.day01_GCP_PROJECT_ID}")
        return client

    except Exception as e:
        print(f"❌ Failed to create BigQuery client: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Ensure you have set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("  2. Or authenticate with: gcloud auth application-default login")
        print("  3. Verify your GCP project ID in config/.env")
        return None


def day01_ensure_dataset_exists(client, dataset_id):
    """
    Ensure BigQuery dataset exists, create if not.

    Args:
        client: BigQuery client
        dataset_id (str): Dataset ID

    Returns:
        bool: True if dataset exists/created, False otherwise
    """
    try:
        from google.cloud import bigquery

        dataset_ref = f"{client.project}.{dataset_id}"

        try:
            client.get_dataset(dataset_ref)
            print(f"✅ Dataset exists: {dataset_id}")
            return True
        except Exception:
            # Dataset doesn't exist, create it
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = config.day01_BQ_LOCATION
            dataset = client.create_dataset(dataset, exists_ok=True)
            print(f"✅ Created dataset: {dataset_id}")
            return True

    except Exception as e:
        print(f"❌ Failed to ensure dataset exists: {str(e)}")
        return False


def day01_load_to_bigquery(client, df, table_name, schema):
    """
    Load DataFrame to BigQuery table.

    Args:
        client: BigQuery client
        df (pd.DataFrame): Data to load
        table_name (str): Table name
        schema (list): BigQuery schema

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from google.cloud import bigquery

        # Construct table ID
        table_id = f"{client.project}.{config.day01_BQ_DATASET}.{table_name}"

        # Configure load job
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite table
        )

        # Load data
        print(f"🔄 Loading {len(df)} rows to {table_id}...")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

        # Wait for job to complete
        job.result()

        # Get table info
        table = client.get_table(table_id)
        print(f"✅ Loaded {table.num_rows} rows to {table_id}")

        return True

    except Exception as e:
        print(f"❌ Failed to load data to BigQuery: {str(e)}")
        return False


def day01_load_ga4_to_bigquery(client):
    """
    Load GA4 data to BigQuery.

    Args:
        client: BigQuery client

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("📊 LOADING GA4 DATA TO BIGQUERY")
    print("="*60)

    # Check if processed file exists
    if not os.path.exists(config.day01_GA4_PROCESSED_FILE):
        print(f"❌ GA4 data file not found: {config.day01_GA4_PROCESSED_FILE}")
        print("   Run: python day01_DATA_extract_ga4.py")
        return False

    # Read CSV
    df = pd.read_csv(config.day01_GA4_PROCESSED_FILE)
    print(f"📂 Loaded {len(df)} rows from {config.day01_GA4_PROCESSED_FILE}")

    # Convert date column to proper format
    df['date'] = pd.to_datetime(df['date']).dt.date

    # Load to BigQuery
    success = day01_load_to_bigquery(
        client,
        df,
        config.day01_GA4_TABLE,
        config.day01_GA4_SCHEMA
    )

    return success


def day01_load_ads_to_bigquery(client):
    """
    Load Google Ads data to BigQuery.

    Args:
        client: BigQuery client

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("📊 LOADING GOOGLE ADS DATA TO BIGQUERY")
    print("="*60)

    # Check if processed file exists
    if not os.path.exists(config.day01_ADS_PROCESSED_FILE):
        print(f"❌ Ads data file not found: {config.day01_ADS_PROCESSED_FILE}")
        print("   Run: python day01_DATA_extract_ads.py")
        return False

    # Read CSV
    df = pd.read_csv(config.day01_ADS_PROCESSED_FILE)
    print(f"📂 Loaded {len(df)} rows from {config.day01_ADS_PROCESSED_FILE}")

    # Convert date column to proper format
    df['date'] = pd.to_datetime(df['date']).dt.date

    # Load to BigQuery
    success = day01_load_to_bigquery(
        client,
        df,
        config.day01_ADS_TABLE,
        config.day01_ADS_SCHEMA
    )

    return success


def day01_verify_data_in_bigquery(client):
    """
    Verify data was loaded successfully by running COUNT queries.

    Args:
        client: BigQuery client
    """
    print("\n" + "="*60)
    print("🔍 VERIFYING DATA IN BIGQUERY")
    print("="*60)

    try:
        # Query GA4 table
        ga4_query = f"""
            SELECT COUNT(*) as row_count
            FROM `{client.project}.{config.day01_BQ_DATASET}.{config.day01_GA4_TABLE}`
        """
        ga4_result = client.query(ga4_query).result()
        ga4_count = list(ga4_result)[0].row_count
        print(f"✅ GA4 Sessions table: {ga4_count} rows")

        # Query Ads table
        ads_query = f"""
            SELECT COUNT(*) as row_count
            FROM `{client.project}.{config.day01_BQ_DATASET}.{config.day01_ADS_TABLE}`
        """
        ads_result = client.query(ads_query).result()
        ads_count = list(ads_result)[0].row_count
        print(f"✅ Google Ads Campaigns table: {ads_count} rows")

        # Show sample join query
        print("\n💡 Sample query to join both tables:")
        print(f"""
SELECT
  ga4.date,
  ga4.sessions,
  ga4.conversions as ga4_conversions,
  ads.campaign_name,
  ads.spend,
  ads.conversions as ads_conversions
FROM `{client.project}.{config.day01_BQ_DATASET}.{config.day01_GA4_TABLE}` ga4
JOIN `{client.project}.{config.day01_BQ_DATASET}.{config.day01_ADS_TABLE}` ads
  ON ga4.date = ads.date
WHERE ga4.source = 'google'
ORDER BY ga4.date DESC
LIMIT 10;
        """)

    except Exception as e:
        print(f"⚠️  Could not verify data: {str(e)}")


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Load data to BigQuery')
    parser.add_argument('--table', choices=['ga4', 'ads', 'both'], default='both',
                       help='Which table to load (default: both)')
    args = parser.parse_args()

    try:
        print("\n" + "="*60)
        print("🚀 DAY 01 - BIGQUERY DATA LOADER")
        print("="*60 + "\n")

        # Check if BigQuery library is available
        if not day01_check_bigquery_available():
            print("\n⚠️  BigQuery functionality not available")
            print("   Data has been saved to CSV files in data/processed/")
            print("   Install google-cloud-bigquery to enable BigQuery upload")
            sys.exit(1)

        # Create BigQuery client
        client = day01_create_bigquery_client()
        if client is None:
            print("\n⚠️  Could not create BigQuery client")
            print("   Data has been saved to CSV files in data/processed/")
            sys.exit(1)

        # Ensure dataset exists
        if not day01_ensure_dataset_exists(client, config.day01_BQ_DATASET):
            sys.exit(1)

        # Load data based on argument
        success_ga4 = True
        success_ads = True

        if args.table in ['ga4', 'both']:
            success_ga4 = day01_load_ga4_to_bigquery(client)

        if args.table in ['ads', 'both']:
            success_ads = day01_load_ads_to_bigquery(client)

        # Verify if both loads were requested and successful
        if args.table == 'both' and success_ga4 and success_ads:
            day01_verify_data_in_bigquery(client)

        # Final message
        print("\n" + "="*60)
        if success_ga4 and success_ads:
            print("✅ DATA LOAD COMPLETE!")
        else:
            print("⚠️  PARTIAL SUCCESS - Check errors above")
        print("="*60 + "\n")

        print("Next steps:")
        print("  1. Open BigQuery Console: https://console.cloud.google.com/bigquery")
        print(f"  2. Navigate to: {config.day01_GCP_PROJECT_ID} → {config.day01_BQ_DATASET}")
        print("  3. Run queries to analyze your data!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
