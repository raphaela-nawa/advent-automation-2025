-- ============================================================================
-- Sample Query: Actionable Business Insights
-- ============================================================================
-- Business Question: What specific actions should I take today?
-- Use Case: Generate daily/weekly action list for Carol
-- ============================================================================

-- ============================================================================
-- 1. URGENT: VIP guests who need immediate re-engagement
-- ============================================================================
SELECT
    'VIP Re-engagement' as action_category,
    guest_id,
    first_name || ' ' || last_name as guest_name,
    email,
    total_ltv_gross_brl as ltv,
    days_since_last_booking,
    latest_room_type as preferred_room,
    recommended_action
FROM day07_guest_ltv_analysis
WHERE recommended_action LIKE 'URGENT:%'
ORDER BY retention_priority_score DESC
LIMIT 10;

-- ============================================================================
-- 2. OPPORTUNITY: First-time guests ready for conversion to repeat
-- ============================================================================
SELECT
    'Convert First-Timers' as action_category,
    guest_id,
    first_name || ' ' || last_name as guest_name,
    email,
    first_booking_value_brl,
    days_since_last_booking,
    avg_guest_rating,
    CASE
        WHEN days_since_last_booking <= 30 THEN 'Send welcome-back offer'
        WHEN days_since_last_booking <= 90 THEN 'Send seasonal promotion'
        ELSE 'Send win-back campaign'
    END as suggested_message
FROM day07_guest_ltv_analysis
WHERE
    loyalty_segment = 'First-Timer (1 visit)'
    AND first_booking_value_brl >= 1000
    AND avg_guest_rating >= 4.0
    AND days_since_last_booking BETWEEN 30 AND 180
ORDER BY first_booking_value_brl DESC
LIMIT 15;

-- ============================================================================
-- 3. RETENTION: High-value guests approaching churn risk
-- ============================================================================
SELECT
    'Retention Risk' as action_category,
    guest_id,
    first_name || ' ' || last_name as guest_name,
    email,
    total_ltv_gross_brl as ltv,
    lifetime_bookings,
    days_since_last_booking,
    avg_days_between_bookings as typical_booking_interval,
    'Send personalized offer' as suggested_message
FROM day07_guest_ltv_analysis
WHERE
    ltv_segment IN ('High Value (R$2500-3999)', 'VIP (R$4000+)')
    AND engagement_status = 'Cooling (3-6 months)'
    AND days_since_last_booking > (avg_days_between_bookings * 1.5)
ORDER BY retention_priority_score DESC
LIMIT 10;

-- ============================================================================
-- 4. MARKETING: Best months to increase advertising spend
-- ============================================================================
SELECT
    'Marketing Investment' as action_category,
    cohort_month,
    season_category,
    cohort_quality_score,
    value_per_guest_brl,
    repeat_guest_pct,
    'Increase ad spend for this acquisition period' as recommendation
FROM day07_guest_cohorts
WHERE
    cohort_quality_score >= (SELECT AVG(cohort_quality_score) * 1.1 FROM day07_guest_cohorts)
    AND value_per_guest_brl >= 1500
ORDER BY cohort_quality_score DESC
LIMIT 5;

-- ============================================================================
-- 5. OPERATIONAL: Cohorts with poor retention needing investigation
-- ============================================================================
SELECT
    'Investigate Issues' as action_category,
    cohort_month,
    cohort_size,
    retention_3m_pct,
    avg_guest_rating,
    return_speed,
    'Review feedback and service quality for this period' as recommendation
FROM day07_retention_matrix
WHERE
    retention_3m_maturity = 'Mature'
    AND retention_3m_pct < 20
ORDER BY cohort_month DESC;

-- ============================================================================
-- 6. SUMMARY: Quick action dashboard
-- ============================================================================
SELECT
    'Action Summary' as report_type,
    (SELECT COUNT(*) FROM day07_guest_ltv_analysis
     WHERE recommended_action LIKE 'URGENT:%') as urgent_vip_reengagement,

    (SELECT COUNT(*) FROM day07_guest_ltv_analysis
     WHERE loyalty_segment = 'First-Timer (1 visit)'
     AND first_booking_value_brl >= 1000
     AND days_since_last_booking BETWEEN 30 AND 180) as first_timer_opportunities,

    (SELECT COUNT(*) FROM day07_guest_ltv_analysis
     WHERE engagement_status = 'At Risk (6-12 months)'
     AND ltv_segment IN ('VIP (R$4000+)', 'High Value (R$2500-3999)')) as high_value_at_risk,

    (SELECT COUNT(*) FROM day07_retention_matrix
     WHERE retention_3m_maturity = 'Mature'
     AND meets_3m_target = '✗') as cohorts_below_target;
