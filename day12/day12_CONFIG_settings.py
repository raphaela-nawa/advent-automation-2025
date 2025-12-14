#!/usr/bin/env python3
"""
Day 12 - Configuration Settings for Great Expectations Data Quality Framework
Security-focused data validation configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DAY 12 CONFIGURATION - GREAT EXPECTATIONS DATA QUALITY
# ============================================================================

# Project paths
DAY12_PROJECT_ROOT = Path(__file__).parent
DAY12_DATA_DIR = DAY12_PROJECT_ROOT / "data"
DAY12_GE_DIR = DAY12_PROJECT_ROOT / "great_expectations"
DAY12_LOGS_DIR = DAY12_PROJECT_ROOT / "logs"

# Data source paths
DAY12_SECURITY_EVENTS_PATH = DAY12_DATA_DIR / "day12_security_events.csv"
DAY12_COMPLIANCE_AUDIT_PATH = DAY12_DATA_DIR / "day12_compliance_audit.csv"

# Great Expectations configuration
DAY12_GE_PROJECT_NAME = "day12_security_data_quality"
DAY12_GE_DATASOURCE_NAME = "day12_security_logs_datasource"
DAY12_GE_EXPECTATION_SUITE_NAME = "day12_security_validation_suite"
DAY12_GE_CHECKPOINT_NAME = "day12_security_checkpoint"

# Data quality thresholds (cybersecurity-specific)
DAY12_THRESHOLD_NULL_EVENT_IDS = 0.02  # Max 2% null event IDs acceptable
DAY12_THRESHOLD_FUTURE_TIMESTAMPS = 0.01  # Max 1% future timestamps
DAY12_THRESHOLD_PII_LEAKAGE = 0.01  # Max 1% PII in username fields
DAY12_THRESHOLD_MISSING_CRITICAL_FIELDS = 0.05  # Max 5% missing critical fields
DAY12_THRESHOLD_SEVERITY_RISK_CORRELATION = 0.95  # 95% must correlate correctly

# Severity to risk score mapping (for validation)
DAY12_SEVERITY_RISK_MAPPING = {
    'critical': (90, 100),
    'high': (70, 89),
    'medium': (40, 69),
    'low': (10, 39),
    'info': (0, 9)
}

# Required fields for security logs (completeness check)
DAY12_REQUIRED_SECURITY_FIELDS = [
    'event_id',
    'timestamp',
    'event_type',
    'severity',
    'source_system',
    'action_taken',
    'username',
    'source_ip',
    'risk_score',
    'status'
]

# Valid values for categorical fields
DAY12_VALID_SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']
DAY12_VALID_ACTIONS = ['allowed', 'blocked', 'quarantined', 'alerted', 'logged']
DAY12_VALID_STATUSES = ['open', 'investigating', 'resolved', 'false_positive']

# Compliance tags
DAY12_VALID_COMPLIANCE_TAGS = ['HIPAA', 'PCI-DSS', 'SOX', 'GDPR', None]

# Timestamp validation
DAY12_MIN_TIMESTAMP = "2024-01-01T00:00:00"  # Events shouldn't be older than this
DAY12_MAX_FUTURE_HOURS = 1  # Max 1 hour in future (for clock skew tolerance)

# PII detection patterns (regex for username validation)
DAY12_PII_EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Risk score bounds
DAY12_MIN_RISK_SCORE = 0
DAY12_MAX_RISK_SCORE = 100

# Failure actions (what to do when expectations fail)
DAY12_FAILURE_ACTIONS = {
    'critical_failure': {
        'action': 'block_pipeline',
        'notify': True,
        'log_level': 'ERROR',
        'description': 'Stop processing and alert security team'
    },
    'warning': {
        'action': 'continue_with_warning',
        'notify': True,
        'log_level': 'WARNING',
        'description': 'Log issue but continue processing'
    },
    'info': {
        'action': 'log_only',
        'notify': False,
        'log_level': 'INFO',
        'description': 'Record for audit purposes only'
    }
}

# Expectation to failure action mapping
DAY12_EXPECTATION_FAILURE_MAPPING = {
    'expect_column_values_to_not_be_null': 'critical_failure',  # Missing critical fields
    'expect_column_values_to_match_regex': 'critical_failure',  # PII leakage
    'expect_column_values_to_be_between': 'warning',  # Risk score bounds
    'expect_column_values_to_be_in_set': 'warning',  # Invalid categorical values
    'expect_table_row_count_to_be_between': 'info',  # Row count monitoring
}

# Validation results storage
DAY12_VALIDATION_RESULTS_DIR = DAY12_LOGS_DIR / "validation_results"
DAY12_VALIDATION_RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Notification settings (environment variables)
DAY12_NOTIFY_ON_FAILURE = os.getenv('DAY12_NOTIFY_ON_FAILURE', 'true').lower() == 'true'
DAY12_SLACK_WEBHOOK_URL = os.getenv('DAY12_SLACK_WEBHOOK_URL', None)
DAY12_ALERT_EMAIL = os.getenv('DAY12_ALERT_EMAIL', None)

# Logging configuration
DAY12_LOG_FILE = DAY12_LOGS_DIR / "day12_validation.log"
DAY12_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DAY12_LOG_LEVEL = os.getenv('DAY12_LOG_LEVEL', 'INFO')

# Great Expectations Data Docs configuration
DAY12_DATA_DOCS_SITE_NAME = "day12_local_site"
DAY12_BUILD_DATA_DOCS = True

# Integration settings (for use in other projects)
DAY12_CHECKPOINT_RUN_NAME_PREFIX = "day12_validation_run"
DAY12_VALIDATION_OPERATOR_NAME = "day12_action_list_operator"

# Performance settings
DAY12_SAMPLE_SIZE = None  # None = validate all rows, or set to int for sampling
DAY12_ENABLE_PROFILING = True  # Generate data profiling reports

# Environment-specific overrides
DAY12_ENVIRONMENT = os.getenv('DAY12_ENVIRONMENT', 'development')

if DAY12_ENVIRONMENT == 'production':
    # Stricter thresholds in production
    DAY12_THRESHOLD_NULL_EVENT_IDS = 0.001
    DAY12_THRESHOLD_PII_LEAKAGE = 0.0001
    DAY12_THRESHOLD_FUTURE_TIMESTAMPS = 0.001

# Display configuration summary
def day12_print_config_summary():
    """Print configuration summary for verification"""
    print("=" * 80)
    print("DAY 12 - GREAT EXPECTATIONS CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"Environment: {DAY12_ENVIRONMENT}")
    print(f"Project Root: {DAY12_PROJECT_ROOT}")
    print(f"Data Directory: {DAY12_DATA_DIR}")
    print(f"GE Directory: {DAY12_GE_DIR}")
    print(f"Expectation Suite: {DAY12_GE_EXPECTATION_SUITE_NAME}")
    print(f"Checkpoint: {DAY12_GE_CHECKPOINT_NAME}")
    print(f"\nData Quality Thresholds:")
    print(f"  - Null Event IDs: {DAY12_THRESHOLD_NULL_EVENT_IDS * 100}%")
    print(f"  - PII Leakage: {DAY12_THRESHOLD_PII_LEAKAGE * 100}%")
    print(f"  - Future Timestamps: {DAY12_THRESHOLD_FUTURE_TIMESTAMPS * 100}%")
    print(f"\nNotifications:")
    print(f"  - Notify on Failure: {DAY12_NOTIFY_ON_FAILURE}")
    print(f"  - Slack Webhook: {'Configured' if DAY12_SLACK_WEBHOOK_URL else 'Not configured'}")
    print("=" * 80)


if __name__ == "__main__":
    day12_print_config_summary()
