# Codex Prompt: Generate Synthetic Financial Consulting Data

## Context
Generate synthetic data for a financial consulting firm's metrics tracking system. This data will be used to calculate utilization rates, project profitability, client ROI, and burn rates.

## Requirements

### 1. Generate Three Related Tables

#### Table 1: `day06_projects`
Create 15-20 consulting projects with:
- `project_id` (TEXT, PRIMARY KEY): Format "PROJ-001", "PROJ-002", etc.
- `client_id` (TEXT): Format "CLIENT-A", "CLIENT-B", etc. (5-7 unique clients)
- `project_name` (TEXT): Realistic consulting project names (e.g., "Marketing Strategy Overhaul", "Digital Transformation Roadmap")
- `start_date` (DATE): Between 2023-01-01 and 2024-06-01
- `end_date` (DATE): 1-6 months after start_date
- `budget_usd` (DECIMAL): Between $50,000 and $500,000
- `contract_type` (TEXT): "Fixed Price" or "Time & Materials"
- `status` (TEXT): "Active", "Completed", or "On Hold"

#### Table 2: `day06_timesheets`
Create 200-300 timesheet entries with:
- `timesheet_id` (INTEGER, PRIMARY KEY): Auto-increment starting from 1
- `project_id` (TEXT, FOREIGN KEY): References day06_projects.project_id
- `consultant_id` (TEXT): Format "CONS-001" through "CONS-010" (10 consultants)
- `date` (DATE): Within the project's start_date and end_date range
- `hours_worked` (DECIMAL): Between 2 and 10 hours per day
- `is_billable` (BOOLEAN): TRUE for 70-80% of entries, FALSE for others
- `hourly_rate_usd` (DECIMAL): Between $100 and $250 per hour
- `task_description` (TEXT): Brief descriptions like "Client workshop", "Data analysis", "Report writing"

#### Table 3: `day06_expenses`
Create 50-80 expense entries with:
- `expense_id` (INTEGER, PRIMARY KEY): Auto-increment starting from 1
- `project_id` (TEXT, FOREIGN KEY): References day06_projects.project_id
- `expense_date` (DATE): Within the project's date range
- `expense_type` (TEXT): "Travel", "Software Licenses", "Subcontractor", "Marketing", "Office Supplies"
- `amount_usd` (DECIMAL): Between $100 and $15,000
- `is_reimbursable` (BOOLEAN): TRUE for 60% of entries

### 2. Data Relationships and Business Logic

**Ensure:**
- Each project has 5-20 timesheet entries
- Each project has 1-5 expense entries
- Total timesheet hours per project should be realistic (50-500 hours)
- Some consultants should have higher utilization than others (70-85% billable for top performers, 40-60% for others)
- Some projects should be profitable (revenue > costs), others break-even or loss-making
- Include edge cases: projects with zero expenses, projects with 100% billable hours, projects with very low margins

### 3. Output Format

Generate Python code using SQLite3 that:
1. Creates the three tables with proper schema
2. Inserts synthetic data using realistic patterns
3. Saves to `data/day06_consulting.db`
4. Prints summary statistics after generation

### 4. Code Structure

```python
#!/usr/bin/env python3
"""
Synthetic Data Generator for Day 06: Financial Consulting Metrics

This script generates realistic consulting firm data for:
- Projects with clients and budgets
- Timesheets with billable/non-billable hours
- Expenses with reimbursement tracking

Usage:
    python day06_DATA_synthetic_generator.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DAY06_DB_PATH = "data/day06_consulting.db"
DAY06_NUM_PROJECTS = 18
DAY06_NUM_CONSULTANTS = 10
DAY06_NUM_CLIENTS = 6

# Rest of the code here...
```

### 5. Key Requirements

- Use proper day-scoped naming: `day06_` prefix for all tables, `DAY06_` for constants
- Include docstrings and comments explaining business logic
- Add data validation (no negative amounts, dates in valid ranges)
- Print useful output: "Generated X projects, Y timesheets, Z expenses"
- Create indexes on foreign keys for performance
- Include at least 3 consultants with different utilization profiles:
  - High performer: 80-85% billable
  - Average: 60-70% billable
  - Low: 40-50% billable (lots of internal/training time)

### 6. Sample Output Expected

```
Generating synthetic consulting data...

Created 18 projects across 6 clients
  - Budget range: $50,000 - $500,000
  - Total portfolio value: $3,850,000

Generated 287 timesheet entries for 10 consultants
  - Total hours: 1,843 hours
  - Billable hours: 1,398 (76%)
  - Revenue potential: $234,500

Created 64 expense entries
  - Total expenses: $128,450
  - Reimbursable: $78,200 (61%)

Database saved to: data/day06_consulting.db

Top consultants by billable hours:
  CONS-003: 85% billable (172 hours)
  CONS-007: 82% billable (164 hours)
  CONS-001: 78% billable (156 hours)
```

### 7. Testing Requirements

After generation, the script should validate:
- All foreign keys reference valid project_ids
- All dates are within valid ranges
- All amounts are positive
- At least 50% of projects have both timesheets and expenses
- Database file is created and is not empty

## Constraints

- Total execution time: < 5 seconds
- Database file size: < 1 MB
- Use only Python standard library + sqlite3
- No external API calls or data sources
- Reproducible: Use `random.seed(42)` for consistent results

## Deliverable

Complete Python script named `day06_DATA_synthetic_generator.py` that generates realistic consulting data following all requirements above.
