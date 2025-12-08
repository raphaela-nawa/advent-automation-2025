-- Day 08 - Marts: Engagement Cohorts
-- Analyze DAU/MAU rates, feature adoption, and retention by cohort over time

{{ config(materialized='table') }}

WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

engagement AS (
    SELECT * FROM {{ ref('int_user_engagement') }}
),

feature_usage AS (
    SELECT
        day08_user_id,
        day08_cohort_month,
        COUNT(DISTINCT day08_feature_name) AS day08_features_used
    FROM {{ ref('int_feature_usage') }}
    GROUP BY day08_user_id, day08_cohort_month
),

cohort_sizes AS (
    SELECT
        day08_cohort_month,
        COUNT(DISTINCT day08_user_id) AS day08_cohort_size
    FROM users
    GROUP BY day08_cohort_month
),

cohort_engagement AS (
    SELECT
        e.day08_cohort_month,
        e.day08_months_since_signup,

        -- Engagement metrics
        COUNT(DISTINCT e.day08_user_id) AS day08_active_users,
        SUM(e.day08_is_dau) AS day08_total_dau,
        SUM(e.day08_is_mau) AS day08_total_mau,
        AVG(e.day08_daily_events) AS day08_avg_daily_events,

        -- Feature adoption
        COUNT(DISTINCT CASE WHEN fu.day08_features_used > 0 THEN e.day08_user_id END) AS day08_users_with_features,
        AVG(COALESCE(fu.day08_features_used, 0)) AS day08_avg_features_per_user

    FROM engagement e
    LEFT JOIN feature_usage fu
        ON e.day08_user_id = fu.day08_user_id
        AND e.day08_cohort_month = fu.day08_cohort_month
    GROUP BY
        e.day08_cohort_month,
        e.day08_months_since_signup
)

SELECT
    ce.day08_cohort_month,
    ce.day08_months_since_signup,
    cs.day08_cohort_size,
    ce.day08_active_users,
    ce.day08_total_dau,
    ce.day08_total_mau,
    ce.day08_avg_daily_events,
    ce.day08_users_with_features,
    ce.day08_avg_features_per_user,

    -- Rates and percentages
    ROUND(100.0 * ce.day08_active_users / NULLIF(cs.day08_cohort_size, 0), 2) AS day08_retention_rate,
    ROUND(100.0 * ce.day08_total_dau / NULLIF(cs.day08_cohort_size, 0), 2) AS day08_dau_rate,
    ROUND(100.0 * ce.day08_total_mau / NULLIF(cs.day08_cohort_size, 0), 2) AS day08_mau_rate,
    ROUND(100.0 * ce.day08_users_with_features / NULLIF(ce.day08_active_users, 0), 2) AS day08_feature_adoption_rate

FROM cohort_engagement ce
INNER JOIN cohort_sizes cs
    ON ce.day08_cohort_month = cs.day08_cohort_month
ORDER BY
    ce.day08_cohort_month,
    ce.day08_months_since_signup
