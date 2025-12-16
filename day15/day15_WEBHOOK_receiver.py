"""
Day 15 - Real-Time Analytics Orchestrator
Webhook receiver for SaaS events

Author: Ricardo (SaaS Analytics)
Project: Christmas Data Advent 2025 - Day 15
Purpose: Non-blocking webhook endpoint that queues events in Redis for batch processing
"""

from flask import Flask, request, jsonify
import json
import time
import logging
from datetime import datetime
from day15_CONFIG_redis import (
    day15_get_redis_connection,
    DAY15_EVENT_QUEUE,
    DAY15_IDEMPOTENCY_SET,
    DAY15_IDEMPOTENCY_TTL_SECONDS,
    DAY15_USE_MOCK_REDIS,
    DAY15_WEBHOOK_HOST,
    DAY15_WEBHOOK_PORT,
    DAY15_LOG_FILE,
    DAY15_LOG_LEVEL
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

# Initialize Flask app
app = Flask(__name__)

# Mock queue for testing without Redis
day15_mock_queue = []

def day15_is_duplicate_event(redis_conn, event_id):
    """Check if event has already been processed (idempotency check)"""
    if DAY15_USE_MOCK_REDIS:
        # Mock implementation
        return event_id in [e.get('event_id') for e in day15_mock_queue if 'processed' in e]

    return redis_conn.sismember(DAY15_IDEMPOTENCY_SET, event_id)

def day15_mark_event_received(redis_conn, event_id):
    """Mark event as received to prevent duplicates"""
    if DAY15_USE_MOCK_REDIS:
        return True

    # Add to set with TTL
    redis_conn.sadd(DAY15_IDEMPOTENCY_SET, event_id)
    redis_conn.expire(DAY15_IDEMPOTENCY_SET, DAY15_IDEMPOTENCY_TTL_SECONDS)
    return True

def day15_queue_event(redis_conn, event_data):
    """Add event to Redis queue for processing"""
    if DAY15_USE_MOCK_REDIS:
        day15_mock_queue.append(event_data)
        logger.info(f"Event queued (mock): {event_data['event_id']}, queue size: {len(day15_mock_queue)}")
        return True

    # Push to Redis list (queue)
    redis_conn.lpush(DAY15_EVENT_QUEUE, json.dumps(event_data))
    queue_size = redis_conn.llen(DAY15_EVENT_QUEUE)
    logger.info(f"Event queued: {event_data['event_id']}, queue depth: {queue_size}")
    return True

@app.route('/health', methods=['GET'])
def day15_health_check():
    """Health check endpoint"""
    try:
        if not DAY15_USE_MOCK_REDIS:
            redis_conn = day15_get_redis_connection()
            redis_conn.ping()
            queue_depth = redis_conn.llen(DAY15_EVENT_QUEUE)
        else:
            queue_depth = len(day15_mock_queue)

        return jsonify({
            'status': 'healthy',
            'queue_depth': queue_depth,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/webhook/events', methods=['POST'])
def day15_receive_event():
    """
    Webhook endpoint to receive SaaS events

    Expected payload:
    {
        "event_id": "unique-event-id",
        "event_type": "user_signup|subscription_created|usage_tracked",
        "user_id": "user-123",
        "timestamp": "2025-12-16T10:30:00Z",
        "metadata": {
            "plan": "premium",
            "amount": 99.99,
            ...
        }
    }
    """
    start_time = time.time()

    try:
        # Validate request
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        event = request.get_json()

        # Validate required fields
        required_fields = ['event_id', 'event_type', 'timestamp']
        missing_fields = [f for f in required_fields if f not in event]

        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        event_id = event['event_id']
        event_type = event['event_type']

        # Get Redis connection
        redis_conn = day15_get_redis_connection() if not DAY15_USE_MOCK_REDIS else None

        # Check for duplicate (idempotency)
        if day15_is_duplicate_event(redis_conn, event_id):
            logger.info(f"Duplicate event ignored: {event_id}")
            return jsonify({
                'status': 'ignored',
                'reason': 'duplicate_event',
                'event_id': event_id
            }), 200

        # Add received timestamp
        event['received_at'] = datetime.utcnow().isoformat()

        # Queue event for processing
        day15_queue_event(redis_conn, event)
        day15_mark_event_received(redis_conn, event_id)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        logger.info(f"Event received: {event_type} ({event_id}) - latency: {latency_ms:.2f}ms")

        return jsonify({
            'status': 'accepted',
            'event_id': event_id,
            'queued_at': event['received_at'],
            'latency_ms': round(latency_ms, 2)
        }), 202  # 202 Accepted - processing will happen async

    except Exception as e:
        logger.error(f"Error receiving event: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/webhook/batch', methods=['POST'])
def day15_receive_batch():
    """
    Batch webhook endpoint for multiple events

    Expected payload:
    {
        "events": [
            {...event1...},
            {...event2...},
            ...
        ]
    }
    """
    start_time = time.time()

    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        events = data.get('events', [])

        if not events or not isinstance(events, list):
            return jsonify({'error': 'events array required'}), 400

        redis_conn = day15_get_redis_connection() if not DAY15_USE_MOCK_REDIS else None

        results = {
            'accepted': 0,
            'duplicates': 0,
            'errors': 0
        }

        for event in events:
            try:
                event_id = event.get('event_id')
                if not event_id:
                    results['errors'] += 1
                    continue

                if day15_is_duplicate_event(redis_conn, event_id):
                    results['duplicates'] += 1
                    continue

                event['received_at'] = datetime.utcnow().isoformat()
                day15_queue_event(redis_conn, event)
                day15_mark_event_received(redis_conn, event_id)
                results['accepted'] += 1

            except Exception as e:
                logger.error(f"Error processing event in batch: {e}")
                results['errors'] += 1

        latency_ms = (time.time() - start_time) * 1000

        logger.info(f"Batch processed: {results['accepted']} accepted, {results['duplicates']} duplicates, {results['errors']} errors - latency: {latency_ms:.2f}ms")

        return jsonify({
            'status': 'processed',
            'results': results,
            'total_events': len(events),
            'latency_ms': round(latency_ms, 2)
        }), 202

    except Exception as e:
        logger.error(f"Error receiving batch: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def day15_run_webhook_server():
    """Start the webhook server"""
    logger.info(f"Starting Day 15 webhook server on {DAY15_WEBHOOK_HOST}:{DAY15_WEBHOOK_PORT}")
    logger.info(f"Using mock Redis: {DAY15_USE_MOCK_REDIS}")

    app.run(
        host=DAY15_WEBHOOK_HOST,
        port=DAY15_WEBHOOK_PORT,
        debug=False  # Set to False for production-like behavior
    )

if __name__ == '__main__':
    day15_run_webhook_server()
