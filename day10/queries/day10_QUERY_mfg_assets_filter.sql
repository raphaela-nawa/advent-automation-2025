-- ============================================================================
-- Day 10: Query 3 - MFG Company Operational Assets Filter
-- ============================================================================
-- ⭐ CRITICAL FOR DAY 16: Luna's Compliance Dashboard
--
-- Business Question: "What are all the operational assets for the MFG company?"
--
-- Purpose: Isolate Equipment, IP, and Certification assets for compliance tracking
-- Use Case: Day 16 will consume this query for departmental compliance dashboard
-- ============================================================================

SELECT
    a.asset_id,
    a.asset_name,
    a.asset_class,
    a.asset_type,
    h.market_value,
    h.quantity,
    acc.account_name,
    c.client_name,
    d.full_date as as_of_date,
    -- Add metadata useful for compliance dashboard
    CASE
        WHEN a.asset_class = 'Equipment' THEN
            CASE
                WHEN a.asset_type LIKE '%Maintenance%' THEN 'Under Maintenance'
                ELSE 'Active'
            END
        WHEN a.asset_class = 'Certification' THEN
            CASE
                WHEN a.valid_to IS NOT NULL AND a.valid_to < DATE('now') THEN 'Expired'
                WHEN a.valid_to IS NOT NULL AND a.valid_to < DATE('now', '+90 days') THEN 'Expiring Soon'
                ELSE 'Current'
            END
        ELSE 'Active'
    END as compliance_status,
    -- Extract jurisdiction/location from asset configuration
    CASE
        WHEN a.asset_class = 'Equipment' THEN
            CASE
                WHEN a.asset_id IN ('EQ_MFG_001', 'EQ_MFG_006') THEN 'UK'
                WHEN a.asset_id IN ('EQ_MFG_002', 'EQ_MFG_009') THEN 'Netherlands'
                WHEN a.asset_id IN ('EQ_MFG_003', 'EQ_MFG_007') THEN 'Germany'
                WHEN a.asset_id = 'EQ_MFG_004' THEN 'France'
                WHEN a.asset_id = 'EQ_MFG_005' THEN 'Poland'
                WHEN a.asset_id = 'EQ_MFG_008' THEN 'Czech Republic'
                WHEN a.asset_id = 'EQ_MFG_010' THEN 'Spain'
                ELSE 'EMEA'
            END
        WHEN a.asset_class = 'IP' THEN
            CASE
                WHEN a.asset_name LIKE '%EU%' OR a.asset_name LIKE '%European Union%' THEN 'European Union'
                WHEN a.asset_name LIKE '%GB%' OR a.asset_name LIKE '%United Kingdom%' THEN 'United Kingdom'
                WHEN a.asset_name LIKE '%DE%' OR a.asset_name LIKE '%Germany%' THEN 'Germany'
                WHEN a.asset_name LIKE '%FR%' OR a.asset_name LIKE '%France%' THEN 'France'
                WHEN a.asset_name LIKE '%NL%' OR a.asset_name LIKE '%Netherlands%' THEN 'Netherlands'
                WHEN a.asset_name LIKE '%ES%' OR a.asset_name LIKE '%Spain%' THEN 'Spain'
                ELSE 'Multi-jurisdictional'
            END
        WHEN a.asset_class = 'Certification' THEN
            CASE
                WHEN a.asset_name LIKE '%EU%' OR a.asset_name LIKE '%European Union%' THEN 'European Union'
                WHEN a.asset_name LIKE '%UK%' THEN 'United Kingdom'
                WHEN a.asset_name LIKE '%DE%' THEN 'Germany'
                ELSE 'Multi-jurisdictional'
            END
        ELSE NULL
    END as jurisdiction
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_accounts acc ON h.account_key = acc.account_key
JOIN dim_clients c ON acc.parent_client_key = c.client_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE
    -- Filter 1: MFG Owner Family only
    c.client_name = 'MFG Owner Family'
    -- Filter 2: Operational asset classes only (Equipment, IP, Certification)
    AND a.asset_class IN ('Equipment', 'IP', 'Certification')
    -- Filter 3: Current asset versions only (SCD Type 2)
    AND a.is_current = TRUE
    -- Filter 4: Most recent date
    AND h.date_key = (SELECT MAX(date_key) FROM dim_date WHERE date_key IN (SELECT DISTINCT date_key FROM fct_holdings))
ORDER BY
    a.asset_class,
    a.asset_id;

-- ============================================================================
-- EXPECTED OUTPUT (30 rows for Day 16)
-- ============================================================================
-- | asset_id      | asset_name                    | asset_class    | market_value | jurisdiction     | compliance_status |
-- |---------------|-------------------------------|----------------|--------------|------------------|-------------------|
-- | CERT_MFG_001  | CE Marking - Product Line A   | Certification  | 10,000       | European Union   | Current           |
-- | CERT_MFG_002  | ISO 9001 - UK Facility        | Certification  | 15,000       | United Kingdom   | Current           |
-- | ...           | ...                           | ...            | ...          | ...              | ...               |
-- | EQ_MFG_001    | CNC Machine Haas VF-2         | Equipment      | 85,000       | UK               | Active            |
-- | EQ_MFG_002    | 3D Printer HP Multi Jet       | Equipment      | 120,000      | Netherlands      | Active            |
-- | ...           | ...                           | ...            | ...          | ...              | ...               |
-- | IP_MFG_001    | Patent EP12345 - Rapid Tool   | IP             | 500,000      | European Union   | Active            |
-- | IP_MFG_002    | Trademark MFG QuickFab        | IP             | 50,000       | European Union   | Active            |
-- | ...           | ...                           | ...            | ...          | ...              | ...               |

-- ============================================================================
-- DAY 16 INTEGRATION POINTS
-- ============================================================================
-- Luna's compliance dashboard (Day 16) will:
-- 1. Import this query as a view or materialized table
-- 2. Add regulatory deadline tracking (REACH renewals, CE expiration dates)
-- 3. Visualize compliance status by jurisdiction
-- 4. Alert on expiring certifications (90-day warning)
-- 5. Track equipment maintenance cycles
-- 6. Monitor IP renewal dates

-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: Verify exactly 30 MFG operational assets
SELECT
    COUNT(*) as mfg_asset_count,
    CASE WHEN COUNT(*) = 30 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM (
    SELECT DISTINCT a.asset_id
    FROM fct_holdings h
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_accounts acc ON h.account_key = acc.account_key
    JOIN dim_clients c ON acc.parent_client_key = c.client_key
    WHERE c.client_name = 'MFG Owner Family'
      AND a.asset_class IN ('Equipment', 'IP', 'Certification')
      AND a.is_current = TRUE
);

-- Check 2: Verify distribution (10 Equipment, 10 IP, 10 Certification)
SELECT
    a.asset_class,
    COUNT(DISTINCT a.asset_id) as asset_count,
    CASE WHEN COUNT(DISTINCT a.asset_id) = 10 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_accounts acc ON h.account_key = acc.account_key
JOIN dim_clients c ON acc.parent_client_key = c.client_key
WHERE c.client_name = 'MFG Owner Family'
  AND a.asset_class IN ('Equipment', 'IP', 'Certification')
  AND a.is_current = TRUE
GROUP BY a.asset_class
ORDER BY a.asset_class;

-- Check 3: Verify naming convention (EQ_MFG_*, IP_MFG_*, CERT_MFG_*)
SELECT
    COUNT(*) as correct_naming_count,
    CASE WHEN COUNT(*) = 30 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM (
    SELECT DISTINCT a.asset_id
    FROM fct_holdings h
    JOIN dim_assets a ON h.asset_key = a.asset_key
    JOIN dim_accounts acc ON h.account_key = acc.account_key
    JOIN dim_clients c ON acc.parent_client_key = c.client_key
    WHERE c.client_name = 'MFG Owner Family'
      AND a.asset_class IN ('Equipment', 'IP', 'Certification')
      AND a.is_current = TRUE
      AND (a.asset_id LIKE 'EQ_MFG_%' OR a.asset_id LIKE 'IP_MFG_%' OR a.asset_id LIKE 'CERT_MFG_%')
);

-- ============================================================================
-- EXPORT FOR DAY 16
-- ============================================================================
-- To export this data for Day 16, run:
-- sqlite3 data/day10_family_office_dw.db < queries/day10_QUERY_mfg_assets_filter.sql > day16_mfg_assets_input.csv
--
-- Or create a view for direct access:
/*
CREATE VIEW IF NOT EXISTS v_mfg_operational_assets AS
SELECT [main query above];
*/
