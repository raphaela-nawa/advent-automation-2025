-- Portfolio snapshot at latest available date with derived jurisdiction
WITH latest_date AS (
    SELECT MAX(d.full_date) AS max_date
    FROM fct_holdings h
    JOIN dim_date d ON h.date_key = d.date_key
), base_holdings AS (
    SELECT
        h.holding_key,
        c.client_name,
        c.client_type,
        a.asset_id,
        a.asset_name,
        a.asset_class,
        a.asset_type,
        h.market_value,
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
)
SELECT *
FROM base_holdings;
