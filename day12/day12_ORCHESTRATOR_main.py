#!/usr/bin/env python3
"""
Day 12 - Data Quality Orchestrator
Main orchestration script for automated data quality validation
Context: Sal (Cybersecurity Analyst) - Daily security data validation

This script can be scheduled to run daily/hourly for continuous validation
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Import validation components
from day12_VALIDATOR_cybersecurity import day12_validate_security_events
from day12_GENERATE_data_docs import day12_generate_html_report
from day12_CONFIG_settings import (
    DAY12_VALIDATION_RESULTS_DIR,
    DAY12_NOTIFY_ON_FAILURE,
    DAY12_SLACK_WEBHOOK_URL,
    DAY12_LOG_FILE
)

logger = logging.getLogger(__name__)


def day12_send_failure_notification(results: dict):
    """
    Send notification when validation fails
    In production, this would integrate with Slack/Email/PagerDuty
    """
    if not DAY12_NOTIFY_ON_FAILURE:
        return

    failed_expectations = [e for e in results['expectations'] if not e['success']]

    message = f"""
🚨 DATA QUALITY VALIDATION FAILED

Dataset: {results['dataset']}
Time: {results['timestamp']}
Total Rows: {results['total_rows']:,}

SUMMARY:
- Total Expectations: {results['statistics']['total_expectations']}
- Passed: {results['statistics']['passed']} ✓
- Failed: {results['statistics']['failed']} ✗
- Success Rate: {results['statistics']['success_rate']}%

FAILED EXPECTATIONS:
"""

    for exp in failed_expectations[:5]:  # Show first 5 failures
        message += f"\n- {exp['expectation_type']}"
        if 'column' in exp:
            message += f" ({exp['column']})"
        if 'percentage' in exp:
            message += f" - {exp['percentage']}% issues"

    logger.warning(message)

    # In production, send to Slack:
    if DAY12_SLACK_WEBHOOK_URL:
        logger.info(f"Would send alert to Slack: {DAY12_SLACK_WEBHOOK_URL[:50]}...")
        # import requests
        # requests.post(DAY12_SLACK_WEBHOOK_URL, json={"text": message})

    print("\n" + message)


def day12_run_orchestration():
    """
    Main orchestration function
    Returns: exit code (0 = success, 1 = validation failed)
    """
    logger.info("=" * 80)
    logger.info("DAY 12 - DATA QUALITY ORCHESTRATION STARTING")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    exit_code = 0

    try:
        # Step 1: Run validation
        logger.info("\n[STEP 1/3] Running data quality validation...")
        results = day12_validate_security_events()

        # Step 2: Generate HTML report
        logger.info("\n[STEP 2/3] Generating HTML report...")
        results_file = sorted(DAY12_VALIDATION_RESULTS_DIR.glob("validation_*.json"))[-1]
        html_report = day12_generate_html_report(results_file)
        logger.info(f"✅ Report generated: {html_report}")

        # Step 3: Handle validation results
        logger.info("\n[STEP 3/3] Processing results...")

        if results['success']:
            logger.info("✅ All validation checks passed!")
            logger.info("✅ Data quality meets requirements")
            exit_code = 0
        else:
            logger.warning("⚠️  Some validation checks failed")
            logger.warning("❌ Data quality issues detected")

            # Send failure notification
            day12_send_failure_notification(results)

            # Exit with error code (for CI/CD pipelines)
            exit_code = 1

        # Log summary
        logger.info("\n" + "=" * 80)
        logger.info("ORCHESTRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Dataset: {results['dataset']}")
        logger.info(f"Expectations: {results['statistics']['total_expectations']}")
        logger.info(f"Passed: {results['statistics']['passed']}")
        logger.info(f"Failed: {results['statistics']['failed']}")
        logger.info(f"Success Rate: {results['statistics']['success_rate']}%")
        logger.info(f"Status: {'✅ PASS' if results['success'] else '❌ FAIL'}")
        logger.info(f"Exit Code: {exit_code}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Orchestration failed with error: {e}", exc_info=True)
        exit_code = 2  # System error

    return exit_code


if __name__ == "__main__":
    exit_code = day12_run_orchestration()

    logger.info(f"\n🏁 Orchestration complete. Exit code: {exit_code}")
    logger.info(f"📋 Full logs: {DAY12_LOG_FILE}")

    sys.exit(exit_code)
