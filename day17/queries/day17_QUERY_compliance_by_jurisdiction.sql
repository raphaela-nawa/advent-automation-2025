-- Compliance status by jurisdiction (synthetic status derived from asset_key)
WITH latest_date AS (
    SELECT MAX(d.full_date) AS max_date
    FROM fct_holdings h
    JOIN dim_date d ON h.date_key = d.date_key
), base_holdings AS (
    SELECT
        a.asset_key,
        a.asset_id,
        a.asset_class,
        c.client_name,
        c.client_type,
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
        asset_class,
        jurisdiction,
        CASE
            WHEN asset_key % 3 = 0 THEN 'Expired'
            WHEN asset_key % 3 = 1 THEN 'Expiring <90d'
            ELSE 'Current'
        END AS compliance_status
    FROM base_holdings
)
SELECT
    jurisdiction,
    compliance_status,
    COUNT(DISTINCT asset_id) AS asset_count
FROM status_map
GROUP BY jurisdiction, compliance_status
ORDER BY jurisdiction, compliance_status;
