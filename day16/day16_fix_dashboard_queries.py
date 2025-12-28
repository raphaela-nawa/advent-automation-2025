"""
Fix existing Metabase dashboard by updating all card queries to use BigQuery syntax
"""

import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).parent.parent
env_path = root_dir / "config" / ".env"
load_dotenv(env_path)

METABASE_URL = os.getenv("DAY16_METABASE_URL")
METABASE_API_KEY = os.getenv("DAY16_METABASE_API_KEY")
BIGQUERY_DATABASE_ID = 3  # Nomade Labs - BigQuery
DATASET = os.getenv("DAY16_BQ_DATASET", "day16_saas_metrics")
PROJECT = os.getenv("DAY16_GCP_PROJECT_ID", "advent2025-day16")

# Setup session
session = requests.Session()
session.headers.update({"X-Api-Key": METABASE_API_KEY})

print("=" * 70)
print("FIXING METABASE DASHBOARD QUERIES")
print("=" * 70)
print(f"\n🔗 Using Database: Nomade Labs - BigQuery (ID: {BIGQUERY_DATABASE_ID})")
print(f"📊 Dataset: {PROJECT}.{DATASET}")

# Card definitions with correct BigQuery SQL
CARD_QUERIES = {
    "Current MRR": {
        "sql": f"""
SELECT ROUND(current_mrr, 2) as current_mrr
FROM `{PROJECT}.{DATASET}.day06_dashboard_kpis`
        """.strip(),
        "visualization": "scalar"
    },
    "Churn Rate (%)": {
        "sql": f"""
SELECT ROUND(overall_churn_rate_pct, 2) as churn_rate_pct
FROM `{PROJECT}.{DATASET}.day06_dashboard_kpis`
        """.strip(),
        "visualization": "scalar"
    },
    "Active Customers": {
        "sql": f"""
SELECT active_customers
FROM `{PROJECT}.{DATASET}.day06_dashboard_kpis`
        """.strip(),
        "visualization": "scalar"
    },
    "Healthy Customers %": {
        "sql": f"""
SELECT ROUND((healthy_customers * 100.0 / (healthy_customers + at_risk_customers + critical_customers)), 1) as healthy_pct
FROM `{PROJECT}.{DATASET}.day06_dashboard_kpis`
        """.strip(),
        "visualization": "scalar"
    },
    "MRR Growth Over Time": {
        "sql": f"""
SELECT
  month,
  cumulative_mrr,
  net_mrr,
  new_mrr,
  expansion_mrr,
  contraction_mrr,
  churn_mrr
FROM `{PROJECT}.{DATASET}.day06_mrr_summary`
ORDER BY month ASC
        """.strip(),
        "visualization": "line"
    },
    "Month-over-Month Growth Rate": {
        "sql": f"""
SELECT
  month,
  ROUND(mom_growth_rate_pct, 2) as growth_rate_pct
FROM `{PROJECT}.{DATASET}.day06_mrr_summary`
ORDER BY month ASC
        """.strip(),
        "visualization": "line"
    },
    "Cohort Retention Curves": {
        "sql": f"""
SELECT
  cohort_month,
  months_since_signup,
  ROUND(retention_rate_pct, 2) as retention_rate_pct
FROM `{PROJECT}.{DATASET}.day06_retention_curves`
WHERE months_since_signup <= 12
ORDER BY cohort_month ASC, months_since_signup ASC
        """.strip(),
        "visualization": "line"
    },
    "Churn Heatmap": {
        "sql": f"""
SELECT
  cohort_month,
  plan_tier,
  ROUND(churn_rate_pct, 1) as churn_rate_pct
FROM `{PROJECT}.{DATASET}.day06_churn_by_cohort`
ORDER BY cohort_month DESC, plan_tier ASC
        """.strip(),
        "visualization": "table"
    },
    "Customer Health Distribution": {
        "sql": f"""
SELECT
  health_status,
  COUNT(*) as customer_count
FROM `{PROJECT}.{DATASET}.day06_customer_health`
WHERE customer_status = 'active'
GROUP BY health_status
ORDER BY customer_count DESC
        """.strip(),
        "visualization": "pie"
    },
    "Top At-Risk Customers": {
        "sql": f"""
SELECT
  customer_id,
  ROUND(ltv_estimate, 2) as ltv,
  ROUND(mrr_current, 2) as current_mrr,
  health_status,
  plan_tier
FROM `{PROJECT}.{DATASET}.day06_customer_health`
WHERE health_status = 'At Risk' AND customer_status = 'active'
ORDER BY ltv_estimate DESC
LIMIT 10
        """.strip(),
        "visualization": "table"
    }
}

# Find all dashboards
print(f"\n📋 Finding Day 16 dashboard...")
response = session.get(f"{METABASE_URL}/api/dashboard")
if response.status_code != 200:
    print(f"❌ Failed to fetch dashboards: {response.status_code}")
    exit(1)

dashboards = response.json()
day16_dashboard = None
for dash in dashboards:
    if 'saas' in dash['name'].lower() or 'health' in dash['name'].lower():
        day16_dashboard = dash
        print(f"✅ Found dashboard: {dash['name']} (ID: {dash['id']})")
        break

if not day16_dashboard:
    print("❌ Could not find Day 16 dashboard")
    exit(1)

# Get dashboard details
dashboard_id = day16_dashboard['id']
response = session.get(f"{METABASE_URL}/api/dashboard/{dashboard_id}")
if response.status_code != 200:
    print(f"❌ Failed to fetch dashboard details: {response.status_code}")
    exit(1)

dashboard = response.json()
print(f"\n🔍 Dashboard has {len(dashboard['dashcards'])} cards")

# Update each card
print(f"\n🔧 Updating card queries...")
updated_count = 0
skipped_count = 0

for dashcard in dashboard['dashcards']:
    card = dashcard.get('card')
    if not card:
        continue

    card_id = card.get('id')
    if not card_id:
        print(f"  ⚠️  Skipping card - no ID found")
        skipped_count += 1
        continue

    card_name = card.get('name', 'Unknown')

    # Find matching query
    matching_query = None
    for query_name, query_config in CARD_QUERIES.items():
        if query_name.lower() in card_name.lower() or card_name.lower() in query_name.lower():
            matching_query = query_config
            break

    if not matching_query:
        print(f"  ⚠️  Skipping '{card_name}' - no matching query found")
        skipped_count += 1
        continue

    # Update card with SQL query
    print(f"\n  📊 Updating '{card_name}' (ID: {card_id})...")

    update_payload = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": matching_query["sql"],
                "template-tags": {}
            },
            "database": BIGQUERY_DATABASE_ID
        },
        "display": matching_query["visualization"],
        "name": card_name,
        "visualization_settings": {}
    }

    response = session.put(
        f"{METABASE_URL}/api/card/{card_id}",
        json=update_payload
    )

    if response.status_code == 200:
        print(f"     ✅ Updated successfully!")
        print(f"     📝 Query preview: {matching_query['sql'][:80]}...")
        updated_count += 1
    else:
        print(f"     ❌ Update failed: {response.status_code}")
        print(f"     Response: {response.text[:200]}")

print("\n" + "=" * 70)
print("DASHBOARD UPDATE COMPLETE")
print("=" * 70)
print(f"\n✅ Updated: {updated_count} cards")
print(f"⚠️  Skipped: {skipped_count} cards")
print(f"\n🔗 View dashboard: {METABASE_URL}/dashboard/{dashboard_id}")
print("\n💡 Refresh your Metabase dashboard to see the changes!")
print("=" * 70)
