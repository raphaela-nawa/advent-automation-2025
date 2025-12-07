# Codex Prompt: Generate Synthetic SaaS Health Metrics Data

## Context
Generate synthetic data for a SaaS company's health metrics tracking system. This data will be used to calculate MRR movements, churn rates, cohort retention, and customer health scores for dashboard visualization.

## Requirements

### 1. Generate Three Related Tables

#### Table 1: `day06_customers`
Create **500 unique customers** with:
- `customer_id` (TEXT, PRIMARY KEY): Format "cus_" + 16-char random string (Stripe-style: "cus_1234567890abcdef")
- `email` (TEXT): Realistic email addresses (e.g., "john.smith@techcorp.com")
- `signup_date` (DATE): Distributed across **24 months** (2023-01-01 to 2024-12-31)
  - **Cohort distribution**: More signups in early months, declining over time (realistic growth curve)
- `plan_tier` (TEXT): One of "Starter", "Pro", or "Enterprise"
  - Distribution: 50% Starter, 35% Pro, 15% Enterprise
- `mrr_current` (DECIMAL): Monthly Recurring Revenue based on plan tier:
  - Starter: $29-$99 (random variation)
  - Pro: $199-$499
  - Enterprise: $999-$2,999
- `status` (TEXT): Either "active" or "churned"
  - **Churn rate**: 5-8% monthly (realistic SaaS churn)
  - Older cohorts should have higher churn rates

#### Table 2: `day06_subscriptions`
Create **subscription history** for all 500 customers (multiple subscriptions per customer if they upgraded/downgraded):
- `subscription_id` (TEXT, PRIMARY KEY): Format "sub_" + 16-char random string (Stripe-style)
- `customer_id` (TEXT, FOREIGN KEY): References day06_customers.customer_id
- `start_date` (DATE): Subscription start date
  - First subscription: Same as customer signup_date
  - Subsequent subscriptions: After previous end_date (upgrades/downgrades)
- `end_date` (DATE): NULL if currently active, or churn/change date
- `mrr` (DECIMAL): MRR for this subscription period
- `plan_tier` (TEXT): "Starter", "Pro", or "Enterprise"

**Business Logic for Subscriptions:**
- **New MRR**: Customer's first subscription (start_date = signup_date)
- **Expansion MRR**: Upgrade from lower to higher tier (Starter → Pro → Enterprise)
  - 15-20% of customers should have at least one upgrade
- **Contraction MRR**: Downgrade from higher to lower tier
  - 5-10% of customers should have at least one downgrade
- **Churn MRR**: Subscription ends (end_date IS NOT NULL)
  - 5-8% monthly churn rate
- **Retention**: Active customers maintain same plan tier
  - Most customers (70-75%) should remain in original tier

#### Table 3: `day06_mrr_movements`
Create **pre-aggregated monthly MRR movements** for 24 months (2023-01 to 2024-12):
- `month` (DATE, PRIMARY KEY): First day of each month (e.g., "2023-01-01")
- `new_mrr` (DECIMAL): Sum of MRR from new customers that month
- `expansion_mrr` (DECIMAL): Sum of MRR increases from upgrades
- `contraction_mrr` (DECIMAL): Sum of MRR decreases from downgrades
- `churn_mrr` (DECIMAL): Sum of MRR lost from cancellations
- `net_mrr` (DECIMAL): Calculated as: new_mrr + expansion_mrr - contraction_mrr - churn_mrr

**Formula**: `net_mrr = new_mrr + expansion_mrr - contraction_mrr - churn_mrr`

### 2. Data Relationships and Business Logic

**Ensure Realistic SaaS Behavior:**

1. **MRR Growth Pattern**:
   - Start with ~$50K MRR in month 1
   - Grow to ~$200K MRR by month 24 (4x growth)
   - Growth should be mostly linear with some monthly variance

2. **Cohort Retention Curves**:
   - Month 0 (signup): 100% retention
   - Month 1: 90-95% retention
   - Month 3: 80-85% retention
   - Month 6: 70-75% retention
   - Month 12: 60-65% retention
   - Month 24: 50-55% retention

3. **Plan Tier Distribution**:
   - Starter: 50% of customers (entry point)
   - Pro: 35% of customers (sweet spot)
   - Enterprise: 15% of customers (high value)

4. **Customer Lifecycle Examples**:
   - **Happy Path**: Starter → Pro → Enterprise (stays active)
   - **Expansion**: Starter → Pro (stays active)
   - **Contraction**: Pro → Starter (stays active but downgraded)
   - **Churn**: Any tier → churned (end_date set)
   - **Stable**: Same tier throughout (most common)

5. **Edge Cases to Include**:
   - Customers who upgrade twice (Starter → Pro → Enterprise)
   - Customers who downgrade after upgrading (Pro → Starter)
   - Customers who churn immediately (month 1)
   - Customers who stay active for 24+ months
   - Enterprise customers with high MRR ($2K+/month)

### 3. Output Format

Generate Python code using SQLite3 that:
1. Creates the three tables with proper schema and foreign keys
2. Inserts synthetic data using realistic SaaS patterns
3. Saves to `data/day06_saas_metrics.db`
4. Prints comprehensive summary statistics after generation
5. Validates data integrity (foreign keys, date ranges, MRR calculations)

### 4. Code Structure

```python
#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 06: SaaS Health Metrics Foundation

This script generates realistic SaaS subscription data for executive dashboards:
- 500 customers across 24 months
- Subscription history with upgrades/downgrades/churn
- Pre-aggregated MRR movements for waterfall analysis

Stakeholder: SaaS Executive (C-level)
Use Case: MRR tracking, churn analysis, cohort retention, customer health scoring

Usage:
    python day06_DATA_synthetic_saas.py
"""

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
DAY06_DB_PATH = "data/day06_saas_metrics.db"
DAY06_NUM_CUSTOMERS = 500
DAY06_NUM_MONTHS = 24
DAY06_START_DATE = datetime(2023, 1, 1)

# Plan tier pricing
DAY06_PLAN_PRICING = {
    'Starter': (29, 99),      # Min, Max MRR
    'Pro': (199, 499),
    'Enterprise': (999, 2999)
}

# SaaS metrics targets
DAY06_MONTHLY_CHURN_RATE = 0.06  # 6% monthly churn
DAY06_UPGRADE_PROBABILITY = 0.18  # 18% upgrade rate
DAY06_DOWNGRADE_PROBABILITY = 0.08  # 8% downgrade rate

# Rest of the code here...
```

### 5. Key Requirements

- **Naming Convention**: Use `day06_` prefix for all tables, `DAY06_` for constants
- **Documentation**: Include docstrings explaining SaaS business logic
- **Data Validation**:
  - No negative MRR values
  - Dates in valid ranges (2023-01-01 to 2024-12-31)
  - end_date > start_date (if not NULL)
  - Foreign keys validated
- **Indexes**: Create indexes on:
  - `day06_subscriptions.customer_id`
  - `day06_subscriptions.start_date`
  - `day06_customers.signup_date`
  - `day06_customers.status`
- **Realistic IDs**: Use Stripe-style IDs (e.g., "cus_AbCdEf1234567890")

### 6. Sample Output Expected

```
Generating synthetic SaaS metrics data...
============================================================

Created 500 customers across 24 months (2023-01 to 2024-12)
  - Starter tier: 250 customers (50%)
  - Pro tier: 175 customers (35%)
  - Enterprise tier: 75 customers (15%)
  - Active customers: 312 (62%)
  - Churned customers: 188 (38%)

Generated 687 subscription records
  - New subscriptions: 500
  - Upgrades (Expansion): 98 (19.6%)
  - Downgrades (Contraction): 42 (8.4%)
  - Churned subscriptions: 188 (37.6%)

MRR Movements Summary (24 months):
  - Total New MRR: $1,245,678
  - Total Expansion MRR: $234,567
  - Total Contraction MRR: $67,890
  - Total Churn MRR: $456,789
  - Net MRR Growth: $955,566

Current MRR (Month 24): $203,456
  - Starting MRR (Month 1): $52,345
  - MRR Growth: 288% over 24 months

Cohort Retention Analysis:
  - 2023-01 cohort (24 months old): 54% retained
  - 2023-06 cohort (18 months old): 62% retained
  - 2024-01 cohort (12 months old): 67% retained
  - 2024-06 cohort (6 months old): 78% retained

Data Integrity Checks:
  ✓ All foreign keys valid
  ✓ All dates within valid range
  ✓ All MRR values positive
  ✓ MRR movements balance correctly
  ✓ No orphaned subscriptions

Database saved to: data/day06_saas_metrics.db
File size: 248 KB
============================================================
```

### 7. Testing Requirements

After generation, the script should validate:
- All `customer_id` in `day06_subscriptions` exist in `day06_customers`
- All subscription dates are within customer lifetime
- MRR movements sum correctly for each month
- At least 50% of customers have only 1 subscription (stable customers)
- At least 15% of customers have 2+ subscriptions (lifecycle changes)
- Current MRR matches sum of active subscriptions
- Churn rate is within expected range (5-8% monthly)

### 8. Advanced Requirements

**Cohort-Based Data Generation:**
```python
def day06_generate_cohort_customers(cohort_month: datetime, num_customers: int) -> List[Dict]:
    """
    Generate customers for a specific signup cohort.

    Apply cohort-specific retention curves:
    - Older cohorts have higher cumulative churn
    - Newer cohorts have higher retention
    """
    # Implementation details...
```

**MRR Movement Calculation:**
```python
def day06_calculate_mrr_movements(month: datetime, subscriptions: List[Dict]) -> Dict:
    """
    Calculate New, Expansion, Contraction, and Churn MRR for a given month.

    Returns:
        {
            'new_mrr': float,
            'expansion_mrr': float,
            'contraction_mrr': float,
            'churn_mrr': float,
            'net_mrr': float
        }
    """
    # Implementation details...
```

**Customer ID Generation (Stripe-style):**
```python
def day06_generate_customer_id() -> str:
    """Generate Stripe-style customer ID: cus_[16-char random string]"""
    random_str = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    return f"cus_{random_str}"

def day06_generate_subscription_id() -> str:
    """Generate Stripe-style subscription ID: sub_[16-char random string]"""
    random_str = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    return f"sub_{random_str}"
```

## Constraints

- **Execution Time**: < 10 seconds
- **Database Size**: < 500 KB
- **Dependencies**: Python standard library + sqlite3 only
- **Reproducibility**: Use `random.seed(42)` for consistent results
- **No External Calls**: No API calls or external data sources

## Deliverable

Complete Python script named `day06_DATA_synthetic_saas.py` that:
1. Generates 500 customers with realistic SaaS behavior
2. Creates subscription history with upgrades/downgrades/churn
3. Pre-calculates MRR movements for 24 months
4. Validates data integrity
5. Prints comprehensive summary statistics
6. Saves to `data/day06_saas_metrics.db`

This data will feed into 4 SQL views:
- `day06_mrr_summary` (MRR waterfall)
- `day06_churn_by_cohort` (churn analysis)
- `day06_retention_curves` (retention over time)
- `day06_customer_health` (LTV/CAC scoring)

---

**IMPORTANT**: This data should look realistic enough to demonstrate how SaaS health metrics work in practice. Focus on creating meaningful patterns that will result in interesting dashboard visualizations on Day 19.
