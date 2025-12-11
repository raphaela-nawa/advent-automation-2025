# Day 11: Retail Daily Performance Report Automation

**Project 3A - Orchestration Pillar**
**Stakeholder:** Gleyson - Retail marketing professional who needs automated daily reports
**Industry:** Retail/E-commerce Marketing
**Tool:** Python orchestration (n8n-equivalent workflow architecture)

## 📋 Overview

This project automates the daily delivery of retail performance reports by:
1. Fetching GA4 and Google Ads data from Day 01 sources
2. Calculating key performance metrics
3. Formatting beautiful Slack messages with Block Kit
4. Sending reports on schedule (daily at 8am UTC)
5. Logging all execution for audit trails

### What This Project Does

- ✅ **Automated Data Fetching** with multi-source fallback (BigQuery → CSV → Synthetic)
- ✅ **Metric Calculation** - 18 KPIs including sessions, spend, conversions, CTR, CPC
- ✅ **Rich Slack Formatting** using Block Kit with emojis and markdown
- ✅ **Flexible Scheduling** via cron or Python scheduler (APScheduler)
- ✅ **Error Handling** with retry logic and error notifications
- ✅ **Idempotent Operations** - re-running produces same report safely
- ✅ **Comprehensive Logging** for audit and debugging

### What This Project Does NOT Do

- ❌ Data ingestion (that's Day 01)
- ❌ Complex data modeling (that's Pilar B)
- ❌ Interactive dashboards (that's Pilar D)
- ❌ AI insights (that's Pilar E)

This is a **pure orchestration project** - automating the flow of information from source to destination.

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
python3 --version

# Install dependencies
cd day11
pip install -r day11_requirements.txt
```

### Test the Workflow (No Configuration Needed)

```bash
# Test with synthetic data (works immediately)
python3 day11_TEST_workflow.py
```

This will:
- Generate realistic synthetic data
- Calculate metrics
- Format Slack message
- Display full report
- Save Slack payload to JSON

**Output:**
- Console report with all metrics
- `day11_sample_slack_payload.json` - Slack message structure
- Execution logs in `logs/day11_orchestration.log`

### Configure and Run for Real

1. **Get a Slack Webhook URL:**
   - Go to https://api.slack.com/messaging/webhooks
   - Create an incoming webhook for your channel
   - Copy the webhook URL

2. **Configure environment variables:**
   ```bash
   # Edit ../config/.env and add:
   DAY11_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. **Test Slack connection:**
   ```bash
   python3 day11_ORCHESTRATOR_main.py test
   ```

4. **Run the report once:**
   ```bash
   python3 day11_ORCHESTRATOR_main.py
   ```

5. **Schedule daily execution:**
   ```bash
   # Option A: Using system cron
   crontab -e
   # Add: 0 8 * * * cd /path/to/day11 && python3 day11_ORCHESTRATOR_main.py

   # Option B: Using Python scheduler (no cron needed)
   python3 day11_SCHEDULER_daemon.py
   ```

---

## 📊 Report Contents

### GA4 Metrics (Website Traffic)
- Total Sessions
- Total Conversions
- Average Bounce Rate
- Top Traffic Source with session count

### Google Ads Metrics (Paid Advertising)
- Total Spend
- Total Conversions
- Cost per Conversion
- Average CPC (Cost per Click)
- Total Clicks & Impressions
- CTR (Click-through Rate)
- Top Performing Campaign

### Alerts & Warnings
- 🔴 Bounce rate > 60%
- 🔴 Conversions < 5
- 🔴 Cost per conversion > $50

---

## 🏗️ Project Structure

```
day11/
├── workflows/
│   └── day11_n8n_workflow_architecture.json  # Workflow documentation
├── logs/
│   └── day11_orchestration.log                # Execution logs
├── screenshots/                                # Evidence (add your own)
├── data/                                       # Temporary data cache
│
├── day11_CONFIG_settings.py                   # Configuration management
├── day11_DATA_fetcher.py                      # Data retrieval with fallbacks
├── day11_FORMATTER_slack.py                   # Slack Block Kit formatter
├── day11_SENDER_slack.py                      # Slack webhook sender
├── day11_ORCHESTRATOR_main.py                 # Main workflow orchestrator
├── day11_SCHEDULER_daemon.py                  # APScheduler for scheduling
├── day11_TEST_workflow.py                     # Test script with synthetic data
│
├── day11_requirements.txt                     # Python dependencies
├── .env.example                               # Environment variable template
└── README.md                                  # This file
```

---

## ⚙️ Configuration

All configuration is in `../config/.env`. Copy from [.env.example](.env.example):

### Required Configuration

```bash
# Slack webhook URL (required)
DAY11_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Optional Configuration

```bash
# Scheduling
DAY11_SCHEDULE_CRON=0 8 * * *      # Daily at 8am UTC
DAY11_TIMEZONE=UTC                  # IANA timezone name
DAY11_RUN_ON_WEEKENDS=false         # Skip weekends?

# Report settings
DAY11_REPORT_DAYS_BACK=7            # Last N days of data

# Data sources (tries in order)
DAY11_USE_BIGQUERY=true             # Try BigQuery first
DAY11_USE_LOCAL_CSV=true            # Fall back to CSV files

# Error handling
DAY11_RETRY_ATTEMPTS=3              # Retry failed operations
DAY11_RETRY_DELAY_SECONDS=10        # Delay between retries
DAY11_ENABLE_ERROR_NOTIFICATIONS=true  # Send errors to Slack

# Logging
DAY11_LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR

# Testing
DAY11_DRY_RUN=false                 # Don't actually send to Slack
DAY11_TEST_MODE=false               # Send test message instead
```

---

## 🔄 Data Source Strategy

The workflow uses a **3-tier fallback strategy**:

### 1. BigQuery (Primary)
Fetches data from BigQuery tables created by Day 01:
- `marketing_data.ga4_sessions`
- `marketing_data.google_ads_campaigns`

**Requirements:**
- `DAY01_GCP_PROJECT_ID` configured
- Google Cloud authentication set up
- BigQuery tables exist with data

### 2. Local CSV (Fallback)
Reads CSV files from Day 01's output directory:
- `../day01/data/processed/ga4_sessions.csv`
- `../day01/data/processed/ads_campaigns.csv`

**Requirements:**
- Day 01 project has been run
- CSV files exist in Day 01 directory

### 3. Synthetic Data (Last Resort)
Generates realistic synthetic data automatically:
- 7 days of GA4 sessions (5 traffic sources)
- 7 days of Google Ads campaigns (4 campaigns)

**Requirements:** None - always works!

---

## 📅 Scheduling Options

### Option 1: System Cron (Recommended for Production)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 8am UTC)
0 8 * * * cd /path/to/advent-automation-2025/day11 && /usr/bin/python3 day11_ORCHESTRATOR_main.py >> /path/to/logs/cron.log 2>&1
```

**Cron Examples:**
```bash
0 8 * * *         # Every day at 8:00 AM UTC
0 8 * * 1-5       # Weekdays only at 8:00 AM
0 9,17 * * *      # Daily at 9:00 AM and 5:00 PM
*/30 9-17 * * 1-5 # Every 30 min, 9am-5pm, weekdays
```

### Option 2: Python APScheduler (No Cron Access Needed)

```bash
# Start the scheduler daemon
python3 day11_SCHEDULER_daemon.py

# Or run immediately, then schedule
python3 day11_SCHEDULER_daemon.py now

# Run in background
nohup python3 day11_SCHEDULER_daemon.py > scheduler.log 2>&1 &
```

### Option 3: Manual Execution

```bash
# Run once
python3 day11_ORCHESTRATOR_main.py

# Test mode (test message only)
python3 day11_ORCHESTRATOR_main.py test

# Dry run (log only, don't send)
python3 day11_ORCHESTRATOR_main.py dry-run
```

---

## 🧪 Testing

### Test 1: Synthetic Data Workflow

```bash
python3 day11_TEST_workflow.py
```

**Expected Output:**
- Generates 35 GA4 rows, 28 Ads rows
- Calculates 18 metrics
- Formats Slack message
- Displays full report
- Creates `day11_sample_slack_payload.json`

### Test 2: Slack Connection

```bash
python3 day11_ORCHESTRATOR_main.py test
```

**Expected Output:**
- Sends test message to Slack
- Verifies webhook URL works
- Logs success/failure

### Test 3: Full Report with Real Data

```bash
# First, ensure Day 01 has been run to generate data
cd ../day01
python3 day01_DATA_extract_ga4.py
python3 day01_DATA_extract_ads.py

# Then run Day 11 report
cd ../day11
python3 day11_ORCHESTRATOR_main.py
```

---

## 📈 Monitoring & Logs

### Log Location

```bash
day11/logs/day11_orchestration.log
```

### What's Logged

- ✅ Execution start/end times
- ✅ Data source used (BigQuery/CSV/Synthetic)
- ✅ Row counts fetched
- ✅ Metrics calculated
- ✅ Slack send status (success/failure)
- ✅ Error messages with context
- ✅ Full text report for audit

### Example Log Output

```
2025-12-11 08:00:00 - INFO - Starting Day 11 Daily Performance Report
2025-12-11 08:00:00 - INFO - Step 1/4: Fetching data from Day 01 sources...
2025-12-11 08:00:01 - INFO - ✓ Data fetched: 35 GA4 rows, 28 Ads rows
2025-12-11 08:00:01 - INFO - Step 2/4: Calculating performance metrics...
2025-12-11 08:00:01 - INFO -   - Total Sessions: 46,387
2025-12-11 08:00:01 - INFO -   - Total Spend: $15,496.16
2025-12-11 08:00:01 - INFO - Step 3/4: Formatting Slack message...
2025-12-11 08:00:01 - INFO - Step 4/4: Sending to Slack...
2025-12-11 08:00:02 - INFO - ✓ Message sent successfully to Slack
2025-12-11 08:00:02 - INFO - ✓ Day 11 Report Completed Successfully
2025-12-11 08:00:02 - INFO - Execution duration: 2.15 seconds
```

---

## 🛠️ Troubleshooting

### Error: "No Slack webhook URL configured"

**Solution:** Set `DAY11_SLACK_WEBHOOK_URL` in `../config/.env`

### Error: "No module named 'google'"

**Expected!** BigQuery client not installed. The workflow will fall back to CSV or synthetic data.

**To fix:** `pip install google-cloud-bigquery google-auth`

### Error: "Failed to send message to Slack"

**Possible causes:**
1. Invalid webhook URL
2. Network connectivity issue
3. Slack workspace restrictions

**Debug steps:**
```bash
# Test webhook manually
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test message"}'

# Run in test mode
python3 day11_ORCHESTRATOR_main.py test
```

### No Data / Empty CSV Files

**Expected** if Day 01 hasn't been run yet. The workflow automatically falls back to synthetic data.

**To use real data:**
```bash
cd ../day01
python3 day01_DATA_extract_ga4.py
python3 day01_DATA_extract_ads.py
```

---

## 🎯 Success Criteria (Orchestration Week)

Based on [ORCHESTRATION_DELIVERY_CRITERIA.md](../common/prompt%20library/ORCHESTRATION_DELIVERY_CRITERIA.md):

### Functional Requirements
- [x] **Scheduling/Triggering:** Daily 8am UTC via cron or APScheduler
- [x] **Idempotency:** Re-running same day produces identical report
- [x] **Error Handling:** Retry logic with exponential backoff
- [x] **Logging:** Structured logs with execution status and timing
- [x] **Monitoring:** Success/failure logged, execution duration tracked
- [x] **Configuration Management:** All secrets in .env, not in code
- [x] **Data Validation:** Handles empty data, validates metrics

### Code Quality
- [x] **Modularity:** Separate modules for fetch, format, send, orchestrate
- [x] **Testability:** Test script works without production systems
- [x] **Documentation:** Inline comments + comprehensive README
- [x] **Dependencies:** Pinned versions in day11_requirements.txt
- [x] **Naming Convention:** All files, functions, variables use `day11_` prefix

### Portfolio Quality
- [x] **Synthetic Data:** Works out-of-box with synthetic data
- [x] **Evidence:** Sample Slack payload JSON, test output, logs
- [x] **Upwork Positioning:** Clear skill demonstration
- [x] **README:** Complete setup and testing instructions

---

## 💼 Upwork Portfolio Positioning

### Project Title
**Automated Daily Retail Performance Reports - n8n Workflow Architecture**

### Skills Demonstrated
- **Low-Code Workflow Orchestration:** n8n-equivalent architecture in Python
- **Marketing Automation:** Automated GA4 + Google Ads reporting
- **Slack Integration:** Rich message formatting with Block Kit
- **Data Pipeline Management:** Multi-source data fetching with fallbacks
- **Production Reliability:** Error handling, retries, logging, idempotency

### Tech Stack
Python 3.11+, pandas, requests, APScheduler, Slack Block Kit API, Google Cloud BigQuery (optional)

### Time to Deliver
3 hours (following orchestration week constraints)

### Business Value
- ✅ Saves 30 minutes daily of manual report generation
- ✅ Ensures stakeholders get consistent updates
- ✅ Reduces human error in metric calculation
- ✅ Provides audit trail for compliance
- ✅ Gracefully handles data source failures

### Applicable Industries
- E-commerce & Retail
- Digital Marketing Agencies
- SaaS Companies
- Performance Marketing Teams
- Any business running paid advertising campaigns

---

## 🔗 Related Projects

- **[Day 01](../day01/):** GA4 + Google Ads data ingestion (data source)
- **Day 12:** Great Expectations data quality (validation layer)
- **Day 13:** Alert triage orchestrator (similar pattern, different domain)

---

## 📖 Architecture & Design Decisions

### Why Python Instead of n8n GUI?

1. **Version Control:** Python code is easier to review and track changes
2. **Testing:** Can test locally without n8n instance
3. **Flexibility:** More control over data transformations
4. **Deployment:** Works anywhere (cron, Docker, cloud functions)
5. **Integration:** Seamlessly connects with Day 01 codebase

### Workflow Pattern: Scheduled Batch Job

```
[Cron/Scheduler] → [Fetch Data] → [Calculate Metrics] → [Format Message] → [Send to Slack] → [Log Results]
                          ↓               ↓                    ↓                 ↓
                    [Error Handler] ← [Retry Logic] ← [Error Notification]
```

### Idempotency Strategy

- Daily reports are naturally idempotent
- Re-running for the same date range produces identical results
- No side effects or state mutations
- Safe to retry on failure

### Error Handling Philosophy

1. **Graceful Degradation:** BigQuery → CSV → Synthetic (always works)
2. **Explicit Logging:** Every step logged for debugging
3. **User Notification:** Errors sent to Slack (if configured)
4. **Retry with Backoff:** Network failures get 3 attempts with exponential delay

---

## 🎓 Learning Outcomes

After implementing this project, you'll understand:

- ✅ How to build reliable workflow orchestration
- ✅ Multi-source data fetching with fallback strategies
- ✅ Slack Block Kit message formatting
- ✅ Cron scheduling vs Python-based scheduling
- ✅ Production error handling patterns
- ✅ Idempotent operation design
- ✅ Audit logging for compliance
- ✅ Code organization for maintainability

---

## 📝 Notes

- **Time to Complete:** ~3 hours (including testing)
- **Cost:** Free (uses synthetic data by default)
- **Python Version:** 3.11+ required
- **Dependencies:** See [day11_requirements.txt](day11_requirements.txt)

---

**Built as part of the Christmas Data Advent Calendar 2025** 🎄
**Orchestration Week - Day 11 - Gleyson (Retail Marketing Automation)**
