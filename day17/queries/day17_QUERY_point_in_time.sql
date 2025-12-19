-- Point-in-time portfolio composition
-- Param: :as_of_date (YYYY-MM-DD)
SELECT
    c.client_name,
    a.asset_class,
    COUNT(*) AS asset_count,
    SUM(h.market_value) AS total_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
    AND :as_of_date BETWEEN a.valid_from AND COALESCE(a.valid_to, '9999-12-31')
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE d.full_date = :as_of_date
GROUP BY c.client_name, a.asset_class
ORDER BY total_value DESC;
