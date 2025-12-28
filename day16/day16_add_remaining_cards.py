"""
Add remaining 6 cards to the existing Metabase dashboard
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
DASHBOARD_ID = 12  # Murilo's SaaS Health Metrics Dashboard

# Setup session
session = requests.Session()
session.headers.update({"X-Api-Key": METABASE_API_KEY})

print("=" * 70)
print("ADDING REMAINING CARDS TO DASHBOARD")
print("=" * 70)
print(f"\n🔗 Dashboard ID: {DASHBOARD_ID}")
print(f"📊 Database: Nomade Labs - BigQuery (ID: {BIGQUERY_DATABASE_ID})")
print(f"📁 Dataset: {PROJECT}.{DATASET}")

# Define the 6 remaining cards
REMAINING_CARDS = [
    {
        "name": "MRR Growth Over Time",
        "description": "Cumulative MRR and net MRR changes over time",
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
        "visualization_type": "line",
        "display_settings": {
            "graph.dimensions": ["month"],
            "graph.metrics": ["cumulative_mrr", "net_mrr"]
        },
        "layout": {"row": 3, "col": 0, "size_x": 6, "size_y": 4}
    },
    {
        "name": "Month-over-Month Growth Rate",
        "description": "MoM growth percentage trend",
        "sql": f"""
SELECT
  month,
  ROUND(mom_growth_rate_pct, 2) as growth_rate_pct
FROM `{PROJECT}.{DATASET}.day06_mrr_summary`
ORDER BY month ASC
        """.strip(),
        "visualization_type": "line",
        "display_settings": {
            "graph.dimensions": ["month"],
            "graph.metrics": ["growth_rate_pct"]
        },
        "layout": {"row": 3, "col": 6, "size_x": 6, "size_y": 4}
    },
    {
        "name": "⭐ Cohort Retention Curves",
        "description": "PRIMARY VISUAL - Retention by cohort over 12 months",
        "sql": f"""
SELECT
  cohort_month,
  months_since_signup,
  ROUND(retention_rate_pct, 2) as retention_rate_pct
FROM `{PROJECT}.{DATASET}.day06_retention_curves`
WHERE months_since_signup <= 12
ORDER BY cohort_month ASC, months_since_signup ASC
        """.strip(),
        "visualization_type": "line",
        "display_settings": {
            "graph.dimensions": ["months_since_signup", "cohort_month"],
            "graph.metrics": ["retention_rate_pct"]
        },
        "layout": {"row": 7, "col": 0, "size_x": 8, "size_y": 5}
    },
    {
        "name": "Churn Heatmap by Cohort × Plan",
        "description": "Churn rates by cohort and plan tier",
        "sql": f"""
SELECT
  FORMAT_DATE('%Y-%m', cohort_month) as cohort,
  plan_tier,
  ROUND(churn_rate_pct, 1) as churn_rate_pct
FROM `{PROJECT}.{DATASET}.day06_churn_by_cohort`
ORDER BY cohort_month DESC, plan_tier ASC
        """.strip(),
        "visualization_type": "table",
        "display_settings": {},
        "layout": {"row": 7, "col": 8, "size_x": 4, "size_y": 5}
    },
    {
        "name": "Customer Health Distribution",
        "description": "Breakdown by health status",
        "sql": f"""
SELECT
  health_status,
  COUNT(*) as customer_count
FROM `{PROJECT}.{DATASET}.day06_customer_health`
WHERE customer_status = 'active'
GROUP BY health_status
ORDER BY customer_count DESC
        """.strip(),
        "visualization_type": "pie",
        "display_settings": {
            "graph.dimensions": ["health_status"],
            "graph.metrics": ["customer_count"]
        },
        "layout": {"row": 12, "col": 0, "size_x": 6, "size_y": 4}
    },
    {
        "name": "Top 10 At-Risk Customers",
        "description": "High-value customers at risk of churning",
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
        "visualization_type": "table",
        "display_settings": {},
        "layout": {"row": 12, "col": 6, "size_x": 6, "size_y": 4}
    }
]

print(f"\n📝 Creating {len(REMAINING_CARDS)} new cards...")

created_cards = []

for i, card_config in enumerate(REMAINING_CARDS, 1):
    print(f"\n{i}. Creating '{card_config['name']}'...")

    # Create card payload
    payload = {
        "name": card_config["name"],
        "description": card_config["description"],
        "display": card_config["visualization_type"],
        "visualization_settings": card_config["display_settings"],
        "dataset_query": {
            "type": "native",
            "native": {
                "query": card_config["sql"],
                "template-tags": {}
            },
            "database": BIGQUERY_DATABASE_ID
        }
    }

    # Create the card
    response = session.post(
        f"{METABASE_URL}/api/card",
        json=payload
    )

    if response.status_code == 200:
        card_data = response.json()
        card_id = card_data["id"]
        print(f"   ✅ Card created! ID: {card_id}")

        created_cards.append({
            "id": card_id,
            "layout": card_config["layout"]
        })
    else:
        print(f"   ❌ Failed to create card: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

if not created_cards:
    print("\n❌ No cards were created. Exiting.")
    exit(1)

print(f"\n✅ Created {len(created_cards)} cards successfully!")

# Add cards to dashboard
print(f"\n📐 Adding cards to dashboard...")

for card_info in created_cards:
    card_id = card_info["id"]
    layout = card_info["layout"]

    payload = {
        "cardId": card_id,
        "row": layout["row"],
        "col": layout["col"],
        "sizeX": layout["size_x"],
        "sizeY": layout["size_y"]
    }

    response = session.post(
        f"{METABASE_URL}/api/dashboard/{DASHBOARD_ID}/cards",
        json=payload
    )

    if response.status_code == 200:
        print(f"   ✅ Added card {card_id} to dashboard")
    else:
        print(f"   ❌ Failed to add card {card_id}: {response.status_code}")

print("\n" + "=" * 70)
print("✅ DASHBOARD COMPLETE!")
print("=" * 70)
print(f"\n🔗 View your dashboard: {METABASE_URL}/dashboard/{DASHBOARD_ID}")
print(f"\n📊 Your dashboard now has:")
print("   - 4 KPI Cards (Current MRR, Churn Rate, Active Customers, Healthy %)")
print("   - 2 Growth Charts (MRR Growth, Growth Rate)")
print("   - 2 Retention Charts (⭐ Cohort Retention Curves, Churn Heatmap)")
print("   - 2 Health Charts (Health Distribution, Top At-Risk Customers)")
print(f"\n💡 Next steps:")
print("   1. Refresh the dashboard in your browser")
print("   2. Adjust visual styling (colors, fonts)")
print("   3. Take screenshots")
print("   4. Export dashboard JSON")
print("\n" + "=" * 70)
