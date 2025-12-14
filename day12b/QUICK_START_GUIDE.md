# GE Cloud Validation - Quick Start Guide

## Running Your First Validation (3 Commands)

### ✅ Already Complete - Your Two Datasets Are Uploaded:
1. `day12_security_events.csv` (1,000 security logs)
2. `day12_compliance_audit.csv` (compliance records)

---

## Run Validation Now (1 Command)

```bash
cd /Users/raphaelanawa/Desktop/advent2025/repo/advent-automation-2025/day12b
python3 day12b_SIMPLIFIED_cloud_validation.py
```

**Expected Output:**
```
✅ Connected to GE Cloud successfully!
✅ Loaded data from day12_security_events.csv
✅ Added 8 expectations to suite
🔍 Running validation...

VALIDATION RESULTS
Overall Success: ❌ FAIL (this is good - catches issues!)
Total Expectations: 8
Passed: 7 ✓
Failed: 1 ✗
Success Rate: 87.50%

⚠️  FAILED EXPECTATIONS:
   ✗ expect_column_values_to_match_regex (username)

📄 Results saved to: logs/validation_results_cloud_*.json
🌐 View in GE Cloud at: https://app.greatexpectations.io
```

---

## What Just Happened?

### The Validation Workflow (5 Steps):

```
1. CONNECT → Connected to your GE Cloud workspace
2. LOAD DATA → Loaded 1,000 security events from CSV
3. CREATE SUITE → Created "day12b_security_validation_suite"
4. ADD EXPECTATIONS → Added 8 validation rules
5. VALIDATE → Checked data against rules → 7 passed, 1 failed
```

### Your 8 Validation Rules:

| # | Expectation | What It Checks | Status |
|---|-------------|----------------|--------|
| 1 | `ExpectTableRowCountToBeBetween` | Has 100-1M records | ✅ PASS |
| 2 | `ExpectColumnValuesToNotBeNull` | Event IDs not null (98%+) | ✅ PASS |
| 3 | `ExpectColumnValuesToNotBeNull` | Timestamps not null (100%) | ✅ PASS |
| 4 | `ExpectColumnValuesToBeInSet` | Severity in allowed values | ✅ PASS |
| 5 | `ExpectColumnValuesToBeInSet` | Action in allowed values | ✅ PASS |
| 6 | `ExpectColumnValuesToBeInSet` | Status in allowed values | ✅ PASS |
| 7 | `ExpectColumnValuesToBeBetween` | Risk score 0-100 | ✅ PASS |
| 8 | `ExpectColumnValuesToMatchRegex` | Usernames anonymized (user_XXXX) | ❌ FAIL |

### Why Did #8 Fail? (This Is Good!)

**Expected:** Usernames should be anonymized like `user_1234`
**Found:** 5.3% of usernames are email addresses (PII leakage!)
**Threshold:** 95% should match the pattern
**Result:** Only 94.7% matched → FAIL

**This proves your validator works!** It caught a real GDPR/HIPAA compliance issue.

---

## View Results in GE Cloud Dashboard

1. Open: **https://app.greatexpectations.io**
2. Navigate to: **"Validation Results"** or **"Data Docs"**
3. Find your validation run (Dec 12, 2025 at 7:13 PM)
4. See:
   - Green checks ✅ for passed expectations
   - Red X ❌ for failed expectations
   - Detailed metrics and historical trends

---

## Key Files & Their Purpose

```
day12b/
├── day12b_SIMPLIFIED_cloud_validation.py  ← Main script (run this!)
│   └─> Connects → Loads data → Creates suite → Validates
│
├── day12b_CONFIG_ge_cloud.py              ← Configuration
│   └─> GE Cloud credentials, data paths, thresholds
│
├── logs/
│   ├── validation_results_cloud_*.json    ← JSON results
│   └── day12b_cloud_validation.log        ← Full logs
│
├── VALIDATION_LOGIC_EXPLAINED.md          ← Deep dive explanation
└── QUICK_START_GUIDE.md                   ← This file
```

---

## The 3 Core Concepts

### 1. Expectation = A Rule About Your Data

```python
# Example: "Event IDs should not be null"
gxe.ExpectColumnValuesToNotBeNull(
    column="event_id",
    mostly=0.98  # Allow 2% to be null
)
```

Think of it like: **"I expect my data to have this property"**

### 2. Expectation Suite = Collection of Rules

```python
suite = gx.ExpectationSuite(name="security_validation_suite")
suite.add_expectation(rule1)
suite.add_expectation(rule2)
suite.add_expectation(rule3)
```

Think of it like: **A "test suite" for data quality**

### 3. Validation = Checking Data Against Rules

```python
results = batch.validate(suite)
# Returns: {success: False, statistics: {evaluated: 8, successful: 7, ...}}
```

Think of it like: **Running pytest on your data**

---

## Common Commands

### Run validation:
```bash
python3 day12b_SIMPLIFIED_cloud_validation.py
```

### Check exit code (for CI/CD):
```bash
python3 day12b_SIMPLIFIED_cloud_validation.py
echo $?  # 0=pass, 1=fail, 2=error
```

### View logs:
```bash
tail -f logs/day12b_cloud_validation.log
```

### View JSON results:
```bash
cat logs/validation_results_cloud_*.json | jq .
```

---

## Next Steps

### 1. Validate Your Second Dataset (Compliance Audit)

Edit [day12b_SIMPLIFIED_cloud_validation.py](day12b_SIMPLIFIED_cloud_validation.py):

```python
# Change line 58-60 from:
batch = context.data_sources.pandas_default.read_csv(
    str(DAY12B_SECURITY_EVENTS_PATH)  # Currently: security_events.csv
)

# To:
batch = context.data_sources.pandas_default.read_csv(
    str(DAY12B_COMPLIANCE_AUDIT_PATH)  # Switch to: compliance_audit.csv
)
```

Then run: `python3 day12b_SIMPLIFIED_cloud_validation.py`

### 2. Add More Expectations

Common cybersecurity expectations:

```python
# Detect SQL injection attempts
suite.add_expectation(
    gxe.ExpectColumnValuesToNotMatchRegex(
        column="user_input",
        regex=r"(SELECT|INSERT|UPDATE|DELETE|DROP|EXEC|UNION)",
        mostly=1.0
    )
)

# Ensure IP addresses are valid format
suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="source_ip",
        regex=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
        mostly=0.99
    )
)

# Check timestamp recency (no events older than 90 days)
suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(
        column="timestamp",
        min_value=datetime.now() - timedelta(days=90),
        max_value=datetime.now()
    )
)
```

### 3. Set Up Automation

**GitHub Actions CI/CD:**
```yaml
- name: Data Quality Gate
  run: |
    python3 day12b/day12b_SIMPLIFIED_cloud_validation.py
    if [ $? -ne 0 ]; then
      echo "❌ Data quality failed - blocking deployment"
      exit 1
    fi
```

**Airflow DAG:**
```python
validate_task = PythonOperator(
    task_id='validate_security_logs',
    python_callable=day12b_run_simplified_validation
)
```

### 4. Explore GE Cloud Features

In the GE Cloud UI (https://app.greatexpectations.io):
- 📊 View Data Docs (interactive validation results)
- 📈 See historical trends (validation success rate over time)
- 🔔 Set up alerts (Slack/email notifications on failures)
- 👥 Invite team members (collaborative data quality)
- ⏰ Schedule validations (run automatically daily/hourly)

---

## Troubleshooting

### "Connection refused" or "Authentication failed"
**Fix:** Check credentials in `config/.env`:
```bash
DAY12B_GE_CLOUD_ORG_ID=1e917a7d-d773-4453-b934-e0560408b0ff
DAY12B_GE_CLOUD_ACCESS_TOKEN=your-access-token-here
```

### "File not found" error
**Fix:** Ensure data file exists:
```bash
ls -la ../day12/data/day12_security_events.csv
```

### Want to run Day 12A (custom framework) for comparison?
```bash
cd ../day12
python3 day12_ORCHESTRATOR_main.py
```

---

## Success Criteria

You know validation is working when:
- ✅ Script connects to GE Cloud (no authentication errors)
- ✅ Data loads successfully (shows row count)
- ✅ All 8 expectations are created
- ✅ Validation runs and returns results
- ✅ Results saved to `logs/` directory
- ✅ You can view results in GE Cloud dashboard
- ✅ Exit code reflects validation status (0 or 1, not 2)

**Your current status:** ✅ ALL CRITERIA MET!

---

## Key Takeaways

1. **GE Cloud validation is a 5-step workflow:**
   Connect → Load → Suite → Expectations → Validate

2. **Expectations are declarative:**
   You say WHAT you expect, GE figures out HOW to check it

3. **The `mostly` parameter is critical:**
   Real-world data is messy - set realistic thresholds (95-99%, not 100%)

4. **Failed validations are good:**
   They prove your validator catches real issues!

5. **Results are stored in GE Cloud:**
   Historical tracking, team collaboration, trend analysis

6. **Exit codes enable automation:**
   0=pass (deploy), 1=fail (block), 2=error (investigate)

---

**📚 For Deep Dive:** See [VALIDATION_LOGIC_EXPLAINED.md](VALIDATION_LOGIC_EXPLAINED.md)

**📖 For Setup:** See [README_12B.md](README_12B.md)

**🌐 GE Cloud Dashboard:** https://app.greatexpectations.io
