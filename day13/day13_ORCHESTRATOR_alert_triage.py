"""
day13_ORCHESTRATOR_alert_triage.py

Python orchestrator for Day 13: Alert Triage (Finance Compliance).
Ingests alerts from Gmail (sample/stub) and a CSV drop folder,
classifies severity, deduplicates within a time window, routes to Slack/email,
and records an audit trail in SQLite with SLA timestamps.
"""

import csv
import datetime
import hashlib
import json
import logging
import os
import pathlib
import smtplib
import sqlite3
import ssl
import sys
from email.mime.text import MIMEText
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from day13.day13_CONFIG_routing_rules import day13_load_routing_matrix_from_env


def day13_setup_logging(log_path: str) -> None:
    pathlib.Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )


def day13_load_env() -> None:
    load_dotenv()


def day13_default_config() -> Dict[str, Any]:
    return {
        "gmail_sample_path": os.getenv(
            "DAY13_GMAIL_SAMPLE_PATH", "day13/data/day13_mock_emails.json"
        ),
        "csv_drop_folder": os.getenv("DAY13_CSV_DROP_FOLDER", "day13/data"),
        "audit_db_path": os.getenv("DAY13_AUDIT_DB_PATH", "day13/data/day13_audit_log.db"),
        "dedup_window_minutes": int(os.getenv("DAY13_DEDUP_WINDOW_MINUTES", "1440")),
        "slack_webhook": os.getenv("DAY13_SLACK_WEBHOOK_URL", ""),
        "smtp_host": os.getenv("DAY13_SMTP_HOST", ""),
        "smtp_port": int(os.getenv("DAY13_SMTP_PORT", "587")),
        "smtp_user": os.getenv("DAY13_SMTP_USER", ""),
        "smtp_password": os.getenv("DAY13_SMTP_PASSWORD", ""),
        "email_recipients": [
            r.strip()
            for r in os.getenv("DAY13_EMAIL_RECIPIENTS", "compliance@example.com").split(",")
            if r.strip()
        ],
        "dry_run": os.getenv("DAY13_DRY_RUN", "true").lower() == "true",
    }


def day13_init_sqlite(db_path: str) -> sqlite3.Connection:
    pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dedup_index (
            alert_hash TEXT PRIMARY KEY,
            first_seen_utc TEXT NOT NULL,
            source TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_hash TEXT NOT NULL,
            severity TEXT NOT NULL,
            source TEXT NOT NULL,
            routed_to TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            triaged_at_utc TEXT NOT NULL,
            sla_seconds INTEGER NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def day13_compute_hash(alert: Dict[str, Any]) -> str:
    serialized = json.dumps(alert, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def day13_is_duplicate(
    conn: sqlite3.Connection, alert_hash: str, dedup_window_minutes: int
) -> bool:
    cursor = conn.execute(
        "SELECT first_seen_utc FROM dedup_index WHERE alert_hash = ?", (alert_hash,)
    )
    row = cursor.fetchone()
    if not row:
        return False
    first_seen = datetime.datetime.fromisoformat(row[0].replace("Z", "+00:00"))
    age_minutes = (
        datetime.datetime.now(datetime.timezone.utc) - first_seen
    ).total_seconds() / 60
    return age_minutes <= dedup_window_minutes


def day13_record_dedup(conn: sqlite3.Connection, alert_hash: str, source: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO dedup_index (alert_hash, first_seen_utc, source) VALUES (?, ?, ?)",
        (
            alert_hash,
            datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            source,
        ),
    )
    conn.commit()


def day13_classify_alert(alert: Dict[str, Any]) -> str:
    """
    Lightweight classifier based on hints, risk score, keywords, and country.
    """
    hint = alert.get("severity_hint", "").lower()
    subject = alert.get("subject", "").lower()
    body = alert.get("body", "").lower()
    risk_score = float(alert.get("risk_score", 0) or 0)
    country = alert.get("country", "").upper()

    high_risk_countries = {"IR", "RU", "NG", "PA", "KY", "AF", "SY"}

    if hint in {"critical", "high", "medium", "low"}:
        return hint
    if "sanction" in subject or "sanctions" in body:
        return "critical"
    if risk_score >= 90 or "high-risk" in subject:
        return "critical"
    if risk_score >= 75 or country in high_risk_countries:
        return "high"
    if risk_score >= 40 or "suspicious" in subject:
        return "medium"
    return "low"


def day13_ingest_gmail_stub(sample_path: str) -> List[Dict[str, Any]]:
    """
    Reads synthetic Gmail alerts from JSON. In real use, replace with Gmail API call.
    """
    path = pathlib.Path(sample_path)
    if not path.exists():
        logging.warning("Gmail sample file not found at %s", sample_path)
        return []
    try:
        data = json.loads(path.read_text())
        alerts = []
        for item in data:
            alerts.append(
                {
                    "source": "gmail",
                    "message_id": item.get("message_id", ""),
                    "vendor": item.get("vendor", ""),
                    "subject": item.get("subject", ""),
                    "body": item.get("body", ""),
                    "severity_hint": item.get("severity_hint"),
                    "created_at": item.get("created_at"),
                }
            )
        return alerts
    except json.JSONDecodeError as exc:
        logging.error("Failed to parse Gmail sample JSON: %s", exc)
        return []


def day13_ingest_csv_drop(csv_folder: str) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    for csv_file in pathlib.Path(csv_folder).glob("*.csv"):
        with csv_file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                alerts.append(
                    {
                        "source": "csv",
                        "external_id": row.get("txn_id"),
                        "customer_id": row.get("customer_id"),
                        "amount": float(row.get("amount", 0) or 0),
                        "currency": row.get("currency"),
                        "country": row.get("country"),
                        "txn_type": row.get("txn_type"),
                        "risk_score": float(row.get("risk_score", 0) or 0),
                        "created_at": row.get("created_at"),
                        "severity_hint": "high" if float(row.get("risk_score", 0) or 0) >= 80 else "",
                    }
                )
    return alerts


def day13_send_slack(webhook_url: str, message: str, dry_run: bool) -> None:
    if dry_run or not webhook_url:
        logging.info("[DRY-RUN] Slack message: %s", message)
        return
    try:
        import requests

        response = requests.post(webhook_url, json={"text": message}, timeout=5)
        response.raise_for_status()
        logging.info("Sent Slack message")
    except Exception as exc:  # pragma: no cover - best-effort logging
        logging.error("Failed to send Slack message: %s", exc)


def day13_send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    recipients: List[str],
    subject: str,
    body: str,
    dry_run: bool,
) -> None:
    if dry_run or not recipients or not smtp_host:
        logging.info("[DRY-RUN] Email to %s | %s", ",".join(recipients), subject)
        return
    message = MIMEText(body)
    message["From"] = smtp_user
    message["To"] = ",".join(recipients)
    message["Subject"] = subject
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipients, message.as_string())
        logging.info("Sent email to %s", recipients)
    except Exception as exc:  # pragma: no cover - best-effort logging
        logging.error("Failed to send email: %s", exc)


def day13_route_alert(
    severity: str,
    routing_matrix: Dict[str, List[str]],
    config: Dict[str, Any],
    alert: Dict[str, Any],
    dry_run: bool,
) -> List[str]:
    destinations = routing_matrix.get(severity, [])
    routed = []
    message = f"[{severity.upper()}] {alert.get('subject','Txn '+str(alert.get('external_id','')))}"
    for destination in destinations:
        if destination.startswith("slack:"):
            day13_send_slack(config["slack_webhook"], message, dry_run)
            routed.append(destination)
        elif destination.startswith("email:"):
            day13_send_email(
                smtp_host=config["smtp_host"],
                smtp_port=config["smtp_port"],
                smtp_user=config["smtp_user"],
                smtp_password=config["smtp_password"],
                recipients=config["email_recipients"],
                subject=message,
                body=json.dumps(alert, indent=2),
                dry_run=dry_run,
            )
            routed.append(destination)
    return routed


def day13_store_audit(
    conn: sqlite3.Connection,
    alert_hash: str,
    severity: str,
    source: str,
    routed_to: List[str],
    created_at: str,
    triaged_at: datetime.datetime,
    alert_payload: Dict[str, Any],
) -> None:
    created_dt = None
    if created_at:
        try:
            created_dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            created_dt = None
    if created_dt is None:
        created_dt = triaged_at
    sla_seconds = int((triaged_at - created_dt).total_seconds())
    conn.execute(
        """
        INSERT INTO audit_log (
            alert_hash, severity, source, routed_to, created_at_utc,
            triaged_at_utc, sla_seconds, payload
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert_hash,
            severity,
            source,
            ",".join(routed_to),
            created_dt.isoformat().replace("+00:00", "Z"),
            triaged_at.isoformat().replace("+00:00", "Z"),
            sla_seconds,
            json.dumps(alert_payload),
        ),
    )
    conn.commit()


def day13_process_alerts() -> Tuple[int, int]:
    day13_load_env()
    config = day13_default_config()
    day13_setup_logging("day13/logs/day13_execution.log")
    routing_matrix = day13_load_routing_matrix_from_env()
    conn = day13_init_sqlite(config["audit_db_path"])

    ingested = []
    ingested.extend(day13_ingest_gmail_stub(config["gmail_sample_path"]))
    ingested.extend(day13_ingest_csv_drop(config["csv_drop_folder"]))

    processed = 0
    skipped = 0
    for alert in ingested:
        alert_hash = day13_compute_hash(alert)
        if day13_is_duplicate(conn, alert_hash, config["dedup_window_minutes"]):
            skipped += 1
            logging.info("Duplicate detected, skipped: %s", alert_hash[:8])
            continue
        severity = day13_classify_alert(alert)
        routed_to = day13_route_alert(
            severity=severity,
            routing_matrix=routing_matrix,
            config=config,
            alert=alert,
            dry_run=config["dry_run"],
        )
        triaged_at = datetime.datetime.now(datetime.timezone.utc)
        day13_store_audit(
            conn=conn,
            alert_hash=alert_hash,
            severity=severity,
            source=alert.get("source", "unknown"),
            routed_to=routed_to,
            created_at=alert.get("created_at"),
            triaged_at=triaged_at,
            alert_payload=alert,
        )
        day13_record_dedup(conn, alert_hash, alert.get("source", "unknown"))
        processed += 1
        logging.info("Processed %s | severity=%s | routed=%s", alert_hash[:8], severity, routed_to)

    logging.info("Run complete | processed=%s | duplicates_skipped=%s", processed, skipped)
    return processed, skipped


def day13_run_once() -> None:
    day13_process_alerts()


if __name__ == "__main__":
    day13_run_once()
