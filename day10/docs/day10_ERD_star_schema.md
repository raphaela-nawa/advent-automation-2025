

# Day 10: Family Office Data Warehouse - Star Schema ERD

## Overview

This document describes the Kimball star schema for the Family Office Data Warehouse, designed for multi-jurisdictional portfolio tracking with SCD Type 2 historical compliance capabilities.

---

## Star Schema Design

### Grain

**Fact Table Grain:** One row per asset per account per date

**Key Decision:** Monthly snapshots provide sufficient granularity for wealth planning while keeping fact table size manageable.

---

## Dimension Tables

### 1. dim_date (Conformed Dimension)

**Purpose:** Conformed date dimension for temporal analysis (reusable in Day 16)

**Type:** Standard dimension (no SCD)

**Structure:**
```
dim_date
├── date_key (PK)              INTEGER - Surrogate key (YYYYMMDD format)
├── full_date                  DATE    - Actual date value
├── year                       INTEGER - Year (2023, 2024, etc.)
├── quarter                    INTEGER - Calendar quarter (1-4)
├── month                      INTEGER - Month (1-12)
├── fiscal_quarter             INTEGER - Fiscal quarter (configurable)
└── fiscal_year                INTEGER - Fiscal year
```

**Business Rules:**
- date_key format: YYYYMMDD (e.g., 20240615 for June 15, 2024)
- Fiscal year alignment: Configurable via CONFIG (currently calendar year = fiscal year)
- Date range: 2023-01-01 to 2024-12-31 (24 months)

**Indexes:**
- `idx_dim_date_full_date` on (full_date)
- `idx_dim_date_year_quarter` on (year, quarter)

---

### 2. dim_clients (Family Dimension)

**Purpose:** Family office clients (UHNW families)

**Type:** Standard dimension (no SCD)

**Structure:**
```
dim_clients
├── client_key (PK)            INTEGER - Surrogate key
├── client_id                  VARCHAR - Natural key (FAM_001, FAM_002, etc.)
├── client_name                VARCHAR - "Smith Family", "MFG Owner Family", etc.
└── client_type                VARCHAR - "Traditional Investments", "Manufacturing Owner", etc.
```

**Business Rules:**
- 5 families total
- **Critical:** FAM_003 = "MFG Owner Family" (owns operational assets for Day 16)
- client_id follows pattern: FAM_XXX

**Indexes:**
- `idx_dim_clients_id` on (client_id)
- `idx_dim_clients_name` on (client_name)

---

### 3. dim_accounts (Account Dimension)

**Purpose:** Investment and operating accounts for each family

**Type:** Standard dimension (no SCD)

**Structure:**
```
dim_accounts
├── account_key (PK)           INTEGER - Surrogate key
├── account_id                 VARCHAR - Natural key (ACC_FAM_001_001, etc.)
├── account_name               VARCHAR - "Investment Account", "MFG Company Operating Account"
├── account_type               VARCHAR - "Operating", "Investment", etc.
└── parent_client_key (FK)     INTEGER → dim_clients.client_key
```

**Business Rules:**
- Each family has 2-3 accounts
- **Critical:** MFG Owner Family must have "MFG Company Operating Account"
- parent_client_key links account to family (enables consolidated family reporting)

**Indexes:**
- `idx_dim_accounts_id` on (account_id)
- `idx_dim_accounts_client` on (parent_client_key)
- `idx_dim_accounts_type` on (account_type)

---

### 4. dim_assets (SCD Type 2 Dimension - Conformed)

**Purpose:** Portfolio assets with historical tracking (Equipment, IP, Certifications, Financial)

**Type:** SCD Type 2 (tracks historical changes in classifications)

**Structure:**
```
dim_assets
├── asset_key (PK)             INTEGER - Surrogate key (changes with each version)
├── asset_id                   VARCHAR - Natural key (EQ_MFG_001, IP_MFG_002, etc.)
├── asset_name                 VARCHAR - "CNC Machine Haas VF-2", "Patent EP12345"
├── asset_class                VARCHAR - "Equipment", "IP", "Certification", "Equity"
├── asset_type                 VARCHAR - Subtype within class ("CNC Machine", "Patent")
├── valid_from                 DATE    - SCD Type 2: Start date for this version
├── valid_to                   DATE    - SCD Type 2: End date (NULL if current)
└── is_current                 BOOLEAN - SCD Type 2: TRUE for latest version
```

**Asset Classes:**
- **Equity:** Stocks, bonds, funds (50 assets)
- **Operating Company:** Operating company stakes (20 assets)
- **Equipment:** Manufacturing equipment (10 assets - **CRITICAL FOR DAY 16**)
- **IP:** Patents, trademarks, copyrights (10 assets - **CRITICAL FOR DAY 16**)
- **Certification:** Regulatory certifications (10 assets - **CRITICAL FOR DAY 16**)

**Business Rules:**
- asset_key (surrogate) changes with each new version
- asset_id (natural key) stays constant across versions
- **MFG operational assets:** EQ_MFG_*, IP_MFG_*, CERT_MFG_* (30 total for Day 16)
- SCD Type 2 triggers:
  * Equipment lifecycle changes (Active → Maintenance → Active)
  * Certification renewals (Standard v1.0 → v2.0)
  * Regulatory reclassifications

**Indexes:**
- `idx_dim_assets_id` on (asset_id)
- `idx_dim_assets_class` on (asset_class)
- `idx_dim_assets_current` on (is_current)
- `idx_dim_assets_valid_dates` on (valid_from, valid_to)
- `idx_dim_assets_mfg` on (asset_id) WHERE MFG assets

**SCD Type 2 Example:**
```
asset_key | asset_id    | asset_type             | valid_from | valid_to   | is_current
----------|-------------|------------------------|------------|------------|------------
1         | EQ_MFG_001  | CNC Machine            | 2023-01-01 | 2024-06-30 | FALSE
2         | EQ_MFG_001  | CNC Machine (Maint...) | 2024-07-01 | 2024-09-30 | FALSE
3         | EQ_MFG_001  | CNC Machine            | 2024-10-01 | NULL       | TRUE
```

---

## Fact Table

### fct_holdings (Transaction Fact)

**Purpose:** Portfolio holdings at asset-account-date grain

**Grain:** One row per asset per account per date (monthly snapshots)

**Structure:**
```
fct_holdings
├── holding_key (PK)           INTEGER - Surrogate key
├── client_key (FK)            INTEGER → dim_clients.client_key
├── asset_key (FK)             INTEGER → dim_assets.asset_key
├── account_key (FK)           INTEGER → dim_accounts.account_key
├── date_key (FK)              INTEGER → dim_date.date_key
├── quantity                   DECIMAL - Shares/units/percentage ownership
├── market_value               DECIMAL - Current market value (EUR)
└── cost_basis                 DECIMAL - Original cost basis (EUR)
```

**Business Rules:**
- Monthly snapshots (1st of each month)
- market_value calculated at month-end
- quantity: shares for equity, units for equipment/certs, % for operating stakes
- **Critical:** MFG operational assets (30) all linked to "MFG Company Operating Account"

**Indexes:**
- `idx_fct_holdings_client` on (client_key)
- `idx_fct_holdings_asset` on (asset_key)
- `idx_fct_holdings_account` on (account_key)
- `idx_fct_holdings_date` on (date_key)
- `idx_fct_holdings_composite` on (date_key, client_key, asset_key)

**Row Count:** ~12,000 rows (100 assets × 24 months × varying family holdings)

---

## Entity Relationships

### Visual Representation (Text-based)

```
┌─────────────────────────┐
│     dim_date            │
│  - date_key (PK)        │
│  - full_date            │
│  - year, quarter, month │
│  - fiscal_quarter       │
└──────────┬──────────────┘
           │
           │ (N:1)
           ↓
┌──────────────────────────────────────────────────────┐
│                  fct_holdings                        │
│  - holding_key (PK)                                  │
│  - client_key (FK) ────→ dim_clients.client_key      │
│  - asset_key (FK) ─────→ dim_assets.asset_key        │
│  - account_key (FK) ───→ dim_accounts.account_key    │
│  - date_key (FK) ──────→ dim_date.date_key           │
│  - quantity, market_value, cost_basis                │
└──────────────────────────────────────────────────────┘
     ↑           ↑           ↑
     │ (N:1)     │ (N:1)     │ (N:1)
     │           │           │
┌────┴────────┐  │  ┌────────┴──────────┐
│dim_clients  │  │  │  dim_accounts     │
│client_key(PK│  │  │  account_key (PK) │
│client_id    │  │  │  account_id       │
│client_name  │  │  │  account_name     │
│client_type  │  │  │  account_type     │
└─────────────┘  │  │  parent_client_key│─┐
                 │  └───────────────────┘ │
                 │                        │ (N:1)
                 │ (N:1)                  │
                 │                        ↓
            ┌────┴──────────────────────────┐
            │       dim_assets (SCD Type 2) │
            │  - asset_key (PK) - Surrogate │
            │  - asset_id (Natural Key)     │
            │  - asset_name                 │
            │  - asset_class                │
            │  - asset_type                 │
            │  - valid_from, valid_to       │
            │  - is_current                 │
            └───────────────────────────────┘
```

### Cardinalities

- **dim_clients → dim_accounts:** 1:N (one family has multiple accounts)
- **dim_accounts → fct_holdings:** 1:N (one account has many holdings over time)
- **dim_assets → fct_holdings:** 1:N (one asset version appears in many holdings)
- **dim_date → fct_holdings:** 1:N (one date has many holdings)

**Important:** Due to SCD Type 2 on dim_assets, the same asset_id can have multiple asset_keys (one per version). The fact table links to the specific version that was valid at that point in time.

---

## Conformed Dimensions Strategy

### Prepared for Day 16 (Luna's Compliance Dashboard)

Two dimensions are designed as **conformed dimensions** for reuse:

1. **dim_date:**
   - Day 16 will JOIN to same date dimension for temporal analysis
   - Enables cross-project trending (family office portfolio vs. compliance deadlines)

2. **dim_assets:**
   - Day 16 will filter `WHERE asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%'`
   - Same asset_id values, same SCD Type 2 structure
   - Luna's dashboard can leverage historical tracking (e.g., "When did this equipment last enter maintenance?")

**Integration Pattern:**
```sql
-- Day 16 will consume MFG assets via:
SELECT * FROM dim_assets
WHERE asset_id IN (
    SELECT asset_id FROM day10.dim_assets
    WHERE asset_class IN ('Equipment', 'IP', 'Certification')
      AND is_current = TRUE
)
```

---

## Query Patterns

### Pattern 1: Current State (Simple)

```sql
-- Latest portfolio value by client
SELECT c.client_name, SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date)
  AND a.is_current = TRUE
GROUP BY c.client_name;
```

### Pattern 2: Point-in-Time (SCD Type 2)

```sql
-- Portfolio as of June 15, 2024 (historical compliance query)
SELECT c.client_name, a.asset_class, SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE d.full_date = '2024-06-15'
  AND '2024-06-15' BETWEEN a.valid_from AND COALESCE(a.valid_to, '9999-12-31')
GROUP BY c.client_name, a.asset_class;
```

### Pattern 3: Trend Analysis

```sql
-- Portfolio value growth by quarter
SELECT d.year, d.quarter, SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE a.is_current = TRUE
  AND d.month IN (3, 6, 9, 12)  -- Quarter-end months
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;
```

### Pattern 4: MFG Asset Filter (For Day 16)

```sql
-- Isolate MFG operational assets only
SELECT a.asset_id, a.asset_name, a.asset_class, h.market_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
JOIN dim_accounts acc ON h.account_key = acc.account_key
JOIN dim_clients c ON acc.parent_client_key = c.client_key
WHERE c.client_name = 'MFG Owner Family'
  AND a.asset_class IN ('Equipment', 'IP', 'Certification')
  AND a.is_current = TRUE;
```

---

## Design Decisions

### 1. Why Kimball Star Schema (not Data Vault)?

**Chosen:** Kimball Star Schema

**Rationale:**
- **Performance:** Simple 4-way JOINs for analytics (fast aggregations)
- **Business-friendly:** Non-technical users can understand star schema
- **Sufficient flexibility:** SCD Type 2 handles historical tracking needs
- **3-hour constraint:** Kimball faster to implement than Data Vault

**Tradeoff:** Less flexible for adding new source systems (would require dimension redesign)

---

### 2. Why SCD Type 2 on dim_assets (not Snapshot Fact)?

**Chosen:** SCD Type 2 Dimension

**Rationale:**
- **Storage efficiency:** Only stores changes (not daily snapshots)
- **Audit compliance:** Full historical reconstruction capability
- **Query simplicity:** Standard SCD Type 2 pattern

**Tradeoff:** Slightly more complex queries (need valid_from/valid_to filters)

---

### 3. Why Include Operational Assets in Family Office DW?

**Chosen:** Include Equipment/IP/Certification in enterprise DW

**Rationale:**
- **Consolidated wealth view:** Rafael needs total asset picture (financial + operational)
- **Conformed dimensions:** Prepares for Day 16 departmental analytics
- **Kimball bus architecture:** Conformed dimensions enable enterprise + departmental reporting

**Tradeoff:** Mixes enterprise (family office) and departmental (manufacturing compliance) concerns

---

## Table Statistics

| Table | Row Count | Primary Use |
|-------|-----------|-------------|
| dim_date | ~731 | Temporal analysis (2 years) |
| dim_clients | 5 | Family aggregation |
| dim_accounts | ~12 | Account-level reporting |
| dim_assets | ~103 | Asset tracking (100 base + 3 SCD versions) |
| fct_holdings | ~12,000 | Core analytics (100 assets × 24 months × families) |

---

## Validation Queries

```sql
-- Validate star schema referential integrity
SELECT 'dim_date' as table_name, COUNT(*) as row_count FROM dim_date
UNION ALL SELECT 'dim_clients', COUNT(*) FROM dim_clients
UNION ALL SELECT 'dim_accounts', COUNT(*) FROM dim_accounts
UNION ALL SELECT 'dim_assets', COUNT(*) FROM dim_assets
UNION ALL SELECT 'fct_holdings', COUNT(*) FROM fct_holdings;

-- Validate MFG assets (should be exactly 30)
SELECT COUNT(DISTINCT asset_id) as mfg_asset_count
FROM dim_assets
WHERE (asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%')
  AND is_current = TRUE;
```

---

## Future Enhancements (Production)

1. **Add audit columns:** created_by, created_at, updated_by, updated_at
2. **Currency dimension:** Support multi-currency (currently EUR only)
3. **Jurisdiction dimension:** Formalize jurisdiction tracking (currently embedded in asset names)
4. **Bridge tables:** Many-to-many relationships (e.g., asset shared across families)
5. **Incremental refresh:** ETL process for daily/monthly updates (currently full rebuild)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Maintained By:** Day 10 Project
**Critical Dependencies:** Day 16 (Luna's Compliance Dashboard) will consume MFG assets
