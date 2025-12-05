-- ============================================================================
-- Sample Query: Top Performing Cohorts Analysis
-- ============================================================================
-- Business Question: Which months brought in the highest quality guests?
-- Use Case: Optimize marketing budget allocation by season/month
-- ============================================================================

-- Find the top 10 cohorts by quality score and revenue
SELECT
    cohort_month,
    season_category,
    cohort_size,
    total_cohort_value_brl,
    value_per_guest_brl,
    cohort_quality_score,
    retention_ever_pct as repeat_guest_pct,
    avg_guest_rating,
    direct_channel_pct,
    vip_count
FROM day07_guest_cohorts
ORDER BY cohort_quality_score DESC
LIMIT 10;

-- Compare high season vs low season performance
SELECT
    season_category,
    COUNT(DISTINCT cohort_month) as num_cohorts,
    SUM(cohort_size) as total_guests,
    ROUND(AVG(value_per_guest_brl), 2) as avg_value_per_guest,
    ROUND(AVG(cohort_quality_score), 1) as avg_quality_score,
    ROUND(AVG(bookings_per_guest), 2) as avg_bookings_per_guest,
    ROUND(AVG(avg_guest_rating), 2) as avg_satisfaction
FROM day07_guest_cohorts
GROUP BY season_category
ORDER BY avg_quality_score DESC;
