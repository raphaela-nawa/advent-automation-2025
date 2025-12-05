#!/usr/bin/env python3
"""
Configuration Settings for Day 07: Hospitality LTV & Cohort Model

This module contains all configuration variables for Carol's pousada
hospitality analytics project. All variables use the DAY07_ prefix
for project isolation.

Business Context:
- Boutique pousada in Campos do Jordão, São Paulo, Brazil
- Mountain resort targeting weekend couples and family vacations
- Peak seasons: Winter (Jun-Aug) and Summer holidays (Dec-Jan)
"""

import os
from pathlib import Path

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Primary database path for hospitality data
DAY07_DB_PATH = os.getenv(
    "DAY07_DB_PATH",
    str(Path(__file__).parent / "data" / "day07_hospitality.db")
)

# =============================================================================
# BUSINESS RULES & METRICS
# =============================================================================

# Cohort Analysis Parameters
DAY07_COHORT_START_DATE = "2022-06-01"  # First cohort month
DAY07_COHORT_END_DATE = "2024-12-31"    # Last cohort month
DAY07_COHORT_ANALYSIS_MONTHS = [1, 3, 6, 12]  # Retention analysis periods

# LTV (Lifetime Value) Thresholds
DAY07_LTV_VIP_THRESHOLD = 4000.0        # BRL - Guests above this are VIP
DAY07_LTV_HIGH_VALUE_THRESHOLD = 2500.0  # BRL - High value segment
DAY07_LTV_AVERAGE_THRESHOLD = 1200.0     # BRL - Average guest

# Retention Targets (percentage of cohort)
DAY07_RETENTION_TARGET_1M = 0.15   # 15% return within 1 month
DAY07_RETENTION_TARGET_3M = 0.25   # 25% return within 3 months
DAY07_RETENTION_TARGET_6M = 0.35   # 35% return within 6 months
DAY07_RETENTION_TARGET_12M = 0.40  # 40% return within 12 months

# =============================================================================
# PRICING CONFIGURATION
# =============================================================================

# Room Type Base Prices (BRL per night, low season)
DAY07_ROOM_PRICES = {
    "Standard": {"low": 350, "high": 490},
    "Deluxe": {"low": 650, "high": 910},
    "Suite": {"low": 1000, "high": 1400},
    "Family Room": {"low": 850, "high": 1190}
}

# Seasonal multiplier
DAY07_HIGH_SEASON_MULTIPLIER = 1.40  # 40% increase in high season

# High season months (Jun-Aug winter, Dec-Jan summer in Brazil)
DAY07_HIGH_SEASON_MONTHS = [6, 7, 8, 12, 1]

# =============================================================================
# OPERATIONAL PARAMETERS
# =============================================================================

# Check-in/Check-out times
DAY07_CHECK_IN_HOUR_MIN = 14   # 2 PM earliest
DAY07_CHECK_IN_HOUR_MAX = 20   # 8 PM latest
DAY07_CHECK_OUT_HOUR_MIN = 8   # 8 AM earliest
DAY07_CHECK_OUT_HOUR_MAX = 12  # 12 PM latest

# Average stay duration (nights)
DAY07_AVG_STAY_DURATION = 2.5
DAY07_MIN_STAY_DURATION = 1
DAY07_MAX_STAY_DURATION = 7

# Guest distribution
DAY07_GUEST_TYPE_DISTRIBUTION = {
    "Couple": 0.45,
    "Family": 0.30,
    "Individual": 0.15,
    "Business": 0.10
}

# =============================================================================
# BOOKING SOURCES & COMMISSIONS
# =============================================================================

DAY07_BOOKING_SOURCES = {
    "Booking.com": {"weight": 0.50, "commission": 0.15},
    "Direct Website": {"weight": 0.30, "commission": 0.00},
    "Airbnb": {"weight": 0.15, "commission": 0.12},
    "Phone": {"weight": 0.05, "commission": 0.00}
}

# =============================================================================
# DATA QUALITY & VALIDATION
# =============================================================================

# Expected ranges for validation
DAY07_MIN_TOTAL_BOOKINGS = 400
DAY07_MAX_TOTAL_BOOKINGS = 600
DAY07_MIN_UNIQUE_GUESTS = 150
DAY07_MAX_UNIQUE_GUESTS = 200

DAY07_EXPECTED_CANCELLATION_RATE = 0.10  # 10%
DAY07_EXPECTED_REPEAT_GUEST_RATE = 0.30  # 30%

# =============================================================================
# SQL MODEL PATHS
# =============================================================================

DAY07_MODEL_DIR = Path(__file__).parent / "models"
DAY07_QUERY_DIR = Path(__file__).parent / "queries"

DAY07_MODEL_COHORTS = DAY07_MODEL_DIR / "day07_MODEL_cohorts.sql"
DAY07_MODEL_LTV = DAY07_MODEL_DIR / "day07_MODEL_ltv.sql"
DAY07_MODEL_RETENTION = DAY07_MODEL_DIR / "day07_MODEL_retention.sql"

# =============================================================================
# EXPORT & VISUALIZATION
# =============================================================================

# Output formats for Looker Studio / BI tools
DAY07_EXPORT_DIR = Path(__file__).parent / "exports"
DAY07_EXPORT_FORMATS = ["csv", "json"]

# Date format for exports
DAY07_DATE_FORMAT = "%Y-%m-%d"
DAY07_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def day07_get_season(month: int) -> str:
    """
    Determine if a month is high or low season.

    Args:
        month: Month number (1-12)

    Returns:
        "high" or "low"
    """
    return "high" if month in DAY07_HIGH_SEASON_MONTHS else "low"


def day07_calculate_room_price(room_type: str, month: int) -> float:
    """
    Calculate room price based on type and season.

    Args:
        room_type: Room type (Standard, Deluxe, Suite, Family Room)
        month: Month number (1-12)

    Returns:
        Price in BRL
    """
    if room_type not in DAY07_ROOM_PRICES:
        raise ValueError(f"Invalid room type: {room_type}")

    season = day07_get_season(month)
    return DAY07_ROOM_PRICES[room_type][season]


def day07_classify_guest_value(ltv: float) -> str:
    """
    Classify guest based on their LTV.

    Args:
        ltv: Lifetime value in BRL

    Returns:
        Guest segment: VIP, High Value, Average, or Low Value
    """
    if ltv >= DAY07_LTV_VIP_THRESHOLD:
        return "VIP"
    elif ltv >= DAY07_LTV_HIGH_VALUE_THRESHOLD:
        return "High Value"
    elif ltv >= DAY07_LTV_AVERAGE_THRESHOLD:
        return "Average"
    else:
        return "Low Value"


def day07_get_booking_commission(source: str) -> float:
    """
    Get commission rate for booking source.

    Args:
        source: Booking source name

    Returns:
        Commission rate (0.0 to 1.0)
    """
    if source not in DAY07_BOOKING_SOURCES:
        return 0.0
    return DAY07_BOOKING_SOURCES[source]["commission"]


# =============================================================================
# ENVIRONMENT VALIDATION
# =============================================================================

def day07_validate_config() -> bool:
    """
    Validate that all required configuration is set correctly.

    Returns:
        True if valid, raises ValueError otherwise
    """
    # Check database path is writable
    db_dir = Path(DAY07_DB_PATH).parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

    # Validate retention periods are in ascending order
    retention_months = DAY07_COHORT_ANALYSIS_MONTHS
    if retention_months != sorted(retention_months):
        raise ValueError("Cohort analysis months must be in ascending order")

    # Validate LTV thresholds
    if not (DAY07_LTV_AVERAGE_THRESHOLD < DAY07_LTV_HIGH_VALUE_THRESHOLD < DAY07_LTV_VIP_THRESHOLD):
        raise ValueError("LTV thresholds must be in ascending order")

    # Validate booking source weights sum to 1.0
    total_weight = sum(source["weight"] for source in DAY07_BOOKING_SOURCES.values())
    if not 0.99 <= total_weight <= 1.01:  # Allow small floating point errors
        raise ValueError(f"Booking source weights must sum to 1.0, got {total_weight}")

    return True


if __name__ == "__main__":
    """Test configuration when run directly"""
    print("Day 07 Configuration Settings")
    print("=" * 50)
    print(f"Database Path: {DAY07_DB_PATH}")
    print(f"Cohort Period: {DAY07_COHORT_START_DATE} to {DAY07_COHORT_END_DATE}")
    print(f"VIP LTV Threshold: R$ {DAY07_LTV_VIP_THRESHOLD:,.2f}")
    print(f"High Season Months: {DAY07_HIGH_SEASON_MONTHS}")
    print(f"Retention Targets: {DAY07_COHORT_ANALYSIS_MONTHS} months")
    print("\nRoom Prices (Low/High Season):")
    for room_type, prices in DAY07_ROOM_PRICES.items():
        print(f"  {room_type}: R$ {prices['low']:.2f} / R$ {prices['high']:.2f}")
    print("\nBooking Sources & Commissions:")
    for source, config in DAY07_BOOKING_SOURCES.items():
        print(f"  {source}: {config['weight']*100:.0f}% (commission: {config['commission']*100:.0f}%)")
    print("\nValidating configuration...")
    try:
        day07_validate_config()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
