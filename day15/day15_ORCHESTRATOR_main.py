"""
Day 15 - Real-Time Analytics Orchestrator
Main orchestrator for running webhook and consumer together

Author: Ricardo (SaaS Analytics)
Project: Christmas Data Advent 2025 - Day 15
Purpose: Manage both webhook receiver and batch processor as a unified service
"""

import sys
import logging
import multiprocessing
import time
from datetime import datetime

from day15_CONFIG_redis import (
    day15_validate_config,
    DAY15_LOG_FILE,
    DAY15_LOG_LEVEL,
    DAY15_USE_MOCK_REDIS,
    DAY15_WEBHOOK_PORT
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, DAY15_LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DAY15_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def day15_run_webhook_process():
    """Run webhook receiver in separate process"""
    from day15_WEBHOOK_receiver import day15_run_webhook_server
    try:
        day15_run_webhook_server()
    except Exception as e:
        logger.error(f"Webhook process error: {e}", exc_info=True)
        sys.exit(1)

def day15_run_consumer_process():
    """Run batch consumer in separate process"""
    from day15_CONSUMER_batch_processor import day15_run_consumer
    try:
        day15_run_consumer()
    except Exception as e:
        logger.error(f"Consumer process error: {e}", exc_info=True)
        sys.exit(1)

def day15_main():
    """Main orchestrator - runs both webhook and consumer"""
    logger.info("=" * 80)
    logger.info("Day 15 - Real-Time Analytics Orchestrator")
    logger.info("Author: Ricardo (SaaS Analytics)")
    logger.info("Project: Christmas Data Advent 2025")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.utcnow().isoformat()}Z")
    logger.info(f"Mock Redis mode: {DAY15_USE_MOCK_REDIS}")
    logger.info(f"Webhook port: {DAY15_WEBHOOK_PORT}")
    logger.info("=" * 80)

    # Validate configuration
    logger.info("Validating configuration...")
    config_errors = day15_validate_config()

    if config_errors:
        logger.error("Configuration validation failed:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please fix configuration errors before running")
        sys.exit(1)

    logger.info("Configuration validated successfully")

    # Start both processes
    webhook_process = multiprocessing.Process(
        target=day15_run_webhook_process,
        name="day15-webhook"
    )

    consumer_process = multiprocessing.Process(
        target=day15_run_consumer_process,
        name="day15-consumer"
    )

    try:
        logger.info("Starting webhook receiver process...")
        webhook_process.start()

        # Give webhook time to start
        time.sleep(2)

        logger.info("Starting batch consumer process...")
        consumer_process.start()

        logger.info("=" * 80)
        logger.info("Both processes running. Press Ctrl+C to stop.")
        logger.info("Webhook endpoint: http://localhost:{}/webhook/events".format(DAY15_WEBHOOK_PORT))
        logger.info("Health check: http://localhost:{}/health".format(DAY15_WEBHOOK_PORT))
        logger.info("=" * 80)

        # Wait for processes
        webhook_process.join()
        consumer_process.join()

    except KeyboardInterrupt:
        logger.info("Shutdown signal received")

        # Graceful shutdown
        logger.info("Stopping webhook receiver...")
        webhook_process.terminate()
        webhook_process.join(timeout=5)

        logger.info("Stopping batch consumer...")
        consumer_process.terminate()
        consumer_process.join(timeout=5)

        logger.info("Shutdown complete")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)

        # Force cleanup
        if webhook_process.is_alive():
            webhook_process.terminate()
        if consumer_process.is_alive():
            consumer_process.terminate()

        sys.exit(1)

if __name__ == '__main__':
    day15_main()
