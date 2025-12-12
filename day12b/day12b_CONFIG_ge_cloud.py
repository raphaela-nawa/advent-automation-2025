#!/usr/bin/env python3
"""
Day 12B - Great Expectations Cloud Configuration
Connects to GE Cloud for enterprise data quality validation
Context: Sal (Cybersecurity Analyst) - Production GE Cloud deployment
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

# ============================================================================
# DAY 12B CONFIGURATION - GREAT EXPECTATIONS CLOUD
# ============================================================================

# GE Cloud credentials (from environment)
DAY12B_GE_CLOUD_ORG_ID = os.getenv('DAY12B_GE_CLOUD_ORG_ID')
DAY12B_GE_CLOUD_ACCESS_TOKEN = os.getenv('DAY12B_GE_CLOUD_ACCESS_TOKEN')
DAY12B_GE_CLOUD_BASE_URL = os.getenv('DAY12B_GE_CLOUD_BASE_URL', 'https://app.greatexpectations.io')

# Project paths (reuse Day 12A data)
DAY12B_PROJECT_ROOT = Path(__file__).parent
DAY12B_DATA_DIR = DAY12B_PROJECT_ROOT.parent / "day12" / "data"  # Reuse Day 12A data
DAY12B_LOGS_DIR = DAY12B_PROJECT_ROOT / "logs"

# Data source paths (same synthetic data as Day 12A)
DAY12B_SECURITY_EVENTS_PATH = DAY12B_DATA_DIR / "day12_security_events.csv"
DAY12B_COMPLIANCE_AUDIT_PATH = DAY12B_DATA_DIR / "day12_compliance_audit.csv"

# GE Cloud configuration
DAY12B_DATASOURCE_NAME = "day12b_security_logs_cloud"
DAY12B_DATA_ASSET_NAME = "security_events"
DAY12B_EXPECTATION_SUITE_NAME = "day12b_security_validation_suite"
DAY12B_CHECKPOINT_NAME = "day12b_security_checkpoint"

# Data quality thresholds (same as Day 12A for consistency)
DAY12B_THRESHOLD_NULL_EVENT_IDS = 0.02  # Max 2% null event IDs acceptable
DAY12B_THRESHOLD_FUTURE_TIMESTAMPS = 0.01  # Max 1% future timestamps
DAY12B_THRESHOLD_PII_LEAKAGE = 0.01  # Max 1% PII in username fields

# Severity to risk score mapping (for custom validation)
DAY12B_SEVERITY_RISK_MAPPING = {
    'critical': (90, 100),
    'high': (70, 89),
    'medium': (40, 69),
    'low': (10, 39),
    'info': (0, 9)
}

# Valid values for categorical fields
DAY12B_VALID_SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']
DAY12B_VALID_ACTIONS = ['allowed', 'blocked', 'quarantined', 'alerted', 'logged']
DAY12B_VALID_STATUSES = ['open', 'investigating', 'resolved', 'false_positive']

# Logging configuration
DAY12B_LOG_FILE = DAY12B_LOGS_DIR / "day12b_cloud_validation.log"
DAY12B_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DAY12B_LOG_LEVEL = os.getenv('DAY12B_LOG_LEVEL', 'INFO')

# Notification settings
DAY12B_NOTIFY_ON_FAILURE = os.getenv('DAY12B_NOTIFY_ON_FAILURE', 'true').lower() == 'true'
DAY12B_SLACK_WEBHOOK_URL = os.getenv('DAY12B_SLACK_WEBHOOK_URL', None)

# Create directories
DAY12B_LOGS_DIR.mkdir(exist_ok=True, parents=True)


def day12b_print_config_summary():
    """Print configuration summary for verification"""
    print("=" * 80)
    print("DAY 12B - GREAT EXPECTATIONS CLOUD CONFIGURATION")
    print("=" * 80)
    print(f"GE Cloud Org ID: {DAY12B_GE_CLOUD_ORG_ID[:20]}..." if DAY12B_GE_CLOUD_ORG_ID else "Not configured")
    print(f"GE Cloud URL: {DAY12B_GE_CLOUD_BASE_URL}")
    print(f"Data Source: {DAY12B_SECURITY_EVENTS_PATH}")
    print(f"Datasource Name: {DAY12B_DATASOURCE_NAME}")
    print(f"Expectation Suite: {DAY12B_EXPECTATION_SUITE_NAME}")
    print(f"Checkpoint: {DAY12B_CHECKPOINT_NAME}")
    print(f"Log File: {DAY12B_LOG_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    day12b_print_config_summary()
