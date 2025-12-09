{{
  config(
    materialized='view',
    tags=['staging', 'operations']
  )
}}

WITH source AS (
    SELECT * FROM reviews
),

renamed AS (
    SELECT
        review_id AS day09_review_id,
        stay_id AS day09_stay_id,
        booking_id AS day09_booking_id,
        platform AS day09_platform,
        property_id AS day09_property_id,
        guest_id AS day09_guest_id,
        review_timestamp AS day09_review_timestamp,
        rating AS day09_rating,
        comment AS day09_comment

    FROM source
)

SELECT * FROM renamed
