#!/usr/bin/env python3
"""
Configuration settings for Day 06: SaaS Health Metrics Foundation

This module centralizes all configuration values for the SaaS metrics project.
All variables use day-scoped naming (DAY06_*) to prevent conflicts.

Stakeholder: Murilo (Simetryk SaaS)
Use Case: MRR tracking, churn analysis, cohort retention, customer health scoring
"""

from pathlib import Path
from datetime import datetime

# ============================================================================
# Database Configuration
# ============================================================================

DAY06_DB_PATH = Path(__file__).parent / "data" / "day06_saas_metrics.db"
DAY06_DB_PATH_STR = str(DAY06_DB_PATH)

# ============================================================================
# Synthetic Data Generation Parameters
# ============================================================================

# Number of customers to generate
DAY06_NUM_CUSTOMERS = 500

# Time range for data generation
DAY06_NUM_MONTHS = 24
DAY06_START_DATE = datetime(2023, 1, 1)
DAY06_END_DATE = datetime(2024, 12, 31)

# ============================================================================
# SaaS Plan Tiers and Pricing
# ============================================================================

DAY06_PLAN_TIERS = ['Starter', 'Pro', 'Enterprise']

# MRR ranges for each plan tier (min, max)
DAY06_PLAN_PRICING = {
    'Starter': (29, 99),
    'Pro': (199, 499),
    'Enterprise': (999, 2999)
}

# Distribution of customers across plan tiers
DAY06_PLAN_DISTRIBUTION = {
    'Starter': 0.50,      # 50% of customers
    'Pro': 0.35,          # 35% of customers
    'Enterprise': 0.15    # 15% of customers
}

# ============================================================================
# SaaS Metrics - Business Logic Parameters
# ============================================================================

# Churn and Retention
DAY06_MONTHLY_CHURN_RATE = 0.06  # 6% monthly churn rate (realistic SaaS benchmark)

# Retention curve targets (by months since signup)
DAY06_RETENTION_CURVE = {
    0: 1.00,   # Month 0: 100% retention (signup)
    1: 0.92,   # Month 1: 92% retention
    3: 0.82,   # Month 3: 82% retention
    6: 0.72,   # Month 6: 72% retention
    12: 0.62,  # Month 12: 62% retention
    24: 0.52   # Month 24: 52% retention
}

# Upgrade and Downgrade probabilities
DAY06_UPGRADE_PROBABILITY = 0.18    # 18% of customers upgrade
DAY06_DOWNGRADE_PROBABILITY = 0.08  # 8% of customers downgrade

# ============================================================================
# MRR Growth Targets
# ============================================================================

DAY06_STARTING_MRR = 50000   # Starting MRR in month 1: $50K
DAY06_ENDING_MRR = 200000    # Target MRR in month 24: $200K (4x growth)

# ============================================================================
# Customer Health Scoring
# ============================================================================

# Customer Acquisition Cost (CAC) assumption
DAY06_DEFAULT_CAC = 500.0  # $500 per customer

# LTV/CAC ratio thresholds for health scoring
DAY06_HEALTH_THRESHOLDS = {
    'Healthy': 3.0,      # LTV/CAC > 3 = Healthy
    'At Risk': 1.0,      # LTV/CAC > 1 = At Risk
    'Critical': 0.0      # LTV/CAC <= 1 = Critical
}

# ============================================================================
# Data Generation Helpers
# ============================================================================

# Customer ID format (Stripe-style)
DAY06_CUSTOMER_ID_PREFIX = "cus_"
DAY06_CUSTOMER_ID_LENGTH = 16

# Subscription ID format (Stripe-style)
DAY06_SUBSCRIPTION_ID_PREFIX = "sub_"
DAY06_SUBSCRIPTION_ID_LENGTH = 16

# Email domains for synthetic data
DAY06_EMAIL_DOMAINS = [
    'gmail.com',
    'yahoo.com',
    'outlook.com',
    'techcorp.com',
    'startup.io',
    'enterprise.com',
    'business.net',
    'company.org'
]

# First names for synthetic customers
DAY06_FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa',
    'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Thomas',
    'Linda', 'Charles', 'Elizabeth', 'Daniel', 'Barbara', 'Matthew', 'Susan',
    'Anthony', 'Jessica', 'Mark', 'Karen', 'Donald', 'Nancy', 'Steven', 'Betty'
]

# Last names for synthetic customers
DAY06_LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
    'Ramirez', 'Lewis', 'Robinson'
]

# ============================================================================
# Random Seed for Reproducibility
# ============================================================================

DAY06_RANDOM_SEED = 42  # For consistent data generation across runs

# ============================================================================
# SQL Model Paths
# ============================================================================

DAY06_MODEL_BASE_TABLES = Path(__file__).parent / "models" / "day06_MODEL_base_tables.sql"
DAY06_MODEL_VIEWS = Path(__file__).parent / "models" / "day06_MODEL_views.sql"

# ============================================================================
# Query Paths
# ============================================================================

DAY06_QUERIES_DIR = Path(__file__).parent / "queries"
DAY06_QUERY_MRR_WATERFALL = DAY06_QUERIES_DIR / "day06_QUERY_mrr_waterfall.sql"
DAY06_QUERY_CHURN_ANALYSIS = DAY06_QUERIES_DIR / "day06_QUERY_churn_analysis.sql"
DAY06_QUERY_RETENTION = DAY06_QUERIES_DIR / "day06_QUERY_retention.sql"
DAY06_QUERY_CUSTOMER_HEALTH = DAY06_QUERIES_DIR / "day06_QUERY_customer_health.sql"

# ============================================================================
# Dashboard Integration (Day 19)
# ============================================================================

DAY06_DASHBOARD_VIEWS = [
    'day06_mrr_summary',        # MRR Waterfall Chart
    'day06_churn_by_cohort',    # Churn Heatmap
    'day06_retention_curves',   # Retention Line Chart
    'day06_customer_health'     # Health Score Distribution
]

# ============================================================================
# Validation Thresholds
# ============================================================================

# Data integrity checks
DAY06_MIN_SUBSCRIPTIONS_PER_CUSTOMER = 1
DAY06_MAX_SUBSCRIPTIONS_PER_CUSTOMER = 5  # Most customers have 1-2, some have up to 5

DAY06_MIN_ACTIVE_CUSTOMERS_PERCENT = 0.50  # At least 50% should be active
DAY06_MAX_ACTIVE_CUSTOMERS_PERCENT = 0.80  # At most 80% should be active

# MRR validation
DAY06_MIN_TOTAL_MRR = 100000   # Minimum total MRR across all time
DAY06_MAX_TOTAL_MRR = 5000000  # Maximum total MRR across all time

# ============================================================================
# Logging Configuration
# ============================================================================

DAY06_LOG_LEVEL = "INFO"
DAY06_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Helper Functions
# ============================================================================

def day06_get_plan_mrr_range(plan_tier: str) -> tuple:
    """
    Get the MRR range (min, max) for a given plan tier.

    Args:
        plan_tier: One of 'Starter', 'Pro', 'Enterprise'

    Returns:
        Tuple of (min_mrr, max_mrr)
    """
    if plan_tier not in DAY06_PLAN_PRICING:
        raise ValueError(f"Invalid plan tier: {plan_tier}")
    return DAY06_PLAN_PRICING[plan_tier]


def day06_get_health_status(ltv_cac_ratio: float) -> str:
    """
    Determine customer health status based on LTV/CAC ratio.

    Args:
        ltv_cac_ratio: Lifetime Value / Customer Acquisition Cost ratio

    Returns:
        One of 'Healthy', 'At Risk', 'Critical', 'Churned'
    """
    if ltv_cac_ratio > DAY06_HEALTH_THRESHOLDS['Healthy']:
        return 'Healthy'
    elif ltv_cac_ratio > DAY06_HEALTH_THRESHOLDS['At Risk']:
        return 'At Risk'
    else:
        return 'Critical'


def day06_validate_date_range(date_obj: datetime) -> bool:
    """
    Validate that a date is within the valid range for this project.

    Args:
        date_obj: datetime object to validate

    Returns:
        True if valid, False otherwise
    """
    return DAY06_START_DATE <= date_obj <= DAY06_END_DATE


if __name__ == "__main__":
    print("Day 06: SaaS Health Metrics Foundation - Configuration")
    print("=" * 60)
    print(f"Database Path: {DAY06_DB_PATH}")
    print(f"Number of Customers: {DAY06_NUM_CUSTOMERS}")
    print(f"Date Range: {DAY06_START_DATE.date()} to {DAY06_END_DATE.date()}")
    print(f"Plan Tiers: {', '.join(DAY06_PLAN_TIERS)}")
    print(f"Monthly Churn Rate: {DAY06_MONTHLY_CHURN_RATE * 100:.1f}%")
    print(f"Target MRR Growth: ${DAY06_STARTING_MRR:,} → ${DAY06_ENDING_MRR:,}")
    print("=" * 60)