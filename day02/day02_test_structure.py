"""
Test script to validate Day 02 project structure
Tests imports and basic functionality without requiring API credentials
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")

    try:
        # Test individual module imports
        from src import __init__
        print("   ✓ src.__init__ imported")

        from src import meta_extractor
        print("   ✓ src.meta_extractor imported")

        from src import data_manager
        print("   ✓ src.data_manager imported")

        from src import audience_segmentation
        print("   ✓ src.audience_segmentation imported")

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_database_init():
    """Test database initialization"""
    print("\nTesting database initialization...")

    try:
        from src.data_manager import DataManager

        # Create a test database in memory
        dm = DataManager(':memory:')
        print("   ✓ DataManager initialized successfully")

        # Test database summary (should be empty)
        summary = dm.get_database_summary()
        print(f"   ✓ Database summary: {summary}")

        return True

    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")

    required_files = [
        'requirements.txt',
        '.env.example_day02',
        'README.md',
        'pipeline.py',
        'src/__init__.py',
        'src/config.py',
        'src/meta_extractor.py',
        'src/data_manager.py',
        'src/audience_segmentation.py'
    ]

    project_dir = Path(__file__).parent

    all_exist = True
    for file_path in required_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False

    return all_exist


def main():
    """Run all tests"""
    print("=" * 50)
    print("DAY 02 - PROJECT STRUCTURE VALIDATION")
    print("=" * 50 + "\n")

    results = []

    # Test file structure
    results.append(("File Structure", test_file_structure()))

    # Test imports (skip config which requires .env)
    results.append(("Module Imports", test_imports()))

    # Test database
    results.append(("Database Init", test_database_init()))

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All structural tests passed!")
        print("\nNext steps:")
        print("1. Set up your .env file:")
        print("   cd day02")
        print("   cp .env.example_day02 .env")
        print("   # Edit .env with your credentials")
        print("\n2. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n3. Run the pipeline:")
        print("   python pipeline.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
