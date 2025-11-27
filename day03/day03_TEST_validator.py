"""
Day 03 - Simple test script to validate GDPR validation logic
Tests the validator without requiring BigQuery or Flask server
"""

import json
from day03_PIPELINE_gdpr_validator import day03_GDPRValidator, day03_calculate_retention_date
from datetime import datetime

def day03_test_validation():
    """Test the GDPR validator with sample payloads."""

    print("=" * 60)
    print("Day 03 - GDPR Validator Test")
    print("=" * 60)

    validator = day03_GDPRValidator()

    # Test 1: Valid lead with consent
    print("\n[Test 1] Valid lead WITH consent:")
    with open("data/sample_payloads/lead_with_consent.json", "r") as f:
        payload1 = json.load(f)

    is_valid, error, processed = validator.validate_lead(payload1)
    if is_valid:
        print("✅ PASSED - Lead validated successfully")
        print(f"   Lead ID: {processed['lead_id']}")
        print(f"   Consent Given: {processed['consent_given']}")
        print(f"   Retention Date: {processed['data_retention_date']}")
    else:
        print(f"❌ FAILED - {error}")

    # Test 2: Valid lead without consent
    print("\n[Test 2] Valid lead WITHOUT consent:")
    with open("data/sample_payloads/lead_without_consent.json", "r") as f:
        payload2 = json.load(f)

    is_valid, error, processed = validator.validate_lead(payload2)
    if is_valid:
        print("✅ PASSED - Lead validated successfully")
        print(f"   Lead ID: {processed['lead_id']}")
        print(f"   Consent Given: {processed['consent_given']}")
        print(f"   Retention Date: {processed['data_retention_date']}")
    else:
        print(f"❌ FAILED - {error}")

    # Test 3: Invalid email
    print("\n[Test 3] Invalid email format:")
    payload3 = payload1.copy()
    payload3["email"] = "invalid-email"

    is_valid, error, processed = validator.validate_lead(payload3)
    if not is_valid:
        print(f"✅ PASSED - Correctly rejected: {error}")
    else:
        print("❌ FAILED - Should have rejected invalid email")

    # Test 4: Missing required field
    print("\n[Test 4] Missing required field:")
    payload4 = payload1.copy()
    del payload4["consent_purpose"]

    is_valid, error, processed = validator.validate_lead(payload4)
    if not is_valid:
        print(f"✅ PASSED - Correctly rejected: {error}")
    else:
        print("❌ FAILED - Should have rejected missing field")

    # Test 5: Invalid consent purpose
    print("\n[Test 5] Invalid consent purpose:")
    payload5 = payload1.copy()
    payload5["consent_purpose"] = "invalid_purpose"

    is_valid, error, processed = validator.validate_lead(payload5)
    if not is_valid:
        print(f"✅ PASSED - Correctly rejected: {error}")
    else:
        print("❌ FAILED - Should have rejected invalid purpose")

    # Test 6: Retention date calculation
    print("\n[Test 6] Retention date calculation:")
    test_timestamp = datetime(2024, 11, 26, 10, 30, 0)

    # With consent: +365 days
    retention_with = day03_calculate_retention_date(test_timestamp, True, 30)
    expected_with = datetime(2025, 11, 26, 10, 30, 0)

    if retention_with.date() == expected_with.date():
        print(f"✅ PASSED - With consent: {retention_with.date()} (365 days)")
    else:
        print(f"❌ FAILED - Expected {expected_with.date()}, got {retention_with.date()}")

    # Without consent: +30 days
    retention_without = day03_calculate_retention_date(test_timestamp, False, 30)
    expected_without = datetime(2024, 12, 26, 10, 30, 0)

    if retention_without.date() == expected_without.date():
        print(f"✅ PASSED - Without consent: {retention_without.date()} (30 days)")
    else:
        print(f"❌ FAILED - Expected {expected_without.date()}, got {retention_without.date()}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    day03_test_validation()
