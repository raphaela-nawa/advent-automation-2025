-- ============================================================================
-- Day 06: SaaS Health Metrics Foundation - Analytical Views
-- ============================================================================
--
-- Stakeholder: SaaS Executive (C-level)
-- Purpose: Create 4 analytical views ready for dashboard consumption (Day 19)
--
-- Views:
--   1. day06_mrr_summary - MRR waterfall (New, Expansion, Contraction, Churn)
--   2. day06_churn_by_cohort - Churn rate by signup month and segment
--   3. day06_retention_curves - Cohort-based retention analysis
--   4. day06_customer_health - LTV/CAC and health scoring
--
-- Usage:
--   sqlite3 data/day06_saas_metrics.db < models/day06_MODEL_views.sql
--
-- ============================================================================

-- Drop existing views if they exist
DROP VIEW IF EXISTS day06_customer_health;
DROP VIEW IF EXISTS day06_retention_curves;
DROP VIEW IF EXISTS day06_churn_by_cohort;
DROP VIEW IF EXISTS day06_mrr_summary;

-- ============================================================================
-- View 1: day06_mrr_summary
-- ============================================================================
--
-- Purpose: MRR Waterfall Chart - Shows monthly MRR movements
--
-- Business Logic:
-- - Simply exposes the pre-calculated mrr_movements table
-- - Shows: New MRR + Expansion MRR - Contraction MRR - Churn MRR = Net MRR
--
-- Dashboard Integration (Day 19):
-- - Chart Type: Waterfall chart
-- - X-axis: month
-- - Y-axes: new_mrr, expansion_mrr, contraction_mrr, churn_mrr, net_mrr
-- - Visualization: Stack bars showing MRR composition
--
CREATE VIEW day06_mrr_summary AS
WITH monthly_data AS (
    SELECT
        month,
        ROUND(new_mrr, 2) as new_mrr,
        ROUND(expansion_mrr, 2) as expansion_mrr,
        ROUND(contraction_mrr, 2) as contraction_mrr,
        ROUND(churn_mrr, 2) as churn_mrr,
        ROUND(net_mrr, 2) as net_mrr,
        -- Cumulative MRR (running total)
        ROUND(SUM(net_mrr) OVER (
            ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) as cumulative_mrr
    FROM day06_mrr_movements
)
SELECT
    month,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churn_mrr,
    net_mrr,
    cumulative_mrr,
    -- Month-over-month growth rate (based on previous cumulative)
    CASE
        WHEN LAG(cumulative_mrr) OVER (ORDER BY month) IS NULL THEN NULL
        WHEN LAG(cumulative_mrr) OVER (ORDER BY month) = 0 THEN NULL
        ELSE ROUND(100.0 * net_mrr / LAG(cumulative_mrr) OVER (ORDER BY month), 2)
    END as mom_growth_rate_pct
FROM monthly_data
ORDER BY month;

-- ============================================================================
-- View 2: day06_churn_by_cohort
-- ============================================================================
--
-- Purpose: Churn Analysis - Churn rate by signup cohort and plan tier
--
-- Business Logic:
-- - Cohort = Month of first signup (YYYY-MM format)
-- - Churn Rate = (Churned Customers / Total Customers) * 100
-- - Segmented by plan tier (Starter/Pro/Enterprise)
--
-- Dashboard Integration (Day 19):
-- - Chart Type: Heatmap
-- - Rows: cohort_month
-- - Columns: plan_tier
-- - Color: churn_rate_pct (darker = higher churn)
--
CREATE VIEW day06_churn_by_cohort AS
SELECT
    -- Extract YYYY-MM from signup_date for cohort grouping
    strftime('%Y-%m', signup_date) as cohort_month,
    plan_tier,
    COUNT(*) as cohort_size,
    SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) as churned_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
    ROUND(100.0 * SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) / COUNT(*), 2) as churn_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) / COUNT(*), 2) as retention_rate_pct
FROM day06_customers
GROUP BY strftime('%Y-%m', signup_date), plan_tier
ORDER BY cohort_month, plan_tier;

-- ============================================================================
-- View 3: day06_retention_curves
-- ============================================================================
--
-- Purpose: Cohort Retention Curves - Track how cohorts retain over time
--
-- Business Logic:
-- - For each signup cohort, track % of customers still active N months later
-- - months_since_signup = 0 means signup month (100% retention by definition)
-- - months_since_signup = 6 means 6 months after signup
--
-- Dashboard Integration (Day 19):
-- - Chart Type: Line chart
-- - X-axis: months_since_signup
-- - Y-axis: retention_rate_pct
-- - Series: Different lines for each cohort_month
--
CREATE VIEW day06_retention_curves AS
WITH cohort_base AS (
    -- Identify cohort for each customer
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month,
        signup_date,
        status
    FROM day06_customers
),
subscription_activity AS (
    -- Get all subscription activity per customer
    SELECT
        cb.customer_id,
        cb.cohort_month,
        cb.signup_date,
        cb.status,
        s.start_date,
        s.end_date,
        -- Calculate which month this subscription was active in
        strftime('%Y-%m', s.start_date) as activity_month
    FROM cohort_base cb
    JOIN day06_subscriptions s ON cb.customer_id = s.customer_id
),
monthly_retention AS (
    -- For each cohort and month, count active customers
    SELECT
        cohort_month,
        activity_month,
        -- Calculate months since signup
        CAST(
            (CAST(strftime('%Y', activity_month) AS INTEGER) - CAST(strftime('%Y', cohort_month) AS INTEGER)) * 12 +
            (CAST(strftime('%m', activity_month) AS INTEGER) - CAST(strftime('%m', cohort_month) AS INTEGER))
        AS INTEGER) as months_since_signup,
        COUNT(DISTINCT customer_id) as active_customers
    FROM subscription_activity
    GROUP BY cohort_month, activity_month
),
cohort_sizes AS (
    -- Get the initial size of each cohort (month 0)
    SELECT
        cohort_month,
        COUNT(*) as cohort_size
    FROM cohort_base
    GROUP BY cohort_month
)
SELECT
    mr.cohort_month,
    mr.months_since_signup,
    mr.active_customers as retained_customers,
    cs.cohort_size,
    ROUND(100.0 * mr.active_customers / cs.cohort_size, 2) as retention_rate_pct
FROM monthly_retention mr
JOIN cohort_sizes cs ON mr.cohort_month = cs.cohort_month
WHERE mr.months_since_signup >= 0  -- Only show from signup month onwards
ORDER BY mr.cohort_month, mr.months_since_signup;

-- ============================================================================
-- View 4: day06_customer_health
-- ============================================================================
--
-- Purpose: Customer Health Scoring - LTV/CAC analysis and health status
--
-- Business Logic:
-- - LTV (Lifetime Value) = MRR * Customer Age in Months (simplified)
-- - CAC (Customer Acquisition Cost) = Assumed $500 per customer
-- - LTV/CAC Ratio:
--     > 3.0 = Healthy (good unit economics)
--     1.0 - 3.0 = At Risk (marginal unit economics)
--     < 1.0 = Critical (losing money)
-- - Churned customers are always marked as "Churned" regardless of LTV/CAC
--
-- Dashboard Integration (Day 19):
-- - Chart Type: Pie chart showing distribution by health_status
-- - Table: Top customers by ltv_cac_ratio
--
CREATE VIEW day06_customer_health AS
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.email,
        c.signup_date,
        c.plan_tier,
        c.mrr_current,
        c.status,
        -- Calculate customer age in months
        CAST(
            (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(strftime('%Y', c.signup_date) AS INTEGER)) * 12 +
            (CAST(strftime('%m', 'now') AS INTEGER) - CAST(strftime('%m', c.signup_date) AS INTEGER))
        AS INTEGER) as customer_age_months,
        -- LTV Estimate: MRR * Age in Months (simplified lifetime value)
        c.mrr_current * CAST(
            (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(strftime('%Y', c.signup_date) AS INTEGER)) * 12 +
            (CAST(strftime('%m', 'now') AS INTEGER) - CAST(strftime('%m', c.signup_date) AS INTEGER))
        AS INTEGER) as ltv_estimate
    FROM day06_customers c
)
SELECT
    customer_id,
    email,
    plan_tier,
    signup_date,
    ROUND(mrr_current, 2) as mrr_current,
    customer_age_months,
    ROUND(ltv_estimate, 2) as ltv_estimate,
    -- Assumed CAC of $500 per customer (industry average for SaaS)
    500.0 as cac_assumed,
    -- LTV/CAC Ratio
    ROUND(ltv_estimate / 500.0, 2) as ltv_cac_ratio,
    -- Health Status Classification
    CASE
        WHEN status = 'churned' THEN 'Churned'
        WHEN ltv_estimate / 500.0 >= 3.0 THEN 'Healthy'
        WHEN ltv_estimate / 500.0 >= 1.0 THEN 'At Risk'
        ELSE 'Critical'
    END as health_status,
    status as customer_status
FROM customer_metrics
ORDER BY ltv_cac_ratio DESC;

-- ============================================================================
-- Summary View: Dashboard Overview
-- ============================================================================
--
-- Purpose: High-level KPIs for dashboard homepage
--
CREATE VIEW day06_dashboard_kpis AS
SELECT
    -- Current MRR (from latest month)
    (SELECT ROUND(SUM(net_mrr), 2) FROM day06_mrr_movements) as total_mrr_growth,
    (SELECT ROUND(SUM(mrr_current), 2) FROM day06_customers WHERE status = 'active') as current_mrr,
    -- Customer counts
    (SELECT COUNT(*) FROM day06_customers WHERE status = 'active') as active_customers,
    (SELECT COUNT(*) FROM day06_customers WHERE status = 'churned') as churned_customers,
    (SELECT ROUND(100.0 * COUNT(CASE WHEN status = 'churned' THEN 1 END) / COUNT(*), 2)
     FROM day06_customers) as overall_churn_rate_pct,
    -- MRR by plan tier
    (SELECT ROUND(SUM(mrr_current), 2) FROM day06_customers WHERE status = 'active' AND plan_tier = 'Starter') as starter_mrr,
    (SELECT ROUND(SUM(mrr_current), 2) FROM day06_customers WHERE status = 'active' AND plan_tier = 'Pro') as pro_mrr,
    (SELECT ROUND(SUM(mrr_current), 2) FROM day06_customers WHERE status = 'active' AND plan_tier = 'Enterprise') as enterprise_mrr,
    -- Health distribution
    (SELECT COUNT(*) FROM day06_customer_health WHERE health_status = 'Healthy') as healthy_customers,
    (SELECT COUNT(*) FROM day06_customer_health WHERE health_status = 'At Risk') as at_risk_customers,
    (SELECT COUNT(*) FROM day06_customer_health WHERE health_status = 'Critical') as critical_customers;

-- ============================================================================
-- End of Analytical Views
-- ============================================================================

-- To validate views, run:
-- SELECT * FROM day06_mrr_summary LIMIT 5;
-- SELECT * FROM day06_churn_by_cohort LIMIT 10;
-- SELECT * FROM day06_retention_curves WHERE cohort_month = '2023-01' LIMIT 10;
-- SELECT * FROM day06_customer_health ORDER BY ltv_cac_ratio DESC LIMIT 10;
-- SELECT * FROM day06_dashboard_kpis;
