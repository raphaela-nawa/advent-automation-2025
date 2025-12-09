{{
  config(
    materialized='view',
    tags=['intermediate', 'funnel']
  )
}}

/*
    Funnel Events Model
    -------------------
    Combines all funnel stages: Inquiry → Booking → Check-in → Check-out → Review
    Creates a unified event stream for funnel analysis.
*/

WITH airbnb_inquiries AS (
    SELECT
        day09_inquiry_id AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_inquiry_timestamp AS event_timestamp,
        'inquiry' AS stage,
        NULL AS booking_id,
        NULL AS final_booking_value
    FROM {{ ref('stg_airbnb_inquiries') }}
),

booking_com_inquiries AS (
    SELECT
        day09_inquiry_id AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_inquiry_timestamp AS event_timestamp,
        'inquiry' AS stage,
        NULL AS booking_id,
        NULL AS final_booking_value
    FROM {{ ref('stg_booking_com_inquiries') }}
),

bookings AS (
    SELECT
        day09_booking_id AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_booking_timestamp AS event_timestamp,
        'booking' AS stage,
        day09_booking_id AS booking_id,
        day09_total_price AS final_booking_value
    FROM {{ ref('int_unified_reservations') }}
),

check_ins AS (
    SELECT
        day09_stay_id || '_checkin' AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_check_in_timestamp AS event_timestamp,
        'check_in' AS stage,
        day09_booking_id AS booking_id,
        NULL AS final_booking_value
    FROM {{ ref('stg_stays') }}
    WHERE day09_check_in_timestamp IS NOT NULL
),

check_outs AS (
    SELECT
        day09_stay_id || '_checkout' AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_check_out_timestamp AS event_timestamp,
        'check_out' AS stage,
        day09_booking_id AS booking_id,
        NULL AS final_booking_value
    FROM {{ ref('stg_stays') }}
    WHERE day09_check_out_timestamp IS NOT NULL
        AND day09_stay_status = 'completed'
),

reviews AS (
    SELECT
        day09_review_id AS event_id,
        day09_platform AS platform,
        day09_guest_id AS guest_id,
        day09_property_id AS property_id,
        day09_review_timestamp AS event_timestamp,
        'review' AS stage,
        day09_booking_id AS booking_id,
        NULL AS final_booking_value
    FROM {{ ref('stg_reviews') }}
),

all_events AS (
    SELECT * FROM airbnb_inquiries
    UNION ALL
    SELECT * FROM booking_com_inquiries
    UNION ALL
    SELECT * FROM bookings
    UNION ALL
    SELECT * FROM check_ins
    UNION ALL
    SELECT * FROM check_outs
    UNION ALL
    SELECT * FROM reviews
),

enriched AS (
    SELECT
        event_id AS day09_event_id,
        platform AS day09_platform,
        guest_id AS day09_guest_id,
        property_id AS day09_property_id,
        event_timestamp AS day09_event_timestamp,
        stage AS day09_stage,
        booking_id AS day09_booking_id,
        final_booking_value AS day09_final_booking_value,

        -- Calculate time to next stage (using LEAD)
        JULIANDAY(LEAD(event_timestamp) OVER (
            PARTITION BY guest_id, property_id
            ORDER BY event_timestamp
        )) - JULIANDAY(event_timestamp) AS day09_days_to_next_stage,

        -- Did this event convert to the next stage?
        CASE
            WHEN LEAD(stage) OVER (PARTITION BY guest_id, property_id ORDER BY event_timestamp) IS NOT NULL
            THEN 1
            ELSE 0
        END AS day09_converted_to_next_stage

    FROM all_events
)

SELECT * FROM enriched
ORDER BY day09_event_timestamp
