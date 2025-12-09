{{
  config(
    materialized='view',
    tags=['staging', 'booking_com']
  )
}}

WITH source AS (
    SELECT * FROM booking_com_bookings
),

renamed AS (
    SELECT
        booking_id AS day09_booking_id,
        'booking_com' AS day09_platform,
        guest_email AS day09_guest_id,  -- Unification: use email as guest_id
        property_code AS day09_property_id,  -- Unification: use property_id
        booking_timestamp AS day09_booking_timestamp,
        arrival_date AS day09_check_in_date,
        departure_date AS day09_check_out_date,
        guest_count AS day09_num_guests,
        nights AS day09_nights,
        rate_per_night AS day09_nightly_rate,
        total_amount AS day09_total_price,
        commission AS day09_platform_fee,
        host_payout AS day09_net_revenue,
        booking_status AS day09_status

    FROM source
)

SELECT * FROM renamed
