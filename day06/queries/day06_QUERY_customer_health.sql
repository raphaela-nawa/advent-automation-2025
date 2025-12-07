-- ============================================================================
-- Day 06: Customer Health Analysis Query
-- ============================================================================
--
-- Purpose: Analyze customer health based on LTV/CAC ratio
-- Stakeholder: SaaS Executive (C-level)
-- Dashboard: Day 19 - Customer Health Distribution
--
-- Usage:
--   sqlite3 data/day06_saas_metrics.db < queries/day06_QUERY_customer_health.sql
--
-- ============================================================================

-- Query 1: Top customers by LTV/CAC ratio
-- ============================================================================
SELECT
    customer_id,
    email,
    plan_tier,
    signup_date,
    mrr_current,
    customer_age_months,
    ltv_estimate,
    ltv_cac_ratio,
    health_status
FROM day06_customer_health
WHERE customer_status = 'active'
ORDER BY ltv_cac_ratio DESC
LIMIT 20;

-- Query 2: Customer health distribution
-- ============================================================================
SELECT
    health_status,
    COUNT(*) as customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM day06_customer_health), 2) as pct_of_total,
    ROUND(SUM(mrr_current), 2) as total_mrr,
    ROUND(AVG(ltv_cac_ratio), 2) as avg_ltv_cac_ratio,
    ROUND(AVG(customer_age_months), 1) as avg_age_months
FROM day06_customer_health
GROUP BY health_status
ORDER BY
    CASE health_status
        WHEN 'Healthy' THEN 1
        WHEN 'At Risk' THEN 2
        WHEN 'Critical' THEN 3
        WHEN 'Churned' THEN 4
    END;

-- Query 3: Health status by plan tier
-- ============================================================================
SELECT
    plan_tier,
    health_status,
    COUNT(*) as customer_count,
    ROUND(AVG(mrr_current), 2) as avg_mrr,
    ROUND(AVG(ltv_cac_ratio), 2) as avg_ltv_cac_ratio
FROM day06_customer_health
GROUP BY plan_tier, health_status
ORDER BY plan_tier, health_status;

-- Query 4: At-risk customers requiring attention (LTV/CAC between 1-3)
-- ============================================================================
SELECT
    customer_id,
    email,
    plan_tier,
    signup_date,
    customer_age_months,
    ROUND(mrr_current, 2) as mrr_current,
    ROUND(ltv_cac_ratio, 2) as ltv_cac_ratio,
    CASE
        WHEN ltv_cac_ratio < 1.5 THEN 'High Priority'
        WHEN ltv_cac_ratio < 2.0 THEN 'Medium Priority'
        ELSE 'Low Priority'
    END as intervention_priority
FROM day06_customer_health
WHERE health_status = 'At Risk'
ORDER BY ltv_cac_ratio ASC, mrr_current DESC;

-- Query 5: Critical customers (LTV < CAC, losing money)
-- ============================================================================
SELECT
    customer_id,
    email,
    plan_tier,
    signup_date,
    customer_age_months,
    ROUND(mrr_current, 2) as mrr_current,
    ROUND(ltv_estimate, 2) as ltv_estimate,
    ROUND(ltv_cac_ratio, 2) as ltv_cac_ratio,
    ROUND(500.0 - ltv_estimate, 2) as ltv_shortfall
FROM day06_customer_health
WHERE health_status = 'Critical' AND customer_status = 'active'
ORDER BY ltv_cac_ratio ASC;

-- Query 6: MRR concentration by health status
-- ============================================================================
WITH health_mrr AS (
    SELECT
        health_status,
        SUM(mrr_current) as total_mrr
    FROM day06_customer_health
    GROUP BY health_status
)
SELECT
    health_status,
    ROUND(total_mrr, 2) as mrr,
    ROUND(100.0 * total_mrr / (SELECT SUM(total_mrr) FROM health_mrr), 2) as pct_of_total_mrr,
    CASE
        WHEN health_status = 'Healthy' AND
             100.0 * total_mrr / (SELECT SUM(total_mrr) FROM health_mrr) < 50 THEN 'Warning: Low healthy MRR'
        WHEN health_status IN ('At Risk', 'Critical') AND
             100.0 * total_mrr / (SELECT SUM(total_mrr) FROM health_mrr) > 30 THEN 'Alert: High risky MRR'
        ELSE 'Normal'
    END as risk_assessment
FROM health_mrr
ORDER BY total_mrr DESC;

-- Query 7: Customer lifetime analysis (average LTV by cohort age)
-- ============================================================================
SELECT
    CASE
        WHEN customer_age_months < 6 THEN '0-5 months'
        WHEN customer_age_months < 12 THEN '6-11 months'
        WHEN customer_age_months < 18 THEN '12-17 months'
        WHEN customer_age_months < 24 THEN '18-23 months'
        ELSE '24+ months'
    END as age_bucket,
    COUNT(*) as customer_count,
    ROUND(AVG(ltv_estimate), 2) as avg_ltv,
    ROUND(AVG(ltv_cac_ratio), 2) as avg_ltv_cac_ratio,
    ROUND(AVG(mrr_current), 2) as avg_current_mrr
FROM day06_customer_health
WHERE customer_status = 'active'
GROUP BY age_bucket
ORDER BY MIN(customer_age_months);

-- Query 8: Payback period analysis (months to recover CAC)
-- ============================================================================
SELECT
    customer_id,
    email,
    plan_tier,
    signup_date,
    ROUND(mrr_current, 2) as mrr_current,
    customer_age_months,
    -- Months needed to pay back $500 CAC
    CASE
        WHEN mrr_current > 0 THEN ROUND(500.0 / mrr_current, 1)
        ELSE NULL
    END as payback_months,
    CASE
        WHEN customer_age_months >= (500.0 / mrr_current) THEN 'Paid Back'
        ELSE 'Not Yet Paid Back'
    END as payback_status,
    ROUND(ltv_cac_ratio, 2) as current_ltv_cac_ratio
FROM day06_customer_health
WHERE customer_status = 'active' AND mrr_current > 0
ORDER BY payback_months ASC
LIMIT 20;

-- Query 9: Enterprise customer health (high-value segment)
-- ============================================================================
SELECT
    customer_id,
    email,
    signup_date,
    customer_age_months,
    ROUND(mrr_current, 2) as mrr_current,
    ROUND(ltv_estimate, 2) as ltv_estimate,
    ROUND(ltv_cac_ratio, 2) as ltv_cac_ratio,
    health_status,
    CASE
        WHEN health_status = 'Churned' THEN 'Lost High-Value Customer'
        WHEN health_status = 'Critical' THEN 'Urgent Intervention Needed'
        WHEN health_status = 'At Risk' THEN 'Proactive Engagement Recommended'
        ELSE 'Maintain Relationship'
    END as recommended_action
FROM day06_customer_health
WHERE plan_tier = 'Enterprise'
ORDER BY ltv_cac_ratio DESC;

-- Query 10: Health score improvement opportunities
-- ============================================================================
WITH upgrade_potential AS (
    SELECT
        customer_id,
        email,
        plan_tier,
        customer_age_months,
        ROUND(mrr_current, 2) as current_mrr,
        ROUND(ltv_cac_ratio, 2) as current_ltv_cac,
        -- Simulate upgrade impact
        CASE plan_tier
            WHEN 'Starter' THEN ROUND((ltv_estimate + (349 - mrr_current) * customer_age_months) / 500.0, 2)
            WHEN 'Pro' THEN ROUND((ltv_estimate + (1999 - mrr_current) * customer_age_months) / 500.0, 2)
            ELSE NULL
        END as projected_ltv_cac_after_upgrade,
        health_status
    FROM day06_customer_health
    WHERE customer_status = 'active'
      AND plan_tier IN ('Starter', 'Pro')
)
SELECT
    customer_id,
    email,
    plan_tier as current_tier,
    CASE plan_tier
        WHEN 'Starter' THEN 'Pro'
        WHEN 'Pro' THEN 'Enterprise'
    END as suggested_upgrade,
    current_mrr,
    current_ltv_cac,
    projected_ltv_cac_after_upgrade,
    ROUND(projected_ltv_cac_after_upgrade - current_ltv_cac, 2) as ltv_cac_improvement,
    health_status
FROM upgrade_potential
WHERE health_status IN ('At Risk', 'Critical')
  AND projected_ltv_cac_after_upgrade > current_ltv_cac + 0.5  -- Meaningful improvement
ORDER BY ltv_cac_improvement DESC
LIMIT 20;

-- ============================================================================
-- Dashboard Integration Notes
-- ============================================================================
--
-- For Day 19 Dashboard, use Query 2 as primary data source for pie chart
--
-- Pie Chart Configuration:
-- - Segments: health_status (Healthy, At Risk, Critical, Churned)
-- - Values: customer_count
-- - Colors:
--     Healthy: Green
--     At Risk: Yellow
--     Critical: Red
--     Churned: Gray
--
-- Table Widget (from Query 1):
-- - Top 10 customers by LTV/CAC ratio
-- - Columns: email, plan_tier, mrr_current, ltv_cac_ratio, health_status
-- - Sortable by any column
--
-- Alert Widget (from Query 4):
-- - List of at-risk customers requiring intervention
-- - Priority badge: High/Medium/Low
-- - Click to see customer details
--
-- KPI Cards (from Query 2):
-- - Healthy Customers: COUNT(*) WHERE health_status = 'Healthy'
-- - At-Risk Customers: COUNT(*) WHERE health_status = 'At Risk'
-- - Average LTV/CAC Ratio: AVG(ltv_cac_ratio)
