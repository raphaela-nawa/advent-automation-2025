# Delivery Criteria - Data Visualization Projects (Days 16-20)
Christmas Data Advent 2025 - Visualization Week

**Purpose:** Define success criteria, anti-patterns, and delivery standards for data visualization projects focusing on decision-support analytics over aesthetic polish.

**Time Constraint:** 3 hours per project
**Core Principles:** Analytical clarity, data-to-decision flow, minimalism, technical ownership

---

## 📊 STRATEGIC DECISION: "DATA VISUALIZATION" NOT "DASHBOARD"

### Why This Naming Matters

**"Dashboard" implies:**
- Visual polish and design aesthetics
- UI/UX perfection
- Interactive features and animations
- Stakeholder presentation layer
- Time spent on colors, layouts, branding

**"Data Visualization" emphasizes:**
- **Analytical thinking first** - What decision does this support?
- **Data-to-insight flow** - Model → Transform → Visualize → Decide
- **Minimum viable visual** - Simplest chart that answers the question
- **Technical ownership** - You own the data pipeline AND the viz
- **Speed over perfection** - 3 hours = function beats form

### The Renaming Philosophy

> **"If the chart doesn't support a specific decision, it doesn't belong in the visualization."**

This pillar trains you to think like an analyst, not a designer:
- Start with the decision/question
- Work backwards to the minimum data needed
- Choose the simplest chart type that works
- Only add interactivity if it changes the decision

**Portfolio Positioning:** "Data Visualization" signals analytical rigor. "Dashboard" signals design skills. For data roles, analytical thinking > pretty charts.

---

## 📋 PROJECT-LEVEL PRINCIPLE

### Every Visualization Must Answer Three Questions:

1. **WHO is making a decision?** (Specific stakeholder, not "management")
2. **WHAT decision are they making?** (Specific action, not "monitoring")
3. **WHAT is the MINIMUM visual that supports this decision?** (Bar chart? Line chart? Table?)

### Example Application:

❌ **Bad Framing:** "Build a sales dashboard for the team"
✅ **Good Framing:** "Help [Sales Manager Maria] decide [which underperforming reps need coaching this week] using [a single table: rep name, quota gap %, trend arrow]"

❌ **Bad Framing:** "Visualize customer data"
✅ **Good Framing:** "Help [CS Lead John] identify [which accounts to prioritize for upsell calls today] using [a scatter plot: ARR vs health score, colored by contract renewal date]"

### The Exclusion Principle

**If you can't articulate the specific decision a chart supports, DELETE IT.**

Common violations:
- "Vanity metrics" that look impressive but drive no action
- Multiple ways to show the same insight (pick ONE)
- Charts added "for completeness" without decision context
- Interactive filters that don't change the decision outcome

---

## ⏱️ TIME MANAGEMENT (3 hours)

### Ideal Distribution:

| Phase | Time | What to Do |
|-------|------|------------|
| **Decision Framing** | 15 min | Define WHO, WHAT decision, WHAT minimum visual |
| **Data Prep** | 45 min | Query data from models (Day 6-10), validate, export |
| **Visualization Build** | 90 min | Create charts, add minimal interactivity |
| **Documentation** | 30 min | README with decision context, screenshots |

### 🚨 SIGNS YOU'RE DEVIATING FROM SCOPE:

- Spending >15 min on color schemes
- Building custom CSS/styling
- Adding 5+ chart types "to show flexibility"
- Implementing complex filtering logic
- Trying to make it "look like Tableau"
- Adding features the stakeholder didn't ask for

**If this happens:** STOP. Return to the three questions (WHO, WHAT decision, WHAT minimum visual). Deliver the promised minimum first.

---

## 📋 DECISION MATRIX

### ✅ MANDATORY OUTPUT (You MUST deliver this)

| Item | Description | Location |
|------|-------------|----------|
| **Visualization file(s)** | `.py` (Streamlit/Plotly), `.pbix` (Power BI), `.html` (static charts) | `/dayXX/` |
| **Decision context doc** | WHO, WHAT decision, WHAT visual - answers the three questions | `/dayXX/README.md` or `/dayXX/docs/` |
| **Data source connection** | Queries connecting to Day 6-10 models OR synthetic data | `/dayXX/queries/` or embedded in code |
| **Screenshots** | Evidence of working visualization | `/dayXX/screenshots/` |
| **Reproducible config** | `.env.example` with day-specific variables | `/dayXX/.env.example` |
| **Dependencies** | Day-specific requirements (if needed) | `/dayXX/dayXX_requirements.txt` |
| **Minimal documentation** | README with Quick Start | `/dayXX/README.md` |

### ❌ FORBIDDEN OUTPUT (DON'T do this - will exceed 3h)

| Item | Why NOT |
|------|---------|
| **Custom UI frameworks** | Use Streamlit/Plotly/native tools - no React/Vue/Angular |
| **Authentication systems** | No login pages - assume internal tool |
| **Database writes** | Read-only visualizations - no "update data" features |
| **Real-time streaming** | Batch data refresh is fine - no WebSockets |
| **Mobile responsiveness** | Desktop-first is fine - no mobile optimization |
| **Advanced animations** | Static or simple transitions only |
| **AI/ML predictions** | Show existing model outputs - don't build new models |
| **Complex drill-downs** | 1-2 levels max - not a full BI tool |

---

## ✅ COMPLETE PROJECT CHECKLIST

### **BEFORE considering the project complete, verify:**

#### **1. Decision Clarity**
- [ ] README explicitly states WHO is making a decision
- [ ] README explicitly states WHAT decision they're making
- [ ] README explicitly states WHY this visualization (not others) supports the decision
- [ ] Every chart in the visualization has a clear decision purpose (no "nice to have" charts)

#### **2. Core Functionality**
- [ ] Visualization loads without errors
- [ ] Data displays correctly (no empty charts, broken queries)
- [ ] Charts are readable (labels, titles, axes clear)
- [ ] Insights are obvious within 10 seconds of viewing

#### **3. Data Pipeline**
- [ ] Connects to existing models (Day 6-10) OR uses synthetic data
- [ ] Queries documented (SQL files or code comments)
- [ ] Data refresh process explained (manual? scheduled? on-demand?)

#### **4. Reproducibility** (following PROMPT_project_setup.md rules)
- [ ] `.env.example` lists ALL necessary variables (format: `DAYXX_DB_PATH`, `DAYXX_SPECIFIC_VAR`)
- [ ] Variables added to root `config/.env` following existing convention
- [ ] `dayXX_requirements.txt` has specific dependencies (if needed)
- [ ] README has "Quick Start" section that works copy-paste

#### **5. Minimum Quality**
- [ ] Charts have titles and axis labels
- [ ] Data values are formatted appropriately (%, $, K/M notation)
- [ ] Color choices are colorblind-safe (or monochrome)
- [ ] Screenshots show full context (not cropped mid-chart)

#### **6. Naming Convention (CRITICAL)**
- [ ] All files have `dayXX_` prefix
- [ ] Global variables have `dayXX_` or `DAYXX_` prefix
- [ ] Classes have `dayXX_` prefix
- [ ] Main functions have `dayXX_` prefix

#### **7. Delivery**
- [ ] Git commit with descriptive message
- [ ] Push to GitHub
- [ ] Screenshots committed to repo

#### **8. Final Test (5 minutes)**
- [ ] Clone repo in another folder
- [ ] Run commands from README
- [ ] Works? ✅ Project complete. Doesn't work? ❌ Debug and fix.

---

## 🎯 TECHNICAL REQUIREMENTS

### Allowed Tools (Pick ONE per project)

| Tool | Use Case | Learning Curve | Portfolio Value |
|------|----------|----------------|-----------------|
| **Metabase** | SQL-first BI, open-source | Low | High (modern analytics teams) |
| **Streamlit** | Python-native, fast prototyping | Low | High (popular in data teams) |
| **Plotly (Python)** | Interactive charts, Dash apps | Medium | High (industry standard) |
| **Plotly (JS/HTML)** | Standalone HTML dashboards | Medium | Medium (web skills) |
| **Matplotlib/Seaborn** | Static charts, reports | Low | Medium (analysis-focused) |
| **Power BI** | Enterprise dashboards | Medium | High (enterprise demand) |
| **Looker Studio** | Google ecosystem | Low | Medium (startups/SMB) |
| **Tableau Public** | Visual storytelling | Medium | High (analyst roles) |

**Decision Guide:**
- **Stakeholder is technical (engineer/analyst)?** → Metabase (SQL-first) or Streamlit (Python-native)
- **Stakeholder is non-technical (executive/manager)?** → Power BI or Looker Studio
- **Portfolio focus (Upwork/LinkedIn)?** → Metabase (modern BI) or Power BI (enterprise demand)
- **Time constraint (<3h)?** → Metabase (SQL queries auto-viz) or Streamlit (fastest Python option)
- **SQL-first workflow preference?** → Metabase (designed for this)

### Data Source Requirements

**Option 1: Connect to Existing Models (PREFERRED)**
- Query Day 6-10 modeling projects (SQLite databases, dbt models)
- Reuse analytical views (e.g., Day 6 SaaS metrics, Day 10 family office assets)
- Document connection in README: "Consumes data from Day X model"

**Option 2: Synthetic Data (If no model exists)**
- Generate synthetic data that mirrors real-world structure
- Document assumptions: "Simulates [business context] with [N] records"
- Keep data generation script: `dayXX_DATA_synthetic.py`

**❌ DO NOT:**
- Call live APIs during visualization rendering (pre-fetch and cache)
- Use real customer data (privacy risk)
- Fetch data on every page load (cache or pre-process)

### Delivery Format Requirements

**Minimum Viable Delivery:**
- [ ] 2-4 visualizations (charts/tables) - OR 4-6 cards if using Metabase (see Day 16)
- [ ] Clear titles and labels on all visuals
- [ ] Decision context documented
- [ ] Screenshot showing full layout

**Metabase-Specific Requirements (Day 16):**
- [ ] Dashboard JSON export file
- [ ] SQL queries documented in separate markdown file
- [ ] All cards use native SQL queries (not GUI query builder)

**Stretch Goals (if time permits):**
- [ ] 1-2 basic filters (date range, category selector)
- [ ] Download data as CSV button
- [ ] Simple drill-down (click chart to see details)

**What NOT to build:**
- ❌ Complex navigation (multiple pages)
- ❌ User management (login/roles)
- ❌ Data editing features
- ❌ Real-time updates
- ❌ Mobile-specific layouts

---

## 🎯 SUCCESS CRITERIA

### Technical Success:
- ✅ Visualization loads in <5 seconds
- ✅ Charts render correctly (no broken visuals)
- ✅ Data values match source queries
- ✅ Can be run locally by following README

### Analytical Success:
- ✅ Decision context is crystal clear (WHO, WHAT decision, WHAT visual)
- ✅ Charts answer the stated question
- ✅ Insights are obvious within 10 seconds
- ✅ No "decorative" charts - every visual has purpose

### Portfolio Success:
- ✅ Non-technical person understands the business value from README
- ✅ Screenshots show professional (not perfect) quality
- ✅ Demonstrates analytical thinking (decision-first approach)
- ✅ Upwork positioning clear: "Built X visualization to support Y decision"

---

## ❌ ANTI-PATTERNS TO AVOID

### Anti-Pattern 1: "Kitchen Sink Dashboard"
**Problem:** Adding every possible chart "to show capability"
**Solution:** Ruthlessly cut charts that don't support the stated decision
**Example:** If decision is "prioritize leads", only show lead scoring/prioritization visuals - remove generic "total leads over time" vanity metrics

### Anti-Pattern 2: "Designer Mode"
**Problem:** Spending >30min on colors, fonts, layouts
**Solution:** Use tool defaults. Focus time on data accuracy and insight clarity
**Example:** Streamlit default theme is fine. Don't build custom CSS.

### Anti-Pattern 3: "Feature Creep"
**Problem:** "Wouldn't it be cool if..." syndrome
**Solution:** Stick to the three questions. Only build what supports the decision.
**Example:** Stakeholder needs "top 10 products by margin" → Don't add "product category breakdown" unless it changes the decision

### Anti-Pattern 4: "Interactivity Obsession"
**Problem:** Adding filters/dropdowns that don't change the decision
**Solution:** Only add interactivity if stakeholder uses different parameters for the same decision
**Example:** Sales rep performance viz → Date range filter is useful. "Filter by rep shoe size" is not.

### Anti-Pattern 5: "Static Image Export"
**Problem:** Taking a screenshot instead of building reproducible viz
**Solution:** Code-based visualization that can refresh with new data
**Example:** Don't export PNG from Excel. Build Streamlit app that queries live DB.

### Anti-Pattern 6: "The Silent Chart"
**Problem:** Chart with no title, no labels, no context
**Solution:** Every chart needs: title (what), axis labels (units), annotation (insight)
**Example:** ❌ Bar chart with numbers. ✅ "Top 5 Products by Margin ($K) - Q1 2025"

---

## 🎯 QUALITY THRESHOLDS

### Minimum Standards (Must Meet)

**Data Accuracy:**
- [ ] Query results match source data (spot-check 5+ records)
- [ ] Aggregations are correct (SUM, AVG, COUNT logic validated)
- [ ] Filters work as expected (date ranges, categories)
- [ ] No "NaN", "null", "undefined" showing in charts

**Visual Clarity:**
- [ ] Chart titles describe what the chart shows
- [ ] Axis labels include units (%, $, K, M)
- [ ] Legend is present when multiple series shown
- [ ] Colors distinguish categories clearly (no red-green for colorblind)

**Decision Support:**
- [ ] Answer to decision question is obvious in <10 seconds
- [ ] Stakeholder can take action without additional analysis
- [ ] Thresholds/benchmarks shown where relevant (goals, targets, averages)
- [ ] Trend direction is clear (up/down, good/bad)

### Disqualifying Defects (Must Fix)

**❌ Showstoppers:**
- Visualization doesn't load (crashes, errors)
- Charts are empty or show wrong data
- Decision context is missing or unclear
- README Quick Start doesn't work
- Cannot reproduce locally

**❌ Major Issues:**
- Chart type doesn't match data (pie chart for time series)
- Missing axis labels or titles
- Data formatting issues (e.g., showing 0.157 instead of 15.7%)
- Broken filters/interactivity

---

## 📖 DOCUMENTATION REQUIREMENTS

### README Structure (Day XX)

```markdown
# Day XX: [Stakeholder Name] - [Decision Context]

**Industry:** [e.g., SaaS, Manufacturing, Finance]
**Stakeholder:** [Name] ([Role]) - [Context from persona]
**Built with:** [Tool: Streamlit/Plotly/Power BI/etc]
**Time to deliver:** 3 hours

---

## Decision Context (CRITICAL SECTION)

### WHO is making a decision?
[Specific person and role: e.g., "Sarah, VP of Sales"]

### WHAT decision are they making?
[Specific action: e.g., "Which 10 sales reps to assign to high-value accounts this quarter"]

### WHAT minimum visual supports this decision?
[Chart type and rationale: e.g., "Scatter plot: Rep win rate (x-axis) vs deal size (y-axis), colored by tenure. Helps identify high performers who can handle large deals."]

### Why THIS visualization (not others)?
[Justification: e.g., "Scatter plot reveals non-obvious patterns - tenure alone doesn't predict success. Some new reps have high win rates on large deals. Table would miss this insight."]

---

## Business Problem

[Paragraph describing stakeholder pain point]

---

## Solution Delivered

### Visualizations:
1. **[Chart Name]**: [What decision it supports]
2. **[Chart Name]**: [What decision it supports]
3. **[Chart Name]**: [What decision it supports]

### Data Source:
- **Model:** [Day X project OR "Synthetic data simulating Y"]
- **Refresh:** [Manual/Daily/On-demand]
- **Volume:** [N records, M dimensions]

---

## Key Insights (From Synthetic Data)

[3-5 bullet points showing insights visible in the visualization]
- Insight 1 → Decision implication
- Insight 2 → Decision implication
- Insight 3 → Decision implication

---

## How to Run Locally

### Prerequisites:
- Python 3.9+ (if Streamlit/Plotly)
- [Tool-specific requirements]

### Setup:
```bash
# 1. Configure environment variables
cp .env.example .env
# Edit .env with your paths

# 2. Install dependencies
pip install -r dayXX_requirements.txt

# 3. Run visualization
streamlit run dayXX_VIZ_main.py
# OR
python dayXX_VIZ_main.py
```

### Expected Output:
[Screenshot or description of what user should see]

---

## Architecture Decisions

### Decision 1: Why [Tool X] over [Tool Y]?
[Rationale based on stakeholder, data volume, time constraint]

### Decision 2: Why these 3 charts (not 10)?
[Decision-driven chart selection - removed charts that didn't support decision]

### Decision 3: [Tool-specific decision]
[e.g., Why Streamlit's native caching over custom solution?]

---

## Limitations & Future Enhancements

**Current Limitations:**
- [e.g., Manual data refresh - stakeholder must re-run script]
- [e.g., Desktop-only layout - no mobile optimization]
- [e.g., 3-month date range - older data not shown]

**Possible Enhancements (out of 3h scope):**
- [ ] Automated daily refresh via GitHub Actions
- [ ] Email alerts when thresholds breached
- [ ] Export to PDF for stakeholder meetings
- [ ] Drill-down to individual record details

---

## Portfolio Notes

**Demonstrates:**
- Data-to-decision thinking (analytical framing)
- [Tool] proficiency (interactive visualizations)
- Data pipeline ownership (model → query → viz)
- Decision-driven design (minimal effective visual)

**Upwork Keywords:** [Tool] visualization, decision support analytics, [industry] dashboards, data storytelling

---

## Files Structure

```
dayXX/
├── dayXX_VIZ_main.py (or .pbix, .html)
├── dayXX_CONFIG_settings.py
├── queries/
│   └── dayXX_QUERY_data_source.sql
├── data/ (if using synthetic data)
│   └── dayXX_synthetic_data.csv
├── screenshots/
│   ├── dayXX_full_viz.png
│   └── dayXX_detail_view.png
├── dayXX_requirements.txt
├── .env.example
└── README.md
```

---

Built as part of Christmas Data Advent 2025 - Visualization Week (Days 16-20)
```

---

## 🎯 PROJECT-SPECIFIC CRITERIA

### **Day 16 - Murilo (SaaS Health Metrics Dashboard - Metabase)**

**Stakeholder:** Murilo (SaaS Founder - Simetryk)
**Project:** SaaS Health Metrics Dashboard
**Tool:** Metabase
**Data Source:** Day 6 (SaaS health metrics - MRR, churn, retention)

#### Why Metabase for Day 16

Metabase is used as the visualization layer because:
* **It is SQL-first** - Queries are explicit and version-controllable
* **It minimizes manual design decisions** - Default styling is production-ready
* **It is widely recognized in modern analytics teams** - Portfolio signal for BI engineering roles
* **It allows fast iteration without sacrificing rigor** - 3-hour constraint demands speed

**Critical Philosophy:**
> Metabase is treated as **a rendering and exploration layer, not a product UI.**

This means:
- No custom colors or branding
- No complex calculated fields in UI (do it in SQL)
- No embedded explanations (dashboard is self-explanatory or it's wrong)
- Default styling is used throughout

#### Decision Context

- **WHO:** Murilo, SaaS founder managing subscription business (technical background, reviews metrics weekly)
- **WHAT decision:** Which customer cohorts show declining retention and need proactive intervention THIS MONTH to prevent churn acceleration
- **WHAT visual:** Line chart showing cohort retention curves (x-axis: months since signup, y-axis: retention %, series: one line per signup cohort month)

**Why THIS visualization:**
- Shows WHEN customers churn (month 3 vs month 12 = different problems)
- Enables comparison across cohorts (product changes, marketing channel shifts)
- Matches Murilo's mental model (thinks in "signup cohorts" from Stripe dashboard)

**Rejected alternatives:**
- ❌ Single churn % metric - Hides cohort-level variation
- ❌ Table of raw numbers - 24 cohorts × 24 months = 576 data points, pattern recognition requires visual
- ❌ Pie chart of segments - Static snapshot doesn't show trend degradation

#### Dashboard Structure (4-Section Framework)

**Section 1 - Context: Business Health Baseline**
- Card: Executive KPI metrics (4 cards: MRR, Churn Rate %, Active Customers, LTV/CAC)
- SQL Source: `SELECT * FROM day06_dashboard_kpis`
- Filter: Time range selector (Last 30d, 90d, 12m, All time)

**Section 2 - Change & Trends: Growth Trajectory**
- Card: MRR Growth Over Time (stacked area chart - new, expansion, contraction, churn with cumulative line overlay)
- Card: Month-over-Month Growth Rate (line chart with 0% reference line)
- SQL Source: `day06_mrr_summary`

**Section 3 - Drivers: Cohort Patterns (PRIMARY DECISION VISUAL)**
- Card: Cohort Retention Curves (line chart, multi-series, 12-month focus)
  - SQL: `SELECT * FROM day06_retention_curves WHERE months_since_signup <= 12`
  - X-axis: Months since signup, Y-axis: Retention %, Series: cohort_month
  - Reference line: 50% retention (SaaS benchmark)
- Card: Churn Heatmap by Cohort × Plan Tier (pivot table with color gradient)
  - SQL: `SELECT * FROM day06_churn_by_cohort`

**Section 4 - Risk: Customer Health Alerts**
- Card: At-Risk Customer Distribution (pie chart: Healthy/At Risk/Critical)
- Card: Top 10 Critical Customers (table sorted by LTV/CAC ratio)
- SQL Source: `day06_customer_health`

#### Mandatory Output

**Dashboard Completeness:**
- [ ] 6 cards minimum (all 4 sections covered)
- [ ] Cohort retention curves visible (PRIMARY decision visual present)
- [ ] MRR waterfall shows 4 components (New, Expansion, Contraction, Churn)
- [ ] At-risk customer identification present
- [ ] Each card answers distinct question (no duplicate insights)

**Technical Quality:**
- [ ] All cards use SQL native queries (not GUI query builder)
- [ ] SQL queries documented in `day16_QUERIES_metabase.md`
- [ ] Time range filter works across all relevant cards
- [ ] Dashboard loads in <5 seconds

**Data Accuracy:**
- [ ] Retention curves start at 100% for month 0
- [ ] MRR waterfall balances: New + Expansion - Contraction - Churn = Net MRR
- [ ] Churn rates match Day 6 validation queries (spot-check 3 cohorts)

**Documentation:**
- [ ] Screenshot of complete dashboard: `day16/screenshots/day16_full_dashboard.png`
- [ ] Individual card screenshots (6 files)
- [ ] Metabase dashboard JSON export: `day16/day16_metabase_dashboard.json`
- [ ] README documents connection to Day 6: "Consumes 4 views from Day 6 SaaS metrics model"

#### When to Stop

**Success Criteria:**
- ✅ Dashboard has 6 cards covering all 4 sections
- ✅ Cohort retention curves show degradation (lines slope downward from 100%)
- ✅ MRR waterfall correctly shows: New + Expansion - Contraction - Churn = Net MRR
- ✅ Churn heatmap reveals plan tier + cohort risk patterns
- ✅ Time range filter updates all time-series cards
- ✅ README explains: "Helps Murilo identify which customer cohorts show declining retention and need proactive intervention this month"
- ✅ Connection to Day 6 documented
- ✅ SQL queries are clean, readable, documented

**Scope Creep to AVOID:**
- ❌ Churn prediction model (ML) - Just show historical retention
- ❌ Stripe integration - Use Day 6 synthetic data only
- ❌ Automated email alerts - Static dashboard, no alerting
- ❌ Custom CSS/styling - Metabase defaults only
- ❌ Multi-page dashboard - Single page, 6 cards maximum
- ❌ Real-time API calls - Query static SQLite database

#### Expected Files

```
day16/
├── README.md                               # Decision context, setup instructions
├── day16_metabase_dashboard.json           # Metabase dashboard export
├── day16_QUERIES_metabase.md               # All SQL queries documented
├── screenshots/
│   ├── day16_full_dashboard.png            # Complete dashboard
│   ├── day16_card_1_kpis.png               # Executive metrics
│   ├── day16_card_2_mrr_trend.png          # MRR growth
│   ├── day16_card_3_growth_rate.png        # MoM growth rate
│   ├── day16_card_4_retention_curves.png   # Cohort retention (PRIMARY)
│   ├── day16_card_5_churn_heatmap.png      # Churn by segment
│   └── day16_card_6_health_alerts.png      # At-risk customers
├── day16_CONFIG_metabase.md                # Metabase connection guide
└── .env.example                            # Environment variables (if needed)
```

#### Setup & Installation

```bash
# Option 1: Docker (recommended)
docker run -d -p 3000:3000 --name metabase metabase/metabase

# Option 2: Java JAR
java -jar metabase.jar

# Access: http://localhost:3000
# First-time setup: Create admin account, add SQLite database
# Database path: ../day06/data/day06_saas_metrics.db
# Import dashboard: Upload day16_metabase_dashboard.json
```

#### AI Readiness (Future Pillar Alignment)

This Metabase dashboard is **AI-readable by design**:

**Each chart:**
* Backed by clean SQL query (not GUI-generated)
* Returns interpretable aggregates (cohort_month, retention_rate_pct)
* Can be summarized programmatically

**Future AI layer can:**
* Generate textual summaries - "MRR grew 12% MoM, driven by $8K expansion"
* Highlight changes - "Feb 2024 cohort has 22% churn vs 15% average"
* Explain drivers - "Starter tier = 60% of churn but only 40% of MRR"

**Architectural separation:**
- Visualization layer (Metabase) is "dumb" on purpose
- All intelligence lives in SQL queries and Day 6 data model
- AI can read SQL directly, not reverse-engineer dashboard config

#### 3-Hour Timeline

**Hour 1: Setup & First Visuals (60 min)**
- 0:00-0:15 - Install Metabase, connect to Day 6 database
- 0:15-0:30 - Section 1: Executive KPIs (4 metric cards)
- 0:30-1:00 - Section 2: MRR trends (stacked area + growth rate)

**Hour 2: Core Decision Visual (60 min)**
- 1:00-1:30 - Section 3: Cohort retention curves (PRIMARY VISUAL)
- 1:30-2:00 - Section 3: Churn heatmap (cohort × plan tier)

**Hour 3: Risk Alerts & Documentation (60 min)**
- 2:00-2:30 - Section 4: Customer health (pie chart + critical table)
- 2:30-2:50 - Dashboard assembly, filter testing, validation
- 2:50-3:00 - Export JSON, SQL queries, screenshots, README

**3:00 - HARD STOP**

#### Naming Examples

```python
# ✅ CORRECT
DAY16_DB_PATH = "../day06/data/day06_saas_metrics.db"
DAY16_METABASE_PORT = 3000

# Environment variables
DAY16_METABASE_DASHBOARD_ID = "saas-health-metrics"

# ❌ WRONG
DB_PATH = "database.db"  # Too generic
METABASE_PORT = 3000  # No prefix
```

---

### **Day 17 - Rafael (Legal Analytics Dashboard - Asset Compliance Tracking)**

**Stakeholder:** Rafael (Cross-Border Wealth Planning Attorney)
**Project:** Multi-Jurisdictional Asset Compliance Dashboard
**Tool:** Streamlit or Plotly
**Data Source:** Day 10 (Family Office Asset Management DW - MFG operational assets + SCD Type 2 tracking)

#### Decision Context

- **WHO:** Rafael, cross-border wealth planning attorney managing UHNW family portfolios across multiple jurisdictions
- **WHAT decision:** Which assets require regulatory attention THIS QUARTER based on classification changes, jurisdictional compliance status, and upcoming audit dates
- **WHAT visual:** Timeline view showing asset classification changes (SCD Type 2 history) + compliance status table filtered by jurisdiction and asset class

**Why THIS visualization:**
- Shows WHEN asset classifications changed (equipment lifecycle, regulatory updates) - critical for audit trails
- Enables jurisdictional filtering (EU assets have different compliance requirements than US assets)
- Surfaces upcoming compliance deadlines (certifications expiring, regulatory reviews due)

**Rejected alternatives:**
- ❌ Static portfolio snapshot - Loses historical audit trail (SCD Type 2 value)
- ❌ Simple asset list - Doesn't show compliance timeline or urgency
- ❌ Generic BI dashboard - Legal analytics require jurisdiction-specific views

#### Dashboard Structure (4-Section Framework)

**Section 1 - Context: Portfolio Overview**
- Card: Portfolio summary metrics (Total Assets, Assets by Jurisdiction, Assets by Class)
- SQL Source: `SELECT COUNT(*), SUM(market_value) FROM fct_holdings JOIN dim_assets`
- Filter: Jurisdiction selector (US, EU, UK, etc.), Asset class filter (Equipment, IP, Certification, Equity)

**Section 2 - Change & Trends: Historical Tracking (PRIMARY DECISION VISUAL)**
- Card: Asset Classification Timeline (SCD Type 2 visualization)
  - Timeline showing asset_id changes over time (valid_from → valid_to)
  - Color-coded by asset_class transition (Active → Maintenance → Disposed)
  - Interactive: Click asset to see full history
- Card: Classification Changes This Quarter (table)
  - SQL: `SELECT * FROM dim_assets WHERE valid_from >= QUARTER_START`

**Section 3 - Drivers: Compliance Status**
- Card: Compliance Status by Jurisdiction (grouped bar chart)
  - X-axis: Jurisdiction (US, EU, UK)
  - Y-axis: Asset count
  - Series: Compliance status (Current, Expiring <90d, Expired)
- Card: High-Risk Assets Table (MFG operational assets requiring attention)
  - Certifications expiring soon
  - Equipment under regulatory review
  - IP renewal deadlines approaching

**Section 4 - Risk: Audit Readiness**
- Card: Upcoming Compliance Deadlines (sorted by urgency)
  - Next 30 days (Critical - red)
  - 30-90 days (Warning - yellow)
  - >90 days (OK - green)
- Card: Point-in-Time Query Interface
  - User input: Date picker ("Show portfolio as of [date]")
  - Output: Asset composition on that historical date (demonstrates SCD Type 2 value)

#### Mandatory Output

**Dashboard Completeness:**
- [ ] 6-8 visualizations covering all 4 sections
- [ ] SCD Type 2 timeline visible (showing asset classification changes over time)
- [ ] Jurisdiction filter works across all cards
- [ ] Point-in-time query demonstrates historical audit capability
- [ ] MFG operational assets clearly identified (Equipment, IP, Certification from Day 10)

**Technical Quality:**
- [ ] Connects to Day 10 SQLite database (`day10_family_office_dw.db`)
- [ ] SQL queries documented in `day17_QUERIES_legal_analytics.md`
- [ ] Jurisdiction filter updates all relevant visuals
- [ ] Dashboard loads in <5 seconds

**Data Accuracy:**
- [ ] SCD Type 2 history accurately displays valid_from/valid_to transitions
- [ ] Portfolio value matches Day 10 validation queries
- [ ] Asset counts by jurisdiction sum to total assets
- [ ] Point-in-time query returns correct historical state

**Documentation:**
- [ ] Screenshot of complete dashboard: `day17/screenshots/day17_full_dashboard.png`
- [ ] Individual screenshots of SCD Type 2 timeline and compliance table
- [ ] README documents connection to Day 10: "Consumes dim_assets (SCD Type 2) and fct_holdings from Day 10 Family Office DW"
- [ ] README explains legal context: "Helps Rafael track asset classification changes for regulatory compliance and audit readiness"

#### When to Stop

**Success Criteria:**
- ✅ Dashboard has 6-8 cards covering all 4 sections
- ✅ SCD Type 2 timeline shows asset classification changes (e.g., EQ_MFG_001: Active → Maintenance → Active)
- ✅ Jurisdiction filter updates all visuals (test: switch from "All" to "EU only")
- ✅ Point-in-time query works: "Show portfolio as of 2024-06-15" returns historical asset state
- ✅ MFG operational assets visible (30 assets: Equipment, IP, Certification)
- ✅ Compliance deadline table sorted by urgency (Critical <30d shown first)
- ✅ README explains: "Helps Rafael track multi-jurisdictional asset compliance and audit readiness using SCD Type 2 historical tracking"
- ✅ Connection to Day 10 documented

**Scope Creep to AVOID:**
- ❌ Real legal document generation - Just show compliance data
- ❌ Automated regulatory filing - Dashboard displays info only
- ❌ Multi-currency conversion - Use Day 10 values as-is
- ❌ Custom legal templates - Focus on data visualization
- ❌ User authentication/roles - Single-user dashboard (Rafael)
- ❌ Email alerts for deadlines - Static dashboard only

#### Expected Files

```
day17/
├── README.md                                   # Decision context, legal analytics focus
├── day17_VIZ_legal_analytics_dashboard.py      # Streamlit or Plotly dashboard
├── day17_QUERIES_legal_analytics.md            # All SQL queries documented
├── queries/
│   ├── day17_QUERY_scd_timeline.sql            # SCD Type 2 historical changes
│   ├── day17_QUERY_compliance_by_jurisdiction.sql
│   ├── day17_QUERY_point_in_time.sql           # Historical portfolio state
│   └── day17_QUERY_upcoming_deadlines.sql
├── screenshots/
│   ├── day17_full_dashboard.png                # Complete dashboard
│   ├── day17_scd_timeline.png                  # Asset classification history
│   ├── day17_compliance_table.png              # Jurisdiction compliance view
│   └── day17_point_in_time_query.png           # Historical query demo
├── day17_CONFIG_settings.py
├── day17_requirements.txt
└── .env.example
```

#### Setup & Installation

```bash
# Install dependencies
pip install streamlit plotly pandas sqlite3

# Run dashboard
streamlit run day17_VIZ_legal_analytics_dashboard.py

# Access: http://localhost:8501
# Database connection: ../day10/data/day10_family_office_dw.db
```

#### Legal Analytics Philosophy

This dashboard is designed for **legal compliance analysis**, not generic BI:

**Key Differences from Business Dashboards:**
- **Audit trail emphasis** - SCD Type 2 timeline is PRIMARY visual (not vanity metric)
- **Jurisdictional context** - Every visual must support jurisdiction filtering (US, EU, UK compliance rules differ)
- **Point-in-time reconstruction** - "What was the portfolio on [historical date]?" is a core legal requirement
- **Deadline tracking** - Compliance deadlines are risk-weighted (30d vs 90d urgency)

**What Legal Analytics Requires:**
- Historical change tracking (SCD Type 2)
- Jurisdiction-aware filtering
- Audit-ready point-in-time queries
- Deadline/expiry urgency flagging

**What It Does NOT Need:**
- Real-time updates (quarterly compliance review is typical)
- Predictive analytics (legal compliance is fact-based, not probabilistic)
- Collaboration features (attorney reviews solo)

#### 3-Hour Timeline

**Hour 1: Setup & Context Visuals (60 min)**
- 0:00-0:15 - Connect to Day 10 database, validate data
- 0:15-0:30 - Section 1: Portfolio summary metrics (3 cards)
- 0:30-1:00 - Jurisdiction and asset class filters

**Hour 2: SCD Type 2 Timeline (PRIMARY VISUAL) (60 min)**
- 1:00-1:40 - Section 2: Build SCD Type 2 timeline visualization
  - Query: `SELECT * FROM dim_assets WHERE asset_id IN (SELECT DISTINCT asset_id FROM dim_assets GROUP BY asset_id HAVING COUNT(*) > 1)`
  - Visualize: Timeline with valid_from/valid_to ranges, color by asset_class
- 1:40-2:00 - Section 2: Classification changes table (this quarter)

**Hour 3: Compliance & Deadlines (60 min)**
- 2:00-2:30 - Section 3: Compliance status by jurisdiction (bar chart)
- 2:30-2:45 - Section 4: Upcoming deadlines table (sorted by urgency)
- 2:45-3:00 - Point-in-time query interface (date picker + results table)

**3:00 - HARD STOP**

#### Naming Examples

```python
# ✅ CORRECT
DAY17_DB_PATH = "../day10/data/day10_family_office_dw.db"
DAY17_JURISDICTIONS = ['US', 'EU', 'UK', 'APAC']
DAY17_DEADLINE_THRESHOLDS = {'critical': 30, 'warning': 90}

def day17_query_scd_timeline():
    """Fetch SCD Type 2 asset history for timeline visualization"""
    pass

class day17_LegalAnalyticsDashboard:
    pass

# ❌ WRONG
DB_PATH = "database.db"  # Too generic
JURISDICTIONS = ['US', 'EU']  # No prefix
```

#### Key SQL Queries

**SCD Type 2 Timeline Query:**
```sql
-- Show asset classification changes over time
SELECT
    asset_id,
    asset_name,
    asset_class,
    valid_from,
    valid_to,
    is_current,
    CASE
        WHEN is_current = TRUE THEN 'Current'
        ELSE 'Historical'
    END as version_status
FROM dim_assets
WHERE asset_id IN (
    -- Only show assets with multiple versions (SCD Type 2 examples)
    SELECT asset_id
    FROM dim_assets
    GROUP BY asset_id
    HAVING COUNT(*) > 1
)
ORDER BY asset_id, valid_from;
```

**Point-in-Time Query:**
```sql
-- "What was the portfolio composition on 2024-06-15?"
SELECT
    c.client_name,
    a.asset_class,
    COUNT(*) as asset_count,
    SUM(h.market_value) as total_value
FROM fct_holdings h
JOIN dim_assets a ON h.asset_key = a.asset_key
    AND '2024-06-15' BETWEEN a.valid_from AND COALESCE(a.valid_to, '9999-12-31')
JOIN dim_clients c ON h.client_key = c.client_key
JOIN dim_date d ON h.date_key = d.date_key
WHERE d.full_date = '2024-06-15'
GROUP BY c.client_name, a.asset_class
ORDER BY total_value DESC;
```

**Tool Recommendation:** Streamlit (fast, Python-native, good for legal data tables) or Plotly (interactive timeline visualizations)

---

### **Day 18 - Andrea (Transport Policy KPI Dashboard)**

**Stakeholder:** Andrea (Policy Analyst - Transport Regulation)
**Project:** Municipal Transport Regulation Tracker
**Data Source:** Day 14 (Querido Diário API - transport regulations)

**Decision Context:**
- **WHO:** Andrea, Policy Analyst monitoring municipal transport regulations
- **WHAT decision:** Which municipalities to prioritize for policy review THIS WEEK based on regulation activity
- **WHAT visual:** Heatmap: Municipalities (rows), Weeks (columns), Cell color = number of transport regulations published

**Mandatory Output:**
- [ ] **Primary Visual:** Heatmap showing regulation activity by municipality over time
- [ ] **Secondary Visual:** Bar chart: Top 10 municipalities by total regulation count
- [ ] **Metric Cards:** Total regulations, active municipalities, most active city
- [ ] **Filter:** Regulation type (trânsito, mobilidade, transporte, etc.)
- [ ] **Data Source:** Queries Day 14 cached API responses OR synthetic gazette data
- [ ] **Screenshot:** Evidence of working dashboard with heatmap

**When to Stop:**
- ✅ Heatmap shows last 12 weeks of data
- ✅ Color intensity indicates activity level
- ✅ Top 10 chart helps prioritize municipalities
- ✅ Regulation type filter works
- ✅ README explains: "Helps Andrea identify policy hotspots requiring review"
- ✅ Connection to Day 14 documented
- ❌ DON'T do: Real-time API calls, full-text search, NLP analysis, automated policy summaries

**Tool Recommendation:** Plotly (heatmaps) or Streamlit with Plotly Express

---

### **Day 20 - Carol (Hospitality LTV Dashboard)**

**Stakeholder:** Carol (Pousada Owner - Campos do Jordão)
**Project:** Guest Lifetime Value & Retention Dashboard
**Data Source:** Day 7 (Hospitality LTV & cohort model)

**Decision Context:**
- **WHO:** Carol, pousada owner managing guest relationships
- **WHAT decision:** Which guest cohorts to target with loyalty campaigns THIS QUARTER based on LTV potential
- **WHAT visual:** Scatter plot: Average LTV (x-axis) vs Return rate % (y-axis), one dot per cohort, sized by cohort size

**Mandatory Output:**
- [ ] **Primary Visual:** Scatter plot showing LTV vs Return rate by cohort
- [ ] **Secondary Visual:** Table: Top 20 guests by LTV with contact info (synthetic)
- [ ] **Metric Cards:** Average LTV, return guest rate, average booking value
- [ ] **Filter:** Booking season selector (Summer, Winter, All)
- [ ] **Data Source:** Queries Day 7 database OR synthetic hospitality data
- [ ] **Screenshot:** Evidence of working dashboard with scatter plot

**When to Stop:**
- ✅ Scatter plot reveals cohort segments (e.g., high LTV + low return = re-engagement target)
- ✅ Top guests table shows LTV ranking
- ✅ Season filter updates all visuals
- ✅ Metric cards calculate correctly
- ✅ README explains: "Helps Carol prioritize guest retention efforts by LTV segment"
- ✅ Connection to Day 7 documented (if using that data)
- ❌ DON'T do: Email integration, booking system, dynamic pricing, churn prediction

**Tool Recommendation:** Streamlit or Tableau Public (hospitality context benefits from visual storytelling)

---

## 🔄 PIVOT RULE (1 hour)

**For all Visualization projects:**

If after **1 hour** you still haven't:
- Loaded data successfully AND
- Created at least ONE working chart

➡️ **IMMEDIATE PIVOT to simpler approach:**

1. Use Matplotlib instead of interactive tools (static PNG is fine)
2. Use CSV files instead of database connections
3. Use 3 charts instead of 5
4. Use built-in tool themes (no custom styling)
5. Skip filters/interactivity (can document as "future enhancement")

**DON'T spend more than 1h fighting with tool setup. The goal is to deliver, not perfectionism.**

**Example Pivot Scenarios:**

**Day 16 (Power BI):**
```bash
# After 1h, if Power BI installation failing:

# BEFORE (complex):
# Installing Power BI Desktop, connecting to SQLite...

# AFTER (simple pivot):
# Export data to CSV from Day 10
# Use Streamlit with st.dataframe() and st.bar_chart()
# Document: "Prototyped in Streamlit, production would use Power BI"
```

**Day 17 (Looker Studio):**
```bash
# After 1h, if Looker Studio auth issues:

# BEFORE (complex):
# Fighting with Google OAuth, data source connectors...

# AFTER (simple pivot):
# Use Plotly to create standalone HTML dashboard
# Document: "Standalone version - production would use Looker Studio"
```

---

## 📊 VISUALIZATION BEST PRACTICES

### Chart Type Selection Guide

| Decision Type | Recommended Chart | Why |
|---------------|-------------------|-----|
| **Compare categories** | Bar chart (horizontal) | Easy to read labels, clear comparisons |
| **Show trends over time** | Line chart | Brain processes time left-to-right naturally |
| **Show parts of whole** | Stacked bar OR table | Pie charts hard to read >5 categories |
| **Show correlations** | Scatter plot | Reveals non-linear relationships |
| **Show distributions** | Histogram or box plot | Shows spread and outliers |
| **Show rankings** | Sorted bar chart | Immediate identification of top/bottom |
| **Show hierarchy** | Treemap (use sparingly) | Space-efficient but harder to read |
| **Show geographic** | Choropleth map | Context-specific (avoid if geography not relevant) |

### The "10-Second Rule"

**Your visualization should answer the decision question in <10 seconds.**

How to achieve this:
- **Annotate the insight:** Add text label pointing to key finding
- **Sort intelligently:** Highest to lowest for rankings
- **Use color sparingly:** Highlight the 1-3 items that matter most
- **Remove gridlines:** Reduce visual clutter
- **Direct titles:** "Top 5 Products by Margin" > "Product Analysis"

### Color Guidelines

**Do:**
- Use grayscale + 1 accent color for emphasis
- Use colorblind-safe palettes (avoid red-green)
- Use color to encode urgency (red=bad, green=good is intuitive)

**Don't:**
- Use rainbow gradients (hard to interpret magnitude)
- Use >5 colors in single chart (cognitively overwhelming)
- Use color without purpose (decoration ≠ insight)

### Interactivity Guidelines

**Add interactivity when:**
- Stakeholder needs to explore different time periods (date filter)
- Stakeholder needs to drill down (click chart → details)
- Stakeholder needs to compare scenarios (dropdown selector)

**Skip interactivity when:**
- Decision is obvious from static view
- Adding it takes >20 minutes
- Stakeholder will only view once (PDF export would work)

---

## 📁 EXPECTED FILE STRUCTURE (per project)

### Day 16 (Streamlit):
```
day16/
├── day16_VIZ_compliance_dashboard.py
├── day16_CONFIG_settings.py
├── queries/
│   └── day16_QUERY_mfg_assets_compliance.sql
├── screenshots/
│   ├── day16_full_dashboard.png
│   └── day16_urgency_filtering.png
├── day16_requirements.txt
├── .env.example
└── README.md
```

### Day 17 (Looker Studio):
```
day17/
├── day17_VIZ_looker_studio.url (link to published dashboard)
├── day17_QUERY_campaign_data.sql
├── screenshots/
│   ├── day17_full_dashboard.png
│   ├── day17_campaign_roi_chart.png
│   └── day17_trend_chart.png
├── data/
│   └── day17_synthetic_campaign_data.csv
└── README.md
```

### Day 18 (Plotly HTML):
```
day18/
├── day18_VIZ_dashboard.html (standalone dashboard)
├── day18_VIZ_generator.py (script that generates HTML)
├── day18_CONFIG_settings.py
├── queries/
│   └── day18_QUERY_gazette_data.sql
├── screenshots/
│   └── day18_full_dashboard.png
├── day18_requirements.txt
├── .env.example
└── README.md
```

### Day 19 (Streamlit):
```
day19/
├── day19_VIZ_saas_health_dashboard.py
├── day19_CONFIG_settings.py
├── queries/
│   └── day19_QUERY_saas_metrics.sql
├── screenshots/
│   ├── day19_retention_curves.png
│   └── day19_mrr_waterfall.png
├── day19_requirements.txt
├── .env.example
└── README.md
```

### Day 20 (Tableau Public):
```
day20/
├── day20_VIZ_hospitality_ltv.twbx
├── day20_VIZ_tableau_link.url
├── data/
│   └── day20_guest_ltv_data.csv
├── screenshots/
│   ├── day20_scatter_plot.png
│   └── day20_top_guests_table.png
└── README.md
```

---

## 📊 FINAL VALIDATION CHECKLIST

Before pushing to GitHub:

### Code Quality:
- [ ] All files have `day16_` (or dayXX_) prefix
- [ ] All variables/classes/functions follow isolated naming
- [ ] Environment variables in config/.env follow `DAYXX_` pattern
- [ ] .env.example includes all required variables
- [ ] Dependencies listed in dayXX_requirements.txt

### Functionality:
- [ ] Visualization loads without errors
- [ ] All charts display correctly (no empty/broken visuals)
- [ ] Filters/interactivity works as expected
- [ ] Data values are accurate (spot-checked against source)
- [ ] Decision question answered in <10 seconds

### Decision Clarity:
- [ ] README states WHO is making a decision
- [ ] README states WHAT decision they're making
- [ ] README states WHY this visualization supports the decision
- [ ] Every chart has clear purpose (no decorative charts)

### Documentation:
- [ ] README explains decision context
- [ ] Configuration instructions are clear
- [ ] Quick Start works (tested in clean environment)
- [ ] Screenshots committed to repo
- [ ] Connection to data source documented (Day X model or synthetic)

### Portfolio Readiness:
- [ ] Non-technical person can understand business value from README
- [ ] Demonstrates analytical thinking (decision-first approach)
- [ ] Screenshots show professional quality
- [ ] Upwork keywords documented

---

## 💡 FINAL REMINDER

**You're building a PORTFOLIO, not a production product.**

The goal is to demonstrate:
- ✅ You think analytically (decision-first, not viz-first)
- ✅ You choose appropriate chart types for decisions
- ✅ You can work with data pipelines (model → query → viz)
- ✅ You can deliver in 3 hours
- ✅ You know how to work with code isolation
- ✅ You prioritize insight clarity over visual polish

**NOT to demonstrate:**
- ❌ Perfect, pixel-perfect design
- ❌ Every chart type and feature
- ❌ Complex interactivity
- ❌ Production-ready at scale

**Focus: Function > Form. Insight > Aesthetics. Decision Support > Decoration. Delivered > Ideal. Isolated > Shared.**

---

## 🧪 TESTING STRATEGY

### Local Testing Requirements:

**All Visualization Projects:**
- [ ] Can load visualization by following README Quick Start
- [ ] All charts render correctly (no errors in console/logs)
- [ ] Data values spot-checked against source (5+ records)
- [ ] Filters update visuals correctly (if applicable)
- [ ] Screenshots match actual output

**Tool-Specific Tests:**

**Streamlit:**
```bash
# Run and verify
streamlit run dayXX_VIZ_main.py
# Should open browser, show charts, no errors in terminal
```

**Plotly (standalone HTML):**
```bash
# Generate HTML
python dayXX_VIZ_generator.py
# Open dayXX_VIZ_dashboard.html in browser
# Verify charts load and interactivity works
```

**Power BI:**
- [ ] .pbix file opens without errors
- [ ] Data source connection works (or uses embedded data)
- [ ] All visuals render
- [ ] Can export to PDF

**Tableau Public:**
- [ ] Published dashboard link works
- [ ] .twbx file opens locally in Tableau Desktop/Reader
- [ ] Data extracts included (no live connections for portfolio)

---

## 📖 EXAMPLE: DECISION CONTEXT SECTION

### Template:
```markdown
## Decision Context

### WHO is making a decision?
[Name], [Role] at [Organization Type]
- **Background:** [1-2 sentences from persona/project brief]
- **Responsibility:** [What they're accountable for]

### WHAT decision are they making?
[Specific action verb] + [Target] + [Time horizon]

**Examples:**
- "Prioritize which 10 customer accounts to call this week for upsell"
- "Decide which ad campaigns to pause tomorrow based on ROI"
- "Identify which certifications need renewal this month to avoid penalties"

### WHAT minimum visual supports this decision?
[Chart type] + [What it shows] + [Why this chart type]

**Example:**
"Sorted table showing: Asset name, expiry date, days until expiry, urgency flag.
Why table? Luna needs exact dates to schedule renewals - chart wouldn't provide precision needed."

### Why THIS visualization (not others)?
[Justify choices made, especially what you DIDN'T build]

**Example:**
"Considered timeline chart, but Luna doesn't need historical view - only future expirations matter.
Considered map of facility locations, but location doesn't affect renewal priority - urgency does."
```

---

## END OF DOCUMENT
