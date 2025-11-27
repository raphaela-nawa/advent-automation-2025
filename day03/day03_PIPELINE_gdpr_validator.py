"""
Day 03 - GDPR Lead Validation Pipeline
Validates lead data and calculates retention dates based on GDPR requirements.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import re

from day03_CONFIG_settings import (
    DAY03_REQUIRED_FIELDS,
    DAY03_VALID_CONSENT_PURPOSES,
    DAY03_GDPR_RETENTION_DAYS
)


class day03_GDPRValidator:
    """Validates lead data for GDPR compliance."""

    def __init__(self):
        self.required_fields = DAY03_REQUIRED_FIELDS
        self.valid_purposes = DAY03_VALID_CONSENT_PURPOSES
        self.retention_days = DAY03_GDPR_RETENTION_DAYS

    def validate_lead(self, payload: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validates a lead payload for GDPR compliance.

        Args:
            payload: Dictionary containing lead data

        Returns:
            Tuple of (is_valid, error_message, processed_lead)
        """
        # Check required fields
        missing_fields = [field for field in self.required_fields if field not in payload]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}", None

        # Validate email format
        if not self._is_valid_email(payload.get("email", "")):
            return False, "Invalid email format", None

        # Validate consent purpose
        consent_purpose = payload.get("consent_purpose", "")
        if consent_purpose not in self.valid_purposes:
            return False, f"Invalid consent purpose. Must be one of: {', '.join(self.valid_purposes)}", None

        # Validate timestamp format
        try:
            consent_timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, "Invalid timestamp format. Use ISO 8601 format (e.g., 2024-11-26T10:30:00Z)", None

        # Process the lead
        processed_lead = self._process_lead(payload, consent_timestamp)

        return True, None, processed_lead

    def _is_valid_email(self, email: str) -> bool:
        """Validates email format using regex."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def _process_lead(self, payload: Dict, consent_timestamp: datetime) -> Dict:
        """
        Processes a valid lead and adds metadata.

        Args:
            payload: Original payload
            consent_timestamp: Parsed timestamp

        Returns:
            Processed lead with metadata
        """
        lead_id = str(uuid.uuid4())
        consent_given = payload.get("consent_given", False)

        # Calculate retention date
        retention_date = day03_calculate_retention_date(
            consent_timestamp,
            consent_given,
            self.retention_days
        )

        processed_lead = {
            "lead_id": lead_id,
            "name": payload["name"],
            "email": payload["email"],
            "consent_timestamp": consent_timestamp.isoformat(),
            "consent_purpose": payload["consent_purpose"],
            "ip_address": payload.get("ip_address", "unknown"),
            "data_retention_date": retention_date.isoformat(),
            "consent_given": consent_given,
            "created_at": datetime.utcnow().isoformat()
        }

        return processed_lead


def day03_calculate_retention_date(
    consent_timestamp: datetime,
    consent_given: bool,
    retention_days: int = DAY03_GDPR_RETENTION_DAYS
) -> datetime:
    """
    Calculates GDPR data retention date.

    For leads without consent: retention_date = consent_timestamp + retention_days
    For leads with consent: retention_date = consent_timestamp + 1 year (365 days)

    Args:
        consent_timestamp: When the consent was recorded
        consent_given: Whether consent was given
        retention_days: Number of days for non-consented data (default: 30)

    Returns:
        Retention date as datetime
    """
    if consent_given:
        # With consent, keep data for 1 year
        return consent_timestamp + timedelta(days=365)
    else:
        # Without consent, keep data for retention_days only
        return consent_timestamp + timedelta(days=retention_days)


def day03_format_lead_for_bigquery(lead: Dict) -> Dict:
    """
    Formats a processed lead for BigQuery insertion.

    Args:
        lead: Processed lead dictionary

    Returns:
        BigQuery-compatible lead dictionary
    """
    return {
        "lead_id": lead["lead_id"],
        "name": lead["name"],
        "email": lead["email"],
        "consent_timestamp": lead["consent_timestamp"],
        "consent_purpose": lead["consent_purpose"],
        "ip_address": lead["ip_address"],
        "data_retention_date": lead["data_retention_date"].split("T")[0],  # Extract date only
        "consent_given": lead["consent_given"],
        "created_at": lead["created_at"]
    }
