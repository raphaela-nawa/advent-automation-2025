{{
  config(
    materialized='view',
    tags=['intermediate', 'unification']
  )
}}

/*
    Platform Unification Logic
    ---------------------------
    This model unifies bookings from Airbnb and Booking.com into a common schema.
    Key unification decisions:
    - guest_id: Airbnb uses guest_id, Booking.com uses guest_email
    - property_id: Both use property_id (Booking.com property_code renamed)
    - Pricing: Airbnb uses total_price/platform_fee, Booking.com uses total_amount/commission
    - Status: Both use status field (booking_status renamed for Booking.com)
*/

WITH airbnb AS (
    SELECT * FROM {{ ref('stg_airbnb_bookings') }}
),

booking_com AS (
    SELECT * FROM {{ ref('stg_booking_com_bookings') }}
),

unified AS (
    -- Airbnb bookings
    SELECT
        day09_booking_id,
        day09_platform,
        day09_guest_id,
        day09_property_id,
        day09_booking_timestamp,
        day09_check_in_date,
        day09_check_out_date,
        day09_num_guests,
        day09_nights,
        day09_nightly_rate,
        day09_total_price,
        day09_platform_fee,
        day09_net_revenue,
        day09_status
    FROM airbnb

    UNION ALL

    -- Booking.com bookings
    SELECT
        day09_booking_id,
        day09_platform,
        day09_guest_id,
        day09_property_id,
        day09_booking_timestamp,
        day09_check_in_date,
        day09_check_out_date,
        day09_num_guests,
        day09_nights,
        day09_nightly_rate,
        day09_total_price,
        day09_platform_fee,
        day09_net_revenue,
        day09_status
    FROM booking_com
),

enriched AS (
    SELECT
        *,
        -- Calculate ADR (Average Daily Rate)
        CASE
            WHEN day09_nights > 0 THEN ROUND(day09_total_price / day09_nights, 2)
            ELSE 0
        END AS day09_adr,

        -- Calculate booking lead time (days between booking and check-in)
        JULIANDAY(day09_check_in_date) - JULIANDAY(DATE(day09_booking_timestamp)) AS day09_lead_time_days,

        -- Calculate length of stay
        day09_nights AS day09_length_of_stay,

        -- Normalize check-in date to month for cohort analysis
        DATE(day09_check_in_date, 'start of month') AS day09_check_in_month

    FROM unified
)

SELECT * FROM enriched
