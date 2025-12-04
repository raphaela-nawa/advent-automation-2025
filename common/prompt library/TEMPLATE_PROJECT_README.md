# TEMPLATE: Project README for Modeling Projects (Days 6-10)

**HOW TO USE THIS TEMPLATE:**
1. Copy this entire file to your project folder as `README.md`
2. Replace all `[PLACEHOLDER_TEXT]` with your actual content
3. Remove sections that don't apply to your project
4. Keep the structure and ordering of sections
5. Ensure all code examples use the correct `dayXX_` prefix for your day number

---

# Day [DAY_NUMBER]: [PROJECT_NAME]

> [ONE_LINE_DESCRIPTION]

**Part of:** [Advent Automation 2025 - 25 Days of Data Engineering](../../README.md)

---

## Table of Contents
- [Challenge](#challenge)
- [Built For](#built-for)
- [What It Does](#what-it-does)
- [Technical Stack](#technical-stack)
- [Data](#data)
- [Quick Start](#quick-start)
- [Architectural Decisions](#architectural-decisions)
- [Results](#results)
- [How to Adapt for Your Data](#how-to-adapt-for-your-data)
- [What I Learned](#what-i-learned)
- [Links](#links)

---

## Challenge

[BUSINESS_CHALLENGE]

**Why this matters:**
[Explain the business impact or technical importance. 2-3 sentences.]

---

## Built For

**Stakeholder:** [STAKEHOLDER_NAME]
**Role/Context:** [STAKEHOLDER_ROLE]

[Briefly explain why this is relevant to them. 1-2 sentences.]

---

## What It Does

[CORE_FUNCTIONALITY_BULLETS]

**Example structure:**
- Calculates [metric/model] using [technique]
- Generates [output type] showing [business insight]
- Implements [data modeling pattern] for [use case]
- Provides [analytical capability] for [stakeholder need]

---

## Technical Stack

**Language:** Python 3.11+
**Database:** [SQLite / PostgreSQL / BigQuery]
**Data Modeling:** [SQL / dbt Core 1.7+]

**Key Libraries:**
- [Library 1] - [Purpose]
- [Library 2] - [Purpose]
- [Library 3] - [Purpose]

**Output Format:** [CSV / Database Tables / dbt Models / SQL Views]

---

## Data

**Source:** Synthetic data generated for demonstration
**Type:** [Business domain - e.g., Financial consulting, Hospitality, Family office]
**Volume:** [Approximate row counts for main tables]

**Schema Overview:**

```
[TABLE_NAME_1] (dayXX_[table_name])
├── [column_1] ([type]) - [description]
├── [column_2] ([type]) - [description]
└── [column_3] ([type]) - [description]

[TABLE_NAME_2] (dayXX_[table_name])
├── [column_1] ([type]) - [description]
└── [column_2] ([type]) - [description]
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- [Additional tool - e.g., SQLite3, dbt-core, etc.]

### Setup Instructions

#### 1. Clone and Navigate
```bash
cd advent-automation-2025/day[XX]
```

#### 2. Install Dependencies
```bash
pip install -r day[XX]_requirements.txt
```

#### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add the following to your root `config/.env`:
```bash
# Day [XX] - [Project Name]
DAYXX_DB_PATH=/path/to/day[XX]_database.db
DAYXX_[SPECIFIC_CONFIG_1]=[value]
DAYXX_[SPECIFIC_CONFIG_2]=[value]
```

#### 4. Generate Synthetic Data
```bash
python day[XX]_DATA_synthetic_generator.py
```

Expected output:
```
Generating synthetic data...
Created [X] [entity_type_1]
Created [Y] [entity_type_2]
Data saved to data/day[XX]_database.db
```

#### 5. Run Models

**For SQL Projects:**
```bash
sqlite3 data/day[XX]_database.db < models/day[XX]_MODEL_[model_name].sql
```

**For dbt Projects:**

First, configure your dbt profile:
```bash
# Copy profile template
cp profiles.yml ~/.dbt/profiles.yml

# Or add to existing profiles.yml:
day[XX]_[project_name]:
  target: dev
  outputs:
    dev:
      type: sqlite
      threads: 1
      database: 'data/day[XX]_database.db'
      schema: 'main'
```

Then run dbt:
```bash
dbt deps
dbt run
dbt test
```

#### 6. Validate Results

**For SQL Projects:**
```bash
sqlite3 data/day[XX]_database.db
```

```sql
-- Check model outputs
SELECT * FROM day[XX]_[model_name] LIMIT 5;
SELECT COUNT(*) FROM day[XX]_[model_name];

-- Validate specific metrics
SELECT [key_metric] FROM day[XX]_[view_name];
```

**For dbt Projects:**
```bash
# View test results
dbt test --select day[XX]_[model_name]

# Generate and serve documentation
dbt docs generate
dbt docs serve
# Open http://localhost:8080
```

### Expected Output

After successful execution, you should see:
- [Output 1 - e.g., "4 SQL views created in the database"]
- [Output 2 - e.g., "dbt models materialized successfully"]
- [Output 3 - e.g., "All tests passing (5/5)"]

---

## Architectural Decisions

### Decision 1: [DECISION_TITLE_1]

**Context:**
[Why was this decision necessary? What problem needed solving?]

**Example:**
"Needed to calculate multiple dependent metrics (utilization rate, profitability, ROI) without duplicating logic or creating maintenance burden."

**Options Considered:**
1. **[Option 1]** - [Brief description with pros/cons]
2. **[Option 2]** - [Brief description with pros/cons]
3. **[Option 3]** - [Brief description with pros/cons]
4. **[Option 4]** - [Brief description with pros/cons]

**Decision:**
[What was chosen?]

**Example:**
"Used CTEs (Common Table Expressions) for all metric calculations, with a clear dependency chain: raw data -> staging -> intermediate metrics -> final metrics."

**Rationale:**
[Why was this the best choice for this context?]

**Tradeoffs:**
- **Gained:**
  - [Benefit 1]
  - [Benefit 2]
  - [Benefit 3]
- **Sacrificed:**
  - [Cost 1]
  - [Cost 2]

**Learning:**
[What would you take to future projects?]

**Example:**
"For analytical queries with multiple dependent calculations under 1M rows, CTEs provide the best balance of readability and performance. Would consider materialized views or temp tables only for larger datasets or frequently-run queries."

---

### Decision 2: [DECISION_TITLE_2]

**Context:**
[Describe the situation that required a decision]

**Options Considered:**
1. **[Option 1]**
2. **[Option 2]**
3. **[Option 3]**

**Decision:**
[State what was chosen]

**Rationale:**
[Explain why this was the best choice]

**Tradeoffs:**
- **Gained:**
  - [Benefit 1]
  - [Benefit 2]
- **Sacrificed:**
  - [Cost 1]
  - [Cost 2]

**Learning:**
[Key takeaway for future projects]

---

### Decision 3: [DECISION_TITLE_3]

**Context:**
[Describe the situation]

**Options Considered:**
1. **[Option 1]**
2. **[Option 2]**

**Decision:**
[State what was chosen]

**Rationale:**
[Explain why]

**Tradeoffs:**
- **Gained:** [Benefits]
- **Sacrificed:** [Costs]

**Learning:**
[Key takeaway]

---

## Results

### Sample Outputs

#### [Metric/Model Name 1]

**Query:**
```sql
SELECT * FROM day[XX]_[model_name] LIMIT 5;
```

**Sample Results:**
```
[SAMPLE_OUTPUT_TABLE_OR_DESCRIPTION]
```

#### [Metric/Model Name 2]

**Query:**
```sql
SELECT [columns] FROM day[XX]_[another_model];
```

**Sample Results:**
```
[SAMPLE_OUTPUT_TABLE_OR_DESCRIPTION]
```

### Key Insights from Synthetic Data

**Note:** These insights are from synthetic data. With real data, you'd see actual business trends specific to your organization.

- **[Insight Category 1]:** [Specific finding with numbers]
- **[Insight Category 2]:** [Specific finding with numbers]
- **[Insight Category 3]:** [Specific finding with numbers]
- **[Insight Category 4]:** [Specific finding with numbers]

**Example structure:**
- **Utilization Rate:** Average of 68% across all consultants, with top performers at 85%+
- **Profitability:** 3 projects account for 60% of total profit
- **Client ROI:** Ranges from 2.1x to 5.8x, with marketing clients showing highest returns
- **Seasonal Patterns:** Q4 shows 35% higher booking rates than Q2

### Visual Examples

[SPACE FOR SCREENSHOTS OR DIAGRAMS]

**For SQL Projects:**
- Screenshot of key query results
- ERD diagram (text-based or image)
- Sample dashboard mockup (if applicable)

**For dbt Projects:**
- Screenshot of dbt DAG (lineage graph)
- Test results summary
- Documentation site preview

**For Data Warehouse Projects:**
- Star schema diagram
- SCD Type 2 historical tracking example
- Sample analytical query results

---

## How to Adapt for Your Data

This project uses synthetic data for demonstration, but it's designed to be production-ready with minimal changes.

### Step 1: Understand Current Schema

**Current Tables:**
```
day[XX]_[table_1]: [Brief description]
day[XX]_[table_2]: [Brief description]
day[XX]_[table_3]: [Brief description]
```

**Current Business Logic:**
- [Calculation 1]: [Formula or description]
- [Calculation 2]: [Formula or description]
- [Threshold/Rule]: [Current value and purpose]

### Step 2: Map Your Data

Create a mapping between your data and the expected schema:

| Your Column | Expected Column | Transformation Needed |
|-------------|----------------|----------------------|
| [your_col_1] | day[XX]_[expected_col_1] | [None / Date format / Calculation] |
| [your_col_2] | day[XX]_[expected_col_2] | [None / Join / Aggregation] |
| [your_col_3] | day[XX]_[expected_col_3] | [None / Type cast / Lookup] |

### Step 3: Modify Data Generator

**Option A: Replace with Real Extraction**

Replace `day[XX]_DATA_synthetic_generator.py` with your extraction logic:

```python
# day[XX]_DATA_extract_real.py
import [your_data_source_library]
from day[XX]_CONFIG_settings import DAYXX_DB_PATH

def day[XX]_extract_from_your_system():
    """
    Extract real data from your system.
    Adjust connection details in .env file.
    """
    # Connect to your data source
    conn = [your_connection_logic]

    # Extract data
    [table_1]_data = [your_query_1]
    [table_2]_data = [your_query_2]

    # Transform to match schema
    transformed = day[XX]_transform_to_schema([table_1]_data)

    # Load to database
    day[XX]_load_to_db(transformed, DAYXX_DB_PATH)

def day[XX]_transform_to_schema(raw_data):
    """
    Transform your data format to match expected schema.
    """
    # Your transformation logic here
    pass
```

**Option B: Modify Synthetic Generator to Match Your Schema**

If your schema differs significantly, adjust the generator:

```python
# In day[XX]_DATA_synthetic_generator.py

# Change table structure
def day[XX]_generate_[table_name]():
    return pd.DataFrame({
        'day[XX]_[your_column_1]': [your_data_generation],
        'day[XX]_[your_column_2]': [your_data_generation],
        # Add/remove columns as needed
    })
```

### Step 4: Adjust Business Logic

Review and adjust calculations in your models:

**For SQL Projects:**
```sql
-- In models/day[XX]_MODEL_metrics.sql

-- Example: Adjust utilization rate threshold
WITH day[XX]_utilization AS (
    SELECT
        consultant_id,
        billable_hours / total_hours as utilization_rate
    FROM day[XX]_timesheets
    WHERE total_hours > 0
)
SELECT
    *,
    CASE
        WHEN utilization_rate >= 0.75 THEN 'High'  -- Adjust this threshold
        WHEN utilization_rate >= 0.50 THEN 'Medium'
        ELSE 'Low'
    END as utilization_category
FROM day[XX]_utilization;
```

**For dbt Projects:**
```yaml
# In dbt_project.yml, adjust variables
vars:
  day[XX]_target_utilization: 0.75  # Change to your target
  day[XX]_billable_rate: 150.00     # Change to your rate
  day[XX]_min_project_value: 5000   # Change to your threshold
```

### Step 5: Update Configuration

Update your `.env` file:
```bash
# Point to real data sources
DAYXX_DB_PATH=/path/to/production/database.db
DAYXX_SOURCE_SYSTEM_URL=https://your-system.com/api
DAYXX_SOURCE_API_KEY=your_api_key_here

# Adjust business parameters
DAYXX_FISCAL_YEAR_START=4  # April for fiscal year starting in April
DAYXX_RETENTION_WINDOW_DAYS=90
DAYXX_MIN_COHORT_SIZE=10
```

### Step 6: Validate with Real Data

**Testing Strategy:**
1. **Small Sample First:** Run with 1 week or 1 month of real data
2. **Validate Known Metrics:** Compare outputs to existing reports/calculations
3. **Check Edge Cases:** Look for null values, outliers, data quality issues
4. **Incremental Scale:** Gradually increase to full dataset

**Validation Queries:**
```sql
-- Compare row counts
SELECT
    'Expected' as source, [expected_count] as count
UNION ALL
SELECT
    'Actual' as source, COUNT(*) as count
FROM day[XX]_[table_name];

-- Check for data quality issues
SELECT
    SUM(CASE WHEN [critical_field] IS NULL THEN 1 ELSE 0 END) as null_count,
    MIN([date_field]) as earliest_date,
    MAX([date_field]) as latest_date
FROM day[XX]_[table_name];

-- Validate business logic
SELECT
    [group_by_field],
    [calculated_metric],
    [known_metric_for_comparison]
FROM day[XX]_[model_name]
WHERE [calculated_metric] != [known_metric_for_comparison];
```

### Step 7: Document Your Changes

Create a `day[XX]_ADAPTATION_NOTES.md` file documenting:
- Schema changes made
- Business logic adjustments
- Configuration values used
- Any assumptions or limitations
- Data quality issues encountered

---

## What I Learned

### Technical Skills

**[Skill Area 1]:**
- [Specific learning point 1]
- [Specific learning point 2]

**[Skill Area 2]:**
- [Specific learning point 1]
- [Specific learning point 2]

**[Skill Area 3]:**
- [Specific learning point 1]

**Example structure:**

**SQL & Data Modeling:**
- How to use window functions (RANK, LAG) for cohort analysis
- When CTEs are more appropriate than subqueries or temp tables
- Implementing SCD Type 2 for historical tracking

**dbt:**
- Setting up incremental models with proper unique keys
- Writing custom macros for reusable business logic
- Configuring source freshness tests

**Business Domain:**
- How consulting firms track utilization and profitability
- Key metrics for hospitality operations (LTV, retention, conversion)
- Family office asset tracking and reporting requirements

### Process & Approach

**What Worked Well:**
- [Approach or technique that was effective]
- [Time management strategy that helped]
- [Tool or resource that was valuable]

**What I'd Do Differently:**
- [Lesson learned about approach]
- [Alternative technique to try next time]
- [Process improvement for future projects]

**Example:**

**What Worked Well:**
- Starting with ER diagram on paper before writing SQL
- Writing tests first (dbt) to clarify expected behavior
- Using ChatGPT to validate SQL logic for edge cases

**What I'd Do Differently:**
- Would create sample data with more edge cases earlier
- Should have read dbt docs on incremental models before starting
- Could have simplified first iteration (KISS principle)

### Business Understanding

**Domain Knowledge Gained:**
- [Business concept 1 learned]
- [Business concept 2 learned]
- [Industry practice or metric understood]

**Stakeholder Perspective:**
- [How this project helps the stakeholder]
- [What decisions this data enables]
- [Business impact of having this model]

---

## Links

**Project Links:**
- LinkedIn Post: [Add your LinkedIn post URL when published]
- Live Demo: [If applicable - Looker Studio, Streamlit, etc.]
- Documentation: [Link to additional docs if any]

**Related Projects:**
- [Previous Day Project] - [Link]
- [Next Day Project] - [Link]
- [Main Advent Calendar] - [Link to main README]

**Learning Resources:**
- [Resource 1 that helped you] - [URL]
- [Resource 2 that helped you] - [URL]
- [Documentation you referenced] - [URL]

---

## Project Structure

```
day[XX]/
├── data/
│   ├── raw/                          # Raw synthetic data (if applicable)
│   └── day[XX]_database.db           # SQLite database with all tables
├── models/                            # SQL models or dbt models
│   ├── day[XX]_MODEL_[name].sql      # Main transformation logic
│   └── ...
├── queries/                           # Sample analytical queries
│   ├── day[XX]_QUERY_[name].sql      # Demonstrating model usage
│   └── ...
├── docs/                              # Documentation files
│   └── day[XX]_ERD_[name].md         # Entity-relationship diagram
├── day[XX]_DATA_synthetic_generator.py  # Data generation script
├── day[XX]_CONFIG_settings.py        # Configuration and constants
├── day[XX]_requirements.txt          # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

**For dbt Projects, additional structure:**
```
day[XX]/
├── dbt_project.yml                   # dbt project configuration
├── profiles.yml                      # Database connection profiles
├── models/
│   ├── staging/
│   │   ├── sources.yml               # Source declarations
│   │   ├── stg_[name].sql            # Staging models
│   │   └── ...
│   ├── intermediate/
│   │   └── int_[name].sql            # Intermediate transformations
│   └── marts/
│       └── fct_[name].sql            # Final fact/dimension tables
├── macros/
│   └── [macro_name].sql              # Custom dbt macros
├── tests/
│   └── schema.yml                    # dbt tests configuration
└── ...
```

---

## Naming Conventions

**Critical for Project Isolation:**

All files, variables, classes, and functions must use the `day[XX]_` prefix to prevent conflicts with other days.

**Files:**
```
day[XX]_DATA_*.py      # Data extraction/generation
day[XX]_MODEL_*.sql    # Data models/transformations
day[XX]_PIPELINE_*.py  # Processing logic
day[XX]_CONFIG_*.py    # Configuration files
day[XX]_TEST_*.py      # Test files
day[XX]_QUERY_*.sql    # Sample queries
```

**Variables:**
```python
# Global variables/constants
DAYXX_DB_PATH = "data/day[XX]_database.db"
DAYXX_TARGET_UTILIZATION = 0.75
DAYXX_FISCAL_YEAR_START = 1

# Class names
class dayXX_MetricsCalculator:
    pass

# Function names
def dayXX_calculate_utilization():
    pass
```

**SQL Objects:**
```sql
-- Tables
CREATE TABLE day[XX]_projects (...);
CREATE TABLE day[XX]_timesheets (...);

-- Views
CREATE VIEW day[XX]_utilization_rate AS ...;
CREATE VIEW day[XX]_project_profitability AS ...;

-- CTEs
WITH day[XX]_billable_hours AS (...)
```

---

## Time Spent

**Total:** 3 hours

| Phase | Time | Notes |
|-------|------|-------|
| Setup & Planning | [XX] min | [What you did] |
| Data Generation | [XX] min | [What you did] |
| Model Development | [XX] min | [What you did] |
| Testing & Validation | [XX] min | [What you did] |
| Documentation | [XX] min | [What you did] |

**Pivot Points:** [Did you need to pivot? When and why?]

---

## Delivery Checklist

Before considering this project complete:

**Core Functionality:**
- [ ] SQL models execute without errors
- [ ] Results match expected business logic
- [ ] Data model is documented (ERD or written description)

**Reproducibility:**
- [ ] `.env.example` lists ALL necessary variables
- [ ] Variables added to root `config/.env` with `DAYXX_` prefix
- [ ] `day[XX]_requirements.txt` documents dependencies
- [ ] README Quick Start section works copy-paste

**Quality:**
- [ ] Code has docstrings explaining business logic
- [ ] Basic error handling present
- [ ] Informative logs showing progress

**Naming Convention:**
- [ ] All files have `day[XX]_` prefix
- [ ] All variables have `day[XX]_` or `DAYXX_` prefix
- [ ] All classes have `day[XX]_` prefix
- [ ] All functions have `day[XX]_` prefix

**Delivery:**
- [ ] Git commit with descriptive message
- [ ] Pushed to GitHub
- [ ] Tested in clean environment (clone + run from README)

---

**Part of:** [Advent Automation 2025 - 25 Days of Data Engineering](../../README.md)

Built with care in 3 hours for portfolio demonstration.
