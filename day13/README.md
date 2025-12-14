## Day 13 – Alert Triage Orchestrator (Finance Compliance)

Automates ingestion, classification, routing, and audit logging of financial compliance alerts for a Legal/GRC leader. Built to run every 15 minutes via Prefect Cloud with 24h deduplication and an auditable SQLite trail.

### Solution Overview
- **Flow:** Gmail alerts (sample JSON) + CSV drop folder → dedup (24h SHA256) → severity classification → routing to Slack/email → SQLite audit with SLA tracking.
- **Scheduling:** Prefect deployment (`*/15 * * * *`, UTC); local `python day13/day13_SCHEDULER_main.py` builds the deployment.
- **Dedup & Audit:** SHA256 of alert payload stored in `dedup_index`; audit log captures routed destinations, severity, timestamps, and SLA seconds.
- **Synthetic Data:** 30 vendor email alerts (`day13/data/day13_mock_emails.json`) and 50 transaction rows (`day13/data/day13_transactions.csv`).

### Files
- `day13_ORCHESTRATOR_alert_triage.py` – ingestion, dedup, classification, routing, audit.
- `day13_SCHEDULER_main.py` – Prefect flow + deployment builder (15m schedule).
- `day13_CONFIG_routing_rules.py` – routing matrix defaults and env overrides.
- `.env.example` – required configuration placeholders.
- `day13_requirements.txt` – pinned dependencies.
- `data/` – synthetic Gmail JSON + CSV; `logs/` – execution logs (created on run).

### Configuration
1) Copy `.env.example` to `config/.env` or export variables:
   - Ingestion: `DAY13_GMAIL_SAMPLE_PATH`, `DAY13_CSV_DROP_FOLDER`
   - Routing: `DAY13_SLACK_WEBHOOK_URL`, `DAY13_EMAIL_RECIPIENTS`, SMTP fields
   - Storage: `DAY13_AUDIT_DB_PATH`
   - Dedup: `DAY13_DEDUP_WINDOW_MINUTES` (default 1440 = 24h)
   - Prefect: `DAY13_PREFECT_WORK_POOL`
   - Mode: `DAY13_DRY_RUN=true` to avoid sending Slack/email
2) Install deps: `pip install -r day13/day13_requirements.txt`

### Running & Testing (local)
- One-off run (dry-run enabled by default):
  - `python day13/day13_ORCHESTRATOR_alert_triage.py`
- Prefect deployment (requires Prefect auth):
  - `python day13/day13_SCHEDULER_main.py`
  - Prefect UI will show the 15m scheduled flow; agent must point to `DAY13_PREFECT_WORK_POOL`.
- Verification:
  - Check log file `day13/logs/day13_execution.log`
  - Inspect audit DB `day13/data/day13_audit_log.db` (`sqlite3 ... "select severity, count(*) from audit_log group by severity;"`)
  - Duplicate run should log `Duplicate detected` entries due to 24h window.

### Notes & Assumptions
- Gmail ingestion uses the provided synthetic JSON; swap to Gmail API by replacing `day13_ingest_gmail_stub`.
- Routing tokens map to Slack/email; Slack uses a single webhook (channel decided in Slack), email uses SMTP.
- Classification combines hints, risk score, keywords, and high-risk country list; adjust in `day13_classify_alert`.
- SLA is computed as triage_time minus alert `created_at` (falls back to triage time if missing).

### Next Steps (optional)
- Wire real Gmail API fetch + IMAP fallback.
- Add ticketing destination (e.g., Jira API) for Critical/High.
- Extend observability with Prometheus-style counters or Prefect blocks. 
