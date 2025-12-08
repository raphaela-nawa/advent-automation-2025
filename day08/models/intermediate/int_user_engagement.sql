-- Day 08 - Intermediate: User Engagement
-- Calculate engagement metrics (DAU, WAU, MAU) by cohort

{{ config(materialized='view') }}

WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

events AS (
    SELECT * FROM {{ ref('stg_events') }}
),

engagement_events AS (
    SELECT
        e.day08_user_id,
        u.day08_cohort_month,
        e.day08_event_date,
        e.day08_event_month_start,
        e.day08_event_type,

        -- Calculate months since signup
        CAST(
            (julianday(e.day08_event_date) - julianday(u.day08_signup_date)) / 30.0
            AS INTEGER
        ) AS day08_months_since_signup,

        -- Calculate weeks since signup
        CAST(
            (julianday(e.day08_event_date) - julianday(u.day08_signup_date)) / 7.0
            AS INTEGER
        ) AS day08_weeks_since_signup,

        -- Calculate days since signup
        julianday(e.day08_event_date) - julianday(u.day08_signup_date) AS day08_days_since_signup

    FROM events e
    INNER JOIN users u ON e.day08_user_id = u.day08_user_id
    WHERE e.day08_event_type IN ('daily_active', 'feature_used', 'paid')
),

daily_engagement AS (
    SELECT
        day08_user_id,
        day08_cohort_month,
        day08_event_date,
        day08_months_since_signup,
        COUNT(*) AS day08_events_count

    FROM engagement_events
    GROUP BY
        day08_user_id,
        day08_cohort_month,
        day08_event_date,
        day08_months_since_signup
),

monthly_engagement AS (
    SELECT
        day08_user_id,
        day08_cohort_month,
        day08_event_month_start,
        day08_months_since_signup,
        COUNT(*) AS day08_monthly_events_count

    FROM engagement_events
    GROUP BY
        day08_user_id,
        day08_cohort_month,
        day08_event_month_start,
        day08_months_since_signup
)

SELECT
    de.day08_user_id,
    de.day08_cohort_month,
    de.day08_event_date,
    de.day08_months_since_signup,
    de.day08_events_count AS day08_daily_events,
    me.day08_monthly_events_count AS day08_monthly_events,

    -- DAU flag (active if any events on that day)
    CASE WHEN de.day08_events_count > 0 THEN 1 ELSE 0 END AS day08_is_dau,

    -- MAU flag (active if any events in that month)
    CASE WHEN me.day08_monthly_events_count > 0 THEN 1 ELSE 0 END AS day08_is_mau

FROM daily_engagement de
LEFT JOIN monthly_engagement me
    ON de.day08_user_id = me.day08_user_id
    AND de.day08_cohort_month = me.day08_cohort_month
    AND de.day08_months_since_signup = me.day08_months_since_signup
