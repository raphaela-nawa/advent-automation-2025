-- Day 08 - Marts: User Health Dimension
-- Comprehensive user health scoring for expansion signals

{{ config(materialized='table') }}

WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

subscriptions AS (
    SELECT * FROM {{ ref('stg_subscriptions') }}
),

funnel_completion AS (
    SELECT
        day08_user_id,
        MAX(day08_is_activated) AS day08_is_activated,
        MAX(day08_is_paid) AS day08_is_paid,
        MIN(CASE WHEN day08_is_activated = 1 THEN day08_days_since_signup END) AS day08_days_to_activation
    FROM {{ ref('int_funnel_steps') }}
    GROUP BY day08_user_id
),

engagement_summary AS (
    SELECT
        day08_user_id,
        COUNT(DISTINCT day08_event_date) AS day08_total_active_days,
        AVG(day08_daily_events) AS day08_avg_events_per_day,
        MAX(day08_event_date) AS day08_last_active_date,
        MIN(day08_event_date) AS day08_first_active_date
    FROM {{ ref('int_user_engagement') }}
    GROUP BY day08_user_id
),

feature_adoption AS (
    SELECT
        day08_user_id,
        day08_features_adopted,
        day08_avg_days_to_adoption
    FROM {{ ref('int_feature_usage') }}
    GROUP BY day08_user_id, day08_features_adopted, day08_avg_days_to_adoption
),

user_health AS (
    SELECT
        u.day08_user_id,
        u.day08_cohort_month,
        u.day08_signup_date,
        u.day08_utm_source,
        u.day08_utm_campaign,

        -- Funnel status
        COALESCE(fc.day08_is_activated, 0) AS day08_is_activated,
        COALESCE(fc.day08_is_paid, 0) AS day08_is_paid,
        fc.day08_days_to_activation,

        -- Subscription info
        s.day08_plan_name,
        s.day08_mrr,
        s.day08_status AS day08_subscription_status,
        s.day08_is_active AS day08_has_active_subscription,

        -- Engagement metrics
        COALESCE(es.day08_total_active_days, 0) AS day08_total_active_days,
        ROUND(COALESCE(es.day08_avg_events_per_day, 0), 2) AS day08_avg_events_per_day,
        es.day08_last_active_date,
        julianday('now') - julianday(es.day08_last_active_date) AS day08_days_since_last_active,

        -- Feature adoption
        COALESCE(fa.day08_features_adopted, 0) AS day08_features_adopted,
        fa.day08_avg_days_to_adoption,

        -- Tenure
        julianday('now') - julianday(u.day08_signup_date) AS day08_days_since_signup

    FROM users u
    LEFT JOIN funnel_completion fc ON u.day08_user_id = fc.day08_user_id
    LEFT JOIN subscriptions s ON u.day08_user_id = s.day08_user_id
    LEFT JOIN engagement_summary es ON u.day08_user_id = es.day08_user_id
    LEFT JOIN feature_adoption fa ON u.day08_user_id = fa.day08_user_id
)

SELECT
    *,

    -- Health scoring components (0-100 scale)
    CASE
        WHEN day08_total_active_days >= 30 THEN 100
        WHEN day08_total_active_days >= 15 THEN 75
        WHEN day08_total_active_days >= 5 THEN 50
        WHEN day08_total_active_days >= 1 THEN 25
        ELSE 0
    END AS day08_engagement_score,

    CASE
        WHEN day08_features_adopted >= 5 THEN 100
        WHEN day08_features_adopted >= 3 THEN 75
        WHEN day08_features_adopted >= 1 THEN 50
        ELSE 0
    END AS day08_feature_adoption_score,

    CASE
        WHEN day08_days_since_last_active <= 7 THEN 100
        WHEN day08_days_since_last_active <= 14 THEN 75
        WHEN day08_days_since_last_active <= 30 THEN 50
        WHEN day08_days_since_last_active <= 60 THEN 25
        ELSE 0
    END AS day08_recency_score,

    -- Overall health score (weighted average)
    ROUND(
        (
            (CASE
                WHEN day08_total_active_days >= 30 THEN 100
                WHEN day08_total_active_days >= 15 THEN 75
                WHEN day08_total_active_days >= 5 THEN 50
                WHEN day08_total_active_days >= 1 THEN 25
                ELSE 0
            END * 0.4) +
            (CASE
                WHEN day08_features_adopted >= 5 THEN 100
                WHEN day08_features_adopted >= 3 THEN 75
                WHEN day08_features_adopted >= 1 THEN 50
                ELSE 0
            END * 0.3) +
            (CASE
                WHEN day08_days_since_last_active <= 7 THEN 100
                WHEN day08_days_since_last_active <= 14 THEN 75
                WHEN day08_days_since_last_active <= 30 THEN 50
                WHEN day08_days_since_last_active <= 60 THEN 25
                ELSE 0
            END * 0.3)
        ), 1
    ) AS day08_overall_health_score,

    -- Health status categorization
    CASE
        WHEN day08_is_paid = 0 THEN 'Not Paid'
        WHEN day08_days_since_last_active <= 7 AND day08_features_adopted >= 3 THEN 'Healthy'
        WHEN day08_days_since_last_active <= 14 AND day08_features_adopted >= 1 THEN 'Engaged'
        WHEN day08_days_since_last_active <= 30 THEN 'At Risk'
        ELSE 'Churning'
    END AS day08_health_status,

    -- Expansion signals
    COALESCE(
        CASE
            WHEN day08_is_paid = 1
                 AND day08_features_adopted >= 4
                 AND day08_total_active_days >= 20
                 AND day08_plan_name = 'Starter'
            THEN 1
            ELSE 0
        END,
        0
    ) AS day08_upsell_candidate

FROM user_health
