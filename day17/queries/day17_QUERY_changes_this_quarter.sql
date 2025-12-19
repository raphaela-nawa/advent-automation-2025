-- Asset classification changes starting in the current quarter (based on latest holdings date)
WITH latest_date AS (
    SELECT MAX(d.full_date) AS max_date
    FROM fct_holdings h
    JOIN dim_date d ON h.date_key = d.date_key
), quarter_start AS (
    SELECT
        date(
            strftime('%Y', max_date) || '-' ||
            printf('%02d', ((CAST(strftime('%m', max_date) AS INTEGER) - 1) / 3) * 3 + 1) || '-01'
        ) AS quarter_start_date
    FROM latest_date
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
        0 AS is_current
    FROM scd_seed
    UNION ALL
    SELECT
        asset_id,
        asset_name,
        asset_class,
        asset_type,
        change_date AS valid_from,
        '9999-12-31' AS valid_to,
        1 AS is_current
    FROM scd_seed
)
SELECT
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    is_current
FROM scd_versions
WHERE valid_from >= (SELECT quarter_start_date FROM quarter_start)
ORDER BY valid_from DESC, asset_id;
