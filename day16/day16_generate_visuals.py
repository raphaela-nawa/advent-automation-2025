"""
Day 16: Generate Dashboard Visuals in Python
Compare these with your Metabase dashboard to verify accuracy
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load data
data_dir = Path('data')
df_kpis = pd.read_csv(data_dir / 'day06_dashboard_kpis.csv')
df_mrr_summary = pd.read_csv(data_dir / 'day06_mrr_summary.csv')
df_retention = pd.read_csv(data_dir / 'day06_retention_curves.csv')
df_churn_cohort = pd.read_csv(data_dir / 'day06_churn_by_cohort.csv')
df_customer_health = pd.read_csv(data_dir / 'day06_customer_health.csv')

print("✅ Data loaded successfully!\n")

# Parse dates
df_mrr_summary['month'] = pd.to_datetime(df_mrr_summary['month'])
df_retention['cohort_month'] = pd.to_datetime(df_retention['cohort_month'])
df_churn_cohort['cohort_month'] = pd.to_datetime(df_churn_cohort['cohort_month'])

# ============================================================================
# SECTION 1: BUSINESS HEALTH BASELINE (4 KPIs)
# ============================================================================

print("=" * 70)
print("SECTION 1: BUSINESS HEALTH BASELINE (4 KPIs)")
print("=" * 70)

current_mrr = df_kpis['current_mrr'].iloc[0]
churn_rate = df_kpis['overall_churn_rate_pct'].iloc[0]
active_customers = df_kpis['active_customers'].iloc[0]

healthy = df_kpis['healthy_customers'].iloc[0]
at_risk = df_kpis['at_risk_customers'].iloc[0]
critical = df_kpis['critical_customers'].iloc[0]
total = healthy + at_risk + critical
healthy_pct = (healthy / total) * 100

print(f"\n💰 Current MRR: ${current_mrr:,.2f}")
print(f"📉 Churn Rate: {churn_rate:.2f}%")
print(f"👥 Active Customers: {active_customers:,}")
print(f"✅ Healthy Customers: {healthy_pct:.1f}%")

# Visualize KPIs
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle('Section 1: Business Health Baseline (4 KPIs)', fontsize=16, fontweight='bold', y=1.02)

# KPI 1: Current MRR
axes[0, 0].text(0.5, 0.5, f'${current_mrr:,.0f}',
                ha='center', va='center', fontsize=42, fontweight='bold', color='#2ecc71')
axes[0, 0].text(0.5, 0.15, 'Current MRR', ha='center', va='center', fontsize=16, color='#555')
axes[0, 0].set_xlim(0, 1)
axes[0, 0].set_ylim(0, 1)
axes[0, 0].axis('off')

# KPI 2: Churn Rate
axes[0, 1].text(0.5, 0.5, f'{churn_rate:.1f}%',
                ha='center', va='center', fontsize=42, fontweight='bold', color='#e74c3c')
axes[0, 1].text(0.5, 0.15, 'Churn Rate', ha='center', va='center', fontsize=16, color='#555')
axes[0, 1].set_xlim(0, 1)
axes[0, 1].set_ylim(0, 1)
axes[0, 1].axis('off')

# KPI 3: Active Customers
axes[1, 0].text(0.5, 0.5, f'{active_customers:,}',
                ha='center', va='center', fontsize=42, fontweight='bold', color='#3498db')
axes[1, 0].text(0.5, 0.15, 'Active Customers', ha='center', va='center', fontsize=16, color='#555')
axes[1, 0].set_xlim(0, 1)
axes[1, 0].set_ylim(0, 1)
axes[1, 0].axis('off')

# KPI 4: Healthy %
axes[1, 1].text(0.5, 0.5, f'{healthy_pct:.1f}%',
                ha='center', va='center', fontsize=42, fontweight='bold', color='#2ecc71')
axes[1, 1].text(0.5, 0.15, 'Healthy Customers', ha='center', va='center', fontsize=16, color='#555')
axes[1, 1].set_xlim(0, 1)
axes[1, 1].set_ylim(0, 1)
axes[1, 1].axis('off')

plt.tight_layout()
plt.savefig('day16_section1_kpis.png', dpi=150, bbox_inches='tight')
print("\n✅ Saved: day16_section1_kpis.png")
plt.show()

# ============================================================================
# SECTION 2: GROWTH TRAJECTORY (2 CARDS)
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: GROWTH TRAJECTORY")
print("=" * 70)

df_mrr_summary = df_mrr_summary.sort_values('month')

print(f"\n📈 MRR Growth - Latest Month: ${df_mrr_summary['net_mrr'].iloc[-1]:,.2f}")
print(f"📊 Growth Rate - Latest Month: {df_mrr_summary['mom_growth_rate_pct'].iloc[-1]:.2f}%")

# Card 2.1: MRR Growth Over Time
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(df_mrr_summary['month'], df_mrr_summary['cumulative_mrr'],
        color='#2c3e50', linewidth=3, marker='o', markersize=6, label='Cumulative MRR')

# Add net MRR bars
colors = ['green' if x >= 0 else 'red' for x in df_mrr_summary['net_mrr']]
ax.bar(df_mrr_summary['month'], df_mrr_summary['net_mrr'],
       alpha=0.3, color=colors, label='Net MRR Change')

ax.set_title('Card 2.1: MRR Growth Over Time', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('MRR ($)', fontsize=12)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('day16_section2_mrr_growth.png', dpi=150, bbox_inches='tight')
print("\n✅ Saved: day16_section2_mrr_growth.png")
plt.show()

# Card 2.2: Month-over-Month Growth Rate
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(df_mrr_summary['month'], df_mrr_summary['mom_growth_rate_pct'],
        color='#3498db', linewidth=2.5, marker='o', markersize=7)

# Fill areas
ax.fill_between(df_mrr_summary['month'], 0, df_mrr_summary['mom_growth_rate_pct'],
                where=(df_mrr_summary['mom_growth_rate_pct'] >= 0),
                alpha=0.3, color='green', label='Positive Growth')
ax.fill_between(df_mrr_summary['month'], 0, df_mrr_summary['mom_growth_rate_pct'],
                where=(df_mrr_summary['mom_growth_rate_pct'] < 0),
                alpha=0.3, color='red', label='Negative Growth')

ax.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1)
ax.set_title('Card 2.2: Month-over-Month Growth Rate (%)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Growth Rate (%)', fontsize=12)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('day16_section2_growth_rate.png', dpi=150, bbox_inches='tight')
print("✅ Saved: day16_section2_growth_rate.png")
plt.show()

# ============================================================================
# SECTION 3: COHORT RETENTION ANALYSIS (⭐ PRIMARY VISUAL)
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: COHORT RETENTION ANALYSIS")
print("=" * 70)

df_retention_12m = df_retention[df_retention['months_since_signup'] <= 12].copy()
cohorts = sorted(df_retention_12m['cohort_month'].unique())

print(f"\n⭐ Cohort Retention Curves: {len(cohorts)} cohorts tracked")
print(f"📊 Total data points: {len(df_retention_12m)}")

# Card 3.1: Cohort Retention Curves (PRIMARY VISUAL)
fig, ax = plt.subplots(figsize=(16, 9))

colors = sns.color_palette('husl', len(cohorts))

for i, cohort in enumerate(cohorts):
    cohort_data = df_retention_12m[df_retention_12m['cohort_month'] == cohort]
    cohort_data = cohort_data.sort_values('months_since_signup')

    ax.plot(cohort_data['months_since_signup'], cohort_data['retention_rate_pct'],
            color=colors[i], linewidth=2.5, marker='o', markersize=5,
            label=cohort.strftime('%Y-%m'), alpha=0.85)

ax.set_title('⭐ Card 3.1: Cohort Retention Curves (PRIMARY DECISION VISUAL)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Months Since Signup', fontsize=13)
ax.set_ylabel('Retention Rate (%)', fontsize=13)
ax.set_ylim(0, 105)
ax.set_xlim(-0.5, 12.5)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', ncol=2, fontsize=9,
          frameon=True, shadow=True)
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig('day16_section3_cohort_retention.png', dpi=150, bbox_inches='tight')
print("\n✅ Saved: day16_section3_cohort_retention.png")
plt.show()

# Card 3.2: Churn Heatmap
pivot = df_churn_cohort.pivot_table(
    index='cohort_month',
    columns='plan_tier',
    values='churn_rate_pct',
    aggfunc='mean'
)
pivot.index = pivot.index.strftime('%Y-%m')

fig, ax = plt.subplots(figsize=(10, 14))
sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd',
            linewidths=0.5, cbar_kws={'label': 'Churn Rate (%)'},
            ax=ax, vmin=0, vmax=60)

ax.set_title('Card 3.2: Churn Heatmap by Cohort × Plan Tier',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Plan Tier', fontsize=13)
ax.set_ylabel('Cohort Month', fontsize=13)
plt.tight_layout()
plt.savefig('day16_section3_churn_heatmap.png', dpi=150, bbox_inches='tight')
print("✅ Saved: day16_section3_churn_heatmap.png")
plt.show()

# ============================================================================
# SECTION 4: CUSTOMER HEALTH ALERTS
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: CUSTOMER HEALTH ALERTS")
print("=" * 70)

health_distribution = df_customer_health['health_status'].value_counts()

print(f"\n🚨 Customer Health Distribution:")
for status, count in health_distribution.items():
    pct = (count / health_distribution.sum()) * 100
    print(f"   {status}: {count} ({pct:.1f}%)")

# Card 4.1: Customer Health Distribution
fig, ax = plt.subplots(figsize=(10, 8))

colors_map = {'Healthy': '#2ecc71', 'At Risk': '#f39c12', 'Churned': '#95a5a6', 'Critical': '#e74c3c'}
pie_colors = [colors_map.get(status, 'gray') for status in health_distribution.index]

wedges, texts, autotexts = ax.pie(health_distribution.values,
                                    labels=health_distribution.index,
                                    autopct='%1.1f%%',
                                    startangle=90,
                                    colors=pie_colors,
                                    textprops={'fontsize': 13, 'weight': 'bold'},
                                    explode=[0.05] * len(health_distribution))

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(14)

ax.set_title('Card 4.1: Customer Health Distribution',
             fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('day16_section4_health_distribution.png', dpi=150, bbox_inches='tight')
print("\n✅ Saved: day16_section4_health_distribution.png")
plt.show()

# Card 4.2: Top At-Risk Customers
at_risk_customers = df_customer_health[
    df_customer_health['health_status'] == 'At Risk'
].nlargest(10, 'ltv_estimate')

if len(at_risk_customers) > 0:
    fig, ax = plt.subplots(figsize=(12, 7))

    at_risk_sorted = at_risk_customers.sort_values('ltv_estimate', ascending=True)
    bars = ax.barh(range(len(at_risk_sorted)), at_risk_sorted['ltv_estimate'],
                   color='#e74c3c', alpha=0.8, edgecolor='darkred', linewidth=1.5)

    ax.set_yticks(range(len(at_risk_sorted)))
    ax.set_yticklabels(at_risk_sorted['customer_id'], fontsize=10)

    # Add value labels
    for i, (idx, row) in enumerate(at_risk_sorted.iterrows()):
        ax.text(row['ltv_estimate'] + 30, i, f"${row['ltv_estimate']:,.0f}",
                va='center', fontsize=10, fontweight='bold')

    ax.set_title(f"Card 4.2: Top {len(at_risk_customers)} At-Risk Customers (by LTV)",
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Lifetime Value ($)', fontsize=12)
    ax.set_ylabel('Customer ID', fontsize=12)
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig('day16_section4_at_risk_customers.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: day16_section4_at_risk_customers.png")
    plt.show()

    print(f"\n💰 Total LTV at risk: ${at_risk_customers['ltv_estimate'].sum():,.2f}")
else:
    print("\n✅ No at-risk customers!")

print("\n" + "=" * 70)
print("✅ ALL VISUALIZATIONS GENERATED!")
print("=" * 70)
print("\n📁 Saved files:")
print("   - day16_section1_kpis.png")
print("   - day16_section2_mrr_growth.png")
print("   - day16_section2_growth_rate.png")
print("   - day16_section3_cohort_retention.png")
print("   - day16_section3_churn_heatmap.png")
print("   - day16_section4_health_distribution.png")
print("   - day16_section4_at_risk_customers.png")
print("\n📊 Compare these with your Metabase dashboard!")
print("=" * 70)
