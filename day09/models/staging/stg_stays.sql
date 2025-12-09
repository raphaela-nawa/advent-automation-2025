{{
  config(
    materialized='view',
    tags=['staging', 'operations']
  )
}}

WITH source AS (
    SELECT * FROM stays
),

renamed AS (
    SELECT
        stay_id AS day09_stay_id,
        booking_id AS day09_booking_id,
        platform AS day09_platform,
        property_id AS day09_property_id,
        guest_id AS day09_guest_id,
        check_in_timestamp AS day09_check_in_timestamp,
        check_out_timestamp AS day09_check_out_timestamp,
        num_guests AS day09_num_guests,
        stay_status AS day09_stay_status

    FROM source
)

SELECT * FROM renamed
