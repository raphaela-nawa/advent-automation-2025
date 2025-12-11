"""
Day 11 Scheduler Daemon
Runs the orchestrator on a schedule using APScheduler

This script keeps running and executes the report based on the cron schedule.
Alternative to system cron if you don't have access to crontab.

Author: Gleyson - Retail Marketing Automation Specialist
"""

import logging
import sys
import signal
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from day11_CONFIG_settings import (
    DAY11_SCHEDULE_CRON,
    DAY11_TIMEZONE,
    DAY11_LOG_FILE,
    DAY11_LOG_LEVEL,
    day11_ensure_directories
)
from day11_ORCHESTRATOR_main import Day11Orchestrator

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

# Global scheduler instance
scheduler = None


def day11_scheduled_job():
    """Job function that runs on schedule."""
    logger.info("Scheduled job triggered")

    try:
        orchestrator = Day11Orchestrator()
        success = orchestrator.day11_run_report()

        if success:
            logger.info("Scheduled job completed successfully")
        else:
            logger.error("Scheduled job failed")

    except Exception as e:
        logger.error(f"Scheduled job error: {e}")


def day11_start_scheduler():
    """Start the scheduler daemon."""
    global scheduler

    logger.info("=" * 70)
    logger.info("Starting Day 11 Scheduler Daemon")
    logger.info(f"Schedule: {DAY11_SCHEDULE_CRON}")
    logger.info(f"Timezone: {DAY11_TIMEZONE}")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("=" * 70)

    # Create scheduler
    timezone = pytz.timezone(DAY11_TIMEZONE)
    scheduler = BlockingScheduler(timezone=timezone)

    # Parse cron expression
    # Format: "minute hour day month day_of_week"
    # Example: "0 8 * * *" = Every day at 8:00 AM
    cron_parts = DAY11_SCHEDULE_CRON.split()

    if len(cron_parts) != 5:
        logger.error(f"Invalid cron expression: {DAY11_SCHEDULE_CRON}")
        logger.error("Expected format: 'minute hour day month day_of_week'")
        sys.exit(1)

    minute, hour, day, month, day_of_week = cron_parts

    # Add job with cron trigger
    trigger = CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        timezone=timezone
    )

    scheduler.add_job(
        day11_scheduled_job,
        trigger=trigger,
        id='day11_daily_report',
        name='Day 11 Daily Performance Report',
        replace_existing=True
    )

    # Log next run time
    next_run = scheduler.get_jobs()[0].next_run_time
    logger.info(f"Next scheduled run: {next_run}")

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping scheduler...")
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped gracefully")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start scheduler (blocks until shutdown)
    try:
        logger.info("Scheduler is now running. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


def day11_run_once_then_schedule():
    """Run the report immediately, then start the scheduler."""
    logger.info("Running report immediately before starting scheduler...")

    orchestrator = Day11Orchestrator()
    orchestrator.day11_run_report()

    logger.info("Initial run complete. Starting scheduler...")
    day11_start_scheduler()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "now":
            # Run once immediately, then start scheduler
            day11_run_once_then_schedule()

        elif command == "help":
            print("""
Day 11 Scheduler Daemon - Usage

Commands:
  python day11_SCHEDULER_daemon.py        Start scheduler (waits for schedule)
  python day11_SCHEDULER_daemon.py now    Run immediately, then start scheduler
  python day11_SCHEDULER_daemon.py help   Show this help message

Configuration:
  Set DAY11_SCHEDULE_CRON in config/.env (default: "0 8 * * *" = 8am daily)
  Set DAY11_TIMEZONE in config/.env (default: "UTC")

Cron Format:
  minute hour day month day_of_week

Examples:
  "0 8 * * *"       = Every day at 8:00 AM
  "0 8 * * 1-5"     = Weekdays at 8:00 AM
  "0 9,17 * * *"    = Every day at 9:00 AM and 5:00 PM
  "*/30 9-17 * * *" = Every 30 minutes between 9 AM and 5 PM

To run in background:
  nohup python day11_SCHEDULER_daemon.py > scheduler.log 2>&1 &

To stop:
  Press Ctrl+C or send SIGTERM signal
            """)
            sys.exit(0)

        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Run with 'help' for usage information")
            sys.exit(1)
    else:
        # Default: start scheduler
        day11_start_scheduler()
