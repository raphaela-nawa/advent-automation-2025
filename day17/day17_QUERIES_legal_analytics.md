# Day 17 SQL Queries - Legal Analytics Dashboard

All queries target the Day 10 family office data warehouse: `day10/data/day10_family_office_dw.db`.

## Query List

1. **Portfolio Snapshot (latest date)**
   - File: `day17/queries/day17_QUERY_portfolio_overview.sql`
   - Purpose: Base dataset for portfolio summary metrics and asset breakdowns.
   - Notes: Jurisdiction is derived deterministically from `client_name`.

2. **SCD Type 2 Timeline**
   - File: `day17/queries/day17_QUERY_scd_timeline.sql`
   - Purpose: Show asset classification changes over time (valid_from/valid_to).

3. **Classification Changes This Quarter**
   - File: `day17/queries/day17_QUERY_changes_this_quarter.sql`
   - Purpose: List asset versions that became valid during the current quarter.

4. **Compliance Status by Jurisdiction**
   - File: `day17/queries/day17_QUERY_compliance_by_jurisdiction.sql`
   - Purpose: Count assets by jurisdiction and compliance status.
   - Notes: Compliance status is synthetic, derived from `asset_key % 3`.

5. **Upcoming Compliance Deadlines**
   - File: `day17/queries/day17_QUERY_upcoming_deadlines.sql`
   - Purpose: Provide a table of compliance deadlines with urgency.
   - Notes: Deadline dates are synthetic offsets from the latest available date.

6. **Point-in-Time Portfolio Composition**
   - File: `day17/queries/day17_QUERY_point_in_time.sql`
   - Purpose: Reconstruct the portfolio as of a specific date.
   - Param: `:as_of_date` (YYYY-MM-DD)

## Synthetic Logic Used

- **Jurisdiction mapping:** Derived from `dim_clients.client_type` with asset_class overrides for `Certification` (EU) and `IP` (UK).
- **SCD timeline:** Synthetic history created for Equipment/IP/Certification assets using a change date 60 days before the latest holdings date.
- **Compliance status:** Derived from `asset_key % 3` to create deterministic categories.
- **Deadline dates:** Derived from the latest date with fixed offsets (-15, +45, +180 days).

These rules are documented so the dashboard stays reproducible and explainable.
