#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 07: Hospitality LTV & Cohort Analysis

This script produces a SQLite database with Brazilian hospitality data for
Carol's pousada in Campos do Jordão. It models guest cohorts, repeat behavior,
seasonality, and LTV patterns inspired by Booking.com style reservations.

Usage:
    python day07_DATA_synthetic_generator.py
"""

import calendar
import random
import sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from day07_CONFIG_settings import (
    DAY07_BOOKING_SOURCES,
    DAY07_CHECK_IN_HOUR_MAX,
    DAY07_CHECK_IN_HOUR_MIN,
    DAY07_CHECK_OUT_HOUR_MAX,
    DAY07_CHECK_OUT_HOUR_MIN,
    DAY07_COHORT_ANALYSIS_MONTHS,
    DAY07_COHORT_END_DATE,
    DAY07_COHORT_START_DATE,
    DAY07_DB_PATH,
    DAY07_EXPECTED_CANCELLATION_RATE,
    DAY07_HIGH_SEASON_MONTHS,
    DAY07_HIGH_SEASON_MULTIPLIER,
    DAY07_LTV_VIP_THRESHOLD,
    day07_get_booking_commission,
    day07_get_season,
    day07_validate_config,
)

# Reproducible output
random.seed(42)


# =============================================================================
# CONSTANTS & SOURCE DATA
# =============================================================================

DAY07_NUM_GUESTS = 180
DAY07_TARGET_BOOKINGS = 500
DAY07_COHORT_MONTHS = 24
DAY07_MAX_LEAD_TIME_HIGH = (30, 90)
DAY07_MAX_LEAD_TIME_LOW = (5, 30)
DAY07_MAX_NIGHTS = 7
DAY07_MIN_NIGHTS = 1
DAY07_BREAKFAST_RATE = 0.8
DAY07_REVIEW_SUBMIT_RATE = 0.3
DAY07_STAY_CANCELLATION_RATE = DAY07_EXPECTED_CANCELLATION_RATE

DAY07_FIRST_NAMES = [
    "João",
    "Maria",
    "José",
    "Ana",
    "Carlos",
    "Mariana",
    "Pedro",
    "Julia",
    "Lucas",
    "Beatriz",
    "Gabriel",
    "Larissa",
    "Rafael",
    "Camila",
    "Fernando",
    "Patricia",
    "Rodrigo",
    "Amanda",
    "Bruno",
    "Fernanda",
    "Diego",
    "Isabela",
    "Claudia",
    "Eduardo",
    "Renata",
    "Felipe",
    "Sofia",
    "Caio",
    "Luana",
]

DAY07_LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Lima",
    "Costa",
    "Ferreira",
    "Rodrigues",
    "Almeida",
    "Pereira",
    "Carvalho",
    "Ribeiro",
    "Martins",
    "Araújo",
    "Melo",
    "Barbosa",
    "Gomes",
    "Cardoso",
    "Nascimento",
    "Castro",
    "Moura",
    "Teixeira",
    "Freitas",
    "Pinto",
]

DAY07_EMAIL_DOMAINS = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com.br"]

DAY07_SPECIAL_REQUESTS = [
    "Late check-in",
    "Vegetarian breakfast",
    "Extra bed",
    "Berço no quarto",
    "Quarto com vista",
    "Cama king-size",
]

DAY07_REVIEWS = [
    "Lugar maravilhoso!",
    "Vista incrível",
    "Café da manhã excelente",
    "Equipe muito atenciosa",
    "Quarto aconchegante e limpo",
    "Voltaríamos com certeza",
    "Ótimo custo-benefício",
    "Chalé super confortável",
]

DAY07_REFERRALS = [
    None,
    "Friend Recommendation",
    "Google Search",
    "Social Media",
    "Returning Guest",
]

DAY07_ROOM_RATE_RANGES = {
    "Standard": (300, 500),
    "Deluxe": (500, 800),
    "Suite": (800, 1200),
    "Family Room": (700, 1000),
}

DAY07_ROOM_WEIGHTS = {
    "Standard": 0.4,
    "Deluxe": 0.35,
    "Suite": 0.15,
    "Family Room": 0.10,
}

DAY07_GUEST_TYPES = {
    "Couple": 0.45,
    "Family": 0.30,
    "Individual": 0.15,
    "Business": 0.10,
}

DAY07_COUNTRY_WEIGHTS = {
    "Brazil": 0.80,
    "Argentina": 0.15,
    "Other": 0.05,
}


# =============================================================================
# HELPERS
# =============================================================================


def day07_months_between(start: date, months: int) -> List[date]:
    """Generate the first day of sequential months starting from start."""
    results = []
    for offset in range(months):
        month = (start.month - 1 + offset) % 12 + 1
        year = start.year + ((start.month - 1 + offset) // 12)
        results.append(date(year, month, 1))
    return results


def day07_random_date_in_month(month_start: date) -> date:
    """Pick a random day within the month of the provided date."""
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)
    max_day = (next_month - month_start).days
    return month_start + timedelta(days=random.randint(0, max_day - 1))


def day07_add_months(base: date, months: int) -> date:
    """Add months to a date while clamping the day to month length."""
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def day07_random_phone() -> str:
    """Generate a Brazilian-style phone number."""
    ddd = random.choice(["11", "12", "21", "31", "41"])
    first = random.randint(90000, 99999)
    second = random.randint(1000, 9999)
    return f"+55 ({ddd}) {first}-{second:04d}"


def day07_weighted_choice(options: Dict[str, float]) -> str:
    """Select a key from a weight mapping."""
    keys = list(options.keys())
    weights = list(options.values())
    return random.choices(keys, weights=weights, k=1)[0]


def day07_initialize_db(db_path: Path) -> sqlite3.Connection:
    """Create/replace the SQLite database and enable FK enforcement."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def day07_create_tables(conn: sqlite3.Connection) -> None:
    """Create hospitality tables and supporting indexes."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS day07_guests (
            guest_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            country TEXT NOT NULL,
            guest_type TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            marketing_consent INTEGER NOT NULL CHECK (marketing_consent IN (0, 1)),
            vip_status INTEGER NOT NULL CHECK (vip_status IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS day07_bookings (
            booking_id TEXT PRIMARY KEY,
            guest_id TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            room_type TEXT NOT NULL,
            number_of_guests INTEGER NOT NULL CHECK (number_of_guests > 0),
            number_of_rooms INTEGER NOT NULL CHECK (number_of_rooms > 0),
            booking_source TEXT NOT NULL,
            status TEXT NOT NULL,
            total_price_brl REAL NOT NULL CHECK (total_price_brl > 0),
            commission_pct REAL NOT NULL CHECK (commission_pct >= 0),
            payment_method TEXT NOT NULL,
            special_requests TEXT,
            FOREIGN KEY (guest_id) REFERENCES day07_guests (guest_id)
        );

        CREATE TABLE IF NOT EXISTS day07_stays (
            stay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL,
            guest_id TEXT NOT NULL,
            actual_check_in TEXT NOT NULL,
            actual_check_out TEXT NOT NULL,
            breakfast_included INTEGER NOT NULL CHECK (breakfast_included IN (0, 1)),
            extras_spent_brl REAL NOT NULL CHECK (extras_spent_brl >= 0),
            guest_rating INTEGER CHECK (guest_rating BETWEEN 1 AND 5),
            review_text TEXT,
            repeat_guest INTEGER NOT NULL CHECK (repeat_guest IN (0, 1)),
            referral_source TEXT,
            FOREIGN KEY (booking_id) REFERENCES day07_bookings (booking_id),
            FOREIGN KEY (guest_id) REFERENCES day07_guests (guest_id)
        );

        CREATE INDEX IF NOT EXISTS idx_day07_bookings_guest
            ON day07_bookings (guest_id);
        CREATE INDEX IF NOT EXISTS idx_day07_bookings_booking_date
            ON day07_bookings (booking_date);
        CREATE INDEX IF NOT EXISTS idx_day07_bookings_check_in
            ON day07_bookings (check_in_date);
        """
    )


def day07_generate_guests(num_guests: int) -> List[Dict[str, str]]:
    """Create guest profiles with country, type, and consent attributes."""
    guests: List[Dict[str, str]] = []
    start_reg = date(2022, 1, 1)
    end_reg = date(2024, 12, 31)

    for idx in range(1, num_guests + 1):
        first = random.choice(DAY07_FIRST_NAMES)
        last = random.choice(DAY07_LAST_NAMES)
        email_base = f"{first}.{last}".lower().replace(" ", "")
        domain = random.choice(DAY07_EMAIL_DOMAINS)
        email = f"{email_base}@{domain}"
        country = day07_weighted_choice(DAY07_COUNTRY_WEIGHTS)
        guest_type = day07_weighted_choice(DAY07_GUEST_TYPES)
        registration = start_reg + timedelta(
            days=random.randint(0, (end_reg - start_reg).days)
        )
        marketing_consent = int(random.random() < 0.6)

        guests.append(
            {
                "guest_id": f"GUEST-{idx:03d}",
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": day07_random_phone(),
                "country": country,
                "guest_type": guest_type,
                "registration_date": registration.isoformat(),
                "marketing_consent": marketing_consent,
                "vip_status": 0,  # Updated after LTV calculation
            }
        )
    return guests


def day07_determine_visit_plan(guests: List[Dict[str, str]], target: int) -> Dict[str, int]:
    """
    Assign visit counts to guests to hit booking volume while preserving repeat mix.

    The base distribution follows 70% first-timers and 30% repeaters with higher
    visit caps for VIP-style guests. Extra visits are layered onto repeat guests
    until the target booking volume is reached.
    """
    plan: Dict[str, int] = {}
    # Base mix
    for guest in guests:
        roll = random.random()
        if roll < 0.7:
            visits = 1
        elif roll < 0.9:
            visits = 2
        elif roll < 0.98:
            visits = random.randint(3, 4)
        else:
            visits = random.randint(5, 7)
        plan[guest["guest_id"]] = visits

    total = sum(plan.values())
    repeat_candidates = [gid for gid, visits in plan.items() if visits > 1]
    # Layer extra visits on repeat guests to reach target bookings
    while total < target and repeat_candidates:
        random.shuffle(repeat_candidates)
        for gid in repeat_candidates:
            if total >= target:
                break
            if plan[gid] >= 9:
                continue
            plan[gid] += 1
            total += 1
    return plan


def day07_room_price(room_type: str, month: int) -> float:
    """Calculate a per-night rate within configured bounds."""
    low, high = DAY07_ROOM_RATE_RANGES[room_type]
    base_price = random.uniform(low, high)
    season = day07_get_season(month)
    if season == "high":
        base_price *= DAY07_HIGH_SEASON_MULTIPLIER
    # Small jitter to avoid perfectly uniform pricing
    return round(base_price * random.uniform(0.95, 1.05), 2)


def day07_booking_lead_time(month: int, source: str) -> int:
    """Select lead time considering seasonality and direct booking behavior."""
    high_season = month in DAY07_HIGH_SEASON_MONTHS
    min_days, max_days = (
        DAY07_MAX_LEAD_TIME_HIGH if high_season else DAY07_MAX_LEAD_TIME_LOW
    )
    if source in ("Direct Website", "Phone"):
        max_days = max(min_days + 5, int(max_days * 0.7))
    return random.randint(min_days, max_days)


def day07_generate_booking_dates(
    first_check_in: date, visits: int
) -> List[date]:
    """Generate sequential check-in dates honoring retention windows."""
    dates = [first_check_in]
    for _ in range(1, visits):
        gap_months = random.choices(
            DAY07_COHORT_ANALYSIS_MONTHS, weights=[0.15, 0.25, 0.35, 0.25], k=1
        )[0]
        base = day07_add_months(dates[-1], gap_months)
        jitter = timedelta(days=random.randint(-4, 7))
        candidate = base + jitter
        dates.append(candidate)
    return dates


def day07_generate_bookings(
    guests: List[Dict[str, str]], visit_plan: Dict[str, int]
) -> Tuple[List[Dict[str, str]], Counter, Dict[str, List[str]]]:
    """
    Build booking records aligned to cohorts, seasonality, and cancellation rules.

    Returns:
        bookings list, cohort counter, and mapping of guest_id to booking_ids.
    """
    start = date.fromisoformat(DAY07_COHORT_START_DATE)
    cohort_months = day07_months_between(start, DAY07_COHORT_MONTHS)
    end_date = date.fromisoformat(DAY07_COHORT_END_DATE)

    bookings: List[Dict[str, str]] = []
    cohort_counter: Counter = Counter()
    booking_ids_by_guest: Dict[str, List[str]] = defaultdict(list)

    booking_idx = 1
    for idx, guest in enumerate(guests):
        guest_id = guest["guest_id"]
        visits = visit_plan.get(guest_id, 1)
        cohort_month = cohort_months[idx % len(cohort_months)]
        first_check_in = day07_random_date_in_month(cohort_month)
        if first_check_in < start:
            first_check_in = start
        if first_check_in > end_date:
            first_check_in = end_date - timedelta(days=7)

        registration_dt = date.fromisoformat(guest["registration_date"])
        if registration_dt > first_check_in:
            adjustment_days = random.randint(10, 60)
            registration_dt = max(date(2022, 1, 1), first_check_in - timedelta(days=adjustment_days))
            guest["registration_date"] = registration_dt.isoformat()

        cohort_counter[first_check_in.strftime("%Y-%m")] += 1
        check_in_dates = day07_generate_booking_dates(first_check_in, visits)

        for check_in in check_in_dates:
            # Keep dates inside allowed window
            if check_in < start:
                check_in = start
            if check_in > end_date:
                check_in = end_date - timedelta(days=random.randint(1, 7))

            nights = random.choices([1, 2, 3, 4, 5, 6, 7], weights=[0.05, 0.35, 0.35, 0.1, 0.08, 0.05, 0.02], k=1)[0]
            check_out = check_in + timedelta(days=nights)
            room_type = day07_weighted_choice(DAY07_ROOM_WEIGHTS)
            booking_source = day07_weighted_choice(
                {k: v["weight"] for k, v in DAY07_BOOKING_SOURCES.items()}
            )
            lead_time_days = day07_booking_lead_time(check_in.month, booking_source)
            booking_date = max(
                registration_dt,
                check_in - timedelta(days=lead_time_days),
            )

            cancellation_bias = DAY07_STAY_CANCELLATION_RATE
            if lead_time_days > 60:
                cancellation_bias += 0.05
            if booking_source in ("Direct Website", "Phone"):
                cancellation_bias -= 0.02
            is_cancelled = random.random() < cancellation_bias
            status = "Cancelled" if is_cancelled else random.choices(
                ["Confirmed", "Checked-In", "Checked-Out"],
                weights=[0.3, 0.2, 0.5],
                k=1,
            )[0]

            price_per_night = day07_room_price(room_type, check_in.month)
            total_price = round(price_per_night * nights, 2)
            number_of_guests = random.choices(
                [1, 2, 3, 4], weights=[0.15, 0.55, 0.2, 0.1], k=1
            )[0]
            if room_type == "Family Room":
                number_of_guests = random.choices([3, 4], weights=[0.6, 0.4], k=1)[0]
            number_of_rooms = 2 if room_type == "Family Room" and random.random() < 0.2 else 1

            payment_method = random.choice(["Credit Card", "Pix", "Bank Transfer", "Cash"])
            special_requests = (
                None if random.random() < 0.6 else random.choice(DAY07_SPECIAL_REQUESTS)
            )

            booking_id = f"BKG-{booking_idx:06d}"
            booking_idx += 1

            bookings.append(
                {
                    "booking_id": booking_id,
                    "guest_id": guest_id,
                    "booking_date": booking_date.isoformat(),
                    "check_in_date": check_in.isoformat(),
                    "check_out_date": check_out.isoformat(),
                    "room_type": room_type,
                    "number_of_guests": number_of_guests,
                    "number_of_rooms": number_of_rooms,
                    "booking_source": booking_source,
                    "status": status,
                    "total_price_brl": total_price,
                    "commission_pct": day07_get_booking_commission(booking_source),
                    "payment_method": payment_method,
                    "special_requests": special_requests,
                    "nights": nights,
                    "is_cancelled": is_cancelled,
                }
            )
            booking_ids_by_guest[guest_id].append(booking_id)

    return bookings, cohort_counter, booking_ids_by_guest


def day07_balance_seasonality(
    bookings: List[Dict[str, str]], guests: List[Dict[str, str]], target_ratio: float = 0.5
) -> None:
    """Adjust check-in dates slightly to keep high/low season mix near target."""
    registration_map = {
        g["guest_id"]: date.fromisoformat(g["registration_date"]) for g in guests
    }
    start = date.fromisoformat(DAY07_COHORT_START_DATE)
    end = date.fromisoformat(DAY07_COHORT_END_DATE)
    first_booking_ids: Dict[str, str] = {}
    for booking in sorted(
        bookings, key=lambda b: date.fromisoformat(b["check_in_date"])
    ):
        gid = booking["guest_id"]
        if gid not in first_booking_ids:
            first_booking_ids[gid] = booking["booking_id"]

    def shift_booking(booking: Dict[str, str], new_check_in: date) -> None:
        nights = max(1, int(booking.get("nights", 1)))
        if new_check_in > end - timedelta(days=nights):
            new_check_in = end - timedelta(days=nights)
        if new_check_in < start:
            new_check_in = start

        booking["check_in_date"] = new_check_in.isoformat()
        booking["check_out_date"] = (new_check_in + timedelta(days=nights)).isoformat()
        lead_time = day07_booking_lead_time(new_check_in.month, booking["booking_source"])
        reg_dt = registration_map[booking["guest_id"]]
        booking_date = max(reg_dt, new_check_in - timedelta(days=lead_time))
        if booking_date > new_check_in:
            booking_date = new_check_in
        booking["booking_date"] = booking_date.isoformat()
        booking["total_price_brl"] = round(
            day07_room_price(booking["room_type"], new_check_in.month) * nights, 2
        )

    def find_candidate(check_in: date, prefer_high: bool) -> date:
        for delta in range(1, 4):
            for sign in (1, -1):
                candidate = day07_add_months(check_in, delta * sign)
                if candidate < start or candidate > end:
                    continue
                if (candidate.month in DAY07_HIGH_SEASON_MONTHS) == prefer_high:
                    return candidate
        return check_in

    def is_high(booking: Dict[str, str]) -> bool:
        return date.fromisoformat(booking["check_in_date"]).month in DAY07_HIGH_SEASON_MONTHS

    total = len(bookings)
    if total == 0:
        return
    high_count = sum(1 for b in bookings if is_high(b))
    current_ratio = high_count / total
    if abs(current_ratio - target_ratio) <= 0.05:
        return

    if current_ratio > target_ratio:
        candidates = [
            b
            for b in bookings
            if is_high(b) and b["booking_id"] not in first_booking_ids.values()
        ]
        prefer_high = False
    else:
        candidates = [
            b
            for b in bookings
            if not is_high(b) and b["booking_id"] not in first_booking_ids.values()
        ]
        prefer_high = True

    required = int((abs(current_ratio - target_ratio) - 0.02) * total)
    for booking in random.sample(candidates, min(len(candidates), required)):
        current_ci = date.fromisoformat(booking["check_in_date"])
        new_ci = find_candidate(current_ci, prefer_high)
        if new_ci != current_ci:
            shift_booking(booking, new_ci)


def day07_rebuild_cohorts(bookings: List[Dict[str, str]]) -> Counter:
    """Recompute first-booking month distribution after adjustments."""
    first_by_guest: Dict[str, date] = {}
    for booking in bookings:
        gid = booking["guest_id"]
        ci = date.fromisoformat(booking["check_in_date"])
        if gid not in first_by_guest or ci < first_by_guest[gid]:
            first_by_guest[gid] = ci

    counter: Counter = Counter()
    for ci in first_by_guest.values():
        counter[ci.strftime("%Y-%m")] += 1
    return counter


def day07_generate_stays(
    bookings: List[Dict[str, str]]
) -> Tuple[List[Dict[str, str]], Dict[str, float]]:
    """Create stay records for non-cancelled bookings and compute LTV per guest."""
    stays: List[Dict[str, str]] = []
    ltv: Dict[str, float] = defaultdict(float)
    stay_counts: Dict[str, int] = defaultdict(int)

    for booking in bookings:
        if booking["is_cancelled"]:
            continue

        check_in_date = date.fromisoformat(booking["check_in_date"])
        check_out_date = date.fromisoformat(booking["check_out_date"])
        check_in_hour = random.randint(DAY07_CHECK_IN_HOUR_MIN, DAY07_CHECK_IN_HOUR_MAX)
        check_out_hour = random.randint(DAY07_CHECK_OUT_HOUR_MIN, DAY07_CHECK_OUT_HOUR_MAX)
        actual_check_in = datetime.combine(check_in_date, datetime.min.time()).replace(
            hour=check_in_hour, minute=random.choice([0, 15, 30, 45])
        )
        actual_check_out = datetime.combine(check_out_date, datetime.min.time()).replace(
            hour=check_out_hour, minute=random.choice([0, 15, 30, 45])
        )

        extras_roll = random.random()
        if extras_roll < 0.4:
            extras = 0.0
        elif extras_roll < 0.8:
            extras = round(random.uniform(50, 150), 2)
        else:
            extras = round(random.uniform(150, 300), 2)

        rating_roll = random.random()
        if rating_roll < 0.1:
            guest_rating = random.choice([2, 3])
        else:
            guest_rating = random.choices([4, 5], weights=[0.45, 0.55], k=1)[0]

        review_text = None
        if random.random() < DAY07_REVIEW_SUBMIT_RATE:
            review_text = random.choice(DAY07_REVIEWS)

        guest_id = booking["guest_id"]
        repeat_guest = int(stay_counts[guest_id] > 0)
        stay_counts[guest_id] += 1

        stays.append(
            {
                "booking_id": booking["booking_id"],
                "guest_id": guest_id,
                "actual_check_in": actual_check_in.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_check_out": actual_check_out.strftime("%Y-%m-%d %H:%M:%S"),
                "breakfast_included": int(random.random() < DAY07_BREAKFAST_RATE),
                "extras_spent_brl": extras,
                "guest_rating": guest_rating,
                "review_text": review_text,
                "repeat_guest": repeat_guest,
                "referral_source": random.choice(DAY07_REFERRALS),
            }
        )

        ltv[guest_id] += booking["total_price_brl"] + extras

    return stays, ltv


def day07_assign_vip_status(
    guests: List[Dict[str, str]], ltv: Dict[str, float]
) -> None:
    """Mark top 10% guests by LTV as VIP."""
    ranked = sorted(ltv.items(), key=lambda kv: kv[1], reverse=True)
    top_count = max(1, int(len(guests) * 0.10))
    vip_ids = {guest_id for guest_id, _ in ranked[:top_count]}
    for guest in guests:
        guest["vip_status"] = int(guest["guest_id"] in vip_ids)


def day07_insert_data(
    conn: sqlite3.Connection,
    guests: List[Dict[str, str]],
    bookings: List[Dict[str, str]],
    stays: List[Dict[str, str]],
) -> None:
    """Persist generated records into SQLite."""
    conn.executemany(
        """
        INSERT INTO day07_guests (
            guest_id, first_name, last_name, email, phone, country,
            guest_type, registration_date, marketing_consent, vip_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                g["guest_id"],
                g["first_name"],
                g["last_name"],
                g["email"],
                g["phone"],
                g["country"],
                g["guest_type"],
                g["registration_date"],
                g["marketing_consent"],
                g["vip_status"],
            )
            for g in guests
        ],
    )

    conn.executemany(
        """
        INSERT INTO day07_bookings (
            booking_id, guest_id, booking_date, check_in_date, check_out_date,
            room_type, number_of_guests, number_of_rooms, booking_source, status,
            total_price_brl, commission_pct, payment_method, special_requests
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                b["booking_id"],
                b["guest_id"],
                b["booking_date"],
                b["check_in_date"],
                b["check_out_date"],
                b["room_type"],
                b["number_of_guests"],
                b["number_of_rooms"],
                b["booking_source"],
                b["status"],
                b["total_price_brl"],
                b["commission_pct"],
                b["payment_method"],
                b["special_requests"],
            )
            for b in bookings
        ],
    )

    conn.executemany(
        """
        INSERT INTO day07_stays (
            booking_id, guest_id, actual_check_in, actual_check_out,
            breakfast_included, extras_spent_brl, guest_rating, review_text,
            repeat_guest, referral_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                s["booking_id"],
                s["guest_id"],
                s["actual_check_in"],
                s["actual_check_out"],
                s["breakfast_included"],
                s["extras_spent_brl"],
                s["guest_rating"],
                s["review_text"],
                s["repeat_guest"],
                s["referral_source"],
            )
            for s in stays
        ],
    )
    conn.commit()


def day07_validate(conn: sqlite3.Connection, cohort_counter: Counter) -> None:
    """Run integrity checks on FK relationships, dates, pricing, and cohorts."""
    cur = conn.cursor()
    fk_issue_bookings = cur.execute(
        """
        SELECT COUNT(*) FROM day07_bookings b
        LEFT JOIN day07_guests g ON b.guest_id = g.guest_id
        WHERE g.guest_id IS NULL
        """
    ).fetchone()[0]
    if fk_issue_bookings:
        raise ValueError("Foreign key validation failed for bookings.")

    fk_issue_stays = cur.execute(
        """
        SELECT COUNT(*) FROM day07_stays s
        LEFT JOIN day07_bookings b ON s.booking_id = b.booking_id
        WHERE b.booking_id IS NULL
        """
    ).fetchone()[0]
    if fk_issue_stays:
        raise ValueError("Foreign key validation failed for stays.")

    date_issues = cur.execute(
        """
        SELECT COUNT(*) FROM day07_bookings
        WHERE booking_date > check_in_date
           OR check_out_date <= check_in_date
        """
    ).fetchone()[0]
    if date_issues:
        raise ValueError("Date logic violation detected in bookings.")

    negative_amounts = cur.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT total_price_brl AS amount FROM day07_bookings
            UNION ALL
            SELECT extras_spent_brl FROM day07_stays
        ) WHERE amount < 0
        """
    ).fetchone()[0]
    if negative_amounts:
        raise ValueError("Negative monetary values found.")

    cancellation_rate = cur.execute(
        """
        SELECT AVG(status = 'Cancelled') FROM day07_bookings
        """
    ).fetchone()[0]
    if cancellation_rate is not None and not (0.05 <= cancellation_rate <= 0.16):
        raise ValueError("Cancellation rate outside expected bounds.")

    repeat_ratio = cur.execute(
        """
        SELECT AVG(booking_count > 1) FROM (
            SELECT guest_id, COUNT(*) AS booking_count
            FROM day07_bookings
            GROUP BY guest_id
        )
        """
    ).fetchone()[0]
    if repeat_ratio is not None and repeat_ratio < 0.25:
        raise ValueError("Repeat guest rate below expectation.")

    # Cohort evenness: keep spread within a 2x ratio to avoid heavy clustering
    if cohort_counter:
        counts = cohort_counter.values()
        if max(counts) / max(1, min(counts)) > 2.0:
            raise ValueError("Cohort distribution too uneven.")

    # Pricing sanity by season and room type
    price_checks = cur.execute(
        """
        SELECT room_type, check_in_date, total_price_brl
        FROM day07_bookings
        """
    ).fetchall()
    for room_type, check_in_date, total in price_checks:
        nights = cur.execute(
            "SELECT julianday(check_out_date) - julianday(check_in_date) FROM day07_bookings WHERE room_type=? AND check_in_date=? AND total_price_brl=?",
            (room_type, check_in_date, total),
        ).fetchone()[0]
        nights = max(1.0, nights)
        per_night = total / nights
        low, high = DAY07_ROOM_RATE_RANGES[room_type]
        season = day07_get_season(date.fromisoformat(check_in_date).month)
        high_cap = high * DAY07_HIGH_SEASON_MULTIPLIER * 1.1
        low_cap = low * 0.8
        if season == "high":
            if per_night < low or per_night > high_cap:
                raise ValueError("Per-night price out of expected high-season bounds.")
        else:
            if per_night < low_cap or per_night > high * 1.1:
                raise ValueError("Per-night price out of expected low-season bounds.")


def day07_print_summary(
    guests: List[Dict[str, str]],
    bookings: List[Dict[str, str]],
    stays: List[Dict[str, str]],
    cohort_counter: Counter,
    ltv: Dict[str, float],
) -> None:
    """Display helpful generation metrics."""
    countries = Counter(g["country"] for g in guests)
    types = Counter(g["guest_type"] for g in guests)
    vip_count = sum(g["vip_status"] for g in guests)
    cancelled = sum(1 for b in bookings if b["status"] == "Cancelled")
    high_season = sum(
        1
        for b in bookings
        if date.fromisoformat(b["check_in_date"]).month in DAY07_HIGH_SEASON_MONTHS
    )
    avg_stay = (
        sum(
            (
                date.fromisoformat(b["check_out_date"])
                - date.fromisoformat(b["check_in_date"])
            ).days
            for b in bookings
            if b["status"] != "Cancelled"
        )
        / max(1, len(stays))
    )
    avg_rating = (
        sum(s["guest_rating"] for s in stays) / max(1, len(stays))
        if stays
        else 0
    )
    total_revenue = sum(ltv.values())
    review_count = sum(1 for s in stays if s["review_text"])

    print("Generating synthetic hospitality data for Carol's Pousada...\n")
    print(f"Created {len(guests)} guests")
    print(
        "  - Guest types: "
        + ", ".join(f"{k} ({v/len(guests)*100:.0f}%)" for k, v in types.items())
    )
    print(
        "  - Countries: "
        + ", ".join(f"{k} ({v/len(guests)*100:.0f}%)" for k, v in countries.items())
    )
    print(f"  - VIP guests: {vip_count} ({vip_count/len(guests)*100:.0f}%)\n")

    print(
        f"Generated {len(bookings)} bookings across {len(cohort_counter)} cohort months"
    )
    check_in_dates = [date.fromisoformat(b["check_in_date"]) for b in bookings]
    print(
        f"  - Date range: {min(check_in_dates)} to {max(check_in_dates)}"
    )
    source_counts = Counter(b["booking_source"] for b in bookings)
    print(
        "  - Booking sources: "
        + ", ".join(
            f"{src} ({count/len(bookings)*100:.0f}%)"
            for src, count in source_counts.most_common()
        )
    )
    print(
        f"  - Status: Active {len(bookings) - cancelled}, Cancelled {cancelled} ({cancelled/len(bookings)*100:.0f}%)"
    )
    print(f"  - High season bookings: {high_season} ({high_season/len(bookings)*100:.0f}%)\n")

    print(f"Created {len(stays)} stay records (excludes cancelled)")
    print(f"  - Average stay duration: {avg_stay:.1f} nights")
    print(f"  - Average guest rating: {avg_rating:.1f}/5.0")
    print(f"  - Reviews submitted: {review_count} ({review_count/max(1,len(stays))*100:.0f}%)")
    print(f"  - Total extras revenue: R$ {sum(s['extras_spent_brl'] for s in stays):,.0f}")

    top_guests = sorted(ltv.items(), key=lambda kv: kv[1], reverse=True)[:3]
    print("\nTop guests by LTV (cumulative spend):")
    for guest_id, value in top_guests:
        print(f"  {guest_id}: R$ {value:,.0f}")

    print(f"\nDatabase saved to: {DAY07_DB_PATH}")


def main() -> None:
    """Entry point to generate tables, populate data, and validate integrity."""
    day07_validate_config()
    db_path = Path(DAY07_DB_PATH)

    guests = day07_generate_guests(DAY07_NUM_GUESTS)
    visit_plan = day07_determine_visit_plan(guests, DAY07_TARGET_BOOKINGS)
    bookings, cohort_counter, _ = day07_generate_bookings(guests, visit_plan)
    day07_balance_seasonality(bookings, guests)
    cohort_counter = day07_rebuild_cohorts(bookings)
    stays, ltv = day07_generate_stays(bookings)
    day07_assign_vip_status(guests, ltv)

    conn = day07_initialize_db(db_path)
    day07_create_tables(conn)
    day07_insert_data(conn, guests, bookings, stays)
    day07_validate(conn, cohort_counter)
    day07_print_summary(guests, bookings, stays, cohort_counter, ltv)


if __name__ == "__main__":
    main()
