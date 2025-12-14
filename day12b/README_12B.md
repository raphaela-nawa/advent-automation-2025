# Day 12B: Great Expectations Cloud Integration

> **Enterprise data quality validation using GE Cloud for cybersecurity logs**

**Part of:** [Day 12: Cybersecurity Data Quality Framework](../day12/README.md)

---

## Overview

Day 12B demonstrates **production-ready integration with Great Expectations Cloud**, the enterprise SaaS platform for data quality validation. This implementation uses native GE expectations, cloud-hosted Data Docs, and team collaboration features.

### Why Day 12B?

While [Day 12A](../day12/) shows you can build GE-style validation from scratch, **Day 12B proves you can use the actual enterprise tool properly**. This is important for:
- Hiring managers wanting GE Cloud experience
- Teams already using GE Cloud
- Production deployments requiring managed infrastructure
- Multi-user collaboration needs

---

## Key Differences from Day 12A

| Feature | Day 12A (Custom) | Day 12B (GE Cloud) |
|---------|------------------|-------------------|
| **Setup** | No external account | Requires GE Cloud account |
| **Data Docs** | Local HTML files | Cloud-hosted dashboard |
| **Expectations** | Custom Python classes | Native GE expectations |
| **Collaboration** | Single developer | Multi-user with permissions |
| **Versioning** | Git only | GE Cloud + Git |
| **Monitoring** | Custom logging | GE Cloud monitoring UI |
| **Deployment** | Self-hosted | Managed cloud service |

---

## Quick Start

### Prerequisites

1. **Great Expectations Cloud Account**
   - Sign up at https://greatexpectations.io/cloud
   - Free tier available for testing
   - Note your Organization ID and create an Access Token

2. **Python Environment**
   ```bash
   python3 --version  # 3.11+ recommended
   pip install -r day12b_requirements.txt
   ```

### Setup (15 minutes)

**Step 1: Configure GE Cloud Credentials**

```bash
# Copy environment template
cp day12b/.env.example ../config/.env

# Edit config/.env and add your credentials:
DAY12B_GE_CLOUD_ORG_ID=your-org-id-here
DAY12B_GE_CLOUD_ACCESS_TOKEN=your-access-token-here
```

**Getting your GE Cloud credentials:**
1. Login to https://app.greatexpectations.io
2. Navigate to **Settings → Access Tokens**
3. Click **"Create Token"** with **"Data Context"** permissions
4. Copy your **Organization ID** from the URL or Settings
5. Paste both values into `config/.env`

**Step 2: Initialize GE Cloud Connection**

```bash
cd day12b
python3 day12b_SETUP_cloud.py
```

Expected output:
```
================================================================================
DAY 12B - CONNECTING TO GREAT EXPECTATIONS CLOUD
================================================================================
📡 Connecting to GE Cloud (Org: abc123...)
✅ Successfully connected to GE Cloud!

📊 Setting up Cloud Datasource...
✅ Created datasource: day12b_security_logs_cloud
✅ Added data asset: security_events
📊 Loaded 1000 records from day12_security_events.csv

🔍 Verifying GE Cloud Setup...
✅ Found 1 datasource(s):
   - day12b_security_logs_cloud
✅ GE Cloud setup verified successfully!

================================================================================
SETUP COMPLETE
================================================================================
Next steps:
1. Run: python3 day12b_CREATE_expectations.py
2. View Data Docs at: https://app.greatexpectations.io
================================================================================
```

**Step 3: Create Expectation Suite**

```bash
python3 day12b_CREATE_expectations.py
```

This creates **8 native GE expectations**:
- `expect_table_row_count_to_be_between` - Reasonable event count
- `expect_table_columns_to_match_set` - Required columns present
- `expect_column_values_to_not_be_null` - Completeness checks
- `expect_column_values_to_be_in_set` - Categorical validation
- `expect_column_values_to_be_between` - Risk score bounds
- `expect_column_values_to_match_regex` - PII anonymization check
- `expect_column_values_to_be_of_type` - Type validation

**Step 4: Run Validation**

```bash
python3 day12b_RUN_validation_cloud.py
echo $?  # Check exit code: 0=pass, 1=fail, 2=error
```

**Step 5: View Results in GE Cloud**

1. Open https://app.greatexpectations.io
2. Navigate to **Data Docs**
3. View validation results with interactive UI
4. Share reports with team members

---

## GE Cloud Features Demonstrated

### 1. Cloud-Hosted Data Docs
Unlike Day 12A's local HTML, GE Cloud provides:
- Always up-to-date validation results
- Shareable URLs for stakeholders
- Historical validation trends
- Team collaboration features

### 2. Native GE Expectations
Uses official GE expectations instead of custom code:
```python
# Day 12A (custom)
validator.expect_column_values_to_not_be_null('event_id', threshold=0.02)

# Day 12B (native GE)
validator.expect_column_values_to_not_be_null(
    column="event_id",
    mostly=0.98,  # GE's parameter name
    meta={"severity": "critical"}
)
```

### 3. Checkpoint Management
GE Cloud checkpoints enable:
- Scheduled validation runs
- Multiple data sources in one checkpoint
- Action-based workflows (notify on failure)
- Version-controlled validation suites

### 4. API-First Design
All operations available via API for automation:
- Create/update expectations programmatically
- Trigger validations from CI/CD
- Query validation history
- Export results to external systems

---

## File Structure

```
day12b/
├── day12b_CONFIG_ge_cloud.py         # GE Cloud connection config
├── day12b_SETUP_cloud.py             # Initialize GE Cloud datasource
├── day12b_CREATE_expectations.py     # Build native GE expectation suite
├── day12b_RUN_validation_cloud.py    # Run validation via Cloud
├── day12b_requirements.txt           # Dependencies (GE Cloud SDK)
├── .env.example                      # Configuration template
├── logs/                             # Local execution logs
│   └── validation_results_cloud_*.json
└── README_12B.md                     # This file
```

**Note:** Reuses synthetic data from [Day 12A](../day12/data/) - no need to regenerate.

---

## Validation Results

Same synthetic data as Day 12A, but results viewed in GE Cloud UI:

**Expected Outcome:**
- **Status:** ❌ FAIL (intentional - data has quality issues)
- **Success Rate:** ~85-90%
- **Failed Checks:**
  - Username regex (PII detection) - 5.3% contain email addresses
  - Null event IDs - 1.4% missing

**Why Failures are Expected:**
The synthetic data includes intentional quality issues to demonstrate the validator catches real problems. In production, you'd:
1. Fix data source issues
2. Adjust thresholds based on acceptable limits
3. Set up alerts for critical failures

---

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Data Quality Validation

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r day12b/day12b_requirements.txt

      - name: Run GE Cloud Validation
        env:
          DAY12B_GE_CLOUD_ORG_ID: ${{ secrets.GE_CLOUD_ORG_ID }}
          DAY12B_GE_CLOUD_ACCESS_TOKEN: ${{ secrets.GE_CLOUD_ACCESS_TOKEN }}
        run: |
          cd day12b
          python3 day12b_RUN_validation_cloud.py
```

### Python Script Integration

```python
from day12b.day12b_SETUP_cloud import day12b_get_cloud_context
from day12b.day12b_RUN_validation_cloud import day12b_run_validation

# Connect to GE Cloud
context = day12b_get_cloud_context()

# Run validation
results = day12b_run_validation(context)

# Check results
if results.success:
    print("✅ Data quality checks passed")
else:
    print("❌ Data quality issues detected")
    # Block pipeline, send alert, etc.
```

### Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def run_ge_cloud_validation():
    from day12b.day12b_RUN_validation_cloud import day12b_run_cloud_validation
    exit_code = day12b_run_cloud_validation()
    if exit_code != 0:
        raise ValueError("Data quality validation failed")

dag = DAG(
    'security_data_quality',
    start_date=datetime(2025, 1, 1),
    schedule_interval='0 6 * * *'  # Daily 6 AM
)

validate_task = PythonOperator(
    task_id='validate_security_logs',
    python_callable=run_ge_cloud_validation,
    dag=dag
)
```

---

## Comparison: When to Use Which

### Use Day 12A (Custom Framework) When:
- ✅ Learning GE concepts without Cloud account
- ✅ Air-gapped/offline environments
- ✅ Dependency issues prevent GE installation
- ✅ Need ultra-lightweight validation
- ✅ Want full control over implementation

### Use Day 12B (GE Cloud) When:
- ✅ Production enterprise deployment
- ✅ Team collaboration required
- ✅ Want managed Data Docs hosting
- ✅ Need historical validation trends
- ✅ Integrating with existing GE Cloud setup
- ✅ Want official GE support

### Use Both When:
- ✅ **Portfolio projects** (shows versatility)
- ✅ **Migration scenarios** (Day 12A → Day 12B)
- ✅ **Hybrid deployments** (some teams use Cloud, others don't)

---

## Troubleshooting

### "Could not connect to GE Cloud"

**Check:**
1. Credentials in `config/.env` are correct
2. Access token has "Data Context" permissions
3. Organization ID matches your GE Cloud account
4. Network allows HTTPS to `app.greatexpectations.io`

**Test connection:**
```python
import great_expectations as gx
context = gx.get_context(
    mode="cloud",
    cloud_organization_id="your-org-id",
    cloud_access_token="your-token"
)
print(context.list_datasources())  # Should not error
```

### "Datasource already exists"

**Solution:** The setup script handles this automatically. If you want to recreate:
```python
context = day12b_get_cloud_context()
context.delete_datasource("day12b_security_logs_cloud")
# Then re-run day12b_SETUP_cloud.py
```

### "Validation results show 0%"

**Check:**
1. Data file exists at `../day12/data/day12_security_events.csv`
2. Run Day 12A data generator first: `cd ../day12 && python3 day12_GENERATOR_synthetic_data.py`
3. Verify data loaded: `context.list_datasources()` should show assets

---

## Next Steps

### For Learning:
1. Explore GE Cloud UI at https://app.greatexpectations.io
2. Modify expectations in `day12b_CREATE_expectations.py`
3. Try different data sources (SQL, S3, Snowflake)
4. Set up Slack/email notifications

### For Production:
1. Replace synthetic data with real security logs
2. Calibrate thresholds based on production patterns
3. Set up scheduled checkpoints in GE Cloud
4. Configure action-based workflows (alert on failure)
5. Enable team access and permissions

### For Portfolio:
1. Take screenshots of GE Cloud Data Docs
2. Record video walkthrough of validation process
3. Write blog post comparing Day 12A vs 12B
4. Add to resume: "Great Expectations Cloud - Enterprise data quality platform"

---

## Resources

- **GE Cloud Docs:** https://docs.greatexpectations.io/docs/cloud
- **GE Cloud Dashboard:** https://app.greatexpectations.io
- **Day 12A (Custom Framework):** [../day12/README.md](../day12/README.md)
- **Main Project:** [Advent Automation 2025](../README.md)

---

**Created:** December 12, 2025
**Version:** 1.0
**Status:** ✅ Ready for GE Cloud Setup
