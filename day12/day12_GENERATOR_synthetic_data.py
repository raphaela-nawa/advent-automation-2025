#!/usr/bin/env python3
"""
Day 12 - Synthetic Security Log Generator
Generates realistic cybersecurity log data for Great Expectations validation testing
Context: Sal (Cybersecurity Analyst) - Security Operations Center logs
"""

import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import json

# Initialize Faker for generating synthetic data
fake = Faker()
Faker.seed(12345)  # For reproducibility
random.seed(12345)

def day12_generate_security_logs(num_records: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic security event logs with realistic patterns

    Includes intentional data quality issues for validation testing:
    - Some null values
    - Some timestamp anomalies
    - Some severity mismatches
    - Some PII that shouldn't be there (for validation)
    """

    # Security event types based on real SOC operations
    EVENT_TYPES = [
        'login_attempt', 'login_success', 'login_failure',
        'privilege_escalation', 'file_access', 'network_connection',
        'suspicious_activity', 'malware_detected', 'data_exfiltration_attempt',
        'firewall_block', 'ids_alert', 'vulnerability_scan'
    ]

    SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']

    SOURCES = [
        'firewall', 'ids', 'endpoint_protection', 'web_gateway',
        'email_gateway', 'authentication_server', 'database_audit',
        'network_monitor', 'dlp_system'
    ]

    ACTIONS = ['allowed', 'blocked', 'quarantined', 'alerted', 'logged']

    records = []
    base_time = datetime.now() - timedelta(days=7)

    for i in range(num_records):
        # Introduce some null values (data quality issue)
        event_id = f"EVT-{i:06d}" if random.random() > 0.01 else None

        # Generate timestamp with occasional anomalies
        if random.random() > 0.02:  # 98% good timestamps
            timestamp = base_time + timedelta(
                seconds=random.randint(0, 7 * 24 * 3600)
            )
        else:  # 2% anomalous timestamps (future or too far past)
            timestamp = datetime.now() + timedelta(days=random.randint(1, 365))

        event_type = random.choice(EVENT_TYPES)
        severity = random.choice(SEVERITIES)
        source = random.choice(SOURCES)
        action = random.choice(ACTIONS)

        # Generate user info (with occasional PII leaks for validation testing)
        if random.random() > 0.05:  # 95% properly anonymized
            username = f"user_{random.randint(1000, 9999)}"
        else:  # 5% contains PII (email addresses - should be flagged)
            username = fake.email()

        # Source IP (mostly internal, some external)
        if random.random() > 0.3:
            source_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        else:
            source_ip = fake.ipv4_public()

        # Destination IP
        dest_ip = fake.ipv4() if random.random() > 0.05 else None

        # Generate event details
        details = {
            'protocol': random.choice(['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']),
            'port': random.choice([22, 80, 443, 3389, 1433, 3306, 8080]),
            'bytes_transferred': random.randint(0, 1000000)
        }

        # Risk score (should correlate with severity)
        if severity == 'critical':
            risk_score = random.randint(90, 100)
        elif severity == 'high':
            risk_score = random.randint(70, 89)
        elif severity == 'medium':
            risk_score = random.randint(40, 69)
        elif severity == 'low':
            risk_score = random.randint(10, 39)
        else:  # info
            risk_score = random.randint(0, 9)

        # Occasionally introduce mismatches (data quality issue)
        if random.random() < 0.03:  # 3% mismatches
            risk_score = random.randint(0, 100)

        # Status field (for completeness checks)
        status = random.choice(['open', 'investigating', 'resolved', 'false_positive'])
        if random.random() < 0.02:  # 2% null status
            status = None

        record = {
            'event_id': event_id,
            'timestamp': timestamp.isoformat(),
            'event_type': event_type,
            'severity': severity,
            'source_system': source,
            'action_taken': action,
            'username': username,
            'source_ip': source_ip,
            'destination_ip': dest_ip,
            'risk_score': risk_score,
            'status': status,
            'details': json.dumps(details)
        }

        records.append(record)

    df = pd.DataFrame(records)

    # Add some derived fields
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

    return df


def day12_generate_compliance_audit_logs(num_records: int = 500) -> pd.DataFrame:
    """
    Generate compliance audit logs for regulatory requirements
    (HIPAA, PCI-DSS, SOX-like scenarios)
    """

    AUDIT_ACTIONS = [
        'data_access', 'data_modification', 'data_deletion',
        'permission_change', 'configuration_change', 'report_generation',
        'backup_completed', 'restore_initiated'
    ]

    SYSTEMS = [
        'patient_db', 'financial_system', 'payment_processor',
        'hr_system', 'backup_system', 'audit_log_system'
    ]

    records = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        timestamp = base_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 3600)
        )

        record = {
            'audit_id': f"AUD-{i:06d}",
            'timestamp': timestamp.isoformat(),
            'action': random.choice(AUDIT_ACTIONS),
            'system': random.choice(SYSTEMS),
            'user_id': f"usr_{random.randint(100, 999)}",
            'session_id': fake.uuid4(),
            'record_count': random.randint(1, 1000),
            'success': random.choice([True, True, True, False]),  # Mostly successful
            'compliance_tag': random.choice(['HIPAA', 'PCI-DSS', 'SOX', 'GDPR', None])
        }

        records.append(record)

    return pd.DataFrame(records)


if __name__ == "__main__":
    print("🔐 Day 12 - Generating Synthetic Security Data...")

    # Generate security event logs
    print("\n📊 Generating security event logs...")
    security_logs = day12_generate_security_logs(1000)
    output_path = "data/day12_security_events.csv"
    security_logs.to_csv(output_path, index=False)
    print(f"✅ Generated {len(security_logs)} security events → {output_path}")

    # Display sample data
    print("\n🔍 Sample security events:")
    print(security_logs.head(10))

    print("\n📈 Data quality summary:")
    print(f"  - Total records: {len(security_logs)}")
    print(f"  - Null event_ids: {security_logs['event_id'].isna().sum()}")
    print(f"  - Null statuses: {security_logs['status'].isna().sum()}")
    print(f"  - Potential PII in usernames: {security_logs['username'].str.contains('@', na=False).sum()}")
    print(f"  - Date range: {security_logs['timestamp'].min()} to {security_logs['timestamp'].max()}")

    # Generate compliance audit logs
    print("\n\n📊 Generating compliance audit logs...")
    audit_logs = day12_generate_compliance_audit_logs(500)
    audit_output_path = "data/day12_compliance_audit.csv"
    audit_logs.to_csv(audit_output_path, index=False)
    print(f"✅ Generated {len(audit_logs)} audit records → {audit_output_path}")

    print("\n✅ Synthetic data generation complete!")
    print("\n⚠️  Data includes intentional quality issues for validation testing:")
    print("   - Missing event IDs (~1%)")
    print("   - Future timestamps (~2%)")
    print("   - PII leakage in usernames (~5%)")
    print("   - Severity/risk score mismatches (~3%)")
    print("   - Null status fields (~2%)")
