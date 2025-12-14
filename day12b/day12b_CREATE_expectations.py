#!/usr/bin/env python3
"""
Day 12B - Create Great Expectations Cloud Expectation Suite
Defines cybersecurity-specific data quality expectations using native GE expectations
"""

import great_expectations as gx
from great_expectations.core import ExpectationSuite
import logging

from day12b_SETUP_cloud import day12b_get_cloud_context
from day12b_CONFIG_ge_cloud import (
    DAY12B_EXPECTATION_SUITE_NAME,
    DAY12B_DATASOURCE_NAME,
    DAY12B_DATA_ASSET_NAME,
    DAY12B_VALID_SEVERITIES,
    DAY12B_VALID_ACTIONS,
    DAY12B_VALID_STATUSES,
    DAY12B_LOG_FILE,
    DAY12B_LOG_FORMAT
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=DAY12B_LOG_FORMAT,
    handlers=[
        logging.FileHandler(DAY12B_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def day12b_create_expectation_suite(context):
    """
    Create expectation suite with cybersecurity-specific validations
    Uses native GE expectations (not custom)
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - CREATING EXPECTATION SUITE")
    logger.info("=" * 80)

    try:
        # Create new expectation suite
        logger.info(f"Creating expectation suite: {DAY12B_EXPECTATION_SUITE_NAME}")

        suite = context.add_expectation_suite(
            expectation_suite_name=DAY12B_EXPECTATION_SUITE_NAME
        )

        logger.info("✅ Expectation suite created")
        logger.info("\n📋 Adding expectations...")

        # Get data asset for validation
        datasource = context.get_datasource(DAY12B_DATASOURCE_NAME)
        data_asset = datasource.get_asset(DAY12B_DATA_ASSET_NAME)
        batch_request = data_asset.build_batch_request()

        # Get validator
        validator = context.get_validator(
            batch_request=batch_request,
            expectation_suite_name=DAY12B_EXPECTATION_SUITE_NAME
        )

        # =====================================================================
        # EXPECTATION 1: Table-level validations
        # =====================================================================
        logger.info("\n1️⃣ Adding table-level expectations...")

        # Row count should be reasonable
        validator.expect_table_row_count_to_be_between(
            min_value=100,
            max_value=1000000,
            meta={
                "description": "Security logs should have reasonable number of events"
            }
        )
        logger.info("   ✓ expect_table_row_count_to_be_between")

        # Table should have expected columns
        validator.expect_table_columns_to_match_set(
            column_set=[
                'event_id', 'timestamp', 'event_type', 'severity',
                'source_system', 'action_taken', 'username', 'source_ip',
                'destination_ip', 'risk_score', 'status', 'details'
            ],
            exact_match=False,  # Allow extra columns
            meta={
                "description": "Security events must have all required fields"
            }
        )
        logger.info("   ✓ expect_table_columns_to_match_set")

        # =====================================================================
        # EXPECTATION 2: Null value checks (completeness)
        # =====================================================================
        logger.info("\n2️⃣ Adding completeness expectations...")

        # Event ID should be mostly non-null (allow 2% missing)
        validator.expect_column_values_to_not_be_null(
            column="event_id",
            mostly=0.98,  # At least 98% non-null
            meta={
                "description": "Event IDs critical for tracking - max 2% missing allowed",
                "severity": "critical"
            }
        )
        logger.info("   ✓ expect_column_values_to_not_be_null (event_id)")

        # Timestamp should always exist
        validator.expect_column_values_to_not_be_null(
            column="timestamp",
            mostly=1.0,  # 100% non-null
            meta={
                "description": "Timestamps mandatory for security logs",
                "severity": "critical"
            }
        )
        logger.info("   ✓ expect_column_values_to_not_be_null (timestamp)")

        # =====================================================================
        # EXPECTATION 3: Categorical validations
        # =====================================================================
        logger.info("\n3️⃣ Adding categorical value expectations...")

        # Severity must be in valid set
        validator.expect_column_values_to_be_in_set(
            column="severity",
            value_set=DAY12B_VALID_SEVERITIES,
            mostly=1.0,
            meta={
                "description": "Severity must be: critical, high, medium, low, or info",
                "severity": "warning"
            }
        )
        logger.info("   ✓ expect_column_values_to_be_in_set (severity)")

        # Action taken must be valid
        validator.expect_column_values_to_be_in_set(
            column="action_taken",
            value_set=DAY12B_VALID_ACTIONS,
            mostly=1.0,
            meta={
                "description": "Action must be: allowed, blocked, quarantined, alerted, or logged",
                "severity": "warning"
            }
        )
        logger.info("   ✓ expect_column_values_to_be_in_set (action_taken)")

        # Status must be valid
        validator.expect_column_values_to_be_in_set(
            column="status",
            value_set=DAY12B_VALID_STATUSES,
            mostly=0.98,  # Allow some nulls
            meta={
                "description": "Status must be: open, investigating, resolved, or false_positive",
                "severity": "info"
            }
        )
        logger.info("   ✓ expect_column_values_to_be_in_set (status)")

        # =====================================================================
        # EXPECTATION 4: Range validations
        # =====================================================================
        logger.info("\n4️⃣ Adding range expectations...")

        # Risk score must be 0-100
        validator.expect_column_values_to_be_between(
            column="risk_score",
            min_value=0,
            max_value=100,
            mostly=1.0,
            meta={
                "description": "Risk scores must be 0-100",
                "severity": "warning"
            }
        )
        logger.info("   ✓ expect_column_values_to_be_between (risk_score)")

        # =====================================================================
        # EXPECTATION 5: Pattern validations (PII detection)
        # =====================================================================
        logger.info("\n5️⃣ Adding pattern-based expectations (PII detection)...")

        # Username should NOT contain email addresses (GDPR/HIPAA)
        validator.expect_column_values_to_match_regex(
            column="username",
            regex="^user_\\d+$",  # Should be user_1234 format
            mostly=0.95,  # Allow 5% for synthetic data testing
            meta={
                "description": "Usernames should be anonymized (user_XXXX), not email addresses",
                "severity": "critical",
                "compliance": "GDPR, HIPAA"
            }
        )
        logger.info("   ✓ expect_column_values_to_match_regex (username anonymization)")

        # =====================================================================
        # EXPECTATION 6: Type validations
        # =====================================================================
        logger.info("\n6️⃣ Adding type expectations...")

        # Risk score should be numeric
        validator.expect_column_values_to_be_of_type(
            column="risk_score",
            type_="int64",
            meta={
                "description": "Risk score must be integer type"
            }
        )
        logger.info("   ✓ expect_column_values_to_be_of_type (risk_score)")

        # =====================================================================
        # Save expectation suite
        # =====================================================================
        logger.info("\n💾 Saving expectation suite to GE Cloud...")
        validator.save_expectation_suite(discard_failed_expectations=False)

        logger.info("\n✅ Expectation suite created successfully!")
        logger.info(f"Suite name: {DAY12B_EXPECTATION_SUITE_NAME}")
        logger.info(f"Total expectations: {len(suite.expectations)}")

        return suite

    except Exception as e:
        logger.error(f"❌ Failed to create expectation suite: {e}")
        logger.exception("Full error:")
        return None


def day12b_create_expectations():
    """Main function to create expectations"""
    logger.info("=" * 80)
    logger.info("DAY 12B - CREATING GREAT EXPECTATIONS CLOUD SUITE")
    logger.info("=" * 80)

    # Connect to GE Cloud
    context = day12b_get_cloud_context()
    if not context:
        logger.error("❌ Could not connect to GE Cloud")
        return None

    # Create expectation suite
    suite = day12b_create_expectation_suite(context)

    if suite:
        logger.info("\n" + "=" * 80)
        logger.info("EXPECTATIONS CREATED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info("Next steps:")
        logger.info("1. View expectations at: https://app.greatexpectations.io")
        logger.info("2. Run validation: python3 day12b_RUN_validation_cloud.py")
        logger.info("=" * 80)
        return suite
    else:
        logger.error("❌ Failed to create expectations")
        return None


if __name__ == "__main__":
    suite = day12b_create_expectations()
