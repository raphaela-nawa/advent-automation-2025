"""
Day 01 Analytics Pipeline
Generates statistics and visualizations from scraped IBA Registry data
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

class Day01Analytics:
    def __init__(self, data_path):
        """Load scraped data"""
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.resources = pd.DataFrame(self.data['resources'])
        self.metadata = self.data['metadata']

        # Country name to ISO code mapping for map visualization
        self.country_to_iso = {
            'Australia': 'AUS', 'Japan': 'JPN', 'Uk': 'GBR', 'United Kingdom': 'GBR',
            'England': 'GBR', 'Scotland': 'GBR', 'Wales': 'GBR', 'Northern Ireland': 'GBR',
            'America': 'USA', 'Usa': 'USA', 'United States': 'USA', 'Canada': 'CAN',
            'Brazil': 'BRA', 'Brasil': 'BRA', 'Mexico': 'MEX', 'Argentina': 'ARG',
            'Chile': 'CHL', 'Colombia': 'COL', 'Peru': 'PER',
            'Zambia': 'ZMB', 'Nigeria': 'NGA', 'South Africa': 'ZAF',
            'Pakistan': 'PAK', 'India': 'IND', 'Singapore': 'SGP', 'Taiwan': 'TWN',
            'New Zealand': 'NZL', 'International': None, 'Unknown': None,
            'Aba': 'USA', 'Iba': None, 'Ccbe': None
        }

    def get_key_metrics(self):
        """Calculate top-level metrics"""
        # Count unique countries, excluding Unknown and International
        valid_countries = self.resources[
            ~self.resources['country'].isin(['Unknown', 'International'])
        ]['country'].nunique()

        # Count regions (exclude N/A if present)
        valid_regions = self.resources[
            self.resources['region'] != 'N/A'
        ]['region'].nunique()

        return {
            'total_resources': len(self.resources),
            'countries': valid_countries,
            'regions': valid_regions,
            'quality_score': 100 - self.data['statistics']['other_percentage']
        }

    def plot_regional_distribution(self):
        """Horizontal bar chart of resources by region"""
        region_counts = self.resources['region'].value_counts()

        fig = px.bar(
            x=region_counts.values,
            y=region_counts.index,
            orientation='h',
            title='📍 Resources by Region',
            labels={'x': 'Number of Resources', 'y': 'Region'},
            color=region_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Number of Resources",
            yaxis_title="Region"
        )
        return fig

    def plot_type_breakdown(self, exclude_other=True):
        """Pie chart of resource types"""
        type_counts = self.resources['type'].value_counts()

        if exclude_other and 'other' in type_counts.index:
            type_counts = type_counts.drop('other')

        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='🏷️ Resource Types Distribution',
            hole=0.3,  # Donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        return fig

    def plot_country_map(self):
        """World map colored by resource count"""
        country_counts = self.resources['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']

        # Filter out non-country entries
        country_counts = country_counts[
            ~country_counts['country'].isin(['Unknown', 'International', 'N/A'])
        ]

        # Map to ISO codes
        country_counts['iso_code'] = country_counts['country'].map(self.country_to_iso)

        # Drop entries without valid ISO codes
        country_counts = country_counts.dropna(subset=['iso_code'])

        fig = px.choropleth(
            country_counts,
            locations='iso_code',
            color='count',
            hover_name='country',
            hover_data={'iso_code': False, 'count': True},
            title='🗺️ Global Coverage',
            color_continuous_scale='Viridis',
            labels={'count': 'Resources'}
        )

        fig.update_layout(
            height=500,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )

        return fig

    def get_top_contributors(self, n=10):
        """Table of top N countries by resource count"""
        country_stats = self.resources.groupby('country').agg({
            'type': lambda x: ', '.join(x.unique()[:3]),  # Top 3 types
            'title': 'count'
        }).reset_index()

        country_stats.columns = ['Country', 'Types', 'Count']
        country_stats['Percentage'] = (country_stats['Count'] / len(self.resources) * 100).round(1)

        # Reorder columns
        country_stats = country_stats[['Country', 'Count', 'Percentage', 'Types']]

        return country_stats.nlargest(n, 'Count')

    def get_summary_stats(self):
        """Generate text summary for dashboard"""
        stats = self.data['statistics']

        # Find most common type (excluding contact_email)
        type_counts = {k: v for k, v in stats['by_type'].items() if k != 'contact_email'}
        most_common_type = max(type_counts, key=type_counts.get) if type_counts else 'N/A'

        return {
            'most_common_type': most_common_type,
            'most_active_region': max(stats['by_region'], key=stats['by_region'].get),
            'coverage_quality': f"{100 - stats['other_percentage']:.1f}%",
            'total_contacts': stats['by_type'].get('contact_email', 0)
        }

    def plot_type_by_region(self):
        """Stacked bar chart: resource types per region"""
        # Create pivot table
        type_region = pd.crosstab(self.resources['region'], self.resources['type'])

        fig = go.Figure()

        for resource_type in type_region.columns:
            fig.add_trace(go.Bar(
                name=resource_type,
                x=type_region.index,
                y=type_region[resource_type],
                text=type_region[resource_type],
                textposition='inside'
            ))

        fig.update_layout(
            barmode='stack',
            title='📊 Resource Types by Region',
            xaxis_title='Region',
            yaxis_title='Count',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def get_contact_directory(self):
        """Extract all contact emails with metadata"""
        contacts = self.resources[self.resources['type'] == 'contact_email'].copy()

        if len(contacts) == 0:
            return pd.DataFrame()

        # Select relevant columns
        contact_df = contacts[['contact_name', 'title', 'country', 'region']].copy()
        contact_df.columns = ['Name', 'Email', 'Country', 'Region']

        return contact_df.sort_values(['Region', 'Country'])

if __name__ == "__main__":
    # Test the analytics
    analytics = Day01Analytics('day01_DATA_registry_raw.json')

    print("Key Metrics:")
    print(analytics.get_key_metrics())

    print("\nSummary Stats:")
    print(analytics.get_summary_stats())

    print("\nTop Contributors:")
    print(analytics.get_top_contributors())

    print("\nTest plots...")
    fig1 = analytics.plot_regional_distribution()
    fig2 = analytics.plot_type_breakdown()
    fig3 = analytics.plot_country_map()
    print("✅ All plots generated successfully")
