"""
Day 16: Metabase Dashboard Auto-Setup via API
Automatically creates all 6 dashboard cards so you only need to adjust visual layout

SETUP:
1. Copy .env.example to .env
2. Edit .env with your Metabase credentials
3. Run: python3 day16_METABASE_auto_setup.py
"""

import requests
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION - Loaded from .env file
# ============================================================================

METABASE_URL = os.getenv("DAY16_METABASE_URL")
METABASE_EMAIL = os.getenv("DAY16_METABASE_EMAIL")
METABASE_PASSWORD = os.getenv("DAY16_METABASE_PASSWORD")
BIGQUERY_DATABASE_NAME = os.getenv("DAY16_METABASE_DATABASE_NAME", "Day 16 - SaaS Health Metrics")

# Validate required environment variables
REQUIRED_ENV_VARS = {
    "DAY16_METABASE_URL": METABASE_URL,
    "DAY16_METABASE_EMAIL": METABASE_EMAIL,
    "DAY16_METABASE_PASSWORD": METABASE_PASSWORD
}

missing_vars = [var for var, value in REQUIRED_ENV_VARS.items() if not value]
if missing_vars:
    print("❌ ERROR: Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n💡 Fix:")
    print("   1. Copy .env.example to .env")
    print("   2. Edit .env with your Metabase credentials")
    print("   3. Run this script again")
    exit(1)

# ============================================================================
# CARD DEFINITIONS - All 6 dashboard cards
# ============================================================================

DASHBOARD_CARDS = [
    # SECTION 1: Business Health Baseline (4 Cards)
    {
        "name": "Current MRR",
        "description": "Executive KPI - Current Monthly Recurring Revenue",
        "sql": """
SELECT
  ROUND(current_mrr, 2) as current_mrr
FROM `advent2025-day16.day16_saas_metrics.day06_dashboard_kpis`
        """.strip(),
        "visualization_type": "scalar",  # Single number
        "display_settings": {
            "number.style": "currency",
            "number.currency": "USD"
        }
    },
    {
        "name": "Churn Rate (%)",
        "description": "Executive KPI - Current churn percentage",
        "sql": """
SELECT
  ROUND(overall_churn_rate_pct, 2) as churn_rate_pct
FROM `advent2025-day16.day16_saas_metrics.day06_dashboard_kpis`
        """.strip(),
        "visualization_type": "scalar",
        "display_settings": {
            "number.style": "percent",
            "number.scale": 1  # Already in percentage
        }
    },
    {
        "name": "Active Customers",
        "description": "Executive KPI - Total active customer count",
        "sql": """
SELECT
  active_customers
FROM `advent2025-day16.day16_saas_metrics.day06_dashboard_kpis`
        """.strip(),
        "visualization_type": "scalar",
        "display_settings": {
            "number.style": "decimal"
        }
    },
    {
        "name": "Healthy Customers %",
        "description": "Executive KPI - Percentage of healthy customers",
        "sql": """
SELECT
  ROUND((healthy_customers * 100.0 / (healthy_customers + at_risk_customers + critical_customers)), 1) as healthy_pct
FROM `advent2025-day16.day16_saas_metrics.day06_dashboard_kpis`
        """.strip(),
        "visualization_type": "scalar",
        "display_settings": {
            "number.style": "percent",
            "number.scale": 1
        }
    },

    # SECTION 2: Growth Trajectory (2 Cards)
    {
        "name": "MRR Growth Over Time",
        "description": "Shows MRR composition - new, expansion, contraction, churn",
        "sql": """
SELECT
  month,
  ROUND(new_mrr, 2) as new_mrr,
  ROUND(expansion_mrr, 2) as expansion_mrr,
  ROUND(contraction_mrr, 2) as contraction_mrr,
  ROUND(churned_mrr, 2) as churned_mrr,
  ROUND(net_mrr, 2) as net_mrr
FROM `advent2025-day16.day16_saas_metrics.day06_mrr_summary`
ORDER BY month ASC
        """.strip(),
        "visualization_type": "area",  # Area chart
        "display_settings": {
            "graph.dimensions": ["month"],
            "graph.metrics": ["new_mrr", "expansion_mrr", "contraction_mrr", "churned_mrr"]
        }
    },
    {
        "name": "Month-over-Month Growth Rate",
        "description": "Shows growth velocity trend",
        "sql": """
SELECT
  month,
  ROUND(growth_rate * 100, 2) as growth_rate_pct
FROM `advent2025-day16.day16_saas_metrics.day06_mrr_summary`
ORDER BY month ASC
        """.strip(),
        "visualization_type": "line",
        "display_settings": {
            "graph.dimensions": ["month"],
            "graph.metrics": ["growth_rate_pct"]
        }
    },

    # SECTION 3: Cohort Patterns (2 Cards) - PRIMARY VISUAL
    {
        "name": "Cohort Retention Curves (PRIMARY)",
        "description": "PRIMARY DECISION VISUAL - Shows which cohorts have declining retention",
        "sql": """
SELECT
  cohort_month,
  months_since_signup,
  ROUND(retention_rate_pct, 2) as retention_rate_pct
FROM `advent2025-day16.day16_saas_metrics.day06_retention_curves`
WHERE months_since_signup <= 12
ORDER BY cohort_month ASC, months_since_signup ASC
        """.strip(),
        "visualization_type": "line",
        "display_settings": {
            "graph.dimensions": ["months_since_signup"],
            "graph.metrics": ["retention_rate_pct"],
            "graph.series_settings": {
                "cohort_month": {"color": "#509EE3"}
            }
        }
    },
    {
        "name": "Churn Heatmap: Cohort × Plan Tier",
        "description": "Identify which plan tiers + cohorts have highest churn risk",
        "sql": """
SELECT
  cohort_month,
  plan_tier,
  ROUND(churn_rate * 100, 2) as churn_rate_pct,
  churned_customers,
  cohort_size
FROM `advent2025-day16.day16_saas_metrics.day06_churn_by_cohort`
WHERE cohort_size > 5
ORDER BY cohort_month ASC, plan_tier ASC
        """.strip(),
        "visualization_type": "table",  # Metabase doesn't have native pivot, use table
        "display_settings": {}
    },

    # SECTION 4: Customer Health Alerts (2 Cards)
    {
        "name": "At-Risk Customer Distribution",
        "description": "Show proportion of customers by health status",
        "sql": """
SELECT
  health_status,
  COUNT(*) as customer_count
FROM `advent2025-day16.day16_saas_metrics.day06_customer_health`
GROUP BY health_status
ORDER BY customer_count DESC
        """.strip(),
        "visualization_type": "pie",
        "display_settings": {
            "graph.dimensions": ["health_status"],
            "graph.metrics": ["customer_count"]
        }
    },
    {
        "name": "Top 10 Critical Customers",
        "description": "Actionable list - who to call TODAY",
        "sql": """
SELECT
  customer_id,
  ROUND(ltv, 2) as lifetime_value,
  ROUND(health_score, 2) as health_score,
  health_status,
  days_since_last_activity,
  risk_reason
FROM `advent2025-day16.day16_saas_metrics.day06_customer_health`
WHERE health_status = 'Critical'
ORDER BY ltv DESC
LIMIT 10
        """.strip(),
        "visualization_type": "table",
        "display_settings": {}
    }
]

# ============================================================================
# METABASE API CLIENT
# ============================================================================

class MetabaseClient:
    def __init__(self, url: str, email: str, password: str):
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.session_token = None
        self.database_id = None

        # Login
        self._login(email, password)

    def _login(self, email: str, password: str):
        """Authenticate with Metabase"""
        print("🔐 Logging into Metabase...")

        response = self.session.post(
            f"{self.url}/api/session",
            json={"username": email, "password": password}
        )

        if response.status_code == 200:
            self.session_token = response.json()["id"]
            self.session.headers.update({"X-Metabase-Session": self.session_token})
            print("✅ Login successful!")
        else:
            raise Exception(f"❌ Login failed: {response.status_code} - {response.text}")

    def get_database_id(self, database_name: str) -> Optional[int]:
        """Find database ID by name"""
        print(f"🔍 Finding database '{database_name}'...")

        response = self.session.get(f"{self.url}/api/database")

        if response.status_code == 200:
            databases = response.json()["data"]
            for db in databases:
                if db["name"] == database_name:
                    self.database_id = db["id"]
                    print(f"✅ Found database ID: {self.database_id}")
                    return self.database_id

            print(f"❌ Database '{database_name}' not found")
            print("Available databases:")
            for db in databases:
                print(f"  - {db['name']}")
            return None
        else:
            raise Exception(f"❌ Failed to fetch databases: {response.status_code}")

    def create_card(self, card_config: Dict) -> Optional[int]:
        """Create a Metabase card (question)"""
        print(f"\n📊 Creating card: {card_config['name']}...")

        if not self.database_id:
            raise Exception("❌ Database ID not set. Call get_database_id() first.")

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
                "database": self.database_id
            }
        }

        response = self.session.post(
            f"{self.url}/api/card",
            json=payload
        )

        if response.status_code == 200:
            card_id = response.json()["id"]
            print(f"✅ Card created! ID: {card_id}")
            return card_id
        else:
            print(f"❌ Failed to create card: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def create_dashboard(self, name: str, description: str) -> Optional[int]:
        """Create a Metabase dashboard"""
        print(f"\n📋 Creating dashboard: {name}...")

        payload = {
            "name": name,
            "description": description
        }

        response = self.session.post(
            f"{self.url}/api/dashboard",
            json=payload
        )

        if response.status_code == 200:
            dashboard_id = response.json()["id"]
            print(f"✅ Dashboard created! ID: {dashboard_id}")
            return dashboard_id
        else:
            print(f"❌ Failed to create dashboard: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def add_card_to_dashboard(self, dashboard_id: int, card_id: int, row: int = 0, col: int = 0, size_x: int = 6, size_y: int = 4):
        """Add a card to a dashboard"""
        print(f"➕ Adding card {card_id} to dashboard {dashboard_id}...")

        payload = {
            "cardId": card_id,
            "row": row,
            "col": col,
            "sizeX": size_x,
            "sizeY": size_y
        }

        response = self.session.post(
            f"{self.url}/api/dashboard/{dashboard_id}/cards",
            json=payload
        )

        if response.status_code == 200:
            print(f"✅ Card added to dashboard!")
            return True
        else:
            print(f"❌ Failed to add card: {response.status_code}")
            return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("Day 16: Metabase Dashboard Auto-Setup")
    print("=" * 70)
    print()

    # Step 1: Connect to Metabase
    try:
        client = MetabaseClient(METABASE_URL, METABASE_EMAIL, METABASE_PASSWORD)
    except Exception as e:
        print(f"\n❌ Error connecting to Metabase: {e}")
        print("\n💡 Make sure you updated METABASE_URL, METABASE_EMAIL, and METABASE_PASSWORD")
        return

    # Step 2: Get database ID
    if not client.get_database_id(BIGQUERY_DATABASE_NAME):
        print("\n❌ Could not find BigQuery database. Exiting.")
        print("💡 Make sure BIGQUERY_DATABASE_NAME matches exactly (case-sensitive)")
        return

    # Step 3: Create dashboard
    dashboard_id = client.create_dashboard(
        name="Murilo's SaaS Health Metrics Dashboard",
        description="Day 16 - Cohort retention analytics for proactive customer intervention"
    )

    if not dashboard_id:
        print("\n❌ Failed to create dashboard. Exiting.")
        return

    # Step 4: Create all cards
    card_ids = []

    for i, card_config in enumerate(DASHBOARD_CARDS):
        card_id = client.create_card(card_config)
        if card_id:
            card_ids.append(card_id)
        else:
            print(f"⚠️  Skipping card {i+1} due to error")

    print(f"\n✅ Created {len(card_ids)}/{len(DASHBOARD_CARDS)} cards successfully!")

    # Step 5: Add cards to dashboard
    print("\n📐 Adding cards to dashboard layout...")

    # Layout: 4 KPIs in row 1, then 2x2 grid for remaining cards
    layouts = [
        # Row 1: 4 KPI metrics (each takes 3 cols)
        {"row": 0, "col": 0, "size_x": 3, "size_y": 3},   # Current MRR
        {"row": 0, "col": 3, "size_x": 3, "size_y": 3},   # Churn Rate
        {"row": 0, "col": 6, "size_x": 3, "size_y": 3},   # Active Customers
        {"row": 0, "col": 9, "size_x": 3, "size_y": 3},   # Healthy %

        # Row 2: MRR charts (full width)
        {"row": 3, "col": 0, "size_x": 12, "size_y": 5},  # MRR Growth
        {"row": 8, "col": 0, "size_x": 12, "size_y": 4},  # MoM Growth

        # Row 3: Cohort analysis (PRIMARY)
        {"row": 12, "col": 0, "size_x": 12, "size_y": 6}, # Retention Curves (PRIMARY)
        {"row": 18, "col": 0, "size_x": 12, "size_y": 5}, # Churn Heatmap

        # Row 4: Customer health
        {"row": 23, "col": 0, "size_x": 6, "size_y": 5},  # Pie chart
        {"row": 23, "col": 6, "size_x": 6, "size_y": 5},  # Critical customers table
    ]

    for card_id, layout in zip(card_ids, layouts):
        client.add_card_to_dashboard(
            dashboard_id=dashboard_id,
            card_id=card_id,
            **layout
        )

    # Done!
    print("\n" + "=" * 70)
    print("✅ DASHBOARD SETUP COMPLETE!")
    print("=" * 70)
    print(f"\n🔗 Dashboard URL: {METABASE_URL}/dashboard/{dashboard_id}")
    print("\n📝 Next steps:")
    print("1. Open the dashboard link above")
    print("2. Adjust visual styling (colors, fonts) as needed")
    print("3. Take screenshots for documentation")
    print("4. Export dashboard JSON (Settings → Export)")
    print("\n🎉 You're done! 80% of the work is automated.")
    print()

if __name__ == "__main__":
    main()
