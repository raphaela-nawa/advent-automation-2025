#!/usr/bin/env python3
"""
Day 12B - Run Existing GE Cloud Checkpoint
Uses the checkpoints already created in GE Cloud to persist validation results to dashboard
"""

import great_expectations as gx
import os
import logging
from datetime import datetime
import json

from day12b_CONFIG_ge_cloud import (
    DAY12B_GE_CLOUD_ORG_ID,
    DAY12B_GE_CLOUD_ACCESS_TOKEN,
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


def day12b_run_cloud_checkpoint():
    """
    Run existing GE Cloud checkpoints - results WILL appear in dashboard!
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - RUN GE CLOUD CHECKPOINTS")
    logger.info("=" * 80)

    try:
        # Step 1: Connect to GE Cloud
        logger.info("\n📡 Connecting to GE Cloud...")
        context = gx.get_context(mode="cloud")
        logger.info("✅ Connected to GE Cloud successfully!")

        # Step 2: List available checkpoints
        logger.info("\n📋 Listing available checkpoints...")
        checkpoint_names = context.checkpoints.all()
        logger.info(f"Found {len(checkpoint_names)} checkpoint(s):")
        for i, cp_name in enumerate(checkpoint_names, 1):
            # Extract just the name from the complex string
            if 'name=' in str(cp_name):
                clean_name = str(cp_name).split("name='")[1].split("'")[0]
            else:
                clean_name = str(cp_name)
            logger.info(f"  {i}. {clean_name}")

        if len(checkpoint_names) == 0:
            logger.error("❌ No checkpoints found in GE Cloud!")
            logger.error("You need to create a checkpoint first via the UI")
            return 2

        # Step 3: Get the first checkpoint
        checkpoint_name = checkpoint_names[0]
        if 'name=' in str(checkpoint_name):
            clean_checkpoint_name = str(checkpoint_name).split("name='")[1].split("'")[0]
        else:
            clean_checkpoint_name = str(checkpoint_name)

        logger.info(f"\n🎯 Using checkpoint: {clean_checkpoint_name}")

        # Get the checkpoint object
        try:
            # Try to get by the clean name
            checkpoint = context.checkpoints.get(clean_checkpoint_name)
        except:
            # If that fails, use the first element
            checkpoint = checkpoint_name

        # Step 4: Run the checkpoint
        logger.info("\n🔍 Running checkpoint validation...")
        logger.info("This will persist results to GE Cloud dashboard!")

        result = checkpoint.run()

        # Step 5: Parse results
        success = result.success

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Overall Success: {'✅ PASS' if success else '❌ FAIL'}")

        # Get detailed statistics
        if hasattr(result, 'run_results') and result.run_results:
            for run_id, run_result in result.run_results.items():
                if 'validation_result' in run_result:
                    stats = run_result['validation_result'].get('statistics', {})
                    logger.info(f"Total Expectations: {stats.get('evaluated_expectations', 0)}")
                    logger.info(f"Passed: {stats.get('successful_expectations', 0)} ✓")
                    logger.info(f"Failed: {stats.get('unsuccessful_expectations', 0)} ✗")
                    logger.info(f"Success Rate: {stats.get('success_percent', 0):.2f}%")

        logger.info("=" * 80)

        # Step 6: Save results locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = DAY12B_LOGS_DIR / f"checkpoint_run_{timestamp}.json"

        results_dict = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "checkpoint_name": clean_checkpoint_name,
            "persisted_to_cloud": True,
            "run_id": str(result.run_id) if hasattr(result, 'run_id') else None
        }

        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)

        logger.info(f"\n📄 Results saved locally to: {results_file}")
        logger.info(f"🌐 View in GE Cloud at: https://app.greatexpectations.io")
        logger.info(f"\n✅ Validation results are NOW VISIBLE in GE Cloud dashboard!")
        logger.info(f"   Navigate to: Validations → See your checkpoint run")

        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION COMPLETE - CHECK DASHBOARD NOW!")
        logger.info("=" * 80)
        logger.info(f"Status: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"Exit Code: {0 if success else 1}")
        logger.info("=" * 80)

        return 0 if success else 1

    except Exception as e:
        logger.error(f"\n❌ Checkpoint run failed: {e}")
        logger.exception("Full error:")
        return 2


if __name__ == "__main__":
    import sys
    exit_code = day12b_run_cloud_checkpoint()
    sys.exit(exit_code)
