#!/usr/bin/env python3
"""
Day 12 - Great Expectations Project Initialization
Sets up Great Expectations project structure and datasources
"""

import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
import os
from pathlib import Path

# Import configuration
from day12_CONFIG_settings import (
    DAY12_GE_DIR,
    DAY12_DATA_DIR,
    DAY12_GE_DATASOURCE_NAME,
    DAY12_SECURITY_EVENTS_PATH
)

def day12_initialize_ge_project():
    """
    Initialize Great Expectations project and configure datasource
    """
    print("=" * 80)
    print("DAY 12 - GREAT EXPECTATIONS PROJECT INITIALIZATION")
    print("=" * 80)

    # Create GE directory if it doesn't exist
    DAY12_GE_DIR.mkdir(exist_ok=True, parents=True)

    # Initialize Data Context
    print("\n📁 Initializing Data Context...")
    try:
        context = gx.get_context(project_root_dir=str(DAY12_GE_DIR.parent))
        print("✅ Data Context initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Data Context: {e}")
        return None

    # Configure Pandas Datasource for CSV files
    print(f"\n📊 Configuring datasource: {DAY12_GE_DATASOURCE_NAME}...")

    try:
        # Add datasource for CSV files
        datasource_config = {
            "name": DAY12_GE_DATASOURCE_NAME,
            "class_name": "Datasource",
            "execution_engine": {
                "class_name": "PandasExecutionEngine"
            },
            "data_connectors": {
                "default_runtime_data_connector_name": {
                    "class_name": "RuntimeDataConnector",
                    "batch_identifiers": ["default_identifier_name"]
                }
            }
        }

        context.add_datasource(**datasource_config)
        print(f"✅ Datasource '{DAY12_GE_DATASOURCE_NAME}' configured")
    except Exception as e:
        print(f"⚠️  Datasource may already exist or error occurred: {e}")

    # List configured datasources
    print("\n📋 Configured datasources:")
    datasources = context.list_datasources()
    for ds in datasources:
        print(f"  - {ds['name']}")

    print("\n✅ Great Expectations project initialized successfully!")
    print(f"\nProject directory: {DAY12_GE_DIR}")
    print(f"Data directory: {DAY12_DATA_DIR}")

    return context


if __name__ == "__main__":
    context = day12_initialize_ge_project()

    if context:
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Run day12_CREATE_expectations.py to create expectation suite")
        print("2. Run day12_RUN_validation.py to execute validation")
        print("3. View Data Docs in great_expectations/uncommitted/data_docs/")
        print("=" * 80)
