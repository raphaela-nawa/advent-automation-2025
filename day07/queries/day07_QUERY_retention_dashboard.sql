-- ============================================================================
-- Sample Query: Retention Performance Dashboard
-- ============================================================================
-- Business Question: How well am I retaining guests across different cohorts?
-- Use Case: Monitor retention health and identify areas for improvement
-- ============================================================================

-- Recent cohorts retention performance (last 12 cohorts with mature data)
SELECT
    cohort_month,
    season_category,
    cohort_size,
    retention_1m_pct,
    meets_1m_target,
    retention_3m_pct,
    meets_3m_target,
    retention_6m_pct,
    meets_6m_target,
    retention_12m_pct,
    meets_12m_target,
    retention_score,
    recommended_action
FROM day07_retention_matrix
WHERE retention_3m_maturity = 'Mature'
ORDER BY cohort_month DESC
LIMIT 12;

-- Overall retention performance summary
SELECT
    'Overall Average' as metric_category,
    ROUND(AVG(retention_1m_pct), 1) as avg_retention_1m,
    ROUND(AVG(retention_3m_pct), 1) as avg_retention_3m,
    ROUND(AVG(retention_6m_pct), 1) as avg_retention_6m,
    ROUND(AVG(retention_12m_pct), 1) as avg_retention_12m,
    ROUND(AVG(retention_score), 1) as avg_retention_score
FROM day07_retention_matrix
WHERE retention_3m_maturity = 'Mature'

UNION ALL

SELECT
    'Target Benchmark' as metric_category,
    15.0 as target_1m,
    25.0 as target_3m,
    35.0 as target_6m,
    40.0 as target_12m,
    NULL as retention_score

UNION ALL

SELECT
    'Best Cohort' as metric_category,
    MAX(retention_1m_pct),
    MAX(retention_3m_pct),
    MAX(retention_6m_pct),
    MAX(retention_12m_pct),
    MAX(retention_score)
FROM day07_retention_matrix
WHERE retention_3m_maturity = 'Mature';

-- Retention by season comparison
SELECT
    season_category,
    COUNT(*) as num_cohorts,
    ROUND(AVG(retention_1m_pct), 1) as avg_retention_1m_pct,
    ROUND(AVG(retention_3m_pct), 1) as avg_retention_3m_pct,
    ROUND(AVG(retention_6m_pct), 1) as avg_retention_6m_pct,
    ROUND(AVG(retention_score), 1) as avg_retention_score,
    ROUND(AVG(avg_months_to_first_return), 1) as avg_months_to_return
FROM day07_retention_matrix
WHERE retention_3m_maturity = 'Mature'
GROUP BY season_category
ORDER BY avg_retention_score DESC;

-- Cohorts needing attention (below target)
SELECT
    cohort_month,
    cohort_size,
    retention_3m_pct,
    variance_from_3m_target,
    retention_score,
    return_speed,
    recommended_action
FROM day07_retention_matrix
WHERE
    retention_3m_maturity = 'Mature'
    AND meets_3m_target = '✗'
ORDER BY variance_from_3m_target ASC;
