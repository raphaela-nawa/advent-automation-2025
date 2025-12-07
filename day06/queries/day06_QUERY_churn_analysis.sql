-- ============================================================================
-- Day 06: Churn Analysis Query
-- ============================================================================
--
-- Purpose: Analyze churn rates by cohort and plan tier
-- Stakeholder: Murilo (Simetryk SaaS)
-- Dashboard: Day 19 - Churn Heatmap
--
-- Usage:
--   sqlite3 data/day06_saas_metrics.db < queries/day06_QUERY_churn_analysis.sql
--
-- ============================================================================

-- Query 1: Complete churn breakdown by cohort and plan tier
-- ============================================================================
SELECT
    cohort_month,
    plan_tier,
    cohort_size,
    active_count,
    churned_count,
    churn_rate_pct,
    retention_rate_pct
FROM day06_churn_by_cohort
ORDER BY cohort_month, plan_tier;

-- Query 2: Overall churn rate by plan tier (aggregated across all cohorts)
-- ============================================================================
SELECT
    plan_tier,
    SUM(cohort_size) as total_customers,
    SUM(active_count) as total_active,
    SUM(churned_count) as total_churned,
    ROUND(100.0 * SUM(churned_count) / SUM(cohort_size), 2) as overall_churn_rate_pct,
    ROUND(100.0 * SUM(active_count) / SUM(cohort_size), 2) as overall_retention_rate_pct
FROM day06_churn_by_cohort
GROUP BY plan_tier
ORDER BY overall_churn_rate_pct ASC;

-- Query 3: Churn rate trend over time (by cohort month, all tiers combined)
-- ============================================================================
SELECT
    cohort_month,
    SUM(cohort_size) as cohort_size,
    SUM(churned_count) as churned_count,
    ROUND(100.0 * SUM(churned_count) / SUM(cohort_size), 2) as churn_rate_pct
FROM day06_churn_by_cohort
GROUP BY cohort_month
ORDER BY cohort_month;

-- Query 4: Best and worst performing cohorts (lowest and highest churn)
-- ============================================================================
WITH cohort_performance AS (
    SELECT
        cohort_month,
        plan_tier,
        cohort_size,
        churn_rate_pct
    FROM day06_churn_by_cohort
)
SELECT 'Best (Lowest Churn)' as category, cohort_month, plan_tier, cohort_size, churn_rate_pct
FROM cohort_performance
ORDER BY churn_rate_pct ASC, cohort_size DESC
LIMIT 5
UNION ALL
SELECT 'Worst (Highest Churn)', cohort_month, plan_tier, cohort_size, churn_rate_pct
FROM cohort_performance
ORDER BY churn_rate_pct DESC, cohort_size DESC
LIMIT 5;

-- Query 5: Churn rate comparison: Early cohorts vs Recent cohorts
-- ============================================================================
WITH cohort_split AS (
    SELECT
        cohort_month,
        plan_tier,
        cohort_size,
        churned_count,
        churn_rate_pct,
        CASE
            WHEN cohort_month <= '2023-06' THEN 'Early Cohorts (2023 H1)'
            WHEN cohort_month <= '2023-12' THEN 'Mid Cohorts (2023 H2)'
            ELSE 'Recent Cohorts (2024)'
        END as cohort_period
    FROM day06_churn_by_cohort
)
SELECT
    cohort_period,
    plan_tier,
    SUM(cohort_size) as total_customers,
    SUM(churned_count) as total_churned,
    ROUND(100.0 * SUM(churned_count) / SUM(cohort_size), 2) as avg_churn_rate_pct
FROM cohort_split
GROUP BY cohort_period, plan_tier
ORDER BY cohort_period, plan_tier;

-- Query 6: Plan tier with best/worst retention
-- ============================================================================
SELECT
    plan_tier,
    SUM(cohort_size) as total_customers,
    SUM(active_count) as currently_active,
    ROUND(100.0 * SUM(active_count) / SUM(cohort_size), 2) as retention_rate_pct,
    CASE
        WHEN ROUND(100.0 * SUM(active_count) / SUM(cohort_size), 2) >= 70 THEN 'Excellent'
        WHEN ROUND(100.0 * SUM(active_count) / SUM(cohort_size), 2) >= 60 THEN 'Good'
        WHEN ROUND(100.0 * SUM(active_count) / SUM(cohort_size), 2) >= 50 THEN 'Fair'
        ELSE 'Poor'
    END as retention_grade
FROM day06_churn_by_cohort
GROUP BY plan_tier
ORDER BY retention_rate_pct DESC;

-- Query 7: Cohort size distribution (how many customers per cohort)
-- ============================================================================
SELECT
    cohort_month,
    SUM(cohort_size) as total_signups,
    ROUND(100.0 * SUM(cohort_size) / (SELECT COUNT(*) FROM day06_customers), 2) as pct_of_total_customers
FROM day06_churn_by_cohort
GROUP BY cohort_month
ORDER BY cohort_month;

-- Query 8: Churn impact analysis (MRR lost by cohort)
-- ============================================================================
SELECT
    c.cohort_month,
    c.plan_tier,
    c.churned_count,
    c.churn_rate_pct,
    -- Estimate average MRR per customer by plan tier
    CASE c.plan_tier
        WHEN 'Starter' THEN c.churned_count * 64  -- Avg Starter MRR ~$64
        WHEN 'Pro' THEN c.churned_count * 349     -- Avg Pro MRR ~$349
        WHEN 'Enterprise' THEN c.churned_count * 1999  -- Avg Enterprise MRR ~$1999
    END as estimated_mrr_lost
FROM day06_churn_by_cohort c
WHERE c.churned_count > 0
ORDER BY estimated_mrr_lost DESC
LIMIT 10;

-- ============================================================================
-- Dashboard Integration Notes
-- ============================================================================
--
-- For Day 19 Dashboard, use Query 1 as primary data source for heatmap
--
-- Heatmap Configuration:
-- - Rows: cohort_month
-- - Columns: plan_tier
-- - Color: churn_rate_pct (gradient from green=low to red=high)
-- - Threshold colors:
--     < 20%: Dark green (excellent retention)
--     20-40%: Light green (good retention)
--     40-60%: Yellow (moderate churn)
--     > 60%: Red (high churn)
--
-- KPI Cards (from Query 2):
-- - Overall Churn Rate: AVG(churn_rate_pct)
-- - Best Performing Tier: plan_tier with lowest churn
-- - Worst Performing Tier: plan_tier with highest churn
--
-- Trend Chart (from Query 3):
-- - Line chart showing churn rate trend over time
-- - X-axis: cohort_month
-- - Y-axis: churn_rate_pct
