"""
IBA Climate Registry Intelligence Layer
Streamlit Dashboard for Analytics and Search
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from day01_PIPELINE_analytics import Day01Analytics

# Page configuration
st.set_page_config(
    page_title="IBA Climate Registry Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌍 IBA Climate Registry Intelligence Layer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analytics Dashboard for Bar Association Climate Initiatives</div>', unsafe_allow_html=True)

# Initialize analytics
@st.cache_resource
def load_analytics():
    """Load analytics with caching"""
    data_path = Path(__file__).parent / 'day01_DATA_registry_raw.json'
    return Day01Analytics(str(data_path))

try:
    analytics = load_analytics()
    metrics = analytics.get_key_metrics()
    summary = analytics.get_summary_stats()

    # Sidebar
    with st.sidebar:
        st.image("https://www.ibanet.org/images/default-source/default-album/iba-logo.png", width=200)
        st.markdown("---")

        st.subheader("About")
        st.markdown("""
        This dashboard provides intelligence on bar association climate initiatives worldwide,
        built on top of the IBA Climate Registry.
        """)

        st.markdown("---")
        st.subheader("Quick Stats")
        st.metric("Data Source", "IBA Climate Registry")
        st.metric("Last Updated", analytics.metadata['scraped_at'])
        st.metric("Quality Score", f"{metrics['quality_score']:.1f}%")

        st.markdown("---")
        st.markdown("**Contact:** Sara Carnegie (IBA LPRU)")
        st.markdown("**Project:** Day 01 - 3h MVP")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📚 Total Resources",
            value=metrics['total_resources'],
            help="Total number of resources scraped from IBA Registry"
        )

    with col2:
        st.metric(
            label="🌍 Countries",
            value=metrics['countries'],
            help="Number of countries represented"
        )

    with col3:
        st.metric(
            label="📍 Regions",
            value=metrics['regions'],
            help="IBA regions covered"
        )

    with col4:
        st.metric(
            label="📧 Contacts",
            value=summary['total_contacts'],
            help="Number of contact emails available"
        )

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🗺️ Geographic Analysis", "📋 Resources", "📧 Contacts"])

    with tab1:
        st.subheader("Registry Overview")

        # Summary insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Most Active Region:** {summary['most_active_region']}")
        with col2:
            st.info(f"**Most Common Type:** {summary['most_common_type'].title()}")
        with col3:
            st.info(f"**Classification Quality:** {summary['coverage_quality']}")

        st.markdown("---")

        # Main visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                analytics.plot_regional_distribution(),
                use_container_width=True,
                key="regional_dist"
            )

        with col2:
            exclude_other = st.checkbox("Exclude 'Other' category", value=True, key="exclude_other_pie")
            st.plotly_chart(
                analytics.plot_type_breakdown(exclude_other=exclude_other),
                use_container_width=True,
                key="type_breakdown"
            )

        # Stacked bar chart
        st.plotly_chart(
            analytics.plot_type_by_region(),
            use_container_width=True,
            key="type_by_region"
        )

    with tab2:
        st.subheader("Global Coverage Analysis")

        # World map
        st.plotly_chart(
            analytics.plot_country_map(),
            use_container_width=True,
            key="world_map"
        )

        st.markdown("---")

        # Top contributors
        st.subheader("🏆 Top Contributors")
        top_n = st.slider("Number of countries to display", 5, 20, 10, key="top_n_slider")

        top_contributors = analytics.get_top_contributors(n=top_n)

        st.dataframe(
            top_contributors,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Country": st.column_config.TextColumn("Country", width="medium"),
                "Count": st.column_config.NumberColumn("Resources", format="%d"),
                "Percentage": st.column_config.NumberColumn("% of Total", format="%.1f%%"),
                "Types": st.column_config.TextColumn("Resource Types", width="large")
            }
        )

    with tab3:
        st.subheader("Resource Directory")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_region = st.multiselect(
                "Filter by Region",
                options=sorted(analytics.resources['region'].unique()),
                default=None
            )

        with col2:
            selected_type = st.multiselect(
                "Filter by Type",
                options=sorted(analytics.resources['type'].unique()),
                default=None
            )

        with col3:
            selected_country = st.multiselect(
                "Filter by Country",
                options=sorted(analytics.resources['country'].unique()),
                default=None
            )

        # Apply filters
        filtered_df = analytics.resources.copy()

        if selected_region:
            filtered_df = filtered_df[filtered_df['region'].isin(selected_region)]

        if selected_type:
            filtered_df = filtered_df[filtered_df['type'].isin(selected_type)]

        if selected_country:
            filtered_df = filtered_df[filtered_df['country'].isin(selected_country)]

        # Display results
        st.write(f"**Showing {len(filtered_df)} of {len(analytics.resources)} resources**")

        # Prepare display dataframe
        display_df = filtered_df[['title', 'type', 'country', 'region', 'url']].copy()
        display_df.columns = ['Title', 'Type', 'Country', 'Region', 'URL']

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Title": st.column_config.TextColumn("Title", width="large"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Country": st.column_config.TextColumn("Country", width="medium"),
                "Region": st.column_config.TextColumn("Region", width="medium"),
                "URL": st.column_config.LinkColumn("Link", width="medium")
            }
        )

    with tab4:
        st.subheader("Contact Directory")

        contact_df = analytics.get_contact_directory()

        if len(contact_df) > 0:
            st.write(f"**{len(contact_df)} contacts available**")

            # Filter by region
            contact_regions = st.multiselect(
                "Filter by Region",
                options=sorted(contact_df['Region'].unique()),
                default=None,
                key="contact_region_filter"
            )

            if contact_regions:
                contact_df = contact_df[contact_df['Region'].isin(contact_regions)]

            st.dataframe(
                contact_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Name": st.column_config.TextColumn("Contact Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="large"),
                    "Country": st.column_config.TextColumn("Country", width="medium"),
                    "Region": st.column_config.TextColumn("Region", width="medium")
                }
            )
        else:
            st.info("No contact information available in the registry.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Built for IBA LPRU | Data Source: <a href="https://www.ibanet.org/IBA-Climate-Registry" target="_blank">IBA Climate Registry</a> |
        Last Updated: {scraped_at}
    </div>
    """.format(scraped_at=analytics.metadata['scraped_at']), unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ Data file not found. Please run the scraper first: `python day01_DATA_scraper.py`")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()
