"""
Day 01 Configuration Settings
GA4 + Google Ads → BigQuery Pipeline

This file contains all configuration constants and schemas for Day 01.
All variables are prefixed with day01_ to prevent cross-contamination.
"""

import os
from dotenv import load_dotenv

# Load environment variables from root config/.env
load_dotenv('../config/.env')

# ============================================================================
# BigQuery Configuration
# ============================================================================
day01_GCP_PROJECT_ID = os.getenv('DAY01_GCP_PROJECT_ID', 'your-project-id')
day01_BQ_DATASET = os.getenv('DAY01_BQ_DATASET', 'marketing_data')
day01_BQ_LOCATION = os.getenv('DAY01_BQ_LOCATION', 'US')

# Table names
day01_GA4_TABLE = 'ga4_sessions'
day01_ADS_TABLE = 'google_ads_campaigns'

# ============================================================================
# GA4 Configuration
# ============================================================================
day01_GA4_PROPERTY_ID = os.getenv('DAY01_GA4_PROPERTY_ID', '213025502')  # Google Merchandise Store Demo
day01_GA4_CREDENTIALS_PATH = os.getenv('DAY01_GA4_CREDENTIALS_PATH', './credentials/ga4_service_account.json')

# ============================================================================
# Feature Flags
# ============================================================================
day01_USE_SYNTHETIC_DATA = os.getenv('DAY01_USE_SYNTHETIC_DATA', 'true').lower() == 'true'
day01_SYNTHETIC_DAYS = int(os.getenv('DAY01_SYNTHETIC_DAYS', '30'))
day01_NUM_CAMPAIGNS = int(os.getenv('DAY01_NUM_CAMPAIGNS', '4'))

# ============================================================================
# BigQuery Schemas
# ============================================================================
day01_GA4_SCHEMA = [
    {'name': 'date', 'type': 'DATE', 'mode': 'REQUIRED'},
    {'name': 'sessions', 'type': 'INTEGER', 'mode': 'REQUIRED'},
    {'name': 'conversions', 'type': 'INTEGER', 'mode': 'REQUIRED'},
    {'name': 'bounce_rate', 'type': 'FLOAT', 'mode': 'REQUIRED'},
    {'name': 'source', 'type': 'STRING', 'mode': 'REQUIRED'}
]

day01_ADS_SCHEMA = [
    {'name': 'date', 'type': 'DATE', 'mode': 'REQUIRED'},
    {'name': 'campaign_name', 'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'spend', 'type': 'FLOAT', 'mode': 'REQUIRED'},
    {'name': 'clicks', 'type': 'INTEGER', 'mode': 'REQUIRED'},
    {'name': 'impressions', 'type': 'INTEGER', 'mode': 'REQUIRED'},
    {'name': 'conversions', 'type': 'INTEGER', 'mode': 'REQUIRED'}
]

# ============================================================================
# Synthetic Data Configuration
# ============================================================================
day01_TRAFFIC_SOURCES = ['google', 'facebook', 'direct', 'email', 'linkedin']

day01_CAMPAIGN_NAMES = [
    'Brand Campaign',
    'Product Launch',
    'Retargeting',
    'Black Friday Special'
]

# GA4 Synthetic Data Ranges
day01_GA4_SESSIONS_MIN = 1000
day01_GA4_SESSIONS_MAX = 2000
day01_GA4_CONVERSION_RATE_MIN = 0.02  # 2%
day01_GA4_CONVERSION_RATE_MAX = 0.05  # 5%
day01_GA4_BOUNCE_RATE_MIN = 0.35
day01_GA4_BOUNCE_RATE_MAX = 0.55

# Google Ads Synthetic Data Ranges
day01_ADS_SPEND_MIN = 300.0
day01_ADS_SPEND_MAX = 800.0
day01_ADS_IMPRESSIONS_MIN = 10000
day01_ADS_IMPRESSIONS_MAX = 25000
day01_ADS_CTR_MIN = 0.02  # 2%
day01_ADS_CTR_MAX = 0.04  # 4%
day01_ADS_CONVERSION_RATE_MIN = 0.03  # 3%
day01_ADS_CONVERSION_RATE_MAX = 0.08  # 8%

# ============================================================================
# File Paths
# ============================================================================
day01_RAW_DATA_DIR = './data/raw'
day01_PROCESSED_DATA_DIR = './data/processed'

day01_GA4_SYNTHETIC_FILE = f'{day01_RAW_DATA_DIR}/ga4_synthetic.csv'
day01_ADS_SYNTHETIC_FILE = f'{day01_RAW_DATA_DIR}/ads_synthetic.csv'

day01_GA4_PROCESSED_FILE = f'{day01_PROCESSED_DATA_DIR}/ga4_sessions.csv'
day01_ADS_PROCESSED_FILE = f'{day01_PROCESSED_DATA_DIR}/ads_campaigns.csv'
