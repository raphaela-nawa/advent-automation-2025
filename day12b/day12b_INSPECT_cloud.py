#!/usr/bin/env python3
"""
Day 12B - Inspect GE Cloud Configuration
Debug what's actually in your GE Cloud workspace
"""

import great_expectations as gx
import os
import json
from pprint import pprint

from day12b_CONFIG_ge_cloud import (
    DAY12B_GE_CLOUD_ORG_ID,
    DAY12B_GE_CLOUD_ACCESS_TOKEN
)

# Set environment variables
os.environ['GX_CLOUD_ORGANIZATION_ID'] = DAY12B_GE_CLOUD_ORG_ID
os.environ['GX_CLOUD_ACCESS_TOKEN'] = DAY12B_GE_CLOUD_ACCESS_TOKEN

print("=" * 80)
print("GE CLOUD INSPECTION - What's Actually in Your Workspace")
print("=" * 80)

# Connect
print("\n1. Connecting to GE Cloud...")
context = gx.get_context(mode="cloud")
print(f"✅ Connected to workspace")

# Inspect Datasources
print("\n2. DATASOURCES:")
print("-" * 80)
try:
    datasource_names = context.data_sources.all()
    print(f"Found {len(datasource_names)} datasource(s):")

    for i, ds_name in enumerate(datasource_names, 1):
        print(f"\n{i}. Datasource Name: {ds_name}")
        print(f"   Type: {type(ds_name)}")

        # Try to get the datasource object
        try:
            if isinstance(ds_name, str):
                ds = context.data_sources.get(ds_name)
            else:
                ds = ds_name

            print(f"   Datasource Object: {type(ds)}")

            # Try to list assets
            if hasattr(ds, 'assets'):
                print(f"   Assets Type: {type(ds.assets)}")
                if isinstance(ds.assets, dict):
                    print(f"   Number of Assets: {len(ds.assets)}")
                    for asset_name, asset in ds.assets.items():
                        print(f"      - {asset_name} ({type(asset).__name__})")
                elif isinstance(ds.assets, list):
                    print(f"   Number of Assets: {len(ds.assets)}")
                    for asset in ds.assets:
                        print(f"      - {asset.name if hasattr(asset, 'name') else asset}")
        except Exception as e:
            print(f"   ⚠️ Error getting datasource: {e}")

except Exception as e:
    print(f"❌ Error listing datasources: {e}")

# Inspect Expectation Suites
print("\n3. EXPECTATION SUITES:")
print("-" * 80)
try:
    suite_names = context.suites.all()
    print(f"Found {len(suite_names)} suite(s):")
    for suite_name in suite_names:
        print(f"  - {suite_name}")

        # Try to get suite details
        try:
            suite = context.suites.get(suite_name)
            print(f"    Expectations: {len(suite.expectations)}")
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
except Exception as e:
    print(f"❌ Error listing suites: {e}")

# Inspect Validation Definitions
print("\n4. VALIDATION DEFINITIONS:")
print("-" * 80)
try:
    validation_def_names = context.validation_definitions.all()
    print(f"Found {len(validation_def_names)} validation definition(s):")
    for vd_name in validation_def_names:
        print(f"  - {vd_name}")
except Exception as e:
    print(f"❌ Error listing validation definitions: {e}")

# Inspect Checkpoints
print("\n5. CHECKPOINTS:")
print("-" * 80)
try:
    checkpoint_names = context.checkpoints.all()
    print(f"Found {len(checkpoint_names)} checkpoint(s):")
    for cp_name in checkpoint_names:
        print(f"  - {cp_name}")
except Exception as e:
    print(f"❌ Error listing checkpoints: {e}")

# Check pandas_default specifically
print("\n6. PANDAS_DEFAULT DATASOURCE:")
print("-" * 80)
try:
    pandas_default = context.data_sources.pandas_default
    print(f"✅ pandas_default exists: {type(pandas_default)}")
    print(f"   This is an ephemeral datasource (not saved to Cloud)")
except Exception as e:
    print(f"❌ Error accessing pandas_default: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

# Provide diagnosis
if len(suite_names) > 0:
    print("✅ Expectation Suites exist in Cloud")
else:
    print("❌ No Expectation Suites in Cloud")

if len(datasource_names) > 0:
    print("✅ Datasources exist in Cloud")
else:
    print("❌ No Datasources in Cloud (only pandas_default)")

if len(checkpoint_names) > 0:
    print("✅ Checkpoints exist in Cloud")
else:
    print("❌ No Checkpoints in Cloud - THIS IS WHY DASHBOARD IS EMPTY!")

if len(validation_def_names) > 0:
    print("✅ Validation Definitions exist in Cloud")
else:
    print("❌ No Validation Definitions in Cloud")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

if len(checkpoint_names) == 0:
    print("\nYou need to create a Checkpoint to see results in dashboard!")
    print("\nWorkflow:")
    print("1. Create Validation Definition (links Suite + Data Asset)")
    print("2. Create Checkpoint (uses Validation Definition)")
    print("3. Run Checkpoint")
    print("4. Results appear in GE Cloud dashboard")

print("\n" + "=" * 80)
