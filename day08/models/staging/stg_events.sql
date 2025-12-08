-- Day 08 - Staging: Events
-- Clean and standardize event tracking data

{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day08_saas', 'raw_events') }}
),

renamed AS (
    SELECT
        event_id AS day08_event_id,
        user_id AS day08_user_id,
        event_type AS day08_event_type,
        event_date AS day08_event_date,
        event_timestamp AS day08_event_timestamp,
        feature_name AS day08_feature_name,

        -- Derived fields
        CAST(strftime('%Y', event_date) AS INTEGER) AS day08_event_year,
        CAST(strftime('%m', event_date) AS INTEGER) AS day08_event_month,
        CAST(strftime('%w', event_date) AS INTEGER) AS day08_event_day_of_week,
        date(event_date, 'start of month') AS day08_event_month_start

    FROM source
)

SELECT * FROM renamed
