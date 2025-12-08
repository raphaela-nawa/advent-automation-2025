-- Day 08 - Staging: Users
-- Clean and standardize user data with signup tracking

{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day08_saas', 'raw_users') }}
),

renamed AS (
    SELECT
        user_id AS day08_user_id,
        signup_date AS day08_signup_date,
        email AS day08_email,
        utm_source AS day08_utm_source,
        utm_campaign AS day08_utm_campaign,
        first_visit_date AS day08_first_visit_date,

        -- Derived fields
        CAST(strftime('%Y', signup_date) AS INTEGER) AS day08_signup_year,
        CAST(strftime('%m', signup_date) AS INTEGER) AS day08_signup_month,
        date(signup_date, 'start of month') AS day08_cohort_month

    FROM source
)

SELECT * FROM renamed
