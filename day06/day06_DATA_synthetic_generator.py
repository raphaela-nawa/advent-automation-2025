#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 06: Financial Consulting Metrics

This script builds a SQLite database with realistic consulting projects,
timesheets, and expenses to support downstream metric modeling.

Usage:
    python day06_DATA_synthetic_generator.py
"""

import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from day06_CONFIG_settings import (
    DAY06_CONSULTANT_TIERS as DAY06_TIERS,
    DAY06_CONTRACT_TYPES as DAY06_CONTRACTS,
    DAY06_CURRENCY_FORMAT,
    DAY06_DB_PATH,
    DAY06_DB_PATH_STR,
    DAY06_EXPENSE_TYPES,
    DAY06_MAX_EXPENSE_AMOUNT as DAY06_EXP_MAX,
    DAY06_MAX_HOURS_PER_DAY,
    DAY06_MAX_HOURLY_RATE,
    DAY06_MAX_PROJECT_BUDGET,
    DAY06_MAX_PROJECT_DURATION_DAYS,
    DAY06_MAX_TIMESHEETS_PER_PROJECT,
    DAY06_MIN_EXPENSE_AMOUNT as DAY06_EXP_MIN,
    DAY06_MIN_EXPENSES_PER_PROJECT,
    DAY06_MIN_HOURS_PER_DAY,
    DAY06_MIN_HOURLY_RATE,
    DAY06_MIN_PROJECT_BUDGET,
    DAY06_MIN_PROJECT_DURATION_DAYS,
    DAY06_MIN_TIMESHEETS_PER_PROJECT,
    DAY06_NUM_CLIENTS,
    DAY06_NUM_CONSULTANTS,
    DAY06_NUM_PROJECTS,
    DAY06_PROJECT_END_DATE,
    DAY06_PROJECT_NAMES,
    DAY06_PROJECT_START_DATE,
    DAY06_PROJECT_STATUSES,
    DAY06_REIMBURSABLE_PERCENTAGE,
    DAY06_TASK_DESCRIPTIONS,
    DAY06_MAX_EXPENSES_PER_PROJECT,
)

# Reproducible output for deterministic test runs
random.seed(42)


@dataclass
class Day06Consultant:
    """Consultant profile with utilization tendencies."""

    consultant_id: str
    tier: str
    billable_probability: float
    hourly_rate: float


def day06_random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random date between start and end inclusive."""
    delta_days = (end - start).days
    offset = random.randint(0, delta_days)
    return start + timedelta(days=offset)


def day06_format_currency(amount: float) -> str:
    """Local helper to avoid circular imports while keeping consistent format."""
    return DAY06_CURRENCY_FORMAT.format(symbol="$", amount=amount)


def day06_initialize_db(db_path: Path) -> sqlite3.Connection:
    """Create/replace the SQLite database and ensure FK enforcement."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def day06_create_tables(conn: sqlite3.Connection) -> None:
    """Create tables and supporting indexes."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS day06_projects (
            project_id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            project_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            budget_usd REAL NOT NULL CHECK (budget_usd > 0),
            contract_type TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS day06_timesheets (
            timesheet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            consultant_id TEXT NOT NULL,
            date TEXT NOT NULL,
            hours_worked REAL NOT NULL CHECK (hours_worked > 0),
            is_billable INTEGER NOT NULL CHECK (is_billable IN (0, 1)),
            hourly_rate_usd REAL NOT NULL CHECK (hourly_rate_usd > 0),
            task_description TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES day06_projects (project_id)
        );

        CREATE TABLE IF NOT EXISTS day06_expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            expense_type TEXT NOT NULL,
            amount_usd REAL NOT NULL CHECK (amount_usd > 0),
            is_reimbursable INTEGER NOT NULL CHECK (is_reimbursable IN (0, 1)),
            FOREIGN KEY (project_id) REFERENCES day06_projects (project_id)
        );

        CREATE INDEX IF NOT EXISTS idx_day06_timesheets_project
            ON day06_timesheets (project_id);
        CREATE INDEX IF NOT EXISTS idx_day06_timesheets_consultant
            ON day06_timesheets (consultant_id);
        CREATE INDEX IF NOT EXISTS idx_day06_expenses_project
            ON day06_expenses (project_id);
        """
    )


def day06_generate_clients(num_clients: int) -> List[str]:
    """Create client identifiers like CLIENT-A, CLIENT-B, ..."""
    base_char = ord("A")
    return [f"CLIENT-{chr(base_char + i)}" for i in range(num_clients)]


def day06_generate_projects(
    num_projects: int, clients: List[str]
) -> List[Dict[str, str]]:
    """Generate project records with budgets and timelines."""
    start_range = datetime.fromisoformat(DAY06_PROJECT_START_DATE)
    end_range = datetime.fromisoformat(DAY06_PROJECT_END_DATE)
    total_days = (end_range - start_range).days

    project_names = random.sample(DAY06_PROJECT_NAMES, num_projects)
    projects: List[Dict[str, str]] = []
    for idx in range(num_projects):
        project_id = f"PROJ-{idx+1:03d}"
        start_date = start_range + timedelta(days=random.randint(0, total_days))
        duration_days = random.randint(
            DAY06_MIN_PROJECT_DURATION_DAYS, DAY06_MAX_PROJECT_DURATION_DAYS
        )
        end_date = start_date + timedelta(days=duration_days)
        budget_usd = random.randint(DAY06_MIN_PROJECT_BUDGET, DAY06_MAX_PROJECT_BUDGET)

        projects.append(
            {
                "project_id": project_id,
                "client_id": random.choice(clients),
                "project_name": project_names[idx],
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "budget_usd": budget_usd,
                "contract_type": random.choice(DAY06_CONTRACTS),
                "status": random.choices(
                    population=DAY06_PROJECT_STATUSES,
                    weights=[0.45, 0.4, 0.15],
                    k=1,
                )[0],
            }
        )
    return projects


def day06_build_consultant_profiles() -> List[Day06Consultant]:
    """Create consultant records with utilization tendencies."""
    consultants: List[Day06Consultant] = []
    consultant_idx = 1
    for tier_name, tier_config in DAY06_TIERS.items():
        for _ in range(tier_config["count"]):
            consultant_id = f"CONS-{consultant_idx:03d}"
            billable_probability = round(
                random.uniform(*tier_config["billable_rate"]), 2
            )
            hourly_rate = round(random.uniform(*tier_config["hourly_rate_range"]), 2)
            consultants.append(
                Day06Consultant(
                    consultant_id=consultant_id,
                    tier=tier_name,
                    billable_probability=billable_probability,
                    hourly_rate=hourly_rate,
                )
            )
            consultant_idx += 1
    return consultants


def day06_assign_project_profiles(
    projects: List[Dict[str, str]],
) -> Dict[str, Dict[str, float]]:
    """
    Assign profitability/utilization profiles to projects.

    Some projects are forced into edge cases: zero expenses,
    all-billable, or intentionally low-margin.
    """
    profile_templates = [
        {
            "name": "premium",
            "billable_bias": 0.12,
            "expense_multiplier": 0.7,
            "tier_weights": {"high_performer": 0.5, "average": 0.4, "below_target": 0.1},
        },
        {
            "name": "steady",
            "billable_bias": 0.0,
            "expense_multiplier": 1.0,
            "tier_weights": {"high_performer": 0.35, "average": 0.5, "below_target": 0.15},
        },
        {
            "name": "troubled",
            "billable_bias": -0.15,
            "expense_multiplier": 1.35,
            "tier_weights": {"high_performer": 0.25, "average": 0.45, "below_target": 0.3},
        },
    ]

    project_ids = [proj["project_id"] for proj in projects]
    special_ids = random.sample(project_ids, 3)
    zero_expense_id, all_billable_id, low_margin_id = special_ids

    profile_map: Dict[str, Dict[str, float]] = {}
    for project_id in project_ids:
        base_profile = random.choice(profile_templates).copy()
        base_profile["force_all_billable"] = False
        base_profile["skip_expenses"] = False

        if project_id == zero_expense_id:
            base_profile["skip_expenses"] = True
            base_profile["expense_multiplier"] = 0.0
            base_profile["name"] = "zero_expense"
        if project_id == all_billable_id:
            base_profile["force_all_billable"] = True
            base_profile["billable_bias"] = 0.25
            base_profile["name"] = "all_billable"
        if project_id == low_margin_id:
            base_profile["billable_bias"] = -0.3
            base_profile["expense_multiplier"] *= 1.6
            base_profile["name"] = "low_margin"

        profile_map[project_id] = base_profile
    return profile_map


def day06_distribute_counts(
    ids: Iterable[str],
    target_total: int,
    min_per: int,
    max_per: int,
    zero_allowed: Iterable[str] = (),
) -> Dict[str, int]:
    """Distribute counts across IDs while respecting min/max and total target."""
    ids_list = list(ids)
    zero_set = set(zero_allowed)
    counts = {pid: (0 if pid in zero_set else min_per) for pid in ids_list}
    base_total = sum(counts.values())

    capacity = sum((0 if pid in zero_set else max_per) for pid in ids_list)
    if target_total > capacity:
        target_total = capacity
    if target_total < base_total:
        target_total = base_total

    remaining = target_total - base_total
    while remaining > 0:
        random.shuffle(ids_list)
        progress = False
        for pid in ids_list:
            if remaining <= 0:
                break
            current = counts[pid]
            upper = 0 if pid in zero_set else max_per
            if current >= upper:
                continue
            add_cap = upper - current
            add = random.randint(0, min(add_cap, remaining))
            if add > 0:
                counts[pid] += add
                remaining -= add
                progress = True
        if not progress:
            break
    return counts


def day06_choose_consultant(
    profile: Dict[str, float],
    consultants_by_tier: Dict[str, List[Day06Consultant]],
) -> Day06Consultant:
    """Pick a consultant using tier weights from project profile."""
    tier_weights = profile.get("tier_weights", {})
    tier_order = list(DAY06_TIERS.keys())
    weights = [tier_weights.get(tier, 1 / len(tier_order)) for tier in tier_order]
    chosen_tier = random.choices(tier_order, weights=weights, k=1)[0]
    return random.choice(consultants_by_tier[chosen_tier])


def day06_generate_timesheets(
    projects: List[Dict[str, str]],
    consultants: List[Day06Consultant],
    timesheet_counts: Dict[str, int],
    project_profiles: Dict[str, Dict[str, float]],
) -> Tuple[List[Tuple], Dict[str, float]]:
    """Generate timesheet rows and aggregated metrics."""
    consultants_by_tier: Dict[str, List[Day06Consultant]] = {
        tier: [] for tier in DAY06_TIERS.keys()
    }
    for consultant in consultants:
        consultants_by_tier[consultant.tier].append(consultant)

    timesheets: List[Tuple] = []
    project_hours: Dict[str, float] = {}
    project_billable_hours: Dict[str, float] = {}
    consultant_hours: Dict[str, Dict[str, float]] = {}
    billable_revenue = 0.0

    for project in projects:
        project_id = project["project_id"]
        num_entries = timesheet_counts[project_id]
        profile = project_profiles[project_id]

        start_dt = datetime.fromisoformat(project["start_date"])
        end_dt = datetime.fromisoformat(project["end_date"])
        max_possible = num_entries * DAY06_MAX_HOURS_PER_DAY
        target_hours = random.randint(50, max(50, min(200, max_possible)))

        remaining_hours = float(target_hours)
        for entry_idx in range(num_entries):
            consultant = day06_choose_consultant(profile, consultants_by_tier)
            base_prob = consultant.billable_probability
            adjusted_prob = min(
                1.0, max(0.0, base_prob + profile.get("billable_bias", 0.0))
            )
            is_billable = (
                1
                if profile.get("force_all_billable")
                else int(random.random() < adjusted_prob)
            )

            entries_left = num_entries - entry_idx
            min_remaining = DAY06_MIN_HOURS_PER_DAY * (entries_left - 1)
            min_current = max(
                DAY06_MIN_HOURS_PER_DAY,
                remaining_hours - DAY06_MAX_HOURS_PER_DAY * (entries_left - 1),
            )
            max_current = min(
                DAY06_MAX_HOURS_PER_DAY, remaining_hours - min_remaining
            )
            if entries_left == 1:
                hours_worked = round(
                    max(
                        DAY06_MIN_HOURS_PER_DAY,
                        min(DAY06_MAX_HOURS_PER_DAY, remaining_hours),
                    ),
                    2,
                )
            else:
                hours_worked = round(random.uniform(min_current, max_current), 2)

            remaining_hours = max(0.0, remaining_hours - hours_worked)

            hourly_rate = round(
                random.uniform(
                    max(DAY06_MIN_HOURLY_RATE, consultant.hourly_rate - 10),
                    min(DAY06_MAX_HOURLY_RATE, consultant.hourly_rate + 10),
                ),
                2,
            )

            work_date = day06_random_date(start_dt, end_dt).date().isoformat()
            task_description = random.choice(DAY06_TASK_DESCRIPTIONS)

            timesheets.append(
                (
                    project_id,
                    consultant.consultant_id,
                    work_date,
                    hours_worked,
                    is_billable,
                    hourly_rate,
                    task_description,
                )
            )

            project_hours[project_id] = project_hours.get(project_id, 0.0) + hours_worked
            if is_billable:
                project_billable_hours[project_id] = project_billable_hours.get(
                    project_id, 0.0
                ) + hours_worked
                billable_revenue += hours_worked * hourly_rate

            stats = consultant_hours.setdefault(
                consultant.consultant_id, {"total": 0.0, "billable": 0.0}
            )
            stats["total"] += hours_worked
            if is_billable:
                stats["billable"] += hours_worked

    summary = {
        "total_entries": len(timesheets),
        "total_hours": sum(project_hours.values()),
        "billable_hours": sum(project_billable_hours.values()),
        "billable_revenue": billable_revenue,
        "project_hours": project_hours,
        "project_billable_hours": project_billable_hours,
        "consultant_hours": consultant_hours,
    }
    return timesheets, summary


def day06_generate_expenses(
    projects: List[Dict[str, str]],
    project_profiles: Dict[str, Dict[str, float]],
    expense_counts: Dict[str, int],
) -> Tuple[List[Tuple], Dict[str, float]]:
    """Generate expense rows based on project profiles."""
    expenses: List[Tuple] = []
    total_expenses = 0.0
    reimbursable_total = 0.0

    for project in projects:
        project_id = project["project_id"]
        profile = project_profiles[project_id]
        count = expense_counts.get(project_id, 0)
        if count == 0 or profile.get("skip_expenses"):
            continue

        start_dt = datetime.fromisoformat(project["start_date"])
        end_dt = datetime.fromisoformat(project["end_date"])

        for _ in range(count):
            base_amount = random.uniform(DAY06_EXP_MIN, DAY06_EXP_MAX)
            amount = round(
                min(DAY06_EXP_MAX, base_amount * profile.get("expense_multiplier", 1.0)),
                2,
            )
            is_reimbursable = int(random.random() < DAY06_REIMBURSABLE_PERCENTAGE)
            expense_date = day06_random_date(start_dt, end_dt).date().isoformat()

            expenses.append(
                (
                    project_id,
                    expense_date,
                    random.choice(DAY06_EXPENSE_TYPES),
                    amount,
                    is_reimbursable,
                )
            )

            total_expenses += amount
            if is_reimbursable:
                reimbursable_total += amount

    summary = {
        "total_entries": len(expenses),
        "total_expenses": total_expenses,
        "reimbursable_total": reimbursable_total,
    }
    return expenses, summary


def day06_insert_data(
    conn: sqlite3.Connection,
    projects: List[Dict[str, str]],
    timesheets: List[Tuple],
    expenses: List[Tuple],
) -> None:
    """Persist generated data into SQLite."""
    conn.executemany(
        """
        INSERT INTO day06_projects (
            project_id, client_id, project_name, start_date, end_date,
            budget_usd, contract_type, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                project["project_id"],
                project["client_id"],
                project["project_name"],
                project["start_date"],
                project["end_date"],
                project["budget_usd"],
                project["contract_type"],
                project["status"],
            )
            for project in projects
        ],
    )

    conn.executemany(
        """
        INSERT INTO day06_timesheets (
            project_id, consultant_id, date, hours_worked, is_billable,
            hourly_rate_usd, task_description
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        timesheets,
    )

    conn.executemany(
        """
        INSERT INTO day06_expenses (
            project_id, expense_date, expense_type, amount_usd, is_reimbursable
        ) VALUES (?, ?, ?, ?, ?)
        """,
        expenses,
    )
    conn.commit()


def day06_validate_database(
    conn: sqlite3.Connection,
    db_path: Path,
    timesheet_counts: Dict[str, int],
    expense_counts: Dict[str, int],
) -> None:
    """Run post-generation validation checks."""
    cur = conn.cursor()

    fk_issues = cur.execute(
        """
        SELECT COUNT(*) FROM day06_timesheets t
        LEFT JOIN day06_projects p ON t.project_id = p.project_id
        WHERE p.project_id IS NULL
        """
    ).fetchone()[0]
    if fk_issues:
        raise ValueError("Foreign key validation failed for timesheets.")

    date_issues = cur.execute(
        """
        SELECT COUNT(*) FROM day06_timesheets t
        JOIN day06_projects p ON t.project_id = p.project_id
        WHERE t.date < p.start_date OR t.date > p.end_date
        """
    ).fetchone()[0]
    if date_issues:
        raise ValueError("Timesheet dates fall outside project ranges.")

    expense_date_issues = cur.execute(
        """
        SELECT COUNT(*) FROM day06_expenses e
        JOIN day06_projects p ON e.project_id = p.project_id
        WHERE e.expense_date < p.start_date OR e.expense_date > p.end_date
        """
    ).fetchone()[0]
    if expense_date_issues:
        raise ValueError("Expense dates fall outside project ranges.")

    negative_amounts = cur.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT budget_usd AS amount FROM day06_projects
            UNION ALL
            SELECT amount_usd FROM day06_expenses
            UNION ALL
            SELECT hourly_rate_usd FROM day06_timesheets
            UNION ALL
            SELECT hours_worked FROM day06_timesheets
        ) WHERE amount <= 0
        """
    ).fetchone()[0]
    if negative_amounts:
        raise ValueError("Non-positive amounts detected in generated data.")

    projects_with_both = cur.execute(
        """
        SELECT COUNT(*) FROM day06_projects p
        WHERE EXISTS (SELECT 1 FROM day06_timesheets t WHERE t.project_id = p.project_id)
          AND EXISTS (SELECT 1 FROM day06_expenses e WHERE e.project_id = p.project_id)
        """
    ).fetchone()[0]
    total_projects = cur.execute("SELECT COUNT(*) FROM day06_projects").fetchone()[0]
    if projects_with_both < total_projects / 2:
        raise ValueError("Less than 50% of projects have both timesheets and expenses.")

    too_few_timesheets = [
        pid for pid, count in timesheet_counts.items() if count < DAY06_MIN_TIMESHEETS_PER_PROJECT
    ]
    too_many_timesheets = [
        pid for pid, count in timesheet_counts.items() if count > DAY06_MAX_TIMESHEETS_PER_PROJECT
    ]
    if too_few_timesheets or too_many_timesheets:
        raise ValueError("Timesheet counts per project outside expected bounds.")

    if db_path.stat().st_size <= 0 or db_path.stat().st_size >= 1_000_000:
        raise ValueError("Database file size validation failed.")

    # Ensure expense counts match expectations (allows zero for flagged projects).
    for pid, count in expense_counts.items():
        if count not in range(0, DAY06_MAX_EXPENSES_PER_PROJECT + 1):
            raise ValueError("Expense counts per project outside expected bounds.")


def day06_print_summary(
    projects: List[Dict[str, str]],
    timesheet_summary: Dict[str, float],
    expense_summary: Dict[str, float],
) -> None:
    """Display generation summary and top consultants."""
    budgets = [p["budget_usd"] for p in projects]
    total_budget = sum(budgets)
    billable_hours = timesheet_summary["billable_hours"]
    total_hours = max(timesheet_summary["total_hours"], 1e-6)
    billable_pct = (billable_hours / total_hours) * 100

    reimbursable_total = expense_summary["reimbursable_total"]
    total_expenses = expense_summary["total_expenses"]
    reimbursable_pct = (
        (reimbursable_total / total_expenses) * 100 if total_expenses else 0.0
    )

    print("Generating synthetic consulting data...\n")
    print(f"Created {len(projects)} projects across {DAY06_NUM_CLIENTS} clients")
    print(
        f"  - Budget range: {day06_format_currency(min(budgets))} - "
        f"{day06_format_currency(max(budgets))}"
    )
    print(f"  - Total portfolio value: {day06_format_currency(total_budget)}\n")

    print(
        f"Generated {timesheet_summary['total_entries']} timesheet entries for {DAY06_NUM_CONSULTANTS} consultants"
    )
    print(
        f"  - Total hours: {timesheet_summary['total_hours']:.0f} hours"
        f"\n  - Billable hours: {billable_hours:.0f} ({billable_pct:.0f}%)"
        f"\n  - Revenue potential: {day06_format_currency(timesheet_summary['billable_revenue']):>}"
    )

    print(f"\nCreated {expense_summary['total_entries']} expense entries")
    print(
        f"  - Total expenses: {day06_format_currency(total_expenses)}"
        f"\n  - Reimbursable: {day06_format_currency(reimbursable_total)} ({reimbursable_pct:.0f}%)"
    )

    print(f"\nDatabase saved to: {DAY06_DB_PATH_STR}\n")

    consultant_hours = timesheet_summary["consultant_hours"]
    consultant_stats = []
    for consultant_id, stats in consultant_hours.items():
        total = stats["total"]
        billable = stats["billable"]
        pct = (billable / total) * 100 if total else 0.0
        consultant_stats.append((consultant_id, pct, total, billable))
    top_consultants = sorted(consultant_stats, key=lambda x: x[1], reverse=True)[:3]

    print("Top consultants by billable hours:")
    for cid, pct, total, billable in top_consultants:
        print(
            f"  {cid}: {pct:.0f}% billable ({billable:.0f} of {total:.0f} hours)"
        )


def main() -> None:
    """Entry point for synthetic data generation."""
    clients = day06_generate_clients(DAY06_NUM_CLIENTS)
    projects = day06_generate_projects(DAY06_NUM_PROJECTS, clients)
    consultants = day06_build_consultant_profiles()
    project_profiles = day06_assign_project_profiles(projects)

    # Timesheets: target volume in 200-300 range while keeping per-project bounds.
    timesheet_target_total = random.randint(200, 300)
    timesheet_counts = day06_distribute_counts(
        [p["project_id"] for p in projects],
        target_total=timesheet_target_total,
        min_per=DAY06_MIN_TIMESHEETS_PER_PROJECT,
        max_per=DAY06_MAX_TIMESHEETS_PER_PROJECT,
    )

    timesheets, timesheet_summary = day06_generate_timesheets(
        projects, consultants, timesheet_counts, project_profiles
    )

    # Expenses: keep a few zero-expense edge cases while hitting total range.
    expense_target_total = random.randint(55, 75)
    zero_expense_projects = {
        pid for pid, profile in project_profiles.items() if profile.get("skip_expenses")
    }
    expense_counts = day06_distribute_counts(
        [p["project_id"] for p in projects],
        target_total=expense_target_total,
        min_per=DAY06_MIN_EXPENSES_PER_PROJECT,
        max_per=DAY06_MAX_EXPENSES_PER_PROJECT,
        zero_allowed=zero_expense_projects,
    )

    expenses, expense_summary = day06_generate_expenses(
        projects, project_profiles, expense_counts
    )

    conn = day06_initialize_db(DAY06_DB_PATH)
    day06_create_tables(conn)
    day06_insert_data(conn, projects, timesheets, expenses)
    day06_validate_database(conn, DAY06_DB_PATH, timesheet_counts, expense_counts)
    day06_print_summary(projects, timesheet_summary, expense_summary)


if __name__ == "__main__":
    main()
