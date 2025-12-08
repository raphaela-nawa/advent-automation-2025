-- Day 08 - Marts: Acquisition Funnel
-- Track conversion through Visit → Signup → Activation → Paid by cohort
-- INCREMENTAL MODEL: Only processes new cohort months

{{
  config(
    materialized='incremental',
    unique_key='day08_cohort_month',
    on_schema_change='append_new_columns'
  )
}}

WITH funnel_steps AS (
    SELECT * FROM {{ ref('int_funnel_steps') }}

    {% if is_incremental() %}
    -- Only process new cohorts when running incrementally
    WHERE day08_cohort_month > (SELECT MAX(day08_cohort_month) FROM {{ this }})
    {% endif %}
),

cohort_funnel AS (
    SELECT
        day08_cohort_month,

        -- Funnel stage counts
        COUNT(DISTINCT CASE WHEN day08_is_visit = 1 THEN day08_user_id END) AS day08_visitors,
        COUNT(DISTINCT CASE WHEN day08_is_signup = 1 THEN day08_user_id END) AS day08_signups,
        COUNT(DISTINCT CASE WHEN day08_is_activated = 1 THEN day08_user_id END) AS day08_activated,
        COUNT(DISTINCT CASE WHEN day08_is_paid = 1 THEN day08_user_id END) AS day08_paid,

        -- Attribution breakdown
        COUNT(DISTINCT CASE WHEN day08_utm_source = 'google' THEN day08_user_id END) AS day08_google_visitors,
        COUNT(DISTINCT CASE WHEN day08_utm_source = 'facebook' THEN day08_user_id END) AS day08_facebook_visitors,
        COUNT(DISTINCT CASE WHEN day08_utm_source = 'organic' THEN day08_user_id END) AS day08_organic_visitors

    FROM funnel_steps
    GROUP BY day08_cohort_month
)

SELECT
    day08_cohort_month,
    day08_visitors,
    day08_signups,
    day08_activated,
    day08_paid,
    day08_google_visitors,
    day08_facebook_visitors,
    day08_organic_visitors,

    -- Conversion rates
    ROUND(100.0 * day08_signups / NULLIF(day08_visitors, 0), 2) AS day08_visit_to_signup_rate,
    ROUND(100.0 * day08_activated / NULLIF(day08_signups, 0), 2) AS day08_signup_to_activation_rate,
    ROUND(100.0 * day08_paid / NULLIF(day08_activated, 0), 2) AS day08_activation_to_paid_rate,
    ROUND(100.0 * day08_paid / NULLIF(day08_visitors, 0), 2) AS day08_overall_conversion_rate,

    -- Metadata
    DATETIME('now') AS day08_updated_at

FROM cohort_funnel
ORDER BY day08_cohort_month
