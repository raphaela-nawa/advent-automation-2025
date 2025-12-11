#!/usr/bin/env python3
"""
README.md Auto-Updater for Advent Automation 2025

This script automatically updates the main README.md file by:
1. Scanning all dayXX/ folders for completion status
2. Reading project metadata from each day's README
3. Updating the project table with current information

Usage:
    # Manual run (recommended daily after completing a project)
    python common/utils/update_readme.py

    # Dry run (preview changes without writing)
    python common/utils/update_readme.py --dry-run

    # Verbose output
    python common/utils/update_readme.py --verbose

Computing Effort:
    - Execution time: < 1 second (scans 25 folders, reads ~25 files)
    - Memory usage: < 5 MB (minimal file I/O)
    - Can be run manually or via git pre-commit hook

Automation Options:
    1. Manual: Run after completing each day's project
    2. Git Hook: Auto-run on git commit (see setup instructions below)
    3. GitHub Actions: Auto-run on push (see .github/workflows/update_readme.yml)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectInfo:
    """Represents information about a single day's project."""
    day: int
    pillar: str
    project_name: str
    industry: str
    status: str  # "✅ Complete" or "🚧 Planned"
    folder_path: Path
    has_readme: bool
    has_code: bool


class ReadmeUpdater:
    """Handles scanning projects and updating the main README."""

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize the updater.

        Args:
            repo_root: Path to repository root. Auto-detected if None.
        """
        if repo_root is None:
            # Auto-detect repo root (script is in common/utils/)
            self.repo_root = Path(__file__).parent.parent.parent
        else:
            self.repo_root = Path(repo_root)

        self.readme_path = self.repo_root / "README.md"

        # Pillar definitions
        self.pillars = {
            range(1, 6): "Ingestion",
            range(6, 11): "Modeling",
            range(11, 16): "Orchestration",
            range(16, 21): "Dashboards",
            range(21, 26): "AI Insights"
        }

    def get_pillar(self, day: int) -> str:
        """Get pillar name for a given day."""
        for day_range, pillar in self.pillars.items():
            if day in day_range:
                return pillar
        return "Unknown"

    def scan_project(self, day: int) -> ProjectInfo:
        """
        Scan a single day's project folder for metadata.

        Args:
            day: Day number (1-25)

        Returns:
            ProjectInfo with detected metadata
        """
        folder_path = self.repo_root / f"day{day:02d}"
        pillar = self.get_pillar(day)

        # Default values
        project_name = "TBD"
        industry = "TBD"
        status = "🚧 Planned"
        has_readme = False
        has_code = False

        # Check if folder exists
        if not folder_path.exists():
            return ProjectInfo(
                day=day,
                pillar=pillar,
                project_name=project_name,
                industry=industry,
                status=status,
                folder_path=folder_path,
                has_readme=False,
                has_code=False
            )

        # Check for README
        readme_path = folder_path / "README.md"
        if readme_path.exists():
            has_readme = True
            # Extract metadata from README
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()

                # Extract project title (first # header)
                # Support both "Day XX:" and "Day XX -" formats, and remove emojis
                title_match = re.search(r'^#\s+Day\s+\d+\s*[-:]\s*(.+)$', readme_content, re.MULTILINE)
                if title_match:
                    # Remove emojis and clean up
                    project_name = re.sub(r'[^\w\s\-&→+()/,.]', '', title_match.group(1)).strip()

                # Extract industry (look for various patterns)
                industry_patterns = [
                    # Pattern 1: **For:** Role/Industry | (highest priority, new template format)
                    r'\*\*For:\*\*\s*(.+?)\s*\|',
                    # Pattern 2: **For:** Name (Role/Industry)
                    r'\*\*For:\*\*\s*[^(]+\(([^)]+)\)',
                    # Pattern 3: **Stakeholder:** Name - Role/Industry
                    r'\*\*Stakeholder:\*\*\s*[^-]+-\s*([^(]+?)(?:\s+who\s+|$)',
                    # Pattern 4: **Industry:** or **Industry **
                    r'\*\*Industry[:\s]+\*\*\s*(.+)',
                    # Pattern 5: **Built For:** ... **Role/Context:**
                    r'\*\*Built For[:\s]+\*\*[^\n]*\n\*\*Role/Context[:\s]+\*\*\s*(.+)',
                    # Pattern 6: Table format
                    r'\|\s*\d+\s*\|\s*\w+\s*\|\s*[^|]+\|\s*(.+?)\s*\|',
                    # Pattern 7: One-line pitch or business problem with industry context
                    r'\*\*Business Problem:\*\*\s*([^.]+)',
                ]
                for pattern in industry_patterns:
                    industry_match = re.search(pattern, readme_content, re.IGNORECASE)
                    if industry_match:
                        industry = industry_match.group(1).strip()
                        # Clean up common prefixes/suffixes
                        industry = re.sub(r'^(Cultural\s+)', '', industry)
                        industry = re.sub(r'\s+(needs|requires|lacks).*$', '', industry)
                        break

            except Exception as e:
                print(f"Warning: Error reading README for day {day:02d}: {e}")

        # Check for code files (any .py files with dayXX_ prefix)
        has_code = any(
            f.name.startswith(f"day{day:02d}_") and f.suffix == '.py'
            for f in folder_path.iterdir()
            if f.is_file()
        )

        # Determine status
        if has_readme and has_code:
            status = "✅ Complete"
        elif has_readme or has_code:
            status = "🚧 In Progress"
        else:
            status = "🚧 Planned"

        return ProjectInfo(
            day=day,
            pillar=pillar,
            project_name=project_name,
            industry=industry,
            status=status,
            folder_path=folder_path,
            has_readme=has_readme,
            has_code=has_code
        )

    def scan_all_projects(self, verbose: bool = False) -> List[ProjectInfo]:
        """
        Scan all 25 day folders.

        Args:
            verbose: Print progress information

        Returns:
            List of ProjectInfo for all days
        """
        projects = []

        if verbose:
            print("Scanning project folders...")

        for day in range(1, 26):
            project = self.scan_project(day)
            projects.append(project)

            if verbose:
                status_icon = "✅" if project.status == "✅ Complete" else "🚧"
                print(f"  {status_icon} Day {day:02d}: {project.project_name} ({project.status})")

        return projects

    def generate_table_rows(self, projects: List[ProjectInfo]) -> str:
        """
        Generate markdown table rows for all projects.

        Args:
            projects: List of ProjectInfo

        Returns:
            Markdown table rows as string
        """
        rows = []

        for project in projects:
            row = (
                f"| {project.day} "
                f"| {project.pillar} "
                f"| {project.project_name} "
                f"| {project.industry} "
                f"| {project.status} "
                f"| [Day {project.day:02d}](./day{project.day:02d}) |"
            )
            rows.append(row)

        return "\n".join(rows)

    def update_readme(self, projects: List[ProjectInfo], dry_run: bool = False, verbose: bool = False) -> bool:
        """
        Update the main README.md file with project information.

        Args:
            projects: List of ProjectInfo
            dry_run: If True, print changes without writing
            verbose: Print detailed information

        Returns:
            True if README was updated (or would be updated in dry run)
        """
        if not self.readme_path.exists():
            print(f"Error: README.md not found at {self.readme_path}")
            return False

        # Read current README
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # Generate new table rows
        new_table_rows = self.generate_table_rows(projects)

        # Define table header and separator
        table_header = "| Day | Pillar | Project | Industry | Status | Code |"
        table_separator = "|-----|--------|---------|----------|--------|------|"
        table_start = f"{table_header}\n{table_separator}"

        # Find and replace the table
        # Pattern: Match from table header to the next --- or ## section
        pattern = re.compile(
            r'(\|\s*Day\s*\|\s*Pillar\s*\|.*?\n\|[-|]+\|.*?\n)(.*?)(?=\n---|\n##|$)',
            re.DOTALL
        )

        match = pattern.search(readme_content)
        if not match:
            print("Error: Could not find project table in README.md")
            print("Expected format:")
            print(table_header)
            print(table_separator)
            return False

        # Replace table content
        new_readme = pattern.sub(
            f"\\1{new_table_rows}\n",
            readme_content
        )

        # Check if content changed
        if new_readme == readme_content:
            if verbose:
                print("No changes detected. README is already up to date.")
            return False

        # Show diff if verbose
        if verbose or dry_run:
            print("\n" + "="*60)
            print("CHANGES TO BE MADE:")
            print("="*60)
            print("\nOLD TABLE:")
            print(match.group(2))
            print("\nNEW TABLE:")
            print(new_table_rows)
            print("\n" + "="*60)

        # Write changes (unless dry run)
        if not dry_run:
            # Backup original
            backup_path = self.readme_path.with_suffix('.md.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            # Write updated README
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_readme)

            if verbose:
                print(f"\n✅ README.md updated successfully!")
                print(f"   Backup saved to: {backup_path.name}")

            # Generate summary
            complete_count = sum(1 for p in projects if p.status == "✅ Complete")
            in_progress_count = sum(1 for p in projects if "Progress" in p.status)
            planned_count = sum(1 for p in projects if p.status == "🚧 Planned")

            print(f"\n📊 Project Status Summary:")
            print(f"   ✅ Complete:     {complete_count}/25")
            print(f"   🚧 In Progress:  {in_progress_count}/25")
            print(f"   🚧 Planned:      {planned_count}/25")

        else:
            print("\n🔍 DRY RUN: No files were modified.")

        return True

    def generate_git_hook(self) -> str:
        """
        Generate a pre-commit git hook script.

        Returns:
            Shell script content for git hook
        """
        return """#!/bin/bash
# Git pre-commit hook - Auto-update README.md
# This hook runs automatically before each commit

echo "🔄 Auto-updating README.md..."

# Run the update script
python common/utils/update_readme.py --verbose

# Check if README was modified
if git diff --name-only | grep -q "README.md"; then
    echo "📝 README.md was updated. Adding to commit..."
    git add README.md
    echo "✅ README.md staged for commit."
else
    echo "✅ README.md is already up to date."
fi

exit 0
"""


def setup_git_hook(repo_root: Path, verbose: bool = False):
    """
    Install git pre-commit hook to auto-update README.

    Args:
        repo_root: Path to repository root
        verbose: Print detailed information
    """
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"

    if hook_path.exists():
        print(f"⚠️  Git hook already exists at {hook_path}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    updater = ReadmeUpdater(repo_root)
    hook_content = updater.generate_git_hook()

    hook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    # Make executable
    os.chmod(hook_path, 0o755)

    print(f"✅ Git pre-commit hook installed at {hook_path}")
    print(f"   README.md will auto-update on every commit.")
    print(f"\nTo disable: rm {hook_path}")


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update README.md with current project status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update README
  python common/utils/update_readme.py

  # Preview changes without writing
  python common/utils/update_readme.py --dry-run

  # Install git hook for automatic updates
  python common/utils/update_readme.py --setup-git-hook

Computing Effort:
  - Execution time: < 1 second
  - Memory usage: < 5 MB
  - Safe to run automatically on every commit
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed information'
    )

    parser.add_argument(
        '--setup-git-hook',
        action='store_true',
        help='Install git pre-commit hook for automatic updates'
    )

    parser.add_argument(
        '--repo-root',
        type=Path,
        help='Path to repository root (auto-detected if not specified)'
    )

    args = parser.parse_args()

    # Initialize updater
    updater = ReadmeUpdater(repo_root=args.repo_root)

    # Setup git hook if requested
    if args.setup_git_hook:
        setup_git_hook(updater.repo_root, verbose=args.verbose)
        return

    # Scan projects
    start_time = datetime.now()
    projects = updater.scan_all_projects(verbose=args.verbose)
    scan_time = (datetime.now() - start_time).total_seconds()

    # Update README
    updated = updater.update_readme(
        projects,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    if args.verbose:
        print(f"\n⏱️  Execution time: {scan_time:.3f} seconds")

    # Exit code
    if args.dry_run:
        return 0
    elif updated:
        return 0
    else:
        return 1  # No changes made


if __name__ == "__main__":
    main()
