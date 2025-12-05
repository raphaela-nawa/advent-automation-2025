-- ============================================================================
-- Day 07: Retention Matrix Model for Carol's Pousada
-- ============================================================================
-- Business Purpose:
--   Create a cohort retention matrix showing what percentage of each cohort
--   returns after 1, 3, 6, and 12 months to:
--   - Identify which cohorts have the best retention
--   - Understand typical return patterns (how long until next visit)
--   - Measure effectiveness of retention campaigns
--   - Compare seasonal cohorts (winter vs. summer acquisition)
--
-- Stakeholder: Carol (Pousada Owner)
-- Use Case: Track and improve guest retention, benchmark against goals
-- ============================================================================

-- ============================================================================
-- STEP 1: Identify First and Subsequent Bookings per Guest
-- ============================================================================
-- For retention analysis, we need to know when each guest first booked
-- and when they returned

DROP VIEW IF EXISTS day07_retention_matrix;
CREATE VIEW day07_retention_matrix AS

WITH day07_guest_first_booking AS (
    SELECT
        guest_id,
        MIN(booking_date) as first_booking_date,
        MIN(check_in_date) as first_check_in_date,
        STRFTIME('%Y-%m', MIN(booking_date)) as cohort_month,
        CAST(STRFTIME('%Y', MIN(booking_date)) AS INTEGER) as cohort_year,
        CAST(STRFTIME('%m', MIN(booking_date)) AS INTEGER) as cohort_month_num
    FROM day07_bookings
    WHERE status != 'Cancelled'
    GROUP BY guest_id
),

-- ============================================================================
-- STEP 2: Get All Return Bookings with Time Since First Booking
-- ============================================================================
-- For each booking after the first, calculate how many months have passed

day07_return_bookings AS (
    SELECT
        fb.guest_id,
        fb.cohort_month,
        fb.first_booking_date,
        b.booking_id,
        b.booking_date as return_booking_date,

        -- Calculate months between first booking and this booking
        CAST(
            (JULIANDAY(b.booking_date) - JULIANDAY(fb.first_booking_date)) / 30.44
        AS INTEGER) as months_since_first,

        -- Also track days for more precise analysis
        CAST(JULIANDAY(b.booking_date) - JULIANDAY(fb.first_booking_date) AS INTEGER) as days_since_first,

        -- Booking details
        b.total_price_brl,
        b.room_type

    FROM day07_guest_first_booking fb
    JOIN day07_bookings b ON fb.guest_id = b.guest_id
    WHERE
        b.status != 'Cancelled'
        AND b.booking_date > fb.first_booking_date  -- Only bookings AFTER the first
),

-- ============================================================================
-- STEP 3: Calculate Retention Flags for Standard Time Windows
-- ============================================================================
-- Mark whether each guest returned within key time windows

day07_retention_flags AS (
    SELECT
        guest_id,
        cohort_month,
        first_booking_date,

        -- Count return bookings
        COUNT(DISTINCT booking_id) as total_return_bookings,

        -- Retention windows (1M, 3M, 6M, 12M)
        MAX(CASE WHEN days_since_first BETWEEN 0 AND 30 THEN 1 ELSE 0 END) as returned_within_1month,
        MAX(CASE WHEN days_since_first BETWEEN 31 AND 90 THEN 1 ELSE 0 END) as returned_1to3months,
        MAX(CASE WHEN days_since_first BETWEEN 0 AND 90 THEN 1 ELSE 0 END) as returned_within_3months,
        MAX(CASE WHEN days_since_first BETWEEN 91 AND 180 THEN 1 ELSE 0 END) as returned_3to6months,
        MAX(CASE WHEN days_since_first BETWEEN 0 AND 180 THEN 1 ELSE 0 END) as returned_within_6months,
        MAX(CASE WHEN days_since_first BETWEEN 181 AND 365 THEN 1 ELSE 0 END) as returned_6to12months,
        MAX(CASE WHEN days_since_first BETWEEN 0 AND 365 THEN 1 ELSE 0 END) as returned_within_12months,
        MAX(CASE WHEN days_since_first > 365 THEN 1 ELSE 0 END) as returned_after_12months,

        -- First return metrics
        MIN(days_since_first) as days_to_first_return,
        MIN(CASE WHEN days_since_first > 0 THEN return_booking_date END) as first_return_date,
        SUM(total_price_brl) as total_return_revenue_brl

    FROM day07_return_bookings
    GROUP BY guest_id, cohort_month, first_booking_date
),

-- ============================================================================
-- STEP 4: Calculate Cohort Size and Retention Counts
-- ============================================================================
-- Aggregate to cohort level to calculate retention percentages

day07_cohort_retention_counts AS (
    SELECT
        fb.cohort_month,
        fb.cohort_year,
        fb.cohort_month_num,

        -- Total cohort size (denominator for retention %)
        COUNT(DISTINCT fb.guest_id) as cohort_size,

        -- How many guests returned at each window
        COUNT(DISTINCT CASE WHEN rf.returned_within_1month = 1 THEN fb.guest_id END) as returned_1m,
        COUNT(DISTINCT CASE WHEN rf.returned_within_3months = 1 THEN fb.guest_id END) as returned_3m,
        COUNT(DISTINCT CASE WHEN rf.returned_within_6months = 1 THEN fb.guest_id END) as returned_6m,
        COUNT(DISTINCT CASE WHEN rf.returned_within_12months = 1 THEN fb.guest_id END) as returned_12m,

        -- Incremental returns (returned in this window but not before)
        COUNT(DISTINCT CASE WHEN rf.returned_1to3months = 1 AND rf.returned_within_1month = 0 THEN fb.guest_id END) as new_returns_1to3m,
        COUNT(DISTINCT CASE WHEN rf.returned_3to6months = 1 AND rf.returned_within_3months = 0 THEN fb.guest_id END) as new_returns_3to6m,
        COUNT(DISTINCT CASE WHEN rf.returned_6to12months = 1 AND rf.returned_within_6months = 0 THEN fb.guest_id END) as new_returns_6to12m,

        -- Ever returned (any time)
        COUNT(DISTINCT CASE WHEN rf.guest_id IS NOT NULL THEN fb.guest_id END) as total_returned,

        -- Revenue from returning guests
        COALESCE(SUM(rf.total_return_revenue_brl), 0) as total_return_revenue_brl,

        -- Average time to first return
        ROUND(AVG(rf.days_to_first_return), 1) as avg_days_to_first_return

    FROM day07_guest_first_booking fb
    LEFT JOIN day07_retention_flags rf ON fb.guest_id = rf.guest_id
    GROUP BY fb.cohort_month, fb.cohort_year, fb.cohort_month_num
),

-- ============================================================================
-- STEP 5: Calculate Retention Percentages
-- ============================================================================
-- Convert counts to percentages for easy interpretation

day07_cohort_retention_rates AS (
    SELECT
        cohort_month,
        cohort_year,
        cohort_month_num,
        cohort_size,

        -- === RETENTION RATES (% of cohort) ===
        ROUND(100.0 * returned_1m / cohort_size, 1) as retention_1m_pct,
        ROUND(100.0 * returned_3m / cohort_size, 1) as retention_3m_pct,
        ROUND(100.0 * returned_6m / cohort_size, 1) as retention_6m_pct,
        ROUND(100.0 * returned_12m / cohort_size, 1) as retention_12m_pct,
        ROUND(100.0 * total_returned / cohort_size, 1) as retention_ever_pct,

        -- === RAW COUNTS ===
        returned_1m,
        returned_3m,
        returned_6m,
        returned_12m,
        total_returned,

        -- === INCREMENTAL RETURNS (new in each period) ===
        new_returns_1to3m,
        new_returns_3to6m,
        new_returns_6to12m,

        -- === VALUE METRICS ===
        total_return_revenue_brl,
        ROUND(total_return_revenue_brl / NULLIF(total_returned, 0), 2) as avg_return_revenue_per_guest_brl,

        -- === TIME METRICS ===
        avg_days_to_first_return,
        ROUND(avg_days_to_first_return / 30.44, 1) as avg_months_to_first_return,

        -- === RETENTION SCORE (0-100) ===
        -- Composite score: weighted average of retention across all periods
        ROUND(
            (100.0 * returned_1m / cohort_size * 0.40) +   -- 1M retention: 40% weight
            (100.0 * returned_3m / cohort_size * 0.25) +   -- 3M retention: 25% weight
            (100.0 * returned_6m / cohort_size * 0.20) +   -- 6M retention: 20% weight
            (100.0 * returned_12m / cohort_size * 0.15)    -- 12M retention: 15% weight
        , 1) as retention_score,

        -- === SEASONALITY ===
        CASE
            WHEN cohort_month_num IN (6, 7, 8) THEN 'High (Winter)'
            WHEN cohort_month_num IN (12, 1) THEN 'High (Summer)'
            ELSE 'Low'
        END as season_category

    FROM day07_cohort_retention_counts
)

-- ============================================================================
-- FINAL OUTPUT: Retention Matrix with Trend Analysis
-- ============================================================================
-- Add month-over-month comparisons and trend indicators

SELECT
    cohort_month,
    cohort_year,
    cohort_month_num,
    season_category,
    cohort_size,

    -- === RETENTION MATRIX (Main Output) ===
    retention_1m_pct,
    returned_1m,
    retention_3m_pct,
    returned_3m,
    retention_6m_pct,
    returned_6m,
    retention_12m_pct,
    returned_12m,
    retention_ever_pct,
    total_returned,

    -- === INCREMENTAL RETENTION (Period-over-Period) ===
    -- Shows how many NEW guests returned in each subsequent period
    returned_1m as new_guests_0to1m,
    new_returns_1to3m as new_guests_1to3m,
    new_returns_3to6m as new_guests_3to6m,
    new_returns_6to12m as new_guests_6to12m,

    -- === RETENTION CURVE SHAPE ===
    -- Indicates whether retention accelerates or decelerates over time
    CASE
        WHEN retention_3m_pct - retention_1m_pct > 10 THEN 'Fast Growth (1-3M)'
        WHEN retention_6m_pct - retention_3m_pct > 10 THEN 'Fast Growth (3-6M)'
        WHEN retention_12m_pct - retention_6m_pct > 10 THEN 'Late Bloomers (6-12M)'
        WHEN retention_3m_pct < 5 THEN 'Poor Early Retention'
        ELSE 'Steady Growth'
    END as retention_pattern,

    -- === VALUE METRICS ===
    total_return_revenue_brl,
    avg_return_revenue_per_guest_brl,
    ROUND(total_return_revenue_brl / cohort_size, 2) as return_revenue_per_cohort_member_brl,

    -- === TIME TO RETURN ===
    avg_days_to_first_return,
    avg_months_to_first_return,
    CASE
        WHEN avg_days_to_first_return <= 30 THEN 'Fast (≤ 1 month)'
        WHEN avg_days_to_first_return <= 90 THEN 'Normal (1-3 months)'
        WHEN avg_days_to_first_return <= 180 THEN 'Slow (3-6 months)'
        ELSE 'Very Slow (> 6 months)'
    END as return_speed,

    -- === COMPOSITE SCORE ===
    retention_score,

    -- === COMPARISON TO TARGETS (from config) ===
    -- Target: 15% @ 1M, 25% @ 3M, 35% @ 6M, 40% @ 12M
    CASE WHEN retention_1m_pct >= 15 THEN '✓' ELSE '✗' END as meets_1m_target,
    CASE WHEN retention_3m_pct >= 25 THEN '✓' ELSE '✗' END as meets_3m_target,
    CASE WHEN retention_6m_pct >= 35 THEN '✓' ELSE '✗' END as meets_6m_target,
    CASE WHEN retention_12m_pct >= 40 THEN '✓' ELSE '✗' END as meets_12m_target,

    -- === PERFORMANCE VS TARGETS ===
    ROUND(retention_1m_pct - 15, 1) as variance_from_1m_target,
    ROUND(retention_3m_pct - 25, 1) as variance_from_3m_target,
    ROUND(retention_6m_pct - 35, 1) as variance_from_6m_target,
    ROUND(retention_12m_pct - 40, 1) as variance_from_12m_target,

    -- === TREND COMPARISON (Compare to previous cohort) ===
    LAG(retention_3m_pct) OVER (ORDER BY cohort_year, cohort_month_num) as prev_cohort_retention_3m_pct,
    ROUND(
        retention_3m_pct - LAG(retention_3m_pct) OVER (ORDER BY cohort_year, cohort_month_num),
    1) as retention_3m_change_vs_prev,

    -- === ACTION RECOMMENDATIONS ===
    CASE
        WHEN retention_score >= 70 THEN 'Excellent - Maintain strategy'
        WHEN retention_score >= 50 AND retention_3m_pct < 25 THEN 'Good overall - Improve early retention'
        WHEN retention_score >= 50 THEN 'Good - Continue monitoring'
        WHEN retention_1m_pct < 10 THEN 'URGENT - Fix immediate follow-up'
        WHEN retention_3m_pct < 20 THEN 'Priority - Enhance 90-day engagement'
        WHEN retention_6m_pct < 30 THEN 'Action needed - Long-term retention weak'
        ELSE 'Review - Below average performance'
    END as recommended_action,

    -- === DATA MATURITY ===
    -- Indicates if cohort has existed long enough for each metric to be meaningful
    CASE
        WHEN JULIANDAY('now') - JULIANDAY(cohort_month || '-01') >= 30 THEN 'Mature'
        ELSE 'Immature'
    END as retention_1m_maturity,
    CASE
        WHEN JULIANDAY('now') - JULIANDAY(cohort_month || '-01') >= 90 THEN 'Mature'
        ELSE 'Immature'
    END as retention_3m_maturity,
    CASE
        WHEN JULIANDAY('now') - JULIANDAY(cohort_month || '-01') >= 180 THEN 'Mature'
        ELSE 'Immature'
    END as retention_6m_maturity,
    CASE
        WHEN JULIANDAY('now') - JULIANDAY(cohort_month || '-01') >= 365 THEN 'Mature'
        ELSE 'Immature'
    END as retention_12m_maturity

FROM day07_cohort_retention_rates
ORDER BY cohort_year, cohort_month_num;

-- ============================================================================
-- BUSINESS INSIGHTS & USAGE
-- ============================================================================
--
-- This retention matrix enables Carol to answer questions like:
--
-- 1. "What's my overall retention rate at 3 months?"
--    → SELECT AVG(retention_3m_pct) FROM day07_retention_matrix
--      WHERE retention_3m_maturity = 'Mature'
--
-- 2. "Which cohorts have the best retention?"
--    → ORDER BY retention_score DESC
--
-- 3. "Do winter or summer cohorts retain better?"
--    → GROUP BY season_category and compare retention_3m_pct
--
-- 4. "Am I meeting my retention targets?"
--    → Check meets_3m_target and variance_from_3m_target columns
--
-- 5. "Is retention improving month-over-month?"
--    → Look at retention_3m_change_vs_prev trend
--
-- 6. "Which cohorts need immediate attention?"
--    → WHERE recommended_action LIKE 'URGENT%' OR 'Priority%'
--
-- 7. "How long does it take for guests to return?"
--    → Check avg_months_to_first_return and return_speed
--
-- 8. "What's the typical retention curve shape?"
--    → Analyze retention_pattern distribution
--
-- Sample Query - Retention Performance Dashboard:
-- SELECT
--     cohort_month,
--     cohort_size,
--     retention_1m_pct,
--     retention_3m_pct,
--     retention_6m_pct,
--     retention_12m_pct,
--     retention_score,
--     recommended_action
-- FROM day07_retention_matrix
-- WHERE retention_3m_maturity = 'Mature'
-- ORDER BY cohort_month DESC
-- LIMIT 12;
-- ============================================================================
