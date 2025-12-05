-- ============================================================================
-- Day 07: Lifetime Value (LTV) Analysis Model for Carol's Pousada
-- ============================================================================
-- Business Purpose:
--   Calculate cumulative lifetime value for each guest to:
--   - Identify highest-value guests for VIP treatment and retention campaigns
--   - Track how value accumulates over time and across bookings
--   - Compare LTV across cohorts to optimize acquisition strategy
--   - Predict future value based on early booking patterns
--
-- Stakeholder: Carol (Pousada Owner)
-- Use Case: Segment guests by value, prioritize retention efforts on high-LTV guests
-- ============================================================================

-- ============================================================================
-- STEP 1: Calculate Revenue per Booking
-- ============================================================================
-- Start with all completed bookings and their associated revenue

DROP VIEW IF EXISTS day07_guest_ltv_analysis;
CREATE VIEW day07_guest_ltv_analysis AS

WITH day07_booking_revenue AS (
    SELECT
        b.booking_id,
        b.guest_id,
        b.booking_date,
        b.check_in_date,
        b.check_out_date,
        b.room_type,
        b.booking_source,
        b.total_price_brl as room_revenue_brl,

        -- Calculate net revenue (after commission)
        b.total_price_brl * (1 - b.commission_pct) as net_room_revenue_brl,

        -- Add extras from stays (if stay exists)
        COALESCE(s.extras_spent_brl, 0) as extras_revenue_brl,

        -- Total booking value
        b.total_price_brl + COALESCE(s.extras_spent_brl, 0) as total_booking_value_brl,

        -- Net value after commissions
        (b.total_price_brl * (1 - b.commission_pct)) + COALESCE(s.extras_spent_brl, 0) as net_booking_value_brl,

        -- Stay quality indicators
        s.guest_rating,
        s.repeat_guest,

        -- Calculate nights stayed
        JULIANDAY(b.check_out_date) - JULIANDAY(b.check_in_date) as nights_stayed

    FROM day07_bookings b
    LEFT JOIN day07_stays s ON b.booking_id = s.booking_id
    WHERE b.status != 'Cancelled'  -- Only completed bookings contribute to LTV
),

-- ============================================================================
-- STEP 2: Assign Cohort and Calculate Booking Sequence
-- ============================================================================
-- For each guest, identify their cohort and number their bookings chronologically

day07_guest_booking_sequence AS (
    SELECT
        br.*,

        -- Get cohort information
        STRFTIME('%Y-%m',
            MIN(br.booking_date) OVER (PARTITION BY br.guest_id)
        ) as cohort_month,

        MIN(br.booking_date) OVER (PARTITION BY br.guest_id) as first_booking_date,

        -- Assign booking number for each guest (1st booking, 2nd booking, etc.)
        ROW_NUMBER() OVER (
            PARTITION BY br.guest_id
            ORDER BY br.booking_date, br.booking_id
        ) as booking_number,

        -- Total number of bookings per guest
        COUNT(*) OVER (PARTITION BY br.guest_id) as total_bookings,

        -- Days since previous booking (for retention analysis)
        JULIANDAY(br.booking_date) -
        LAG(JULIANDAY(br.booking_date)) OVER (
            PARTITION BY br.guest_id
            ORDER BY br.booking_date
        ) as days_since_last_booking,

        -- Days since first booking (guest tenure)
        JULIANDAY(br.booking_date) -
        MIN(JULIANDAY(br.booking_date)) OVER (PARTITION BY br.guest_id) as days_since_first_booking

    FROM day07_booking_revenue br
),

-- ============================================================================
-- STEP 3: Calculate Cumulative LTV (Core Metric)
-- ============================================================================
-- Use window functions to calculate running totals of spending

day07_cumulative_ltv AS (
    SELECT
        gbs.*,

        -- === CUMULATIVE VALUE METRICS (Window Functions) ===

        -- Cumulative gross revenue (total spent so far)
        SUM(gbs.total_booking_value_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_ltv_gross_brl,

        -- Cumulative net revenue (after commissions)
        SUM(gbs.net_booking_value_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_ltv_net_brl,

        -- Cumulative room revenue only
        SUM(gbs.room_revenue_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_room_revenue_brl,

        -- Cumulative extras revenue
        SUM(gbs.extras_revenue_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_extras_revenue_brl,

        -- Cumulative nights stayed
        SUM(gbs.nights_stayed) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_nights_stayed,

        -- === AVERAGE VALUE METRICS ===

        -- Average value per booking (up to this point)
        AVG(gbs.total_booking_value_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as avg_booking_value_brl,

        -- Moving average (last 3 bookings) for trend detection
        AVG(gbs.total_booking_value_brl) OVER (
            PARTITION BY gbs.guest_id
            ORDER BY gbs.booking_date, gbs.booking_id
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as moving_avg_value_3bookings_brl,

        -- === RANKING METRICS ===

        -- Rank guests by current cumulative LTV (within cohort)
        DENSE_RANK() OVER (
            PARTITION BY STRFTIME('%Y-%m', MIN(gbs.booking_date) OVER (PARTITION BY gbs.guest_id))
            ORDER BY SUM(gbs.total_booking_value_brl) OVER (
                PARTITION BY gbs.guest_id
                ORDER BY gbs.booking_date, gbs.booking_id
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) DESC
        ) as ltv_rank_in_cohort

    FROM day07_guest_booking_sequence gbs
),

-- ============================================================================
-- STEP 4: Calculate Guest-Level LTV Summary
-- ============================================================================
-- Aggregate to one row per guest with their total LTV and behavior patterns

day07_guest_ltv_summary AS (
    SELECT
        guest_id,
        cohort_month,
        first_booking_date,

        -- === TOTAL VALUE METRICS ===
        MAX(cumulative_ltv_gross_brl) as total_ltv_gross_brl,
        MAX(cumulative_ltv_net_brl) as total_ltv_net_brl,
        MAX(cumulative_room_revenue_brl) as total_room_revenue_brl,
        MAX(cumulative_extras_revenue_brl) as total_extras_revenue_brl,

        -- === BOOKING BEHAVIOR ===
        MAX(total_bookings) as lifetime_bookings,
        MAX(cumulative_nights_stayed) as lifetime_nights,
        ROUND(MAX(cumulative_ltv_gross_brl) / MAX(total_bookings), 2) as avg_booking_value_brl,
        ROUND(MAX(cumulative_ltv_gross_brl) / MAX(cumulative_nights_stayed), 2) as avg_revenue_per_night_brl,

        -- === VALUE TREND ===
        -- Compare first booking value to average to detect increasing/decreasing spend
        MIN(CASE WHEN booking_number = 1 THEN total_booking_value_brl END) as first_booking_value_brl,
        MAX(CASE WHEN booking_number = MAX(total_bookings) THEN total_booking_value_brl END) as last_booking_value_brl,

        -- === TIMING METRICS ===
        MAX(days_since_first_booking) as customer_tenure_days,
        ROUND(AVG(CASE WHEN days_since_last_booking IS NOT NULL THEN days_since_last_booking END), 1) as avg_days_between_bookings,

        -- === LOYALTY INDICATORS ===
        MAX(CASE WHEN booking_number = MAX(total_bookings) THEN booking_date END) as last_booking_date,
        JULIANDAY('now') - JULIANDAY(MAX(CASE WHEN booking_number = MAX(total_bookings) THEN booking_date END)) as days_since_last_booking,

        -- === QUALITY METRICS ===
        ROUND(AVG(guest_rating), 2) as avg_guest_rating,

        -- === CHANNEL PREFERENCE ===
        MAX(CASE WHEN booking_number = 1 THEN booking_source END) as first_booking_source,
        MAX(CASE WHEN booking_number = MAX(total_bookings) THEN booking_source END) as latest_booking_source,

        -- Room preference
        MAX(CASE WHEN booking_number = MAX(total_bookings) THEN room_type END) as latest_room_type

    FROM day07_cumulative_ltv
    GROUP BY guest_id, cohort_month, first_booking_date
)

-- ============================================================================
-- FINAL OUTPUT: Complete LTV Analysis with Guest Details
-- ============================================================================
-- Join with guest table and add segmentation

SELECT
    ltv.guest_id,
    g.first_name,
    g.last_name,
    g.email,
    g.country,
    g.guest_type,
    g.vip_status,

    -- === COHORT INFORMATION ===
    ltv.cohort_month,
    ltv.first_booking_date,
    ltv.last_booking_date,
    ltv.customer_tenure_days,
    ROUND(ltv.customer_tenure_days / 30.0, 1) as customer_tenure_months,

    -- === LIFETIME VALUE METRICS ===
    ltv.total_ltv_gross_brl,
    ltv.total_ltv_net_brl,
    ltv.total_room_revenue_brl,
    ltv.total_extras_revenue_brl,
    ROUND(100.0 * ltv.total_extras_revenue_brl / ltv.total_ltv_gross_brl, 1) as extras_pct_of_ltv,

    -- === BOOKING BEHAVIOR ===
    ltv.lifetime_bookings,
    ltv.lifetime_nights,
    ltv.avg_booking_value_brl,
    ltv.avg_revenue_per_night_brl,
    ltv.avg_days_between_bookings,

    -- === VALUE TREND ===
    ltv.first_booking_value_brl,
    ltv.last_booking_value_brl,
    ROUND(ltv.last_booking_value_brl - ltv.first_booking_value_brl, 2) as value_change_brl,
    ROUND(100.0 * (ltv.last_booking_value_brl - ltv.first_booking_value_brl) / ltv.first_booking_value_brl, 1) as value_change_pct,

    -- === ENGAGEMENT STATUS ===
    ltv.days_since_last_booking,
    CASE
        WHEN ltv.days_since_last_booking <= 30 THEN 'Active (< 1 month)'
        WHEN ltv.days_since_last_booking <= 90 THEN 'Recent (1-3 months)'
        WHEN ltv.days_since_last_booking <= 180 THEN 'Cooling (3-6 months)'
        WHEN ltv.days_since_last_booking <= 365 THEN 'At Risk (6-12 months)'
        ELSE 'Churned (> 1 year)'
    END as engagement_status,

    -- === LTV SEGMENT ===
    CASE
        WHEN ltv.total_ltv_gross_brl >= 4000 THEN 'VIP (R$4000+)'
        WHEN ltv.total_ltv_gross_brl >= 2500 THEN 'High Value (R$2500-3999)'
        WHEN ltv.total_ltv_gross_brl >= 1200 THEN 'Average (R$1200-2499)'
        ELSE 'Low Value (< R$1200)'
    END as ltv_segment,

    -- === LOYALTY SEGMENT ===
    CASE
        WHEN ltv.lifetime_bookings >= 5 THEN 'Super Loyal (5+ visits)'
        WHEN ltv.lifetime_bookings >= 3 THEN 'Loyal (3-4 visits)'
        WHEN ltv.lifetime_bookings = 2 THEN 'Returning (2 visits)'
        ELSE 'First-Timer (1 visit)'
    END as loyalty_segment,

    -- === QUALITY INDICATORS ===
    ltv.avg_guest_rating,
    ltv.first_booking_source,
    ltv.latest_booking_source,
    ltv.latest_room_type,

    -- === PREDICTED VALUE (Simple Heuristic) ===
    -- Predict future LTV based on current trajectory
    CASE
        WHEN ltv.lifetime_bookings = 1 THEN
            ROUND(ltv.total_ltv_gross_brl * 2.5, 2)  -- First-timers who return typically do 2-3 more bookings
        WHEN ltv.days_since_last_booking <= 180 THEN
            ROUND(ltv.total_ltv_gross_brl + (ltv.avg_booking_value_brl * 2), 2)  -- Active guests: predict 2 more bookings
        ELSE
            ltv.total_ltv_gross_brl  -- Inactive guests: no growth expected
    END as predicted_future_ltv_brl,

    -- === RETENTION PRIORITY SCORE (0-100) ===
    -- Higher score = higher priority for retention campaigns
    ROUND(
        -- High LTV gets more weight (40%)
        (MIN(ltv.total_ltv_gross_brl / 5000.0, 1.0) * 40) +
        -- Recent activity is important (25%)
        (CASE
            WHEN ltv.days_since_last_booking <= 30 THEN 25
            WHEN ltv.days_since_last_booking <= 90 THEN 20
            WHEN ltv.days_since_last_booking <= 180 THEN 10
            ELSE 0
        END) +
        -- Repeat guests are valuable (20%)
        (MIN(ltv.lifetime_bookings / 5.0, 1.0) * 20) +
        -- High satisfaction matters (15%)
        ((ltv.avg_guest_rating / 5.0) * 15)
    , 1) as retention_priority_score,

    -- === ACTION RECOMMENDATIONS ===
    CASE
        WHEN ltv.total_ltv_gross_brl >= 4000 AND ltv.days_since_last_booking > 90 THEN 'URGENT: VIP re-engagement needed'
        WHEN ltv.total_ltv_gross_brl >= 2500 AND ltv.days_since_last_booking > 180 THEN 'Priority: Win-back campaign'
        WHEN ltv.lifetime_bookings = 1 AND ltv.days_since_last_booking > 60 THEN 'Opportunity: Convert to repeat guest'
        WHEN ltv.days_since_last_booking <= 30 THEN 'Maintain: Continue current engagement'
        WHEN ltv.days_since_last_booking > 365 THEN 'Low Priority: Likely churned'
        ELSE 'Monitor: Regular check-in'
    END as recommended_action

FROM day07_guest_ltv_summary ltv
JOIN day07_guests g ON ltv.guest_id = g.guest_id
ORDER BY ltv.total_ltv_gross_brl DESC, ltv.last_booking_date DESC;

-- ============================================================================
-- BUSINESS INSIGHTS & USAGE
-- ============================================================================
--
-- This view enables Carol to answer questions like:
--
-- 1. "Who are my top 20 guests by lifetime value?"
--    → ORDER BY total_ltv_gross_brl DESC LIMIT 20
--
-- 2. "Which high-value guests haven't booked recently?"
--    → WHERE ltv_segment IN ('VIP', 'High Value') AND engagement_status = 'At Risk'
--
-- 3. "Which first-time guests should I target for repeat visits?"
--    → WHERE loyalty_segment = 'First-Timer' AND first_booking_value_brl > 1500
--
-- 4. "Are guests spending more or less over time?"
--    → Check value_change_pct and value_change_brl
--
-- 5. "What's the predicted lifetime value of my active guests?"
--    → SUM(predicted_future_ltv_brl) WHERE engagement_status = 'Active'
--
-- 6. "Which guests should I prioritize for retention campaigns?"
--    → ORDER BY retention_priority_score DESC LIMIT 50
--
-- Sample Query:
-- SELECT guest_id, first_name, last_name, total_ltv_gross_brl,
--        lifetime_bookings, recommended_action
-- FROM day07_guest_ltv_analysis
-- WHERE retention_priority_score >= 70
-- ORDER BY retention_priority_score DESC;
-- ============================================================================
