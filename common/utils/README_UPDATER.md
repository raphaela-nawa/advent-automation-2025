# README Auto-Updater Documentation

## Overview

The README auto-updater keeps your main README.md synchronized with your project progress by automatically scanning day folders and updating the project table.

## Computing Effort

**Very Lightweight:**
- **Execution time:** < 1 second (typically 0.1-0.3s)
- **Memory usage:** < 5 MB
- **Disk I/O:** Reads ~25 files (one README per day folder)
- **Network:** None (runs locally or on GitHub's servers)

**Cost Analysis:**
- **Manual runs:** Free, instant, no server needed
- **Git hook:** Free, adds ~0.1s to each commit
- **GitHub Actions:** Free tier includes 2,000 minutes/month (this uses ~0.2 min per run)

## Usage Options

### Option 1: Manual Run (Recommended for Start)

Run manually after completing each day's project:

```bash
# Update README
python common/utils/update_readme.py

# Preview changes first (dry run)
python common/utils/update_readme.py --dry-run

# Verbose output (see what's happening)
python common/utils/update_readme.py --verbose
```

**Pros:**
- Full control over when updates happen
- See exactly what changed
- No setup required

**Cons:**
- You have to remember to run it
- Manual step in your workflow

**Best for:** Starting out, or if you want explicit control

---

### Option 2: Git Pre-Commit Hook (Automatic on Commit)

Install once, then README auto-updates whenever you commit:

```bash
# One-time setup
python common/utils/update_readme.py --setup-git-hook

# Now README updates automatically on every commit
git add day06/
git commit -m "Complete Day 6"  # README updates automatically here
```

**How it works:**
1. You commit code changes
2. Git runs the pre-commit hook automatically
3. Script scans projects and updates README
4. Updated README is added to your commit
5. Commit proceeds normally

**Pros:**
- Completely automatic
- Zero extra effort after setup
- README always in sync with code

**Cons:**
- Adds ~0.1s to each commit
- All commits trigger update (even non-project commits)

**Best for:** Once you're comfortable with the script, this is ideal

---

### Option 3: GitHub Actions (Automatic on Push)

Automatically updates README when you push to GitHub:

**Setup:**
1. The workflow file is already created at `.github/workflows/update_readme.yml`
2. Push to GitHub - it works automatically!

**How it works:**
1. You push code to GitHub
2. GitHub Actions triggers the workflow
3. Workflow runs the update script
4. If README changed, GitHub commits and pushes it back
5. You pull the updated README next time

**Pros:**
- Zero local overhead
- Works even if you forget to run locally
- Visual feedback in GitHub Actions tab
- Good for team collaboration

**Cons:**
- Requires GitHub repository
- Small delay (10-30 seconds after push)
- Creates an extra commit for README update

**Best for:** Public repos, team projects, or if you want hands-off automation

---

## What the Script Detects

The updater automatically determines project status by scanning:

1. **Folder existence:** `day01/`, `day02/`, etc.
2. **README presence:** `dayXX/README.md` exists
3. **Code files:** Any `dayXX_*.py` files present
4. **Project metadata:** Extracts title and industry from README

**Status Logic:**
- ✅ **Complete:** Has README + code files
- 🚧 **In Progress:** Has README OR code (but not both)
- 🚧 **Planned:** No README or code yet

**Metadata Extraction:**
```markdown
# Day 06: Financial Consulting Metrics
# ↑ Extracted as project name

**Industry:** Financial Consulting
# ↑ Extracted as industry
```

---

## Examples

### Example 1: Manual Update After Completing Day 6

```bash
$ python common/utils/update_readme.py --verbose

Scanning project folders...
  ✅ Day 01: GA4 + Google Ads → BigQuery (✅ Complete)
  ✅ Day 02: Meta Analytics & LTV (✅ Complete)
  ✅ Day 03: GDPR Lead Ingestion Webhook (✅ Complete)
  ✅ Day 04: Cardano Blockchain Transparency (✅ Complete)
  🚧 Day 05: TBD (🚧 Planned)
  ✅ Day 06: Financial Consulting Metrics Layer (✅ Complete)  # NEW!
  🚧 Day 07: TBD (🚧 Planned)
  ...

✅ README.md updated successfully!
   Backup saved to: README.md.backup

📊 Project Status Summary:
   ✅ Complete:     6/25
   🚧 In Progress:  0/25
   🚧 Planned:      19/25

⏱️  Execution time: 0.089 seconds
```

### Example 2: Dry Run (Preview Changes)

```bash
$ python common/utils/update_readme.py --dry-run --verbose

Scanning project folders...
  ...

============================================================
CHANGES TO BE MADE:
============================================================

OLD TABLE:
| 6 | Modeling | TBD | TBD | 🚧 Planned | [Day 06](./day06) |

NEW TABLE:
| 6 | Modeling | Financial Consulting Metrics Layer | Financial Consulting | ✅ Complete | [Day 06](./day06) |

============================================================

🔍 DRY RUN: No files were modified.
```

### Example 3: Git Hook in Action

```bash
# After installing git hook
$ git add day06/
$ git commit -m "Complete Day 6: Financial metrics layer"

🔄 Auto-updating README.md...
Scanning project folders...
  ✅ Day 06: Financial Consulting Metrics Layer (✅ Complete)

✅ README.md updated successfully!
📝 README.md was updated. Adding to commit...
✅ README.md staged for commit.

[main abc1234] Complete Day 6: Financial metrics layer
 15 files changed, 350 insertions(+), 5 deletions(-)
```

---

## Troubleshooting

### Problem: Script doesn't detect my project as complete

**Solution:** Check that you have:
1. A `README.md` in `dayXX/` folder
2. At least one `dayXX_*.py` file
3. The README starts with `# Day XX: Project Name`

### Problem: Project name shows as "TBD"

**Solution:** Make sure your README has this format:
```markdown
# Day 06: Your Project Name Here
```

### Problem: Industry shows as "TBD"

**Solution:** Add industry info in your README:
```markdown
**Industry:** Your Industry Here
```
Or use the template format:
```markdown
**Built For:** Name
**Role/Context:** Industry/Context
```

### Problem: Git hook isn't running

**Solution:**
1. Check hook exists: `ls -la .git/hooks/pre-commit`
2. Check it's executable: `chmod +x .git/hooks/pre-commit`
3. Reinstall: `python common/utils/update_readme.py --setup-git-hook`

### Problem: GitHub Actions not triggering

**Solution:**
1. Check workflow file exists: `.github/workflows/update_readme.yml`
2. Push changes to `main` branch (not other branches)
3. Make changes to `dayXX/` folders (not just README)
4. Check Actions tab on GitHub for error messages

---

## Customization

### Change Status Logic

Edit `scan_project()` method in `update_readme.py`:

```python
# Current logic
if has_readme and has_code:
    status = "✅ Complete"

# Custom: Require tests too
if has_readme and has_code and has_tests:
    status = "✅ Complete"
```

### Change Metadata Extraction

Edit `scan_project()` method to look for different patterns:

```python
# Add custom industry detection
industry_patterns = [
    r'\*\*Industry[:\s]+\*\*\s*(.+)',
    r'YOUR_CUSTOM_PATTERN_HERE',  # Add here
]
```

### Add Progress Percentage

The script already calculates completion. You could add to README:

```python
# In update_readme() after writing table
progress = f"\n\n**Progress:** {complete_count}/25 projects complete ({complete_count*4}%)\n"
```

---

## Performance Optimization

Already optimized, but if you have concerns:

### Reduce Scan Scope

Only scan changed folders:

```bash
# Only check Day 6
python update_readme.py --day 6  # (Would need to implement)
```

### Cache Results

For very large repos, add caching:

```python
# Cache project info for 1 hour
@functools.lru_cache(maxsize=128)
def scan_project_cached(day: int) -> ProjectInfo:
    return scan_project(day)
```

---

## Recommendation: Which Option to Use?

**Week 1 (Days 1-5):** Manual runs
- Learn how the script works
- See what it detects
- Build confidence

**Week 2-3 (Days 6-15):** Git hook
- Install: `python common/utils/update_readme.py --setup-git-hook`
- Forget about it - README auto-updates

**Week 4+ (Days 16-25):** Keep git hook OR add GitHub Actions
- Git hook is usually enough
- Add GitHub Actions if working with team or want backup automation

---

## FAQ

**Q: Does this work offline?**
A: Yes! Manual runs and git hooks work 100% offline. Only GitHub Actions requires internet.

**Q: Will it slow down my commits?**
A: Negligible. Adds ~0.1 seconds. You won't notice it.

**Q: What if I don't want auto-updates?**
A: Just run manually when needed. Don't install the git hook.

**Q: Can it break my README?**
A: Very unlikely. It creates a backup before every write (`README.md.backup`). You can always restore.

**Q: Does it modify my day folders?**
A: No. Read-only. It only reads from `dayXX/` folders and writes to `README.md`.

**Q: What about merge conflicts?**
A: If you and GitHub Actions both update README, you'll get a conflict. Just keep your local version or pull before pushing.

---

## Summary

| Method | Computing Effort | Setup | Best For |
|--------|-----------------|-------|----------|
| **Manual** | 0.1s per run | None | Learning, explicit control |
| **Git Hook** | 0.1s per commit | 1 command | Daily use, automatic updates |
| **GitHub Actions** | 10s per push (on GitHub) | Already set up | Team projects, backup automation |

**Recommended workflow:**
1. Start with manual runs (first week)
2. Install git hook after you're comfortable
3. Optionally enable GitHub Actions for extra automation

All three options are lightweight and won't impact your workflow performance!
