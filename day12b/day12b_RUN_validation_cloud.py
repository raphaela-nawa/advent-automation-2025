#!/usr/bin/env python3
"""
Day 12B - Run Validation via Great Expectations Cloud
Executes validation and retrieves results from GE Cloud
"""

import great_expectations as gx
import logging
import json
from datetime import datetime

from day12b_SETUP_cloud import day12b_get_cloud_context
from day12b_CONFIG_ge_cloud import (
    DAY12B_EXPECTATION_SUITE_NAME,
    DAY12B_DATASOURCE_NAME,
    DAY12B_DATA_ASSET_NAME,
    DAY12B_CHECKPOINT_NAME,
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


def day12b_create_checkpoint(context):
    """
    Create or update checkpoint for validation
    """
    logger.info("\n📋 Setting up validation checkpoint...")

    try:
        # Get datasource and data asset
        datasource = context.get_datasource(DAY12B_DATASOURCE_NAME)
        data_asset = datasource.get_asset(DAY12B_DATA_ASSET_NAME)

        # Create batch request
        batch_request = data_asset.build_batch_request()

        # Create or update checkpoint
        checkpoint = context.add_or_update_checkpoint(
            name=DAY12B_CHECKPOINT_NAME,
            validations=[
                {
                    "batch_request": batch_request,
                    "expectation_suite_name": DAY12B_EXPECTATION_SUITE_NAME
                }
            ]
        )

        logger.info(f"✅ Checkpoint created/updated: {DAY12B_CHECKPOINT_NAME}")
        return checkpoint

    except Exception as e:
        logger.error(f"❌ Failed to create checkpoint: {e}")
        logger.exception("Full error:")
        return None


def day12b_run_validation(context):
    """
    Run validation via checkpoint and return results
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - RUNNING CLOUD VALIDATION")
    logger.info("=" * 80)

    try:
        # Create checkpoint
        checkpoint = day12b_create_checkpoint(context)
        if not checkpoint:
            logger.error("❌ Could not create checkpoint")
            return None

        # Run validation
        logger.info(f"\n🔍 Running validation: {DAY12B_CHECKPOINT_NAME}")
        logger.info(f"Expectation Suite: {DAY12B_EXPECTATION_SUITE_NAME}")
        logger.info(f"Data Asset: {DAY12B_DATA_ASSET_NAME}")

        results = checkpoint.run()

        logger.info("✅ Validation completed!")

        # Parse results
        run_results = results.run_results

        # Get validation result
        validation_result = list(run_results.values())[0] if run_results else None

        if not validation_result:
            logger.error("❌ No validation results found")
            return None

        # Extract statistics
        success = validation_result["success"]
        statistics = validation_result.get("statistics", {})

        evaluated_expectations = statistics.get("evaluated_expectations", 0)
        successful_expectations = statistics.get("successful_expectations", 0)
        unsuccessful_expectations = statistics.get("unsuccessful_expectations", 0)
        success_percent = statistics.get("success_percent", 0)

        # Log results
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Overall Success: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"Total Expectations: {evaluated_expectations}")
        logger.info(f"Passed: {successful_expectations} ✓")
        logger.info(f"Failed: {unsuccessful_expectations} ✗")
        logger.info(f"Success Rate: {success_percent:.2f}%")
        logger.info("=" * 80)

        # Show failed expectations
        if unsuccessful_expectations > 0:
            logger.info("\n⚠️  FAILED EXPECTATIONS:")
            validation_result_obj = validation_result.get("results", [])
            for result in validation_result_obj:
                if not result.get("success", True):
                    exp_type = result.get("expectation_config", {}).get("expectation_type", "unknown")
                    column = result.get("expectation_config", {}).get("kwargs", {}).get("column", "N/A")
                    logger.info(f"   ✗ {exp_type} ({column})")

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = DAY12B_LOGS_DIR / f"validation_results_cloud_{timestamp}.json"

        with open(results_file, 'w') as f:
            # Convert to serializable format
            results_dict = {
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "statistics": statistics,
                "expectation_suite": DAY12B_EXPECTATION_SUITE_NAME,
                "checkpoint": DAY12B_CHECKPOINT_NAME
            }
            json.dump(results_dict, f, indent=2)

        logger.info(f"\n📄 Results saved to: {results_file}")
        logger.info(f"🌐 View Data Docs at: https://app.greatexpectations.io")

        return results

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        logger.exception("Full error:")
        return None


def day12b_run_cloud_validation():
    """Main validation function"""
    logger.info("=" * 80)
    logger.info("DAY 12B - GREAT EXPECTATIONS CLOUD VALIDATION")
    logger.info("=" * 80)

    # Connect to GE Cloud
    context = day12b_get_cloud_context()
    if not context:
        logger.error("❌ Could not connect to GE Cloud")
        return None

    # Run validation
    results = day12b_run_validation(context)

    if results:
        success = results.success
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Status: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"Exit Code: {0 if success else 1}")
        logger.info("=" * 80)

        return 0 if success else 1
    else:
        logger.error("❌ Validation failed to run")
        return 2


if __name__ == "__main__":
    import sys
    exit_code = day12b_run_cloud_validation()
    sys.exit(exit_code)
