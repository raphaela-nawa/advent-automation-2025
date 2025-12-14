#!/usr/bin/env python3
"""
Day 12B - GE Cloud Validation with Persistent Results
This version SAVES results to GE Cloud dashboard (not just local)
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
    DAY12B_LOG_FORMAT,
    DAY12B_CHECKPOINT_NAME
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

# Set GE Cloud environment variables (required by GE Cloud API)
os.environ['GX_CLOUD_ORGANIZATION_ID'] = DAY12B_GE_CLOUD_ORG_ID
os.environ['GX_CLOUD_ACCESS_TOKEN'] = DAY12B_GE_CLOUD_ACCESS_TOKEN


def day12b_run_cloud_persistent_validation():
    """
    Run GE Cloud validation WITH persistent results visible in dashboard
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - GE CLOUD VALIDATION (Persistent to Dashboard)")
    logger.info("=" * 80)

    try:
        # Step 1: Connect to GE Cloud
        logger.info("\n📡 Connecting to GE Cloud...")
        context = gx.get_context(mode="cloud")
        logger.info("✅ Connected to GE Cloud successfully!")

        # Step 2: Get or create datasource using the uploaded datasets
        logger.info("\n📊 Setting up datasource...")

        # List existing datasources (returns list of datasource names as strings)
        datasource_names = context.data_sources.all()
        logger.info(f"Found {len(datasource_names)} datasource(s) in GE Cloud:")
        for ds_name in datasource_names:
            logger.info(f"   - {ds_name}")

        # Use the first available datasource (your uploaded datasets)
        if len(datasource_names) == 0:
            logger.error("❌ No datasources found in GE Cloud!")
            logger.error("Please upload your datasets via the GE Cloud UI first")
            return 2

        datasource_name = datasource_names[0]
        datasource = context.data_sources.get(datasource_name)
        logger.info(f"✅ Using datasource: {datasource_name}")

        # Step 3: Get data asset
        logger.info(f"\n📁 Getting data assets from datasource...")
        asset_names = list(datasource.assets.keys()) if hasattr(datasource, 'assets') and isinstance(datasource.assets, dict) else []

        if len(asset_names) == 0:
            logger.error("❌ No assets found in datasource!")
            logger.error("Try using context.data_sources.pandas_default instead")
            # Fallback to pandas_default
            logger.info("🔄 Falling back to pandas_default datasource...")
            data_asset_name = "security_events_csv"
        else:
            logger.info(f"Found {len(asset_names)} asset(s):")
            for asset_name in asset_names:
                logger.info(f"   - {asset_name}")
            data_asset_name = asset_names[0]

        logger.info(f"✅ Using asset: {data_asset_name}")

        # Step 4: Get the data asset object
        data_asset = datasource.get_asset(data_asset_name)

        # Step 5: Create a batch request
        logger.info(f"\n📦 Creating batch from asset...")
        batch_request = data_asset.build_batch_request()

        # Step 5: Create expectation suite (will be saved to Cloud)
        logger.info(f"\n📋 Creating expectation suite: {DAY12B_EXPECTATION_SUITE_NAME}")

        # Check if suite already exists
        try:
            suite = context.get_expectation_suite(DAY12B_EXPECTATION_SUITE_NAME)
            logger.info(f"⚠️  Suite '{DAY12B_EXPECTATION_SUITE_NAME}' already exists, updating...")
        except:
            suite = gx.ExpectationSuite(name=DAY12B_EXPECTATION_SUITE_NAME)
            logger.info(f"✅ Created new suite: {DAY12B_EXPECTATION_SUITE_NAME}")

        # Clear existing expectations (fresh start)
        suite.expectations = []

        # Step 6: Add cybersecurity-specific expectations
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

        # 2. Event ID completeness (critical field)
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column="event_id",
                mostly=0.98,
                meta={"description": "Event IDs critical for tracking - max 2% missing", "severity": "critical"}
            )
        )
        logger.info("   ✓ Event ID completeness expectation")

        # 3. Timestamp completeness (mandatory)
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column="timestamp",
                mostly=1.0,
                meta={"description": "Timestamps mandatory for security logs", "severity": "critical"}
            )
        )
        logger.info("   ✓ Timestamp completeness expectation")

        # 4. Severity must be in valid set
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="severity",
                value_set=DAY12B_VALID_SEVERITIES,
                mostly=1.0,
                meta={"description": "Severity must be: critical, high, medium, low, or info", "severity": "warning"}
            )
        )
        logger.info("   ✓ Severity validation expectation")

        # 5. Action taken must be valid
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="action_taken",
                value_set=DAY12B_VALID_ACTIONS,
                mostly=1.0,
                meta={"description": "Action must be: allowed, blocked, quarantined, alerted, or logged"}
            )
        )
        logger.info("   ✓ Action validation expectation")

        # 6. Status must be valid (allow some nulls)
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="status",
                value_set=DAY12B_VALID_STATUSES,
                mostly=0.98,
                meta={"description": "Status must be: open, investigating, resolved, or false_positive"}
            )
        )
        logger.info("   ✓ Status validation expectation")

        # 7. Risk score range (0-100)
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(
                column="risk_score",
                min_value=0,
                max_value=100,
                mostly=1.0,
                meta={"description": "Risk scores must be 0-100", "severity": "warning"}
            )
        )
        logger.info("   ✓ Risk score range expectation")

        # 8. Username anonymization (PII detection - GDPR/HIPAA compliance)
        suite.add_expectation(
            gxe.ExpectColumnValuesToMatchRegex(
                column="username",
                regex="^user_\\d+$",
                mostly=0.95,
                meta={
                    "description": "Usernames should be anonymized (user_XXXX), not email addresses",
                    "severity": "critical",
                    "compliance": "GDPR, HIPAA"
                }
            )
        )
        logger.info("   ✓ Username anonymization expectation (PII detection)")

        logger.info(f"\n✅ Added {len(suite.expectations)} expectations to suite")

        # Step 7: SAVE the suite to GE Cloud (THIS IS KEY!)
        logger.info(f"\n💾 Saving expectation suite to GE Cloud...")
        context.add_or_update_expectation_suite(expectation_suite=suite)
        logger.info(f"✅ Suite saved to GE Cloud - now visible in dashboard!")

        # Step 8: Create a Validation Definition (links suite to data asset)
        logger.info(f"\n🔗 Creating Validation Definition...")
        validation_definition_name = f"{DAY12B_EXPECTATION_SUITE_NAME}_validation"

        try:
            validation_definition = context.validation_definitions.add(
                name=validation_definition_name,
                data=batch_request,
                suite=suite
            )
            logger.info(f"✅ Created Validation Definition: {validation_definition_name}")
        except Exception as e:
            logger.warning(f"⚠️  Validation Definition may already exist: {e}")
            # Get existing validation definition
            validation_definition = context.validation_definitions.get(validation_definition_name)
            logger.info(f"✅ Using existing Validation Definition: {validation_definition_name}")

        # Step 9: Create Checkpoint (THIS makes results visible in dashboard)
        logger.info(f"\n📍 Creating Checkpoint...")

        try:
            checkpoint = context.checkpoints.add(
                name=DAY12B_CHECKPOINT_NAME,
                validation_definitions=[validation_definition]
            )
            logger.info(f"✅ Created Checkpoint: {DAY12B_CHECKPOINT_NAME}")
        except Exception as e:
            logger.warning(f"⚠️  Checkpoint may already exist: {e}")
            checkpoint = context.checkpoints.get(DAY12B_CHECKPOINT_NAME)
            logger.info(f"✅ Using existing Checkpoint: {DAY12B_CHECKPOINT_NAME}")

        # Step 10: RUN the checkpoint (this persists to Cloud!)
        logger.info("\n🔍 Running checkpoint validation...")
        logger.info("This will be visible in GE Cloud dashboard!")

        checkpoint_result = checkpoint.run()

        # Step 11: Parse results
        success = checkpoint_result.success

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Overall Success: {'✅ PASS' if success else '❌ FAIL'}")

        # Get detailed statistics from validation results
        validation_results = checkpoint_result.run_results
        for result_id, result in validation_results.items():
            stats = result.get('validation_result', {}).get('statistics', {})
            logger.info(f"Total Expectations: {stats.get('evaluated_expectations', 0)}")
            logger.info(f"Passed: {stats.get('successful_expectations', 0)} ✓")
            logger.info(f"Failed: {stats.get('unsuccessful_expectations', 0)} ✗")
            logger.info(f"Success Rate: {stats.get('success_percent', 0):.2f}%")

        logger.info("=" * 80)

        # Show failed expectations
        if not success:
            logger.info("\n⚠️  FAILED EXPECTATIONS:")
            for result_id, result in validation_results.items():
                validation_result = result.get('validation_result', {})
                for exp_result in validation_result.get('results', []):
                    if not exp_result.get('success', True):
                        exp_config = exp_result.get('expectation_config', {})
                        exp_type = exp_config.get('type', 'unknown')
                        column = exp_config.get('kwargs', {}).get('column', 'N/A')
                        logger.info(f"   ✗ {exp_type} ({column})")

        # Step 12: Save results locally as well
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = DAY12B_LOGS_DIR / f"validation_results_checkpoint_{timestamp}.json"

        results_dict = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "checkpoint_name": DAY12B_CHECKPOINT_NAME,
            "expectation_suite": DAY12B_EXPECTATION_SUITE_NAME,
            "cloud_persisted": True,
            "validation_results": str(checkpoint_result)
        }

        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)

        logger.info(f"\n📄 Results saved to: {results_file}")
        logger.info(f"🌐 View in GE Cloud at: https://app.greatexpectations.io")
        logger.info(f"   → Navigate to 'Validations' or 'Data Docs' to see results!")

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION COMPLETE - RESULTS NOW IN CLOUD DASHBOARD")
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
    exit_code = day12b_run_cloud_persistent_validation()
    sys.exit(exit_code)
