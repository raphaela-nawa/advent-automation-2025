"""
Day 03 - BigQuery Data Loading Module
Handles BigQuery table creation and data insertion for GDPR leads.
"""

import logging
from typing import List, Dict
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from day03_CONFIG_settings import (
    DAY03_GCP_PROJECT_ID,
    DAY03_BQ_DATASET,
    DAY03_BQ_TABLE,
    DAY03_BQ_LOCATION,
    DAY03_BQ_SCHEMA
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class day03_BigQueryLoader:
    """Handles BigQuery operations for GDPR leads."""

    def __init__(self):
        """Initialize BigQuery client and configuration."""
        self.client = bigquery.Client(project=DAY03_GCP_PROJECT_ID)
        self.dataset_id = f"{DAY03_GCP_PROJECT_ID}.{DAY03_BQ_DATASET}"
        self.table_id = f"{self.dataset_id}.{DAY03_BQ_TABLE}"
        self.location = DAY03_BQ_LOCATION

    def day03_ensure_dataset_exists(self) -> None:
        """Creates dataset if it doesn't exist."""
        try:
            self.client.get_dataset(self.dataset_id)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            logger.info(f"Creating dataset {self.dataset_id}")
            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = self.location
            self.client.create_dataset(dataset, timeout=30)
            logger.info(f"Dataset {self.dataset_id} created successfully")

    def day03_ensure_table_exists(self) -> None:
        """Creates table with GDPR schema if it doesn't exist."""
        try:
            self.client.get_table(self.table_id)
            logger.info(f"Table {self.table_id} already exists")
        except NotFound:
            logger.info(f"Creating table {self.table_id}")

            # Convert schema list to BigQuery SchemaField objects
            schema = [
                bigquery.SchemaField(
                    field["name"],
                    field["type"],
                    mode=field.get("mode", "NULLABLE")
                )
                for field in DAY03_BQ_SCHEMA
            ]

            table = bigquery.Table(self.table_id, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Table {self.table_id} created successfully")

    def day03_insert_lead(self, lead: Dict) -> bool:
        """
        Inserts a single lead into BigQuery.

        Args:
            lead: Processed lead dictionary

        Returns:
            True if successful, False otherwise
        """
        return self.day03_insert_leads([lead])

    def day03_insert_leads(self, leads: List[Dict]) -> bool:
        """
        Inserts multiple leads into BigQuery.

        Args:
            leads: List of processed lead dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure dataset and table exist
            self.day03_ensure_dataset_exists()
            self.day03_ensure_table_exists()

            # Insert rows
            errors = self.client.insert_rows_json(self.table_id, leads)

            if errors:
                logger.error(f"Errors occurred while inserting rows: {errors}")
                return False

            logger.info(f"Successfully inserted {len(leads)} lead(s) into {self.table_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert leads into BigQuery: {str(e)}")
            return False

    def day03_query_leads(self, limit: int = 10) -> List[Dict]:
        """
        Queries recent leads from BigQuery.

        Args:
            limit: Number of leads to retrieve

        Returns:
            List of lead dictionaries
        """
        try:
            query = f"""
                SELECT
                    lead_id,
                    name,
                    email,
                    consent_timestamp,
                    consent_purpose,
                    consent_given,
                    data_retention_date,
                    ip_address,
                    created_at
                FROM `{self.table_id}`
                ORDER BY created_at DESC
                LIMIT {limit}
            """

            query_job = self.client.query(query)
            results = query_job.result()

            leads = [dict(row) for row in results]
            logger.info(f"Retrieved {len(leads)} lead(s) from {self.table_id}")
            return leads

        except Exception as e:
            logger.error(f"Failed to query leads from BigQuery: {str(e)}")
            return []

    def day03_count_leads(self) -> int:
        """
        Counts total number of leads in BigQuery.

        Returns:
            Total count of leads
        """
        try:
            query = f"SELECT COUNT(*) as total FROM `{self.table_id}`"
            query_job = self.client.query(query)
            results = query_job.result()

            for row in results:
                return row.total

            return 0

        except Exception as e:
            logger.error(f"Failed to count leads: {str(e)}")
            return 0


def day03_load_lead_to_bigquery(lead: Dict) -> bool:
    """
    Convenience function to load a single lead to BigQuery.

    Args:
        lead: Processed lead dictionary

    Returns:
        True if successful, False otherwise
    """
    loader = day03_BigQueryLoader()
    return loader.day03_insert_lead(lead)


if __name__ == "__main__":
    # Test BigQuery connection and table creation
    logger.info("Testing BigQuery connection...")

    loader = day03_BigQueryLoader()

    try:
        loader.day03_ensure_dataset_exists()
        loader.day03_ensure_table_exists()

        count = loader.day03_count_leads()
        logger.info(f"Current number of leads in table: {count}")

        logger.info("BigQuery setup complete and working!")

    except Exception as e:
        logger.error(f"BigQuery test failed: {str(e)}")
        logger.info("Make sure your GCP credentials are configured correctly")
