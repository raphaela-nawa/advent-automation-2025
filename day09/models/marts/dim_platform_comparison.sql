{{
  config(
    materialized='table',
    tags=['marts', 'dimensions']
  )
}}

/*
    Platform Comparison Dimension
    ------------------------------
    Compares performance metrics between Airbnb and Booking.com.
    Key metrics:
    - Booking volume
    - Revenue generation
    - Average booking value
    - Commission rates
    - Lead time differences
*/

WITH platform_stats AS (
    SELECT
        day09_platform,
        COUNT(*) AS total_bookings,
        SUM(day09_nights) AS total_nights,
        SUM(day09_total_price) AS total_revenue,
        SUM(day09_platform_fee) AS total_fees,
        SUM(day09_net_revenue) AS total_net_revenue,
        AVG(day09_total_price) AS avg_booking_value,
        AVG(day09_adr) AS avg_daily_rate,
        AVG(day09_nights) AS avg_length_of_stay,
        AVG(day09_lead_time_days) AS avg_lead_time_days,
        MIN(day09_booking_timestamp) AS first_booking,
        MAX(day09_booking_timestamp) AS last_booking
    FROM {{ ref('fct_reservations_unified') }}
    GROUP BY day09_platform
),

totals AS (
    SELECT
        SUM(total_bookings) AS overall_bookings,
        SUM(total_revenue) AS overall_revenue
    FROM platform_stats
)

SELECT
    ps.day09_platform,
    ps.total_bookings,

    -- Market share (bookings)
    ROUND(100.0 * ps.total_bookings / NULLIF(t.overall_bookings, 0), 2) AS day09_booking_share_pct,

    ps.total_nights,
    ps.total_revenue,

    -- Market share (revenue)
    ROUND(100.0 * ps.total_revenue / NULLIF(t.overall_revenue, 0), 2) AS day09_revenue_share_pct,

    ps.total_fees,
    ps.total_net_revenue,

    -- Effective commission rate
    ROUND(100.0 * ps.total_fees / NULLIF(ps.total_revenue, 0), 2) AS day09_commission_rate_pct,

    -- Performance metrics
    ROUND(ps.avg_booking_value, 2) AS day09_avg_booking_value,
    ROUND(ps.avg_daily_rate, 2) AS day09_avg_daily_rate,
    ROUND(ps.avg_length_of_stay, 1) AS day09_avg_length_of_stay,
    ROUND(ps.avg_lead_time_days, 1) AS day09_avg_lead_time_days,

    -- Date range
    ps.first_booking AS day09_first_booking,
    ps.last_booking AS day09_last_booking,

    -- Days active
    CAST(JULIANDAY(ps.last_booking) - JULIANDAY(ps.first_booking) AS INTEGER) AS day09_days_active

FROM platform_stats ps
CROSS JOIN totals t
ORDER BY ps.total_revenue DESC
