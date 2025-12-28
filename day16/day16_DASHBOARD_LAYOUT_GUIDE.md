# Day 16: Metabase Dashboard Layout Guide

## 📊 Dashboard: Murilo's SaaS Health Metrics Dashboard

**Dashboard URL:** https://green-sponge.metabaseapp.com/dashboard/12

---

## 🎨 Recommended Layout

### Section 1: Business Health Baseline (Row 1)
**Layout:** 4 KPI cards in a single row (3 columns each)

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Current MRR │ Churn Rate  │   Active    │  Healthy    │
│             │     (%)     │  Customers  │ Customers % │
│ $210,596.39 │   35.60%    │     322     │   95.3%     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Cards:**
- **Current MRR** (ID: 127) - 3x3 grid
- **Churn Rate (%)** (ID: 128) - 3x3 grid
- **Active Customers** (ID: 129) - 3x3 grid
- **Healthy Customers %** (ID: 130) - 3x3 grid

**Styling Tips:**
- Current MRR: Green background (#2ecc71)
- Churn Rate: Red background (#e74c3c)
- Active Customers: Blue background (#3498db)
- Healthy %: Green background (#2ecc71)
- Large font size: 36-42pt for numbers
- Small gray text: 12-14pt for labels

---

### Section 2: Growth Trajectory (Row 2)
**Layout:** 2 line charts side by side (6 columns each)

```
┌──────────────────────────────┬──────────────────────────────┐
│   MRR Growth Over Time       │  Month-over-Month Growth %   │
│   (Line Chart)               │      (Line Chart)            │
│   - Cumulative MRR           │   Latest: -2.03%             │
│   - Net MRR Change           │                              │
└──────────────────────────────┴──────────────────────────────┘
```

**Cards:**
- **MRR Growth Over Time** (ID: 137) - 6x4 grid
  - Display: Line chart with 2 series (cumulative_mrr, net_mrr)
  - X-axis: month
  - Y-axis: MRR ($)

- **Month-over-Month Growth Rate** (ID: 138) - 6x4 grid
  - Display: Line chart with area fill
  - X-axis: month
  - Y-axis: growth_rate_pct (%)
  - Color: Green for positive, red for negative

**Styling Tips:**
- Add goal line at 0% for growth rate chart
- Use smooth curve interpolation
- Show data labels on hover

---

### Section 3: Cohort Retention Analysis (Row 3) ⭐ PRIMARY
**Layout:** Large cohort chart (8 cols) + compact heatmap (4 cols)

```
┌─────────────────────────────────────────┬───────────────┐
│  ⭐ Cohort Retention Curves             │ Churn Heatmap │
│  (Multi-line Chart)                     │   (Table)     │
│                                         │               │
│  23 cohorts tracked over 12 months     │ Cohort × Plan │
│                                         │               │
└─────────────────────────────────────────┴───────────────┘
```

**Cards:**
- **⭐ Cohort Retention Curves** (ID: 139) - 8x5 grid **PRIMARY DECISION VISUAL**
  - Display: Line chart with multiple series (one per cohort)
  - X-axis: months_since_signup (0-12)
  - Y-axis: retention_rate_pct (0-100%)
  - Series: One line per cohort_month
  - Colors: Use distinct colors for each cohort (husl palette)

- **Churn Heatmap by Cohort × Plan** (ID: 140) - 4x5 grid
  - Display: Table with conditional formatting
  - Columns: cohort, plan_tier, churn_rate_pct
  - Conditional formatting: Red gradient (higher = darker red)

**Styling Tips:**
- Cohort Retention:
  - Legend on right side
  - Grid lines enabled
  - Line thickness: 2-3px
  - Markers on data points
- Heatmap:
  - Color scale: White → Yellow → Orange → Red
  - Font: Monospace for percentages

**💡 Decision Insight:**
- Look for cohorts with steeper decline slopes = higher churn risk
- Compare early cohorts vs recent cohorts to see if retention is improving

---

### Section 4: Customer Health Alerts (Row 4)
**Layout:** 2 charts side by side (6 columns each)

```
┌──────────────────────────────┬──────────────────────────────┐
│  Customer Health Distribution│   Top 10 At-Risk Customers   │
│       (Pie Chart)            │         (Table)              │
│                              │                              │
│  Healthy: 61.4%              │  Total LTV at risk:          │
│  At Risk: 3.0%               │  $13,790.43                  │
│  Churned: 35.6%              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

**Cards:**
- **Customer Health Distribution** (ID: 141) - 6x4 grid
  - Display: Pie chart
  - Dimension: health_status
  - Metric: customer_count
  - Colors:
    - Healthy: #2ecc71 (green)
    - At Risk: #f39c12 (orange)
    - Churned: #95a5a6 (gray)

- **Top 10 At-Risk Customers** (ID: 142) - 6x4 grid
  - Display: Table
  - Columns: customer_id, ltv, current_mrr, health_status, plan_tier
  - Sort: Descending by ltv
  - Limit: 10 rows

**Styling Tips:**
- Pie chart: Show percentages and labels
- Table:
  - Bold customer_id column
  - Currency format for ltv and current_mrr
  - Highlight rows with ltv > $1,500

**💡 Action Required:**
- Contact these customers TODAY to prevent churn
- Total potential revenue loss: $13,790.43

---

## 📐 Grid Layout Coordinates

| Card Name | Row | Col | Size X | Size Y |
|-----------|-----|-----|--------|--------|
| Current MRR | 0 | 0 | 3 | 3 |
| Churn Rate (%) | 0 | 3 | 3 | 3 |
| Active Customers | 0 | 6 | 3 | 3 |
| Healthy Customers % | 0 | 9 | 3 | 3 |
| MRR Growth Over Time | 3 | 0 | 6 | 4 |
| Month-over-Month Growth Rate | 3 | 6 | 6 | 4 |
| ⭐ Cohort Retention Curves | 7 | 0 | 8 | 5 |
| Churn Heatmap | 7 | 8 | 4 | 5 |
| Customer Health Distribution | 12 | 0 | 6 | 4 |
| Top 10 At-Risk Customers | 12 | 6 | 6 | 4 |

---

## 🔧 Manual Setup Instructions

### Step 1: Open Dashboard in Edit Mode
1. Go to https://green-sponge.metabaseapp.com/dashboard/12
2. Click **"Edit"** button (pencil icon, top right)

### Step 2: Add Cards to Dashboard

For each card, click **"Add a question"** and search by name or ID:

**Section 1: KPIs (Already Added ✅)**
- Current MRR (ID: 127)
- Churn Rate (%) (ID: 128)
- Active Customers (ID: 129)
- Healthy Customers % (ID: 130)

**Section 2: Growth (New Cards)**
1. Search for **"MRR Growth Over Time"** (ID: 137)
   - Drag to position: Row 3, left side (6 columns wide)

2. Search for **"Month-over-Month Growth Rate"** (ID: 138)
   - Drag to position: Row 3, right side (6 columns wide)

**Section 3: Retention (New Cards)**
3. Search for **"⭐ Cohort Retention Curves"** (ID: 139)
   - Drag to position: Row 7, left side (8 columns wide)
   - **This is the PRIMARY visual** - make it large!

4. Search for **"Churn Heatmap by Cohort × Plan"** (ID: 140)
   - Drag to position: Row 7, right side (4 columns wide)

**Section 4: Health (New Cards)**
5. Search for **"Customer Health Distribution"** (ID: 141)
   - Drag to position: Row 12, left side (6 columns wide)

6. Search for **"Top 10 At-Risk Customers"** (ID: 142)
   - Drag to position: Row 12, right side (6 columns wide)

### Step 3: Adjust Sizing
- Drag card corners to resize
- Drag cards to reposition
- Ensure no overlapping

### Step 4: Save Dashboard
- Click **"Save"** (top right)
- View the final dashboard

---

## 🎨 Visual Styling Recommendations

### Color Palette
- **Positive/Healthy:** #2ecc71 (green)
- **Negative/Risk:** #e74c3c (red)
- **Warning:** #f39c12 (orange)
- **Neutral:** #3498db (blue)
- **Inactive:** #95a5a6 (gray)

### Typography
- **KPI Numbers:** 36-42pt, Bold
- **KPI Labels:** 12-14pt, Regular, Gray
- **Chart Titles:** 16-18pt, Bold
- **Chart Labels:** 10-12pt, Regular
- **Table Headers:** 11pt, Bold
- **Table Data:** 10pt, Regular

### Chart Settings
- **Line Charts:**
  - Line thickness: 2-3px
  - Markers: Enabled (circles, 4-5px)
  - Grid: Horizontal lines only
  - Legend: Right side or bottom

- **Pie Chart:**
  - Show percentages inside slices
  - Show labels outside
  - Explode slices slightly (5%)

- **Tables:**
  - Alternating row colors
  - Bold headers
  - Currency formatting: $X,XXX.XX
  - Percentage formatting: XX.X%

---

## 📊 Expected Numbers Summary

### Section 1: KPIs
- Current MRR: **$210,596.39**
- Churn Rate: **35.60%**
- Active Customers: **322**
- Healthy Customers %: **95.3%**

### Section 2: Growth
- Latest Net MRR: **-$4,352.72** (declining!)
- Latest Growth Rate: **-2.03%**
- Data Points: **24 months**

### Section 3: Retention
- Cohorts Tracked: **23**
- Data Points: **299** (12 months × 23 cohorts)
- Example: Jan 2023 cohort retention: 100% → 52.3% over 12 months

### Section 4: Health
- Healthy: **307 customers (61.4%)**
- At Risk: **15 customers (3.0%)**
- Churned: **178 customers (35.6%)**
- Total LTV at Risk: **$13,790.43**

---

## 📸 Screenshots Checklist

After completing the layout, take these screenshots:

- [ ] **Full Dashboard View** - All 10 cards visible
- [ ] **Section 1: KPIs** - Close-up of 4 KPI cards
- [ ] **Section 2: Growth Charts** - MRR and Growth Rate charts
- [ ] **Section 3: ⭐ Cohort Retention** - PRIMARY VISUAL (large screenshot)
- [ ] **Section 4: Customer Health** - Pie chart and at-risk table
- [ ] **Individual Card Examples** - 2-3 cards showing data quality

Save screenshots to: `day16/screenshots/`

---

## 🔗 Quick Links

- **Dashboard:** https://green-sponge.metabaseapp.com/dashboard/12
- **Card 137:** https://green-sponge.metabaseapp.com/question/137 (MRR Growth)
- **Card 138:** https://green-sponge.metabaseapp.com/question/138 (Growth Rate)
- **Card 139:** https://green-sponge.metabaseapp.com/question/139 (⭐ Cohort Retention)
- **Card 140:** https://green-sponge.metabaseapp.com/question/140 (Churn Heatmap)
- **Card 141:** https://green-sponge.metabaseapp.com/question/141 (Health Distribution)
- **Card 142:** https://green-sponge.metabaseapp.com/question/142 (At-Risk Customers)

---

## ✅ Completion Checklist

- [x] Fix existing 4 KPI cards with correct SQL
- [x] Create 6 remaining cards with BigQuery queries
- [ ] Add all 6 cards to dashboard layout
- [ ] Adjust visual styling (colors, fonts, sizes)
- [ ] Take screenshots of completed dashboard
- [ ] Export dashboard JSON
- [ ] Commit to git

---

## 💡 Tips for Success

1. **Start with the PRIMARY visual** (⭐ Cohort Retention Curves) - make it prominent
2. **Use consistent colors** throughout the dashboard
3. **Test each card individually** before adding to dashboard
4. **Mobile view:** Check how it looks on smaller screens
5. **Filters:** Consider adding date range filter if needed
6. **Refresh data:** Set auto-refresh interval (hourly/daily)

---

## 🆘 Troubleshooting

### "Card shows no data"
- Check if BigQuery tables exist: `advent2025-day16.day16_saas_metrics.*`
- Verify dataset permissions in BigQuery
- Run query directly in Metabase SQL editor

### "Connection error"
- Refresh Metabase database connection
- Check BigQuery service account key is valid
- Verify project ID and dataset name are correct

### "Query timeout"
- Cohort retention query takes ~5-10 seconds (299 rows)
- Add indexes to BigQuery tables if needed
- Consider materializing retention table as view

---

**Last Updated:** 2025-12-23
**Author:** Claude Code
**Dashboard Owner:** Murilo
