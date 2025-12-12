#!/usr/bin/env python3
"""
Day 12B - Great Expectations Cloud Setup
Initializes GE Cloud connection and creates datasource
"""

import great_expectations as gx
from great_expectations.data_context import CloudDataContext
import pandas as pd
import logging

from day12b_CONFIG_ge_cloud import (
    DAY12B_GE_CLOUD_ORG_ID,
    DAY12B_GE_CLOUD_ACCESS_TOKEN,
    DAY12B_DATASOURCE_NAME,
    DAY12B_DATA_ASSET_NAME,
    DAY12B_SECURITY_EVENTS_PATH,
    DAY12B_LOG_FILE,
    DAY12B_LOG_FORMAT
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=DAY12B_LOG_FORMAT,
    handlers=[
        logging.FileHandler(DAY12B_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def day12b_get_cloud_context():
    """
    Connect to Great Expectations Cloud
    Returns Cloud Data Context for validation operations
    """
    logger.info("=" * 80)
    logger.info("DAY 12B - CONNECTING TO GREAT EXPECTATIONS CLOUD")
    logger.info("=" * 80)

    if not DAY12B_GE_CLOUD_ORG_ID or not DAY12B_GE_CLOUD_ACCESS_TOKEN:
        logger.error("❌ GE Cloud credentials not configured!")
        logger.error("Please set DAY12B_GE_CLOUD_ORG_ID and DAY12B_GE_CLOUD_ACCESS_TOKEN")
        logger.error("See .env.example for instructions")
        return None

    try:
        logger.info(f"📡 Connecting to GE Cloud (Org: {DAY12B_GE_CLOUD_ORG_ID[:20]}...)")

        context = gx.get_context(
            mode="cloud",
            cloud_organization_id=DAY12B_GE_CLOUD_ORG_ID,
            cloud_access_token=DAY12B_GE_CLOUD_ACCESS_TOKEN
        )

        logger.info("✅ Successfully connected to GE Cloud!")
        logger.info(f"Context Type: {type(context).__name__}")

        return context

    except Exception as e:
        logger.error(f"❌ Failed to connect to GE Cloud: {e}")
        logger.error("Check your credentials and network connection")
        return None


def day12b_create_cloud_datasource(context):
    """
    Create or update pandas datasource in GE Cloud
    """
    logger.info("\n📊 Setting up Cloud Datasource...")

    try:
        # Check if datasource already exists
        existing_datasources = context.list_datasources()
        datasource_names = [ds.name for ds in existing_datasources]

        if DAY12B_DATASOURCE_NAME in datasource_names:
            logger.info(f"⚠️  Datasource '{DAY12B_DATASOURCE_NAME}' already exists")
            datasource = context.get_datasource(DAY12B_DATASOURCE_NAME)
            logger.info(f"✅ Using existing datasource")
        else:
            logger.info(f"Creating new datasource: {DAY12B_DATASOURCE_NAME}")

            # Create pandas datasource for CSV files
            datasource = context.sources.add_pandas(
                name=DAY12B_DATASOURCE_NAME
            )

            logger.info(f"✅ Created datasource: {DAY12B_DATASOURCE_NAME}")

        # Add or update data asset
        logger.info(f"Adding data asset: {DAY12B_DATA_ASSET_NAME}")

        # Read CSV to create batch
        df = pd.read_csv(DAY12B_SECURITY_EVENTS_PATH)
        logger.info(f"📊 Loaded {len(df)} records from {DAY12B_SECURITY_EVENTS_PATH.name}")

        # Add CSV asset
        data_asset = datasource.add_csv_asset(
            name=DAY12B_DATA_ASSET_NAME,
            filepath_or_buffer=str(DAY12B_SECURITY_EVENTS_PATH)
        )

        logger.info(f"✅ Added data asset: {DAY12B_DATA_ASSET_NAME}")

        return datasource

    except Exception as e:
        logger.error(f"❌ Failed to create datasource: {e}")
        logger.exception("Full error:")
        return None


def day12b_verify_setup(context):
    """Verify GE Cloud setup is working"""
    logger.info("\n🔍 Verifying GE Cloud Setup...")

    try:
        # List datasources
        datasources = context.list_datasources()
        logger.info(f"✅ Found {len(datasources)} datasource(s):")
        for ds in datasources:
            logger.info(f"   - {ds.name}")

        # List expectation suites
        suites = context.list_expectation_suite_names()
        logger.info(f"✅ Found {len(suites)} expectation suite(s):")
        for suite in suites:
            logger.info(f"   - {suite}")

        logger.info("\n✅ GE Cloud setup verified successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Setup verification failed: {e}")
        return False


def day12b_setup_cloud():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("DAY 12B - GREAT EXPECTATIONS CLOUD SETUP")
    logger.info("=" * 80)

    # Step 1: Connect to GE Cloud
    context = day12b_get_cloud_context()
    if not context:
        logger.error("❌ Setup failed - could not connect to GE Cloud")
        return None

    # Step 2: Create datasource
    datasource = day12b_create_cloud_datasource(context)
    if not datasource:
        logger.error("❌ Setup failed - could not create datasource")
        return None

    # Step 3: Verify setup
    verified = day12b_verify_setup(context)
    if not verified:
        logger.warning("⚠️  Setup completed but verification failed")

    logger.info("\n" + "=" * 80)
    logger.info("SETUP COMPLETE")
    logger.info("=" * 80)
    logger.info("Next steps:")
    logger.info("1. Run: python3 day12b_CREATE_expectations.py")
    logger.info("2. View Data Docs at: https://app.greatexpectations.io")
    logger.info("=" * 80)

    return context


if __name__ == "__main__":
    context = day12b_setup_cloud()
    if context:
        logger.info("✅ Setup successful!")
    else:
        logger.error("❌ Setup failed!")
