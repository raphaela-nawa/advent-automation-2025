"""
Day 03 - GDPR Lead Ingestion Configuration
All constants are day-scoped to prevent conflicts with other projects.
"""

import os
from dotenv import load_dotenv

# Load environment variables from root config/.env
load_dotenv(dotenv_path="../config/.env")

# BigQuery Configuration
DAY03_GCP_PROJECT_ID = os.getenv("DAY03_GCP_PROJECT_ID", "advent2025-day03")
DAY03_BQ_DATASET = os.getenv("DAY03_BQ_DATASET", "gdpr_leads_dataset")
DAY03_BQ_TABLE = os.getenv("DAY03_BQ_TABLE", "gdpr_leads")
DAY03_BQ_LOCATION = os.getenv("DAY03_BQ_LOCATION", "US")

# GDPR Configuration
DAY03_GDPR_RETENTION_DAYS = int(os.getenv("DAY03_GDPR_RETENTION_DAYS", "30"))
DAY03_WEBHOOK_PORT = int(os.getenv("DAY03_WEBHOOK_PORT", "5000"))
DAY03_WEBHOOK_HOST = os.getenv("DAY03_WEBHOOK_HOST", "0.0.0.0")

# Required fields for GDPR validation
DAY03_REQUIRED_FIELDS = [
    "name",
    "email",
    "consent_given",
    "consent_purpose",
    "timestamp"
]

# Valid consent purposes
DAY03_VALID_CONSENT_PURPOSES = [
    "marketing_communications",
    "product_updates",
    "newsletter",
    "customer_service",
    "research_surveys"
]

# BigQuery Schema
DAY03_BQ_SCHEMA = [
    {"name": "lead_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "email", "type": "STRING", "mode": "REQUIRED"},
    {"name": "consent_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "consent_purpose", "type": "STRING", "mode": "REQUIRED"},
    {"name": "ip_address", "type": "STRING", "mode": "NULLABLE"},
    {"name": "data_retention_date", "type": "DATE", "mode": "REQUIRED"},
    {"name": "consent_given", "type": "BOOLEAN", "mode": "REQUIRED"},
    {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"}
]
