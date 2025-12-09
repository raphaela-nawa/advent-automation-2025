{{
  config(
    materialized='view',
    tags=['staging', 'airbnb']
  )
}}

WITH source AS (
    SELECT * FROM airbnb_bookings
),

renamed AS (
    SELECT
        booking_id AS day09_booking_id,
        'airbnb' AS day09_platform,
        guest_id AS day09_guest_id,
        property_id AS day09_property_id,
        booking_timestamp AS day09_booking_timestamp,
        check_in_date AS day09_check_in_date,
        check_out_date AS day09_check_out_date,
        num_guests AS day09_num_guests,
        nights AS day09_nights,
        nightly_rate AS day09_nightly_rate,
        total_price AS day09_total_price,
        platform_fee AS day09_platform_fee,
        net_revenue AS day09_net_revenue,
        status AS day09_status

    FROM source
)

SELECT * FROM renamed
