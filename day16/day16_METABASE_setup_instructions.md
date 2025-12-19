# Day 16: Metabase Auto-Setup Instructions

## 🚀 Quick Start (5 minutes setup, script runs while you do other work)

### Step 1: Setup Environment Variables (2 minutes)

**The script uses the ROOT `config/.env` file - this keeps all project credentials in one place!**

```bash
# Open the root .env file (NOT a local day16/.env)
code config/.env  # or nano config/.env, vim config/.env, etc.
```

**Add these 4 lines to `config/.env`:**
```bash
# Day 16: Metabase Cloud Configuration
DAY16_METABASE_URL=https://your-instance.metabaseapp.com
DAY16_METABASE_EMAIL=your-email@example.com
DAY16_METABASE_PASSWORD=your-actual-password
DAY16_METABASE_DATABASE_NAME=Day 16 - SaaS Health Metrics
```

**How to find your Metabase URL:**
- If you signed up at metabase.com, it's usually: `https://[your-company].metabaseapp.com`
- Check your browser address bar when logged into Metabase

**⚠️  IMPORTANT:** `config/.env` is in root `.gitignore` - your password is safe!

---

### Step 2: Install Python Packages (1 minute)

```bash
cd day16
pip install -r day16_requirements.txt
```

This installs:
- `python-dotenv` - For loading `.env` file
- `requests` - For Metabase API calls

---

### Step 3: Run the Script (2 minutes to start, then runs on its own)

```bash
cd day16
python3 day16_METABASE_auto_setup.py
```

**The script will:**
- ✅ Load credentials from `../config/.env`
- ✅ Validate all required variables are set
- ✅ Create dashboard and all cards automatically

**What the script does:**
1. ✅ Logs into your Metabase account
2. ✅ Finds your BigQuery database connection
3. ✅ Creates a new dashboard: "Murilo's SaaS Health Metrics Dashboard"
4. ✅ Creates all 10 cards (6 main + 4 bonus if you want)
5. ✅ Adds cards to dashboard with smart layout
6. ✅ Prints dashboard URL when done

**Expected output:**
```
======================================================================
Day 16: Metabase Dashboard Auto-Setup
======================================================================

🔐 Logging into Metabase...
✅ Login successful!

🔍 Finding database 'Day 16 - SaaS Health Metrics'...
✅ Found database ID: 2

📋 Creating dashboard: Murilo's SaaS Health Metrics Dashboard...
✅ Dashboard created! ID: 5

📊 Creating card: Current MRR...
✅ Card created! ID: 12

📊 Creating card: Churn Rate (%)...
✅ Card created! ID: 13

... (continues for all 10 cards)

======================================================================
✅ DASHBOARD SETUP COMPLETE!
======================================================================

🔗 Dashboard URL: https://your-instance.metabaseapp.com/dashboard/5

📝 Next steps:
1. Open the dashboard link above
2. Adjust visual styling (colors, fonts) as needed
3. Take screenshots for documentation
4. Export dashboard JSON (Settings → Export)

🎉 You're done! 80% of the work is automated.
```

---

## ⏱️ Time Savings

**Without script (manual):**
- Create 10 cards: ~30 minutes
- Add to dashboard: ~10 minutes
- Layout adjustment: ~10 minutes
- **Total: ~50 minutes**

**With script:**
- Setup script: ~5 minutes
- Script runs: ~2 minutes
- Visual tweaks: ~10 minutes
- **Total: ~17 minutes** (save 33 minutes!)

**Plus:** You can work on other projects while the script runs!

---

## 🎨 After Script Completes

The dashboard will be **80% ready**. You only need to:

### Visual Adjustments (10 minutes)
1. **Card colors** - Change metric colors (green/yellow/red thresholds)
2. **Chart styling** - Adjust line colors in retention curves
3. **Layout tweaks** - Resize cards if needed
4. **Titles** - Add subtitles or descriptions if desired

### Screenshots (5 minutes)
1. Full dashboard view → `screenshots/day16_full_dashboard.png`
2. Individual cards → `screenshots/day16_card_*.png`

### Export Dashboard (1 minute)
1. Click dashboard Settings (⚙️)
2. Click "Export"
3. Save as `day16_metabase_dashboard.json`

---

## 🆘 Troubleshooting

### "Login failed: 401"
**Cause:** Wrong email or password
**Fix:** Double-check `DAY16_METABASE_EMAIL` and `DAY16_METABASE_PASSWORD` in `config/.env` file

---

### "Database 'Day 16 - SaaS Health Metrics' not found"
**Cause:** Database name doesn't match exactly
**Fix:**
1. Log into Metabase
2. Go to Settings → Databases
3. Copy the **exact name** (case-sensitive)
4. Update `DAY16_METABASE_DATABASE_NAME` in `config/.env` file

---

### "Failed to create card: 400"
**Cause:** SQL syntax error or missing table
**Fix:**
1. Check that all 8 tables are uploaded to BigQuery
2. Verify table names match: `day06_dashboard_kpis`, etc.
3. Run validation query:
```bash
bq ls advent2025-day16:day16_saas_metrics
```

---

### "ModuleNotFoundError: No module named 'requests'"
**Cause:** Python `requests` library not installed
**Fix:**
```bash
pip install requests
```

---

## 🔐 Security Note

**✅ Your credentials are safe!**

The script uses **environment variables** from `config/.env` (root .env file):
- ✅ `config/.env` is in root `.gitignore` - never committed to git
- ✅ Passwords stay on your local machine only
- ✅ All projects share the same credential file (DRY principle)

**What gets committed to git:**
- ✅ `day16_METABASE_auto_setup.py` - Script (no passwords)
- ✅ `day16/.env.example` - Template (placeholder values)
- ✅ Root `.gitignore` - Protects `config/.env`

**What NEVER gets committed:**
- ❌ `config/.env` - Contains ALL project passwords
- ❌ `*.json` - Service account keys

---

## 📊 What Gets Created

### Dashboard Layout:

```
+----------+----------+----------+----------+
| MRR      | Churn %  | Active   | Healthy% |
| $210K    | 35.6%    | 322      | 95.3%    |
+----------+----------+----------+----------+
|                                           |
|     MRR Growth Over Time (Area Chart)    |
|                                           |
+-------------------------------------------+
|                                           |
|     MoM Growth Rate (Line Chart)          |
|                                           |
+-------------------------------------------+
|                                           |
| Cohort Retention Curves (PRIMARY VISUAL) |
|         (Multi-line chart)                |
|                                           |
+-------------------------------------------+
|                                           |
|   Churn Heatmap: Cohort × Plan Tier      |
|              (Table)                      |
|                                           |
+-------------------------------------------+
| At-Risk Distribution  | Top 10 Critical   |
|     (Pie Chart)       | Customers (Table) |
+---------------------+---------------------+
```

---

## 🎯 Success Criteria

After running the script, you should have:

- ✅ 1 dashboard created
- ✅ 10 cards created (6 main + 4 bonus)
- ✅ All cards added to dashboard with layout
- ✅ Dashboard accessible via URL
- ✅ All cards showing data (not errors)

If any card shows an error, check:
1. BigQuery tables are uploaded correctly
2. Table names match exactly
3. Service account has permissions

---

## 💡 Pro Tips

**Tip 1: Test with 1 card first**
Comment out all but the first card in `DASHBOARD_CARDS` array to test connection:
```python
DASHBOARD_CARDS = [
    {
        "name": "Current MRR",
        # ... only keep this one
    },
    # Comment out the rest for testing
]
```

**Tip 2: Save dashboard URL**
The script prints the dashboard URL at the end. Save it or bookmark it!

**Tip 3: Re-run if needed**
If something goes wrong, you can:
1. Delete the dashboard in Metabase
2. Fix the script
3. Re-run (it will create a new dashboard)

---

## 🚀 Ready to Automate?

1. **Update credentials** in `day16_METABASE_auto_setup.py`
2. **Run script**: `python3 day16_METABASE_auto_setup.py`
3. **Work on other projects** while it runs (~2 minutes)
4. **Come back**, open dashboard URL, adjust visuals
5. **Done!** 🎉

---

Built for Christmas Data Advent 2025 - Day 16
Automation saves you 33 minutes! ⚡
