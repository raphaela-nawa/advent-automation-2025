{{
  config(
    materialized='view',
    tags=['intermediate', 'performance']
  )
}}

/*
    Property Performance Model
    --------------------------
    Aggregates property-level metrics from unified reservations.
    Used for portfolio metrics and platform comparison.
*/

WITH reservations AS (
    SELECT * FROM {{ ref('int_unified_reservations') }}
    WHERE day09_status = 'completed'  -- Only completed bookings
),

stays AS (
    SELECT * FROM {{ ref('stg_stays') }}
    WHERE day09_stay_status = 'completed'  -- Only completed stays
),

reviews AS (
    SELECT * FROM {{ ref('stg_reviews') }}
),

property_bookings AS (
    SELECT
        day09_property_id,
        day09_platform,
        COUNT(*) AS booking_count,
        SUM(day09_nights) AS total_nights_booked,
        SUM(day09_total_price) AS total_revenue,
        SUM(day09_net_revenue) AS total_net_revenue,
        AVG(day09_adr) AS avg_daily_rate,
        AVG(day09_lead_time_days) AS avg_lead_time_days,
        AVG(day09_length_of_stay) AS avg_length_of_stay,
        MIN(day09_check_in_date) AS first_booking_date,
        MAX(day09_check_in_date) AS last_booking_date
    FROM reservations
    GROUP BY day09_property_id, day09_platform
),

property_reviews AS (
    SELECT
        day09_property_id,
        day09_platform,
        COUNT(*) AS review_count,
        AVG(day09_rating) AS avg_rating,
        MIN(day09_rating) AS min_rating,
        MAX(day09_rating) AS max_rating
    FROM reviews
    GROUP BY day09_property_id, day09_platform
),

property_stats AS (
    SELECT
        pb.day09_property_id,
        pb.day09_platform,
        pb.booking_count,
        pb.total_nights_booked,
        pb.total_revenue,
        pb.total_net_revenue,
        ROUND(pb.avg_daily_rate, 2) AS avg_daily_rate,
        ROUND(pb.avg_lead_time_days, 1) AS avg_lead_time_days,
        ROUND(pb.avg_length_of_stay, 1) AS avg_length_of_stay,
        pb.first_booking_date,
        pb.last_booking_date,
        COALESCE(pr.review_count, 0) AS review_count,
        ROUND(COALESCE(pr.avg_rating, 0), 1) AS avg_rating,
        pr.min_rating,
        pr.max_rating,

        -- Calculate review rate
        CASE
            WHEN pb.booking_count > 0
            THEN ROUND(100.0 * COALESCE(pr.review_count, 0) / pb.booking_count, 2)
            ELSE 0
        END AS review_rate_pct

    FROM property_bookings pb
    LEFT JOIN property_reviews pr
        ON pb.day09_property_id = pr.day09_property_id
        AND pb.day09_platform = pr.day09_platform
)

SELECT * FROM property_stats
