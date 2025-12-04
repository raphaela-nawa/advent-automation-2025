#!/usr/bin/env python3
"""
Configuration settings for Day 06: Financial Consulting Metrics Layer

This module centralizes all configuration values for the project.
All variables use day-scoped naming (DAY06_*) to prevent conflicts.
"""

from pathlib import Path

# ============================================================================
# Database Configuration
# ============================================================================

DAY06_DB_PATH = Path(__file__).parent / "data" / "day06_consulting.db"
DAY06_DB_PATH_STR = str(DAY06_DB_PATH)

# ============================================================================
# Synthetic Data Generation Parameters
# ============================================================================

# Number of entities to generate
DAY06_NUM_PROJECTS = 18
DAY06_NUM_CONSULTANTS = 10
DAY06_NUM_CLIENTS = 6
DAY06_MIN_TIMESHEETS_PER_PROJECT = 5
DAY06_MAX_TIMESHEETS_PER_PROJECT = 20
DAY06_MIN_EXPENSES_PER_PROJECT = 1
DAY06_MAX_EXPENSES_PER_PROJECT = 5

# Date ranges for projects
DAY06_PROJECT_START_DATE = "2023-01-01"
DAY06_PROJECT_END_DATE = "2024-06-01"

# Financial parameters
DAY06_MIN_PROJECT_BUDGET = 50000
DAY06_MAX_PROJECT_BUDGET = 500000
DAY06_MIN_HOURLY_RATE = 100
DAY06_MAX_HOURLY_RATE = 250
DAY06_MIN_EXPENSE_AMOUNT = 100
DAY06_MAX_EXPENSE_AMOUNT = 15000

# Business logic parameters
DAY06_BILLABLE_PERCENTAGE = 0.75  # 75% of hours should be billable on average
DAY06_REIMBURSABLE_PERCENTAGE = 0.60  # 60% of expenses are reimbursable

# ============================================================================
# Consultant Performance Tiers
# ============================================================================

# Define different utilization profiles for realistic data
DAY06_CONSULTANT_TIERS = {
    "high_performer": {
        "count": 3,
        "billable_rate": (0.80, 0.85),  # 80-85% billable
        "hourly_rate_range": (180, 250)
    },
    "average": {
        "count": 5,
        "billable_rate": (0.60, 0.70),  # 60-70% billable
        "hourly_rate_range": (130, 180)
    },
    "below_target": {
        "count": 2,
        "billable_rate": (0.40, 0.50),  # 40-50% billable
        "hourly_rate_range": (100, 130)
    }
}

# ============================================================================
# Project Types
# ============================================================================

DAY06_PROJECT_NAMES = [
    "Marketing Strategy Overhaul",
    "Digital Transformation Roadmap",
    "Brand Positioning Study",
    "Customer Experience Enhancement",
    "Market Entry Strategy",
    "Competitive Analysis Deep Dive",
    "Product Launch Campaign",
    "Sales Process Optimization",
    "Channel Partner Strategy",
    "Content Marketing Framework",
    "Social Media Presence Build",
    "Customer Segmentation Analysis",
    "Pricing Strategy Review",
    "Growth Hacking Initiative",
    "Marketing Automation Setup",
    "Lead Generation System",
    "Conversion Rate Optimization",
    "Marketing Analytics Dashboard",
    "Influencer Marketing Campaign",
    "Email Marketing Revamp"
]

DAY06_CONTRACT_TYPES = ["Fixed Price", "Time & Materials"]
DAY06_PROJECT_STATUSES = ["Active", "Completed", "On Hold"]

# ============================================================================
# Expense Types
# ============================================================================

DAY06_EXPENSE_TYPES = [
    "Travel",
    "Software Licenses",
    "Subcontractor",
    "Marketing",
    "Office Supplies"
]

# ============================================================================
# Task Descriptions (for timesheets)
# ============================================================================

DAY06_TASK_DESCRIPTIONS = [
    "Client workshop facilitation",
    "Data analysis and insights",
    "Report writing and documentation",
    "Stakeholder interviews",
    "Market research",
    "Strategy development",
    "Presentation preparation",
    "Project management",
    "Internal review and QA",
    "Training and knowledge transfer",
    "Team collaboration meeting",
    "Proposal development",
    "Risk assessment",
    "Performance tracking",
    "Client status call"
]

# ============================================================================
# Metric Thresholds
# ============================================================================

# Utilization rate categories
DAY06_UTILIZATION_HIGH = 80  # % - High performer threshold
DAY06_UTILIZATION_AVERAGE = 60  # % - Average performer threshold

# Profit margin categories
DAY06_MARGIN_HIGH = 30  # % - High margin threshold
DAY06_MARGIN_HEALTHY = 15  # % - Healthy margin threshold

# Client ROI categories
DAY06_CLIENT_ROI_STRATEGIC = 200  # % - Strategic partner threshold
DAY06_CLIENT_ROI_HIGH = 100  # % - High value threshold
DAY06_CLIENT_ROI_STANDARD = 50  # % - Standard threshold

# Budget burn alert thresholds
DAY06_BUDGET_CRITICAL = 90  # % - Critical alert
DAY06_BUDGET_WARNING = 75  # % - Warning alert
DAY06_BUDGET_WATCH = 50  # % - Watch alert

# ============================================================================
# Display Configuration
# ============================================================================

DAY06_CURRENCY_SYMBOL = "$"
DAY06_CURRENCY_FORMAT = "{symbol}{amount:,.2f}"
DAY06_PERCENTAGE_FORMAT = "{value:.2f}%"

# ============================================================================
# Validation Rules
# ============================================================================

DAY06_MIN_HOURS_PER_DAY = 2
DAY06_MAX_HOURS_PER_DAY = 10
DAY06_MIN_PROJECT_DURATION_DAYS = 30
DAY06_MAX_PROJECT_DURATION_DAYS = 180


def day06_format_currency(amount: float) -> str:
    """
    Format currency value with proper symbol and decimals.

    Args:
        amount: Numeric amount in USD

    Returns:
        Formatted currency string (e.g., "$1,234.56")
    """
    return DAY06_CURRENCY_FORMAT.format(
        symbol=DAY06_CURRENCY_SYMBOL,
        amount=amount
    )


def day06_format_percentage(value: float) -> str:
    """
    Format percentage value with 2 decimal places.

    Args:
        value: Numeric percentage value

    Returns:
        Formatted percentage string (e.g., "75.50%")
    """
    return DAY06_PERCENTAGE_FORMAT.format(value=value)


def day06_validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that end_date is after start_date.

    Args:
        start_date: ISO format date string (YYYY-MM-DD)
        end_date: ISO format date string (YYYY-MM-DD)

    Returns:
        True if valid, False otherwise
    """
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return end > start
    except (ValueError, TypeError):
        return False


# ============================================================================
# Export Configuration Summary
# ============================================================================

def day06_print_config_summary():
    """Print configuration summary for verification."""
    print("="*60)
    print("Day 06 Configuration Summary")
    print("="*60)
    print(f"Database: {DAY06_DB_PATH}")
    print(f"\nData Generation:")
    print(f"  - Projects: {DAY06_NUM_PROJECTS}")
    print(f"  - Consultants: {DAY06_NUM_CONSULTANTS}")
    print(f"  - Clients: {DAY06_NUM_CLIENTS}")
    print(f"\nFinancial Parameters:")
    print(f"  - Project Budget: {day06_format_currency(DAY06_MIN_PROJECT_BUDGET)} - {day06_format_currency(DAY06_MAX_PROJECT_BUDGET)}")
    print(f"  - Hourly Rate: {day06_format_currency(DAY06_MIN_HOURLY_RATE)} - {day06_format_currency(DAY06_MAX_HOURLY_RATE)}")
    print(f"\nMetric Thresholds:")
    print(f"  - High Utilization: ≥{DAY06_UTILIZATION_HIGH}%")
    print(f"  - High Margin: ≥{DAY06_MARGIN_HIGH}%")
    print(f"  - Strategic Client ROI: ≥{DAY06_CLIENT_ROI_STRATEGIC}%")
    print("="*60)


if __name__ == "__main__":
    # Print configuration when run directly
    day06_print_config_summary()
