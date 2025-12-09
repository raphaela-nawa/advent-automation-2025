{{
  config(
    materialized='view',
    tags=['staging', 'booking_com']
  )
}}

WITH source AS (
    SELECT * FROM booking_com_inquiries
),

renamed AS (
    SELECT
        reservation_inquiry_id AS day09_inquiry_id,
        'booking_com' AS day09_platform,
        guest_email AS day09_guest_id,  -- Unification: use email as guest_id
        guest_name AS day09_guest_name,
        property_code AS day09_property_id,  -- Unification: use property_id
        created_at AS day09_inquiry_timestamp,
        arrival_date AS day09_check_in_date,
        departure_date AS day09_check_out_date,
        guest_count AS day09_num_guests,
        inquiry_status AS day09_status

    FROM source
)

SELECT * FROM renamed
