# Day 01: GA4 + Google Ads → BigQuery Pipeline

**Project 1A - Ingestion Pillar**
**Stakeholder:** Daud - Marketing consultant who needs automated GA4 + Google Ads reports for agency clients
**Industry:** Marketing/Advertising

## 📋 Overview

This project extracts marketing data from Google Analytics 4 (GA4) and Google Ads, then loads it into BigQuery for analysis. The pipeline supports both real API data (GA4 Demo Account) and synthetic data generation.

### What This Project Does

1. **Extracts GA4 session data** (sessions, conversions, bounce rate by source)
2. **Generates synthetic Google Ads campaign data** (spend, clicks, impressions, conversions)
3. **Loads both datasets to BigQuery** with properly structured schemas
4. **Provides ready-to-query tables** for marketing analysis

### What This Project Does NOT Do

- ❌ Dashboards or visualizations (that's Pilar D)
- ❌ Scheduling or orchestration (that's Pilar C)
- ❌ Data analysis or insights (that's Pilar E)
- ❌ Complex data modeling (that's Pilar B)

This is a **pure ingestion pipeline** - data in, data out.

---

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Python 3.11+
python --version

# 2. Install dependencies
cd /path/to/advent-automation-2025
pip install -r requirements.txt

# 3. Configure environment variables (see Configuration section)
```

### Run the Pipeline

```bash
# Navigate to day01 folder
cd day01

# Step 1: Extract GA4 data (synthetic by default)
python day01_DATA_extract_ga4.py

# Step 2: Generate Google Ads synthetic data
python day01_DATA_extract_ads.py

# Step 3: Load both datasets to BigQuery
python day01_DATA_load_bigquery.py
```

**That's it!** Your data should now be in BigQuery.

---

## 📊 Data Schema

### Table: `ga4_sessions`

Stores GA4 session metrics by date and traffic source.

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Session date (YYYY-MM-DD) |
| `sessions` | INTEGER | Number of sessions |
| `conversions` | INTEGER | Number of conversions |
| `bounce_rate` | FLOAT | Bounce rate (0.0 to 1.0) |
| `source` | STRING | Traffic source (google, facebook, direct, email, linkedin) |

**Sample Data:**
```
date       | sessions | conversions | bounce_rate | source
-----------|----------|-------------|-------------|----------
2024-11-01 | 1520     | 45          | 0.42        | google
2024-11-01 | 890      | 22          | 0.48        | facebook
2024-11-02 | 1620     | 58          | 0.39        | google
```

### Table: `google_ads_campaigns`

Stores Google Ads campaign performance metrics.

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Campaign date (YYYY-MM-DD) |
| `campaign_name` | STRING | Campaign name |
| `spend` | FLOAT | Daily spend in USD |
| `clicks` | INTEGER | Number of clicks |
| `impressions` | INTEGER | Number of impressions |
| `conversions` | INTEGER | Number of conversions |

**Sample Data:**
```
date       | campaign_name      | spend  | clicks | impressions | conversions
-----------|-------------------|--------|--------|-------------|-------------
2024-11-01 | Brand Campaign    | 450.00 | 320    | 12500       | 18
2024-11-01 | Product Launch    | 680.00 | 510    | 18200       | 25
2024-11-02 | Retargeting       | 320.00 | 245    | 9800        | 15
```

---

## ⚙️ Configuration

### Environment Variables

All configuration is stored in [`../config/.env`](../config/.env). Add these variables:

```bash
# BigQuery Configuration (REQUIRED)
DAY01_GCP_PROJECT_ID="your-gcp-project-id"
DAY01_BQ_DATASET="marketing_data"
DAY01_BQ_LOCATION="US"

# Feature Flags
DAY01_USE_SYNTHETIC_DATA="true"  # Use synthetic data (recommended)
DAY01_SYNTHETIC_DAYS="30"        # Days of historical data
DAY01_NUM_CAMPAIGNS="4"          # Number of ad campaigns

# GA4 Configuration (OPTIONAL - only for real data)
DAY01_GA4_PROPERTY_ID="213025502"  # Google Merchandise Store Demo
DAY01_GA4_CREDENTIALS_PATH="./credentials/ga4_service_account.json"
```

### Google Cloud Authentication

To upload data to BigQuery, authenticate with Google Cloud:

**Option 1: Service Account (Recommended for production)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Option 2: User Account (Quick for testing)**
```bash
gcloud auth application-default login
```

**Get Service Account Credentials:**
1. Go to [GCP Console → IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account with BigQuery Admin role
3. Create a JSON key and download it
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the key path

---

## 📁 Project Structure

```
day01/
├── data/
│   ├── raw/                    # Raw extracted data
│   │   ├── ga4_synthetic.csv   # Generated GA4 data
│   │   └── ads_synthetic.csv   # Generated Ads data
│   └── processed/              # Processed data ready for BigQuery
│       ├── ga4_sessions.csv
│       └── ads_campaigns.csv
│
├── day01_CONFIG_settings.py    # Configuration constants
├── day01_DATA_extract_ga4.py   # GA4 data extractor
├── day01_DATA_extract_ads.py   # Google Ads synthetic generator
├── day01_DATA_load_bigquery.py # BigQuery loader
│
├── day01_requirements.txt      # Project-specific dependencies
├── day01_.env.example          # Environment variable template
└── README.md                   # This file
```

---

## 🔄 Data Sources

### GA4 Data

**Default Mode: Synthetic Data**
- Generates 30 days of realistic session data
- Simulates 5 traffic sources: google, facebook, direct, email, linkedin
- Conversion rate: 2-5% of sessions
- Bounce rate: 35-55%

**Optional: Real GA4 Data**
1. Set `DAY01_USE_SYNTHETIC_DATA="false"` in config/.env
2. Configure GA4 credentials (see [GA4 Setup Guide](#ga4-setup-optional))
3. Uses Google Merchandise Store Demo Account (Property ID: 213025502)

### Google Ads Data

**Always Synthetic** (no free sandbox available)
- Generates data for 4 campaigns: Brand Campaign, Product Launch, Retargeting, Black Friday Special
- Realistic metrics: CTR 2-4%, Conversion Rate 3-8%
- Daily spend: $300-$800 per campaign

---

## 🧪 Testing & Validation

### Verify Data Extraction

After running extraction scripts, check the `data/processed/` folder:

```bash
ls -lh data/processed/
# Should show:
# ga4_sessions.csv
# ads_campaigns.csv

# Preview data
head data/processed/ga4_sessions.csv
head data/processed/ads_campaigns.csv
```

### Verify BigQuery Upload

Run these queries in [BigQuery Console](https://console.cloud.google.com/bigquery):

**Check row counts:**
```sql
-- GA4 Sessions
SELECT COUNT(*) as row_count
FROM `your-project-id.marketing_data.ga4_sessions`;

-- Google Ads Campaigns
SELECT COUNT(*) as row_count
FROM `your-project-id.marketing_data.google_ads_campaigns`;
```

**Sample join query (GA4 + Google Ads):**
```sql
SELECT
  ga4.date,
  ga4.sessions,
  ga4.conversions as ga4_conversions,
  ads.campaign_name,
  ads.spend,
  ads.conversions as ads_conversions,
  ROUND(ads.spend / NULLIF(ads.conversions, 0), 2) as cost_per_conversion
FROM `your-project-id.marketing_data.ga4_sessions` ga4
JOIN `your-project-id.marketing_data.google_ads_campaigns` ads
  ON ga4.date = ads.date
WHERE ga4.source = 'google'
ORDER BY ga4.date DESC
LIMIT 10;
```

---

## 🛠️ Troubleshooting

### Error: "BigQuery project ID not configured"

**Solution:** Set `DAY01_GCP_PROJECT_ID` in `../config/.env`

### Error: "Failed to create BigQuery client"

**Cause:** Missing Google Cloud authentication

**Solution:**
```bash
# Authenticate using gcloud
gcloud auth application-default login

# Or set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Error: "google-cloud-bigquery not installed"

**Solution:**
```bash
pip install google-cloud-bigquery google-analytics-data
```

### Data Not Appearing in BigQuery

1. Check if scripts ran without errors
2. Verify CSV files exist in `data/processed/`
3. Confirm BigQuery dataset was created: `marketing_data`
4. Check GCP Console → BigQuery → Your Project

### GA4 API Not Working

**Expected!** If using synthetic data (default), this is normal. The project pivots to synthetic data automatically.

To use real GA4 data:
1. Set `DAY01_USE_SYNTHETIC_DATA="false"`
2. Configure service account credentials
3. Grant GA4 property access to service account

---

## 📖 GA4 Setup (Optional)

Only follow this if you want to extract **real GA4 data** instead of synthetic.

### Step 1: Get GA4 Service Account Credentials

1. Go to [GCP Console → IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account
3. Create a JSON key and download it
4. Save to `day01/credentials/ga4_service_account.json`

### Step 2: Grant GA4 Access

1. Go to [GA4 Admin Panel](https://analytics.google.com/)
2. Select your property → Admin → Property Access Management
3. Add the service account email (from Step 1)
4. Grant "Viewer" role

### Step 3: Configure Environment

```bash
# In config/.env
DAY01_USE_SYNTHETIC_DATA="false"
DAY01_GA4_PROPERTY_ID="your-property-id"  # Find in GA4 Admin
DAY01_GA4_CREDENTIALS_PATH="./credentials/ga4_service_account.json"
```

### Using GA4 Demo Account

Google provides a demo GA4 property (Google Merchandise Store):
- Property ID: `213025502`
- No credentials needed (if publicly accessible)
- Limited data availability

---

## 🎯 Success Criteria

Before considering this project complete, verify:

- [x] `python day01_DATA_extract_ga4.py` runs without errors
- [x] `python day01_DATA_extract_ads.py` runs without errors
- [x] CSV files exist in `data/processed/`
- [x] `python day01_DATA_load_bigquery.py` runs without errors
- [x] BigQuery tables have data (`SELECT COUNT(*)` > 0)
- [x] Join query works between both tables
- [x] README Quick Start works copy-paste

---

## 📚 Next Steps

This project is **Day 01 - Ingestion only**. Future projects in the advent calendar will add:

- **Day 0X (Pilar B):** Data modeling and transformation
- **Day 0X (Pilar C):** Orchestration and scheduling
- **Day 0X (Pilar D):** Dashboards and visualization
- **Day 0X (Pilar E):** AI-powered insights

For now, your data is ready to query in BigQuery!

---

## 🔗 Resources

- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [GCP Service Accounts](https://cloud.google.com/iam/docs/service-accounts)

---

## 📝 Notes

- **Time to complete:** ~90 minutes (with synthetic data)
- **Cost:** Free tier BigQuery (first 10GB queries/month free)
- **Dependencies:** See [day01_requirements.txt](day01_requirements.txt)
- **Python version:** 3.11+

---

**Built as part of the Christmas Data Advent Calendar 2025** 🎄
