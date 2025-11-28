"""
Day 04 - Setup Validation Script
Quick test to verify all configuration is correct before running the full pipeline
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def day04_test_imports():
    """Test that all required packages are installed."""
    print("🔍 Testing Python package imports...")

    packages = [
        ('requests', 'HTTP requests'),
        ('pandas', 'Data processing'),
        ('google.cloud.bigquery', 'BigQuery client'),
        ('dotenv', 'Environment variables')
    ]

    failed = []

    for package, description in packages:
        try:
            __import__(package)
            print(f"   ✓ {package:25} ({description})")
        except ImportError:
            print(f"   ✗ {package:25} ({description}) - MISSING")
            failed.append(package)

    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("   Run: pip install -r day04_requirements.txt")
        return False

    print("   ✅ All packages installed\n")
    return True


def day04_test_config():
    """Test that configuration loads correctly."""
    print("🔍 Testing configuration...")

    try:
        from day04_CONFIG_settings import day04_validate_config
        day04_validate_config()
        print("   ✅ Configuration valid\n")
        return True
    except ValueError as e:
        print(f"   ❌ Configuration error: {e}\n")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}\n")
        return False


def day04_test_blockfrost_connection():
    """Test Blockfrost API connectivity."""
    print("🔍 Testing Blockfrost API connection...")

    try:
        import requests
        from day04_CONFIG_settings import day04_BLOCKFROST_API_KEY, day04_BLOCKFROST_API_URL

        if not day04_BLOCKFROST_API_KEY or day04_BLOCKFROST_API_KEY == "mainnetYOUR_API_KEY_HERE":
            print("   ⚠️  Blockfrost API key not set")
            print("   → Get free key at: https://blockfrost.io")
            print("   → Add to ../config/.env as DAY04_BLOCKFROST_API_KEY\n")
            return False

        # Test API connection with a simple endpoint
        headers = {"project_id": day04_BLOCKFROST_API_KEY}
        response = requests.get(
            f"{day04_BLOCKFROST_API_URL}/health",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print(f"   ✓ Connected to Blockfrost API")
            print(f"   ✓ Network: {day04_BLOCKFROST_API_URL.split('//')[1].split('.')[0]}")
            print("   ✅ API connection successful\n")
            return True
        else:
            print(f"   ✗ API returned status code: {response.status_code}")
            print(f"   ✗ Response: {response.text}")
            print("   ❌ Check your API key\n")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        print("   → Check internet connection\n")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False


def day04_test_gcp_auth():
    """Test Google Cloud authentication."""
    print("🔍 Testing Google Cloud authentication...")

    try:
        from google.cloud import bigquery
        from day04_CONFIG_settings import day04_GCP_PROJECT_ID

        if not day04_GCP_PROJECT_ID:
            print("   ⚠️  GCP Project ID not set")
            print("   → Add to ../config/.env as DAY04_GCP_PROJECT_ID\n")
            return False

        # Try to create client
        client = bigquery.Client(project=day04_GCP_PROJECT_ID)

        # Test with a simple query
        query = "SELECT 1 as test"
        query_job = client.query(query)
        result = list(query_job.result())

        print(f"   ✓ Authenticated to GCP")
        print(f"   ✓ Project: {day04_GCP_PROJECT_ID}")
        print("   ✅ BigQuery access confirmed\n")
        return True

    except Exception as e:
        print(f"   ❌ GCP authentication failed: {e}")
        print("   → Run: gcloud auth application-default login")
        print("   → Verify project ID is correct\n")
        return False


def day04_test_file_structure():
    """Test that all required files exist."""
    print("🔍 Testing file structure...")

    required_files = [
        'day04_CONFIG_settings.py',
        'day04_DATA_extract_blockfrost.py',
        'day04_DATA_load_bigquery.py',
        'day04_requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.env.example',
        'README.md'
    ]

    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} - MISSING")
            missing.append(file)

    # Check directories
    for dir in ['data/raw', 'data/processed']:
        if os.path.exists(dir):
            print(f"   ✓ {dir}/")
        else:
            print(f"   ✗ {dir}/ - MISSING")
            missing.append(dir)

    if missing:
        print(f"\n   ❌ Missing files/directories: {len(missing)}\n")
        return False

    print("   ✅ All files present\n")
    return True


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("DAY 04 - CARDANO TRANSPARENCY PIPELINE - SETUP VALIDATION")
    print("=" * 70)
    print()

    tests = [
        ("File Structure", day04_test_file_structure),
        ("Python Imports", day04_test_imports),
        ("Configuration", day04_test_config),
        ("Blockfrost API", day04_test_blockfrost_connection),
        ("Google Cloud", day04_test_gcp_auth),
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} test crashed: {e}\n")
            results[name] = False

    # Summary
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20} {status}")

    print()

    total_tests = len(results)
    passed_tests = sum(results.values())

    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED ({passed_tests}/{total_tests})")
        print("\n✅ Ready to run the pipeline!")
        print("\nNext steps:")
        print("  1. docker-compose up                           # Extract metrics")
        print("  2. docker-compose run cardano-transparency \\")
        print("       python day04_DATA_load_bigquery.py        # Load to BigQuery")
        print()
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed_tests}/{total_tests} passed)")
        print("\n❌ Fix the issues above before running the pipeline")
        print()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
