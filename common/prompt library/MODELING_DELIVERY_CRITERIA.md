# Delivery Criteria - Modeling Projects (Days 6-10)

## 📋 DECISION MATRIX

### ✅ MANDATORY OUTPUT (You MUST deliver this)

| Item | Description | Location |
|------|-------------|----------|
| **SQL model files** | `.sql` files with documented logic and business rules | `/dayXX/models/` or `/dayXX/sql/` |
| **Data model documentation** | ERD diagram or schema description | `/dayXX/docs/` or in README |
| **Sample queries** | Queries demonstrating the model in action | `/dayXX/queries/` or in README |
| **Reproducible config** | `.env.example` with day-specific variables | `/dayXX/.env.example` |
| **Dependencies** | Day-specific requirements (if needed) | `/dayXX/dayXX_requirements.txt` |
| **Minimal documentation** | README with Quick Start | `/dayXX/README.md` |

### ❌ FORBIDDEN OUTPUT (DON'T do this - will exceed 3h)

| Item | Why NOT |
|------|---------|
| **Dashboards/visualizations** | That's Pilar D (Dashboard) |
| **Orchestration/scheduling** | That's Pilar C (Orchestration) |
| **AI insights/predictions** | That's Pilar E (AI Insights) |
| **Data ingestion** | That's Pilar A (Ingestion) - assume data is already available |
| **Complex testing frameworks** | Only basic validation (< 30 min) |
| **Premature optimization** | Performance comes later, functionality first |
| **UI/Frontend** | CLI or SQL scripts only |

---

## ✅ COMPLETE PROJECT CHECKLIST

### **BEFORE considering the project complete, verify:**

#### **1. Core Functionality**
- [ ] SQL models execute without errors
- [ ] Results match expected business logic
- [ ] Data model is documented (ERD or written description)

#### **2. Reproducibility** (following PROMPT_project_setup.md rules)
- [ ] `.env.example` lists ALL necessary variables (format: `DAYXX_DB_PATH`, `DAYXX_SPECIFIC_VAR`)
- [ ] Variables added to root `config/.env` following existing convention
- [ ] `dayXX_requirements.txt` has specific dependencies (if needed)
- [ ] README has "Quick Start" section that works copy-paste

#### **3. Minimum Quality**
- [ ] Code has docstrings explaining business logic
- [ ] Basic error handling (try/except where needed)
- [ ] Informative logs (print or logging showing progress)

#### **4. Naming Convention (CRITICAL)**
- [ ] All files have `dayXX_` prefix
- [ ] Global variables have `dayXX_` or `DAYXX_` prefix
- [ ] Classes have `dayXX_` prefix
- [ ] Main functions have `dayXX_` prefix

#### **5. Delivery**
- [ ] Git commit with descriptive message
- [ ] Push to GitHub

#### **6. Final Test (5 minutes)**
- [ ] Clone repo in another folder
- [ ] Run commands from README
- [ ] Works? ✅ Project complete. Doesn't work? ❌ Debug and fix.

---

## ⏱️ TIME MANAGEMENT (3 hours)

### **Ideal Distribution:**

| Phase | Time | What to Do |
|-------|------|------------|
| **Setup** | 15 min | Check to see if corresponding folder exists. If not, create dayXX/ folder, set up database/dbt, configure .env |
| **Model Development** | 120 min | Write SQL, test, iterate on business logic |
| **Documentation** | 30 min | README, comments, ERD (if applicable) |
| **Testing** | 15 min | Run queries, validate results |

### **🚨 SIGNS YOU'RE DEVIATING FROM SCOPE:**

- You're building dashboards
- You're writing complex data validation frameworks
- You're doing exploratory data analysis
- You're optimizing performance before functionality works
- You're adding "cool features" not requested

**If this happens:** STOP. Return to requirements. Deliver the promised minimum first.

---

## 🎯 PROJECT-SPECIFIC CRITERIA

### **Day 6 (Zé/Gui - Financial Consulting Metrics Layer)**

**Data Sources:**
- Synthetic data (projects, timesheets, expenses tables)

**Mandatory Output:**
- [ ] SQLite database with 3 tables: `dayXX_projects`, `dayXX_timesheets`, `dayXX_expenses`
- [ ] SQL file with key metrics:
  - **Utilization Rate**: % billable hours vs. total hours
  - **Project Profitability**: Revenue - Costs per project
  - **Client ROI**: Value delivered vs. client investment
  - **Burn Rate**: Spending vs. billing rate
- [ ] Looker Studio connection prepared (or mockup)
- [ ] README explaining each metric

**When to Stop:**
- ✅ 4+ metrics calculated with CTEs
- ✅ At least 2 window functions used (RANK, LAG, or similar)
- ✅ Each metric has comments explaining the calculation
- ✅ README explains "How Zé/Gui uses this to report to clients"
- ❌ DON'T do: Build actual Looker Studio dashboard, multi-currency handling, forecasting

**Expected Files:**
```
dayXX/
├── data/
│   └── dayXX_consulting.db (SQLite)
├── models/
│   └── dayXX_MODEL_metrics.sql
├── dayXX_DATA_synthetic_generator.py
├── dayXX_CONFIG_settings.py
├── dayXX_requirements.txt (if needed)
├── .env.example
└── README.md
```

**Final Validation:**
```sql
-- Run these queries to validate
SELECT * FROM dayXX_utilization_rate;
SELECT * FROM dayXX_project_profitability;
-- Should return results with no errors
```

**Naming Examples:**
```python
# ✅ CORRECT
DAYXX_DB_PATH = "data/dayXX_consulting.db"
DAYXX_BILLABLE_RATE = 150.0

class dayXX_MetricsCalculator:
    pass

def dayXX_calculate_utilization():
    pass

# ❌ WRONG - Generic names cause conflicts
DB_PATH = "data/database.db"  # Could conflict with Day 02
class MetricsCalculator:  # Too generic
```

---

### **Day 7 (Carol - Hospitality LTV & Cohort Model)**

**Data Sources:**
- Synthetic guest/booking data (pousada in Campos do Jordão)

**Mandatory Output:**
- [ ] SQLite database with `dayXX_guests`, `dayXX_bookings`, `dayXX_stays`
- [ ] Cohort table: Guests grouped by month of first reservation
- [ ] LTV by cohort (how much each cohort has spent to date)
- [ ] Retention matrix (% returning after 1, 3, 6, 12 months)
- [ ] Documented SQL queries
- [ ] Simple visualization prep (CSV or Looker Studio connection)

**When to Stop:**
- ✅ Cohort table with at least 12 months of data
- ✅ LTV calculated with window function (SUM OVER)
- ✅ Retention matrix with at least 3 periods (1M, 3M, 6M)
- ✅ README explains "How Carol uses this for retention strategy"
- ✅ Obvious insights in data (e.g., "January cohort has 30% higher LTV")
- ❌ DON'T do: Churn prediction, real booking system integration, advanced segmentation

**Expected Files:**
```
dayXX/
├── data/
│   └── dayXX_hospitality.db
├── models/
│   ├── dayXX_MODEL_cohorts.sql
│   └── dayXX_MODEL_ltv.sql
├── dayXX_DATA_synthetic_guests.py
├── dayXX_CONFIG_settings.py
├── .env.example
└── README.md
```

**Naming Examples:**
```sql
-- ✅ CORRECT
CREATE TABLE dayXX_guest_cohorts AS ...
CREATE VIEW dayXX_ltv_analysis AS ...

-- ❌ WRONG
CREATE TABLE guest_cohorts AS ...  -- Too generic
```

**Cohort Query Example:**
```sql
-- dayXX_MODEL_cohorts.sql
WITH dayXX_first_booking AS (
    SELECT
        guest_id,
        MIN(booking_date) as first_booking_date,
        DATE_TRUNC('month', MIN(booking_date)) as cohort_month
    FROM dayXX_bookings
    GROUP BY guest_id
),
dayXX_cohort_ltv AS (
    SELECT
        fb.cohort_month,
        fb.guest_id,
        SUM(b.total_spend) OVER (
            PARTITION BY fb.guest_id
            ORDER BY b.booking_date
        ) as cumulative_ltv
    FROM dayXX_first_booking fb
    JOIN dayXX_bookings b ON fb.guest_id = b.guest_id
)
SELECT * FROM dayXX_cohort_ltv;
```

---

### **Day 8 (Patrick - Consulting Project Pipeline with dbt)**

**Data Sources:**
- Synthetic leads/projects data

**Mandatory Output:**
- [ ] dbt project structure:
```
  models/
    staging/
      stg_leads.sql
      stg_projects.sql
    intermediate/
      int_lead_to_project.sql
    marts/
      fct_pipeline_metrics.sql
```
- [ ] Pipeline stages: Lead → Qualification → Proposal → Project → Delivery
- [ ] Metrics: Conversion rate per stage, time-to-close, deal size
- [ ] dbt tests (at least 5 tests)
- [ ] dbt docs generated (static site)

**When to Stop:**
- ✅ dbt project runs with `dbt run` and `dbt test`
- ✅ At least 3 models (staging, intermediate, mart)
- ✅ 5+ tests passing
- ✅ dbt docs generated and included in README (screenshot or link)
- ✅ README explains "How Patrick uses this to prioritize leads"
- ✅ **Architectural Decision**: "Why dbt vs. plain SQL for this?" documented
- ❌ DON'T do: Incremental models (that's Day 9), custom macros yet, multiple sources, production deployment

**Expected Files:**
```
dayXX/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── stg_leads.sql
│   │   └── stg_projects.sql
│   ├── intermediate/
│   │   └── int_lead_to_project.sql
│   └── marts/
│       └── fct_pipeline_metrics.sql
├── tests/
│   └── schema.yml
├── data/
│   └── dayXX_consulting_pipeline.db
├── dayXX_DATA_synthetic_generator.py
├── .env.example
└── README.md
```

**dbt Naming Convention:**
```yaml
# In dbt_project.yml
name: 'dayXX_consulting_pipeline'
profile: 'dayXX_pipeline'

# In models
models:
  dayXX_consulting_pipeline:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

**dbt Model Example:**
```sql
-- models/staging/stg_leads.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('dayXX_pipeline', 'raw_leads') }}
),

renamed AS (
    SELECT
        lead_id AS dayXX_lead_id,
        lead_name AS dayXX_lead_name,
        stage AS dayXX_stage,
        created_at AS dayXX_created_at
    FROM source
)

SELECT * FROM renamed
```

**dbt Tests Example:**
```yaml
# tests/schema.yml
version: 2

models:
  - name: stg_leads
    columns:
      - name: dayXX_lead_id
        tests:
          - unique
          - not_null
      - name: dayXX_stage
        tests:
          - accepted_values:
              values: ['lead', 'qualified', 'proposal', 'project', 'delivery']
```

---

### **Day 9 (Jo - Hospitality Operations Funnel with dbt)**

**Data Sources:**
- Synthetic inquiry/booking/stay/review data (Airbnb-style)

**Mandatory Output:**
- [ ] dbt project with advanced features:
```
  models/
    staging/
      stg_inquiries.sql (source declaration)
      stg_bookings.sql
      stg_stays.sql
      stg_reviews.sql
    intermediate/
      int_funnel_events.sql (union all stages)
    marts/
      fct_funnel_conversion.sql (incremental!)
```
- [ ] Complete funnel: Inquiry → Booking → Check-in → Check-out → Review
- [ ] Metrics: Conversion rate per stage, drop-off points, time between stages
- [ ] Incremental processing (only new events)
- [ ] Custom macro (e.g., `calculate_stage_duration()`)

**When to Stop:**
- ✅ Incremental model working (`dbt run --full-refresh` vs. `dbt run`)
- ✅ At least 1 custom macro created and used
- ✅ Sources declared with freshness tests
- ✅ Complete funnel with 4+ stages
- ✅ README explains "How Jo uses this to optimize conversion"
- ✅ **Architectural Decision**: "Why incremental models?" documented
- ❌ DON'T do: Real-time processing, complex orchestration, external API calls, ML predictions

**Expected Files:**
```
dayXX/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── stg_inquiries.sql
│   │   ├── stg_bookings.sql
│   │   ├── stg_stays.sql
│   │   └── stg_reviews.sql
│   ├── intermediate/
│   │   └── int_funnel_events.sql
│   └── marts/
│       └── fct_funnel_conversion.sql (incremental)
├── macros/
│   └── calculate_stage_duration.sql
├── data/
│   └── dayXX_hospitality_funnel.db
├── dayXX_DATA_synthetic_generator.py
├── .env.example
└── README.md
```

**Incremental Model Example:**
```sql
-- models/marts/fct_funnel_conversion.sql
{{
  config(
    materialized='incremental',
    unique_key='dayXX_event_id',
    on_schema_change='append_new_columns'
  )
}}

WITH funnel_events AS (
    SELECT * FROM {{ ref('int_funnel_events') }}
)

SELECT
    dayXX_event_id,
    dayXX_user_id,
    dayXX_stage,
    dayXX_event_timestamp,
    {{ calculate_stage_duration('dayXX_event_timestamp', 'dayXX_stage') }} as dayXX_time_in_stage
FROM funnel_events

{% if is_incremental() %}
  WHERE dayXX_event_timestamp > (SELECT MAX(dayXX_event_timestamp) FROM {{ this }})
{% endif %}
```

**Custom Macro Example:**
```sql
-- macros/calculate_stage_duration.sql
{% macro calculate_stage_duration(timestamp_col, stage_col) %}
    LAG({{ timestamp_col }}) OVER (
        PARTITION BY {{ stage_col }}
        ORDER BY {{ timestamp_col }}
    ) as previous_timestamp,
    TIMESTAMPDIFF(
        HOUR,
        LAG({{ timestamp_col }}) OVER (PARTITION BY {{ stage_col }} ORDER BY {{ timestamp_col }}),
        {{ timestamp_col }}
    ) as duration_hours
{% endmacro %}
```

**Sources Declaration:**
```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: dayXX_funnel
    database: dayXX_hospitality_funnel
    tables:
      - name: raw_inquiries
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
      - name: raw_bookings
      - name: raw_stays
      - name: raw_reviews
```

---

### **Day 10 (Rafael - Family Office Data Warehouse Kimball)**

**Data Sources:**
- Synthetic family office data (assets, accounts, clients, transactions)

**Mandatory Output:**
- [ ] Star schema with:
  - **Fact Table**: `dayXX_fct_asset_holdings` (grain: asset-date-account)
  - **Dim Tables**: `dayXX_dim_assets` (SCD Type 2), `dayXX_dim_accounts`, `dayXX_dim_clients`, `dayXX_dim_date`
- [ ] SCD Type 2 implementation on `dayXX_dim_assets`:
  - Columns: `asset_key`, `asset_id`, `asset_name`, `asset_class`, `valid_from`, `valid_to`, `is_current`
- [ ] Surrogate keys on all dimensions
- [ ] Date dimension with 5+ years of data
- [ ] SQL queries demonstrating:
  - Total portfolio value per client
  - Asset class allocation over time
  - Historical tracking (SCD Type 2 in action)

**When to Stop:**
- ✅ Star schema documented (ERD diagram - can be text-based)
- ✅ SCD Type 2 implemented and tested (show historical changes)
- ✅ Surrogate keys on all dimensions
- ✅ Date dimension with useful attributes (is_weekend, fiscal_quarter, etc.)
- ✅ 3+ analytical queries demonstrating the DW in use
- ✅ README explains "How Rafael uses this for family office reporting"
- ✅ **Architectural Decision**: "Why Kimball vs. Data Vault?" documented
- ❌ DON'T do: Real-time portfolio tracking, complex financial calculations (IRR, Sharpe ratio), multi-currency handling, Bloomberg/Reuters integration

**Expected Files:**
```
dayXX/
├── data/
│   └── dayXX_family_office_dw.db
├── models/
│   ├── dayXX_MODEL_star_schema.sql (creates all tables)
│   ├── dayXX_MODEL_dim_date.sql
│   ├── dayXX_MODEL_dim_assets_scd2.sql
│   └── dayXX_MODEL_fact_holdings.sql
├── queries/
│   ├── dayXX_QUERY_portfolio_value.sql
│   ├── dayXX_QUERY_asset_allocation.sql
│   └── dayXX_QUERY_historical_tracking.sql
├── docs/
│   └── dayXX_ERD_star_schema.md (or .png)
├── dayXX_DATA_synthetic_generator.py
├── dayXX_CONFIG_settings.py
├── .env.example
└── README.md
```

**Star Schema Structure:**
```sql
-- Fact Table
CREATE TABLE dayXX_fct_asset_holdings (
    holding_key INTEGER PRIMARY KEY,
    asset_key INTEGER,
    account_key INTEGER,
    client_key INTEGER,
    date_key INTEGER,
    quantity DECIMAL(18,4),
    market_value DECIMAL(18,2),
    cost_basis DECIMAL(18,2),
    FOREIGN KEY (asset_key) REFERENCES dayXX_dim_assets(asset_key),
    FOREIGN KEY (account_key) REFERENCES dayXX_dim_accounts(account_key),
    FOREIGN KEY (client_key) REFERENCES dayXX_dim_clients(client_key),
    FOREIGN KEY (date_key) REFERENCES dayXX_dim_date(date_key)
);

-- SCD Type 2 Dimension
CREATE TABLE dayXX_dim_assets (
    asset_key INTEGER PRIMARY KEY,  -- Surrogate key
    asset_id VARCHAR(50),            -- Natural key
    asset_name VARCHAR(200),
    asset_class VARCHAR(50),
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);

-- Date Dimension
CREATE TABLE dayXX_dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    fiscal_quarter INTEGER,
    fiscal_year INTEGER
);

-- Other Dimensions
CREATE TABLE dayXX_dim_clients (
    client_key INTEGER PRIMARY KEY,
    client_id VARCHAR(50),
    client_name VARCHAR(200),
    client_type VARCHAR(50)
);

CREATE TABLE dayXX_dim_accounts (
    account_key INTEGER PRIMARY KEY,
    account_id VARCHAR(50),
    account_name VARCHAR(200),
    account_type VARCHAR(50)
);
```

**SCD Type 2 Logic Example:**
```sql
-- dayXX_MODEL_dim_assets_scd2.sql

-- Insert new asset (first time)
INSERT INTO dayXX_dim_assets (asset_key, asset_id, asset_name, asset_class, valid_from, valid_to, is_current)
VALUES (1, 'AAPL', 'Apple Inc.', 'Equity', '2020-01-01', NULL, TRUE);

-- Update existing asset (asset class changes)
-- 1. Close current record
UPDATE dayXX_dim_assets
SET
    valid_to = '2023-06-30',
    is_current = FALSE
WHERE asset_id = 'AAPL' AND is_current = TRUE;

-- 2. Insert new record with updated information
INSERT INTO dayXX_dim_assets (asset_key, asset_id, asset_name, asset_class, valid_from, valid_to, is_current)
VALUES (2, 'AAPL', 'Apple Inc.', 'Technology Equity', '2023-07-01', NULL, TRUE);
```

**Analytical Query Examples:**
```sql
-- dayXX_QUERY_portfolio_value.sql
-- Total portfolio value per client
SELECT
    c.client_name,
    SUM(f.market_value) as total_portfolio_value,
    COUNT(DISTINCT f.asset_key) as number_of_assets
FROM dayXX_fct_asset_holdings f
JOIN dayXX_dim_clients c ON f.client_key = c.client_key
JOIN dayXX_dim_date d ON f.date_key = d.date_key
WHERE d.full_date = (SELECT MAX(full_date) FROM dayXX_dim_date)
GROUP BY c.client_name
ORDER BY total_portfolio_value DESC;

-- dayXX_QUERY_asset_allocation.sql
-- Asset class allocation over time
SELECT
    d.year,
    d.quarter,
    a.asset_class,
    SUM(f.market_value) as total_value,
    ROUND(100.0 * SUM(f.market_value) / SUM(SUM(f.market_value)) OVER (PARTITION BY d.year, d.quarter), 2) as allocation_pct
FROM dayXX_fct_asset_holdings f
JOIN dayXX_dim_assets a ON f.asset_key = a.asset_key
JOIN dayXX_dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.quarter, a.asset_class
ORDER BY d.year, d.quarter, allocation_pct DESC;

-- dayXX_QUERY_historical_tracking.sql
-- SCD Type 2 in action - show historical changes
SELECT
    asset_id,
    asset_name,
    asset_class,
    valid_from,
    valid_to,
    is_current,
    CASE
        WHEN valid_to IS NULL THEN 'Current'
        ELSE 'Historical'
    END as record_status
FROM dayXX_dim_assets
WHERE asset_id = 'AAPL'
ORDER BY valid_from;
```

**ERD Documentation (Text-based):**
```markdown
# dayXX_ERD_star_schema.md

## Star Schema - Family Office Data Warehouse

### Fact Table: dayXX_fct_asset_holdings
- **Grain**: One row per asset per account per date
- **Keys**:
  - holding_key (PK)
  - asset_key (FK to dim_assets)
  - account_key (FK to dim_accounts)
  - client_key (FK to dim_clients)
  - date_key (FK to dim_date)
- **Measures**:
  - quantity
  - market_value
  - cost_basis

### Dimensions:

#### dayXX_dim_assets (SCD Type 2)
- asset_key (PK - surrogate)
- asset_id (natural key)
- asset_name
- asset_class
- valid_from
- valid_to
- is_current

#### dayXX_dim_clients
- client_key (PK)
- client_id
- client_name
- client_type

#### dayXX_dim_accounts
- account_key (PK)
- account_id
- account_name
- account_type

#### dayXX_dim_date
- date_key (PK)
- full_date
- year, quarter, month
- is_weekend
- fiscal_quarter, fiscal_year

### Relationships:
```
          dayXX_dim_assets (SCD Type 2)
                    |
                    v
dayXX_dim_clients ---> dayXX_fct_asset_holdings <--- dayXX_dim_date
                    ^
                    |
          dayXX_dim_accounts
```
```

---

## 🔄 PIVOT RULE (1 hour)

**For all Modeling projects:**

If after **1 hour** you still haven't:
- Set up the database/dbt environment OR
- Written basic working SQL

➡️ **IMMEDIATE PIVOT to simpler approach:**

1. Use SQLite instead of PostgreSQL/BigQuery
2. Use plain SQL instead of dbt (can migrate later)
3. Reduce number of metrics/dimensions
4. Focus on ONE core feature working perfectly

**DON'T spend more than 1h fighting with setup. The goal is to deliver, not perfectionism.**

**Example Pivot Scenarios:**

**Day 8/9 (dbt projects):**
```bash
# After 1h, if dbt setup still failing:

# BEFORE (complex):
dbt init dayXX_project
# ... 30 minutes of config errors ...

# AFTER (simple pivot):
# Create plain SQL files in models/ folder
# Run directly with sqlite3 or python
# Document: "Will migrate to dbt after proof of concept works"
```

**Day 10 (Data Warehouse):**
```bash
# After 1h, if SCD Type 2 logic too complex:

# BEFORE (full SCD Type 2):
# Trying to implement merge/upsert logic with triggers...

# AFTER (simple pivot):
# Create basic dimension table (no SCD)
# Add is_current flag manually
# Document: "Simplified SCD Type 2 - full implementation in production phase"
```

---

## 📊 FINAL VALIDATION (All Projects)

Before pushing:
```bash
# 1. Test in clean environment
cd /tmp
git clone your-repo
cd advent-automation-2025/dayXX

# 2. Configure .env (add project variables to root config/.env)
# Make sure to follow convention: DAYXX_SPECIFIC_VAR

# 3. Execute
python dayXX_DATA_synthetic_generator.py  # Generate data
sqlite3 data/dayXX_database.db < models/dayXX_MODEL_*.sql  # Run models
# OR
cd dayXX && dbt run && dbt test  # If using dbt

# 4. Validate
# - Models executed without errors? ✅
# - Results make business sense? ✅
# - Logs are informative? ✅
# - Naming convention correct (dayXX_ prefix)? ✅
```

If ALL above works → ✅ **Project complete**

---

## 🔧 INTEGRATION WITH EXISTING STRUCTURE CHECKLIST

Before finalizing any Modeling project, verify:

- [ ] Environment variables added to `config/.env` following existing convention
- [ ] Specific dependencies documented in `dayXX_requirements.txt` (if needed)
- [ ] Common dependencies added to root `requirements.txt` (only if globally relevant)
- [ ] ALL files have `dayXX_` prefix
- [ ] ALL variables/classes/functions follow isolated naming
- [ ] README clearly explains how to configure environment variables
- [ ] Project works INDEPENDENTLY (doesn't depend on other days)

**Environment Variables Example:**
```bash
# In root config/.env

# Day 06 - Financial Consulting Metrics
DAYXX_DB_PATH=/path/to/dayXX_consulting.db
DAYXX_LOOKER_STUDIO_ID=abc123

# Day 07 - Hospitality LTV
DAYXX_HOSPITALITY_DB_PATH=/path/to/dayXX_hospitality.db

# Day 08 - Consulting Pipeline (dbt)
DAYXX_DBT_PROFILES_DIR=/path/to/dayXX/.dbt

# Day 09 - Hospitality Funnel (dbt)
DAYXX_DBT_TARGET=dev

# Day 10 - Family Office DW
DAYXX_DW_DB_PATH=/path/to/dayXX_family_office_dw.db
```

**Dependencies Example:**
```txt
# In root requirements.txt

# Day 06-07: SQL + Analytics
sqlalchemy==2.0.23
pandas==2.1.4

# Day 08-09: dbt
dbt-core==1.7.4
dbt-sqlite==1.7.1

# Day 10: Data Warehouse
sqlalchemy==2.0.23
```

---

## 💡 FINAL REMINDER

**You're building a PORTFOLIO, not a production product.**

The goal is to demonstrate:
- ✅ You know data modeling concepts
- ✅ You know SQL (CTEs, window functions, joins)
- ✅ You understand business logic translation
- ✅ You can document your work
- ✅ You can deliver in 3 hours
- ✅ You know how to work with code isolation

**NOT to demonstrate:**
- ❌ Perfect, bug-free system
- ❌ Optimized performance
- ❌ All edge cases handled
- ❌ Production-ready code

**Focus: Functional > Perfect. Documented > Complex. Delivered > Ideal. Isolated > Shared.**

---

## 📚 QUICK REFERENCE - SQL PATTERNS

### **CTEs (Common Table Expressions)**
```sql
-- Basic CTE
WITH dayXX_metrics AS (
    SELECT
        project_id,
        SUM(hours) as total_hours
    FROM dayXX_timesheets
    GROUP BY project_id
)
SELECT * FROM dayXX_metrics;

-- Multiple CTEs
WITH dayXX_billable AS (
    SELECT project_id, SUM(hours) as billable_hours
    FROM dayXX_timesheets
    WHERE is_billable = TRUE
    GROUP BY project_id
),
dayXX_total AS (
    SELECT project_id, SUM(hours) as total_hours
    FROM dayXX_timesheets
    GROUP BY project_id
)
SELECT
    b.project_id,
    b.billable_hours,
    t.total_hours,
    ROUND(100.0 * b.billable_hours / t.total_hours, 2) as utilization_rate
FROM dayXX_billable b
JOIN dayXX_total t ON b.project_id = t.project_id;
```

### **Window Functions**
```sql
-- Running totals
SELECT
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date) as cumulative_revenue
FROM dayXX_sales;

-- Ranking
SELECT
    project_name,
    profitability,
    RANK() OVER (ORDER BY profitability DESC) as profitability_rank
FROM dayXX_projects;

-- Lag/Lead (comparing to previous period)
SELECT
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) as previous_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY date) as revenue_change
FROM dayXX_monthly_sales;

-- Partition by
SELECT
    client_id,
    project_id,
    revenue,
    SUM(revenue) OVER (PARTITION BY client_id) as client_total_revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY client_id), 2) as pct_of_client_revenue
FROM dayXX_projects;
```

### **Cohort Analysis Pattern**
```sql
-- Step 1: Identify first event per user
WITH dayXX_first_event AS (
    SELECT
        user_id,
        MIN(event_date) as first_event_date,
        DATE_TRUNC('month', MIN(event_date)) as cohort_month
    FROM dayXX_events
    GROUP BY user_id
),

-- Step 2: Calculate time since first event
dayXX_cohort_activity AS (
    SELECT
        fe.cohort_month,
        fe.user_id,
        e.event_date,
        DATEDIFF(MONTH, fe.first_event_date, e.event_date) as months_since_first
    FROM dayXX_first_event fe
    JOIN dayXX_events e ON fe.user_id = e.user_id
),

-- Step 3: Calculate retention
dayXX_retention AS (
    SELECT
        cohort_month,
        months_since_first,
        COUNT(DISTINCT user_id) as active_users
    FROM dayXX_cohort_activity
    GROUP BY cohort_month, months_since_first
)

-- Step 4: Calculate retention rate
SELECT
    r.cohort_month,
    r.months_since_first,
    r.active_users,
    first.cohort_size,
    ROUND(100.0 * r.active_users / first.cohort_size, 2) as retention_rate
FROM dayXX_retention r
JOIN (
    SELECT cohort_month, active_users as cohort_size
    FROM dayXX_retention
    WHERE months_since_first = 0
) first ON r.cohort_month = first.cohort_month
ORDER BY r.cohort_month, r.months_since_first;
```

---

## 🎓 LEARNING RESOURCES (Optional - After 3h)

If you finish early or want to learn more AFTER the 3-hour delivery:

### **SQL & Data Modeling:**
- [SQL Window Functions Tutorial](https://mode.com/sql-tutorial/sql-window-functions/)
- [Kimball Star Schema Guide](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Cohort Analysis SQL](https://sqlsandwich.com/blog/cohort-analysis-sql/)

### **dbt:**
- [dbt Official Docs](https://docs.getdbt.com/)
- [dbt Learn - Free Courses](https://learn.getdbt.com/)
- [Incremental Models Guide](https://docs.getdbt.com/docs/build/incremental-models)

### **Data Warehousing:**
- [SCD Type 2 Tutorial](https://www.sqlshack.com/implementing-slowly-changing-dimensions-scds-in-data-warehouses/)
- [Date Dimension Best Practices](https://www.kimballgroup.com/2008/09/slowly-changing-dimensions-are-not-always-as-easy-as-1-2-3/)

**Remember: These are OPTIONAL. Focus on the 3-hour delivery first!**
