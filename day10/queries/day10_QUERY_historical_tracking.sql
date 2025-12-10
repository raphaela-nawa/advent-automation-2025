-- ============================================================================
-- Day 10: Query 4 - Historical Tracking (SCD Type 2 in Action)
-- ============================================================================
-- Business Question: "What was the classification/status of assets on a specific date?"
--
-- Purpose: Demonstrate SCD Type 2 capability for regulatory compliance
-- Use Case: Tax filings, regulatory audits, estate planning ("as-of" date queries)
-- ============================================================================

-- ============================================================================
-- PART 1: Show All Historical Versions of Changed Assets
-- ============================================================================

SELECT
    a.asset_id,
    a.asset_name,
    a.asset_class,
    a.asset_type,
    a.valid_from,
    a.valid_to,
    a.is_current,
    CASE
        WHEN a.valid_to IS NULL THEN 'Current'
        ELSE 'Historical'
    END as record_status,
    -- Calculate days this version was valid
    CASE
        WHEN a.valid_to IS NULL THEN CAST(JULIANDAY('now') - JULIANDAY(a.valid_from) AS INTEGER)
        ELSE CAST(JULIANDAY(a.valid_to) - JULIANDAY(a.valid_from) + 1 AS INTEGER)
    END as days_valid,
    -- Reason for change (inferred from asset type changes)
    LAG(a.asset_type) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) as previous_type,
    CASE
        WHEN LAG(a.asset_type) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) IS NULL THEN 'Initial Record'
        WHEN a.asset_type LIKE '%Maintenance%' THEN 'Equipment Maintenance'
        WHEN a.asset_type NOT LIKE '%Maintenance%' AND LAG(a.asset_type) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) LIKE '%Maintenance%' THEN 'Return to Service'
        WHEN a.asset_name LIKE '%v2.0%' THEN 'Regulatory Update'
        ELSE 'Classification Change'
    END as change_reason
FROM dim_assets a
WHERE
    -- Only show assets that have multiple versions (changed over time)
    a.asset_id IN (
        SELECT asset_id
        FROM dim_assets
        GROUP BY asset_id
        HAVING COUNT(*) > 1
    )
ORDER BY
    a.asset_id,
    a.valid_from;

-- Expected Output:
-- | asset_id      | asset_name       | asset_type              | valid_from | valid_to   | is_current | record_status | days_valid | change_reason       |
-- |---------------|------------------|-------------------------|------------|------------|------------|---------------|------------|---------------------|
-- | EQ_MFG_001    | CNC Machine...   | CNC Machine             | 2023-01-01 | 2024-06-30 | FALSE      | Historical    | 547        | Initial Record      |
-- | EQ_MFG_001    | CNC Machine...   | CNC Machine (Maint...)  | 2024-07-01 | 2024-09-30 | FALSE      | Historical    | 92         | Equipment Maint...  |
-- | EQ_MFG_001    | CNC Machine...   | CNC Machine             | 2024-10-01 | NULL       | TRUE       | Current       | 71         | Return to Service   |
-- | CERT_MFG_001  | CE Marking...    | Product Certification   | 2023-01-01 | 2024-12-31 | FALSE      | Historical    | 731        | Initial Record      |
-- | CERT_MFG_001  | CE Marking v2.0  | Product Certification   | 2025-01-01 | NULL       | TRUE       | Current       | -20        | Regulatory Update   |

-- ============================================================================
-- PART 2: Point-in-Time Query - "What was the status on [specific date]?"
-- ============================================================================

-- Example 1: Portfolio composition on June 15, 2024
SELECT
    'Portfolio Snapshot: 2024-06-15' as report_title,
    c.client_name,
    a.asset_class,
    COUNT(DISTINCT a.asset_id) as number_of_assets,
    SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE
    -- Point-in-time date filter
    d.full_date = '2024-06-15'
    -- SCD Type 2: Get asset version valid on that date
    AND '2024-06-15' BETWEEN a.valid_from AND COALESCE(a.valid_to, '9999-12-31')
GROUP BY c.client_name, a.asset_class
ORDER BY c.client_name, total_value DESC;

-- Example 2: Specific asset status on August 15, 2024 (during maintenance)
SELECT
    'Asset Status: EQ_MFG_001 on 2024-08-15' as report_title,
    a.asset_id,
    a.asset_name,
    a.asset_type,
    a.valid_from,
    a.valid_to,
    CASE
        WHEN a.asset_type LIKE '%Maintenance%' THEN '⚠️ Under Maintenance'
        ELSE '✅ Active'
    END as status_on_date
FROM dim_assets a
WHERE
    a.asset_id = 'EQ_MFG_001'
    AND '2024-08-15' BETWEEN a.valid_from AND COALESCE(a.valid_to, '9999-12-31');

-- Expected Output:
-- | report_title                          | asset_id   | asset_name          | asset_type                | status_on_date     |
-- |---------------------------------------|------------|---------------------|---------------------------|--------------------|
-- | Asset Status: EQ_MFG_001 on 2024-...  | EQ_MFG_001 | CNC Machine Haas... | CNC Machine (Under Mai... | ⚠️ Under Maintenance |

-- ============================================================================
-- PART 3: Change Audit Trail
-- ============================================================================

-- Show all changes to MFG operational assets over time
SELECT
    a.asset_id,
    a.asset_name,
    a.asset_class,
    a.valid_from as change_date,
    a.asset_type as new_value,
    LAG(a.asset_type) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) as old_value,
    -- Who would have approved this change? (In production, add audit columns)
    'System' as changed_by,
    CASE
        WHEN LAG(a.asset_type) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) IS NULL THEN 'Asset Created'
        ELSE 'Classification Changed'
    END as change_type
FROM dim_assets a
WHERE
    (a.asset_id LIKE 'EQ_MFG_%' OR a.asset_id LIKE 'IP_MFG_%' OR a.asset_id LIKE 'CERT_MFG_%')
    AND a.asset_id IN (
        SELECT asset_id FROM dim_assets GROUP BY asset_id HAVING COUNT(*) > 1
    )
ORDER BY
    a.asset_id,
    a.valid_from;

-- ============================================================================
-- PART 4: Compliance Questions Answered by SCD Type 2
-- ============================================================================

-- Question 1: "Which equipment was under maintenance during Q3 2024?"
SELECT
    a.asset_id,
    a.asset_name,
    a.valid_from as maintenance_start,
    a.valid_to as maintenance_end,
    CAST(JULIANDAY(COALESCE(a.valid_to, DATE('now'))) - JULIANDAY(a.valid_from) AS INTEGER) as days_in_maintenance
FROM dim_assets a
WHERE
    a.asset_class = 'Equipment'
    AND a.asset_type LIKE '%Maintenance%'
    -- Q3 2024 = July, August, September
    AND (
        (a.valid_from BETWEEN '2024-07-01' AND '2024-09-30')
        OR (a.valid_to BETWEEN '2024-07-01' AND '2024-09-30')
        OR (a.valid_from < '2024-07-01' AND COALESCE(a.valid_to, '9999-12-31') > '2024-09-30')
    )
ORDER BY days_in_maintenance DESC;

-- Question 2: "When did CERT_MFG_001 last change its requirements?"
SELECT
    a.asset_id,
    a.asset_name,
    a.valid_from as change_date,
    a.asset_type,
    LAG(a.valid_from) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from) as previous_change_date,
    CAST(JULIANDAY(a.valid_from) - JULIANDAY(LAG(a.valid_from) OVER (PARTITION BY a.asset_id ORDER BY a.valid_from)) AS INTEGER) as days_since_last_change
FROM dim_assets a
WHERE a.asset_id = 'CERT_MFG_001'
ORDER BY a.valid_from DESC
LIMIT 1;

-- Question 3: "Show asset value over time accounting for reclassifications"
SELECT
    d.year,
    d.quarter,
    a.asset_id,
    a.asset_type,
    SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE
    a.asset_id = 'EQ_MFG_001'
    -- This JOIN automatically gets the correct version for each date
GROUP BY d.year, d.quarter, a.asset_id, a.asset_type
ORDER BY d.year, d.quarter;

-- This shows how market value tracking accounts for status changes (e.g., depreciation during maintenance)

-- ============================================================================
-- BUSINESS VALUE DEMONSTRATED
-- ============================================================================
-- SCD Type 2 enables:
-- 1. ✅ Regulatory Compliance: "What was the portfolio on December 31, 2023 for tax filing?"
-- 2. ✅ Audit Trails: "Show all changes to equipment classifications in 2024"
-- 3. ✅ Trend Analysis: "How did asset allocation change after reclassifications?"
-- 4. ✅ Historical Reconstruction: "Reproduce the compliance report submitted on June 30"
-- 5. ✅ Change Management: "Track approval workflow for asset status changes"

-- Without SCD Type 2, you would only know the current state, losing critical historical context.
