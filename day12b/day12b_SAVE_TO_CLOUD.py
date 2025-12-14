#!/usr/bin/env python3
"""
Day 12B - Save Validation Results to GE Cloud Dashboard
Uses pandas_default + saves Expectation Suite and Validation Results to Cloud
"""

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd
import logging
from datetime import datetime
import json
import os

from day12b_CONFIG_ge_cloud import (
    DAY12B_GE_CLOUD_ORG_ID,
    DAY12B_GE_CLOUD_ACCESS_TOKEN,
    DAY12B_SECURITY_EVENTS_PATH,
    DAY12B_EXPECTATION_SUITE_NAME,
    DAY12B_VALID_SEVERITIES,
    DAY12B_VALID_ACTIONS,
    DAY12B_VALID_STATUSES,
    DAY12B_LOGS_DIR,
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

# Set GE Cloud environment variables
os.environ['GX_CLOUD_ORGANIZATION_ID'] = DAY12B_GE_CLOUD_ORG_ID
os.environ['GX_CLOUD_ACCESS_TOKEN'] = DAY12B_GE_CLOUD_ACCESS_TOKEN


def day12b_save_to_cloud():
    """
    Run validation and SAVE results to GE Cloud for dashboard visibility
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - GE CLOUD VALIDATION WITH DASHBOARD PERSISTENCE")
    logger.info("=" * 80)

    try:
        # Step 1: Connect to GE Cloud
        logger.info("\n📡 Connecting to GE Cloud...")
        context = gx.get_context(mode="cloud")
        logger.info("✅ Connected to GE Cloud successfully!")

        # Step 2: Load data using pandas_default (we know this works)
        logger.info(f"\n📊 Loading security events data...")
        batch = context.data_sources.pandas_default.read_csv(
            str(DAY12B_SECURITY_EVENTS_PATH)
        )
        logger.info(f"✅ Loaded data from {DAY12B_SECURITY_EVENTS_PATH.name}")

        # Step 3: Create expectation suite
        logger.info(f"\n📋 Creating expectation suite: {DAY12B_EXPECTATION_SUITE_NAME}")
        suite = gx.ExpectationSuite(name=DAY12B_EXPECTATION_SUITE_NAME)

        # Step 4: Add cybersecurity-specific expectations
        logger.info("\n📝 Adding cybersecurity-specific expectations...")

        # 1. Row count
        suite.add_expectation(
            gxe.ExpectTableRowCountToBeBetween(
                min_value=100,
                max_value=1000000,
                meta={"description": "Security logs should have reasonable event count"}
            )
        )
        logger.info("   ✓ Table row count expectation")

        # 2. Event ID completeness
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column="event_id",
                mostly=0.98,
                meta={"description": "Event IDs critical for tracking", "severity": "critical"}
            )
        )
        logger.info("   ✓ Event ID completeness expectation")

        # 3. Timestamp completeness
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column="timestamp",
                mostly=1.0,
                meta={"description": "Timestamps mandatory", "severity": "critical"}
            )
        )
        logger.info("   ✓ Timestamp completeness expectation")

        # 4. Severity validation
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="severity",
                value_set=DAY12B_VALID_SEVERITIES,
                mostly=1.0,
                meta={"description": "Severity must be valid", "severity": "warning"}
            )
        )
        logger.info("   ✓ Severity validation expectation")

        # 5. Action validation
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="action_taken",
                value_set=DAY12B_VALID_ACTIONS,
                mostly=1.0,
                meta={"description": "Action must be valid"}
            )
        )
        logger.info("   ✓ Action validation expectation")

        # 6. Status validation
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="status",
                value_set=DAY12B_VALID_STATUSES,
                mostly=0.98,
                meta={"description": "Status must be valid"}
            )
        )
        logger.info("   ✓ Status validation expectation")

        # 7. Risk score range
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(
                column="risk_score",
                min_value=0,
                max_value=100,
                mostly=1.0,
                meta={"description": "Risk scores 0-100", "severity": "warning"}
            )
        )
        logger.info("   ✓ Risk score range expectation")

        # 8. Username PII detection
        suite.add_expectation(
            gxe.ExpectColumnValuesToMatchRegex(
                column="username",
                regex="^user_\\d+$",
                mostly=0.95,
                meta={
                    "description": "Usernames anonymized (PII detection)",
                    "severity": "critical",
                    "compliance": "GDPR, HIPAA"
                }
            )
        )
        logger.info("   ✓ Username PII detection expectation")

        logger.info(f"\n✅ Added {len(suite.expectations)} expectations to suite")

        # Step 5: SAVE the suite to GE Cloud (KEY STEP!)
        logger.info(f"\n💾 Saving Expectation Suite to GE Cloud...")
        try:
            context.suites.add(suite)
            logger.info(f"✅ Suite saved to GE Cloud!")
        except Exception as e:
            # Suite might already exist, update it
            logger.warning(f"⚠️  Suite may already exist, updating: {e}")
            context.suites.update(suite)
            logger.info(f"✅ Suite updated in GE Cloud!")

        # Step 6: Run validation
        logger.info("\n🔍 Running validation...")
        results = batch.validate(suite)

        # Step 7: Parse results
        success = results.success
        statistics = results.statistics

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Overall Success: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"Total Expectations: {statistics.get('evaluated_expectations', 0)}")
        logger.info(f"Passed: {statistics.get('successful_expectations', 0)} ✓")
        logger.info(f"Failed: {statistics.get('unsuccessful_expectations', 0)} ✗")
        logger.info(f"Success Rate: {statistics.get('success_percent', 0):.2f}%")
        logger.info("=" * 80)

        # Show failed expectations
        if not success:
            logger.info("\n⚠️  FAILED EXPECTATIONS:")
            for result in results.results:
                if not result.success:
                    exp_config = result.expectation_config
                    exp_type = exp_config.type if hasattr(exp_config, 'type') else str(type(exp_config).__name__)
                    column = exp_config.kwargs.get('column', 'N/A') if hasattr(exp_config, 'kwargs') else 'N/A'
                    logger.info(f"   ✗ {exp_type} ({column})")

        # Step 8: SAVE validation results to Cloud (THIS makes it appear in dashboard!)
        logger.info(f"\n💾 Saving Validation Results to GE Cloud...")
        try:
            # The batch.validate() should already persist to Cloud if suite is saved
            # But let's explicitly save the validation results
            context.validations.save(results)
            logger.info(f"✅ Validation results saved to GE Cloud!")
        except Exception as e:
            logger.warning(f"⚠️  Could not save validation results: {e}")
            logger.info("Results may still be visible in Cloud from batch.validate()")

        # Step 9: Save results locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = DAY12B_LOGS_DIR / f"validation_cloud_saved_{timestamp}.json"

        results_dict = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "evaluated_expectations": statistics.get('evaluated_expectations', 0),
                "successful_expectations": statistics.get('successful_expectations', 0),
                "unsuccessful_expectations": statistics.get('unsuccessful_expectations', 0),
                "success_percent": statistics.get('success_percent', 0)
            },
            "expectation_suite": DAY12B_EXPECTATION_SUITE_NAME,
            "saved_to_cloud": True
        }

        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)

        logger.info(f"\n📄 Results saved locally to: {results_file}")
        logger.info(f"🌐 View in GE Cloud at: https://app.greatexpectations.io")
        logger.info(f"\nIn GE Cloud dashboard, navigate to:")
        logger.info(f"  1. 'Expectation Suites' → See '{DAY12B_EXPECTATION_SUITE_NAME}'")
        logger.info(f"  2. 'Validations' or 'Data Docs' → See validation results")

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION COMPLETE - CHECK GE CLOUD DASHBOARD")
        logger.info("=" * 80)
        logger.info(f"Status: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"Exit Code: {0 if success else 1}")
        logger.info("=" * 80)

        return 0 if success else 1

    except Exception as e:
        logger.error(f"\n❌ Validation failed: {e}")
        logger.exception("Full error:")
        return 2


if __name__ == "__main__":
    import sys
    exit_code = day12b_save_to_cloud()
    sys.exit(exit_code)
