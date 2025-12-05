# Codex Prompt: Generate Synthetic Hospitality Data (Pousada in Campos do Jordão)

## Context
Generate synthetic data for Carol's pousada (boutique inn) in Campos do Jordão, Brazil. This data will be used to calculate guest lifetime value (LTV), cohort analysis, and retention metrics. The data structure mimics **Booking.com's Reservations API** format but adapted for a small hospitality business.

## API Reference
Based on [Booking.com Connectivity APIs](https://developers.booking.com/connectivity/docs/reservations-api/reservations-overview), which includes fields like:
- Guest information (first_name, last_name, email, phone)
- Reservation details (reservation_id, booking_date, status)
- Stay details (arrival_date, departure_date, room_type, total_price, meal_plan)
- Guest counts and room configurations

## Requirements

### 1. Generate Three Related Tables

#### Table 1: `day07_guests`
Create 150-200 unique guests with:
- `guest_id` (TEXT, PRIMARY KEY): Format "GUEST-001", "GUEST-002", etc.
- `first_name` (TEXT): Common Brazilian first names (João, Maria, Ana, Carlos, etc.)
- `last_name` (TEXT): Common Brazilian surnames (Silva, Santos, Oliveira, Souza, etc.)
- `email` (TEXT): Format firstname.lastname@domain.com (use gmail.com, outlook.com, etc.)
- `phone` (TEXT): Brazilian format "+55 (11) 98765-4321"
- `country` (TEXT): 80% "Brazil", 15% "Argentina", 5% "Other" (USA, Chile, Uruguay)
- `guest_type` (TEXT): "Individual", "Family", "Couple", "Business"
- `registration_date` (DATE): Between 2022-01-01 and 2024-12-31
- `marketing_consent` (BOOLEAN): TRUE for 60% of guests
- `vip_status` (BOOLEAN): TRUE for top 10% of guests (those with highest LTV)

#### Table 2: `day07_bookings`
Create 400-600 booking records with:
- `booking_id` (TEXT, PRIMARY KEY): Format "BKG-000001", "BKG-000002", etc.
- `guest_id` (TEXT, FOREIGN KEY): References day07_guests.guest_id
- `booking_date` (DATE): When the reservation was made (can be 1-90 days before check_in_date)
- `check_in_date` (DATE): Between 2022-06-01 and 2024-12-31
- `check_out_date` (DATE): 1-7 nights after check_in_date (most common: 2-3 nights)
- `room_type` (TEXT): "Standard", "Deluxe", "Suite", "Family Room"
- `number_of_guests` (INTEGER): Between 1 and 4
- `number_of_rooms` (INTEGER): Usually 1, occasionally 2 for families
- `booking_source` (TEXT): "Booking.com" (50%), "Direct Website" (30%), "Airbnb" (15%), "Phone" (5%)
- `status` (TEXT): "Confirmed", "Checked-In", "Checked-Out", "Cancelled" (10% cancelled)
- `total_price_brl` (DECIMAL): Price per night varies by room type and season
  - Standard: R$ 300-500
  - Deluxe: R$ 500-800
  - Suite: R$ 800-1200
  - Family Room: R$ 700-1000
  - **High season** (Jun-Aug, Dec-Jan): +40% price
  - **Low season** (Mar-May, Sep-Nov): base price
- `commission_pct` (DECIMAL): 0% for Direct, 15% for Booking.com, 12% for Airbnb, 0% for Phone
- `payment_method` (TEXT): "Credit Card", "Pix", "Bank Transfer", "Cash"
- `special_requests` (TEXT): "Late check-in", "Vegetarian breakfast", "Extra bed", NULL for 60%

#### Table 3: `day07_stays`
Create a stay record for each non-cancelled booking (90% of bookings) with:
- `stay_id` (INTEGER, PRIMARY KEY): Auto-increment starting from 1
- `booking_id` (TEXT, FOREIGN KEY): References day07_bookings.booking_id
- `guest_id` (TEXT, FOREIGN KEY): References day07_guests.guest_id
- `actual_check_in` (DATETIME): Same as booking check_in_date, time between 14:00-20:00
- `actual_check_out` (DATETIME): Same as booking check_out_date, time between 08:00-12:00
- `breakfast_included` (BOOLEAN): TRUE for 80% of stays
- `extras_spent_brl` (DECIMAL): Between R$ 0 and R$ 300 (spa, room service, tours)
  - 40% of guests spend nothing
  - 40% spend R$ 50-150
  - 20% spend R$ 150-300
- `guest_rating` (INTEGER): 1-5 stars (mostly 4-5, with 10% giving 3 or below)
- `review_text` (TEXT): Short review in Portuguese or NULL for 70% (e.g., "Lugar maravilhoso!", "Vista incrível", "Café da manhã excelente")
- `repeat_guest` (BOOLEAN): TRUE if guest_id has previous stays
- `referral_source` (TEXT): NULL, "Friend Recommendation", "Google Search", "Social Media", "Returning Guest"

### 2. Data Relationships and Business Logic

**Ensure:**
- **Cohort Distribution**: Spread guests' first bookings evenly across 24 months (2022-01 to 2024-12)
- **Repeat Guests**: 30% of guests should have 2+ bookings (cohort retention)
  - First-timers: 70%
  - 2 visits: 20%
  - 3-4 visits: 8%
  - 5+ visits: 2% (VIP guests)
- **Retention Patterns**:
  - 1-month return: 15% of cohort
  - 3-month return: 25% of cohort
  - 6-month return: 35% of cohort
  - 12-month return: 40% of cohort
- **Seasonal Patterns**:
  - **High season** (Jun-Aug winter, Dec-Jan summer): 50% of bookings
  - **Low season**: 50% of bookings
  - Higher prices and occupancy in high season
- **Cancellation Logic**: 10% cancellation rate, more common for bookings made >60 days in advance
- **LTV Patterns**:
  - Average guest LTV: R$ 1,200-1,500
  - Top 10% guests: R$ 4,000-8,000 (multiple visits, suites, extras)
  - One-time guests: R$ 600-1,200
- **Booking Lead Time**:
  - High season: 30-90 days advance
  - Low season: 5-30 days advance
  - Direct bookings tend to have shorter lead times

### 3. Output Format

Generate Python code using SQLite3 that:
1. Creates the three tables with proper schema and foreign keys
2. Inserts synthetic data using realistic patterns for a Brazilian pousada
3. Saves to `data/day07_hospitality.db`
4. Prints summary statistics after generation
5. Validates data integrity (all FKs valid, dates logical, cohorts distributed)

### 4. Code Structure

```python
#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 07: Hospitality LTV & Cohort Analysis

This script generates realistic pousada (Brazilian boutique inn) data for:
- Guest profiles with demographics
- Booking records mimicking Booking.com API structure
- Stay details with ratings and extras

Business Context: Carol's pousada in Campos do Jordão
- Boutique mountain resort in São Paulo state
- Peak seasons: Winter (Jun-Aug) and Summer holidays (Dec-Jan)
- Target: Weekend couples and family vacations

Usage:
    python day07_DATA_synthetic_generator.py
"""

import sqlite3
import random
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Tuple

# Configuration (day-scoped naming)
DAY07_DB_PATH = "data/day07_hospitality.db"
DAY07_NUM_GUESTS = 180
DAY07_NUM_BOOKINGS = 500
DAY07_COHORT_MONTHS = 24  # 2 years of cohorts
DAY07_REPEAT_GUEST_PCT = 0.30  # 30% are repeat customers
DAY07_CANCELLATION_RATE = 0.10
DAY07_HIGH_SEASON_MONTHS = [6, 7, 8, 12, 1]  # Jun-Aug (winter), Dec-Jan (summer)

# Brazilian-specific data
DAY07_FIRST_NAMES = [
    "João", "Maria", "José", "Ana", "Carlos", "Mariana", "Pedro", "Julia",
    "Lucas", "Beatriz", "Gabriel", "Larissa", "Rafael", "Camila", "Fernando",
    "Patricia", "Rodrigo", "Amanda", "Bruno", "Fernanda", "Diego", "Isabela"
]

DAY07_LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Ferreira",
    "Rodrigues", "Almeida", "Pereira", "Carvalho", "Ribeiro", "Martins",
    "Araújo", "Melo", "Barbosa", "Gomes", "Cardoso", "Nascimento", "Castro"
]

# Rest of the code here...
```

### 5. Key Requirements

- **Day-scoped naming**: Use `day07_` prefix for all tables, `DAY07_` for constants
- **Include docstrings**: Explain business logic, especially cohort/LTV calculations
- **Data validation**:
  - No negative amounts
  - check_out_date > check_in_date
  - booking_date <= check_in_date
  - All foreign keys valid
  - Price varies by season and room type
- **Print useful output**: "Generated X guests, Y bookings, Z stays"
- **Create indexes**: On guest_id, booking_date, check_in_date for query performance
- **Brazilian context**: Use BRL currency, Brazilian names, Portuguese review snippets
- **Cohort Distribution**: Ensure first bookings are evenly spread across 24 months for meaningful cohort analysis

### 6. Sample Output Expected

```
Generating synthetic hospitality data for Carol's Pousada...

Created 180 guests
  - Guest types: Couple (45%), Family (30%), Individual (15%), Business (10%)
  - Countries: Brazil (80%), Argentina (15%), Other (5%)
  - VIP guests: 18 (10%)

Generated 500 bookings across 24 cohort months
  - Date range: 2022-06-01 to 2024-12-31
  - Booking sources: Booking.com (50%), Direct (30%), Airbnb (15%), Phone (5%)
  - Room types: Standard (40%), Deluxe (35%), Suite (15%), Family (10%)
  - Status: Confirmed/Completed (90%), Cancelled (10%)
  - Total revenue potential: R$ 750,000

Cohort distribution (first booking month):
  2022-H2: 72 guests
  2023-H1: 54 guests
  2023-H2: 68 guests
  2024: 86 guests

Repeat guest analysis:
  - First-time guests: 126 (70%)
  - 2 visits: 36 (20%)
  - 3-4 visits: 14 (8%)
  - 5+ visits: 4 (2%)

Created 450 stay records (90% of bookings - 10% cancelled)
  - Average stay duration: 2.5 nights
  - Average guest rating: 4.3/5.0
  - Total extras revenue: R$ 45,000
  - Reviews submitted: 30%

Seasonal analysis:
  - High season bookings: 250 (50%)
  - Low season bookings: 250 (50%)
  - Average price (high): R$ 840/night
  - Average price (low): R$ 600/night

Database saved to: data/day07_hospitality.db

Top guests by LTV (cumulative spend):
  GUEST-042: R$ 7,200 (6 visits, 18 nights)
  GUEST-089: R$ 6,400 (5 visits, 16 nights)
  GUEST-123: R$ 5,800 (4 visits, 14 nights)
```

### 7. Testing Requirements

After generation, the script should validate:
- All foreign keys in bookings reference valid guest_ids
- All foreign keys in stays reference valid booking_ids
- All dates are in logical order: registration_date <= booking_date <= check_in_date < check_out_date
- All prices are positive and within expected ranges
- At least 25% of guests have multiple bookings (repeat customers)
- Cancellation rate is approximately 10%
- Cohorts are evenly distributed across 24 months
- VIP guests have significantly higher cumulative spend
- Database file is created and contains all three tables

### 8. Cohort & LTV Considerations

**Critical for Analysis:**
- **First Booking Date**: This determines the guest's cohort (YYYY-MM of first booking)
- **Subsequent Bookings**: Must be spaced realistically (not same week, typically 1-12 months apart)
- **LTV Accumulation**: Sum of (room_price + extras) across all stays
- **Retention Windows**: Ensure some guests return at 1M, 3M, 6M, 12M intervals for retention matrix
- **Obvious Insights**: Data should show clear patterns like:
  - Winter cohorts (Jun-Aug) have higher initial spend
  - Couples tend to return more frequently than business travelers
  - Direct bookings have higher LTV (no commission, better margins)
  - VIP guests book premium rooms and spend more on extras

## Constraints

- Total execution time: < 10 seconds
- Database file size: < 2 MB
- Use only Python standard library + sqlite3
- No external API calls or data sources
- Reproducible: Use `random.seed(42)` for consistent results
- Brazilian context: Names, currency (BRL), seasonal patterns

## Deliverable

Complete Python script named `day07_DATA_synthetic_generator.py` that generates realistic hospitality data following all requirements above, optimized for cohort analysis and LTV calculations.

---

## References

Based on Booking.com Connectivity APIs structure:
- [Understanding the Reservations API](https://developers.booking.com/connectivity/docs/reservations-api/reservations-overview)
- [Retrieving reservations summary](https://developers.booking.com/connectivity/docs/reservations-api/retrieving-reservations-summary)
- [About Booking.com Connectivity APIs](https://developers.booking.com/connectivity/docs)
