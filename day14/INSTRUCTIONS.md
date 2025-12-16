# Day 14: Final Instructions to Run

## ✅ Prerequisites Complete
- All configuration done
- Environment variables set in root `.env`

---

## 🚀 Run the Automation (30 seconds)

```bash
# From the day14 directory
python day14_MAIN_automation.py
```

**That's it!**

---

## 📧 Expected Output

```
============================================================
DAY 14: Transport KPI Automation
============================================================

📊 Fetching KPIs (last 30 days)...
Fetching transport data from 2025-11-15 to 2025-12-15...
Querying Sao_Paulo for 'transporte OR mobilidade'...
Querying Rio_de_Janeiro for 'transporte OR mobilidade'...
Querying Brasilia for 'transporte OR mobilidade'...
Querying Salvador for 'transporte OR mobilidade'...
Querying Fortaleza for 'transporte OR mobilidade'...
Querying Belo_Horizonte for 'transporte OR mobilidade'...
Querying Manaus for 'transporte OR mobilidade'...
Querying Curitiba for 'transporte OR mobilidade'...
Querying Recife for 'transporte OR mobilidade'...
Querying Porto_Alegre for 'transporte OR mobilidade'...
Querying Sao_Paulo for 'prazo OR cumprimento OR fiscalização'...
[... 30 total API calls ...]

✅ KPI Summary:
   - New Regulations: 95
   - Active Municipalities: 5
   - Compliance Mentions: 159
   - Safety Incidents: 15

📧 Building HTML email...

📤 Sending email to your-email@gmail.com...

✅ Email sent successfully to your-email@gmail.com

============================================================
✅ AUTOMATION COMPLETE!
============================================================
```

**Runtime:** ~20-30 seconds

---

## 📬 Check Your Inbox

You should receive an email with:

- **Subject:** `🚦 Transport KPI Report - 2025-12-15 (95 regulations, 5 cities)`
- **Body:** Professional HTML email with:
  - 4 KPI cards (New Regulations, Active Municipalities, Compliance, Safety)
  - Active municipality badges (e.g., "Curitiba (24)")
  - Dynamic insights based on data
  - 30-day date range

---

## 🔧 Troubleshooting

### Error: "DAY14_SMTP_PASSWORD not found"

**Fix:** Add variables to root `.env` file (NOT `day14/.env`):

```bash
# Edit: advent-automation-2025/.env
DAY14_SMTP_USER=your-email@gmail.com
DAY14_SMTP_PASSWORD=your-gmail-app-password
DAY14_SMTP_TO=your-email@gmail.com
```

### Error: "SMTPAuthenticationError"

**Fix:**
1. Verify Gmail App Password is correct (16 characters, no spaces)
2. Go to https://myaccount.google.com/apppasswords
3. Generate new password if needed

### KPIs = 0

**Normal!** Some 30-day periods have few publications.

**Fix:** Increase lookback period in `day14_MAIN_automation.py`:
```python
DAYS_BACK = 60  # Change from 30 to 60
```

---

## 📅 Schedule Daily Execution (Optional)

### Linux/Mac (cron)

```bash
crontab -e

# Add this line (runs daily at 8am):
0 8 * * * cd /path/to/day14 && /usr/bin/python3 day14_MAIN_automation.py >> logs/cron.log 2>&1
```

### Windows (Task Scheduler)

1. Open "Task Scheduler"
2. Create Basic Task
3. Trigger: Daily, 8:00 AM
4. Action: Start a program
   - **Program:** `python`
   - **Arguments:** `day14_MAIN_automation.py`
   - **Start in:** `C:\path\to\day14`

---

## ✅ Done!

Your automation is now running. You can:

- **Run manually:** `python day14_MAIN_automation.py` anytime
- **Schedule daily:** Use cron or Task Scheduler
- **Customize:** Edit cities, keywords, lookback period in config files

**Questions?** See [README.md](README.md) for full documentation.
