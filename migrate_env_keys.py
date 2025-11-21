#!/usr/bin/env python3
"""
Migration script to convert old API key naming to new convention.

Old format:
  OPENAI_API_KEY_DEFAULT=...
  ANTHROPIC_API_KEY_DEFAULT=...
  OPENAI_API_KEY_DAY01=...
  ANTHROPIC_API_KEY_DAY01=...

New format:
  KEY_OPENAI=...
  KEY_ANTHROPIC=...
  KEY_OPENAI_DAY01=...
  KEY_ANTHROPIC_DAY01=...
"""

import re
from pathlib import Path

def migrate_env_file(env_path):
    """
    Migrate .env file from old naming convention to new one.

    Args:
        env_path (Path): Path to .env file

    Returns:
        tuple: (success: bool, changes_made: int)
    """
    if not env_path.exists():
        print(f"❌ File not found: {env_path}")
        return False, 0

    # Read original content
    with open(env_path, 'r') as f:
        content = f.read()

    original_content = content
    changes = 0

    # Define migration patterns
    migrations = [
        # OPENAI_API_KEY_DEFAULT -> KEY_OPENAI
        (r'^OPENAI_API_KEY_DEFAULT=', 'KEY_OPENAI='),
        # ANTHROPIC_API_KEY_DEFAULT -> KEY_ANTHROPIC
        (r'^ANTHROPIC_API_KEY_DEFAULT=', 'KEY_ANTHROPIC='),
        # OPENAI_API_KEY_DAY01 -> KEY_OPENAI_DAY01
        (r'^OPENAI_API_KEY_DAY(\d{2})=', r'KEY_OPENAI_DAY\1='),
        # ANTHROPIC_API_KEY_DAY01 -> KEY_ANTHROPIC_DAY01
        (r'^ANTHROPIC_API_KEY_DAY(\d{2})=', r'KEY_ANTHROPIC_DAY\1='),
    ]

    # Apply migrations line by line to preserve comments and structure
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        new_line = line
        for old_pattern, new_pattern in migrations:
            match = re.match(old_pattern, line)
            if match:
                new_line = re.sub(old_pattern, new_pattern, line)
                if new_line != line:
                    changes += 1
                    print(f"  ✓ {line.split('=')[0]} → {new_line.split('=')[0]}")
                break
        new_lines.append(new_line)

    content = '\n'.join(new_lines)

    if changes > 0:
        # Backup original file
        backup_path = env_path.with_suffix('.env.backup')
        with open(backup_path, 'w') as f:
            f.write(original_content)
        print(f"\n📦 Backup created: {backup_path}")

        # Write migrated content
        with open(env_path, 'w') as f:
            f.write(content)

        return True, changes
    else:
        print("ℹ️  No changes needed - file already uses new naming convention")
        return True, 0

def main():
    print("="*60)
    print("ENV KEYS MIGRATION SCRIPT")
    print("="*60)
    print()

    env_path = Path(__file__).parent / "config" / ".env"

    print(f"📂 Target file: {env_path}")
    print()
    print("🔄 Starting migration...")
    print()

    success, changes = migrate_env_file(env_path)

    print()
    print("="*60)
    if success:
        if changes > 0:
            print(f"✅ Migration completed successfully!")
            print(f"   {changes} key(s) renamed to new convention")
            print()
            print("📝 Next steps:")
            print("   1. Review the changes in config/.env")
            print("   2. Test with: python day01/day01_main.py")
            print("   3. If everything works, delete config/.env.backup")
        else:
            print("✅ File already up to date!")
    else:
        print("❌ Migration failed")
        return 1

    print("="*60)
    return 0

if __name__ == "__main__":
    exit(main())
