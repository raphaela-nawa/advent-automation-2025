-- ============================================================================
-- Day 10: Query 2 - Asset Allocation by Class Over Time
-- ============================================================================
-- Business Question: "How is our portfolio allocated across asset classes?"
--
-- Purpose: Strategic asset allocation analysis for wealth planning
-- Use Case: Quarterly investment committee meetings, rebalancing decisions
-- ============================================================================

SELECT
    d.year,
    d.quarter,
    a.asset_class,
    COUNT(DISTINCT a.asset_id) as number_of_assets,
    SUM(h.market_value) as total_value,
    -- Calculate allocation percentage within each quarter
    ROUND(
        (SUM(h.market_value) * 100.0) / SUM(SUM(h.market_value)) OVER (PARTITION BY d.year, d.quarter),
        2
    ) as allocation_pct,
    -- Calculate quarter-over-quarter growth
    ROUND(
        ((SUM(h.market_value) - LAG(SUM(h.market_value)) OVER (PARTITION BY a.asset_class ORDER BY d.year, d.quarter))
         / NULLIF(LAG(SUM(h.market_value)) OVER (PARTITION BY a.asset_class ORDER BY d.year, d.quarter), 0)) * 100,
        2
    ) as qoq_growth_pct
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE
    a.is_current = TRUE  -- Only current asset versions (SCD Type 2)
    -- Filter to end-of-quarter dates only (reduce noise)
    AND d.month IN (3, 6, 9, 12)
    AND d.full_date LIKE '%-01'  -- First day of quarter-end month
GROUP BY
    d.year,
    d.quarter,
    a.asset_class
ORDER BY
    d.year,
    d.quarter,
    allocation_pct DESC;

-- ============================================================================
-- EXPECTED OUTPUT FORMAT
-- ============================================================================
-- | year | quarter | asset_class       | number_of_assets | total_value  | allocation_pct | qoq_growth_pct |
-- |------|---------|-------------------|------------------|--------------|----------------|----------------|
-- | 2024 | Q4      | Equity            | 50               | €35,000,000  | 45.2           | 2.1            |
-- | 2024 | Q4      | Operating Company | 20               | €22,000,000  | 28.4           | -1.5           |
-- | 2024 | Q4      | Equipment         | 10               | €12,000,000  | 15.5           | 0.3            |
-- | 2024 | Q4      | IP                | 10               | €5,500,000   | 7.1            | 1.2            |
-- | 2024 | Q4      | Certification     | 10               | €2,800,000   | 3.6            | 0.0            |

-- ============================================================================
-- BUSINESS INSIGHTS
-- ============================================================================
-- This query enables:
-- 1. Monitor strategic asset allocation targets (e.g., "60% Equity, 20% Alternatives")
-- 2. Identify asset class concentration risks
-- 3. Track Equipment/IP/Certification growth for MFG Owner Family
-- 4. Trigger rebalancing decisions when allocations drift

-- ============================================================================
-- VARIATIONS
-- ============================================================================

-- Variation 1: Current allocation breakdown (latest date only)
/*
SELECT
    a.asset_class,
    COUNT(DISTINCT a.asset_id) as number_of_assets,
    SUM(h.market_value) as total_value,
    ROUND(
        (SUM(h.market_value) * 100.0) / SUM(SUM(h.market_value)) OVER (),
        2
    ) as allocation_pct,
    -- Show top 3 assets in this class
    GROUP_CONCAT(
        a.asset_name || ' (€' || ROUND(h.market_value / 1000, 0) || 'K)',
        ', '
    ) FILTER (WHERE rownum <= 3) as top_assets
FROM (
    SELECT
        h.*,
        a.*,
        ROW_NUMBER() OVER (PARTITION BY a.asset_class ORDER BY h.market_value DESC) as rownum
    FROM fct_holdings h
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_date d ON h.date_key = d.date_key
    WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
      AND a.is_current = TRUE
) subq
GROUP BY asset_class
ORDER BY total_value DESC;
*/

-- Variation 2: Asset allocation by client (who holds what?)
/*
SELECT
    c.client_name,
    a.asset_class,
    COUNT(DISTINCT a.asset_id) as number_of_assets,
    SUM(h.market_value) as total_value,
    ROUND(
        (SUM(h.market_value) * 100.0) / SUM(SUM(h.market_value)) OVER (PARTITION BY c.client_key),
        2
    ) as allocation_pct
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
  AND a.is_current = TRUE
GROUP BY c.client_name, a.asset_class
ORDER BY c.client_name, allocation_pct DESC;
*/

-- Variation 3: Identify allocation drift from target
/*
WITH current_allocation AS (
    SELECT
        a.asset_class,
        SUM(h.market_value) as total_value,
        ROUND(
            (SUM(h.market_value) * 100.0) / SUM(SUM(h.market_value)) OVER (),
            2
        ) as actual_pct
    FROM fct_holdings h
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_date d ON h.date_key = d.date_key
    WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
      AND a.is_current = TRUE
    GROUP BY a.asset_class
),
target_allocation AS (
    -- Define strategic targets (could be in a separate config table)
    SELECT 'Equity' as asset_class, 45.0 as target_pct
    UNION ALL SELECT 'Operating Company', 30.0
    UNION ALL SELECT 'Equipment', 12.0
    UNION ALL SELECT 'IP', 8.0
    UNION ALL SELECT 'Certification', 5.0
)
SELECT
    ca.asset_class,
    ca.actual_pct,
    ta.target_pct,
    ca.actual_pct - ta.target_pct as drift_pct,
    CASE
        WHEN ABS(ca.actual_pct - ta.target_pct) > 5.0 THEN '⚠️ Rebalance Needed'
        WHEN ABS(ca.actual_pct - ta.target_pct) > 3.0 THEN '⚡ Monitor Closely'
        ELSE '✅ On Target'
    END as status
FROM current_allocation ca
LEFT JOIN target_allocation ta ON ca.asset_class = ta.asset_class
ORDER BY ABS(ca.actual_pct - COALESCE(ta.target_pct, ca.actual_pct)) DESC;
*/
