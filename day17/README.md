# Day 17: Rafael - Multi-Jurisdictional Asset Compliance Dashboard

**Industry:** Wealth Management / Legal Compliance
**Stakeholder:** Rafael (Cross-Border Wealth Planning Attorney)
**Built with:** Streamlit + Plotly
**Time to deliver:** 3 hours

---

## Decision Context (CRITICAL SECTION)

### WHO is making a decision?
Rafael, a cross-border wealth planning attorney responsible for audit readiness and regulatory compliance.

### WHAT decision are they making?
Which assets require regulatory attention THIS QUARTER based on classification changes, jurisdictional compliance status, and upcoming audit dates.

### WHAT minimum visual supports this decision?
A timeline of asset classification changes (SCD Type 2) plus a compliance status table filtered by jurisdiction and asset class.

### Why THIS visualization (not others)?
The timeline exposes when asset classifications change (audit trail), while the compliance table prioritizes assets by jurisdiction and urgency. A static snapshot would hide historical transitions that are legally relevant.

---

## Business Problem
Rafael needs a fast, audit-ready view of portfolio changes across jurisdictions. He must identify assets with recent classification changes or upcoming compliance deadlines to prioritize legal reviews this quarter.

---

## Solution Delivered

### Visualizations:
1. **Portfolio Overview Metrics**: Quick snapshot of asset counts and market value.
2. **SCD Type 2 Timeline (Primary)**: Asset classification changes over time.
3. **Changes This Quarter**: Table of assets with new versions in the current quarter.
4. **Compliance Status by Jurisdiction**: Grouped bar chart of current/expiring/expired assets.
5. **High-Risk Assets**: Table filtered to assets needing attention.
6. **Upcoming Deadlines**: Sorted table by urgency.
7. **Point-in-Time Query**: Reconstruct portfolio composition as of a selected date.

### Data Source:
- **Model:** Day 10 Family Office DW (`dim_assets`, `fct_holdings`, `dim_clients`, `dim_date`)
- **Refresh:** Manual (re-run app to refresh)
- **Volume:** Asset and holdings records from Day 10 synthetic DW

---

## Key Insights (from synthetic logic)
- Jurisdictions show different compliance urgency profiles due to derived status rules.
- Equipment and certification assets drive most near-term deadlines.
- SCD timeline highlights assets with multiple classification changes in the quarter.

---

## How to Run Locally

### Prerequisites:
- Python 3.9+

### Setup:
```bash
# 1. Configure environment variables
cp .env.example .env
# Edit .env with your paths

# 2. Install dependencies
pip install -r day17_requirements.txt

# 3. Run visualization
streamlit run day17_VIZ_legal_analytics_dashboard.py
```

### Expected Output:
A Streamlit dashboard with the SCD timeline, compliance status chart, and point-in-time query table.

---

## Architecture Decisions

### Decision 1: Why Streamlit over Metabase/Power BI?
Streamlit enables fast Python-native development with custom timeline visuals and point-in-time query input in under 3 hours.

### Decision 2: Why these 7 visuals (not 10)?
Each visual directly supports audit readiness or compliance prioritization. Additional charts would not change the decision.

### Decision 3: How are jurisdiction and compliance derived?
The Day 10 model does not include jurisdiction, compliance, or multi-version SCD history. For reproducibility, this dashboard derives jurisdiction from `client_type` with asset_class overrides, derives compliance status deterministically, and generates a synthetic SCD change date 60 days before the latest holdings date (documented in `day17/day17_QUERIES_legal_analytics.md`).

---

## Limitations & Future Enhancements

**Current Limitations:**
- Jurisdiction and compliance status are derived (not sourced from real compliance data).
- Manual refresh (no scheduled updates).
- Single-user view (no role-based access).

**Possible Enhancements (out of 3h scope):**
- [ ] Replace synthetic compliance fields with real regulatory data
- [ ] Automated refresh with scheduled job
- [ ] Jurisdiction-specific rule overlays

---

## Portfolio Notes

**Demonstrates:**
- Decision-first legal analytics framing
- SCD Type 2 audit-trail visualization
- SQL-driven reproducibility

**Upwork Keywords:** legal analytics, compliance dashboard, Streamlit, SCD Type 2, audit readiness

---

Built as part of Christmas Data Advent 2025 - Visualization Week (Days 16-20)
