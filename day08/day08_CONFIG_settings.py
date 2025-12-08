"""
Day 08 - SaaS Growth Funnel & Cohort Analysis
Configuration Settings for Patrick's Growth Strategy Project
"""

from pathlib import Path

# Database Configuration
DAY08_DB_PATH = str(Path(__file__).parent / "data" / "day08_saas_funnel.db")

# Data Generation Parameters
DAY08_NUM_USERS = 10000
DAY08_NUM_EVENTS = 100000

# Funnel Configuration
DAY08_FUNNEL_STAGES = ['visit', 'signup', 'activated', 'paid']
DAY08_ACTIVATION_THRESHOLD_DAYS = 7  # Days to become activated after signup

# Marketing Attribution
DAY08_UTM_SOURCES = [
    'google',
    'facebook',
    'linkedin',
    'twitter',
    'organic',
    'referral'
]

DAY08_UTM_CAMPAIGNS = [
    'summer_2024',
    'product_launch',
    'webinar',
    'content_marketing',
    'retargeting'
]

# Product Features
DAY08_FEATURE_NAMES = [
    'dashboard',
    'reports',
    'integrations',
    'api',
    'mobile_app',
    'export'
]

# Subscription Plans
DAY08_PLAN_TIERS = {
    'Starter': 29.0,
    'Pro': 99.0,
    'Enterprise': 299.0
}

# Cohort Analysis Configuration
DAY08_COHORT_PERIODS = [1, 3, 6, 12]  # Months to analyze

# Engagement Metrics Thresholds
DAY08_DAU_THRESHOLD = 1  # Events per day to count as DAU
DAY08_WAU_THRESHOLD = 3  # Events per week to count as WAU
DAY08_MAU_THRESHOLD = 5  # Events per month to count as MAU

# Health Score Weights
DAY08_HEALTH_WEIGHTS = {
    'engagement_score': 0.4,
    'feature_adoption_score': 0.3,
    'retention_score': 0.3
}

# dbt Configuration
DAY08_DBT_PROJECT_NAME = 'day08_saas_funnel'
DAY08_DBT_PROFILE_NAME = 'day08_funnel'
DAY08_DBT_TARGET = 'dev'
