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

### **Day 6 (Murilo - SaaS Health Metrics Foundation)**

**Stakeholder:** Murilo (Simetryk SaaS - originally Day 24)

**Project:** SaaS Health Metrics Foundation (SQL)

**Focus:** Churn, MRR, Retention - dados prontos para dashboard

**Data Sources:**
- Synthetic SaaS data (customers, subscriptions, MRR movements)
- 500 customers, 24 months history
- 3 plan tiers: Starter/Pro/Enterprise

**Mandatory Output:**
- [ ] SQLite database with 3 tables:
  - `day06_customers` (customer_id, signup_date, plan_tier, mrr_current, status)
  - `day06_subscriptions` (subscription_id, customer_id, start_date, end_date, mrr, plan_tier)
  - `day06_mrr_movements` (month, new_mrr, expansion_mrr, contraction_mrr, churn_mrr, net_mrr)
- [ ] 4 SQL Views ready for dashboard consumption:
  - `day06_mrr_summary` - MRR waterfall (New, Expansion, Contraction, Churn)
  - `day06_churn_by_cohort` - Churn rate by signup month and segment
  - `day06_retention_curves` - Cohort-based retention analysis
  - `day06_customer_health` - LTV/CAC and health scoring
- [ ] Sample queries demonstrating each metric
- [ ] README explaining each metric and connection to Dashboard (Day 19)

**When to Stop:**
- ✅ 4 views created with clear business logic
- ✅ MRR Movement correctly calculated (New + Expansion - Contraction - Churn = Net MRR)
- ✅ Cohort analysis with at least 12 months of data
- ✅ Churn rate calculated monthly and by segment (plan tier)
- ✅ Window functions used for retention curves
- ✅ Comments explaining SaaS metric subtleties
- ✅ README explains "How Murilo uses this for SaaS health monitoring"
- ✅ **Dashboard Integration**: Documentation showing which views connect to Day 19 dashboard
- ❌ DON'T do: Churn prediction (ML), real payment gateway integration, dunning management, ARR forecasting

**Expected Files:**
```
day06/
├── data/
│   └── day06_saas_metrics.db (SQLite)
├── models/
│   ├── day06_MODEL_base_tables.sql (creates 3 base tables)
│   └── day06_MODEL_views.sql (creates 4 analytical views)
├── queries/
│   ├── day06_QUERY_mrr_waterfall.sql
│   ├── day06_QUERY_churn_analysis.sql
│   ├── day06_QUERY_retention.sql
│   └── day06_QUERY_customer_health.sql
├── day06_DATA_synthetic_saas.py
├── day06_CONFIG_settings.py
├── day06_requirements.txt (if needed)
├── .env.example
└── README.md
```

**Data Model Schema:**
```sql
-- Base Table 1: Customers
CREATE TABLE day06_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE NOT NULL,
    plan_tier VARCHAR(20) CHECK (plan_tier IN ('Starter', 'Pro', 'Enterprise')),
    mrr_current DECIMAL(10,2),
    status VARCHAR(10) CHECK (status IN ('active', 'churned'))
);

-- Base Table 2: Subscriptions
CREATE TABLE day06_subscriptions (
    subscription_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE,
    mrr DECIMAL(10,2),
    plan_tier VARCHAR(20) CHECK (plan_tier IN ('Starter', 'Pro', 'Enterprise')),
    FOREIGN KEY (customer_id) REFERENCES day06_customers(customer_id)
);

-- Base Table 3: MRR Movements
CREATE TABLE day06_mrr_movements (
    month DATE PRIMARY KEY,
    new_mrr DECIMAL(10,2),
    expansion_mrr DECIMAL(10,2),
    contraction_mrr DECIMAL(10,2),
    churn_mrr DECIMAL(10,2),
    net_mrr DECIMAL(10,2)
);
```

**View Examples:**
```sql
-- View 1: MRR Summary (Waterfall)
CREATE VIEW day06_mrr_summary AS
WITH day06_monthly_changes AS (
    SELECT
        DATE_TRUNC('month', start_date) as month,
        SUM(CASE WHEN start_date = signup_date THEN mrr ELSE 0 END) as new_mrr,
        SUM(CASE WHEN start_date > signup_date AND mrr > prev_mrr THEN mrr - prev_mrr ELSE 0 END) as expansion_mrr,
        SUM(CASE WHEN start_date > signup_date AND mrr < prev_mrr THEN prev_mrr - mrr ELSE 0 END) as contraction_mrr,
        SUM(CASE WHEN end_date IS NOT NULL THEN mrr ELSE 0 END) as churn_mrr
    FROM day06_subscriptions s
    JOIN day06_customers c ON s.customer_id = c.customer_id
)
SELECT
    month,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churn_mrr,
    (new_mrr + expansion_mrr - contraction_mrr - churn_mrr) as net_mrr
FROM day06_monthly_changes;

-- View 2: Churn by Cohort
CREATE VIEW day06_churn_by_cohort AS
WITH day06_cohorts AS (
    SELECT
        DATE_TRUNC('month', signup_date) as cohort_month,
        plan_tier,
        COUNT(*) as cohort_size,
        SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) as churned_count
    FROM day06_customers
    GROUP BY DATE_TRUNC('month', signup_date), plan_tier
)
SELECT
    cohort_month,
    plan_tier,
    cohort_size,
    churned_count,
    ROUND(100.0 * churned_count / cohort_size, 2) as churn_rate_pct
FROM day06_cohorts;

-- View 3: Retention Curves
CREATE VIEW day06_retention_curves AS
WITH day06_first_sub AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(start_date)) as cohort_month
    FROM day06_subscriptions
    GROUP BY customer_id
),
day06_monthly_activity AS (
    SELECT
        fs.cohort_month,
        s.customer_id,
        DATE_TRUNC('month', s.start_date) as activity_month,
        DATEDIFF(MONTH, fs.cohort_month, DATE_TRUNC('month', s.start_date)) as months_since_signup
    FROM day06_first_sub fs
    JOIN day06_subscriptions s ON fs.customer_id = s.customer_id
)
SELECT
    cohort_month,
    months_since_signup,
    COUNT(DISTINCT customer_id) as retained_customers,
    ROUND(100.0 * COUNT(DISTINCT customer_id) /
          FIRST_VALUE(COUNT(DISTINCT customer_id)) OVER (
              PARTITION BY cohort_month
              ORDER BY months_since_signup
          ), 2) as retention_rate_pct
FROM day06_monthly_activity
GROUP BY cohort_month, months_since_signup;

-- View 4: Customer Health Score
CREATE VIEW day06_customer_health AS
WITH day06_customer_metrics AS (
    SELECT
        c.customer_id,
        c.plan_tier,
        c.mrr_current,
        DATEDIFF(MONTH, c.signup_date, CURRENT_DATE) as customer_age_months,
        (c.mrr_current * DATEDIFF(MONTH, c.signup_date, CURRENT_DATE)) as ltv_estimate,
        c.status
    FROM day06_customers c
)
SELECT
    customer_id,
    plan_tier,
    mrr_current,
    customer_age_months,
    ltv_estimate,
    -- Simple CAC assumption: $500 per customer
    ROUND(ltv_estimate / 500.0, 2) as ltv_cac_ratio,
    CASE
        WHEN status = 'churned' THEN 'Churned'
        WHEN ltv_estimate / 500.0 > 3 THEN 'Healthy'
        WHEN ltv_estimate / 500.0 > 1 THEN 'At Risk'
        ELSE 'Critical'
    END as health_status
FROM day06_customer_metrics;
```

**Dashboard Integration (Day 19):**
```markdown
## Connection to Day 19 Dashboard

The following views are designed to be consumed by the Dashboard project:

1. **day06_mrr_summary** → MRR Waterfall Chart
   - X-axis: month
   - Y-axis: new_mrr, expansion_mrr, contraction_mrr, churn_mrr
   - Shows monthly MRR movement breakdown

2. **day06_churn_by_cohort** → Churn Heatmap
   - Rows: cohort_month
   - Columns: plan_tier
   - Color: churn_rate_pct

3. **day06_retention_curves** → Retention Line Chart
   - X-axis: months_since_signup
   - Y-axis: retention_rate_pct
   - Series: cohort_month (different cohorts as separate lines)

4. **day06_customer_health** → Health Score Distribution
   - Pie chart: COUNT(*) GROUP BY health_status
   - Table: Top customers by ltv_cac_ratio
```

**Complexity Assessment:**
- **SQL Complexity:** Média (CTEs, window functions, date calculations)
- **Business Logic:** Alta (SaaS metrics são sutis - MRR movements, cohort logic)
- **Data Volume:** 500 customers, 24 months history (~6,000 subscription records)
- **Time Estimate:** 3h (mais tempo em business logic que código)

**Final Validation:**
```sql
-- Run these queries to validate
SELECT * FROM day06_mrr_summary ORDER BY month;
SELECT * FROM day06_churn_by_cohort ORDER BY cohort_month, plan_tier;
SELECT * FROM day06_retention_curves WHERE cohort_month = '2024-01-01';
SELECT * FROM day06_customer_health WHERE health_status = 'Healthy';
-- Should return results with no errors and sensible values
```

**Naming Examples:**
```python
# ✅ CORRECT
DAY06_DB_PATH = "data/day06_saas_metrics.db"
DAY06_DEFAULT_CAC = 500.0
DAY06_PLAN_TIERS = ['Starter', 'Pro', 'Enterprise']

class day06_SaasMetricsGenerator:
    pass

def day06_calculate_mrr_movement():
    pass

# ❌ WRONG - Generic names cause conflicts
DB_PATH = "data/database.db"  # Could conflict with other days
class MetricsGenerator:  # Too generic
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

### **Day 8 (Patrick - SaaS Growth Funnel & Cohort Analysis with dbt)**

**Stakeholder:** Patrick (MBA, Strategy)

**Project:** SaaS Growth Funnel & Cohort Analysis (dbt)

**Focus:** Acquisition funnel, activation, engagement

**Data Sources:**
- Synthetic SaaS user events data (visits, signups, activations, subscriptions)
- 10K users, 100K events

**Mandatory Output:**
- [ ] dbt project with 5 core models:
```
  models/
    staging/
      stg_users.sql
      stg_events.sql
      stg_subscriptions.sql
      sources.yml
    intermediate/
      int_funnel_steps.sql
      int_user_engagement.sql
      int_feature_usage.sql
    marts/
      fct_acquisition_funnel.sql (incremental)
      fct_engagement_cohorts.sql
      dim_user_health.sql
```

**Core Deliverables:**

**dbt Models:**
1. **Acquisition Funnel** (Visit → Signup → Activation → Paid)
2. **Engagement Cohorts** (DAU/WAU/MAU by cohort)
3. **Feature Adoption** (which features drive retention)
4. **Expansion Signals** (indicators for upsell)
5. **Activation Rate** (time to first value)

**Output Models (Ready for Dashboard):**
```sql
-- Model 1: Funnel Conversion
fct_acquisition_funnel
├── cohort_month
├── visitors
├── signups
├── activated
├── paid
└── conversion_rates

-- Model 2: Engagement by Cohort
fct_engagement_cohorts
├── cohort_month
├── months_since_signup
├── dau_rate
├── feature_adoption_rate
└── retention_rate
```

**When to Stop:**
- ✅ dbt project runs with `dbt run` and `dbt test`
- ✅ All 5 core models created and tested
- ✅ Funnel stages clearly defined (Visit → Signup → Activation → Paid)
- ✅ Cohort analysis with engagement metrics (DAU/WAU/MAU)
- ✅ Feature adoption tracking implemented
- ✅ Incremental model working (`dbt run --full-refresh` vs. `dbt run`)
- ✅ 5+ tests passing
- ✅ README explains "How Patrick uses this for growth strategy"
- ✅ **Dashboard Integration**: Documentation showing connection to Day 16 dashboard
- ✅ **Architectural Decision**: "Why dbt + incremental models for funnel tracking?" documented
- ❌ DON'T do: Real-time processing, complex ML predictions, multi-product handling, advanced attribution, production deployment

**Expected Files:**
```
day08/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── stg_users.sql
│   │   ├── stg_events.sql
│   │   └── stg_subscriptions.sql
│   ├── intermediate/
│   │   ├── int_funnel_steps.sql
│   │   ├── int_user_engagement.sql
│   │   └── int_feature_usage.sql
│   └── marts/
│       ├── fct_acquisition_funnel.sql (incremental)
│       ├── fct_engagement_cohorts.sql
│       └── dim_user_health.sql
├── macros/
│   └── calculate_activation_time.sql
├── tests/
│   └── schema.yml
├── data/
│   └── day08_saas_funnel.db
├── day08_DATA_synthetic_generator.py
├── day08_CONFIG_settings.py
├── .env.example
└── README.md
```

**dbt Naming Convention:**
```yaml
# In dbt_project.yml
name: 'day08_saas_funnel'
profile: 'day08_funnel'

# In models
models:
  day08_saas_funnel:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table
```

**dbt Model Examples:**
```sql
-- models/staging/stg_users.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day08_saas', 'raw_users') }}
),

renamed AS (
    SELECT
        user_id AS day08_user_id,
        signup_date AS day08_signup_date,
        email AS day08_email,
        utm_source AS day08_utm_source,
        utm_campaign AS day08_utm_campaign
    FROM source
)

SELECT * FROM renamed
```

```sql
-- models/marts/fct_acquisition_funnel.sql (incremental)
{{
  config(
    materialized='incremental',
    unique_key='day08_cohort_month',
    on_schema_change='append_new_columns'
  )
}}

WITH funnel_stages AS (
    SELECT * FROM {{ ref('int_funnel_steps') }}
),

cohort_funnel AS (
    SELECT
        DATE_TRUNC('month', signup_date) as day08_cohort_month,
        COUNT(DISTINCT CASE WHEN stage = 'visit' THEN user_id END) as day08_visitors,
        COUNT(DISTINCT CASE WHEN stage = 'signup' THEN user_id END) as day08_signups,
        COUNT(DISTINCT CASE WHEN stage = 'activated' THEN user_id END) as day08_activated,
        COUNT(DISTINCT CASE WHEN stage = 'paid' THEN user_id END) as day08_paid
    FROM funnel_stages
    GROUP BY DATE_TRUNC('month', signup_date)
)

SELECT
    day08_cohort_month,
    day08_visitors,
    day08_signups,
    day08_activated,
    day08_paid,
    ROUND(100.0 * day08_signups / NULLIF(day08_visitors, 0), 2) as day08_visit_to_signup_rate,
    ROUND(100.0 * day08_activated / NULLIF(day08_signups, 0), 2) as day08_signup_to_activation_rate,
    ROUND(100.0 * day08_paid / NULLIF(day08_activated, 0), 2) as day08_activation_to_paid_rate
FROM cohort_funnel

{% if is_incremental() %}
  WHERE day08_cohort_month > (SELECT MAX(day08_cohort_month) FROM {{ this }})
{% endif %}
```

```sql
-- models/marts/fct_engagement_cohorts.sql
{{ config(materialized='table') }}

WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date) as cohort_month
    FROM {{ ref('stg_users') }}
),

engagement_metrics AS (
    SELECT
        uc.cohort_month as day08_cohort_month,
        DATEDIFF(MONTH, uc.cohort_month, e.event_date) as day08_months_since_signup,
        COUNT(DISTINCT CASE WHEN e.event_type = 'daily_active' THEN e.user_id END) /
            NULLIF(COUNT(DISTINCT uc.user_id), 0) as day08_dau_rate,
        COUNT(DISTINCT CASE WHEN e.event_type = 'feature_used' THEN e.user_id END) /
            NULLIF(COUNT(DISTINCT uc.user_id), 0) as day08_feature_adoption_rate,
        COUNT(DISTINCT e.user_id) / NULLIF(COUNT(DISTINCT uc.user_id), 0) as day08_retention_rate
    FROM user_cohorts uc
    LEFT JOIN {{ ref('stg_events') }} e ON uc.user_id = e.user_id
    GROUP BY uc.cohort_month, DATEDIFF(MONTH, uc.cohort_month, e.event_date)
)

SELECT * FROM engagement_metrics
```

**dbt Tests Example:**
```yaml
# tests/schema.yml
version: 2

models:
  - name: stg_users
    columns:
      - name: day08_user_id
        tests:
          - unique
          - not_null
      - name: day08_signup_date
        tests:
          - not_null

  - name: stg_events
    columns:
      - name: day08_event_id
        tests:
          - unique
          - not_null
      - name: day08_user_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: day08_user_id

  - name: fct_acquisition_funnel
    columns:
      - name: day08_cohort_month
        tests:
          - unique
          - not_null
      - name: day08_visitors
        tests:
          - not_null
```

**Dashboard Integration (Day 16):**
```markdown
## Connection to Day 16 Dashboard

The following models are designed to be consumed by the Dashboard project:

1. **fct_acquisition_funnel** → Funnel Conversion Chart
   - X-axis: cohort_month
   - Y-axis: visitors, signups, activated, paid
   - Conversion rates displayed as annotations

2. **fct_engagement_cohorts** → Engagement Trends
   - X-axis: months_since_signup
   - Y-axis: dau_rate, feature_adoption_rate, retention_rate
   - Series: cohort_month (different cohorts as separate lines)

3. **dim_user_health** → User Health Segmentation
   - Pie chart: COUNT(*) GROUP BY health_status
   - Table: Top users by engagement score
```

**Complexity Assessment:**
- **dbt Complexity:** Média (incremental models, macros)
- **Business Logic:** Média (growth metrics, cohort analysis)
- **Data Volume:** 10K users, 100K events
- **Time Estimate:** 3h (dbt setup + models + documentation)

**Final Validation:**
```bash
# Run dbt commands
cd day08
dbt run --full-refresh
dbt test
dbt docs generate

# Validate results
sqlite3 data/day08_saas_funnel.db "SELECT * FROM fct_acquisition_funnel ORDER BY day08_cohort_month;"
sqlite3 data/day08_saas_funnel.db "SELECT * FROM fct_engagement_cohorts WHERE day08_cohort_month = '2024-01-01';"
```

**Naming Examples:**
```python
# ✅ CORRECT
DAY08_DB_PATH = "data/day08_saas_funnel.db"
DAY08_ACTIVATION_THRESHOLD = 3  # days
DAY08_FUNNEL_STAGES = ['visit', 'signup', 'activated', 'paid']

class day08_SaasFunnelGenerator:
    pass

def day08_calculate_activation_rate():
    pass

# ❌ WRONG - Generic names cause conflicts
DB_PATH = "data/database.db"
class FunnelGenerator:  # Too generic
```

---

### **Day 9 (Jo - Property Manager Operations Data Warehouse with dbt)**

**Stakeholder:** Jo (Property Manager - 6 houseboats)

**Project:** Multi-Platform Property Management Data Warehouse Foundation

**Focus:** Unified operations funnel tracking across booking platforms (Airbnb + Booking.com), conversion optimization, and portfolio performance metrics

**Data Sources:**
- Synthetic multi-platform reservation data (Airbnb + Booking.com)
- Complete guest journey: Inquiry → Booking → Check-in → Check-out → Review
- 500+ reservations, 12+ months history

---

## 📋 Public vs Private Deliverables

### **What Goes on GitHub (Public Portfolio)**
✅ **Technical implementation** (dbt models, SQL, macros)
✅ **Architecture documentation** (why dbt, why incremental models)
✅ **Portfolio metrics** (presented as "demonstration of multi-platform data unification")
✅ **Business problem framing** ("Property managers need unified analytics across platforms")
✅ **How to run locally** (setup instructions, sample queries)
✅ **Technical learning objectives** (dbt features demonstrated)

❌ **ANY mention of**: MicroSaaS, commercial plans, product roadmap, MVP, "Phase 1/2/3", business model, pricing, or competitive analysis

### **What Stays Local (Product Development)**
📝 **PRIVATE_PRODUCT_NOTES.md** (NOT in public repo):
- MicroSaaS vision and 3-phase roadmap
- Why this schema powers the commercial product
- Migration path from SQLite → Supabase (production DB)
- Which tables power which SaaS features
- Competitive analysis vs. Guesty/Hostaway
- Technical debt and production hardening notes

🔒 **Add to .gitignore**:
```
PRIVATE_PRODUCT_NOTES.md
MICROSAAS_ROADMAP.md
/business_plan/
/pricing_research/
/competitor_analysis/
*.private.*
```

---

## 📄 Licensing Strategy

**Use MIT License with Commercial Use Restriction**

**Why this approach:**
- Shows confidence in code quality (industry-standard MIT base)
- Protects commercial opportunity (prevents direct cloning for profit)
- Allows educational/portfolio use (helps you get hired)
- Standard for "open core" SaaS models

**LICENSE file to include:**
```
MIT License (Modified for Portfolio Use)

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to use,
copy, modify, merge, and distribute the Software for NON-COMMERCIAL purposes,
subject to the following conditions:

[Standard MIT License conditions...]

COMMERCIAL USE RESTRICTION:
Commercial use of this software (defined as use in a business, product, or
service that generates revenue) requires explicit written permission from
the copyright holder.

For portfolio/educational use: Freely available
For commercial licensing inquiries: [your contact email]
```

**Alternative:** Use "Commons Clause" addon to MIT for stronger protection

---

## 🎯 Mandatory Output

**Core dbt Project Structure:**
- [ ] dbt project with production-ready architecture:
```
  models/
    staging/
      stg_airbnb_inquiries.sql
      stg_airbnb_bookings.sql
      stg_booking_com_inquiries.sql
      stg_booking_com_bookings.sql
      stg_stays.sql (unified across platforms)
      stg_reviews.sql (unified)
      sources.yml (with freshness tests)
    intermediate/
      int_unified_reservations.sql (platform unification logic)
      int_funnel_events.sql (all stages)
      int_property_performance.sql
    marts/
      fct_funnel_conversion.sql (incremental!)
      fct_reservations_unified.sql
      metrics_portfolio_public.sql (powers public-facing portfolio page)
      dim_platform_comparison.sql
```

**Critical Business Requirements:**
- [ ] **Multi-Platform Unification**: Airbnb + Booking.com data merged with platform tracking
- [ ] **Complete Operations Funnel**: Inquiry → Booking → Check-in → Check-out → Review
- [ ] **Portfolio Metrics Mart**: Occupancy rate, ADR (Average Daily Rate), RevPAR, platform mix
- [ ] **Conversion Metrics**: Stage-by-stage conversion rates, drop-off analysis, time-to-conversion
- [ ] **Incremental Processing**: Only new events processed (production-ready pattern)
- [ ] **Custom Business Logic Macros**: `calculate_stage_duration()`, `calculate_occupancy_rate()`, `unify_platform_data()`

---

## ⏱️ When to Stop

### **Technical Completeness:**
- ✅ Incremental model working (`dbt run --full-refresh` vs. `dbt run`)
- ✅ At least 2 custom macros created and used (stage duration + one business logic macro)
- ✅ Sources declared with freshness tests (both Airbnb + Booking.com sources)
- ✅ Complete funnel with 5 stages (inquiry/booking/check-in/check-out/review)
- ✅ Multi-platform unification logic working (Airbnb + Booking.com unified)
- ✅ 5+ dbt tests passing (unique, not_null, relationships, custom)

### **Business Requirements Met:**
- ✅ Portfolio metrics mart created (`metrics_portfolio_public.sql`)
- ✅ Platform comparison dimension showing Airbnb vs Booking.com performance
- ✅ Occupancy rate calculated correctly (nights booked / nights available)
- ✅ ADR and RevPAR metrics accurate

### **Documentation Complete:**
- ✅ **PUBLIC README** (portfolio-focused, no commercial mentions)
- ✅ **PRIVATE_PRODUCT_NOTES.md** (strategic context for your eyes only)
- ✅ **Architectural Decision**: "Why incremental models for operations data?" documented
- ✅ **Architectural Decision**: "Multi-platform unification strategy" documented
- ✅ Clear separation: Public vs Private documentation

### **What NOT to Build:**
- ❌ Real-time processing (batch is fine for portfolio)
- ❌ Complex orchestration (Airflow/Dagster)
- ❌ External API calls (use synthetic data)
- ❌ ML predictions (churn/pricing models)
- ❌ Production deployment (keep local SQLite for portfolio)
- ❌ Real booking platform integrations

---

## 📁 Expected Files

```
day09/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── sources.yml (both platforms declared)
│   │   ├── stg_airbnb_inquiries.sql
│   │   ├── stg_airbnb_bookings.sql
│   │   ├── stg_booking_com_inquiries.sql
│   │   ├── stg_booking_com_bookings.sql
│   │   ├── stg_stays.sql
│   │   └── stg_reviews.sql
│   ├── intermediate/
│   │   ├── int_unified_reservations.sql (★ CRITICAL: platform unification)
│   │   ├── int_funnel_events.sql
│   │   └── int_property_performance.sql
│   └── marts/
│       ├── fct_funnel_conversion.sql (incremental)
│       ├── fct_reservations_unified.sql
│       ├── metrics_portfolio_public.sql (★ CRITICAL: portfolio metrics)
│       └── dim_platform_comparison.sql
├── macros/
│   ├── calculate_stage_duration.sql
│   ├── calculate_occupancy_rate.sql
│   └── unify_platform_data.sql
├── tests/
│   └── schema.yml (5+ tests)
├── data/
│   └── day09_property_operations.db
├── day09_DATA_synthetic_generator.py
├── day09_CONFIG_settings.py
├── .env.example
├── LICENSE (MIT with commercial restriction)
├── README.md (PUBLIC - portfolio focus)
└── PRIVATE_PRODUCT_NOTES.md (LOCAL ONLY - not in git)
```

---

## 📖 Documentation Requirements

### **PUBLIC README Structure (day09/README.md)**

**Purpose:** Portfolio demonstration
**Audience:** Recruiters, hiring managers, data engineering community
**Tone:** Educational, technical, portfolio-focused

**Required Sections:**
```markdown
# Day 9: Multi-Platform Property Management Data Warehouse

## Business Problem
Independent property managers use multiple booking platforms (Airbnb, Booking.com)
but lack unified analytics. This project demonstrates data unification techniques
and dbt best practices for building a production-ready data warehouse.

## Technical Architecture
[Explain dbt project structure, incremental models, multi-platform unification strategy]

## Key Features Demonstrated
- Multi-source data integration (Airbnb + Booking.com)
- Incremental processing for efficient updates
- Custom business logic macros (occupancy, ADR, stage duration)
- Source freshness monitoring
- Comprehensive dbt testing strategy

## Data Models

### Staging Layer
[Describe source declarations and initial transformations]

### Intermediate Layer
[Explain platform unification logic]

### Marts Layer
[Document final business-ready models]

## Metrics Delivered
- Occupancy Rate (nights booked / nights available)
- Average Daily Rate (ADR)
- Revenue Per Available Room (RevPAR)
- Funnel conversion rates (inquiry → review)
- Platform performance comparison

## How to Run Locally
[Step-by-step setup instructions]

## Architecture Decisions

### Why Incremental Models?
[Explain: production-ready pattern, efficient processing, scalable]

### Multi-Platform Unification Strategy
[Explain: common schema, platform tracking, unified metrics]

## Learning Outcomes
- dbt project architecture
- Incremental materialization patterns
- Custom macro development
- Multi-source data integration
- Hospitality industry metrics

---
Built as part of a 25-day data engineering portfolio project
```

**❌ DO NOT INCLUDE in Public README:**
- MicroSaaS vision or product plans
- Commercial opportunity mentions
- MVP or "Phase 1/2/3" language
- Pricing model considerations
- Competitive analysis (Guesty/Hostaway)
- Production migration plans (SQLite → Supabase)

---

### **PRIVATE PRODUCT NOTES Structure (day09/PRIVATE_PRODUCT_NOTES.md)**

**Purpose:** Internal product development documentation
**Audience:** Only you (and future co-founders/investors)
**Location:** Keep local, add to .gitignore

**Required Sections:**
```markdown
# Day 9: Property Manager Data Warehouse - Product Context

## MicroSaaS Vision (CONFIDENTIAL)

### Target Market
- Independent property managers (1-15 properties)
- Currently underserved by enterprise PMS (Guesty charges $30-50/property/month)
- Need unified analytics across Airbnb + Booking.com
- Jo (6 houseboats) = first real user / design partner

### Product Roadmap
**Phase 1 (MVP):** Portfolio Builder
- Public-facing property showcase page
- Unified availability calendar
- Performance metrics dashboard
- Powered by: metrics_portfolio_public.sql

**Phase 2:** Direct Booking Engine
- iCal sync with Airbnb/Booking.com
- Direct booking flow (bypass platform fees)
- Payment processing integration

**Phase 3:** Operations Automation
- Automated guest messages
- Cleaning/maintenance scheduling
- Dynamic pricing suggestions

### How This dbt Project Supports the SaaS

#### Tables → SaaS Features Mapping
- `fct_reservations_unified` → Calendar sync + availability management
- `metrics_portfolio_public` → Public portfolio page (Phase 1 MVP)
- `dim_platform_comparison` → Platform performance analytics
- `fct_funnel_conversion` → Conversion optimization insights

#### Production Migration Path
- **Current:** SQLite (portfolio demonstration)
- **Phase 1 Production:** Supabase (Postgres + Auth + Storage)
- **Migration Strategy:** dbt profiles.yml switch, no code changes needed
- **Timeline:** 2 days after first paying customer

### Competitive Analysis
**vs. Guesty ($30-50/property/month):**
- Guesty: Enterprise-focused, complex, expensive for small operators
- Us: Lightweight, affordable ($10-15/property/month), independent-host-focused

**vs. Hostaway ($25-35/property/month):**
- Hostaway: Good mid-market option, still pricey for 1-10 properties
- Us: Better pricing for micro-operators, simpler UX

### Technical Debt / Production Hardening Needed
- [ ] Add proper error handling in dbt models
- [ ] Implement data quality monitoring (Great Expectations)
- [ ] Add CI/CD for dbt runs (GitHub Actions)
- [ ] Set up incremental backfill strategy
- [ ] Migrate from SQLite to Supabase
- [ ] Add multi-tenancy (property_manager_id in all tables)
- [ ] Implement RBAC (owner vs guest access)

### Pricing Model (Initial Thinking)
- $10/property/month (base tier - analytics only)
- $15/property/month (pro tier - direct booking)
- $20/property/month (automation tier - messages/scheduling)
- Target: 100 properties by Month 6 = $1-2K MRR

### Next Steps After Portfolio Delivery
1. User interview with Jo (validate metrics, get feedback)
2. Design Figma mockups for portfolio page
3. Set up Supabase project
4. Migrate dbt to Supabase profiles
5. Build Next.js frontend for Phase 1 MVP
```

**🔒 CRITICAL:** This file NEVER goes on GitHub. Keep local only.

---

## 💻 Code Examples

### **dbt Project Configuration**

```yaml
# dbt_project.yml
name: 'day09_property_ops'
profile: 'day09_property_ops'
version: '1.0.0'

models:
  day09_property_ops:
    staging:
      +materialized: view
      +tags: ['staging']
    intermediate:
      +materialized: view
      +tags: ['intermediate']
    marts:
      +materialized: table
      +tags: ['marts']
      fct_funnel_conversion:
        +materialized: incremental
        +unique_key: 'day09_event_id'
```

---

### **Staging: Multi-Platform Sources**

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: day09_airbnb
    database: day09_property_operations
    schema: raw
    tables:
      - name: airbnb_inquiries
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
      - name: airbnb_bookings
        freshness:
          warn_after: {count: 6, period: hour}
          error_after: {count: 12, period: hour}

  - name: day09_booking_com
    database: day09_property_operations
    schema: raw
    tables:
      - name: booking_com_inquiries
        freshness:
          warn_after: {count: 12, period: hour}
      - name: booking_com_bookings
        freshness:
          warn_after: {count: 6, period: hour}

  - name: day09_operations
    database: day09_property_operations
    schema: raw
    tables:
      - name: stays
      - name: reviews
```

```sql
-- models/staging/stg_airbnb_inquiries.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day09_airbnb', 'airbnb_inquiries') }}
),

renamed AS (
    SELECT
        inquiry_id AS day09_inquiry_id,
        'airbnb' AS day09_platform,
        guest_id AS day09_guest_id,
        property_id AS day09_property_id,
        inquiry_timestamp AS day09_inquiry_timestamp,
        check_in_date AS day09_check_in_date,
        check_out_date AS day09_check_out_date,
        num_guests AS day09_num_guests,
        status AS day09_status
    FROM source
)

SELECT * FROM renamed
```

```sql
-- models/staging/stg_booking_com_inquiries.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day09_booking_com', 'booking_com_inquiries') }}
),

renamed AS (
    SELECT
        reservation_inquiry_id AS day09_inquiry_id,
        'booking_com' AS day09_platform,
        guest_email AS day09_guest_id,  -- Unification: use email as guest_id
        property_code AS day09_property_id,
        created_at AS day09_inquiry_timestamp,
        arrival_date AS day09_check_in_date,
        departure_date AS day09_check_out_date,
        guest_count AS day09_num_guests,
        inquiry_status AS day09_status
    FROM source
)

SELECT * FROM renamed
```

---

### **Intermediate: Platform Unification**

```sql
-- models/intermediate/int_unified_reservations.sql
{{ config(materialized='view') }}

WITH airbnb AS (
    SELECT * FROM {{ ref('stg_airbnb_bookings') }}
),

booking_com AS (
    SELECT * FROM {{ ref('stg_booking_com_bookings') }}
),

unified AS (
    SELECT
        day09_booking_id,
        day09_platform,
        day09_guest_id,
        day09_property_id,
        day09_check_in_date,
        day09_check_out_date,
        day09_num_guests,
        day09_total_price,
        day09_platform_fee,
        day09_net_revenue,
        day09_booking_timestamp,
        day09_status
    FROM airbnb

    UNION ALL

    SELECT
        day09_booking_id,
        day09_platform,
        day09_guest_id,
        day09_property_id,
        day09_check_in_date,
        day09_check_out_date,
        day09_num_guests,
        day09_total_price,
        day09_platform_fee,
        day09_net_revenue,
        day09_booking_timestamp,
        day09_status
    FROM booking_com
)

SELECT
    *,
    DATEDIFF(day, day09_check_in_date, day09_check_out_date) AS day09_nights,
    day09_total_price / NULLIF(DATEDIFF(day, day09_check_in_date, day09_check_out_date), 0) AS day09_adr
FROM unified
```

---

### **Marts: Incremental Funnel Conversion**

```sql
-- models/marts/fct_funnel_conversion.sql
{{
  config(
    materialized='incremental',
    unique_key='day09_event_id',
    on_schema_change='append_new_columns'
  )
}}

WITH funnel_events AS (
    SELECT * FROM {{ ref('int_funnel_events') }}
)

SELECT
    day09_event_id,
    day09_guest_id,
    day09_property_id,
    day09_platform,
    day09_stage,
    day09_event_timestamp,
    {{ calculate_stage_duration('day09_event_timestamp', 'day09_stage', 'day09_guest_id') }} AS day09_time_in_stage_hours,
    day09_converted_to_next_stage,
    day09_final_booking_value
FROM funnel_events

{% if is_incremental() %}
  WHERE day09_event_timestamp > (SELECT MAX(day09_event_timestamp) FROM {{ this }})
{% endif %}
```

---

### **Marts: Portfolio Metrics (Powers Public Page)**

```sql
-- models/marts/metrics_portfolio_public.sql
{{ config(materialized='table') }}

WITH reservations AS (
    SELECT * FROM {{ ref('fct_reservations_unified') }}
),

property_nights AS (
    SELECT
        day09_property_id,
        COUNT(*) AS day09_total_nights_booked,
        SUM(day09_total_price) AS day09_total_revenue,
        SUM(day09_net_revenue) AS day09_total_net_revenue,
        AVG(day09_adr) AS day09_avg_daily_rate
    FROM reservations
    WHERE day09_status = 'completed'
    GROUP BY day09_property_id
),

-- Calculate available nights (365 days per property for portfolio demo)
property_metrics AS (
    SELECT
        pn.day09_property_id,
        pn.day09_total_nights_booked,
        365 AS day09_nights_available,  -- Simplified for portfolio
        ROUND(100.0 * pn.day09_total_nights_booked / 365, 2) AS day09_occupancy_rate_pct,
        pn.day09_avg_daily_rate,
        ROUND(pn.day09_avg_daily_rate * (pn.day09_total_nights_booked / 365.0), 2) AS day09_revpar,
        pn.day09_total_revenue,
        pn.day09_total_net_revenue
    FROM property_nights pn
)

SELECT * FROM property_metrics
```

---

### **Custom Macros**

```sql
-- macros/calculate_stage_duration.sql
{% macro calculate_stage_duration(timestamp_col, stage_col, partition_col) %}
    TIMESTAMPDIFF(
        HOUR,
        LAG({{ timestamp_col }}) OVER (
            PARTITION BY {{ partition_col }}, {{ stage_col }}
            ORDER BY {{ timestamp_col }}
        ),
        {{ timestamp_col }}
    )
{% endmacro %}
```

```sql
-- macros/calculate_occupancy_rate.sql
{% macro calculate_occupancy_rate(nights_booked_col, nights_available_col) %}
    ROUND(100.0 * {{ nights_booked_col }} / NULLIF({{ nights_available_col }}, 0), 2)
{% endmacro %}
```

```sql
-- macros/unify_platform_data.sql
{% macro unify_platform_data(airbnb_col, booking_com_col, airbnb_default, booking_com_default) %}
    CASE
        WHEN platform = 'airbnb' THEN COALESCE({{ airbnb_col }}, {{ airbnb_default }})
        WHEN platform = 'booking_com' THEN COALESCE({{ booking_com_col }}, {{ booking_com_default }})
        ELSE NULL
    END
{% endmacro %}
```

---

### **dbt Tests**

```yaml
# tests/schema.yml
version: 2

models:
  - name: stg_airbnb_inquiries
    columns:
      - name: day09_inquiry_id
        tests:
          - unique
          - not_null
      - name: day09_platform
        tests:
          - accepted_values:
              values: ['airbnb', 'booking_com']

  - name: fct_reservations_unified
    columns:
      - name: day09_booking_id
        tests:
          - unique
          - not_null
      - name: day09_property_id
        tests:
          - not_null
      - name: day09_platform
        tests:
          - accepted_values:
              values: ['airbnb', 'booking_com']
      - name: day09_adr
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "> 0"

  - name: metrics_portfolio_public
    columns:
      - name: day09_property_id
        tests:
          - unique
          - not_null
      - name: day09_occupancy_rate_pct
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "BETWEEN 0 AND 100"
```

---

## 🎯 Complexity Assessment

- **dbt Complexity:** High (incremental models, multi-source unification, custom macros)
- **Business Logic:** High (hospitality metrics, multi-platform reconciliation)
- **Data Volume:** 500+ reservations, 12 months history, 2 platforms
- **Time Estimate:** 3h (dbt setup 30min, models 90min, testing/docs 60min)

---

## ✅ Final Validation

```bash
# Navigate to project
cd day09

# Full refresh (builds from scratch)
dbt run --full-refresh

# Incremental run (only new data)
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Validate key metrics
sqlite3 data/day09_property_operations.db "SELECT * FROM metrics_portfolio_public;"
sqlite3 data/day09_property_operations.db "SELECT * FROM fct_funnel_conversion ORDER BY day09_event_timestamp DESC LIMIT 10;"
```

**Success Criteria:**
- ✅ All dbt models run without errors
- ✅ Incremental model only processes new events on second run
- ✅ Occupancy rates between 0-100%
- ✅ ADR and RevPAR values are realistic ($50-300/night range)
- ✅ Platform unification works (Airbnb + Booking.com in same tables)
- ✅ 5+ tests passing
- ✅ Public README is portfolio-focused (no commercial mentions)
- ✅ Private notes contain strategic context
- ✅ LICENSE file included with commercial restriction

---

## 🔐 Pre-Commit Checklist

**Before pushing to GitHub:**
- [ ] `PRIVATE_PRODUCT_NOTES.md` is in `.gitignore`
- [ ] No mentions of "MicroSaaS", "MVP", "product roadmap" in public README
- [ ] LICENSE file includes commercial use restriction
- [ ] All code uses `day09_` prefix consistently
- [ ] dbt docs generated and models documented
- [ ] Tests passing (`dbt test`)
- [ ] Public README focuses on portfolio/learning objectives only
- [ ] No business model, pricing, or competitive analysis in public files

---

## 📊 Naming Examples

```python
# ✅ CORRECT
DAY09_DB_PATH = "data/day09_property_operations.db"
DAY09_PLATFORMS = ['airbnb', 'booking_com']
DAY09_FUNNEL_STAGES = ['inquiry', 'booking', 'check_in', 'check_out', 'review']

class day09_PropertyDataGenerator:
    pass

def day09_calculate_occupancy_rate():
    pass

# ❌ WRONG - Generic names cause conflicts
DB_PATH = "data/database.db"
class PropertyGenerator:  # Too generic
```

```sql
-- ✅ CORRECT (dbt models)
CREATE VIEW day09_stg_airbnb_inquiries AS ...
CREATE TABLE day09_fct_reservations_unified AS ...

-- ❌ WRONG
CREATE VIEW stg_inquiries AS ...  -- Too generic
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
