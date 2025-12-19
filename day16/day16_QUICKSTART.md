# Day 16: Quick Start Guide - Metabase Cloud Dashboard

**Goal:** Get your SaaS Health Metrics Dashboard running in 15 minutes.

---

## 📋 Prerequisites

- [ ] Google Cloud Platform account ([Free Tier](https://cloud.google.com/free))
- [ ] Metabase Cloud account ([Free Tier](https://www.metabase.com/start/))
- [ ] `gcloud` CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
- [ ] `bq` CLI installed (included with gcloud)

---

## ⚡ 15-Minute Setup

### Step 1: Export Data (2 minutes)

```bash
cd day16

# Export Day 6 data to CSV
python3 day16_DATA_export_to_csv.py
python3 day16_DATA_generate_retention_curves.py

# Verify CSV files created
ls -l data/*.csv
# Expected: 8 CSV files
```

---

### Step 2: Create BigQuery Dataset (2 minutes)

```bash
# Set your GCP project ID
export DAY16_GCP_PROJECT_ID="your-project-id-here"

# Create dataset
bq mk \
  --dataset \
  --location=US \
  --description="Day 16: SaaS Health Metrics" \
  ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics

# Verify
bq ls --project_id=${DAY16_GCP_PROJECT_ID}
```

---

### Step 3: Upload CSV Files to BigQuery (5 minutes)

**Option A: GCP Console (Easiest for beginners)**

1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Select your project
3. Click on `day16_saas_metrics` dataset
4. For each CSV file in `day16/data/`:
   - Click "Create Table"
   - Source: Upload → Select CSV file
   - Table name: filename without `.csv`
   - Schema: Auto-detect ✅
   - Header rows to skip: 1
   - Click "Create Table"

Repeat for all 8 files:
- `day06_dashboard_kpis.csv`
- `day06_mrr_summary.csv`
- `day06_retention_curves.csv`
- `day06_churn_by_cohort.csv`
- `day06_customer_health.csv`
- `day06_customers.csv`
- `day06_subscriptions.csv`
- `day06_mrr_movements.csv`

**Option B: bq CLI (Faster for experienced users)**

```bash
cd data

# Upload all 8 tables
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

cd ..
```

**Verify Upload:**
```bash
bq ls ${DAY16_GCP_PROJECT_ID}:day16_saas_metrics

# Check row counts
bq query --use_legacy_sql=false \
  "SELECT
    'dashboard_kpis' as table_name, COUNT(*) as rows FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_dashboard_kpis\`
   UNION ALL SELECT 'mrr_summary', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_mrr_summary\`
   UNION ALL SELECT 'retention_curves', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_retention_curves\`
   UNION ALL SELECT 'churn_by_cohort', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_churn_by_cohort\`
   UNION ALL SELECT 'customer_health', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_customer_health\`
   UNION ALL SELECT 'customers', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_customers\`
   UNION ALL SELECT 'subscriptions', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_subscriptions\`
   UNION ALL SELECT 'mrr_movements', COUNT(*) FROM \`${DAY16_GCP_PROJECT_ID}.day16_saas_metrics.day06_mrr_movements\`"
```

**Expected Output:**
```
| table_name       | rows |
|------------------|------|
| dashboard_kpis   | 1    |
| mrr_summary      | 24   |
| retention_curves | 299  |
| churn_by_cohort  | 52   |
| customer_health  | 500  |
| customers        | 500  |
| subscriptions    | 641  |
| mrr_movements    | 24   |
```

---

### Step 4: Create Service Account for Metabase (3 minutes)

```bash
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

echo "✅ Service account key saved to: day16_metabase_key.json"
echo "⚠️  DO NOT COMMIT THIS FILE TO GIT"
```

---

### Step 5: Connect Metabase Cloud to BigQuery (3 minutes)

1. Go to [Metabase Cloud](https://www.metabase.com/start/) and sign up/log in
2. Click "Add a database" (or Settings → Databases → Add database)
3. Select **"BigQuery"**
4. Configure:
   - **Display Name:** `Day 16 - SaaS Health Metrics`
   - **Project ID:** Your GCP project ID (from `$DAY16_GCP_PROJECT_ID`)
   - **Dataset ID:** `day16_saas_metrics`
   - **Service Account JSON:** Click "Upload" and select `day16_metabase_key.json`
5. Click **"Save"**
6. Click **"Sync database schema now"**
7. Wait ~30 seconds for sync to complete

**Verification:**
- Go to "Browse Data" → "Day 16 - SaaS Health Metrics"
- You should see 8 tables listed

---

## 🎨 Creating Dashboard Cards

Now follow the SQL queries in [day16_QUERIES_metabase.md](day16_QUERIES_metabase.md) to create your 6 dashboard cards.

### Quick Card Creation Workflow:

1. In Metabase, click **"New" → "Question"**
2. Select **"Native query"** (raw SQL)
3. Select database: **"Day 16 - SaaS Health Metrics"**
4. Copy/paste SQL from `day16_QUERIES_metabase.md`
5. **Important:** Replace `PROJECT_ID` with your actual GCP project ID
6. Click **"Run"** to test query
7. Click **"Visualize"** and select chart type (as specified in query doc)
8. Click **"Save"** and add to dashboard

### Card Creation Order (30-40 minutes total):

**Section 1: Business Health Baseline (10 min)**
- Card 1.1: Current MRR (Metric)
- Card 1.2: Churn Rate (Metric)
- Card 1.3: Active Customers (Metric)
- Card 1.4: LTV/CAC Ratio (Metric)

**Section 2: Growth Trajectory (10 min)**
- Card 2.1: MRR Growth Over Time (Stacked Area Chart)
- Card 2.2: Month-over-Month Growth Rate (Line Chart)

**Section 3: Cohort Patterns - PRIMARY (10 min)**
- Card 3.1: **Cohort Retention Curves** (Line Chart - Multi-series) ⭐
- Card 3.2: Churn Heatmap (Pivot Table)

**Section 4: Customer Health Alerts (10 min)**
- Card 4.1: At-Risk Customer Distribution (Pie Chart)
- Card 4.2: Top 10 Critical Customers (Table)

---

## 📸 Take Screenshots

Once dashboard is complete:

1. **Full dashboard view:** Screenshot entire dashboard → save as `screenshots/day16_full_dashboard.png`
2. **Individual cards:** Screenshot each of 6 cards → save as `screenshots/day16_card_N_*.png`

---

## ✅ Completion Checklist

- [ ] 8 CSV files exported from Day 6 data
- [ ] BigQuery dataset `day16_saas_metrics` created
- [ ] 8 tables uploaded to BigQuery (verified row counts match expected)
- [ ] Service account created with correct permissions
- [ ] Metabase Cloud connected to BigQuery
- [ ] 6 dashboard cards created (all 4 sections covered)
- [ ] Cohort retention curves display correctly (PRIMARY visual)
- [ ] Dashboard loads in <5 seconds
- [ ] Screenshots captured
- [ ] README.md reviewed and decision context understood

---

## 🆘 Troubleshooting

### "Permission denied" when querying BigQuery
**Fix:** Verify service account has BOTH roles:
```bash
gcloud projects get-iam-policy ${DAY16_GCP_PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:${DAY16_SERVICE_ACCOUNT}@${DAY16_GCP_PROJECT_ID}.iam.gserviceaccount.com"
```
Should show:
- `roles/bigquery.dataViewer`
- `roles/bigquery.jobUser`

### "Table not found" in Metabase
**Fix:** Sync database schema:
1. Settings → Databases → Day 16 - SaaS Health Metrics
2. Click "Sync database schema now"
3. Wait 30 seconds and retry

### "Invalid JSON" when uploading service account key
**Fix:** Ensure you're uploading the `.json` file (not copy/pasting content)

### Retention curves show flat 100% line
**Fix:** Check if `day06_retention_curves.csv` has data:
```bash
wc -l day16/data/day06_retention_curves.csv
# Should show 300 lines (299 data + 1 header)
```
If 1 line (header only), re-run:
```bash
python3 day16_DATA_generate_retention_curves.py
```

---

## 📚 Next Steps

1. **Review decision context:** Read [README.md Decision Context section](README.md#decision-context-critical-section)
2. **Understand PRIMARY visual:** Why cohort retention curves were chosen over alternatives
3. **Test queries:** Run SQL queries manually in BigQuery console to understand data
4. **Customize for real data:** Follow [Detailed Adaptation Guide](README.md#detailed-adaptation-guide)

---

## 💰 Cost Estimate

- **BigQuery Storage:** <1 MB = **$0.00/month** (free tier: 10 GB)
- **BigQuery Queries:** <10 MB scanned per query × 50 queries/day = **$0.00/month** (free tier: 1 TB)
- **Metabase Cloud:** Free tier (3 users, unlimited dashboards)
- **Total:** **$0/month** for this portfolio project

---

## 🎯 Success Criteria

Your dashboard is complete when:

1. ✅ You can identify "declining retention cohorts" in <10 seconds from dashboard
2. ✅ Cohort retention curves show realistic patterns (start 100%, decline to 40-60%)
3. ✅ MRR waterfall balances correctly (New + Exp - Cont - Churn = Net)
4. ✅ You can explain WHY cohort retention curves were chosen (decision-first thinking)
5. ✅ Dashboard loads in <5 seconds

---

**Questions?** Review [day16_CONFIG_bigquery_setup.md](day16_CONFIG_bigquery_setup.md) for detailed troubleshooting.

**Ready to build?** Start with Step 1 above! ⬆️
