-- ============================================================================
-- Day 10: Family Office Data Warehouse - Star Schema Definition
-- ============================================================================
-- Creates all dimension and fact tables for the Kimball star schema
-- Designed for family office multi-jurisdictional portfolio tracking
-- ============================================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS fct_holdings;
DROP TABLE IF EXISTS dim_assets;
DROP TABLE IF EXISTS dim_accounts;
DROP TABLE IF EXISTS dim_clients;
DROP TABLE IF EXISTS dim_date;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- dim_date: Conformed date dimension (reusable for Day 16)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,          -- Surrogate key (YYYYMMDD format)
    full_date DATE NOT NULL,               -- Actual date
    year INTEGER NOT NULL,                 -- Year (2023, 2024, etc.)
    quarter INTEGER NOT NULL,              -- Quarter (1-4)
    month INTEGER NOT NULL,                -- Month (1-12)
    fiscal_quarter INTEGER NOT NULL,       -- Fiscal quarter (configurable)
    fiscal_year INTEGER NOT NULL           -- Fiscal year
);

CREATE INDEX idx_dim_date_full_date ON dim_date(full_date);
CREATE INDEX idx_dim_date_year_quarter ON dim_date(year, quarter);

-- ----------------------------------------------------------------------------
-- dim_clients: Family office clients
-- ----------------------------------------------------------------------------
CREATE TABLE dim_clients (
    client_key INTEGER PRIMARY KEY,        -- Surrogate key
    client_id VARCHAR(50) NOT NULL UNIQUE, -- Natural key (FAM_001, FAM_002, etc.)
    client_name VARCHAR(200) NOT NULL,     -- "Smith Family", "MFG Owner Family", etc.
    client_type VARCHAR(50) NOT NULL       -- "Traditional Investments", "Manufacturing Owner", etc.
);

CREATE INDEX idx_dim_clients_id ON dim_clients(client_id);
CREATE INDEX idx_dim_clients_name ON dim_clients(client_name);

-- ----------------------------------------------------------------------------
-- dim_accounts: Investment and operating accounts
-- ----------------------------------------------------------------------------
CREATE TABLE dim_accounts (
    account_key INTEGER PRIMARY KEY,       -- Surrogate key
    account_id VARCHAR(50) NOT NULL UNIQUE,-- Natural key (ACC_FAM_001_001, etc.)
    account_name VARCHAR(200) NOT NULL,    -- "Investment Account", "MFG Company Operating Account", etc.
    account_type VARCHAR(50) NOT NULL,     -- "Operating", "Investment", etc.
    parent_client_key INTEGER NOT NULL,    -- FK to dim_clients
    FOREIGN KEY (parent_client_key) REFERENCES dim_clients(client_key)
);

CREATE INDEX idx_dim_accounts_id ON dim_accounts(account_id);
CREATE INDEX idx_dim_accounts_client ON dim_accounts(parent_client_key);
CREATE INDEX idx_dim_accounts_type ON dim_accounts(account_type);

-- ----------------------------------------------------------------------------
-- dim_assets: Assets with SCD Type 2 support (Equipment, IP, Certifications, Financial)
-- Conformed dimension (reusable for Day 16)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_assets (
    asset_key INTEGER PRIMARY KEY,         -- Surrogate key (changes with each version)
    asset_id VARCHAR(50) NOT NULL,         -- Natural key (EQ_MFG_001, IP_MFG_002, etc.)
    asset_name VARCHAR(200) NOT NULL,      -- "CNC Machine Haas VF-2", "Patent EP12345", etc.
    asset_class VARCHAR(50) NOT NULL,      -- "Equipment", "IP", "Certification", "Equity", "Operating Company"
    asset_type VARCHAR(50),                -- Subtype within class ("CNC Machine", "Patent", etc.)
    valid_from DATE NOT NULL,              -- SCD Type 2: Start date for this version
    valid_to DATE,                         -- SCD Type 2: End date (NULL if current)
    is_current BOOLEAN NOT NULL DEFAULT TRUE  -- SCD Type 2: TRUE for latest version
);

CREATE INDEX idx_dim_assets_id ON dim_assets(asset_id);
CREATE INDEX idx_dim_assets_class ON dim_assets(asset_class);
CREATE INDEX idx_dim_assets_current ON dim_assets(is_current);
CREATE INDEX idx_dim_assets_valid_dates ON dim_assets(valid_from, valid_to);
CREATE INDEX idx_dim_assets_mfg ON dim_assets(asset_id) WHERE asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%';

-- ============================================================================
-- FACT TABLE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- fct_holdings: Portfolio holdings at asset-account-date grain
-- ----------------------------------------------------------------------------
CREATE TABLE fct_holdings (
    holding_key INTEGER PRIMARY KEY,       -- Surrogate key for each holding record
    client_key INTEGER NOT NULL,           -- FK to dim_clients
    asset_key INTEGER NOT NULL,            -- FK to dim_assets
    account_key INTEGER NOT NULL,          -- FK to dim_accounts
    date_key INTEGER NOT NULL,             -- FK to dim_date
    quantity DECIMAL(18, 4) NOT NULL,      -- Number of shares/units/percentage
    market_value DECIMAL(18, 2) NOT NULL,  -- Current market value
    cost_basis DECIMAL(18, 2),             -- Original cost basis

    FOREIGN KEY (client_key) REFERENCES dim_clients(client_key),
    FOREIGN KEY (asset_key) REFERENCES dim_assets(asset_key),
    FOREIGN KEY (account_key) REFERENCES dim_accounts(account_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE INDEX idx_fct_holdings_client ON fct_holdings(client_key);
CREATE INDEX idx_fct_holdings_asset ON fct_holdings(asset_key);
CREATE INDEX idx_fct_holdings_account ON fct_holdings(account_key);
CREATE INDEX idx_fct_holdings_date ON fct_holdings(date_key);
CREATE INDEX idx_fct_holdings_composite ON fct_holdings(date_key, client_key, asset_key);

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Uncomment to validate schema after creation:

-- SELECT 'dim_date' as table_name, COUNT(*) as row_count FROM dim_date
-- UNION ALL
-- SELECT 'dim_clients', COUNT(*) FROM dim_clients
-- UNION ALL
-- SELECT 'dim_accounts', COUNT(*) FROM dim_accounts
-- UNION ALL
-- SELECT 'dim_assets', COUNT(*) FROM dim_assets
-- UNION ALL
-- SELECT 'fct_holdings', COUNT(*) FROM fct_holdings;
