-- ============================================================================
-- Sample Query: VIP Guest Identification and Engagement
-- ============================================================================
-- Business Question: Who are my most valuable guests and how should I engage them?
-- Use Case: Personalized VIP treatment and retention campaigns
-- ============================================================================

-- Top 20 guests by lifetime value
SELECT
    guest_id,
    first_name,
    last_name,
    email,
    country,
    guest_type,
    total_ltv_gross_brl,
    total_ltv_net_brl,
    lifetime_bookings,
    lifetime_nights,
    avg_guest_rating,
    engagement_status,
    days_since_last_booking,
    recommended_action
FROM day07_guest_ltv_analysis
WHERE ltv_segment IN ('VIP (R$4000+)', 'High Value (R$2500-3999)')
ORDER BY total_ltv_gross_brl DESC
LIMIT 20;

-- VIP guests who need re-engagement (haven't booked recently)
SELECT
    guest_id,
    first_name || ' ' || last_name as full_name,
    email,
    total_ltv_gross_brl,
    lifetime_bookings,
    last_booking_date,
    days_since_last_booking,
    retention_priority_score,
    recommended_action
FROM day07_guest_ltv_analysis
WHERE
    ltv_segment = 'VIP (R$4000+)'
    AND engagement_status IN ('At Risk (6-12 months)', 'Churned (> 1 year)')
ORDER BY retention_priority_score DESC;

-- VIP guest summary statistics
SELECT
    ltv_segment,
    COUNT(*) as guest_count,
    ROUND(AVG(total_ltv_gross_brl), 2) as avg_ltv,
    ROUND(SUM(total_ltv_gross_brl), 2) as total_revenue,
    ROUND(100.0 * SUM(total_ltv_gross_brl) / (SELECT SUM(total_ltv_gross_brl) FROM day07_guest_ltv_analysis), 1) as revenue_share_pct,
    ROUND(AVG(lifetime_bookings), 1) as avg_visits,
    ROUND(AVG(avg_guest_rating), 2) as avg_satisfaction
FROM day07_guest_ltv_analysis
GROUP BY ltv_segment
ORDER BY avg_ltv DESC;
