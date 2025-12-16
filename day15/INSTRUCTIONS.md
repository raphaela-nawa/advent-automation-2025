# Day 15 - Real-Time Analytics Orchestrator

**Project:** Christmas Data Advent 2025 - PROJECT 3E
**Author:** Ricardo (SaaS Analytics)
**Industry:** SaaS / Technology
**Orchestration Pattern:** Event-driven webhook processing with Redis buffer

---

## 📋 Project Overview

This project demonstrates a **real-time event processing pipeline** for SaaS analytics. It receives webhook events from a SaaS application (user signups, subscriptions, usage tracking), queues them in Redis for reliability, and processes them in micro-batches to update analytics dashboards.

### Business Context

Ricardo works as a SaaS analytics specialist and needs to process user events in near-real-time to power analytics dashboards. The system must:
- Accept high-velocity webhook events without blocking
- Prevent duplicate event processing (idempotency)
- Handle failures gracefully with retry logic
- Track processing latency from event receipt to completion
- Scale to handle burst traffic

---

## 🎯 Success Criteria (from ORCHESTRATION_DELIVERY_CRITERIA.md)

### Specific Requirements for Day 15:

- [x] **Webhook Endpoint:** Flask endpoint receiving events
- [x] **Redis Buffer:** Events queued in Redis before processing
- [x] **Batch Processing:** Consumer processes events in micro-batches (size: 10)
- [x] **Idempotency Keys:** Events with same ID don't process twice
- [x] **Latency Monitoring:** Logs show time from event receipt to processing
- [x] **Error Queue:** Failed events go to dead-letter queue for inspection
- [x] **Graceful Shutdown:** Can stop processing without losing events
- [x] **Dashboard Update:** Triggers update to analytics dashboard/database (configurable)

---

## 🏗️ Architecture

```
[SaaS App] → [Webhook Endpoint] → [Redis Queue] → [Batch Consumer] → [Analytics Dashboard]
                   ↓                     ↓                 ↓
              Non-blocking          Buffer Layer      Idempotency Check
              202 Response          (Reliability)      (Deduplication)
                                        ↓
                                 [Dead Letter Queue]
                                    (Failed Events)
```

### Components:

1. **day15_WEBHOOK_receiver.py** - Flask webhook server
   - Accepts POST requests with event data
   - Validates payload and checks for duplicates
   - Queues events in Redis (non-blocking, <50ms response)
   - Returns 202 Accepted immediately

2. **day15_CONSUMER_batch_processor.py** - Event processor
   - Fetches batches of 10 events from Redis queue
   - Processes each event based on type (signup, subscription, usage)
   - Retries failed events up to 3 times
   - Moves permanently failed events to dead-letter queue
   - Tracks latency metrics

3. **day15_ORCHESTRATOR_main.py** - Process manager
   - Runs webhook and consumer as separate processes
   - Handles graceful shutdown signals
   - Validates configuration on startup

4. **day15_CONFIG_redis.py** - Configuration management
   - All settings centralized and isolated (DAY15_ prefix)
   - Mock mode for testing without Redis
   - Environment variable driven

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis Server (optional - can use mock mode)

### Installation

```bash
# Navigate to day15 directory
cd day15

# Install dependencies
pip install -r day15_requirements.txt

# (Optional) Start Redis if using real Redis
# redis-server
```

### Configuration

The system is configured via `config/.env`. Key settings:

```bash
# Use mock mode (no Redis required) - default for testing
DAY15_USE_MOCK_REDIS=true

# Or use real Redis
DAY15_USE_MOCK_REDIS=false
DAY15_REDIS_HOST=localhost
DAY15_REDIS_PORT=6379

# Webhook settings
DAY15_WEBHOOK_PORT=5015

# Processing settings
DAY15_BATCH_SIZE=10
DAY15_BATCH_TIMEOUT_SECONDS=5
```

### Running the Orchestrator

```bash
# Start both webhook and consumer
python3 day15_ORCHESTRATOR_main.py
```

You should see:
```
================================================================================
Day 15 - Real-Time Analytics Orchestrator
Author: Ricardo (SaaS Analytics)
================================================================================
Webhook endpoint: http://localhost:5015/webhook/events
Health check: http://localhost:5015/health
================================================================================
```

### Testing with Synthetic Events

In another terminal:

```bash
# Run basic test scenario (3 events)
python3 day15_TEST_event_generator.py basic

# Run all test scenarios
python3 day15_TEST_event_generator.py

# Test idempotency (duplicate detection)
python3 day15_TEST_event_generator.py idempotency

# Test burst load (50 events)
python3 day15_TEST_event_generator.py burst

# Test batch endpoint (20 events at once)
python3 day15_TEST_event_generator.py batch
```

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:5015/health

# Send single event
curl -X POST http://localhost:5015/webhook/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123456",
    "event_type": "user_signup",
    "user_id": "user_abc123",
    "timestamp": "2025-12-16T10:00:00Z",
    "metadata": {
      "source": "organic",
      "email": "test@example.com"
    }
  }'

# Send batch of events
curl -X POST http://localhost:5015/webhook/batch \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      { "event_id": "evt_001", "event_type": "user_signup", "timestamp": "2025-12-16T10:00:00Z" },
      { "event_id": "evt_002", "event_type": "subscription_created", "timestamp": "2025-12-16T10:01:00Z" }
    ]
  }'
```

---

## 📊 Monitoring

### Log Files

All activity is logged to `day15/logs/day15_pipeline.log`:

```bash
# Watch logs in real-time
tail -f day15/logs/day15_pipeline.log

# View processing statistics
grep "STATISTICS" day15/logs/day15_pipeline.log
```

### Key Metrics Logged:

- **Event latency:** Time from `received_at` to processing completion
- **Queue depth:** Number of events waiting to be processed
- **Success rate:** Events processed vs failed
- **Batch metrics:** Events per batch, batches per minute

### Example Log Output:

```
2025-12-16 19:30:15,234 - INFO - Event received: user_signup (evt_a1b2c3) - latency: 12.45ms
2025-12-16 19:30:15,235 - INFO - Event queued (mock): evt_a1b2c3, queue size: 1
2025-12-16 19:30:20,567 - INFO - Processing batch of 3 events
2025-12-16 19:30:20,578 - INFO - User signup: user_abc123 from organic
2025-12-16 19:30:20,579 - INFO - Processed user_signup (evt_a1b2c3) - latency: 5343.40ms
2025-12-16 19:30:20,601 - INFO - Batch complete: 3 success, 0 failed
```

---

## 🔧 Configuration Reference

### Environment Variables (config/.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `DAY15_REDIS_HOST` | `localhost` | Redis server hostname |
| `DAY15_REDIS_PORT` | `6379` | Redis server port |
| `DAY15_REDIS_PASSWORD` | `""` | Redis password (if required) |
| `DAY15_WEBHOOK_PORT` | `5015` | Webhook server port |
| `DAY15_BATCH_SIZE` | `10` | Events per batch |
| `DAY15_BATCH_TIMEOUT_SECONDS` | `5` | Wait time before processing partial batch |
| `DAY15_MAX_RETRIES` | `3` | Retry attempts for failed events |
| `DAY15_IDEMPOTENCY_TTL_HOURS` | `24` | How long to remember processed event IDs |
| `DAY15_USE_MOCK_REDIS` | `true` | Use in-memory queue instead of Redis |
| `DAY15_DRY_RUN` | `false` | Log events without processing |
| `DAY15_DASHBOARD_UPDATE_ENABLED` | `false` | Enable dashboard API updates |

---

## 🧪 Testing Scenarios

### 1. Basic Event Flow
Tests one event of each type (signup, subscription, usage):
```bash
python3 day15_TEST_event_generator.py basic
```

### 2. Idempotency
Sends same event 3 times to verify duplicate detection:
```bash
python3 day15_TEST_event_generator.py idempotency
```
Expected: 1 accepted, 2 ignored as duplicates

### 3. Burst Load
Sends 50 random events to test throughput:
```bash
python3 day15_TEST_event_generator.py burst
```

### 4. Batch Endpoint
Sends 20 events in a single batch request:
```bash
python3 day15_TEST_event_generator.py batch
```

---

## 📁 File Structure

```
day15/
├── day15_CONFIG_redis.py          # Configuration management
├── day15_WEBHOOK_receiver.py      # Flask webhook server
├── day15_CONSUMER_batch_processor.py  # Event processing consumer
├── day15_ORCHESTRATOR_main.py     # Process orchestration
├── day15_TEST_event_generator.py  # Synthetic event generator
├── day15_requirements.txt         # Python dependencies
├── .env.example                   # Environment variable template
├── logs/
│   └── day15_pipeline.log         # Execution logs
├── data/
│   └── day15_sample_events.json   # Sample event data
└── README.md                      # Full documentation
```

---

## 🚨 Troubleshooting

### Webhook Not Starting

**Problem:** `Connection refused` when testing
**Solution:** Check if port 5015 is available:
```bash
lsof -i :5015
# If in use, change DAY15_WEBHOOK_PORT in config/.env
```

### Redis Connection Failed

**Problem:** `Redis connection failed` error
**Solution:** Use mock mode for testing:
```bash
# In config/.env
DAY15_USE_MOCK_REDIS=true
```

Or start Redis server:
```bash
redis-server
```

### Events Not Processing

**Problem:** Events queued but not processed
**Solution:** Check consumer logs:
```bash
grep "consumer" day15/logs/day15_pipeline.log
```

Ensure both webhook and consumer processes are running.

### High Latency

**Problem:** Processing latency > 10 seconds
**Solution:**
- Reduce `DAY15_BATCH_SIZE` for faster processing
- Increase `DAY15_BATCH_TIMEOUT_SECONDS` to wait for fuller batches
- Check if dashboard API (if enabled) is responding slowly

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **Event-Driven Architecture:** Webhook-based async processing
2. **Queue-Based Reliability:** Redis as message buffer
3. **Idempotency Patterns:** Preventing duplicate processing
4. **Graceful Degradation:** Error handling and dead-letter queues
5. **Latency Monitoring:** End-to-end timing metrics
6. **Process Orchestration:** Multi-process coordination
7. **Isolated Code Design:** All naming follows `day15_` pattern

---

## 📚 Next Steps

### Enhancements for Production:

1. **Horizontal Scaling:**
   - Run multiple consumer processes
   - Use Redis Cluster for HA

2. **Monitoring Dashboard:**
   - Grafana + Prometheus for metrics
   - Alerting on queue depth / failure rate

3. **Event Schema Validation:**
   - JSON Schema validation
   - Reject malformed events early

4. **Dashboard Integration:**
   - Connect to Day 9 (Jo MicroSaaS) dashboard
   - Real-time metrics updates

5. **Cloud Deployment:**
   - Containerize with Docker
   - Deploy to AWS ECS / GCP Cloud Run
   - Use managed Redis (ElastiCache / Memorystore)

---

## 📞 Support

For questions or issues:
1. Check logs: `day15/logs/day15_pipeline.log`
2. Verify configuration: `config/.env`
3. Test with mock mode: `DAY15_USE_MOCK_REDIS=true`
4. Review ORCHESTRATION_DELIVERY_CRITERIA.md

---

**Time to Deliver:** 3 hours
**Status:** ✅ Complete
**Portfolio Ready:** Yes
