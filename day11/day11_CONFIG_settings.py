"""
Day 11 Configuration Settings
n8n Workflow Automation - Retail Daily Performance Report

This module contains all configuration settings for the Day 11 automated
daily performance reporting system. It fetches data from Day 01 (GA4 + Google Ads)
and sends formatted reports via Slack.

Author: Gleyson - Retail Marketing Automation Specialist
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

# ============================================================================
# DAY 11 SPECIFIC CONFIGURATION
# ============================================================================

# Slack Configuration
DAY11_SLACK_WEBHOOK_URL = os.getenv("DAY11_SLACK_WEBHOOK_URL", "")
DAY11_SLACK_CHANNEL = os.getenv("DAY11_SLACK_CHANNEL", "#marketing-reports")

# Email Configuration (alternative to Slack)
DAY11_EMAIL_ENABLED = os.getenv("DAY11_EMAIL_ENABLED", "false").lower() == "true"
DAY11_EMAIL_TO = os.getenv("DAY11_EMAIL_TO", "").split(",")
DAY11_EMAIL_FROM = os.getenv("DAY11_EMAIL_FROM", "reports@example.com")
DAY11_SMTP_HOST = os.getenv("DAY11_SMTP_HOST", "smtp.gmail.com")
DAY11_SMTP_PORT = int(os.getenv("DAY11_SMTP_PORT", "587"))
DAY11_SMTP_USER = os.getenv("DAY11_SMTP_USER", "")
DAY11_SMTP_PASSWORD = os.getenv("DAY11_SMTP_PASSWORD", "")

# Scheduling Configuration
DAY11_SCHEDULE_CRON = os.getenv("DAY11_SCHEDULE_CRON", "0 8 * * *")  # 8am UTC daily
DAY11_TIMEZONE = os.getenv("DAY11_TIMEZONE", "UTC")
DAY11_RUN_ON_WEEKENDS = os.getenv("DAY11_RUN_ON_WEEKENDS", "false").lower() == "true"

# Report Configuration
DAY11_REPORT_DAYS_BACK = int(os.getenv("DAY11_REPORT_DAYS_BACK", "7"))  # Last 7 days
DAY11_COMPARISON_PERIOD = os.getenv("DAY11_COMPARISON_PERIOD", "previous_week")  # vs previous week
DAY11_INCLUDE_CHARTS = os.getenv("DAY11_INCLUDE_CHARTS", "false").lower() == "true"

# Data Source Configuration (from Day 01)
DAY11_USE_BIGQUERY = os.getenv("DAY11_USE_BIGQUERY", "true").lower() == "true"
DAY11_USE_LOCAL_CSV = os.getenv("DAY11_USE_LOCAL_CSV", "true").lower() == "true"  # Fallback to CSV

# BigQuery Settings
DAY11_GCP_PROJECT_ID = os.getenv("DAY01_GCP_PROJECT_ID", "")  # Reuse from Day 01
DAY11_BQ_DATASET = os.getenv("DAY01_BQ_DATASET", "marketing_data")
DAY11_BQ_GA4_TABLE = "ga4_sessions"
DAY11_BQ_ADS_TABLE = "google_ads_campaigns"

# Local Data Paths (fallback)
DAY11_DATA_DIR = Path(__file__).parent / "data"
DAY11_DAY01_DATA_DIR = Path(__file__).parent.parent / "day01" / "data" / "processed"
DAY11_LOG_DIR = Path(__file__).parent / "logs"

# Error Handling
DAY11_RETRY_ATTEMPTS = int(os.getenv("DAY11_RETRY_ATTEMPTS", "3"))
DAY11_RETRY_DELAY_SECONDS = int(os.getenv("DAY11_RETRY_DELAY_SECONDS", "10"))
DAY11_ENABLE_ERROR_NOTIFICATIONS = os.getenv("DAY11_ENABLE_ERROR_NOTIFICATIONS", "true").lower() == "true"

# Logging Configuration
DAY11_LOG_LEVEL = os.getenv("DAY11_LOG_LEVEL", "INFO")
DAY11_LOG_FILE = DAY11_LOG_DIR / "day11_orchestration.log"

# Testing/Debug Mode
DAY11_DRY_RUN = os.getenv("DAY11_DRY_RUN", "false").lower() == "true"
DAY11_TEST_MODE = os.getenv("DAY11_TEST_MODE", "false").lower() == "true"

# ============================================================================
# VALIDATION
# ============================================================================

def day11_validate_config():
    """Validate that required configuration is present."""
    errors = []

    if not DAY11_SLACK_WEBHOOK_URL and not DAY11_EMAIL_ENABLED:
        errors.append("Either DAY11_SLACK_WEBHOOK_URL or DAY11_EMAIL_ENABLED must be configured")

    if DAY11_EMAIL_ENABLED:
        if not DAY11_EMAIL_TO:
            errors.append("DAY11_EMAIL_TO must be set when email is enabled")
        if not DAY11_SMTP_USER or not DAY11_SMTP_PASSWORD:
            errors.append("SMTP credentials must be set when email is enabled")

    if DAY11_USE_BIGQUERY and not DAY11_GCP_PROJECT_ID:
        errors.append("DAY11_GCP_PROJECT_ID must be set when using BigQuery")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return True

# ============================================================================
# CONSTANTS
# ============================================================================

# Report thresholds for highlighting
DAY11_THRESHOLD_HIGH_SPEND = 1000.0  # Alert if daily spend > $1000
DAY11_THRESHOLD_LOW_CONVERSIONS = 5  # Alert if conversions < 5
DAY11_THRESHOLD_HIGH_BOUNCE_RATE = 0.60  # Alert if bounce rate > 60%

# Formatting
DAY11_CURRENCY_SYMBOL = "$"
DAY11_DATE_FORMAT = "%Y-%m-%d"
DAY11_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def day11_ensure_directories():
    """Create required directories if they don't exist."""
    DAY11_DATA_DIR.mkdir(exist_ok=True, parents=True)
    DAY11_LOG_DIR.mkdir(exist_ok=True, parents=True)

if __name__ == "__main__":
    # Test configuration
    print("Day 11 Configuration Test")
    print("=" * 50)
    print(f"Slack Webhook: {'✓ Set' if DAY11_SLACK_WEBHOOK_URL else '✗ Not Set'}")
    print(f"Email Enabled: {DAY11_EMAIL_ENABLED}")
    print(f"Schedule: {DAY11_SCHEDULE_CRON}")
    print(f"Timezone: {DAY11_TIMEZONE}")
    print(f"Report Days: {DAY11_REPORT_DAYS_BACK}")
    print(f"Use BigQuery: {DAY11_USE_BIGQUERY}")
    print(f"Use Local CSV: {DAY11_USE_LOCAL_CSV}")
    print(f"Dry Run Mode: {DAY11_DRY_RUN}")
    print("=" * 50)

    try:
        day11_validate_config()
        print("✓ Configuration is valid!")
    except ValueError as e:
        print(f"✗ Configuration errors:\n{e}")
