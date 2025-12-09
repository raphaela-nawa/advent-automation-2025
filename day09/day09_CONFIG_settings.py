"""
Day 09 Configuration Settings
Property Manager Operations Data Warehouse

Configuration for Jo's multi-platform property management data warehouse.
Supports Airbnb + Booking.com unified analytics.
"""

import os
from pathlib import Path

# Project Paths
DAY09_PROJECT_ROOT = Path(__file__).parent
DAY09_DATA_DIR = DAY09_PROJECT_ROOT / "data"
DAY09_MODELS_DIR = DAY09_PROJECT_ROOT / "models"

# Database Configuration
DAY09_DB_NAME = "day09_property_operations.db"
DAY09_DB_PATH = DAY09_DATA_DIR / DAY09_DB_NAME

# Property Configuration (Jo's 6 houseboats)
DAY09_PROPERTIES = [
    {"id": "HB001", "name": "Floating Paradise", "capacity": 4, "base_price": 180},
    {"id": "HB002", "name": "Lakeside Haven", "capacity": 6, "base_price": 220},
    {"id": "HB003", "name": "Water's Edge Retreat", "capacity": 2, "base_price": 150},
    {"id": "HB004", "name": "Sunset Marina", "capacity": 8, "base_price": 280},
    {"id": "HB005", "name": "Harbor View", "capacity": 4, "base_price": 190},
    {"id": "HB006", "name": "Bay Breeze", "capacity": 6, "base_price": 210},
]

# Platform Configuration
DAY09_PLATFORMS = ["airbnb", "booking_com"]

# Platform Commission Rates
DAY09_PLATFORM_FEES = {
    "airbnb": 0.15,  # 15% host service fee
    "booking_com": 0.18,  # 18% commission
}

# Funnel Stages
DAY09_FUNNEL_STAGES = ["inquiry", "booking", "check_in", "check_out", "review"]

# Conversion Rates (realistic for hospitality)
DAY09_CONVERSION_RATES = {
    "inquiry_to_booking": 0.25,  # 25% of inquiries become bookings
    "booking_to_check_in": 0.92,  # 92% show up (8% cancellation/no-show)
    "check_in_to_check_out": 0.98,  # 98% complete stay
    "check_out_to_review": 0.35,  # 35% leave reviews
}

# Data Generation Settings
DAY09_NUM_MONTHS = 12
DAY09_NUM_INQUIRIES = 500  # Total inquiries across all properties
DAY09_RANDOM_SEED = 42

# Date Range
DAY09_START_DATE = "2024-01-01"
DAY09_END_DATE = "2024-12-31"

# Occupancy Targets (for realistic data generation)
DAY09_TARGET_OCCUPANCY = {
    "HB001": 0.72,  # 72% occupancy
    "HB002": 0.68,
    "HB003": 0.75,
    "HB004": 0.65,
    "HB005": 0.70,
    "HB006": 0.73,
}

# Review Ratings (1-5 stars)
DAY09_AVG_RATING = 4.5
DAY09_RATING_STDDEV = 0.6


def day09_get_db_url():
    """Get database URL for dbt profiles"""
    return f"sqlite:///{DAY09_DB_PATH}"


def day09_ensure_data_dir():
    """Ensure data directory exists"""
    DAY09_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DAY09_DATA_DIR


if __name__ == "__main__":
    print("Day 09 Configuration")
    print("=" * 50)
    print(f"Database Path: {DAY09_DB_PATH}")
    print(f"Properties: {len(DAY09_PROPERTIES)}")
    print(f"Platforms: {', '.join(DAY09_PLATFORMS)}")
    print(f"Date Range: {DAY09_START_DATE} to {DAY09_END_DATE}")
