-- Day 08 - Intermediate: Funnel Steps
-- Combine user and event data to track funnel progression

{{ config(materialized='view') }}

WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

events AS (
    SELECT * FROM {{ ref('stg_events') }}
),

funnel_events AS (
    SELECT
        e.day08_user_id,
        u.day08_cohort_month,
        u.day08_signup_date,
        u.day08_utm_source,
        u.day08_utm_campaign,
        e.day08_event_type,
        e.day08_event_date,
        e.day08_event_timestamp,

        -- Calculate days from signup to each event
        julianday(e.day08_event_date) - julianday(u.day08_signup_date) AS day08_days_since_signup,

        -- Flag funnel stages
        CASE WHEN e.day08_event_type = 'visit' THEN 1 ELSE 0 END AS day08_is_visit,
        CASE WHEN e.day08_event_type = 'signup' THEN 1 ELSE 0 END AS day08_is_signup,
        CASE WHEN e.day08_event_type = 'activated' THEN 1 ELSE 0 END AS day08_is_activated,
        CASE WHEN e.day08_event_type = 'paid' THEN 1 ELSE 0 END AS day08_is_paid

    FROM events e
    INNER JOIN users u ON e.day08_user_id = u.day08_user_id
    WHERE e.day08_event_type IN ('visit', 'signup', 'activated', 'paid')
)

SELECT * FROM funnel_events
