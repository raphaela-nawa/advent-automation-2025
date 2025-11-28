"""
Day 04 Configuration Settings
Cardano Blockchain Transparency Pipeline

This module manages configuration for extracting on-chain transparency metrics
from Cardano blockchain via Blockfrost API and loading to BigQuery.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../config/.env')

# ============================================================================
# BLOCKFROST API CONFIGURATION
# ============================================================================

day04_BLOCKFROST_API_KEY = os.getenv('DAY04_BLOCKFROST_API_KEY')
day04_BLOCKFROST_NETWORK = os.getenv('DAY04_BLOCKFROST_NETWORK', 'mainnet')

# Blockfrost base URLs by network
day04_BLOCKFROST_BASE_URLS = {
    'mainnet': 'https://cardano-mainnet.blockfrost.io/api/v0',
    'testnet': 'https://cardano-testnet.blockfrost.io/api/v0',
    'preprod': 'https://cardano-preprod.blockfrost.io/api/v0',
    'preview': 'https://cardano-preview.blockfrost.io/api/v0'
}

day04_BLOCKFROST_API_URL = day04_BLOCKFROST_BASE_URLS.get(
    day04_BLOCKFROST_NETWORK,
    day04_BLOCKFROST_BASE_URLS['mainnet']
)

# ============================================================================
# BIGQUERY CONFIGURATION
# ============================================================================

day04_GCP_PROJECT_ID = os.getenv('DAY04_GCP_PROJECT_ID')
day04_BQ_DATASET = os.getenv('DAY04_BQ_DATASET', 'cardano_data')
day04_BQ_TABLE = os.getenv('DAY04_BQ_TABLE', 'cardano_network_activity')
day04_BQ_LOCATION = os.getenv('DAY04_BQ_LOCATION', 'US')

# Full table reference
day04_BQ_TABLE_FULL = f"{day04_GCP_PROJECT_ID}.{day04_BQ_DATASET}.{day04_BQ_TABLE}"

# ============================================================================
# CARDANO NETWORK CONSTANTS
# ============================================================================

# Conversion factor: 1 ADA = 1,000,000 Lovelace
day04_LOVELACE_TO_ADA = 1_000_000

# Average transaction fee in USD (approximate - Blockfrost doesn't provide real-time USD)
day04_AVG_TX_FEE_USD = 0.17

# ============================================================================
# DATA PATHS
# ============================================================================

day04_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
day04_RAW_DATA_DIR = os.path.join(day04_DATA_DIR, 'raw')
day04_PROCESSED_DATA_DIR = os.path.join(day04_DATA_DIR, 'processed')

day04_CSV_OUTPUT_PATH = os.path.join(
    day04_PROCESSED_DATA_DIR,
    'cardano_transparency.csv'
)

# ============================================================================
# API REQUEST SETTINGS
# ============================================================================

day04_API_TIMEOUT = 30  # seconds
day04_API_RETRY_ATTEMPTS = 3
day04_API_RETRY_DELAY = 2  # seconds

# ============================================================================
# VALIDATION
# ============================================================================

def day04_validate_config():
    """
    Validates that all required configuration variables are set.

    Raises:
        ValueError: If required configuration is missing
    """
    errors = []

    if not day04_BLOCKFROST_API_KEY:
        errors.append("DAY04_BLOCKFROST_API_KEY is not set. Get free key at https://blockfrost.io")

    if not day04_GCP_PROJECT_ID:
        errors.append("DAY04_GCP_PROJECT_ID is not set")

    if errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    print("✅ Configuration validated successfully")
    print(f"   - Blockfrost Network: {day04_BLOCKFROST_NETWORK}")
    print(f"   - GCP Project: {day04_GCP_PROJECT_ID}")
    print(f"   - BigQuery Table: {day04_BQ_TABLE_FULL}")


if __name__ == '__main__':
    print("Day 04 Configuration Settings")
    print("=" * 60)
    day04_validate_config()
