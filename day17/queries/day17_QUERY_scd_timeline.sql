-- Show asset classification changes over time (SCD Type 2)
-- Synthetic history is generated because Day 10 assets are single-version.
WITH latest_date AS (
    SELECT MAX(d.full_date) AS max_date
    FROM fct_holdings h
    JOIN dim_date d ON h.date_key = d.date_key
), base_assets AS (
    SELECT
        asset_id,
        asset_name,
        asset_class,
        asset_type
    FROM dim_assets
    WHERE asset_class IN ('Equipment', 'IP', 'Certification')
), scd_seed AS (
    SELECT
        asset_id,
        asset_name,
        asset_class,
        asset_type,
        date((SELECT max_date FROM latest_date), '-60 day') AS change_date,
        CASE
            WHEN asset_class = 'Equipment' THEN 'Maintenance'
            WHEN asset_class = 'IP' THEN 'IP Review'
            WHEN asset_class = 'Certification' THEN 'Renewal Pending'
            ELSE asset_class
        END AS prior_class
    FROM base_assets
), scd_versions AS (
    SELECT
        asset_id,
        asset_name,
        prior_class AS asset_class,
        asset_type,
        date(change_date, '-365 day') AS valid_from,
        date(change_date, '-1 day') AS valid_to,
        0 AS is_current,
        'Historical' AS version_status
    FROM scd_seed
    UNION ALL
    SELECT
        asset_id,
        asset_name,
        asset_class,
        asset_type,
        change_date AS valid_from,
        '9999-12-31' AS valid_to,
        1 AS is_current,
        'Current' AS version_status
    FROM scd_seed
)
SELECT *
FROM scd_versions
ORDER BY asset_id, valid_from;
