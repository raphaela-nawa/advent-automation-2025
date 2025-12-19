# Day 16: BigQuery Setup Guide

## Overview
This guide helps you upload the Day 6 SaaS metrics data to BigQuery for use with Metabase Cloud.

---

## Step 1: Create BigQuery Dataset

### Using GCP Console:
1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Select your project (or create a new one)
3. Click "Create Dataset"
4. Use these settings:
   - **Dataset ID**: `day16_saas_metrics`
   - **Location**: `US` (or your preferred region)
   - **Default table expiration**: Never
5. Click "Create Dataset"

### Using gcloud CLI:
```bash
# Set your project ID
export DAY16_GCP_PROJECT_ID="your-project-id"

# Create dataset
bq mk \
  --dataset \
  --location=US \
  --description="Day 16: SaaS Health Metrics for Metabase Dashboard" \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics
```

---

## Step 2: Upload CSV Files to BigQuery

You have 8 CSV files in `day16/data/` that need to be uploaded.

### Option A: Using GCP Console (Easiest)

For each CSV file, follow these steps:

1. In BigQuery, select your `day16_saas_metrics` dataset
2. Click "Create Table"
3. Configure:
   - **Source**: Upload
   - **Select file**: Choose the CSV file
   - **File format**: CSV
   - **Table name**: Use the filename without `.csv` (e.g., `day06_dashboard_kpis`)
   - **Schema**: Auto-detect
   - **Advanced options** → Header rows to skip: `1`
4. Click "Create Table"

Repeat for all 8 files:
- `day06_dashboard_kpis.csv`
- `day06_mrr_summary.csv`
- `day06_retention_curves.csv`
- `day06_churn_by_cohort.csv`
- `day06_customer_health.csv`
- `day06_customers.csv`
- `day06_subscriptions.csv`
- `day06_mrr_movements.csv`

### Option B: Using bq CLI (Faster for bulk upload)

```bash
# Navigate to the data directory
cd day16/data

# Set your project ID
export DAY16_GCP_PROJECT_ID="your-project-id"

# Upload all tables
bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_dashboard_kpis \
  day06_dashboard_kpis.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_mrr_summary \
  day06_mrr_summary.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_retention_curves \
  day06_retention_curves.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_churn_by_cohort \
  day06_churn_by_cohort.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_customer_health \
  day06_customer_health.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_customers \
  day06_customers.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_subscriptions \
  day06_subscriptions.csv

bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics.day06_mrr_movements \
  day06_mrr_movements.csv
```

---

## Step 3: Verify Upload

```bash
# List tables
bq ls ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics

# Check row counts
bq query --use_legacy_sql=false \
  "SELECT 'dashboard_kpis' as table_name, COUNT(*) as row_count FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_dashboard_kpis\`
   UNION ALL
   SELECT 'mrr_summary', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_mrr_summary\`
   UNION ALL
   SELECT 'retention_curves', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_retention_curves\`
   UNION ALL
   SELECT 'churn_by_cohort', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_churn_by_cohort\`
   UNION ALL
   SELECT 'customer_health', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_customer_health\`
   UNION ALL
   SELECT 'customers', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_customers\`
   UNION ALL
   SELECT 'subscriptions', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_subscriptions\`
   UNION ALL
   SELECT 'mrr_movements', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_mrr_movements\`"
```

Expected row counts:
- `dashboard_kpis`: 1
- `mrr_summary`: 24
- `retention_curves`: 299
- `churn_by_cohort`: 52
- `customer_health`: 500
- `customers`: 500
- `subscriptions`: 641
- `mrr_movements`: 24

---

## Step 4: Create Service Account for Metabase

Metabase Cloud needs credentials to access your BigQuery data.

### Create Service Account:
```bash
# Set variables
export DAY16_GCP_PROJECT_ID="your-project-id"
export DAY16_SERVICE_ACCOUNT="metabase-day16"

# Create service account
gcloud iam service-accounts create ${DAY16_SERVICE_ACCOUNT} \
  --display-name="Metabase Day 16 Dashboard" \
  --project=${DAY16_GCP_PROJECT_ID}

# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding ${DAY16_GCP_PROJECT_ID} \
  --member="serviceAccount:${DAY16_SERVICE_ACCOUNT}@${DAY16_GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User role (for running queries)
gcloud projects add-iam-policy-binding ${DAY16_GCP_PROJECT_ID} \
  --member="serviceAccount:${DAY16_SERVICE_ACCOUNT}@${DAY16_GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

# Create and download key
gcloud iam service-accounts keys create day16_metabase_key.json \
  --iam-account=${DAY16_SERVICE_ACCOUNT}@${DAY16_GCP_PROJECT_ID}.iam.gserviceaccount.com
```

**Save the `day16_metabase_key.json` file** - you'll need it for Metabase Cloud connection.

---

## Step 5: Connect Metabase Cloud to BigQuery

1. Go to [Metabase Cloud](https://www.metabase.com/start/)
2. Sign up or log in
3. Click "Add a database"
4. Select "BigQuery"
5. Configure:
   - **Display Name**: Day 16 - SaaS Health Metrics
   - **Project ID**: Your GCP project ID
   - **Dataset ID**: `day16_saas_metrics`
   - **Service Account JSON**: Upload `day16_metabase_key.json`
6. Click "Save"
7. Click "Sync database schema now"

---

## Next Steps

Once connected, you're ready to create dashboard cards using the SQL queries in:
- `day16_QUERIES_metabase.md`

---

## Troubleshooting

### "Permission denied" error:
- Verify service account has both `bigquery.dataViewer` and `bigquery.jobUser` roles
- Check that the service account JSON key is valid

### "Dataset not found":
- Ensure dataset ID is exactly `day16_saas_metrics`
- Verify dataset is in the same project as your service account

### "Table not found":
- Run the verification query in Step 3 to confirm all tables uploaded successfully
- Check table names match exactly (case-sensitive)

---

## Cost Considerations

- **Storage**: ~1 MB total (negligible cost)
- **Queries**: Metabase preview queries are typically <10 MB scanned
- **Expected monthly cost**: <$1 USD (likely free tier)

---

## Security Notes

- ⚠️ **DO NOT commit `day16_metabase_key.json` to git**
- Add to `.gitignore`: `*.json` in day16 folder
- Service account has read-only access (dataViewer role only)
- Consider setting up BigQuery authorized views for production

---

Built for Christmas Data Advent 2025 - Day 16 (Project 4A)
