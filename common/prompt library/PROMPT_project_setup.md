# 🎯 Context & Constraints
I'm working on the Christmas Advent Calendar Repository where each day (Day 01-25) is a standalone 3-hour project with complete isolation from other days.

**Critical Rules:**

✅ Each project lives in its own dayXX/ folder
✅ All files must be prefixed with dayXX_ to prevent cross-contamination
✅ Shared infrastructure (.env, root requirements.txt) already exists
✅ Never overwrite existing structure
✅ Only ADD day-specific files, never REPLACE root files

---

## 📝 Naming Convention Rules

### File Prefixes: (replace day01 for dayXX)

- `day01_DATA_*` → Data collection, scraping, processing
- `day01_PIPELINE_*` → Core logic, processing engines
- `day01_APP_*` → User-facing applications (Streamlit, etc)
- `day01_CONFIG_*` → Configuration, settings, constants
- `day01_DOCS_*` → Documentation, briefs, reports
- `day01_TEST_*` → Testing files (if needed)

### Variables & Classes:
```python
# ✅ CORRECT - Day-scoped
dayXX_REGISTRY_URL = "https://www.ibanet.org/..."

class dayXX_RegistryScraper:
    pass

def dayXX_process_resources():
    pass

# ❌ WRONG - Generic names cause conflicts
OPENAI_MODEL = "gpt-4"  # Could conflict with Day 02
class RegistryScraper:  # Too generic
```

### Environment Variables:
```bash
# In root .env (already exists)
OPENAI_API_KEY=sk-...
# Remember to create according to the convention of the existing .env file
# and to add specific keys for each project (remind me)

# Day-specific variables (if needed)
DAY01_REGISTRY_CACHE_TTL=3600
DAY01_MAX_SCRAPE_PAGES=50
```

---

## 🔧 Dependencies to ADD (not replace)

In root requirements.txt, append:
```txt
# Day 01: IBA Climate Registry Intelligence
beautifulsoup4==4.12.3
chromadb==0.4.22
```

**Do NOT:**
- Remove existing dependencies
- Duplicate dependencies already present
- Reorganize the file

If needed, create a `dayXX_requirements.txt` to highlight that certain specific libraries were used for that context.
