{{
  config(
    materialized='table',
    tags=['marts', 'metrics', 'portfolio']
  )
}}

/*
    Portfolio Metrics Mart
    -----------------------
    ** CRITICAL MODEL **

    Public-facing portfolio metrics for property managers.
    Calculates key hospitality metrics:
    - Occupancy Rate (nights booked / nights available)
    - Average Daily Rate (ADR)
    - Revenue Per Available Room (RevPAR)
    - Platform mix and performance

    This model powers the public portfolio page (Phase 1 MVP).
*/

WITH reservations AS (
    SELECT * FROM {{ ref('fct_reservations_unified') }}
),

property_nights AS (
    SELECT
        day09_property_id,
        COUNT(DISTINCT day09_booking_id) AS total_bookings,
        SUM(day09_nights) AS total_nights_booked,
        SUM(day09_total_price) AS total_revenue,
        SUM(day09_net_revenue) AS total_net_revenue,
        AVG(day09_adr) AS avg_daily_rate,
        MIN(day09_check_in_date) AS first_check_in,
        MAX(day09_check_out_date) AS last_check_out
    FROM reservations
    GROUP BY day09_property_id
),

-- Calculate available nights based on date range in data
date_range AS (
    SELECT
        MIN(day09_check_in_date) AS min_date,
        MAX(day09_check_out_date) AS max_date,
        JULIANDAY(MAX(day09_check_out_date)) - JULIANDAY(MIN(day09_check_in_date)) AS days_in_range
    FROM reservations
),

-- Platform split per property
platform_revenue AS (
    SELECT
        day09_property_id,
        day09_platform,
        COUNT(*) AS bookings_by_platform,
        SUM(day09_total_price) AS revenue_by_platform
    FROM reservations
    GROUP BY day09_property_id, day09_platform
),

property_metrics AS (
    SELECT
        pn.day09_property_id,
        pn.total_bookings,
        pn.total_nights_booked,

        -- Calculate nights available (using actual date range from data)
        CAST(dr.days_in_range AS INTEGER) AS day09_nights_available,

        -- Occupancy Rate: (nights booked / nights available) * 100
        ROUND(
            100.0 * pn.total_nights_booked / NULLIF(dr.days_in_range, 0),
            2
        ) AS day09_occupancy_rate_pct,

        -- Average Daily Rate (ADR)
        ROUND(pn.avg_daily_rate, 2) AS day09_avg_daily_rate,

        -- Revenue Per Available Room (RevPAR) = ADR × Occupancy Rate
        ROUND(
            pn.avg_daily_rate * (pn.total_nights_booked / NULLIF(dr.days_in_range, 0)),
            2
        ) AS day09_revpar,

        -- Total revenues
        pn.total_revenue AS day09_total_revenue,
        pn.total_net_revenue AS day09_total_net_revenue,

        -- Platform fees
        (pn.total_revenue - pn.total_net_revenue) AS day09_total_platform_fees,
        ROUND(
            100.0 * (pn.total_revenue - pn.total_net_revenue) / NULLIF(pn.total_revenue, 0),
            2
        ) AS day09_platform_fee_pct,

        -- Date range
        pn.first_check_in AS day09_first_check_in,
        pn.last_check_out AS day09_last_check_out

    FROM property_nights pn
    CROSS JOIN date_range dr
),

-- Add platform mix
platform_mix AS (
    SELECT
        day09_property_id,
        MAX(CASE WHEN day09_platform = 'airbnb' THEN bookings_by_platform ELSE 0 END) AS airbnb_bookings,
        MAX(CASE WHEN day09_platform = 'booking_com' THEN bookings_by_platform ELSE 0 END) AS booking_com_bookings,
        MAX(CASE WHEN day09_platform = 'airbnb' THEN revenue_by_platform ELSE 0 END) AS airbnb_revenue,
        MAX(CASE WHEN day09_platform = 'booking_com' THEN revenue_by_platform ELSE 0 END) AS booking_com_revenue
    FROM platform_revenue
    GROUP BY day09_property_id
)

SELECT
    pm.*,
    COALESCE(plm.airbnb_bookings, 0) AS day09_airbnb_bookings,
    COALESCE(plm.booking_com_bookings, 0) AS day09_booking_com_bookings,
    COALESCE(plm.airbnb_revenue, 0) AS day09_airbnb_revenue,
    COALESCE(plm.booking_com_revenue, 0) AS day09_booking_com_revenue,

    -- Calculate platform mix percentages
    ROUND(
        100.0 * COALESCE(plm.airbnb_revenue, 0) / NULLIF(pm.day09_total_revenue, 0),
        2
    ) AS day09_airbnb_revenue_pct,
    ROUND(
        100.0 * COALESCE(plm.booking_com_revenue, 0) / NULLIF(pm.day09_total_revenue, 0),
        2
    ) AS day09_booking_com_revenue_pct

FROM property_metrics pm
LEFT JOIN platform_mix plm
    ON pm.day09_property_id = plm.day09_property_id
ORDER BY pm.day09_total_revenue DESC
