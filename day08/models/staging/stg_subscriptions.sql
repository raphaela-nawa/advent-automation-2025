-- Day 08 - Staging: Subscriptions
-- Clean and standardize subscription and payment data

{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('day08_saas', 'raw_subscriptions') }}
),

renamed AS (
    SELECT
        subscription_id AS day08_subscription_id,
        user_id AS day08_user_id,
        plan_name AS day08_plan_name,
        start_date AS day08_start_date,
        end_date AS day08_end_date,
        mrr AS day08_mrr,
        status AS day08_status,

        -- Derived fields
        CASE
            WHEN end_date IS NULL THEN 1
            ELSE 0
        END AS day08_is_active,

        CASE
            WHEN end_date IS NOT NULL
            THEN julianday(end_date) - julianday(start_date)
            ELSE julianday('now') - julianday(start_date)
        END AS day08_subscription_days,

        date(start_date, 'start of month') AS day08_start_month

    FROM source
)

SELECT * FROM renamed
