# Day 16: Metabase SQL Queries

## Dashboard Structure: 4 Sections, 6+ Cards

This document contains all SQL queries needed for Murilo's SaaS Health Metrics Dashboard.

**Decision Context**: Help Murilo identify which customer cohorts show declining retention and need proactive intervention THIS MONTH.

---

## SECTION 1: Business Health Baseline (4 Cards)

### Card 1.1: Current MRR (Metric Card)
**Purpose**: Executive KPI - Current Monthly Recurring Revenue

```sql
SELECT
  ROUND(total_mrr, 2) as current_mrr
FROM `PROJECT_ID.day16_saas_metrics.day06_dashboard_kpis`
```

**Metabase Card Settings**:
- Visualization: Number
- Display: Currency (USD)
- Title: "Current MRR"

---

### Card 1.2: Churn Rate (Metric Card)
**Purpose**: Executive KPI - Current churn percentage

```sql
SELECT
  ROUND(churn_rate * 100, 2) as churn_rate_pct
FROM `PROJECT_ID.day16_saas_metrics.day06_dashboard_kpis`
```

**Metabase Card Settings**:
- Visualization: Number
- Display: Percentage
- Title: "Churn Rate (%)"
- Color: Red if > 5%, Yellow if 3-5%, Green if < 3%

---

### Card 1.3: Active Customers (Metric Card)
**Purpose**: Executive KPI - Total active customer count

```sql
SELECT
  active_customers
FROM `PROJECT_ID.day16_saas_metrics.day06_dashboard_kpis`
```

**Metabase Card Settings**:
- Visualization: Number
- Display: Integer
- Title: "Active Customers"

---

### Card 1.4: LTV/CAC Ratio (Metric Card)
**Purpose**: Executive KPI - Customer acquisition efficiency

```sql
SELECT
  ROUND(ltv_cac_ratio, 2) as ltv_cac_ratio
FROM `PROJECT_ID.day16_saas_metrics.day06_dashboard_kpis`
```

**Metabase Card Settings**:
- Visualization: Number
- Display: Decimal (2 places)
- Title: "LTV/CAC Ratio"
- Color: Green if > 3.0, Yellow if 2-3, Red if < 2

---

## SECTION 2: Growth Trajectory (2 Cards)

### Card 2.1: MRR Growth Over Time (Stacked Area Chart)
**Purpose**: Shows MRR composition - new, expansion, contraction, churn

```sql
SELECT
  month,
  ROUND(new_mrr, 2) as new_mrr,
  ROUND(expansion_mrr, 2) as expansion_mrr,
  ROUND(contraction_mrr, 2) as contraction_mrr,
  ROUND(churned_mrr, 2) as churned_mrr,
  ROUND(net_mrr, 2) as net_mrr
FROM `PROJECT_ID.day16_saas_metrics.day06_mrr_summary`
ORDER BY month ASC
```

**Metabase Card Settings**:
- Visualization: Area Chart (Stacked)
- X-axis: month (Date)
- Y-axis: MRR components
- Series: new_mrr, expansion_mrr, contraction_mrr (negative), churned_mrr (negative)
- Add line overlay: net_mrr
- Title: "MRR Waterfall - New + Expansion - Contraction - Churn"
- Colors:
  - New: Green
  - Expansion: Light Green
  - Contraction: Orange
  - Churn: Red

---

### Card 2.2: Month-over-Month Growth Rate (Line Chart)
**Purpose**: Shows growth velocity trend

```sql
SELECT
  month,
  ROUND(growth_rate * 100, 2) as growth_rate_pct
FROM `PROJECT_ID.day16_saas_metrics.day06_mrr_summary`
ORDER BY month ASC
```

**Metabase Card Settings**:
- Visualization: Line Chart
- X-axis: month
- Y-axis: growth_rate_pct
- Add reference line: 0% (horizontal)
- Title: "MoM Growth Rate (%)"
- Color: Green if positive, Red if negative

---

## SECTION 3: Cohort Patterns (2 Cards) - PRIMARY DECISION VISUAL

### Card 3.1: Cohort Retention Curves (Line Chart - MOST IMPORTANT)
**Purpose**: PRIMARY DECISION VISUAL - Shows which cohorts have declining retention

```sql
SELECT
  cohort_month,
  months_since_signup,
  ROUND(retention_rate_pct, 2) as retention_rate_pct
FROM `PROJECT_ID.day16_saas_metrics.day06_retention_curves`
WHERE months_since_signup <= 12  -- Focus on first year
ORDER BY cohort_month ASC, months_since_signup ASC
```

**Metabase Card Settings**:
- Visualization: Line Chart (Multi-series)
- X-axis: months_since_signup (0-12)
- Y-axis: retention_rate_pct (0-100%)
- Series: One line per cohort_month
- Add reference line: 50% retention (SaaS benchmark)
- Title: "Cohort Retention Curves (12-Month View)"
- Subtitle: "Each line = one signup cohort. Identify declining curves."
- Y-axis range: 0-100%
- Enable legend: Show cohort months

**Analysis Guide for Murilo**:
- Steep drops = churn happening fast (onboarding issue?)
- Gradual decline = slow churn (product value degradation?)
- Compare recent cohorts vs older ones = product improvements working?

---

### Card 3.2: Churn Heatmap by Cohort × Plan Tier (Pivot Table)
**Purpose**: Identify which plan tiers + cohorts have highest churn risk

```sql
SELECT
  cohort_month,
  plan_tier,
  ROUND(churn_rate * 100, 2) as churn_rate_pct,
  churned_customers,
  cohort_size
FROM `PROJECT_ID.day16_saas_metrics.day06_churn_by_cohort`
WHERE cohort_size > 5  -- Filter out small cohorts for statistical significance
ORDER BY cohort_month ASC, plan_tier ASC
```

**Metabase Card Settings**:
- Visualization: Pivot Table
- Rows: cohort_month
- Columns: plan_tier
- Values: churn_rate_pct
- Color gradient: White (0%) → Red (100%)
- Title: "Churn Rate Heatmap: Cohort × Plan Tier"
- Subtitle: "Red = high churn. Which plan tiers need attention?"

---

## SECTION 4: Customer Health Alerts (2 Cards)

### Card 4.1: At-Risk Customer Distribution (Pie Chart)
**Purpose**: Show proportion of customers by health status

```sql
SELECT
  health_status,
  COUNT(*) as customer_count
FROM `PROJECT_ID.day16_saas_metrics.day06_customer_health`
GROUP BY health_status
ORDER BY customer_count DESC
```

**Metabase Card Settings**:
- Visualization: Pie Chart
- Dimension: health_status
- Metric: customer_count
- Title: "Customer Health Distribution"
- Colors:
  - Healthy: Green
  - At Risk: Yellow
  - Critical: Red

---

### Card 4.2: Top 10 Critical Customers (Table)
**Purpose**: Actionable list - who to call TODAY

```sql
SELECT
  customer_id,
  ROUND(ltv, 2) as lifetime_value,
  ROUND(health_score, 2) as health_score,
  health_status,
  days_since_last_activity,
  risk_reason
FROM `PROJECT_ID.day16_saas_metrics.day06_customer_health`
WHERE health_status = 'Critical'
ORDER BY ltv DESC
LIMIT 10
```

**Metabase Card Settings**:
- Visualization: Table
- Title: "Top 10 Critical Customers (by LTV)"
- Subtitle: "High-value customers at risk - prioritize outreach"
- Sort: LTV descending
- Conditional formatting:
  - health_score < 30: Red background
  - days_since_last_activity > 30: Bold

---

## BONUS CARDS (Optional - if time permits)

### Bonus: Net Revenue Retention (NRR) Trend
**Purpose**: Track expansion vs churn over time

```sql
SELECT
  month,
  ROUND(
    (new_mrr + expansion_mrr - contraction_mrr - churned_mrr) /
    LAG(net_mrr, 1) OVER (ORDER BY month) * 100,
    2
  ) as nrr_pct
FROM `PROJECT_ID.day16_saas_metrics.day06_mrr_summary`
ORDER BY month ASC
```

**Metabase Card Settings**:
- Visualization: Line Chart
- Title: "Net Revenue Retention (NRR) Trend"
- Add reference line: 100% (retention breakeven)

---

### Bonus: Average Revenue Per Account (ARPA) by Plan Tier

```sql
SELECT
  plan_tier,
  ROUND(AVG(mrr), 2) as avg_mrr,
  COUNT(*) as customer_count
FROM `PROJECT_ID.day16_saas_metrics.day06_subscriptions`
WHERE end_date IS NULL  -- Active subscriptions only
GROUP BY plan_tier
ORDER BY avg_mrr DESC
```

**Metabase Card Settings**:
- Visualization: Bar Chart
- Title: "ARPA by Plan Tier"

---

## Dashboard Assembly Guide

### Layout Recommendation (Metabase Grid):

```
+------------------+------------------+------------------+------------------+
| 1.1 Current MRR  | 1.2 Churn Rate   | 1.3 Active Cust. | 1.4 LTV/CAC     |
| (Metric)         | (Metric)         | (Metric)         | (Metric)        |
+------------------+------------------+------------------+------------------+
|                  2.1 MRR Growth Over Time (Stacked Area)                 |
|                                                                           |
+------------------------------------------------------------------+-------+
|                  2.2 MoM Growth Rate (Line Chart)                |       |
|                                                                  |       |
+------------------------------------------------------------------+-------+
|                  3.1 COHORT RETENTION CURVES (PRIMARY VISUAL)            |
|                           (Line Chart - Multi-series)                     |
|                                                                           |
+------------------------------------------------------------------+-------+
|                  3.2 Churn Heatmap: Cohort × Plan Tier                   |
|                           (Pivot Table)                                   |
+------------------------------------------------------------------+-------+
| 4.1 Customer Health    |    4.2 Top 10 Critical Customers (Table)        |
| Distribution (Pie)     |                                                  |
+------------------------+--------------------------------------------------+
```

---

## Time-Saving Tips

### Using Metabase Filters:
Add a dashboard-level filter for date range:

```sql
-- Modify queries to include WHERE clause:
WHERE month >= {{start_date}} AND month <= {{end_date}}
```

### Quick Testing:
Run each query in BigQuery console first to verify results before creating Metabase cards.

```bash
# Test in BigQuery:
bq query --use_legacy_sql=false --project_id=YOUR_PROJECT_ID "
SELECT * FROM \`YOUR_PROJECT_ID.day16_saas_metrics.day06_dashboard_kpis\`
"
```

---

## Query Performance Notes

All queries are optimized for Metabase Cloud:
- ✅ No subqueries (faster execution)
- ✅ Pre-aggregated data (Day 6 tables already computed)
- ✅ Simple JOINs avoided where possible
- ✅ ROUND() for clean display
- ✅ Explicit column names (no SELECT *)

Expected query execution time: <2 seconds per card

---

## Validation Checklist

Before finalizing dashboard, verify:

- [ ] Card 1.1: MRR value is realistic ($10K-$100K range)
- [ ] Card 1.2: Churn rate between 2-8%
- [ ] Card 3.1: Retention curves start at 100% (month 0)
- [ ] Card 3.1: Retention curves show downward trend (realistic churn)
- [ ] Card 2.1: MRR waterfall balances (New + Exp - Cont - Churn = Net)
- [ ] Card 4.2: Critical customers table has data

---

## Replace PROJECT_ID

**IMPORTANT**: Replace `PROJECT_ID` in all queries with your actual GCP project ID.

Quick find/replace in Metabase:
- Find: `PROJECT_ID.day16_saas_metrics`
- Replace: `your-actual-project-id.day16_saas_metrics`

---

Built for Christmas Data Advent 2025 - Day 16 (Project 4A)
Stakeholder: Murilo (SaaS Founder - Simetryk)
Tool: Metabase Cloud + BigQuery
