"""
Day 15 - Real-Time Analytics Orchestrator
Configuration for Redis buffer and event processing

Author: Ricardo (SaaS Analytics)
Project: Christmas Data Advent 2025 - Day 15
Context: Near-real-time processing for SaaS metrics (connects to Day 9 - Jo MicroSaaS)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

# Redis Configuration
DAY15_REDIS_HOST = os.getenv('DAY15_REDIS_HOST', 'localhost')
DAY15_REDIS_PORT = int(os.getenv('DAY15_REDIS_PORT', '6379'))
DAY15_REDIS_DB = int(os.getenv('DAY15_REDIS_DB', '0'))
DAY15_REDIS_PASSWORD = os.getenv('DAY15_REDIS_PASSWORD', None)

# Redis Queue Names
DAY15_EVENT_QUEUE = 'day15:events:queue'
DAY15_PROCESSING_QUEUE = 'day15:events:processing'
DAY15_DEAD_LETTER_QUEUE = 'day15:events:failed'
DAY15_IDEMPOTENCY_SET = 'day15:events:processed'

# Webhook Configuration
DAY15_WEBHOOK_HOST = os.getenv('DAY15_WEBHOOK_HOST', '0.0.0.0')
DAY15_WEBHOOK_PORT = int(os.getenv('DAY15_WEBHOOK_PORT', '5000'))

# Processing Configuration
DAY15_BATCH_SIZE = int(os.getenv('DAY15_BATCH_SIZE', '10'))
DAY15_BATCH_TIMEOUT_SECONDS = int(os.getenv('DAY15_BATCH_TIMEOUT_SECONDS', '5'))
DAY15_MAX_RETRIES = int(os.getenv('DAY15_MAX_RETRIES', '3'))
DAY15_RETRY_DELAY_SECONDS = int(os.getenv('DAY15_RETRY_DELAY_SECONDS', '2'))

# Monitoring Configuration
DAY15_LOG_LEVEL = os.getenv('DAY15_LOG_LEVEL', 'INFO')
DAY15_LOG_FILE = 'logs/day15_pipeline.log'
DAY15_METRICS_ENABLED = os.getenv('DAY15_METRICS_ENABLED', 'true').lower() == 'true'

# Idempotency Configuration
DAY15_IDEMPOTENCY_TTL_HOURS = int(os.getenv('DAY15_IDEMPOTENCY_TTL_HOURS', '24'))
DAY15_IDEMPOTENCY_TTL_SECONDS = DAY15_IDEMPOTENCY_TTL_HOURS * 3600

# Dashboard Configuration (connects to Day 9)
DAY15_DASHBOARD_UPDATE_ENABLED = os.getenv('DAY15_DASHBOARD_UPDATE_ENABLED', 'false').lower() == 'true'
DAY15_DASHBOARD_API_URL = os.getenv('DAY15_DASHBOARD_API_URL', 'http://localhost:8000/api/metrics')

# Feature Flags
DAY15_USE_MOCK_REDIS = os.getenv('DAY15_USE_MOCK_REDIS', 'false').lower() == 'true'
DAY15_DRY_RUN = os.getenv('DAY15_DRY_RUN', 'false').lower() == 'true'

def day15_get_redis_connection():
    """Get Redis connection with proper configuration"""
    import redis

    if DAY15_USE_MOCK_REDIS:
        # For testing without Redis
        return None

    return redis.Redis(
        host=DAY15_REDIS_HOST,
        port=DAY15_REDIS_PORT,
        db=DAY15_REDIS_DB,
        password=DAY15_REDIS_PASSWORD,
        decode_responses=True
    )

def day15_validate_config():
    """Validate configuration settings"""
    errors = []

    if not DAY15_USE_MOCK_REDIS:
        try:
            r = day15_get_redis_connection()
            r.ping()
        except Exception as e:
            errors.append(f"Redis connection failed: {e}")

    if DAY15_BATCH_SIZE < 1:
        errors.append("DAY15_BATCH_SIZE must be >= 1")

    if DAY15_BATCH_TIMEOUT_SECONDS < 1:
        errors.append("DAY15_BATCH_TIMEOUT_SECONDS must be >= 1")

    return errors
