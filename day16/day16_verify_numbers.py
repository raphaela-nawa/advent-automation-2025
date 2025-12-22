"""
Day 16: Quick Data Verification Script
Run this to see all dashboard numbers before creating Metabase dashboard
"""

import pandas as pd
from pathlib import Path

# Load all data files
data_dir = Path('data')

print("=" * 70)
print("DAY 16: SAAS HEALTH METRICS - DATA VERIFICATION")
print("=" * 70)

# Load CSVs
df_kpis = pd.read_csv(data_dir / 'day06_dashboard_kpis.csv')
df_mrr_summary = pd.read_csv(data_dir / 'day06_mrr_summary.csv')
df_retention = pd.read_csv(data_dir / 'day06_retention_curves.csv')
df_churn_cohort = pd.read_csv(data_dir / 'day06_churn_by_cohort.csv')
df_customer_health = pd.read_csv(data_dir / 'day06_customer_health.csv')

print("\n✅ All data loaded successfully!")
print(f"\n📊 Dataset sizes:")
print(f"  - KPIs: {len(df_kpis)} rows")
print(f"  - MRR Summary: {len(df_mrr_summary)} rows")
print(f"  - Retention Curves: {len(df_retention)} rows")
print(f"  - Churn by Cohort: {len(df_churn_cohort)} rows")
print(f"  - Customer Health: {len(df_customer_health)} rows")

print("\n" + "=" * 70)
print("SECTION 1: BUSINESS HEALTH BASELINE (4 KPIs)")
print("=" * 70)

# Card 1.1: Current MRR
current_mrr = df_kpis['current_mrr'].iloc[0]
print(f"\n💰 Card 1.1 - Current MRR: ${current_mrr:,.2f}")

# Card 1.2: Churn Rate
churn_rate = df_kpis['overall_churn_rate_pct'].iloc[0]
print(f"📉 Card 1.2 - Churn Rate: {churn_rate:.2f}%")

# Card 1.3: Active Customers
active_customers = df_kpis['active_customers'].iloc[0]
print(f"👥 Card 1.3 - Active Customers: {active_customers:,}")

# Card 1.4: Healthy Customers %
healthy = df_kpis['healthy_customers'].iloc[0]
at_risk = df_kpis['at_risk_customers'].iloc[0]
critical = df_kpis['critical_customers'].iloc[0]
total = healthy + at_risk + critical
healthy_pct = (healthy / total) * 100

print(f"✅ Card 1.4 - Healthy Customers: {healthy_pct:.1f}%")
print(f"   - Healthy: {healthy}")
print(f"   - At Risk: {at_risk}")
print(f"   - Critical: {critical}")

print("\n" + "=" * 70)
print("SECTION 2: GROWTH TRAJECTORY (2 CARDS)")
print("=" * 70)

# Card 2.1: MRR Growth Over Time
df_mrr_summary['month'] = pd.to_datetime(df_mrr_summary['month'])
df_mrr_summary = df_mrr_summary.sort_values('month')

print(f"\n📈 Card 2.1 - MRR Growth Over Time")
print(f"   Columns available: {list(df_mrr_summary.columns)}")
print(f"\n   Last 5 months:")
print(df_mrr_summary[['month', 'net_mrr', 'new_mrr', 'expansion_mrr',
                       'contraction_mrr', 'churn_mrr']].tail().to_string(index=False))

# Card 2.2: MoM Growth Rate
print(f"\n📊 Card 2.2 - Month-over-Month Growth Rate")
print(f"   Latest growth rate: {df_mrr_summary['mom_growth_rate_pct'].iloc[-1]:.2f}%")
print(f"\n   Last 5 months:")
print(df_mrr_summary[['month', 'mom_growth_rate_pct', 'cumulative_mrr']].tail().to_string(index=False))

print("\n" + "=" * 70)
print("SECTION 3: COHORT RETENTION ANALYSIS (2 CARDS)")
print("=" * 70)

# Card 3.1: Cohort Retention Curves (PRIMARY VISUAL)
df_retention['cohort_month'] = pd.to_datetime(df_retention['cohort_month'])
df_retention_12m = df_retention[df_retention['months_since_signup'] <= 12].copy()

cohorts = sorted(df_retention_12m['cohort_month'].unique())
print(f"\n⭐ Card 3.1 - Cohort Retention Curves (PRIMARY DECISION VISUAL)")
print(f"   Total cohorts: {len(cohorts)}")
print(f"   Data points: {len(df_retention_12m)} (12 months × {len(cohorts)} cohorts)")

# Show first 3 cohorts
print(f"\n   First 3 cohorts (month 0, 6, 12):")
for cohort in cohorts[:3]:
    cohort_data = df_retention_12m[df_retention_12m['cohort_month'] == cohort]
    month_0 = cohort_data[cohort_data['months_since_signup'] == 0]['retention_rate_pct'].iloc[0]
    month_6 = cohort_data[cohort_data['months_since_signup'] == 6]['retention_rate_pct'].iloc[0] if len(cohort_data[cohort_data['months_since_signup'] == 6]) > 0 else 0
    month_12 = cohort_data[cohort_data['months_since_signup'] == 12]['retention_rate_pct'].iloc[0] if len(cohort_data[cohort_data['months_since_signup'] == 12]) > 0 else 0
    print(f"   {cohort.strftime('%Y-%m')}: M0={month_0:.1f}%, M6={month_6:.1f}%, M12={month_12:.1f}%")

# Card 3.2: Churn Heatmap
df_churn_cohort['cohort_month'] = pd.to_datetime(df_churn_cohort['cohort_month'])
print(f"\n🔥 Card 3.2 - Churn Heatmap by Cohort × Plan Tier")
print(f"   Total cells: {len(df_churn_cohort)}")
print(f"\n   Sample data (first 10 rows):")
print(df_churn_cohort[['cohort_month', 'plan_tier', 'churn_rate_pct']].head(10).to_string(index=False))

print("\n" + "=" * 70)
print("SECTION 4: CUSTOMER HEALTH ALERTS (2 CARDS)")
print("=" * 70)

# Card 4.1: At-Risk Customer Distribution
health_distribution = df_customer_health['health_status'].value_counts()
print(f"\n🚨 Card 4.1 - At-Risk Customer Distribution")
for status, count in health_distribution.items():
    pct = (count / health_distribution.sum()) * 100
    print(f"   {status}: {count} customers ({pct:.1f}%)")

# Card 4.2: Top 10 At-Risk Customers
at_risk_customers = df_customer_health[
    df_customer_health['health_status'] == 'At Risk'
].nlargest(10, 'ltv_estimate')[['customer_id', 'ltv_estimate', 'mrr_current', 'health_status', 'plan_tier']]

print(f"\n🆘 Card 4.2 - Top 10 At-Risk Customers (by LTV)")
if len(at_risk_customers) > 0:
    print(f"   Total LTV at risk: ${at_risk_customers['ltv_estimate'].sum():,.2f}")
    print(f"\n   Top {min(5, len(at_risk_customers))}:")
    for idx, row in at_risk_customers.head(5).iterrows():
        print(f"   {row['customer_id']}: ${row['ltv_estimate']:,.0f} (MRR: ${row['mrr_current']:.2f}) - {row['plan_tier']}")
else:
    print(f"   No at-risk customers found!")

# Also show churned customers
churned_customers = df_customer_health[
    df_customer_health['health_status'] == 'Churned'
].nlargest(10, 'ltv_estimate')[['customer_id', 'ltv_estimate', 'plan_tier']]

print(f"\n💔 Bonus - Top 10 Churned Customers (by LTV)")
if len(churned_customers) > 0:
    print(f"   Total LTV lost: ${churned_customers['ltv_estimate'].sum():,.2f}")
    print(f"\n   Top 5:")
    for idx, row in churned_customers.head(5).iterrows():
        print(f"   {row['customer_id']}: ${row['ltv_estimate']:,.0f} - {row['plan_tier']}")

print("\n" + "=" * 70)
print("SUMMARY FOR BIGQUERY VERIFICATION")
print("=" * 70)

print(f"\n✅ SECTION 1 - Business Health Baseline:")
print(f"   Current MRR: ${current_mrr:,.2f}")
print(f"   Churn Rate: {churn_rate:.2f}%")
print(f"   Active Customers: {active_customers:,}")
print(f"   Healthy Customers: {healthy_pct:.1f}%")

print(f"\n✅ SECTION 2 - Growth Trajectory:")
print(f"   Latest Net MRR: ${df_mrr_summary['net_mrr'].iloc[-1]:,.2f}")
print(f"   Latest Growth Rate: {df_mrr_summary['mom_growth_rate_pct'].iloc[-1]:.2f}%")
print(f"   Cumulative MRR: ${df_mrr_summary['cumulative_mrr'].iloc[-1]:,.2f}")

print(f"\n✅ SECTION 3 - Cohort Retention:")
print(f"   Total cohorts: {len(cohorts)}")
print(f"   Retention data points: {len(df_retention_12m)}")
print(f"   Churn heatmap cells: {len(df_churn_cohort)}")

print(f"\n✅ SECTION 4 - Customer Health:")
print(f"   Healthy: {health_distribution.get('Healthy', 0)}")
print(f"   At Risk: {health_distribution.get('At Risk', 0)}")
print(f"   Churned: {health_distribution.get('Churned', 0)}")
if len(at_risk_customers) > 0:
    print(f"   Total LTV at risk (top 10): ${at_risk_customers['ltv_estimate'].sum():,.2f}")

print("\n" + "=" * 70)
print("✅ If these numbers look correct, you're ready to create the Metabase dashboard!")
print("\n📝 Next steps:")
print("   1. Connect BigQuery to Metabase")
print("   2. Run: python3 day16_METABASE_auto_setup.py")
print("=" * 70)
