-- ============================================================================
-- Day 10: Query 1 - Total Portfolio Value per Client
-- ============================================================================
-- Business Question: "What is the total portfolio value for each family?"
--
-- Purpose: Executive summary of wealth distribution across family office clients
-- Use Case: Monthly board reporting, client relationship management
-- ============================================================================

SELECT
    c.client_name,
    c.client_type,
    COUNT(DISTINCT a.asset_id) as number_of_assets,
    COUNT(DISTINCT acc.account_id) as number_of_accounts,
    SUM(h.market_value) as total_portfolio_value,
    SUM(h.cost_basis) as total_cost_basis,
    SUM(h.market_value) - SUM(h.cost_basis) as unrealized_gain_loss,
    ROUND(
        ((SUM(h.market_value) - SUM(h.cost_basis)) / NULLIF(SUM(h.cost_basis), 0)) * 100,
        2
    ) as return_pct,
    -- Calculate portfolio allocation percentage
    ROUND(
        (SUM(h.market_value) * 100.0) / SUM(SUM(h.market_value)) OVER (),
        2
    ) as portfolio_allocation_pct
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_accounts acc ON h.account_key = acc.account_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE
    -- Get most recent date available
    d.full_date = (SELECT MAX(full_date) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
    AND a.is_current = TRUE  -- Only current asset versions (SCD Type 2)
GROUP BY
    c.client_name,
    c.client_type
ORDER BY
    total_portfolio_value DESC;

-- ============================================================================
-- EXPECTED OUTPUT FORMAT
-- ============================================================================
-- | client_name      | client_type         | number_of_assets | total_portfolio_value | return_pct | allocation_pct |
-- |------------------|---------------------|------------------|----------------------|------------|----------------|
-- | MFG Owner Family | Manufacturing Owner | 40               | €25,450,000          | 12.5       | 35.2           |
-- | Garcia Family    | Diversified         | 15               | €18,200,000          | 8.3        | 25.1           |
-- | Smith Family     | Traditional Invest  | 12               | €14,800,000          | 6.1        | 20.4           |
-- | ...              | ...                 | ...              | ...                  | ...        | ...            |

-- ============================================================================
-- BUSINESS INSIGHTS
-- ============================================================================
-- This query enables:
-- 1. Identify largest clients (concentration risk)
-- 2. Track portfolio growth over time (compare month-over-month)
-- 3. Benchmark returns across families (who's outperforming?)
-- 4. Validate portfolio allocation targets

-- ============================================================================
-- VARIATIONS
-- ============================================================================

-- Variation 1: Historical trend - Portfolio value over time
/*
SELECT
    d.year,
    d.month,
    c.client_name,
    SUM(h.market_value) as total_portfolio_value
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE a.is_current = TRUE
GROUP BY d.year, d.month, c.client_name
ORDER BY d.year, d.month, total_portfolio_value DESC;
*/

-- Variation 2: Top 10 holdings per client
/*
WITH ranked_holdings AS (
    SELECT
        c.client_name,
        a.asset_name,
        a.asset_class,
        h.market_value,
        ROW_NUMBER() OVER (PARTITION BY c.client_key ORDER BY h.market_value DESC) as rank
    FROM fct_holdings h
    JOIN dim_clients c ON h.client_key = c.client_key
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_date d ON h.date_key = d.date_key
    WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
      AND a.is_current = TRUE
)
SELECT *
FROM ranked_holdings
WHERE rank <= 10
ORDER BY client_name, rank;
*/
