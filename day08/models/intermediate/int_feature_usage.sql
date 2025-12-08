-- Day 08 - Intermediate: Feature Usage
-- Track which features drive retention and engagement

{{ config(materialized='view') }}

WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

events AS (
    SELECT * FROM {{ ref('stg_events') }}
    WHERE day08_event_type = 'feature_used'
    AND day08_feature_name IS NOT NULL
),

feature_usage AS (
    SELECT
        e.day08_user_id,
        u.day08_cohort_month,
        u.day08_signup_date,
        e.day08_feature_name,
        e.day08_event_date,
        e.day08_event_timestamp,

        -- Time to first feature use
        julianday(e.day08_event_date) - julianday(u.day08_signup_date) AS day08_days_to_feature_use,

        -- Count features per user
        ROW_NUMBER() OVER (
            PARTITION BY e.day08_user_id, e.day08_feature_name
            ORDER BY e.day08_event_timestamp
        ) AS day08_feature_use_sequence

    FROM events e
    INNER JOIN users u ON e.day08_user_id = u.day08_user_id
),

first_feature_use AS (
    SELECT
        day08_user_id,
        day08_cohort_month,
        day08_feature_name,
        MIN(day08_event_date) AS day08_first_use_date,
        MIN(day08_days_to_feature_use) AS day08_days_to_first_use

    FROM feature_usage
    GROUP BY
        day08_user_id,
        day08_cohort_month,
        day08_feature_name
),

user_feature_adoption AS (
    SELECT
        day08_user_id,
        day08_cohort_month,
        COUNT(DISTINCT day08_feature_name) AS day08_features_adopted,
        MIN(day08_first_use_date) AS day08_first_feature_date,
        AVG(day08_days_to_first_use) AS day08_avg_days_to_adoption

    FROM first_feature_use
    GROUP BY
        day08_user_id,
        day08_cohort_month
)

SELECT
    fu.*,
    ufa.day08_features_adopted,
    ufa.day08_avg_days_to_adoption

FROM first_feature_use fu
LEFT JOIN user_feature_adoption ufa
    ON fu.day08_user_id = ufa.day08_user_id
    AND fu.day08_cohort_month = ufa.day08_cohort_month
