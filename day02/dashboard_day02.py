"""
Streamlit Dashboard for Day 02 - Creator Intelligence System
Interactive data visualization for Instagram Business analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Creator Intelligence Dashboard",
    page_icon="📊",
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
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    .warning-metric {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-metric {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load data from database and JSON results"""
    from src.data_manager import DataManager

    dm = DataManager()

    # Load database data
    account_metrics = dm.get_account_metrics()
    posts = dm.get_posts()

    # Load Hour 2 analysis results
    results_path = Path(__file__).parent / 'data' / 'hour2_analysis_results.json'
    with open(results_path, 'r') as f:
        analysis_results = json.load(f)

    return account_metrics, posts, analysis_results

# Initialize data
try:
    account_metrics, posts, analysis_results = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run the analysis pipeline first: `python pipeline_day02_hour2.py`")
    data_loaded = False
    st.stop()

# Sidebar navigation
st.sidebar.markdown("## 📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Overview", "📈 Growth Analysis", "🎬 Content Performance", "💰 LTV & ROI", "🤖 AI Insights"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Account Info")
st.sidebar.metric("Current Followers", f"{account_metrics['followers'].iloc[-1]:,}")
st.sidebar.metric("Total Posts", f"{len(posts):,}")
st.sidebar.metric("Avg Engagement", f"{posts['engagement_rate'].mean():.2f}%")
st.sidebar.metric("Account Value", f"${analysis_results['ltv_analysis']['follower_ltv']['total_account_value']:,.0f}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Target")
st.sidebar.info("**Goal:** 200K followers in 6 months\n\n**Required Weekly Growth:** 2.74%")

# Main content based on selected page
if page == "🏠 Overview":
    st.markdown('<div class="main-header">📊 Creator Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown("**Client:** @wanderlust_samira | **Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    st.markdown("---")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    ltv_data = analysis_results['ltv_analysis']['follower_ltv']
    growth_data = analysis_results['ltv_analysis']['growth_scenarios']

    with col1:
        st.metric(
            "Account Value",
            f"${ltv_data['total_account_value']:,.0f}",
            delta=f"${ltv_data['monthly_value_per_follower']:.2f}/follower/month"
        )

    with col2:
        current_followers = account_metrics['followers'].iloc[-1]
        prev_followers = account_metrics['followers'].iloc[-8] if len(account_metrics) >= 8 else account_metrics['followers'].iloc[0]
        weekly_growth = ((current_followers - prev_followers) / prev_followers) * 100
        st.metric(
            "Weekly Growth",
            f"{weekly_growth:.2f}%",
            delta=f"Target: 2.74%",
            delta_color="inverse"
        )

    with col3:
        avg_engagement = posts['engagement_rate'].mean()
        st.metric(
            "Avg Engagement",
            f"{avg_engagement:.2f}%",
            delta="Above 30% is excellent"
        )

    with col4:
        optimistic = growth_data['optimistic']['projected_followers']
        st.metric(
            "6-Month Projection",
            f"{optimistic:,.0f}",
            delta=f"+{growth_data['optimistic']['total_growth']:,.0f}"
        )

    st.markdown("---")

    # Growth Progress
    st.subheader("📈 Growth Progress")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Account growth over time
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=account_metrics['date'],
            y=account_metrics['followers'],
            mode='lines+markers',
            name='Actual Followers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))

        # Add target line
        last_date = account_metrics['date'].iloc[-1]
        target_date = last_date + timedelta(days=180)
        fig.add_trace(go.Scatter(
            x=[last_date, target_date],
            y=[current_followers, 200000],
            mode='lines',
            name='Target Path',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

        fig.update_layout(
            title="Follower Growth Over Time",
            xaxis_title="Date",
            yaxis_title="Followers",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Growth scenarios comparison
        scenarios = ['Pessimistic', 'Realistic', 'Optimistic']
        projections = [
            growth_data['pessimistic']['projected_followers'],
            growth_data['realistic']['projected_followers'],
            growth_data['optimistic']['projected_followers']
        ]

        fig = go.Figure(go.Bar(
            x=scenarios,
            y=projections,
            text=[f"{p:,.0f}" for p in projections],
            textposition='auto',
            marker=dict(color=['#dc3545', '#ffc107', '#28a745'])
        ))

        fig.add_hline(y=200000, line_dash="dash", line_color="red",
                      annotation_text="Target: 200K")

        fig.update_layout(
            title="6-Month Projections",
            yaxis_title="Projected Followers",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # Content Performance Overview
    st.markdown("---")
    st.subheader("🎬 Content Performance Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Content type distribution
        content_counts = posts['media_type'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=content_counts.index,
            values=content_counts.values,
            hole=0.4,
            marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
        )])

        fig.update_layout(
            title="Content Type Distribution",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Engagement by content type
        engagement_by_type = posts.groupby('media_type')['engagement_rate'].mean().sort_values(ascending=True)

        fig = go.Figure(go.Bar(
            x=engagement_by_type.values,
            y=engagement_by_type.index,
            orientation='h',
            text=[f"{v:.2f}%" for v in engagement_by_type.values],
            textposition='auto',
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ))

        fig.update_layout(
            title="Average Engagement by Content Type",
            xaxis_title="Engagement Rate (%)",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    # Recent Top Posts
    st.markdown("---")
    st.subheader("🏆 Top 5 Recent Posts")

    top_posts = posts.nlargest(5, 'engagement_rate')[['timestamp', 'media_type', 'caption', 'engagement_rate', 'likes', 'comments', 'saves', 'reach']]

    for idx, post in top_posts.iterrows():
        with st.expander(f"#{idx+1} - {post['media_type']} - {post['engagement_rate']:.2f}% engagement"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Likes", f"{post['likes']:,}")
            col2.metric("Comments", f"{post['comments']:,}")
            col3.metric("Saves", f"{post['saves']:,}")
            col4.metric("Reach", f"{post['reach']:,}")

            caption_preview = post['caption'][:200] + "..." if len(post['caption']) > 200 else post['caption']
            st.markdown(f"**Caption:** {caption_preview}")
            st.caption(f"Posted: {post['timestamp'].strftime('%Y-%m-%d %H:%M')}")

elif page == "📈 Growth Analysis":
    st.markdown('<div class="main-header">📈 Growth Analysis</div>', unsafe_allow_html=True)

    # Current state
    st.subheader("Current Growth Metrics")

    col1, col2, col3, col4 = st.columns(4)

    current_followers = account_metrics['followers'].iloc[-1]
    start_followers = account_metrics['followers'].iloc[0]
    days = (account_metrics['date'].iloc[-1] - account_metrics['date'].iloc[0]).days
    total_growth = current_followers - start_followers
    growth_pct = (total_growth / start_followers) * 100

    col1.metric("Current Followers", f"{current_followers:,}")
    col2.metric("Total Growth (90 days)", f"+{total_growth:,}", f"{growth_pct:.2f}%")
    col3.metric("Days to 200K (current rate)", f"{int((200000 - current_followers) / (total_growth / days))}")
    col4.metric("Required Daily Growth", f"+{int((200000 - current_followers) / 180)}")

    # Detailed growth chart
    st.markdown("---")
    st.subheader("Daily Growth Trend")

    # Calculate daily growth
    account_metrics['daily_growth'] = account_metrics['followers'].diff()
    account_metrics['weekly_growth_pct'] = account_metrics['followers'].pct_change(periods=7) * 100

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Follower Count Over Time", "Daily New Followers"),
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4]
    )

    # Follower count
    fig.add_trace(
        go.Scatter(
            x=account_metrics['date'],
            y=account_metrics['followers'],
            mode='lines',
            name='Followers',
            line=dict(color='#1f77b4', width=2),
            fill='tonexty'
        ),
        row=1, col=1
    )

    # Daily growth
    fig.add_trace(
        go.Bar(
            x=account_metrics['date'][1:],
            y=account_metrics['daily_growth'][1:],
            name='Daily Growth',
            marker=dict(
                color=account_metrics['daily_growth'][1:],
                colorscale='RdYlGn',
                showscale=True
            )
        ),
        row=2, col=1
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Followers", row=1, col=1)
    fig.update_yaxes(title_text="New Followers", row=2, col=1)

    fig.update_layout(height=700, showlegend=False, hovermode='x unified')

    st.plotly_chart(fig, use_container_width=True)

    # Growth scenarios
    st.markdown("---")
    st.subheader("6-Month Growth Scenarios")

    growth_scenarios = analysis_results['ltv_analysis']['growth_scenarios']

    # Create comparison table
    scenarios_df = pd.DataFrame({
        'Scenario': ['Pessimistic', 'Realistic', 'Optimistic', 'Target'],
        'Weekly Growth': [
            f"{growth_scenarios['pessimistic']['weekly_growth_rate']:.2f}%",
            f"{growth_scenarios['realistic']['weekly_growth_rate']:.2f}%",
            f"{growth_scenarios['optimistic']['weekly_growth_rate']:.2f}%",
            "2.83%"
        ],
        'Projected Followers': [
            f"{growth_scenarios['pessimistic']['projected_followers']:,.0f}",
            f"{growth_scenarios['realistic']['projected_followers']:,.0f}",
            f"{growth_scenarios['optimistic']['projected_followers']:,.0f}",
            "200,000"
        ],
        'Total Growth': [
            f"+{growth_scenarios['pessimistic']['total_growth']:,.0f}",
            f"+{growth_scenarios['realistic']['total_growth']:,.0f}",
            f"+{growth_scenarios['optimistic']['total_growth']:,.0f}",
            "+97,232"
        ],
        'Months to 200K': [
            f"{growth_scenarios['pessimistic']['months_to_200k']:.1f}",
            f"{growth_scenarios['realistic']['months_to_200k']:.1f}",
            f"{growth_scenarios['optimistic']['months_to_200k']:.1f}",
            "6.0"
        ]
    })

    st.dataframe(scenarios_df, hide_index=True, use_container_width=True)

    # Projection visualization
    col1, col2 = st.columns(2)

    with col1:
        # Growth rate comparison
        fig = go.Figure()

        scenarios = ['Current', 'Pessimistic', 'Realistic', 'Optimistic', 'Target']
        growth_rates = [
            growth_pct / (days / 7),  # Weekly rate
            growth_scenarios['pessimistic']['weekly_growth_rate'],
            growth_scenarios['realistic']['weekly_growth_rate'],
            growth_scenarios['optimistic']['weekly_growth_rate'],
            2.83
        ]

        colors = ['#6c757d', '#dc3545', '#ffc107', '#28a745', '#007bff']

        fig.add_trace(go.Bar(
            x=scenarios,
            y=growth_rates,
            text=[f"{g:.2f}%" for g in growth_rates],
            textposition='auto',
            marker=dict(color=colors)
        ))

        fig.update_layout(
            title="Weekly Growth Rate Comparison",
            yaxis_title="Growth Rate (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Time to 200K
        months_to_200k = [
            (200000 - current_followers) / (total_growth / (days/30)),
            growth_scenarios['pessimistic']['months_to_200k'],
            growth_scenarios['realistic']['months_to_200k'],
            growth_scenarios['optimistic']['months_to_200k']
        ]

        scenarios_short = ['Current', 'Pessimistic', 'Realistic', 'Optimistic']

        fig = go.Figure(go.Bar(
            x=scenarios_short,
            y=months_to_200k,
            text=[f"{m:.1f}mo" for m in months_to_200k],
            textposition='auto',
            marker=dict(color=['#6c757d', '#dc3545', '#ffc107', '#28a745'])
        ))

        fig.add_hline(y=6, line_dash="dash", line_color="red",
                      annotation_text="6-Month Target")

        fig.update_layout(
            title="Months to Reach 200K Followers",
            yaxis_title="Months",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # Reach and Impressions
    st.markdown("---")
    st.subheader("Reach & Impressions Trends")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=account_metrics['date'],
        y=account_metrics['reach'],
        mode='lines',
        name='Reach',
        line=dict(color='#1f77b4', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=account_metrics['date'],
        y=account_metrics['impressions'],
        mode='lines',
        name='Impressions',
        line=dict(color='#ff7f0e', width=2)
    ))

    fig.update_layout(
        title="Daily Reach and Impressions",
        xaxis_title="Date",
        yaxis_title="Count",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "🎬 Content Performance":
    st.markdown('<div class="main-header">🎬 Content Performance Analysis</div>', unsafe_allow_html=True)

    # Content type metrics
    st.subheader("Performance by Content Type")

    content_roi = analysis_results['ltv_analysis']['content_roi']

    col1, col2, col3 = st.columns(3)

    for idx, content in enumerate(content_roi):
        col = [col1, col2, col3][idx]
        with col:
            st.markdown(f"### {content['content_type']}")
            st.metric("Posts", content['post_count'])
            st.metric("Avg Engagement", f"{content['avg_engagement_rate']:.2f}%")
            st.metric("ROI", f"{content['roi_percentage']:,.0f}%")
            st.metric("Net Profit/Post", f"${content['net_profit_per_post']:,.0f}")

    # Detailed comparison charts
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # ROI comparison
        fig = go.Figure()

        content_types = [c['content_type'] for c in content_roi]
        roi_values = [c['roi_percentage'] for c in content_roi]

        fig.add_trace(go.Bar(
            x=content_types,
            y=roi_values,
            text=[f"{r:,.0f}%" for r in roi_values],
            textposition='auto',
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ))

        fig.update_layout(
            title="ROI by Content Type",
            yaxis_title="ROI (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Net profit comparison
        profit_values = [c['net_profit_per_post'] for c in content_roi]

        fig = go.Figure(go.Bar(
            x=content_types,
            y=profit_values,
            text=[f"${p:,.0f}" for p in profit_values],
            textposition='auto',
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ))

        fig.update_layout(
            title="Net Profit per Post",
            yaxis_title="Profit ($)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # Engagement over time
    st.markdown("---")
    st.subheader("Engagement Trends")

    # Create time-based engagement chart
    posts_sorted = posts.sort_values('timestamp')
    posts_sorted['rolling_engagement'] = posts_sorted['engagement_rate'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    # Scatter plot with color by content type
    for content_type in posts['media_type'].unique():
        type_data = posts_sorted[posts_sorted['media_type'] == content_type]
        fig.add_trace(go.Scatter(
            x=type_data['timestamp'],
            y=type_data['engagement_rate'],
            mode='markers',
            name=content_type,
            marker=dict(size=8, opacity=0.6)
        ))

    # Add rolling average
    fig.add_trace(go.Scatter(
        x=posts_sorted['timestamp'],
        y=posts_sorted['rolling_engagement'],
        mode='lines',
        name='7-Post Moving Avg',
        line=dict(color='black', width=2, dash='dash')
    ))

    fig.update_layout(
        title="Engagement Rate Over Time (by Content Type)",
        xaxis_title="Date",
        yaxis_title="Engagement Rate (%)",
        hovermode='closest',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Top performing posts
    st.markdown("---")
    st.subheader("🏆 Top 10 Performing Posts")

    top_posts = posts.nlargest(10, 'engagement_rate')[
        ['timestamp', 'media_type', 'caption', 'engagement_rate', 'likes', 'comments', 'saves', 'shares', 'reach']
    ].copy()

    # Format for display
    top_posts['timestamp'] = top_posts['timestamp'].dt.strftime('%Y-%m-%d')
    top_posts['caption_preview'] = top_posts['caption'].str[:60] + "..."
    top_posts['engagement_rate'] = top_posts['engagement_rate'].round(2).astype(str) + "%"

    display_cols = ['timestamp', 'media_type', 'caption_preview', 'engagement_rate', 'likes', 'comments', 'saves', 'reach']
    st.dataframe(
        top_posts[display_cols].reset_index(drop=True),
        hide_index=True,
        use_container_width=True
    )

    # Posting patterns
    st.markdown("---")
    st.subheader("📅 Posting Patterns")

    col1, col2 = st.columns(2)

    with col1:
        # Day of week analysis
        posts['day_of_week'] = posts['timestamp'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        day_engagement = posts.groupby('day_of_week')['engagement_rate'].mean().reindex(day_order)

        fig = go.Figure(go.Bar(
            x=day_engagement.index,
            y=day_engagement.values,
            text=[f"{v:.2f}%" for v in day_engagement.values],
            textposition='auto',
            marker=dict(color=day_engagement.values, colorscale='Viridis', showscale=True)
        ))

        fig.update_layout(
            title="Average Engagement by Day of Week",
            xaxis_title="Day",
            yaxis_title="Avg Engagement (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Hour of day analysis
        posts['hour'] = posts['timestamp'].dt.hour
        hour_engagement = posts.groupby('hour')['engagement_rate'].mean()

        fig = go.Figure(go.Scatter(
            x=hour_engagement.index,
            y=hour_engagement.values,
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title="Average Engagement by Hour of Day",
            xaxis_title="Hour (24h format)",
            yaxis_title="Avg Engagement (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

elif page == "💰 LTV & ROI":
    st.markdown('<div class="main-header">💰 Lifetime Value & ROI Analysis</div>', unsafe_allow_html=True)

    ltv_data = analysis_results['ltv_analysis']['follower_ltv']
    engagement_value = analysis_results['ltv_analysis']['engagement_value']

    # LTV Overview
    st.subheader("Follower Lifetime Value")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("LTV per Follower", f"${ltv_data['ltv_per_follower']:.2f}")
    col2.metric("Monthly Value", f"${ltv_data['monthly_value_per_follower']:.2f}")
    col3.metric("Annual Value", f"${ltv_data['annual_value_per_follower']:.2f}")
    col4.metric("Total Account Value", f"${ltv_data['total_account_value']:,.0f}")

    # Revenue breakdown
    st.markdown("---")
    st.subheader("Revenue Model Breakdown")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Revenue pie chart
        revenue_breakdown = ltv_data['revenue_breakdown']

        labels = ['Ad Revenue', 'Sales Revenue', 'Sponsored Posts']
        values = [
            revenue_breakdown['ad_revenue_monthly'],
            revenue_breakdown['sales_revenue_monthly'],
            revenue_breakdown['sponsored_revenue_monthly']
        ]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            texttemplate='%{label}<br>$%{value:.2f}<br>%{percent}',
            marker=dict(colors=['#ff7f0e', '#1f77b4', '#2ca02c'])
        )])

        fig.update_layout(
            title="Monthly Revenue per Follower",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Revenue projections
        months = list(range(1, 25))
        revenue_projection = [ltv_data['monthly_value_per_follower'] * m * account_metrics['followers'].iloc[-1]
                             for m in months]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=months,
            y=revenue_projection,
            mode='lines',
            fill='tonexty',
            name='Revenue',
            line=dict(color='#28a745', width=3)
        ))

        fig.update_layout(
            title="24-Month Revenue Projection (Current Followers)",
            xaxis_title="Month",
            yaxis_title="Projected Revenue ($)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # Engagement value
    st.markdown("---")
    st.subheader("Engagement Value Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Value per interaction type
        interaction_types = ['Like', 'Comment', 'Save', 'Share']
        interaction_values = [
            engagement_value['value_per_like'],
            engagement_value['value_per_comment'],
            engagement_value['value_per_save'],
            engagement_value['value_per_share']
        ]

        fig = go.Figure(go.Bar(
            x=interaction_types,
            y=interaction_values,
            text=[f"${v:.2f}" for v in interaction_values],
            textposition='auto',
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ))

        fig.update_layout(
            title="Value per Interaction Type",
            yaxis_title="Value ($)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💡 Engagement Economics")
        st.metric("Avg Value per Post", f"${engagement_value['avg_engagement_value_per_post']:,.2f}")
        st.metric("Monthly Engagement Value", f"${engagement_value['monthly_engagement_value']:,.2f}")

        # Calculate total engagement value
        total_likes = posts['likes'].sum()
        total_comments = posts['comments'].sum()
        total_saves = posts['saves'].sum()
        total_shares = posts['shares'].sum()

        total_value = (
            total_likes * engagement_value['value_per_like'] +
            total_comments * engagement_value['value_per_comment'] +
            total_saves * engagement_value['value_per_save'] +
            total_shares * engagement_value['value_per_share']
        )

        st.metric("Total Engagement Value (All Posts)", f"${total_value:,.2f}")

        st.info("💰 **Insight:** Saves are 50x more valuable than likes! Focus on creating save-worthy content (tips, guides, resources).")

    # Content ROI detailed view
    st.markdown("---")
    st.subheader("Content Production ROI")

    content_roi = analysis_results['ltv_analysis']['content_roi']

    # Create comprehensive comparison
    roi_df = pd.DataFrame(content_roi)
    roi_df = roi_df[['content_type', 'post_count', 'avg_engagement_rate', 'value_per_post',
                     'production_cost', 'roi_percentage', 'net_profit_per_post']]

    roi_df.columns = ['Content Type', 'Posts', 'Avg Engagement (%)', 'Value/Post ($)',
                      'Cost ($)', 'ROI (%)', 'Net Profit ($)']

    roi_df['Avg Engagement (%)'] = roi_df['Avg Engagement (%)'].round(2)
    roi_df['Value/Post ($)'] = roi_df['Value/Post ($)'].round(2)
    roi_df['ROI (%)'] = roi_df['ROI (%)'].round(0)
    roi_df['Net Profit ($)'] = roi_df['Net Profit ($)'].round(2)

    st.dataframe(roi_df, hide_index=True, use_container_width=True)

    # ROI visualization
    col1, col2, col3 = st.columns(3)

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=content_roi[0]['roi_percentage'],
            title={'text': "IMAGE ROI"},
            delta={'reference': 5000},
            gauge={'axis': {'range': [None, 10000]},
                   'bar': {'color': "#1f77b4"},
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 5000}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=content_roi[1]['roi_percentage'],
            title={'text': "CAROUSEL ROI"},
            delta={'reference': 3000},
            gauge={'axis': {'range': [None, 6000]},
                   'bar': {'color': "#ff7f0e"},
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 3000}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=content_roi[2]['roi_percentage'],
            title={'text': "VIDEO ROI"},
            delta={'reference': 1500},
            gauge={'axis': {'range': [None, 3000]},
                   'bar': {'color': "#2ca02c"},
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 1500}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

elif page == "🤖 AI Insights":
    st.markdown('<div class="main-header">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)

    ai_insights = analysis_results['ai_insights']

    # Viral Content Patterns
    st.subheader("⚡ Viral Content Patterns")

    viral_patterns = ai_insights['viral_patterns']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Top Themes")
        for theme in viral_patterns['themes']:
            st.markdown(f"- {theme}")

        st.markdown("### 🎭 Emotional Triggers")
        for trigger in viral_patterns['emotional_triggers']:
            st.markdown(f"- {trigger}")

    with col2:
        st.markdown("### ✍️ Writing Style")
        style = viral_patterns['writing_style']
        st.markdown(f"**Tone:** {style['tone']}")
        st.markdown(f"**Length:** {style['length']}")
        st.markdown(f"**Emoji Usage:** {'Frequent' if style['emoji_usage']['frequent'] else 'Rare'}")

        if style['emoji_usage']['frequent']:
            st.markdown("**Common Emojis:** " + " ".join(style['emoji_usage']['common_emojis']))

        st.markdown("### #️⃣ Hashtag Strategy")
        st.markdown(f"**Strategy:** {viral_patterns['hashtag_strategy']['strategy']}")
        st.markdown("**Top Hashtags:** " + ", ".join(viral_patterns['hashtag_strategy']['common_hashtags'][:5]))

    # Success Factors
    st.markdown("---")
    st.subheader("🔑 Success Factors")

    for factor in viral_patterns['success_factors']:
        st.success(factor)

    # Caption Analysis
    st.markdown("---")
    st.subheader("✍️ Caption Effectiveness Analysis")

    caption_analysis = ai_insights['caption_analysis']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ High Performer Patterns")
        for pattern in caption_analysis['high_performers_patterns']:
            st.markdown(f"✅ {pattern}")

    with col2:
        st.markdown("### ❌ Low Performer Issues")
        for issue in caption_analysis['low_performers_issues']:
            st.markdown(f"❌ {issue}")

    # Best Practices
    st.markdown("### 💡 Caption Best Practices")

    col1, col2, col3 = st.columns(3)

    practices = caption_analysis['caption_best_practices']
    for idx, practice in enumerate(practices):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.info(practice)

    st.metric("Optimal Caption Length", caption_analysis['optimal_caption_length'])

    # Recommendations
    st.markdown("---")
    st.subheader("💡 Strategic Recommendations")

    recommendations = ai_insights['recommendations']

    for idx, rec in enumerate(recommendations, 1):
        with st.expander(f"Recommendation #{idx}"):
            st.markdown(rec)

    # Content Calendar
    st.markdown("---")
    st.subheader("📅 4-Week Content Calendar")

    calendar = ai_insights['content_calendar']

    st.markdown(f"**Posting Schedule:** {calendar['posting_schedule']}")

    # Display content pillars
    col1, col2, col3, col4 = st.columns(4)
    pillars = calendar['content_pillars']

    col1.metric("Pillar 1", pillars[0].title())
    col2.metric("Pillar 2", pillars[1].title())
    col3.metric("Pillar 3", pillars[2].title())
    col4.metric("Pillar 4", pillars[3].title())

    # Weekly content ideas
    for week_num in range(1, 5):
        week_key = f"week_{week_num}"
        if week_key in calendar:
            st.markdown(f"### Week {week_num}")
            for idx, idea in enumerate(calendar[week_key], 1):
                st.markdown(f"**Day {idx}:** {idea}")
            st.markdown("---")

    # Growth Strategy
    st.subheader("🚀 Comprehensive Growth Strategy")

    if 'growth_plan' in analysis_results['growth_strategy']:
        growth_plan = analysis_results['growth_strategy']['growth_plan']

        # Immediate Actions
        with st.expander("🎯 Immediate Actions (Next 30 Days)", expanded=True):
            if 'immediate_actions' in growth_plan:
                for action in growth_plan['immediate_actions']['actions']:
                    st.markdown(f"**{action['action']}**")
                    st.markdown(f"_{action['description']}_")
                    st.markdown("")

        # Content Strategy
        with st.expander("📝 Content Strategy"):
            if 'content_strategy' in growth_plan:
                strategy = growth_plan['content_strategy']

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Themes:**")
                    for theme in strategy['themes']:
                        st.markdown(f"- {theme}")

                    st.markdown("**Formats:**")
                    for format in strategy['formats']:
                        st.markdown(f"- {format}")

                with col2:
                    st.markdown("**Frequency:**")
                    for key, value in strategy['frequency'].items():
                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")

        # Engagement Tactics
        with st.expander("🤝 Engagement Tactics"):
            if 'engagement_tactics' in growth_plan:
                for tactic in growth_plan['engagement_tactics']['community_building']:
                    st.markdown(f"**{tactic['tactic']}**")
                    st.markdown(f"_{tactic['description']}_")
                    st.markdown("")

        # Monetization Strategy
        with st.expander("💰 Monetization Strategy"):
            if 'monetization_strategy' in growth_plan:
                for action in growth_plan['monetization_strategy']['actions']:
                    st.markdown(f"**{action['action']}**")
                    st.markdown(f"_{action['description']}_")
                    st.markdown("")

        # Growth Hacks
        with st.expander("🚀 Growth Hacks (Algorithm Optimization)"):
            if 'growth_hacks' in growth_plan:
                for tip in growth_plan['growth_hacks']['algorithm_tips']:
                    st.markdown(f"**{tip['tip']}**")
                    st.markdown(f"_{tip['description']}_")
                    st.markdown("")

        # Key Metrics
        with st.expander("📊 Key Metrics to Track"):
            if 'key_metrics' in growth_plan:
                metrics_df = pd.DataFrame(growth_plan['key_metrics']['metrics_to_track'])
                metrics_df.columns = ['Metric', 'Description']
                st.dataframe(metrics_df, hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>Creator Intelligence Dashboard - Day 02</p>
    <p>Generated: {}</p>
    <p>Data source: SQLite database (creator_intel.db) + Hour 2 Analysis Results</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
