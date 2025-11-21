#!/usr/bin/env python3
"""
Day 01 - Advent Automation 2025
Project-specific automation with dedicated API keys
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.utils.boilerplate import load_secrets, validate_keys

def main():
    # PRODUCTION MODE (for clients):
    # Requires KEY_OPENAI_DAY01 and KEY_ANTHROPIC_DAY01
    # Will NOT fallback to defaults for security
    keys = load_secrets(day=1)

    # DEVELOPMENT MODE (for testing only):
    # Uncomment the line below to allow fallback to default keys during development
    # keys = load_secrets(day=1, allow_defaults=True)

    print("="*50)
    print(f"Day 01 – Automation Ready")
    print(f"Project ID: {keys['project_id']}")
    print("="*50)
    print(f"OPENAI KEY DETECTED:     {bool(keys['openai'])}")
    print(f"ANTHROPIC KEY DETECTED:  {bool(keys['anthropic'])}")

    if keys.get('using_defaults'):
        print(f"⚠️  USING DEFAULT KEYS (Development Mode)")
    else:
        print(f"✓ Using day-specific keys")

    print("="*50)

    # Validate that required keys are present
    # strict_mode=True ensures clients must configure day-specific keys
    try:
        validate_keys(keys, required=["openai", "anthropic"], strict_mode=True)
        print("✓ All required API keys are configured correctly")
    except ValueError as e:
        print(f"✗ Configuration error:\n{e}")
        return 1

    # Your automation code goes here
    print("\n[Day 01 Logic]")
    print("Ready to start automation tasks...")

    return 0

if __name__ == "__main__":
    exit(main())
