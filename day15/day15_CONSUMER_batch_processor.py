"""
Day 15 - Real-Time Analytics Orchestrator
Batch processor consumer for queued events

Author: Ricardo (SaaS Analytics)
Project: Christmas Data Advent 2025 - Day 15
Purpose: Process events from Redis queue in micro-batches and update analytics
"""

import json
import time
import logging
import signal
import sys
from datetime import datetime
from typing import List, Dict, Any
import requests

from day15_CONFIG_redis import (
    day15_get_redis_connection,
    DAY15_EVENT_QUEUE,
    DAY15_PROCESSING_QUEUE,
    DAY15_DEAD_LETTER_QUEUE,
    DAY15_BATCH_SIZE,
    DAY15_BATCH_TIMEOUT_SECONDS,
    DAY15_MAX_RETRIES,
    DAY15_RETRY_DELAY_SECONDS,
    DAY15_USE_MOCK_REDIS,
    DAY15_LOG_FILE,
    DAY15_LOG_LEVEL,
    DAY15_DASHBOARD_UPDATE_ENABLED,
    DAY15_DASHBOARD_API_URL,
    DAY15_DRY_RUN
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

# Global flag for graceful shutdown
day15_running = True

def day15_signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT/SIGTERM"""
    global day15_running
    logger.info("Shutdown signal received, finishing current batch...")
    day15_running = False

signal.signal(signal.SIGINT, day15_signal_handler)
signal.signal(signal.SIGTERM, day15_signal_handler)

class Day15EventProcessor:
    """Processes events from queue in batches"""

    def __init__(self):
        self.redis_conn = day15_get_redis_connection() if not DAY15_USE_MOCK_REDIS else None
        self.stats = {
            'events_processed': 0,
            'batches_processed': 0,
            'events_failed': 0,
            'total_latency_ms': 0
        }

    def day15_fetch_batch(self) -> List[Dict[str, Any]]:
        """Fetch a batch of events from the queue"""
        if DAY15_USE_MOCK_REDIS:
            # Mock implementation
            from day15_WEBHOOK_receiver import day15_mock_queue
            batch = []
            for _ in range(min(DAY15_BATCH_SIZE, len(day15_mock_queue))):
                if day15_mock_queue:
                    batch.append(day15_mock_queue.pop(0))
            return batch

        batch = []
        pipeline = self.redis_conn.pipeline()

        # Use RPOPLPUSH for atomic move to processing queue
        for _ in range(DAY15_BATCH_SIZE):
            pipeline.rpoplpush(DAY15_EVENT_QUEUE, DAY15_PROCESSING_QUEUE)

        results = pipeline.execute()

        for result in results:
            if result:
                try:
                    event = json.loads(result)
                    batch.append(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in queue: {e}")

        return batch

    def day15_process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event

        Business logic for SaaS metrics:
        - user_signup: Increment user count, track source
        - subscription_created: Add to MRR, track plan
        - usage_tracked: Update usage metrics, check limits
        """
        try:
            event_type = event.get('event_type')
            event_id = event.get('event_id')

            # Calculate processing latency
            received_at = event.get('received_at')
            if received_at:
                received_time = datetime.fromisoformat(received_at.replace('Z', '+00:00'))
                latency_ms = (datetime.utcnow() - received_time.replace(tzinfo=None)).total_seconds() * 1000
                self.stats['total_latency_ms'] += latency_ms
            else:
                latency_ms = 0

            if DAY15_DRY_RUN:
                logger.info(f"[DRY RUN] Would process {event_type} ({event_id}) - latency: {latency_ms:.2f}ms")
                return True

            # Process based on event type
            if event_type == 'user_signup':
                self._process_user_signup(event)
            elif event_type == 'subscription_created':
                self._process_subscription(event)
            elif event_type == 'usage_tracked':
                self._process_usage(event)
            else:
                logger.warning(f"Unknown event type: {event_type}")

            logger.info(f"Processed {event_type} ({event_id}) - latency: {latency_ms:.2f}ms")
            return True

        except Exception as e:
            logger.error(f"Error processing event {event.get('event_id')}: {e}", exc_info=True)
            return False

    def _process_user_signup(self, event: Dict[str, Any]):
        """Process user signup event"""
        user_id = event.get('user_id')
        metadata = event.get('metadata', {})
        source = metadata.get('source', 'unknown')

        logger.info(f"User signup: {user_id} from {source}")

        # Update dashboard/database
        if DAY15_DASHBOARD_UPDATE_ENABLED:
            self._update_dashboard({
                'metric': 'user_count',
                'action': 'increment',
                'user_id': user_id,
                'source': source
            })

    def _process_subscription(self, event: Dict[str, Any]):
        """Process subscription created event"""
        user_id = event.get('user_id')
        metadata = event.get('metadata', {})
        plan = metadata.get('plan', 'unknown')
        amount = metadata.get('amount', 0)

        logger.info(f"Subscription created: {user_id} - {plan} (${amount})")

        # Update MRR
        if DAY15_DASHBOARD_UPDATE_ENABLED:
            self._update_dashboard({
                'metric': 'mrr',
                'action': 'add',
                'user_id': user_id,
                'plan': plan,
                'amount': amount
            })

    def _process_usage(self, event: Dict[str, Any]):
        """Process usage tracking event"""
        user_id = event.get('user_id')
        metadata = event.get('metadata', {})
        feature = metadata.get('feature', 'unknown')
        quantity = metadata.get('quantity', 1)

        logger.info(f"Usage tracked: {user_id} - {feature} ({quantity})")

        # Update usage metrics
        if DAY15_DASHBOARD_UPDATE_ENABLED:
            self._update_dashboard({
                'metric': 'usage',
                'action': 'increment',
                'user_id': user_id,
                'feature': feature,
                'quantity': quantity
            })

    def _update_dashboard(self, payload: Dict[str, Any]):
        """Update analytics dashboard via API"""
        try:
            response = requests.post(
                DAY15_DASHBOARD_API_URL,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.debug(f"Dashboard updated: {payload['metric']}")
        except Exception as e:
            logger.warning(f"Dashboard update failed: {e}")
            # Don't fail the event processing if dashboard update fails

    def day15_process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of events"""
        results = {
            'success': 0,
            'failed': 0
        }

        for event in batch:
            event_id = event.get('event_id')

            # Try processing with retries
            success = False
            for attempt in range(1, DAY15_MAX_RETRIES + 1):
                try:
                    if self.day15_process_event(event):
                        success = True
                        break
                    else:
                        if attempt < DAY15_MAX_RETRIES:
                            time.sleep(DAY15_RETRY_DELAY_SECONDS)
                except Exception as e:
                    logger.error(f"Attempt {attempt}/{DAY15_MAX_RETRIES} failed for {event_id}: {e}")
                    if attempt < DAY15_MAX_RETRIES:
                        time.sleep(DAY15_RETRY_DELAY_SECONDS)

            if success:
                results['success'] += 1
                self.stats['events_processed'] += 1
                # Remove from processing queue
                if not DAY15_USE_MOCK_REDIS:
                    self.redis_conn.lrem(DAY15_PROCESSING_QUEUE, 1, json.dumps(event))
            else:
                results['failed'] += 1
                self.stats['events_failed'] += 1
                # Move to dead letter queue
                self.day15_move_to_dead_letter(event)

        return results

    def day15_move_to_dead_letter(self, event: Dict[str, Any]):
        """Move failed event to dead letter queue"""
        if DAY15_USE_MOCK_REDIS:
            logger.warning(f"Event failed (mock): {event.get('event_id')}")
            return

        event['failed_at'] = datetime.utcnow().isoformat()
        event['failure_reason'] = 'max_retries_exceeded'

        self.redis_conn.lpush(DAY15_DEAD_LETTER_QUEUE, json.dumps(event))
        self.redis_conn.lrem(DAY15_PROCESSING_QUEUE, 1, json.dumps(event))

        logger.error(f"Event moved to dead letter queue: {event.get('event_id')}")

    def day15_print_stats(self):
        """Print processing statistics"""
        avg_latency = 0
        if self.stats['events_processed'] > 0:
            avg_latency = self.stats['total_latency_ms'] / self.stats['events_processed']

        logger.info("=" * 60)
        logger.info("PROCESSING STATISTICS")
        logger.info(f"Batches processed: {self.stats['batches_processed']}")
        logger.info(f"Events processed: {self.stats['events_processed']}")
        logger.info(f"Events failed: {self.stats['events_failed']}")
        logger.info(f"Average latency: {avg_latency:.2f}ms")
        logger.info("=" * 60)

def day15_run_consumer():
    """Main consumer loop"""
    logger.info("Starting Day 15 batch processor consumer")
    logger.info(f"Batch size: {DAY15_BATCH_SIZE}, Timeout: {DAY15_BATCH_TIMEOUT_SECONDS}s")
    logger.info(f"Using mock Redis: {DAY15_USE_MOCK_REDIS}")
    logger.info(f"Dry run mode: {DAY15_DRY_RUN}")

    processor = Day15EventProcessor()

    try:
        while day15_running:
            # Fetch batch
            batch = processor.day15_fetch_batch()

            if batch:
                logger.info(f"Processing batch of {len(batch)} events")

                # Process batch
                results = processor.day15_process_batch(batch)
                processor.stats['batches_processed'] += 1

                logger.info(f"Batch complete: {results['success']} success, {results['failed']} failed")
            else:
                # No events, wait before checking again
                time.sleep(DAY15_BATCH_TIMEOUT_SECONDS)

        # Graceful shutdown
        logger.info("Consumer shutting down gracefully")
        processor.day15_print_stats()

    except Exception as e:
        logger.error(f"Fatal error in consumer: {e}", exc_info=True)
        processor.day15_print_stats()
        sys.exit(1)

if __name__ == '__main__':
    day15_run_consumer()
