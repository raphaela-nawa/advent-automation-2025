# Client Setup Guide - Advent Automation 2025

## Quick Start for Clients

This guide helps you configure and run your day-specific automation project.

---

## 📋 Prerequisites

1. **Python 3.11+** installed on your system
2. **API Keys** from:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

---

## 🔧 Setup Instructions

### Step 1: Clone/Download the Project

```bash
cd advent-automation-2025
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Your API Keys

1. **Copy the example configuration:**
   ```bash
   cp config/.env.example config/.env
   ```

2. **Edit `config/.env` with your keys:**

   For **Day 01** project, you need:
   ```bash
   KEY_OPENAI_DAY01=sk-proj-YOUR_OPENAI_KEY_HERE
   KEY_ANTHROPIC_DAY01=sk-ant-YOUR_ANTHROPIC_KEY_HERE
   ```

   For **Day 02** project, you need:
   ```bash
   KEY_OPENAI_DAY02=sk-proj-YOUR_OPENAI_KEY_HERE
   KEY_ANTHROPIC_DAY02=sk-ant-YOUR_ANTHROPIC_KEY_HERE
   ```

   ⚠️ **Important:**
   - Use YOUR OWN API keys, not the developer's defaults
   - Each day project needs its own keys (KEY_*_DAY##)
   - This ensures proper usage tracking and security

### Step 4: Run Your Day Project

```bash
# Run Day 01
python day01/day01_main.py

# Run Day 02
python day02/day02_main.py

# etc...
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Use separate API keys for each day project
- Keep your `.env` file private (never commit to git)
- Monitor your API usage through OpenAI/Anthropic dashboards
- Revoke and regenerate keys if compromised

### ❌ DON'T:
- Share your `.env` file with others
- Use the `KEY_OPENAI` or `KEY_ANTHROPIC` defaults (those are for developers)
- Commit API keys to version control
- Use the same key across multiple projects without tracking

---

## 📊 Usage Tracking

Each day project uses isolated API keys, allowing you to:

- **Track costs** per project/day independently
- **Set spending limits** on specific keys via OpenAI/Anthropic dashboards
- **Monitor usage** separately for each automation
- **Control access** by enabling/disabling specific keys

### Example Usage Dashboard:

```
Day 01 → KEY_OPENAI_DAY01  → $5.23 spent
Day 02 → KEY_OPENAI_DAY02  → $2.10 spent
Day 03 → KEY_OPENAI_DAY03  → $0.00 spent (not used yet)
```

---

## ❓ Troubleshooting

### Error: "Missing API keys for: openai, anthropic"

**Problem:** Day-specific keys not configured in `config/.env`

**Solution:**
```bash
# Check if .env exists
ls -la config/.env

# If not, copy from example
cp config/.env.example config/.env

# Edit and add your keys
nano config/.env  # or use your preferred editor
```

### Error: "SECURITY WARNING: Using default keys"

**Problem:** Script detected you're using developer's default keys instead of day-specific ones

**Solution:** Configure the correct day-specific keys:
```bash
# For Day 01, add to config/.env:
KEY_OPENAI_DAY01=sk-proj-...
KEY_ANTHROPIC_DAY01=sk-ant-...
```

### Keys Not Being Detected

**Checklist:**
1. ✅ File is named exactly `config/.env` (not `.env.example`)
2. ✅ No spaces around the `=` sign
3. ✅ Keys are on the correct format: `KEY_OPENAI_DAY01=sk-...`
4. ✅ No quotes around values (or use double quotes consistently)
5. ✅ File has Unix line endings (not Windows CRLF)

---

## 🆘 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Verify your API keys are valid at:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
3. Contact the project developer with:
   - Day number you're trying to run
   - Error message (remove actual API keys from logs)
   - Python version: `python --version`

---

## 📝 Configuration Template

Here's a complete template for your `config/.env`:

```bash
# ==============================================================================
# YOUR CONFIGURATION - Advent Automation 2025
# ==============================================================================

# Day 01 Project (REQUIRED if using day01/)
KEY_OPENAI_DAY01=sk-proj-YOUR_KEY_HERE
KEY_ANTHROPIC_DAY01=sk-ant-YOUR_KEY_HERE

# Day 02 Project (REQUIRED if using day02/)
# KEY_OPENAI_DAY02=sk-proj-YOUR_KEY_HERE
# KEY_ANTHROPIC_DAY02=sk-ant-YOUR_KEY_HERE

# Add more days as needed...

# NOTE: Do NOT configure KEY_OPENAI or KEY_ANTHROPIC
# Those are reserved for developer use only
```

---

## ✨ Ready to Go!

Once configured, your automation is ready to run. Each day project is independent and uses its own isolated API keys for maximum security and tracking granularity.

**Happy Automating! 🚀**
