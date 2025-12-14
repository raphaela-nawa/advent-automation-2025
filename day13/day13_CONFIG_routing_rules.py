"""
day13_CONFIG_routing_rules.py

Defines routing and classification helpers for Day 13 Alert Triage.
"""

import os
from typing import Dict, List


def day13_default_routing_matrix() -> Dict[str, List[str]]:
    """
    Returns default routing destinations per severity.
    Destinations are tokens understood by the router (e.g., slack:channel, email:list).
    """
    return {
        "critical": ["slack:compliance-critical", "email:compliance-leads"],
        "high": ["slack:compliance-high", "email:compliance"],
        "medium": ["slack:compliance-info"],
        "low": ["email:archive"],
    }


def day13_load_routing_matrix_from_env() -> Dict[str, List[str]]:
    """
    Parse environment-provided routing destinations. Values are comma-separated tokens.
    Example: DAY13_ROUTING_CRITICAL="slack:crit,email:leads"
    """
    matrix = day13_default_routing_matrix()
    env_overrides = {
        "critical": os.getenv("DAY13_ROUTING_CRITICAL"),
        "high": os.getenv("DAY13_ROUTING_HIGH"),
        "medium": os.getenv("DAY13_ROUTING_MEDIUM"),
        "low": os.getenv("DAY13_ROUTING_LOW"),
    }
    for severity, value in env_overrides.items():
        if value:
            destinations = [dest.strip() for dest in value.split(",") if dest.strip()]
            if destinations:
                matrix[severity] = destinations
    return matrix
