-- ============================================================================
-- Day 10: Family Office Data Warehouse - Fact Table Population
-- ============================================================================
-- Note: In this implementation, the fact table is populated by the
-- Python synthetic data generator (day10_DATA_synthetic_generator.py)
-- for better control over realistic portfolio distributions.
--
-- This file documents the logic and provides manual INSERT examples
-- if you want to add holdings programmatically via SQL.
-- ============================================================================

-- ============================================================================
-- FACT TABLE STRUCTURE REMINDER
-- ============================================================================
-- fct_holdings (
--     holding_key INTEGER PRIMARY KEY,
--     client_key INTEGER NOT NULL,
--     asset_key INTEGER NOT NULL,
--     account_key INTEGER NOT NULL,
--     date_key INTEGER NOT NULL,
--     quantity DECIMAL(18, 4) NOT NULL,
--     market_value DECIMAL(18, 2) NOT NULL,
--     cost_basis DECIMAL(18, 2)
-- )

-- ============================================================================
-- POPULATION STRATEGY
-- ============================================================================
-- The synthetic generator populates fct_holdings using this logic:
--
-- 1. MFG Owner Family (client_key=3):
--    - All 30 MFG operational assets (EQ_MFG_*, IP_MFG_*, CERT_MFG_*)
--    - Assigned to "MFG Company Operating Account"
--    - Plus some financial assets in other accounts
--
-- 2. Other Families (client_keys 1,2,4,5):
--    - Random selection of financial assets (8-15 per family)
--    - Random selection of operating company stakes
--    - Distributed across their respective accounts
--
-- 3. Temporal Coverage:
--    - Monthly snapshots from 2023-01-01 to 2024-12-31 (24 months)
--    - Each asset appears once per month per account
--
-- 4. Value Generation:
--    - Equipment/IP/Certs: Based on CONFIG values with ±5% variation
--    - Financial assets: Random price × quantity
--    - Operating stakes: Large lump sums (€500K - €20M)

-- ============================================================================
-- MANUAL INSERT EXAMPLE (if extending data)
-- ============================================================================
-- Example: Add a new holding for Smith Family on 2025-01-01

-- Step 1: Get necessary keys
-- SELECT client_key FROM dim_clients WHERE client_name = 'Smith Family';  -- Returns 1
-- SELECT asset_key FROM dim_assets WHERE asset_id = 'FIN_001' AND is_current = TRUE;  -- Returns X
-- SELECT account_key FROM dim_accounts WHERE parent_client_key = 1 LIMIT 1;  -- Returns Y
-- SELECT date_key FROM dim_date WHERE full_date = '2025-01-01';  -- Returns 20250101

-- Step 2: Insert holding
-- INSERT INTO fct_holdings (
--     holding_key,
--     client_key,
--     asset_key,
--     account_key,
--     date_key,
--     quantity,
--     market_value,
--     cost_basis
-- ) VALUES (
--     (SELECT COALESCE(MAX(holding_key), 0) + 1 FROM fct_holdings),  -- Next available key
--     1,                    -- Smith Family client_key
--     X,                    -- Asset key from step 1
--     Y,                    -- Account key from step 1
--     20250101,             -- Date key (YYYYMMDD)
--     1000.00,              -- 1000 shares
--     150000.00,            -- $150 per share
--     120000.00             -- Cost basis (purchased at $120/share)
-- );

-- ============================================================================
-- INCREMENTAL REFRESH PATTERN (for production)
-- ============================================================================
-- In production, you'd implement incremental refresh to add new holdings
-- without regenerating the entire fact table.

-- Example: Add holdings for latest month (2025-02-01)
/*
WITH latest_holdings AS (
    -- Get most recent holdings for each client-asset-account combination
    SELECT
        h.client_key,
        h.asset_key,
        h.account_key,
        h.quantity,
        h.market_value * 1.02 as updated_market_value,  -- Assume 2% growth
        h.cost_basis
    FROM fct_holdings h
    INNER JOIN (
        SELECT client_key, asset_key, account_key, MAX(date_key) as max_date
        FROM fct_holdings
        GROUP BY client_key, asset_key, account_key
    ) latest
    ON h.client_key = latest.client_key
    AND h.asset_key = latest.asset_key
    AND h.account_key = latest.account_key
    AND h.date_key = latest.max_date
)
INSERT INTO fct_holdings (
    holding_key,
    client_key,
    asset_key,
    account_key,
    date_key,
    quantity,
    market_value,
    cost_basis
)
SELECT
    (SELECT COALESCE(MAX(holding_key), 0) FROM fct_holdings) + ROW_NUMBER() OVER (ORDER BY client_key, asset_key),
    client_key,
    asset_key,
    account_key,
    20250201,  -- New date key
    quantity,
    updated_market_value,
    cost_basis
FROM latest_holdings;
*/

-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================

-- Check 1: Ensure no NULL market values
SELECT
    COUNT(*) as null_market_value_count,
    CASE WHEN COUNT(*) = 0 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM fct_holdings
WHERE market_value IS NULL;

-- Check 2: Ensure all holdings have valid dimension references
SELECT
    COUNT(*) as orphaned_records,
    CASE WHEN COUNT(*) = 0 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM fct_holdings h
LEFT JOIN dim_clients c ON h.client_key = c.client_key
LEFT JOIN dim_assets a ON h.asset_key = a.asset_key
LEFT JOIN dim_accounts acc ON h.account_key = acc.account_key
LEFT JOIN dim_date d ON h.date_key = d.date_key
WHERE c.client_key IS NULL
   OR a.asset_key IS NULL
   OR acc.account_key IS NULL
   OR d.date_key IS NULL;

-- Check 3: Verify MFG assets are in correct account
SELECT
    COUNT(*) as mfg_assets_in_operating_account,
    CASE WHEN COUNT(*) >= 30 * 24 THEN '✅ PASS' ELSE '❌ FAIL' END as status  -- 30 assets × 24 months
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_accounts acc ON h.account_key = acc.account_key
WHERE (a.asset_id LIKE 'EQ_MFG_%' OR a.asset_id LIKE 'IP_MFG_%' OR a.asset_id LIKE 'CERT_MFG_%')
  AND acc.account_name LIKE '%MFG Company Operating%';

-- Check 4: Verify date range coverage
SELECT
    MIN(d.full_date) as earliest_date,
    MAX(d.full_date) as latest_date,
    COUNT(DISTINCT h.date_key) as unique_dates,
    CASE WHEN COUNT(DISTINCT h.date_key) >= 24 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM fct_holdings h
JOIN dim_date d ON h.date_key = d.date_key;

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================

-- Holdings distribution by client
SELECT
    c.client_name,
    COUNT(DISTINCT h.asset_key) as unique_assets,
    COUNT(*) as total_holdings_records,
    SUM(h.market_value) as total_portfolio_value,
    ROUND(AVG(h.market_value), 2) as avg_holding_value
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
GROUP BY c.client_name
ORDER BY total_portfolio_value DESC;

-- Holdings distribution by asset class
SELECT
    a.asset_class,
    COUNT(DISTINCT h.asset_key) as unique_assets,
    COUNT(*) as total_holdings_records,
    SUM(h.market_value) as total_value,
    ROUND(AVG(h.market_value), 2) as avg_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
WHERE a.is_current = TRUE
GROUP BY a.asset_class
ORDER BY total_value DESC;
