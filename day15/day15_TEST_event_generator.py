"""
Day 15 - Real-Time Analytics Orchestrator
Test event generator for synthetic SaaS events

Author: Ricardo (SaaS Analytics)
Project: Christmas Data Advent 2025 - Day 15
Purpose: Generate synthetic events to test the webhook pipeline
"""

import requests
import random
import time
import uuid
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
WEBHOOK_URL = "http://localhost:5015/webhook/events"
BATCH_URL = "http://localhost:5015/webhook/batch"
HEALTH_URL = "http://localhost:5015/health"

# Synthetic data
PLANS = ['free', 'basic', 'premium', 'enterprise']
PLAN_PRICES = {'free': 0, 'basic': 29.99, 'premium': 99.99, 'enterprise': 499.99}
FEATURES = ['api_call', 'report_generation', 'data_export', 'user_invite', 'dashboard_view']
SOURCES = ['organic', 'paid_search', 'referral', 'direct', 'social']

def day15_generate_user_signup_event():
    """Generate synthetic user signup event"""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    event = {
        'event_id': f"evt_{uuid.uuid4().hex}",
        'event_type': 'user_signup',
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'metadata': {
            'source': random.choice(SOURCES),
            'email': f"{user_id}@example.com",
            'company': f"Company {random.randint(1, 100)}",
            'country': random.choice(['US', 'UK', 'CA', 'AU', 'DE'])
        }
    }
    return event

def day15_generate_subscription_event():
    """Generate synthetic subscription created event"""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    plan = random.choice(PLANS)
    event = {
        'event_id': f"evt_{uuid.uuid4().hex}",
        'event_type': 'subscription_created',
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'metadata': {
            'plan': plan,
            'amount': PLAN_PRICES[plan],
            'billing_cycle': random.choice(['monthly', 'annual']),
            'trial': plan == 'free'
        }
    }
    return event

def day15_generate_usage_event():
    """Generate synthetic usage tracking event"""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    feature = random.choice(FEATURES)
    event = {
        'event_id': f"evt_{uuid.uuid4().hex}",
        'event_type': 'usage_tracked',
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'metadata': {
            'feature': feature,
            'quantity': random.randint(1, 100),
            'duration_ms': random.randint(100, 5000)
        }
    }
    return event

def day15_send_single_event(event):
    """Send a single event to webhook"""
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=event,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )

        if response.status_code == 202:
            result = response.json()
            logger.info(f"✓ Event accepted: {event['event_type']} ({event['event_id'][:12]}...) - latency: {result.get('latency_ms', 'N/A')}ms")
            return True
        elif response.status_code == 200:
            result = response.json()
            if result.get('status') == 'ignored':
                logger.warning(f"○ Event ignored (duplicate): {event['event_id'][:12]}...")
                return True
        else:
            logger.error(f"✗ Event rejected: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"✗ Error sending event: {e}")
        return False

def day15_send_batch_events(events):
    """Send multiple events as a batch"""
    try:
        response = requests.post(
            BATCH_URL,
            json={'events': events},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 202:
            result = response.json()
            logger.info(f"✓ Batch accepted: {result['results']} - latency: {result.get('latency_ms', 'N/A')}ms")
            return True
        else:
            logger.error(f"✗ Batch rejected: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"✗ Error sending batch: {e}")
        return False

def day15_check_health():
    """Check webhook health"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            health = response.json()
            logger.info(f"✓ Webhook healthy - queue depth: {health.get('queue_depth', 'N/A')}")
            return True
        else:
            logger.error(f"✗ Webhook unhealthy: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Cannot reach webhook: {e}")
        return False

def day15_test_scenario_basic():
    """Test Scenario 1: Basic event flow"""
    logger.info("=" * 60)
    logger.info("TEST SCENARIO 1: Basic Event Flow")
    logger.info("=" * 60)

    # Check health first
    if not day15_check_health():
        logger.error("Webhook not available. Please start the orchestrator first.")
        return

    # Send one of each event type
    events = [
        day15_generate_user_signup_event(),
        day15_generate_subscription_event(),
        day15_generate_usage_event()
    ]

    for event in events:
        day15_send_single_event(event)
        time.sleep(0.5)

    logger.info("Waiting for processing...")
    time.sleep(3)
    day15_check_health()

def day15_test_scenario_burst():
    """Test Scenario 2: Burst of events"""
    logger.info("=" * 60)
    logger.info("TEST SCENARIO 2: Burst of Events (50 events)")
    logger.info("=" * 60)

    if not day15_check_health():
        return

    # Generate 50 random events
    success_count = 0
    for i in range(50):
        event_type = random.choice(['signup', 'subscription', 'usage'])

        if event_type == 'signup':
            event = day15_generate_user_signup_event()
        elif event_type == 'subscription':
            event = day15_generate_subscription_event()
        else:
            event = day15_generate_usage_event()

        if day15_send_single_event(event):
            success_count += 1

        # Small delay to avoid overwhelming
        time.sleep(0.1)

    logger.info(f"Burst complete: {success_count}/50 events accepted")
    time.sleep(5)
    day15_check_health()

def day15_test_scenario_idempotency():
    """Test Scenario 3: Idempotency (duplicate events)"""
    logger.info("=" * 60)
    logger.info("TEST SCENARIO 3: Idempotency (Duplicate Events)")
    logger.info("=" * 60)

    if not day15_check_health():
        return

    # Create event
    event = day15_generate_user_signup_event()

    # Send same event 3 times
    logger.info("Sending same event 3 times...")
    for i in range(3):
        logger.info(f"Attempt {i+1}/3:")
        day15_send_single_event(event)
        time.sleep(1)

    logger.info("Expected: 1 accepted, 2 ignored as duplicates")

def day15_test_scenario_batch():
    """Test Scenario 4: Batch endpoint"""
    logger.info("=" * 60)
    logger.info("TEST SCENARIO 4: Batch Endpoint (20 events)")
    logger.info("=" * 60)

    if not day15_check_health():
        return

    # Generate batch of 20 events
    events = []
    for i in range(20):
        event_type = random.choice(['signup', 'subscription', 'usage'])
        if event_type == 'signup':
            events.append(day15_generate_user_signup_event())
        elif event_type == 'subscription':
            events.append(day15_generate_subscription_event())
        else:
            events.append(day15_generate_usage_event())

    # Send as batch
    day15_send_batch_events(events)

    time.sleep(3)
    day15_check_health()

def day15_test_all_scenarios():
    """Run all test scenarios"""
    logger.info("\n" + "=" * 60)
    logger.info("Day 15 - Event Pipeline Test Suite")
    logger.info("=" * 60 + "\n")

    scenarios = [
        ("Basic Event Flow", day15_test_scenario_basic),
        ("Idempotency Test", day15_test_scenario_idempotency),
        ("Batch Events", day15_test_scenario_batch),
        ("Burst Load", day15_test_scenario_burst)
    ]

    for name, scenario_func in scenarios:
        try:
            scenario_func()
            time.sleep(2)
        except Exception as e:
            logger.error(f"Scenario '{name}' failed: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("Test suite complete!")
    logger.info("=" * 60)

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        if scenario == 'basic':
            day15_test_scenario_basic()
        elif scenario == 'burst':
            day15_test_scenario_burst()
        elif scenario == 'idempotency':
            day15_test_scenario_idempotency()
        elif scenario == 'batch':
            day15_test_scenario_batch()
        else:
            logger.error(f"Unknown scenario: {scenario}")
            logger.info("Available: basic, burst, idempotency, batch, all")
    else:
        # Run all by default
        day15_test_all_scenarios()
