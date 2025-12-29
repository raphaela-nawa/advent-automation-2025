"""
Day 21: AI Insights Layer - Data Fetching Script
Fetches validated metrics from BigQuery for AI analysis
Reuses Day 16 BigQuery connection and tables
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).parent.parent
env_path = root_dir / "config" / ".env"
load_dotenv(env_path)

# Load configuration
config_path = Path(__file__).parent / "config" / "day21_CONFIG_insight_settings.yaml"
with open(config_path, 'r') as f:
    day21_CONFIG = yaml.safe_load(f)

# BigQuery setup (reuse Day 16 credentials)
day21_PROJECT_ID = day21_CONFIG['bigquery']['project_id']
day21_DATASET_ID = day21_CONFIG['bigquery']['dataset_id']

# Initialize BigQuery client
credentials_path = os.getenv("DAY16_BIGQUERY_CREDENTIALS_PATH")
if not credentials_path:
    raise ValueError("DAY16_BIGQUERY_CREDENTIALS_PATH not found in .env")

credentials = service_account.Credentials.from_service_account_file(credentials_path)
day21_bq_client = bigquery.Client(credentials=credentials, project=day21_PROJECT_ID)


def day21_fetch_kpis():
    """Fetch current KPI snapshot"""
    table = day21_CONFIG['metrics_sources']['kpis']['table']
    columns = day21_CONFIG['metrics_sources']['kpis']['columns']

    query = f"""
    SELECT {', '.join(columns)}
    FROM `{day21_PROJECT_ID}.{day21_DATASET_ID}.{table}`
    LIMIT 1
    """

    result = day21_bq_client.query(query).to_dataframe()
    return result.to_dict('records')[0] if not result.empty else {}


def day21_fetch_mrr_growth():
    """Fetch MRR growth trends (last 12 months)"""
    config = day21_CONFIG['metrics_sources']['mrr_growth']
    table = config['table']
    columns = config['columns']
    order_by = config['order_by']
    limit = config['limit']

    query = f"""
    SELECT {', '.join(columns)}
    FROM `{day21_PROJECT_ID}.{day21_DATASET_ID}.{table}`
    ORDER BY {order_by}
    LIMIT {limit}
    """

    result = day21_bq_client.query(query).to_dataframe()
    return result.to_dict('records')


def day21_fetch_retention():
    """Fetch cohort retention data (best vs worst performers at 12 months)"""
    config = day21_CONFIG['metrics_sources']['retention']
    table = config['table']
    columns = config['columns']
    filters = config['filters']

    where_clause = " AND ".join(filters)

    query = f"""
    SELECT {', '.join(columns)}
    FROM `{day21_PROJECT_ID}.{day21_DATASET_ID}.{table}`
    WHERE {where_clause}
    ORDER BY cohort_month ASC
    """

    result = day21_bq_client.query(query).to_dataframe()
    return result.to_dict('records')


def day21_fetch_at_risk_customers():
    """Fetch top 10 at-risk customers by LTV"""
    config = day21_CONFIG['metrics_sources']['customer_health']
    table = config['table']
    columns = config['columns']
    filters = config['filters']
    order_by = config['order_by']
    limit = config['limit']

    where_clause = " AND ".join(filters)

    query = f"""
    SELECT {', '.join(columns)}
    FROM `{day21_PROJECT_ID}.{day21_DATASET_ID}.{table}`
    WHERE {where_clause}
    ORDER BY {order_by}
    LIMIT {limit}
    """

    result = day21_bq_client.query(query).to_dataframe()
    return result.to_dict('records')


def day21_check_alerts(metrics_data):
    """Check if any automated alerts should be triggered"""
    alerts = day21_CONFIG['alerts']
    triggered_alerts = []

    # Check MRR growth
    mrr_growth = metrics_data['mrr_growth']
    negative_months = sum(1 for m in mrr_growth[:alerts['mrr_growth_negative_months']]
                         if m['mom_growth_rate_pct'] < 0)
    if negative_months >= alerts['mrr_growth_negative_months']:
        triggered_alerts.append({
            "type": "mrr_decline",
            "severity": "high",
            "message": f"MRR has declined for {negative_months} consecutive months"
        })

    # Check churn rate
    kpis = metrics_data['kpis']
    if kpis['churn_rate_pct'] > alerts['churn_rate_threshold_pct']:
        triggered_alerts.append({
            "type": "high_churn",
            "severity": "high",
            "message": f"Churn rate ({kpis['churn_rate_pct']:.1f}%) exceeds threshold ({alerts['churn_rate_threshold_pct']:.1f}%)"
        })

    # Check at-risk LTV
    at_risk_customers = metrics_data['at_risk_customers']
    total_at_risk_ltv = sum(c['ltv_estimate'] for c in at_risk_customers)
    if total_at_risk_ltv > alerts['at_risk_ltv_total']:
        triggered_alerts.append({
            "type": "high_risk_ltv",
            "severity": "medium",
            "message": f"Total at-risk LTV (${total_at_risk_ltv:,.2f}) exceeds threshold (${alerts['at_risk_ltv_total']:,.2f})"
        })

    # Check retention gap
    retention = metrics_data['retention']
    retention_rates = [r['retention_rate_pct'] for r in retention]
    if retention_rates:
        gap = max(retention_rates) - min(retention_rates)
        if gap > alerts['retention_gap_threshold_pct']:
            triggered_alerts.append({
                "type": "retention_gap",
                "severity": "medium",
                "message": f"Best-worst cohort retention gap ({gap:.1f}%) indicates inconsistent customer experience"
            })

    return triggered_alerts


def day21_fetch_all_metrics():
    """Main function to fetch all metrics and save to JSON"""
    print("=" * 70)
    print("DAY 21: FETCHING METRICS FOR AI ANALYSIS")
    print("=" * 70)

    # Fetch all data sources
    print("\n📊 Fetching KPIs...")
    kpis = day21_fetch_kpis()
    print(f"   ✅ Current MRR: ${kpis.get('current_mrr', 0):,.2f}")
    print(f"   ✅ Churn Rate: {kpis.get('churn_rate_pct', 0):.2f}%")

    print("\n📈 Fetching MRR growth trends...")
    mrr_growth = day21_fetch_mrr_growth()
    print(f"   ✅ Retrieved {len(mrr_growth)} months of data")

    print("\n🔄 Fetching cohort retention data...")
    retention = day21_fetch_retention()
    print(f"   ✅ Retrieved {len(retention)} cohort data points")

    print("\n⚠️  Fetching at-risk customers...")
    at_risk_customers = day21_fetch_at_risk_customers()
    total_at_risk_ltv = sum(c['ltv_estimate'] for c in at_risk_customers)
    print(f"   ✅ Retrieved {len(at_risk_customers)} at-risk customers")
    print(f"   💰 Total at-risk LTV: ${total_at_risk_ltv:,.2f}")

    # Combine all metrics
    metrics_data = {
        "kpis": kpis,
        "mrr_growth": mrr_growth,
        "retention": retention,
        "at_risk_customers": at_risk_customers,
        "metadata": {
            "fetched_at": datetime.now().isoformat(),
            "project_id": day21_PROJECT_ID,
            "dataset_id": day21_DATASET_ID
        }
    }

    # Check for alerts
    print("\n🚨 Checking automated alerts...")
    alerts = day21_check_alerts(metrics_data)
    metrics_data["alerts"] = alerts

    if alerts:
        print(f"   ⚠️  {len(alerts)} alert(s) triggered:")
        for alert in alerts:
            print(f"      [{alert['severity'].upper()}] {alert['type']}: {alert['message']}")
    else:
        print("   ✅ No alerts triggered")

    # Save to JSON file
    output_dir = Path(__file__).parent / "insights"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(day21_CONFIG['output']['timestamp_format'])
    output_file = output_dir / f"day21_METRICS_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(metrics_data, f, indent=2, default=str)

    print(f"\n💾 Metrics saved to: {output_file}")
    print("\n" + "=" * 70)

    return metrics_data, output_file


if __name__ == "__main__":
    day21_fetch_all_metrics()
