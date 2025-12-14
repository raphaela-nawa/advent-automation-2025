"""
Day 11 Main Orchestrator
Coordinates the daily performance report workflow

This is the main entry point that:
1. Fetches data from Day 01 sources
2. Calculates metrics
3. Formats Slack message
4. Sends to Slack
5. Logs execution

Can be run manually or via scheduler (cron/APScheduler)

Author: Gleyson - Retail Marketing Automation Specialist
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import traceback

# Import Day 11 modules
from day11_CONFIG_settings import (
    DAY11_LOG_FILE,
    DAY11_LOG_LEVEL,
    DAY11_RUN_ON_WEEKENDS,
    DAY11_TEST_MODE,
    DAY11_DRY_RUN,
    DAY11_ENABLE_ERROR_NOTIFICATIONS,
    day11_ensure_directories
)
from day11_DATA_fetcher import Day11DataFetcher, day11_calculate_metrics
from day11_FORMATTER_slack import Day11SlackFormatter, day11_format_simple_text_report
from day11_SENDER_slack import Day11SlackSender

# Set up logging
day11_ensure_directories()

logging.basicConfig(
    level=getattr(logging, DAY11_LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DAY11_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class Day11Orchestrator:
    """Main orchestrator for the daily performance report workflow."""

    def __init__(self):
        self.fetcher = Day11DataFetcher()
        self.formatter = Day11SlackFormatter()
        self.sender = Day11SlackSender()
        self.execution_start_time = None
        self.execution_end_time = None

    def day11_should_run_today(self) -> bool:
        """
        Check if the report should run today based on configuration.

        Returns:
            True if should run, False otherwise
        """
        if DAY11_RUN_ON_WEEKENDS:
            return True

        # Check if today is a weekend (5=Saturday, 6=Sunday)
        is_weekend = datetime.now().weekday() >= 5

        if is_weekend:
            logger.info("Skipping execution: Weekend and DAY11_RUN_ON_WEEKENDS=false")
            return False

        return True

    def day11_run_report(self) -> bool:
        """
        Execute the complete report workflow.

        Returns:
            True if successful, False otherwise
        """
        self.execution_start_time = datetime.now()
        logger.info("=" * 70)
        logger.info("Starting Day 11 Daily Performance Report")
        logger.info(f"Execution time: {self.execution_start_time}")
        logger.info(f"Test mode: {DAY11_TEST_MODE}, Dry run: {DAY11_DRY_RUN}")
        logger.info("=" * 70)

        try:
            # Step 1: Check if should run today
            if not self.day11_should_run_today():
                logger.info("Execution skipped based on schedule configuration")
                return True  # Not an error, just skipped

            # Step 2: Fetch data
            logger.info("Step 1/4: Fetching data from Day 01 sources...")
            ga4_df, ads_df, source_message = self.fetcher.day11_fetch_all_data()

            if ga4_df is None or ads_df is None:
                raise ValueError("Failed to fetch data from any source")

            logger.info(f"✓ Data fetched: {len(ga4_df)} GA4 rows, {len(ads_df)} Ads rows")

            # Step 3: Calculate metrics
            logger.info("Step 2/4: Calculating performance metrics...")
            metrics = day11_calculate_metrics(ga4_df, ads_df)
            logger.info(f"✓ Metrics calculated: {len(metrics)} KPIs")

            # Log key metrics
            logger.info(f"  - Total Sessions: {metrics['total_sessions']:,}")
            logger.info(f"  - Total Spend: ${metrics['total_spend']:,.2f}")
            logger.info(f"  - Cost per Conversion: ${metrics['cost_per_conversion']:.2f}")

            # Step 4: Format message
            logger.info("Step 3/4: Formatting Slack message...")
            if DAY11_TEST_MODE:
                slack_payload = self.formatter.day11_format_test_message()
                logger.info("✓ Test message formatted")
            else:
                slack_payload = self.formatter.day11_format_daily_report(metrics, source_message)
                logger.info(f"✓ Report formatted: {len(slack_payload['blocks'])} blocks")

            # Step 5: Send to Slack
            logger.info("Step 4/4: Sending to Slack...")
            success = self.sender.day11_send_message(slack_payload)

            if success:
                logger.info("✓ Message sent successfully to Slack")
            else:
                logger.error("✗ Failed to send message to Slack")
                return False

            # Log simple text version for audit
            if not DAY11_TEST_MODE:
                logger.info("\n--- Text Report for Audit Log ---")
                text_report = day11_format_simple_text_report(metrics)
                for line in text_report.split('\n'):
                    logger.info(line)

            self.execution_end_time = datetime.now()
            execution_duration = (self.execution_end_time - self.execution_start_time).total_seconds()

            logger.info("=" * 70)
            logger.info("✓ Day 11 Report Completed Successfully")
            logger.info(f"Execution duration: {execution_duration:.2f} seconds")
            logger.info(f"Data source: {self.fetcher.data_source_used}")
            logger.info("=" * 70)

            return True

        except Exception as e:
            logger.error(f"✗ Report execution failed: {e}")
            logger.error(traceback.format_exc())

            # Send error notification if enabled
            if DAY11_ENABLE_ERROR_NOTIFICATIONS and not DAY11_DRY_RUN:
                try:
                    error_payload = self.formatter.day11_format_error_message(
                        e,
                        f"Failed during daily report execution at {datetime.now()}"
                    )
                    self.sender.day11_send_message(error_payload)
                    logger.info("Error notification sent to Slack")
                except Exception as notify_error:
                    logger.error(f"Failed to send error notification: {notify_error}")

            self.execution_end_time = datetime.now()
            return False


def day11_run_once():
    """Run the report workflow once (for manual execution or cron)."""
    orchestrator = Day11Orchestrator()
    success = orchestrator.day11_run_report()
    sys.exit(0 if success else 1)


def day11_run_test():
    """Run in test mode (sends test message instead of full report)."""
    logger.info("Running in TEST MODE")
    orchestrator = Day11Orchestrator()

    # Test connection
    logger.info("Testing Slack connection...")
    if orchestrator.sender.day11_test_connection():
        logger.info("✓ Slack connection test successful")
        return True
    else:
        logger.error("✗ Slack connection test failed")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            logger.info("=" * 70)
            logger.info("Day 11 Test Mode")
            logger.info("=" * 70)
            success = day11_run_test()
            sys.exit(0 if success else 1)

        elif command == "dry-run":
            logger.info("=" * 70)
            logger.info("Day 11 Dry Run Mode (no actual sends)")
            logger.info("=" * 70)
            # Temporarily enable dry run
            import day11_CONFIG_settings
            day11_CONFIG_settings.DAY11_DRY_RUN = True
            day11_run_once()

        elif command == "help":
            print("""
Day 11 Orchestrator - Usage

Commands:
  python day11_ORCHESTRATOR_main.py              Run the daily report
  python day11_ORCHESTRATOR_main.py test         Test Slack connection
  python day11_ORCHESTRATOR_main.py dry-run      Run without sending to Slack
  python day11_ORCHESTRATOR_main.py help         Show this help message

Environment Variables (set in config/.env):
  DAY11_SLACK_WEBHOOK_URL     Slack webhook URL (required)
  DAY11_SCHEDULE_CRON         Cron schedule (default: "0 8 * * *")
  DAY11_RUN_ON_WEEKENDS       Run on weekends (default: false)
  DAY11_REPORT_DAYS_BACK      Days of data to include (default: 7)
  DAY11_DRY_RUN               Dry run mode (default: false)
  DAY11_TEST_MODE             Test mode (default: false)

For full configuration options, see day11_CONFIG_settings.py
            """)
            sys.exit(0)

        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Run with 'help' for usage information")
            sys.exit(1)
    else:
        # Default: run the report
        day11_run_once()
