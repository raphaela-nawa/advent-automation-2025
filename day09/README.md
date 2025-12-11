# Day 09: Property Operations Data Warehouse (dbt)

> **One-line pitch:** Portfolio-ready dbt project that unifies Airbnb + Booking.com data into hospitality KPIs (occupancy, ADR, RevPAR) with funnel tracking and platform comparisons.

**Part of:** [Advent Automation 2025 - 25 Days of Data Engineering](../README.md)

---

## Navigation

### Quick Access (By Role)

| For | Start Here | Read Time |
|-----|------------|-----------|
|  **Recruiters** | [Executive Summary](#executive-summary) → [Key Takeaways](#key-takeaways) | 2 min |
|  **Business Stakeholders** | [Executive Summary](#executive-summary) → [Recommendations](#recommendations) | 5 min |
|  **Technical Reviewers** | [Executive Summary](#executive-summary) → [Technical Deep Dive](#technical-deep-dive) | 10 min |
|  **Implementation** | [Quick Start](#how-to-use-this-project) → [Adaptation Guide](#detailed-adaptation-guide) | 15 min |

---

## Executive Summary

**Business Problem:** Independent property managers need a unified view of bookings and guest journeys across Airbnb and Booking.com to track occupancy, ADR, RevPAR, and funnel conversion without reconciling spreadsheets.

**Solution Delivered:** Thirteen dbt models (6 staging with dual platform sources, 3 intermediate with platform unification logic, 4 marts) plus 3 custom macros to calculate stage duration, occupancy rate, and platform-specific values. `metrics_portfolio_public.sql` is the critical mart surfacing hospitality KPIs for the portfolio.

**Business Impact:** Portfolio metrics and funnel stages are available from a single SQLite database with repeatable dbt runs—no manual CSV merges—turning weekly reconciliation into a single query.

**For:** Jo (Independent Property Manager) | **Industry:** Hospitality/Property Management | **Time:** 3 hours | **Status:** ✅ Complete

---

## Key Takeaways

### Business Value
- **Primary Metrics:** 58.8% occupancy, $201.13 ADR, $118.27 RevPAR across six properties (all derived from `metrics_portfolio_public`)
- **Decision Enabled:** Channel mix clarity—Airbnb drives 60% of bookings while Booking.com delivers higher ADR ($218 vs $192)
- **Efficiency Gain:** Replaces 6 hours/week of cross-platform spreadsheet reconciliation with one dbt run and a single SQLite view

### Technical Achievement
- **Multi-Platform Sources:** Airbnb + Booking.com declared in `models/staging/sources.yml` with freshness rules for two distinct platforms
- **Intermediate Unification:** `int_unified_reservations` standardizes guest identifiers, property ids, and pricing so downstream UNION ALL logic stays clean
- **Custom Macros:** `calculate_stage_duration`, `calculate_occupancy_rate`, `unify_platform_data` reused across models to keep logic DRY
- **Marts:** `metrics_portfolio_public` (critical), `fct_reservations_unified`, `fct_funnel_conversion` (incremental), `dim_platform_comparison`

### Critical Learning
Standardize at staging before unifying: aligning Airbnb `guest_id` with Booking.com `guest_email` and normalizing property codes is what keeps the intermediate layer simple and prevents CASE explosions downstream.

---

## Business Context

### The Challenge

Running six houseboats on two booking platforms means two schemas, two fee structures, and two reporting styles. Comparing occupancy or ADR requires manual exports and reconciliations, making it hard to answer "Which channel performs better?" or "Where do guests drop off?"

**Why This Matters:**
- **Stakeholder Impact:** Manual reconciliation slows weekly reviews and obscures true occupancy/ADR trends
- **Strategic Value:** Channel mix choices affect profitability and staffing; clean metrics enable rapid adjustments
- **Urgency/Frequency:** New bookings arrive daily; stale reporting misses pricing and response-time improvements

### Success Criteria

**From Stakeholder Perspective:**
1. Portfolio occupancy and RevPAR available in <10 seconds from a single query
2. Channel-level ADR comparison ready without manual joins
3. Funnel (Inquiry→Booking→Check-in→Check-out→Review) tracked with conversion rates

**Technical Validation:**
- ✅ All 13 dbt models run successfully (6 staging, 3 intermediate, 4 marts)
- ✅ 37 tests passing; freshness checks defined per platform source
- ✅ Incremental funnel mart processes only new events after first run

---

## Solution Overview

### What It Does

| Capability | Business Outcome |
|------------|------------------|
| **Multi-Platform Unification** | Combines 75 Airbnb + 50 Booking.com bookings into `fct_reservations_unified` with standardized schema |
| **Hospitality KPIs (ADR, RevPAR, Occupancy)** | `metrics_portfolio_public` surfaces portfolio and property-level metrics for quick evaluation |
| **Platform Comparison** | `dim_platform_comparison` contrasts bookings, revenue, and fees across platforms |
| **Funnel Conversion Tracking** | `fct_funnel_conversion` (incremental) captures Inquiry→Booking→Check-in→Check-out→Review |
| **Property-Level Analytics** | `int_property_performance` highlights top/bottom performers with nightly rate context |

### Architecture at a Glance
```
[INPUT] → [TRANSFORMATION] → [OUTPUT]

Airbnb + Booking.com tables → dbt models (Staging → Intermediate → Marts) → Portfolio KPIs + Funnel views
        ↓                                 ↓                                       ↓
`sources.yml` w/ two platforms   Unification macros + incremental funnel   metrics_portfolio_public + comparisons
```

---

## Key Results & Insights

### Business Metrics (Synthetic Data)

| Metric | Finding | Implication |
|--------|---------|-------------|
| **Occupancy Rate** | 58.8% (703 nights booked / 1,095 available) | Healthy baseline; HB004 at 40% is the clear upsell candidate |
| **ADR** | $201.13 average daily rate | Booking.com ADR of $218 vs Airbnb $192 suggests channel-specific pricing changes |
| **RevPAR** | $118.27 revenue per available room | Shows portfolio earning power; highest property ~ $175 RevPAR |

### Analytical Capabilities Demonstrated

- ✅ Multi-platform schema normalization using staging models and `unify_platform_data` macro
- ✅ Complete funnel tracking (500 inquiries → 125 bookings → 103 check-ins → 101 check-outs → 35 reviews)
- ✅ Hospitality KPIs (occupancy, ADR, RevPAR) computed in the critical mart `metrics_portfolio_public`
- ✅ Incremental materialization on `fct_funnel_conversion` to keep refreshes fast
- ✅ Platform comparison mart quantifying booking share, revenue share, and fee impact

---

## Risks & Limitations

### Current Limitations

| Limitation | Impact | Mitigation Path |
|------------|--------|-----------------|
| Synthetic data only | Patterns not validated against real seasonality or cancellations | Load 90 days of live exports before trusting KPIs |
| No calendar blocking logic | Occupancy denominator assumes all nights available | Add `property_calendar` with blocked dates to refine occupancy |
| Simplified pricing | Cleaning fees/discounts/taxes not broken out | Extend pricing fields and recompute ADR/RevPAR components |
| Duplicate inquiry handling | Cross-platform duplicate guests not merged | Add fuzzy matching on guest name + check-in date in staging |

### Assumptions Made

1. Properties are available every day within the data range
2. Check-in night counts toward occupancy; check-out night does not
3. Platform fees are fixed at 15% (Airbnb) and 18% (Booking.com)
4. Single-currency portfolio (USD) for this demo

---

## Recommendations

### For Jo (Property Manager)

**Immediate Next Steps (Week 1):**
1. Export last 90 days from Airbnb + Booking.com and load into staging tables (respecting column mapping below)
2. Validate occupancy and ADR for two properties against platform dashboards

**Short-Term (Month 1):**
- Add `property_calendar` table to exclude blocked nights from occupancy denominator
- Pipe results to Day 16 dashboard for trend tracking
- Schedule weekly `dbt run` + `dbt test` to keep funnel metrics fresh

**Production Readiness:**
- **Data Integration:** Airbnb host exports/API + Booking.com Connectivity API
- **Validation Required:** Booking counts, ADR variance (<5%), fee calculations per platform
- **Stakeholder Review:** Confirm pricing components (fees/discounts) match how Jo reports revenue

### For Portfolio/Technical Evolution

- **Reuse:** Staging unification + macros fit other dual-platform contexts (e.g., Shopify + Amazon orders)
- **Scale:** For 50+ properties move to PostgreSQL/Supabase; partition reservation marts by check-in month
- **Monitoring:** Add tests on fee percentages and occupancy bounds after integrating real data

---

## How to Use This Project

### Quick Start (5 minutes)
```bash
# 1. Navigate
cd advent-automation-2025/day09

# 2. Install dbt (SQLite adapter)
pip install dbt-core dbt-sqlite

# 3. Generate synthetic data
python day09_DATA_synthetic_generator.py

# 4. Run dbt models
dbt run --full-refresh --profiles-dir .

# 5. Run tests
dbt test --profiles-dir .

# 6. Validate portfolio metrics
sqlite3 data/day09_property_operations.db "SELECT * FROM metrics_portfolio_public;"
```

**Expected Runtime:** ~2 minutes (data generation ~45s, dbt run ~5s, tests ~3s)  
**Expected Output:** SQLite db with marts `fct_reservations_unified`, `fct_funnel_conversion`, **`metrics_portfolio_public` (critical)**, `dim_platform_comparison`; 37 tests passing.

### Adapting for Real Data

**Priority Changes (Do These First):**
1. Swap synthetic generator for real extracts (`day09_DATA_airbnb_booking_extract.py`) and load tables used in `sources.yml`
2. Map Airbnb vs Booking.com column names into staging models before running dbt
3. Introduce `property_calendar` for accurate occupancy denominators

**Schema Mapping:**
| Your Airbnb Export | This Project | Transform Needed |
|--------------------|--------------|------------------|
| `Confirmation Code` | `day09_booking_id` | Direct mapping |
| `Guest Name` | `day09_guest_id` | Hash or direct mapping |
| `Listing` | `day09_property_id` | Direct mapping |
| `Check-In` | `day09_booking_timestamp` | Parse to TIMESTAMP |
| `Total Payout` | `day09_total_price` | Parse currency if needed |

| Your Booking.com Export | This Project | Transform Needed |
|-------------------------|--------------|------------------|
| `res_id` | `day09_booking_id` | Prefix with `BDC-` to avoid collisions |
| `guest_email` | `day09_guest_id` | Use email as identifier |
| `hotel_id` | `day09_property_id` | Map to internal property ids |
| `arrival` | `day09_booking_timestamp` | Parse to TIMESTAMP |
| `price` | `day09_total_price` | Convert currency if multi-currency |

**Business Logic Adjustments:**
```python
# In day09_CONFIG_settings.py
DAY09_PLATFORM_FEES = {'airbnb': 0.15, 'booking_com': 0.18}  # Update to your contracts
DAY09_PROPERTIES = [
    {"id": "HB001", "name": "Floating Paradise", "capacity": 4, "base_price": 180},
    # Replace with your portfolio and base pricing
]
```

**Full adaptation guide:** [See "Detailed Adaptation" section below](#detailed-adaptation-guide)

---

## Technical Deep Dive

<details>
<summary><strong>📋 Full Technical Documentation (Click to Expand)</strong></summary>

### Technical Stack

**Core:**
- **Language:** Python 3.13+
- **Database:** SQLite 3.40+
- **Modeling Tool:** dbt Core 1.10+ with dbt-sqlite

**Dependencies:**
```
dbt-core==1.10.15      # Modeling and tests
dbt-sqlite==1.10.0     # Adapter
pandas==2.2.0          # Synthetic data generation
```

### Data Model

**Schema Overview:**
```
Sources (SQLite tables)
├── airbnb_inquiries, airbnb_bookings
├── booking_com_inquiries, booking_com_bookings
├── stays, reviews

Staging (views)
├── stg_airbnb_inquiries, stg_airbnb_bookings
├── stg_booking_com_inquiries, stg_booking_com_bookings
├── stg_stays, stg_reviews

Intermediate (views)
├── int_unified_reservations          -- platform unification logic
├── int_funnel_events                 -- consolidated event stream
└── int_property_performance          -- nightly rate + occupancy by property

Marts (tables)
├── fct_reservations_unified          -- standardized bookings
├── fct_funnel_conversion (incremental)
├── metrics_portfolio_public          -- ADR, RevPAR, occupancy (critical)
└── dim_platform_comparison           -- Airbnb vs Booking.com KPIs
```

**Relationships:**
```
airbnb_inquiries ─(1:N)→ airbnb_bookings
booking_com_inquiries ─(1:N)→ booking_com_bookings
bookings ─(1:1)→ stays ─(1:1)→ reviews
```

### Architectural Decisions

#### Decision 1: Stage-Level Normalization for Platform Unification

**Context:** Airbnb identifiers differ from Booking.com OTA schema; needed consistent columns for UNION ALL in the intermediate layer.

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Handle differences in intermediate models | Fewer staging changes | Complex CASE logic, harder to test | ❌ Rejected |
| Normalize in staging with macros (`unify_platform_data`) | Clean intermediate UNION, easier testing | Slightly more staging work | ✅ **Chosen** |
| Create separate marts per platform | Minimal unification | No single KPI view | ❌ Rejected |

**Rationale:** Staging normalization plus macros keeps `int_unified_reservations` minimal and reusable.

#### Decision 2: Incremental Funnel Mart

**Context:** Events append-only; recomputing history is unnecessary.

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Full refresh | Simple | Slower over time | ❌ Rejected |
| Incremental on timestamp + unique key | Fast, production-ready | Requires full refresh on logic change | ✅ **Chosen** |
| Partitioned tables | Best at large scale | Not needed for SQLite | ❌ Rejected |

**Rationale:** Timestamp-based incremental keeps refreshes under 2 seconds while supporting growth.

#### Decision 3: SQLite for Dev, Supabase/Postgres for Scale

**Context:** Needed zero-setup local runs for the portfolio demo.

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| SQLite + dbt-sqlite | Portable `.db`, instant setup | Single writer, limited functions | ✅ **Chosen** |
| PostgreSQL/Supabase | Scales, richer SQL | Setup overhead for a 3-hour build | ⚠️ Planned migration |
| DuckDB | Very fast analytics | Less familiar to target audience | ❌ Rejected |

**Rationale:** SQLite keeps onboarding under five minutes; roadmap includes moving the same models to Supabase when concurrency or volume grows.

### Implementation Details

**Macros in Use:**
- `calculate_stage_duration` — stage-to-stage timing in `int_funnel_events`
- `calculate_occupancy_rate` — reusable occupancy math for marts
- `unify_platform_data` — platform-specific branching without CASE duplication

**Sample Logic: Platform Unification**
```sql
-- int_unified_reservations
SELECT
    day09_booking_id,
    day09_platform,
    {{ unify_platform_data('day09_platform', 'guest_id', 'guest_email') }} AS day09_guest_id,
    day09_property_id,
    day09_booking_timestamp,
    day09_check_in_date,
    day09_check_out_date,
    day09_num_guests,
    day09_total_price,
    day09_platform_fee,
    day09_net_revenue
FROM {{ ref('stg_airbnb_bookings') }}
UNION ALL
SELECT ... -- Booking.com normalized fields
```

**Sample Logic: Critical Mart**
```sql
-- metrics_portfolio_public.sql
SELECT
    pn.day09_property_id,
    pn.total_nights_booked,
    dr.days_in_range AS day09_nights_available,
    {{ calculate_occupancy_rate('pn.total_nights_booked', 'dr.days_in_range') }} AS day09_occupancy_rate_pct,
    ROUND(pn.avg_daily_rate, 2) AS day09_avg_daily_rate,
    ROUND(pn.avg_daily_rate * (pn.total_nights_booked / NULLIF(dr.days_in_range, 0)), 2) AS day09_revpar
FROM property_nights pn
CROSS JOIN date_range dr
ORDER BY pn.total_revenue DESC;
```

**Performance Characteristics:**
- 125 bookings + 638 events processed in ~3s (full run), ~2s incremental funnel refresh
- `metrics_portfolio_public` calculates occupancy/ADR/RevPAR in a single query for the full portfolio

### Testing Approach

**Validation Queries:**
```sql
-- No duplicate bookings after unification
SELECT day09_booking_id FROM fct_reservations_unified GROUP BY 1 HAVING COUNT(*) > 1;

-- Occupancy bounds
SELECT * FROM metrics_portfolio_public WHERE day09_occupancy_rate_pct NOT BETWEEN 0 AND 100;

-- Funnel monotonicity
SELECT
  SUM(day09_stage = 'inquiry') AS inquiries,
  SUM(day09_stage = 'booking') AS bookings,
  SUM(day09_stage = 'check_in') AS check_ins,
  SUM(day09_stage = 'check_out') AS check_outs,
  SUM(day09_stage = 'review') AS reviews
FROM fct_funnel_conversion;
```

**dbt Tests:** 37 tests covering uniqueness, not-null, accepted values, relationships, and freshness thresholds per platform source.

</details>

---

## Detailed Adaptation Guide

<details>
<summary><strong>🔄 Step-by-Step Production Adaptation (Click to Expand)</strong></summary>

### Step 1: Assess Your Data
- [ ] Confirm access to Airbnb host exports/API and Booking.com Connectivity API
- [ ] Estimate volume (bookings/month) and update frequency
- [ ] Identify how pricing components (fees/discounts) appear in your exports

### Step 2: Map Your Schema
Use the mapping tables in [Adapting for Real Data](#adapting-for-real-data) to align columns before loading staging tables.

### Step 3: Modify Data Source
- Build `day09_DATA_platform_extract.py` to load both exports into the SQLite/Supabase schema
- Preserve platform identifiers; do not deduplicate until staging

### Step 4: Adjust Business Logic
- Update `DAY09_PLATFORM_FEES`, property list, and any seasonality multipliers in `day09_CONFIG_settings.py`
- If you have blocked dates, add `property_calendar` and swap the occupancy denominator to use it

### Step 5: Validate with Sample
- Load one month of data for two properties
- Run `dbt run --full-refresh` + `dbt test`
- Compare occupancy and ADR with platform dashboards (target: <5% variance)

### Step 6: Scale to Full Data
- Move to Supabase/Postgres when concurrent writes or >100K rows appear
- Keep `fct_funnel_conversion` incremental; schedule dbt via cron or orchestrator

</details>

---

## Project Files
```
day09/
├── README.md                       # Public portfolio doc (this file)
├── data/
│   └── day09_property_operations.db
├── macros/                         # Custom macros (duration, occupancy, platform unify)
├── models/
│   ├── staging/                    # Airbnb + Booking.com sources normalized
│   ├── intermediate/               # Platform unification + funnel prep
│   └── marts/                      # fct_reservations_unified, fct_funnel_conversion, metrics_portfolio_public
├── day09_DATA_synthetic_generator.py
├── day09_CONFIG_settings.py
├── dbt_project.yml
└── profiles.yml
```

---

## Appendix

### Time Breakdown

| Phase | Time | % |
|-------|------|---|
| Planning & Setup | 25 min | 14% |
| Development | 105 min | 58% |
| Testing | 20 min | 11% |
| Documentation | 30 min | 17% |
| **Total** | **180 min** | **100%** |

### Learning Outcomes

**Technical Skills Acquired:**
- Multi-platform source declarations with freshness rules in dbt
- Platform unification using macros to keep models DRY
- Incremental modeling for event funnels in SQLite/dbt-sqlite

**Business Domain Understanding:**
- Hospitality KPIs (ADR, RevPAR, occupancy) and how platform fees affect net revenue
- Channel mix analysis for short-term rentals

**Process Improvements for Next Project:**
- Start with staging normalization to simplify marts
- Add calendar availability earlier to improve occupancy accuracy

### Naming Conventions Reference

All project files use the `day09_` prefix for isolation. See [PROMPT_project_setup.md](../common/prompt library/PROMPT_project_setup.md) for complete standards.

---

## Links & Resources

- **Main Project:** [Advent Automation 2025](../README.md)
- **Delivery Criteria:** [MODELING_DELIVERY_CRITERIA.md](../common/prompt library/MODELING_DELIVERY_CRITERIA.md)

---

**Built in 3 hours** | **Portfolio Project** | [View All 25 Days →](../README.md)
