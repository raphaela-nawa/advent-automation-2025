"""
Meta API Diagnostic Script
Tests the Meta Graph API connection and provides detailed error information
"""

import requests
import json
from src import config

def test_api_endpoint(url, params, description):
    """Test a specific API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        response = requests.get(url, params=params, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Failed!")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("META GRAPH API DIAGNOSTIC")
    print("="*60)

    # Show configuration
    print("\n📋 Configuration:")
    print(f"   Access Token: {config.META_ACCESS_TOKEN[:20]}..." if config.META_ACCESS_TOKEN else "   ❌ Missing")
    print(f"   Account ID: {config.META_ACCOUNT_ID}")
    print(f"   API Version: {config.META_API_VERSION}")
    print(f"   Base URL: {config.META_BASE_URL}")

    if not config.META_ACCESS_TOKEN or not config.META_ACCOUNT_ID:
        print("\n❌ Missing credentials! Check config/.env")
        return

    # Test 1: Token Debug (check token validity)
    test_api_endpoint(
        f"{config.META_BASE_URL}/debug_token",
        {
            'input_token': config.META_ACCESS_TOKEN,
            'access_token': config.META_ACCESS_TOKEN
        },
        "Token Validation"
    )

    # Test 2: Get User Info (basic test)
    test_api_endpoint(
        f"{config.META_BASE_URL}/me",
        {
            'access_token': config.META_ACCESS_TOKEN
        },
        "User Info (me)"
    )

    # Test 3: Get Instagram Account Info
    test_api_endpoint(
        f"{config.META_BASE_URL}/{config.META_ACCOUNT_ID}",
        {
            'fields': 'username,name,profile_picture_url',
            'access_token': config.META_ACCESS_TOKEN
        },
        "Instagram Account Basic Info"
    )

    # Test 4: Get Instagram Account with followers
    test_api_endpoint(
        f"{config.META_BASE_URL}/{config.META_ACCOUNT_ID}",
        {
            'fields': 'username,followers_count',
            'access_token': config.META_ACCESS_TOKEN
        },
        "Instagram Account with Followers"
    )

    # Test 5: List available fields
    test_api_endpoint(
        f"{config.META_BASE_URL}/{config.META_ACCOUNT_ID}",
        {
            'metadata': '1',
            'access_token': config.META_ACCESS_TOKEN
        },
        "Account Metadata (available fields)"
    )

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print("\n💡 Tips:")
    print("   - If token validation fails: Generate a new token")
    print("   - If account ID fails: Verify it's an Instagram Business Account")
    print("   - Check permissions: instagram_basic, instagram_manage_insights")
    print("   - Token expires after ~60 days")
    print("\n")

if __name__ == "__main__":
    main()
