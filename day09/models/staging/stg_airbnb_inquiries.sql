{{
  config(
    materialized='view',
    tags=['staging', 'airbnb']
  )
}}

WITH source AS (
    SELECT * FROM airbnb_inquiries
),

renamed AS (
    SELECT
        inquiry_id AS day09_inquiry_id,
        'airbnb' AS day09_platform,
        guest_id AS day09_guest_id,
        guest_name AS day09_guest_name,
        property_id AS day09_property_id,
        inquiry_timestamp AS day09_inquiry_timestamp,
        check_in_date AS day09_check_in_date,
        check_out_date AS day09_check_out_date,
        num_guests AS day09_num_guests,
        status AS day09_status

    FROM source
)

SELECT * FROM renamed
