-- ============================================================================
-- Day 10: Family Office Data Warehouse - SCD Type 2 Examples
-- ============================================================================
-- Demonstrates Slowly Changing Dimension Type 2 implementation
-- Shows how to track historical changes in asset classifications
-- ============================================================================

-- This script demonstrates SCD Type 2 logic with two real-world examples:
-- 1. Equipment lifecycle changes (Active → Maintenance → Active)
-- 2. Certification regulatory updates (Standard v1.0 → Standard v2.0)

-- ============================================================================
-- EXAMPLE 1: Equipment Lifecycle Changes
-- ============================================================================
-- Scenario: EQ_MFG_001 (CNC Machine) goes through maintenance cycle

-- Initial state (loaded by synthetic generator):
-- asset_key=1, asset_id='EQ_MFG_001', asset_class='Equipment',
-- valid_from='2023-01-01', valid_to=NULL, is_current=TRUE

-- --------------------------------------------------------------------------
-- Step 1: Equipment enters maintenance (2024-07-01)
-- --------------------------------------------------------------------------
-- Close current record
UPDATE dim_assets
SET
    valid_to = '2024-06-30',              -- End date for "Active" status
    is_current = FALSE                     -- No longer current version
WHERE asset_id = 'EQ_MFG_001'
  AND is_current = TRUE;

-- Insert new record with "Maintenance" status
INSERT INTO dim_assets (
    asset_key,
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    is_current
) VALUES (
    (SELECT COALESCE(MAX(asset_key), 0) + 1 FROM dim_assets), -- Next available key
    'EQ_MFG_001',                          -- Same natural key
    'CNC Machine Haas VF-2',               -- Same name
    'Equipment',                            -- Same class
    'CNC Machine (Under Maintenance)',      -- Updated type to reflect status
    '2024-07-01',                          -- Effective start date
    NULL,                                   -- Open-ended (will be closed when status changes again)
    TRUE                                    -- This is now the current version
);

-- --------------------------------------------------------------------------
-- Step 2: Equipment returns to active status (2024-10-01)
-- --------------------------------------------------------------------------
-- Close maintenance record
UPDATE dim_assets
SET
    valid_to = '2024-09-30',              -- End date for "Maintenance" status
    is_current = FALSE
WHERE asset_id = 'EQ_MFG_001'
  AND is_current = TRUE;

-- Insert new record with "Active" status
INSERT INTO dim_assets (
    asset_key,
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    is_current
) VALUES (
    (SELECT COALESCE(MAX(asset_key), 0) + 1 FROM dim_assets),
    'EQ_MFG_001',
    'CNC Machine Haas VF-2',
    'Equipment',
    'CNC Machine',                         -- Back to normal type
    '2024-10-01',
    NULL,                                   -- Currently active (open-ended)
    TRUE
);

-- ============================================================================
-- EXAMPLE 2: Certification Regulatory Update
-- ============================================================================
-- Scenario: CERT_MFG_001 (CE Marking) requirements updated to v2.0

-- Initial state:
-- asset_key=X, asset_id='CERT_MFG_001', asset_type='Product Certification',
-- valid_from='2023-01-01', valid_to=NULL, is_current=TRUE

-- --------------------------------------------------------------------------
-- Step: Regulatory standard updated (2025-01-01)
-- --------------------------------------------------------------------------
-- Close current record (v1.0)
UPDATE dim_assets
SET
    valid_to = '2024-12-31',              -- End date for v1.0 standard
    is_current = FALSE
WHERE asset_id = 'CERT_MFG_001'
  AND is_current = TRUE;

-- Insert new record with updated requirements (v2.0)
INSERT INTO dim_assets (
    asset_key,
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    is_current
) VALUES (
    (SELECT COALESCE(MAX(asset_key), 0) + 1 FROM dim_assets),
    'CERT_MFG_001',
    'CE Marking - Product Line A (Standard v2.0)', -- Updated name to reflect version
    'Certification',
    'Product Certification',
    '2025-01-01',                          -- New standard effective date
    NULL,                                   -- Currently in effect
    TRUE
);

-- ============================================================================
-- VALIDATION: Query to see SCD Type 2 in action
-- ============================================================================
-- This query shows all historical versions of assets that have changed

SELECT
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    is_current,
    CASE
        WHEN valid_to IS NULL THEN 'Current'
        ELSE 'Historical'
    END as record_status,
    -- Calculate days this version was valid
    CASE
        WHEN valid_to IS NULL THEN JULIANDAY('now') - JULIANDAY(valid_from)
        ELSE JULIANDAY(valid_to) - JULIANDAY(valid_from) + 1
    END as days_valid
FROM dim_assets
WHERE asset_id IN ('EQ_MFG_001', 'CERT_MFG_001')
ORDER BY asset_id, valid_from;

-- Expected output for EQ_MFG_001:
-- | asset_id    | asset_name          | valid_from | valid_to   | is_current | record_status |
-- |-------------|---------------------|------------|------------|------------|---------------|
-- | EQ_MFG_001  | CNC Machine...      | 2023-01-01 | 2024-06-30 | FALSE      | Historical    |
-- | EQ_MFG_001  | CNC Machine...      | 2024-07-01 | 2024-09-30 | FALSE      | Historical    |
-- | EQ_MFG_001  | CNC Machine...      | 2024-10-01 | NULL       | TRUE       | Current       |

-- ============================================================================
-- POINT-IN-TIME QUERY EXAMPLE
-- ============================================================================
-- Business question: "What was the status of EQ_MFG_001 on 2024-08-15?"

SELECT
    asset_id,
    asset_name,
    asset_class,
    asset_type,
    valid_from,
    valid_to,
    'Answer: Under Maintenance' as status
FROM dim_assets
WHERE asset_id = 'EQ_MFG_001'
  AND '2024-08-15' BETWEEN valid_from AND COALESCE(valid_to, '9999-12-31');

-- This query returns the "Maintenance" version, demonstrating historical compliance capability

-- ============================================================================
-- SCD TYPE 2 BEST PRACTICES
-- ============================================================================
-- 1. Always use surrogate keys (asset_key changes with each version)
-- 2. Keep natural key stable (asset_id stays the same across versions)
-- 3. Use valid_from/valid_to for temporal queries
-- 4. Maintain is_current flag for easy current-state queries
-- 5. Never DELETE old versions (history is critical for compliance)
-- 6. For bulk updates, wrap in transactions to ensure consistency

-- ============================================================================
-- PRODUCTION NOTES
-- ============================================================================
-- In production, SCD Type 2 updates would be triggered by:
-- 1. Equipment lifecycle events (maintenance, disposal, reactivation)
-- 2. Regulatory changes (certification renewals, standard updates)
-- 3. Asset reclassifications (tax treatment changes, jurisdiction transfers)
-- 4. Ownership changes (different family takes control)
--
-- These updates should be:
-- - Logged in audit trail
-- - Approved by compliance officer
-- - Dated to match legal/regulatory effective date (not system date)
