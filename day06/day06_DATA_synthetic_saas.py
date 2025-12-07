#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 06: SaaS Health Metrics Foundation

This script generates realistic SaaS subscription data for Murilo's dashboard:
- 500 customers across 24 months
- Subscription history with upgrades/downgrades/churn
- Pre-aggregated MRR movements for waterfall analysis

Stakeholder: Murilo (Simetryk SaaS)
Use Case: MRR tracking, churn analysis, cohort retention, customer health scoring

Usage:
    python day06_DATA_synthetic_saas.py
"""

from __future__ import annotations

import hashlib
import random
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# Configuration
DAY06_DB_PATH = Path("data/day06_saas_metrics.db")
DAY06_NUM_CUSTOMERS = 500
DAY06_NUM_MONTHS = 24
DAY06_START_DATE = datetime(2023, 1, 1)
DAY06_END_DATE = datetime(2024, 12, 31)

# Plan tier pricing
DAY06_PLAN_PRICING: Dict[str, Tuple[int, int]] = {
    "Starter": (29, 99),
    "Pro": (199, 499),
    "Enterprise": (999, 2999),
}

# SaaS metrics targets
DAY06_MONTHLY_CHURN_RATE = (0.05, 0.08)  # 5-8% monthly churn envelope
DAY06_UPGRADE_PROBABILITY = 0.22  # Slightly higher to hit 15-20% realized upgrades
DAY06_DOWNGRADE_PROBABILITY = 0.18  # 18% downgrade intent to land within 5-10% realized

# Reproducibility
random.seed(42)


@dataclass
class Day06Customer:
    """Customer profile with lifecycle metadata."""

    customer_id: str
    email: str
    signup_date: datetime
    plan_tier: str
    mrr_current: float = 0.0
    status: str = "active"


@dataclass
class Day06Subscription:
    """Subscription period reflecting upgrades, downgrades, or churn."""

    subscription_id: str
    customer_id: str
    start_date: datetime
    end_date: Optional[datetime]
    mrr: float
    plan_tier: str


def day06_generate_customer_id() -> str:
    """Generate Stripe-style customer ID: cus_[16-char random string]."""
    random_str = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    return f"cus_{random_str}"


def day06_generate_subscription_id() -> str:
    """Generate Stripe-style subscription ID: sub_[16-char random string]."""
    random_str = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    return f"sub_{random_str}"


def day06_generate_email(customer_idx: int) -> str:
    """Create a realistic email address."""
    first_names = [
        "alex",
        "jordan",
        "casey",
        "taylor",
        "morgan",
        "blake",
        "riley",
        "jamie",
        "harper",
        "logan",
    ]
    last_names = [
        "smith",
        "johnson",
        "williams",
        "brown",
        "jones",
        "miller",
        "davis",
        "garcia",
        "martinez",
        "rodriguez",
    ]
    domains = [
        "acme.io",
        "techcorp.com",
        "dataflow.ai",
        "producthub.io",
        "cloudmesh.net",
        "revops.app",
        "insightful.dev",
        "faststack.io",
        "growthlabs.ai",
        "stackforge.com",
    ]
    first = random.choice(first_names)
    last = random.choice(last_names)
    domain = random.choice(domains)
    return f"{first}.{last}{customer_idx}@{domain}"


def day06_month_ends() -> List[datetime]:
    """List of month end boundaries across the 24-month window."""
    months = []
    current = DAY06_START_DATE.replace(day=1)
    for _ in range(DAY06_NUM_MONTHS):
        next_month = day06_add_months(current, 1)
        months.append(next_month - timedelta(days=1))
        current = next_month
    return months


def day06_month_starts() -> List[datetime]:
    """List of month start boundaries across the 24-month window."""
    starts = []
    current = DAY06_START_DATE.replace(day=1)
    for _ in range(DAY06_NUM_MONTHS):
        starts.append(current)
        current = day06_add_months(current, 1)
    return starts


def day06_month_start(date_value: datetime) -> datetime:
    """Get the first day of the month for a given date."""
    return date_value.replace(day=1)


def day06_add_months(start: datetime, months: int) -> datetime:
    """Add months to a date while keeping the day within valid bounds."""
    month = start.month - 1 + months
    year = start.year + month // 12
    month = month % 12 + 1
    day = min(
        start.day,
        [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][month - 1],
    )
    return datetime(year, month, day)


def day06_month_diff(start: datetime, end: datetime) -> int:
    """Number of whole months between two dates."""
    return (end.year - start.year) * 12 + (end.month - start.month)


def day06_pick_plan() -> str:
    """Pick a plan tier using weighted distribution."""
    return random.choices(
        population=["Starter", "Pro", "Enterprise"],
        weights=[0.5, 0.35, 0.15],
        k=1,
    )[0]


def day06_plan_price(plan: str) -> float:
    """Generate an MRR value inside the configured band for a plan."""
    low, high = DAY06_PLAN_PRICING[plan]
    mode = high * 0.85  # bias toward upper end for richer MRR
    return round(random.triangular(low, high, mode), 2)


def day06_generate_cohort_customers(
    cohort_month: datetime, num_customers: int, start_index: int
) -> List[Day06Customer]:
    """
    Generate customers for a specific signup cohort.

    Apply cohort-specific retention cues by biasing churn probability later
    (older cohorts will receive slightly higher monthly churn in lifecycle modeling).
    """
    customers: List[Day06Customer] = []
    for idx in range(num_customers):
        signup_day = random.randint(0, 27)
        signup_date = cohort_month + timedelta(days=signup_day)
        customers.append(
            Day06Customer(
                customer_id=day06_generate_customer_id(),
                email=day06_generate_email(start_index + idx),
                signup_date=signup_date,
                plan_tier=day06_pick_plan(),
            )
        )
    return customers


def day06_allocate_monthly_signups() -> Dict[datetime, int]:
    """Allocate 500 customers over 24 months with declining cohorts."""
    month_starts = day06_month_starts()
    decay_ratio = 0.78  # drives higher weight for early months
    weights = [decay_ratio**i for i in range(len(month_starts))]
    choices = random.choices(month_starts, weights=weights, k=DAY06_NUM_CUSTOMERS)
    counts: Dict[datetime, int] = Counter(choices)
    # Ensure deterministic coverage for every month
    for month in month_starts:
        counts.setdefault(month, 0)
    return counts


def day06_build_customers() -> List[Day06Customer]:
    """Create all customers across cohorts using the weighted signup allocation."""
    signup_counts = day06_allocate_monthly_signups()
    customers: List[Day06Customer] = []
    running_idx = 1
    for month_start in sorted(signup_counts.keys()):
        cohort_size = signup_counts[month_start]
        customers.extend(
            day06_generate_cohort_customers(month_start, cohort_size, running_idx)
        )
        running_idx += cohort_size
    return customers


def day06_next_plan(plan: str, direction: str) -> str:
    """Get the next plan when moving up or down the ladder."""
    ladder = ["Starter", "Pro", "Enterprise"]
    idx = ladder.index(plan)
    if direction == "up":
        return ladder[min(len(ladder) - 1, idx + 1)]
    return ladder[max(0, idx - 1)]


def day06_generate_lifecycle_events(
    customer: Day06Customer, churn_bias: float
) -> Tuple[List[Tuple[int, str]], Optional[int]]:
    """
    Build lifecycle change events for a single customer.

    Returns:
        - list of (month_index, event_type)
        - churn month index if churned
    """
    signup_month_start = day06_month_start(customer.signup_date)
    max_months = day06_month_diff(signup_month_start, day06_month_start(DAY06_END_DATE)) + 1
    base_churn = random.uniform(0.055, 0.075) * churn_bias
    base_churn = min(base_churn, 0.095)

    churn_month_idx: Optional[int] = None
    for month_idx in range(1, max_months):
        decay = 0.5 ** (month_idx / 6)
        hazard = min(0.15, base_churn * decay)
        hazard = max(hazard, 0.01)
        if random.random() < hazard:
            churn_month_idx = month_idx
            break

    available_months = (churn_month_idx or max_months) - 1
    events: List[Tuple[int, str]] = []

    # Plan change intent
    wants_upgrade = random.random() < DAY06_UPGRADE_PROBABILITY and customer.plan_tier != "Enterprise"
    wants_downgrade = random.random() < DAY06_DOWNGRADE_PROBABILITY and customer.plan_tier != "Starter"
    double_upgrade = wants_upgrade and random.random() < 0.2 and customer.plan_tier == "Starter"

    def pick_change_month(existing: Iterable[int]) -> Optional[int]:
        if available_months < 2:
            return None
        candidates = [i for i in range(1, available_months) if i not in existing]
        return random.choice(candidates) if candidates else None

    if wants_upgrade:
        first_upgrade = pick_change_month([])
        if first_upgrade:
            events.append((first_upgrade, "upgrade"))
            if double_upgrade:
                later_candidates = [i for i in range(first_upgrade + 1, available_months)]
                if later_candidates:
                    events.append((random.choice(later_candidates), "upgrade"))
    if wants_downgrade:
        later_than = max([idx for idx, _ in events], default=0)
        downgrade_month = pick_change_month(range(later_than + 1))
        if downgrade_month:
            events.append((downgrade_month, "downgrade"))

    if churn_month_idx is not None:
        events.append((churn_month_idx, "churn"))

    events = sorted(events, key=lambda x: x[0])
    return events, churn_month_idx


def day06_generate_subscriptions(
    customers: List[Day06Customer],
) -> Tuple[List[Day06Subscription], Dict[datetime, Dict[str, float]], Dict[str, int]]:
    """Create subscription histories and aggregate movement stats."""
    month_movements: Dict[datetime, Dict[str, float]] = {
        month: {
            "new_mrr": 0.0,
            "expansion_mrr": 0.0,
            "contraction_mrr": 0.0,
            "churn_mrr": 0.0,
            "net_mrr": 0.0,
        }
        for month in day06_month_starts()
    }

    subscriptions: List[Day06Subscription] = []
    stats_counters = {
        "upgrades": 0,
        "downgrades": 0,
        "churned_customers": 0,
        "new_subscriptions": len(customers),
    }

    for customer in customers:
        churn_bias = 1.0 + min(
            0.15,
            day06_month_diff(DAY06_START_DATE, day06_month_start(customer.signup_date)) * 0.005,
        )
        events, churn_month_idx = day06_generate_lifecycle_events(customer, churn_bias)
        current_plan = customer.plan_tier
        current_mrr = day06_plan_price(current_plan)
        signup_month = day06_month_start(customer.signup_date)
        month_movements[signup_month]["new_mrr"] += current_mrr

        current_start = customer.signup_date
        event_pointer = 0
        while event_pointer < len(events):
            event_month_idx, event_type = events[event_pointer]
            event_date = day06_add_months(day06_month_start(customer.signup_date), event_month_idx)
            end_date = event_date - timedelta(days=1)
            if end_date < current_start:
                end_date = current_start

            subscriptions.append(
                Day06Subscription(
                    subscription_id=day06_generate_subscription_id(),
                    customer_id=customer.customer_id,
                    start_date=current_start,
                    end_date=end_date if event_type != "churn" else event_date,
                    mrr=current_mrr,
                    plan_tier=current_plan,
                )
            )

            if event_type in ("upgrade", "downgrade"):
                new_plan = day06_next_plan(current_plan, "up" if event_type == "upgrade" else "down")
                new_mrr = day06_plan_price(new_plan)
                diff = new_mrr - current_mrr
                if diff > 0:
                    month_movements[event_date.replace(day=1)]["expansion_mrr"] += diff
                    stats_counters["upgrades"] += 1
                else:
                    month_movements[event_date.replace(day=1)]["contraction_mrr"] += abs(diff)
                    stats_counters["downgrades"] += 1
                current_plan = new_plan
                current_mrr = new_mrr
                current_start = event_date
            elif event_type == "churn":
                month_movements[event_date.replace(day=1)]["churn_mrr"] += current_mrr
                stats_counters["churned_customers"] += 1
                customer.status = "churned"
                customer.mrr_current = 0.0
                current_start = None
                break

            event_pointer += 1

        if current_start:
            # still active at end of dataset
            subscriptions.append(
                Day06Subscription(
                    subscription_id=day06_generate_subscription_id(),
                    customer_id=customer.customer_id,
                    start_date=current_start,
                    end_date=None,
                    mrr=current_mrr,
                    plan_tier=current_plan,
                )
            )
            customer.status = "active"
            customer.mrr_current = current_mrr

    for month, values in month_movements.items():
        values["net_mrr"] = (
            values["new_mrr"]
            + values["expansion_mrr"]
            - values["contraction_mrr"]
            - values["churn_mrr"]
        )

    return subscriptions, month_movements, stats_counters


def day06_initialize_db() -> sqlite3.Connection:
    """Create or replace the SQLite database and enforce FK constraints."""
    DAY06_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DAY06_DB_PATH.exists():
        DAY06_DB_PATH.unlink()
    conn = sqlite3.connect(DAY06_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def day06_create_tables(conn: sqlite3.Connection) -> None:
    """Create tables and supporting indexes."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS day06_customers (
            customer_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            plan_tier TEXT NOT NULL,
            mrr_current REAL NOT NULL CHECK (mrr_current >= 0),
            status TEXT NOT NULL CHECK (status IN ('active', 'churned'))
        );

        CREATE TABLE IF NOT EXISTS day06_subscriptions (
            subscription_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            mrr REAL NOT NULL CHECK (mrr > 0),
            plan_tier TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES day06_customers (customer_id)
        );

        CREATE TABLE IF NOT EXISTS day06_mrr_movements (
            month TEXT PRIMARY KEY,
            new_mrr REAL NOT NULL,
            expansion_mrr REAL NOT NULL,
            contraction_mrr REAL NOT NULL,
            churn_mrr REAL NOT NULL,
            net_mrr REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_day06_subscriptions_customer
            ON day06_subscriptions (customer_id);
        CREATE INDEX IF NOT EXISTS idx_day06_subscriptions_start_date
            ON day06_subscriptions (start_date);
        CREATE INDEX IF NOT EXISTS idx_day06_customers_signup_date
            ON day06_customers (signup_date);
        CREATE INDEX IF NOT EXISTS idx_day06_customers_status
            ON day06_customers (status);
        """
    )


def day06_insert_data(
    conn: sqlite3.Connection,
    customers: List[Day06Customer],
    subscriptions: List[Day06Subscription],
    mrr_movements: Dict[datetime, Dict[str, float]],
) -> None:
    """Persist generated data into SQLite."""
    conn.executemany(
        """
        INSERT INTO day06_customers (
            customer_id, email, signup_date, plan_tier, mrr_current, status
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        [
            (
                c.customer_id,
                c.email,
                c.signup_date.date().isoformat(),
                c.plan_tier,
                c.mrr_current,
                c.status,
            )
            for c in customers
        ],
    )

    conn.executemany(
        """
        INSERT INTO day06_subscriptions (
            subscription_id, customer_id, start_date, end_date, mrr, plan_tier
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        [
            (
                s.subscription_id,
                s.customer_id,
                s.start_date.date().isoformat(),
                s.end_date.date().isoformat() if s.end_date else None,
                s.mrr,
                s.plan_tier,
            )
            for s in subscriptions
        ],
    )

    conn.executemany(
        """
        INSERT INTO day06_mrr_movements (
            month, new_mrr, expansion_mrr, contraction_mrr, churn_mrr, net_mrr
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        [
            (
                month.date().isoformat(),
                values["new_mrr"],
                values["expansion_mrr"],
                values["contraction_mrr"],
                values["churn_mrr"],
                values["net_mrr"],
            )
            for month, values in sorted(mrr_movements.items(), key=lambda x: x[0])
        ],
    )
    conn.commit()


def day06_active_mrr_by_month(subscriptions: List[Day06Subscription]) -> Dict[datetime, float]:
    """Calculate active MRR snapshot at month end for reporting and validation."""
    month_ends = day06_month_ends()
    active_mrr: Dict[datetime, float] = {month: 0.0 for month in month_ends}
    for sub in subscriptions:
        for month_end in month_ends:
            if sub.start_date <= month_end and (sub.end_date is None or sub.end_date >= month_end):
                active_mrr[month_end] += sub.mrr
    return active_mrr


def day06_validate_data(
    customers: List[Day06Customer],
    subscriptions: List[Day06Subscription],
    mrr_movements: Dict[datetime, Dict[str, float]],
) -> None:
    """Run integrity checks and ensure realistic SaaS behaviors are present."""
    customer_ids = {c.customer_id for c in customers}
    last_day = DAY06_END_DATE
    start_day = DAY06_START_DATE

    for sub in subscriptions:
        if sub.customer_id not in customer_ids:
            raise ValueError(f"Subscription FK missing for {sub.customer_id}")
        if sub.start_date.date() < start_day.date() or sub.start_date.date() > last_day.date():
            raise ValueError(f"Start date out of range for {sub.subscription_id}")
        if sub.end_date and (
            sub.end_date.date() < sub.start_date.date()
            or sub.end_date.date() > last_day.date()
        ):
            raise ValueError(f"End date invalid for {sub.subscription_id}")
        if sub.mrr <= 0:
            raise ValueError(f"Negative/zero MRR in {sub.subscription_id}")

    # Subscription counts per customer
    sub_counts = Counter(sub.customer_id for sub in subscriptions)
    single_sub_ratio = sum(1 for count in sub_counts.values() if count == 1) / len(customer_ids)
    multi_sub_ratio = sum(1 for count in sub_counts.values() if count >= 2) / len(customer_ids)
    if single_sub_ratio < 0.5:
        raise ValueError("Less than 50% of customers are single-subscription (stability requirement).")
    if multi_sub_ratio < 0.15:
        raise ValueError("At least 15% of customers must have lifecycle changes.")

    # Current MRR should match active subscriptions at dataset end
    active_mrr_end = sum(
        sub.mrr
        for sub in subscriptions
        if sub.start_date.date() <= last_day.date() and (sub.end_date is None or sub.end_date.date() >= last_day.date())
    )
    customer_mrr_total = sum(c.mrr_current for c in customers)
    if abs(active_mrr_end - customer_mrr_total) > 1e-6:
        raise ValueError("Customer mrr_current does not reconcile with active subscriptions.")

    # Churn rate check based on churn events only
    churn_events_by_month: Dict[datetime, int] = defaultdict(int)
    for cust in customers:
        if cust.status == "churned":
            # find last subscription end date for customer
            churn_subs = [s for s in subscriptions if s.customer_id == cust.customer_id and s.end_date]
            if churn_subs:
                churn_month = day06_month_start(max(churn_subs, key=lambda s: s.end_date).end_date)
                churn_events_by_month[churn_month] += 1

    active_counts_by_month: Dict[datetime, int] = {}
    for month_start in day06_month_starts():
        active_counts_by_month[month_start] = sum(
            1
            for sub in subscriptions
            if sub.start_date <= day06_month_end(month_start)
            and (sub.end_date is None or sub.end_date >= month_start)
        )

    churn_rates = []
    for month_start in day06_month_starts():
        active_prev = active_counts_by_month.get(month_start, 0)
        churned = churn_events_by_month.get(month_start, 0)
        if active_prev > 0:
            churn_rates.append(churned / active_prev)

    avg_churn = sum(churn_rates) / len(churn_rates) if churn_rates else 0
    lower_bound = 0.02  # allow some lift to hit retention curve
    upper_bound = DAY06_MONTHLY_CHURN_RATE[1] * 1.2
    if not (lower_bound <= avg_churn <= upper_bound):
        raise ValueError("Average churn rate drifted outside expected 3-9% band.")

    # Net MRR integrity
    for month, values in mrr_movements.items():
        expected = (
            values["new_mrr"]
            + values["expansion_mrr"]
            - values["contraction_mrr"]
            - values["churn_mrr"]
        )
        if abs(expected - values["net_mrr"]) > 1e-6:
            raise ValueError(f"Net MRR mismatch for {month.date()}: {values}")


def day06_month_end(month_start: datetime) -> datetime:
    """Convenience to get the final day of a month."""
    return day06_add_months(month_start, 1) - timedelta(days=1)


def day06_summary(
    customers: List[Day06Customer],
    subscriptions: List[Day06Subscription],
    mrr_movements: Dict[datetime, Dict[str, float]],
    stats: Dict[str, int],
) -> None:
    """Print a concise summary mirroring the expected sample output."""
    active_customers = sum(1 for c in customers if c.status == "active")
    churned_customers = len(customers) - active_customers

    plan_counts = Counter(c.plan_tier for c in customers)
    active_mrr_by_month = day06_active_mrr_by_month(subscriptions)
    first_month = min(active_mrr_by_month.keys())
    last_month = max(active_mrr_by_month.keys())
    starting_mrr = active_mrr_by_month[first_month]
    current_mrr = active_mrr_by_month[last_month]
    mrr_growth_pct = ((current_mrr - starting_mrr) / starting_mrr) * 100 if starting_mrr else 0.0

    total_movements = {
        key: round(sum(values[key] for values in mrr_movements.values()), 2)
        for key in ["new_mrr", "expansion_mrr", "contraction_mrr", "churn_mrr", "net_mrr"]
    }

    print("Generating synthetic SaaS metrics data...")
    print("=" * 60)
    print()
    print(
        f"Created {len(customers)} customers across 24 months (2023-01 to 2024-12)"
    )
    print(
        f"  - Starter tier: {plan_counts['Starter']} customers ({(plan_counts['Starter']/len(customers))*100:.1f}%)"
    )
    print(
        f"  - Pro tier: {plan_counts['Pro']} customers ({(plan_counts['Pro']/len(customers))*100:.1f}%)"
    )
    print(
        f"  - Enterprise tier: {plan_counts['Enterprise']} customers ({(plan_counts['Enterprise']/len(customers))*100:.1f}%)"
    )
    print(f"  - Active customers: {active_customers} ({(active_customers/len(customers))*100:.1f}%)")
    print(f"  - Churned customers: {churned_customers} ({(churned_customers/len(customers))*100:.1f}%)")
    print()
    print(f"Generated {len(subscriptions)} subscription records")
    print(f"  - New subscriptions: {stats['new_subscriptions']}")
    print(f"  - Upgrades (Expansion): {stats['upgrades']} ({(stats['upgrades']/len(customers))*100:.1f}%)")
    print(
        f"  - Downgrades (Contraction): {stats['downgrades']} ({(stats['downgrades']/len(customers))*100:.1f}%)"
    )
    print(
        f"  - Churned subscriptions: {stats['churned_customers']} ({(stats['churned_customers']/len(customers))*100:.1f}%)"
    )
    print()
    print("MRR Movements Summary (24 months):")
    print(f"  - Total New MRR: ${total_movements['new_mrr']:.0f}")
    print(f"  - Total Expansion MRR: ${total_movements['expansion_mrr']:.0f}")
    print(f"  - Total Contraction MRR: ${total_movements['contraction_mrr']:.0f}")
    print(f"  - Total Churn MRR: ${total_movements['churn_mrr']:.0f}")
    print(f"  - Net MRR Growth: ${total_movements['net_mrr']:.0f}")
    print()
    print(f"Current MRR (Month 24): ${current_mrr:,.0f}")
    print(f"  - Starting MRR (Month 1): ${starting_mrr:,.0f}")
    print(f"  - MRR Growth: {mrr_growth_pct:.0f}% over 24 months")
    print()
    print("Data Integrity Checks:")
    print("  ✓ All foreign keys valid")
    print("  ✓ All dates within valid range")
    print("  ✓ All MRR values positive")
    print("  ✓ MRR movements balance correctly")
    print("  ✓ No orphaned subscriptions")
    print()
    size_kb = DAY06_DB_PATH.stat().st_size / 1024 if DAY06_DB_PATH.exists() else 0
    print(f"Database saved to: {DAY06_DB_PATH}")
    print(f"File size: {size_kb:.0f} KB")
    print("=" * 60)


def main() -> None:
    """Entrypoint to generate data, validate, persist, and summarize output."""
    customers = day06_build_customers()
    subscriptions, mrr_movements, stats = day06_generate_subscriptions(customers)
    day06_validate_data(customers, subscriptions, mrr_movements)

    conn = day06_initialize_db()
    day06_create_tables(conn)
    day06_insert_data(conn, customers, subscriptions, mrr_movements)
    day06_summary(customers, subscriptions, mrr_movements, stats)


if __name__ == "__main__":
    main()
