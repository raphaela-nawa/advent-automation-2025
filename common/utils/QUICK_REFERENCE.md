# README Auto-Updater - Quick Reference Card

## TL;DR

**Execution time:** 0.02 seconds | **Memory:** < 5 MB | **Cost:** Free

---

## Three Ways to Use

### 1️⃣ Manual (Recommended to Start)

```bash
# Update README after completing a day
python common/utils/update_readme.py

# See what would change (dry run)
python common/utils/update_readme.py --dry-run

# Detailed output
python common/utils/update_readme.py --verbose
```

**When to use:** Learning phase, want explicit control

---

### 2️⃣ Git Hook (Set and Forget)

```bash
# One-time setup
python common/utils/update_readme.py --setup-git-hook

# Now forget about it - README auto-updates on every commit
git commit -m "Complete Day 6"  # ← README updates here automatically
```

**When to use:** Daily workflow, want automation without thinking

**Computing overhead:** Adds 0.02s to each commit (unnoticeable)

---

### 3️⃣ GitHub Actions (Already Configured)

**No setup needed!** Already configured in `.github/workflows/update_readme.yml`

- Triggers automatically when you push `dayXX/` changes
- Runs on GitHub's servers (not your computer)
- Creates a new commit with updated README
- Takes ~10 seconds per run

**When to use:** Team projects, want cloud automation, don't mind extra commit

---

## What It Does

Scans your project folders and updates this table in README.md:

```markdown
| Day | Pillar | Project | Industry | Status | Code |
|-----|--------|---------|----------|--------|------|
| 6 | Modeling | TBD | TBD | 🚧 Planned | [Day 06](./day06) |
                           ↓ BECOMES ↓
| 6 | Modeling | Financial Metrics | Consulting | ✅ Complete | [Day 06](./day06) |
```

**Status detection:**
- ✅ **Complete:** Has `README.md` + `dayXX_*.py` files
- 🚧 **In Progress:** Has README OR code (not both)
- 🚧 **Planned:** Empty folder or doesn't exist

---

## Common Commands

```bash
# Preview changes before writing
python common/utils/update_readme.py --dry-run --verbose

# Just update (silent)
python common/utils/update_readme.py

# Install automatic updates on commit
python common/utils/update_readme.py --setup-git-hook

# Remove git hook (disable auto-update)
rm .git/hooks/pre-commit
```

---

## File Locations

```
advent-automation-2025/
├── README.md                              # ← Updated automatically
├── .github/workflows/update_readme.yml    # ← GitHub Actions config
└── common/utils/
    ├── update_readme.py                   # ← Main script
    ├── README_UPDATER.md                  # ← Full documentation
    └── QUICK_REFERENCE.md                 # ← This file
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Project not detected as complete | Ensure you have both `README.md` and `dayXX_*.py` files |
| Project name shows "TBD" | Add `# Day XX: Project Name` as first header in README |
| Industry shows "TBD" | Add `**Industry:** Name` in README |
| Git hook not working | Run: `python common/utils/update_readme.py --setup-git-hook` |
| Want to disable auto-update | Delete: `.git/hooks/pre-commit` |

---

## My Recommendation

**Week 1 (Days 1-5):**
```bash
# Run manually to learn
python common/utils/update_readme.py --verbose
```

**Week 2+ (Days 6-25):**
```bash
# Install once, forget forever
python common/utils/update_readme.py --setup-git-hook
```

**Computing effort:** Completely negligible. Runs in 0.02 seconds.

---

## Questions?

Read the full docs: [README_UPDATER.md](./README_UPDATER.md)
