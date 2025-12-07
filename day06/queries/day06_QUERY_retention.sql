-- ============================================================================
-- Day 06: Retention Curves Query
-- ============================================================================
--
-- Purpose: Analyze cohort retention curves over time
-- Stakeholder: SaaS Executive (C-level)
-- Dashboard: Day 19 - Retention Line Chart
--
-- Usage:
--   sqlite3 data/day06_saas_metrics.db < queries/day06_QUERY_retention.sql
--
-- ============================================================================

-- Query 1: Complete retention curves for all cohorts
-- ============================================================================
SELECT
    cohort_month,
    months_since_signup,
    retained_customers,
    cohort_size,
    retention_rate_pct
FROM day06_retention_curves
ORDER BY cohort_month, months_since_signup;

-- Query 2: Retention curves for specific cohorts (early, mid, late)
-- ============================================================================
SELECT
    cohort_month,
    months_since_signup,
    retained_customers,
    cohort_size,
    retention_rate_pct
FROM day06_retention_curves
WHERE cohort_month IN ('2023-01', '2023-06', '2023-12', '2024-01', '2024-06')
ORDER BY cohort_month, months_since_signup;

-- Query 3: Average retention rate by months since signup (across all cohorts)
-- ============================================================================
SELECT
    months_since_signup,
    ROUND(AVG(retention_rate_pct), 2) as avg_retention_rate_pct,
    COUNT(DISTINCT cohort_month) as cohorts_measured,
    SUM(retained_customers) as total_retained,
    SUM(cohort_size) as total_cohort_size
FROM day06_retention_curves
GROUP BY months_since_signup
HAVING cohorts_measured >= 3  -- Only show months with at least 3 cohorts measured
ORDER BY months_since_signup;

-- Query 4: Retention at key milestones (1, 3, 6, 12, 24 months)
-- ============================================================================
SELECT
    cohort_month,
    MAX(CASE WHEN months_since_signup = 0 THEN retention_rate_pct END) as month_0_retention,
    MAX(CASE WHEN months_since_signup = 1 THEN retention_rate_pct END) as month_1_retention,
    MAX(CASE WHEN months_since_signup = 3 THEN retention_rate_pct END) as month_3_retention,
    MAX(CASE WHEN months_since_signup = 6 THEN retention_rate_pct END) as month_6_retention,
    MAX(CASE WHEN months_since_signup = 12 THEN retention_rate_pct END) as month_12_retention,
    MAX(CASE WHEN months_since_signup = 24 THEN retention_rate_pct END) as month_24_retention
FROM day06_retention_curves
GROUP BY cohort_month
ORDER BY cohort_month;

-- Query 5: Cohort retention performance (best vs worst cohorts)
-- ============================================================================
WITH cohort_retention_at_6m AS (
    SELECT
        cohort_month,
        cohort_size,
        retention_rate_pct as retention_at_6m
    FROM day06_retention_curves
    WHERE months_since_signup = 6
)
SELECT
    'Best 6-Month Retention' as category,
    cohort_month,
    cohort_size,
    retention_at_6m
FROM cohort_retention_at_6m
ORDER BY retention_at_6m DESC
LIMIT 3
UNION ALL
SELECT
    'Worst 6-Month Retention',
    cohort_month,
    cohort_size,
    retention_at_6m
FROM cohort_retention_at_6m
ORDER BY retention_at_6m ASC
LIMIT 3;

-- Query 6: Retention drop-off analysis (biggest drops month-over-month)
-- ============================================================================
WITH retention_changes AS (
    SELECT
        cohort_month,
        months_since_signup,
        retention_rate_pct,
        LAG(retention_rate_pct) OVER (
            PARTITION BY cohort_month
            ORDER BY months_since_signup
        ) as prev_month_retention,
        retention_rate_pct - LAG(retention_rate_pct) OVER (
            PARTITION BY cohort_month
            ORDER BY months_since_signup
        ) as retention_drop_pct
    FROM day06_retention_curves
)
SELECT
    cohort_month,
    months_since_signup,
    ROUND(retention_rate_pct, 2) as current_retention,
    ROUND(prev_month_retention, 2) as previous_retention,
    ROUND(retention_drop_pct, 2) as drop_pct,
    CASE
        WHEN retention_drop_pct < -10 THEN 'Critical Drop'
        WHEN retention_drop_pct < -5 THEN 'Significant Drop'
        WHEN retention_drop_pct < -2 THEN 'Normal Churn'
        ELSE 'Stable'
    END as drop_severity
FROM retention_changes
WHERE retention_drop_pct IS NOT NULL
ORDER BY retention_drop_pct ASC
LIMIT 20;

-- Query 7: Expected retention curve (benchmark from mature cohorts)
-- ============================================================================
SELECT
    months_since_signup,
    ROUND(AVG(retention_rate_pct), 2) as benchmark_retention_pct,
    COUNT(DISTINCT cohort_month) as cohorts_included,
    ROUND(MIN(retention_rate_pct), 2) as worst_cohort_retention,
    ROUND(MAX(retention_rate_pct), 2) as best_cohort_retention
FROM day06_retention_curves
WHERE cohort_month <= '2023-06'  -- Only mature cohorts (18+ months old)
GROUP BY months_since_signup
ORDER BY months_since_signup;

-- Query 8: Retention velocity (how fast does retention decay?)
-- ============================================================================
WITH retention_at_milestones AS (
    SELECT
        cohort_month,
        MAX(CASE WHEN months_since_signup = 1 THEN retention_rate_pct END) as m1_retention,
        MAX(CASE WHEN months_since_signup = 6 THEN retention_rate_pct END) as m6_retention,
        MAX(CASE WHEN months_since_signup = 12 THEN retention_rate_pct END) as m12_retention
    FROM day06_retention_curves
    GROUP BY cohort_month
)
SELECT
    cohort_month,
    m1_retention,
    m6_retention,
    m12_retention,
    -- Decay from month 1 to month 6
    ROUND(m1_retention - m6_retention, 2) as m1_to_m6_decay,
    -- Decay from month 6 to month 12
    ROUND(m6_retention - m12_retention, 2) as m6_to_m12_decay,
    CASE
        WHEN (m1_retention - m6_retention) < 10 THEN 'Slow Decay (Healthy)'
        WHEN (m1_retention - m6_retention) < 20 THEN 'Moderate Decay'
        ELSE 'Fast Decay (Warning)'
    END as decay_status
FROM retention_at_milestones
WHERE m1_retention IS NOT NULL AND m6_retention IS NOT NULL
ORDER BY m1_to_m6_decay ASC;

-- ============================================================================
-- Dashboard Integration Notes
-- ============================================================================
--
-- For Day 19 Dashboard, use Query 1 or Query 2 as primary data source
--
-- Line Chart Configuration:
-- - Chart Type: Multi-line chart
-- - X-axis: months_since_signup
-- - Y-axis: retention_rate_pct (0-100%)
-- - Series: Each cohort_month as a separate line
-- - Colors: Gradient from dark (early cohorts) to light (recent cohorts)
-- - Highlight: 2023-01 cohort (oldest, most complete data)
--
-- Benchmark Line (from Query 7):
-- - Dotted line showing expected retention curve
-- - Use AVG(retention_rate_pct) from mature cohorts
--
-- KPI Cards (from Query 3):
-- - Month 1 Retention: avg_retention_rate_pct at months_since_signup = 1
-- - Month 6 Retention: avg_retention_rate_pct at months_since_signup = 6
-- - Month 12 Retention: avg_retention_rate_pct at months_since_signup = 12
