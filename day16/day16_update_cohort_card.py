"""
Update Cohort Retention Curves card to show Best vs. Worst performers only
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
BIGQUERY_DATABASE_ID = 3
DATASET = "day16_saas_metrics"
PROJECT = "advent2025-day16"
CARD_ID = 139  # Cohort Retention Curves card

# Setup session
session = requests.Session()
session.headers.update({"X-Api-Key": METABASE_API_KEY})

print("=" * 70)
print("UPDATING COHORT RETENTION CURVES CARD")
print("=" * 70)
print(f"\nCard ID: {CARD_ID}")

# New SQL query - Best vs. Worst performers only
NEW_SQL = f"""
-- Best vs. Worst Cohort Retention Comparison
-- Shows only 6 cohorts: 3 best + 3 worst performers (by 12-month retention)

SELECT
  cohort_month,
  months_since_signup,
  ROUND(retention_rate_pct, 2) as retention_rate_pct,
  CASE
    WHEN cohort_month IN ('2023-02', '2023-04', '2023-01') THEN '🏆 Best Performers'
    WHEN cohort_month IN ('2023-05', '2023-03', '2023-06') THEN '📉 Worst Performers'
  END as performance_group
FROM `{PROJECT}.{DATASET}.day06_retention_curves`
WHERE
  months_since_signup <= 12
  AND cohort_month IN (
    '2023-02',  -- Best: 60.2% at 12 months
    '2023-04',  -- Best: 52.7% at 12 months
    '2023-01',  -- Best: 52.3% at 12 months
    '2023-05',  -- Worst: 48.7% at 12 months
    '2023-03',  -- Worst: 48.4% at 12 months
    '2023-06'   -- Worst: 48.4% at 12 months
  )
ORDER BY performance_group ASC, cohort_month ASC, months_since_signup ASC
""".strip()

print(f"\n📝 New Query:")
print(f"{NEW_SQL[:200]}...")

# Update card
update_payload = {
    "name": "⭐ Cohort Retention: Best vs. Worst Performers",
    "description": "Compare top 3 and bottom 3 cohorts by 12-month retention rate. Shows what patterns work vs. what doesn't.",
    "dataset_query": {
        "type": "native",
        "native": {
            "query": NEW_SQL,
            "template-tags": {}
        },
        "database": BIGQUERY_DATABASE_ID
    },
    "display": "line",
    "visualization_settings": {
        "graph.dimensions": ["months_since_signup", "cohort_month"],
        "graph.metrics": ["retention_rate_pct"],
        "graph.colors": {
            "2023-02": "#2ecc71",  # Best - Green
            "2023-04": "#27ae60",  # Best - Dark Green
            "2023-01": "#1abc9c",  # Best - Teal
            "2023-05": "#e74c3c",  # Worst - Red
            "2023-03": "#c0392b",  # Worst - Dark Red
            "2023-06": "#e67e22"   # Worst - Orange
        },
        "graph.show_values": False,
        "graph.y_axis.title_text": "Retention Rate (%)",
        "graph.x_axis.title_text": "Months Since Signup",
        "graph.y_axis.scale": "linear",
        "series_settings": {
            "retention_rate_pct": {
                "line.interpolate": "cardinal",
                "line.marker_enabled": True
            }
        }
    }
}

response = session.put(
    f"{METABASE_URL}/api/card/{CARD_ID}",
    json=update_payload
)

if response.status_code == 200:
    print("\n✅ Card updated successfully!")
    print(f"\n🔗 View card: {METABASE_URL}/question/{CARD_ID}")
    print(f"\n📊 Now shows:")
    print("   🏆 BEST PERFORMERS (Green):")
    print("      - Feb 2023: 60.2% retention")
    print("      - Apr 2023: 52.7% retention")
    print("      - Jan 2023: 52.3% retention")
    print("\n   📉 WORST PERFORMERS (Red):")
    print("      - May 2023: 48.7% retention")
    print("      - Mar 2023: 48.4% retention")
    print("      - Jun 2023: 48.4% retention")
    print("\n💡 INSIGHT: Only 6 lines instead of 23 = much clearer visualization!")
    print("   Compare the patterns between best and worst to identify success factors.")
else:
    print(f"\n❌ Update failed: {response.status_code}")
    print(f"Response: {response.text}")

print("\n" + "=" * 70)
