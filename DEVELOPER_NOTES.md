# Developer Notes - Advent Automation 2025

## 🎯 System Architecture Overview

This project implements a **secure, client-ready automation framework** where each day represents an independent project with isolated API keys.

---

## 🔑 Key Management System

### Design Philosophy

1. **Developer Keys (Defaults):**
   - `KEY_OPENAI` and `KEY_ANTHROPIC`
   - Used for development and testing only
   - **NEVER shared with clients**

2. **Client Keys (Day-Specific):**
   - `KEY_OPENAI_DAY01`, `KEY_ANTHROPIC_DAY01`, etc.
   - **REQUIRED** for each client deployment
   - Ensures usage tracking and security isolation

### Security Model

```
┌─────────────────────────────────────────────────┐
│  Development Environment (You)                  │
│  Uses: KEY_OPENAI, KEY_ANTHROPIC               │
│  Mode: allow_defaults=True                      │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  Client Deployment (Production)                 │
│  Uses: KEY_OPENAI_DAY##, KEY_ANTHROPIC_DAY##   │
│  Mode: strict_mode=True (default)               │
│  Result: Isolated usage tracking per client     │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
advent-automation-2025/
├── day01/                      # Client Project 1
│   └── day01_main.py          # Requires KEY_*_DAY01
├── day02/                      # Client Project 2
│   └── day02_main.py          # Requires KEY_*_DAY02
├── ...
├── day25/                      # Client Project 25
├── A_testday/                  # Testing sandbox
├── common/
│   ├── utils/
│   │   └── boilerplate.py     # Core key management
│   └── datasets/               # Shared data
├── config/
│   ├── .env                    # NEVER commit (gitignored)
│   └── .env.example           # Template for clients
├── CLIENT_SETUP_GUIDE.md      # For clients
├── DEVELOPER_NOTES.md         # This file
└── requirements.txt
```

---

## 🛠️ Boilerplate Functions

### `load_secrets(day=None, allow_defaults=False)`

Loads API keys with security controls.

**Parameters:**
- `day` (int): Day number (1-25) for project-specific keys
- `allow_defaults` (bool): Allow fallback to developer keys (default: False)

**Returns:**
```python
{
    "openai": str,          # API key or None
    "anthropic": str,       # API key or None
    "project_id": str,      # e.g., "day01"
    "day": int,             # Day number
    "using_defaults": bool  # True if fell back to defaults
}
```

**Usage Examples:**

```python
# Client/Production mode (strict - no fallback)
keys = load_secrets(day=1)
# Requires: KEY_OPENAI_DAY01, KEY_ANTHROPIC_DAY01

# Development mode (with fallback)
keys = load_secrets(day=1, allow_defaults=True)
# Tries: KEY_OPENAI_DAY01 → falls back to KEY_OPENAI

# General testing (defaults only)
keys = load_secrets()
# Uses: KEY_OPENAI, KEY_ANTHROPIC
```

### `validate_keys(keys, required=None, strict_mode=True)`

Validates key presence and enforces security policies.

**Parameters:**
- `keys` (dict): Output from `load_secrets()`
- `required` (list): Required providers (default: ["openai", "anthropic"])
- `strict_mode` (bool): Enforce day-specific keys (default: True)

**Behavior:**

| Scenario | strict_mode=True | strict_mode=False |
|----------|------------------|-------------------|
| Day-specific keys missing | ❌ ValueError | ⚠️ Warning only |
| Using defaults in day project | ❌ ValueError | ✅ Allowed |
| Keys completely missing | ❌ ValueError | ❌ ValueError |

**Example Error Messages:**

```python
# Missing keys
ValueError: Missing API keys for: openai, anthropic
For Day 01, please configure: KEY_OPENAI_DAY01 and KEY_ANTHROPIC_DAY01 in config/.env

# Using defaults (security warning)
ValueError: ⚠️  SECURITY WARNING: Day 01 is using default keys!
   This is dangerous for production/client deployments.
   Please configure day-specific keys:
   - KEY_OPENAI_DAY01
   - KEY_ANTHROPIC_DAY01

   For development/testing only, use: load_secrets(day=1, allow_defaults=True)
```

### `get_client(provider, day=None)`

Factory function to get configured API clients.

```python
# Get OpenAI client for Day 01
client = get_client("openai", day=1)

# Get Anthropic client for Day 02
client = get_client("anthropic", day=2)

# Returns ready-to-use client instance
response = client.chat.completions.create(...)
```

---

## 🔄 Development Workflow

### Phase 1: Development (You)

```python
# In A_testday/ or during feature development
keys = load_secrets(day=1, allow_defaults=True)
validate_keys(keys, strict_mode=False)
# Uses your KEY_OPENAI/KEY_ANTHROPIC for testing
```

### Phase 2: Prepare for Client

```python
# Switch day##_main.py to production mode
keys = load_secrets(day=1)  # No allow_defaults
validate_keys(keys, strict_mode=True)
# Forces client to configure their own keys
```

### Phase 3: Client Deployment

Client receives:
1. ✅ `day##/` folder with script
2. ✅ `common/` utilities
3. ✅ `config/.env.example` template
4. ✅ `CLIENT_SETUP_GUIDE.md`
5. ❌ NOT your `.env` file (gitignored)

Client configures:
```bash
KEY_OPENAI_DAY##=their_key
KEY_ANTHROPIC_DAY##=their_key
```

---

## 🧪 Testing Checklist

Before delivering to client:

```bash
# 1. Test without day-specific keys (should fail)
python day01/day01_main.py
# Expected: "Missing API keys for Day 01..."

# 2. Add day-specific keys to .env
KEY_OPENAI_DAY01=test_key
KEY_ANTHROPIC_DAY01=test_key

# 3. Test with day-specific keys (should pass)
python day01/day01_main.py
# Expected: "✓ All required API keys are configured correctly"

# 4. Verify no defaults are being used
# Check output for: "✓ Using day-specific keys"
```

---

## 📦 Migration Guide

If you have old key names, use the migration script:

```bash
python migrate_env_keys.py
```

Converts:
- `OPENAI_API_KEY_DEFAULT` → `KEY_OPENAI`
- `ANTHROPIC_API_KEY_DEFAULT` → `KEY_ANTHROPIC`
- `OPENAI_API_KEY_DAY01` → `KEY_OPENAI_DAY01`
- `ANTHROPIC_API_KEY_DAY01` → `KEY_ANTHROPIC_DAY01`

---

## 🎨 Creating New Day Projects

Template for `dayXX/dayXX_main.py`:

```python
#!/usr/bin/env python3
"""
Day XX - Advent Automation 2025
Project description here
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.utils.boilerplate import load_secrets, validate_keys

def main():
    # PRODUCTION MODE (for clients)
    keys = load_secrets(day=XX)

    # DEVELOPMENT MODE (for testing only - comment out for clients)
    # keys = load_secrets(day=XX, allow_defaults=True)

    print("="*50)
    print(f"Day {XX:02d} – Project Name")
    print(f"Project ID: {keys['project_id']}")
    print("="*50)

    try:
        validate_keys(keys)
        print("✓ Configuration OK")
    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1

    # Your automation logic here
    print("\n[Your automation code...]")

    return 0

if __name__ == "__main__":
    exit(main())
```

---

## 🔒 Security Considerations

### Why This Design?

1. **Isolation:** Each client project has separate keys
2. **Tracking:** You can monitor usage per day/client
3. **Control:** Revoke specific keys without affecting others
4. **Safety:** Clients can't accidentally use your dev keys
5. **Compliance:** Clear separation of dev vs prod environments

### Best Practices

- ✅ Always use `strict_mode=True` in production scripts
- ✅ Document which keys are needed in each day's README
- ✅ Test deployment process with fresh .env file
- ✅ Provide clear error messages when keys are missing
- ❌ Never hardcode API keys in source code
- ❌ Never commit .env files to git
- ❌ Never share your default dev keys with clients

---

## 📊 Usage Monitoring

You can track API usage per project:

```python
# In your analytics/monitoring code
day01_usage = get_usage_stats("KEY_OPENAI_DAY01")
day02_usage = get_usage_stats("KEY_OPENAI_DAY02")

# Cost allocation
print(f"Day 01: ${day01_usage.cost}")
print(f"Day 02: ${day02_usage.cost}")
```

---

## 🚀 Deployment Checklist

- [ ] Remove or comment out `allow_defaults=True`
- [ ] Ensure `strict_mode=True` in validation
- [ ] Update `CLIENT_SETUP_GUIDE.md` with project specifics
- [ ] Test with empty .env file
- [ ] Verify error messages are helpful
- [ ] Document required keys in project README
- [ ] Remove any hardcoded test keys
- [ ] Check .gitignore includes .env

---

## 📝 Notes

- Each day is an **independent project** with its own keys
- Keys are **never** shared between days or clients
- The system **fails safe** - missing keys = clear error, not silent defaults
- Clients receive a **turnkey solution** - just add their keys and run

---

**Last Updated:** 2025-11-21
**Maintainer:** [Your Name]
