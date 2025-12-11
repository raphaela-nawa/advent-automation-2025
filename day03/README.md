# Day 03: GDPR Lead Ingestion Pipeline

> **One-line pitch:** Webhook server that validates GDPR-compliant lead data and automatically calculates retention dates before loading to BigQuery.

**Part of:** [Advent Automation 2025 - 25 Days of Data Engineering](../README.md)

---

## Executive Summary

**Business Problem:** Legal/compliance teams need to ensure marketing leads are collected with proper GDPR consent tracking and automatic data retention date calculations.

**Solution Delivered:** Flask webhook API that validates lead data, calculates GDPR retention dates (30 days without consent, 1 year with consent), and stores in BigQuery with full audit trail.

**Business Impact:** Automated compliance enforcement reduces legal risk and ensures 100% of leads have documented consent status and retention dates.

**For:** Legal/Compliance Team | **Industry:** Legal/Compliance | **Time:** 3 hours | **Status:** ✅ Complete

---

## Overview

This project implements a webhook server that:
- Receives lead data via POST requests
- Validates GDPR-required fields (consent timestamp, purpose)
- Calculates data retention dates based on consent status
- Stores validated leads in Google BigQuery

## Features

- **GDPR Compliance**: Automatic retention date calculation (30 days without consent, 1 year with consent)
- **Validation**: Email format, required fields, consent purpose validation
- **BigQuery Integration**: Automatic dataset/table creation and data insertion
- **Cost-Conscious Design**: Uses batch loading (free tier compatible) instead of streaming inserts
- **REST API**: Simple webhook endpoints for lead submission and statistics
- **Day-Scoped**: All code follows `day03_` naming convention to prevent conflicts

## Architecture Decision: Batch vs. Streaming Inserts

This implementation uses **BigQuery batch loading** (`load_table_from_json`) rather than **streaming inserts** (`insert_rows_json`) for the following reasons:

**Free Tier Compatibility:**
- Streaming inserts require BigQuery paid tier
- Batch loading works on free tier, making this project accessible for development/testing

**Cost Considerations:**
- Streaming: $0.01 per 200MB (billed immediately)
- Batch loading: Free for the first 10GB/day, then $0.05 per GB

**Performance Trade-offs:**
- Streaming: Data available immediately (<1 second)
- Batch: Data available after job completes (2-5 seconds)

**When to Switch to Streaming:**
For production systems requiring real-time analytics or SLA guarantees < 5 seconds, streaming inserts would be preferable. The code can be easily modified in [day03_DATA_load_bigquery.py](day03_DATA_load_bigquery.py) by replacing `load_table_from_json()` with `insert_rows_json()`.

This design choice demonstrates awareness of client budget constraints while maintaining full functionality.

## Quick Start

### 1. Install Dependencies

```bash
cd day03
pip install -r day03_requirements.txt
```

### 2. Configure Environment

The environment variables are already configured in `../config/.env`:

```bash
DAY03_GCP_PROJECT_ID="advent2025-day03"
DAY03_BQ_DATASET="gdpr_leads_dataset"
DAY03_BQ_TABLE="gdpr_leads"
DAY03_WEBHOOK_PORT="5000"
DAY03_GDPR_RETENTION_DAYS="30"
```

### 3. Set Up Google Cloud Authentication

```bash
# Option 1: Use Application Default Credentials
gcloud auth application-default login

# Option 2: Use Service Account (recommended for production)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 4. Start the Webhook Server

```bash
python day03_APP_webhook_server.py
```

Server will start on `http://localhost:5000`

### 5. Test with Sample Data

#### Test Lead WITH Consent:
```bash
curl -X POST http://localhost:5000/leads \
  -H "Content-Type: application/json" \
  -d @data/sample_payloads/lead_with_consent.json
```

Expected response:
```json
{
  "status": "success",
  "message": "Lead processed and stored successfully",
  "lead_id": "uuid-here",
  "consent_given": true,
  "data_retention_date": "2025-11-26"
}
```

#### Test Lead WITHOUT Consent:
```bash
curl -X POST http://localhost:5000/leads \
  -H "Content-Type: application/json" \
  -d @data/sample_payloads/lead_without_consent.json
```

Expected response:
```json
{
  "status": "success",
  "message": "Lead processed and stored successfully",
  "lead_id": "uuid-here",
  "consent_given": false,
  "data_retention_date": "2024-12-26"
}
```

#### Test Newsletter Subscription:
```bash
curl -X POST http://localhost:5000/leads \
  -H "Content-Type: application/json" \
  -d @data/sample_payloads/lead_newsletter.json
```

### 6. View Statistics

```bash
curl http://localhost:5000/leads/stats
```

### 7. Health Check

```bash
curl http://localhost:5000/health
```

## Project Structure

```
day03/
├── data/
│   ├── sample_payloads/
│   │   ├── lead_with_consent.json
│   │   ├── lead_without_consent.json
│   │   └── lead_newsletter.json
│   └── processed/
├── day03_APP_webhook_server.py       # Flask webhook server
├── day03_PIPELINE_gdpr_validator.py  # GDPR validation logic
├── day03_DATA_load_bigquery.py       # BigQuery operations
├── day03_CONFIG_settings.py          # Configuration constants
├── day03_requirements.txt            # Dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## API Endpoints

### POST /leads
Receives and processes a GDPR-compliant lead.

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "consent_given": true,
  "consent_purpose": "marketing_communications",
  "ip_address": "192.168.1.1",
  "timestamp": "2024-11-26T10:30:00Z"
}
```

**Valid Consent Purposes:**
- `marketing_communications`
- `product_updates`
- `newsletter`
- `customer_service`
- `research_surveys`

**Response Codes:**
- `201`: Lead processed successfully
- `400`: Validation error
- `500`: Server error

### GET /leads/stats
Returns statistics about stored leads.

**Response:**
```json
{
  "total_leads": 42,
  "recent_leads": [...],
  "timestamp": "2024-11-26T10:30:00Z"
}
```

### GET /health
Health check endpoint.

## BigQuery Schema

Table: `gdpr_leads`

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| lead_id | STRING | REQUIRED | Unique UUID for the lead |
| name | STRING | REQUIRED | Lead's full name |
| email | STRING | REQUIRED | Lead's email address |
| consent_timestamp | TIMESTAMP | REQUIRED | When consent was recorded |
| consent_purpose | STRING | REQUIRED | Purpose of data collection |
| ip_address | STRING | NULLABLE | IP address of submission |
| data_retention_date | DATE | REQUIRED | When data should be deleted |
| consent_given | BOOLEAN | REQUIRED | Whether consent was given |
| created_at | TIMESTAMP | REQUIRED | When record was created |

## GDPR Retention Logic

- **With Consent**: Data retained for **1 year** (365 days)
- **Without Consent**: Data retained for **30 days** (configurable via `DAY03_GDPR_RETENTION_DAYS`)

## Validation Rules

1. **Required Fields**: name, email, consent_given, consent_purpose, timestamp
2. **Email Format**: Must be valid email (regex validated)
3. **Consent Purpose**: Must be one of the valid purposes listed above
4. **Timestamp Format**: Must be ISO 8601 format (e.g., `2024-11-26T10:30:00Z`)

## Testing BigQuery Connection

```bash
python day03_DATA_load_bigquery.py
```

This will:
- Test BigQuery connection
- Create dataset and table if they don't exist
- Display current lead count

## Query Leads in BigQuery

```sql
-- View all leads
SELECT * FROM `advent2025-day03.gdpr_leads_dataset.gdpr_leads`
ORDER BY created_at DESC
LIMIT 10;

-- Count by consent status
SELECT
  consent_given,
  COUNT(*) as total
FROM `advent2025-day03.gdpr_leads_dataset.gdpr_leads`
GROUP BY consent_given;

-- Find leads approaching retention date
SELECT
  lead_id,
  name,
  email,
  data_retention_date,
  DATE_DIFF(data_retention_date, CURRENT_DATE(), DAY) as days_remaining
FROM `advent2025-day03.gdpr_leads_dataset.gdpr_leads`
WHERE data_retention_date <= DATE_ADD(CURRENT_DATE(), INTERVAL 7 DAY)
ORDER BY data_retention_date;
```

## Common Issues

### Authentication Error
```
Error: Could not automatically determine credentials
```
**Solution**: Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change `DAY03_WEBHOOK_PORT` in `config/.env` or kill the process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

### Invalid JSON
```
Error: Content-Type must be application/json
```
**Solution**: Ensure you're sending `Content-Type: application/json` header and valid JSON body

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| DAY03_GCP_PROJECT_ID | advent2025-day03 | GCP project ID |
| DAY03_BQ_DATASET | gdpr_leads_dataset | BigQuery dataset name |
| DAY03_BQ_TABLE | gdpr_leads | BigQuery table name |
| DAY03_BQ_LOCATION | US | BigQuery dataset location |
| DAY03_GDPR_RETENTION_DAYS | 30 | Days to retain non-consented data |
| DAY03_WEBHOOK_PORT | 5000 | Webhook server port |
| DAY03_WEBHOOK_HOST | 0.0.0.0 | Webhook server host |

## Out of Scope (NOT Implemented)

Following the 3-hour delivery criteria, these features are intentionally not included:
- ❌ Automated data deletion/cleanup jobs
- ❌ Web UI for lead submission
- ❌ Complex email validation beyond regex
- ❌ Dashboard/analytics
- ❌ Scheduling/orchestration
- ❌ Multi-region support

## Next Steps

After validating this ingestion pipeline works, you could:
1. **Day 1D**: Add orchestration with Apache Airflow
2. **Day 1E**: Build a Streamlit dashboard to visualize leads
3. **Day 2A**: Implement automated deletion based on retention dates
4. **Day 2B**: Add email verification service integration

## License

Part of the Advent Calendar 2025 project - Educational purposes only.
