-- ============================================================================
-- Day 06: MRR Waterfall Analysis Query
-- ============================================================================
--
-- Purpose: Analyze MRR movements over time for waterfall chart
-- Stakeholder: Murilo (Simetryk SaaS)
-- Dashboard: Day 19 - MRR Waterfall Chart
--
-- Usage:
--   sqlite3 data/day06_saas_metrics.db < queries/day06_QUERY_mrr_waterfall.sql
--
-- ============================================================================

-- Query 1: Complete MRR waterfall for all months
-- ============================================================================
SELECT
    month,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churn_mrr,
    net_mrr,
    cumulative_mrr,
    mom_growth_rate_pct
FROM day06_mrr_summary
ORDER BY month;

-- Query 2: MRR breakdown for latest month
-- ============================================================================
SELECT
    'Latest Month MRR Breakdown' as analysis,
    month,
    new_mrr as 'New MRR',
    expansion_mrr as 'Expansion (Upgrades)',
    contraction_mrr as 'Contraction (Downgrades)',
    churn_mrr as 'Churn (Lost)',
    net_mrr as 'Net MRR Change',
    cumulative_mrr as 'Total MRR'
FROM day06_mrr_summary
ORDER BY month DESC
LIMIT 1;

-- Query 3: MRR growth trajectory (first vs last month)
-- ============================================================================
WITH mrr_bounds AS (
    SELECT
        MIN(month) as first_month,
        MAX(month) as last_month
    FROM day06_mrr_summary
)
SELECT
    'MRR Growth Analysis' as metric,
    f.month as start_month,
    f.cumulative_mrr as starting_mrr,
    l.month as end_month,
    l.cumulative_mrr as ending_mrr,
    ROUND(l.cumulative_mrr - f.cumulative_mrr, 2) as absolute_growth,
    ROUND(100.0 * (l.cumulative_mrr - f.cumulative_mrr) / f.cumulative_mrr, 2) as growth_pct,
    ROUND((l.cumulative_mrr / f.cumulative_mrr), 2) as growth_multiple
FROM mrr_bounds mb
JOIN day06_mrr_summary f ON f.month = mb.first_month
JOIN day06_mrr_summary l ON l.month = mb.last_month;

-- Query 4: Average monthly MRR components
-- ============================================================================
SELECT
    'Average Monthly Values' as metric,
    ROUND(AVG(new_mrr), 2) as avg_new_mrr,
    ROUND(AVG(expansion_mrr), 2) as avg_expansion_mrr,
    ROUND(AVG(contraction_mrr), 2) as avg_contraction_mrr,
    ROUND(AVG(churn_mrr), 2) as avg_churn_mrr,
    ROUND(AVG(net_mrr), 2) as avg_net_mrr
FROM day06_mrr_summary;

-- Query 5: MRR component contribution (total across all months)
-- ============================================================================
WITH totals AS (
    SELECT
        SUM(new_mrr) as total_new,
        SUM(expansion_mrr) as total_expansion,
        SUM(contraction_mrr) as total_contraction,
        SUM(churn_mrr) as total_churn,
        SUM(net_mrr) as total_net
    FROM day06_mrr_summary
)
SELECT
    'New MRR' as component,
    ROUND(total_new, 2) as total_amount,
    ROUND(100.0 * total_new / (total_new + total_expansion), 2) as pct_of_growth
FROM totals
UNION ALL
SELECT
    'Expansion MRR',
    ROUND(total_expansion, 2),
    ROUND(100.0 * total_expansion / (total_new + total_expansion), 2)
FROM totals
UNION ALL
SELECT
    'Contraction MRR',
    ROUND(total_contraction, 2),
    ROUND(100.0 * total_contraction / (total_new + total_expansion), 2)
FROM totals
UNION ALL
SELECT
    'Churn MRR',
    ROUND(total_churn, 2),
    ROUND(100.0 * total_churn / (total_new + total_expansion), 2)
FROM totals
UNION ALL
SELECT
    'Net MRR',
    ROUND(total_net, 2),
    ROUND(100.0 * total_net / (total_new + total_expansion), 2)
FROM totals;

-- Query 6: Months with highest/lowest net MRR change
-- ============================================================================
SELECT 'Best Month' as category, month, net_mrr
FROM day06_mrr_summary
ORDER BY net_mrr DESC
LIMIT 1
UNION ALL
SELECT 'Worst Month', month, net_mrr
FROM day06_mrr_summary
ORDER BY net_mrr ASC
LIMIT 1;

-- Query 7: Quick Rate (expansion vs contraction ratio)
-- ============================================================================
SELECT
    month,
    expansion_mrr,
    contraction_mrr,
    CASE
        WHEN contraction_mrr = 0 THEN NULL
        ELSE ROUND(expansion_mrr / contraction_mrr, 2)
    END as expansion_contraction_ratio,
    CASE
        WHEN expansion_mrr > contraction_mrr THEN 'Healthy (More Upgrades)'
        WHEN expansion_mrr < contraction_mrr THEN 'Warning (More Downgrades)'
        ELSE 'Neutral'
    END as health_status
FROM day06_mrr_summary
WHERE expansion_mrr > 0 OR contraction_mrr > 0
ORDER BY month DESC
LIMIT 10;

-- ============================================================================
-- Dashboard Integration Notes
-- ============================================================================
--
-- For Day 19 Dashboard, use Query 1 (complete waterfall) as primary data source
--
-- Chart Configuration:
-- - Chart Type: Waterfall (or stacked bar)
-- - X-axis: month (time series)
-- - Y-axis: MRR values
-- - Series:
--     1. new_mrr (green, positive)
--     2. expansion_mrr (blue, positive)
--     3. contraction_mrr (orange, negative)
--     4. churn_mrr (red, negative)
--     5. cumulative_mrr (black line, overlay)
--
-- KPI Cards (from Query 2):
-- - Current MRR: cumulative_mrr from latest month
-- - Month-over-Month Growth: mom_growth_rate_pct
-- - Total New MRR: Sum of new_mrr
-- - Total Churn MRR: Sum of churn_mrr
