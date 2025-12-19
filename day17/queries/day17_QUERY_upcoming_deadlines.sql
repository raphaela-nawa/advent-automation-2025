-- Upcoming compliance deadlines (synthetic dates derived from asset_key)
WITH latest_date AS (
    SELECT MAX(d.full_date) AS max_date
    FROM fct_holdings h
    JOIN dim_date d ON h.date_key = d.date_key
), base_holdings AS (
    SELECT
        a.asset_key,
        a.asset_id,
        a.asset_name,
        a.asset_class,
        c.client_name,
        c.client_type,
        d.full_date AS holding_date,
        CASE
            WHEN a.asset_class = 'Certification' THEN 'EU'
            WHEN a.asset_class = 'IP' THEN 'UK'
            WHEN c.client_type = 'Real Estate Focus' THEN 'EU'
            WHEN c.client_type = 'Technology Investments' THEN 'APAC'
            WHEN c.client_type = 'Diversified' THEN 'UK'
            WHEN c.client_type = 'Manufacturing Owner' THEN 'US'
            ELSE 'US'
        END AS jurisdiction
    FROM fct_holdings h
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_clients c ON h.client_key = c.client_key
    JOIN dim_date d ON h.date_key = d.date_key
    JOIN latest_date ld ON d.full_date = ld.max_date
), status_map AS (
    SELECT
        asset_id,
        asset_name,
        asset_class,
        jurisdiction,
        CASE
            WHEN asset_key % 3 = 0 THEN 'Expired'
            WHEN asset_key % 3 = 1 THEN 'Expiring <90d'
            ELSE 'Current'
        END AS compliance_status
    FROM base_holdings
), deadlines AS (
    SELECT
        asset_id,
        asset_name,
        asset_class,
        jurisdiction,
        compliance_status,
        CASE
            WHEN compliance_status = 'Expired' THEN date((SELECT max_date FROM latest_date), '-15 day')
            WHEN compliance_status = 'Expiring <90d' THEN date((SELECT max_date FROM latest_date), '+45 day')
            ELSE date((SELECT max_date FROM latest_date), '+180 day')
        END AS deadline_date
    FROM status_map
)
SELECT
    asset_id,
    asset_name,
    asset_class,
    jurisdiction,
    compliance_status,
    deadline_date,
    CAST(julianday(deadline_date) - julianday((SELECT max_date FROM latest_date)) AS INTEGER) AS days_to_deadline
FROM deadlines
ORDER BY days_to_deadline ASC, asset_id;
