import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from day17_CONFIG_settings import (
    DAY17_DB_PATH,
    DAY17_DEADLINE_THRESHOLDS_DAYS,
    DAY17_JURISDICTIONS,
)

BASE_DIR = Path(__file__).resolve().parent
QUERY_DIR = BASE_DIR / "queries"


def day17_get_db_path() -> Path:
    if DAY17_DB_PATH.is_absolute():
        return DAY17_DB_PATH
    return (BASE_DIR / DAY17_DB_PATH).resolve()


def day17_read_sql(query_filename: str) -> str:
    return (QUERY_DIR / query_filename).read_text()


def day17_query_df(query_filename: str, params: dict | None = None) -> pd.DataFrame:
    db_path = day17_get_db_path()
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(day17_read_sql(query_filename), conn, params=params or {})


def day17_get_date_bounds() -> tuple[pd.Timestamp, pd.Timestamp]:
    db_path = day17_get_db_path()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT MIN(d.full_date), MAX(d.full_date)
            FROM fct_holdings h
            JOIN dim_date d ON h.date_key = d.date_key
            """
        ).fetchone()
    return pd.to_datetime(row[0]), pd.to_datetime(row[1])


def day17_get_latest_date() -> pd.Timestamp:
    db_path = day17_get_db_path()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT MAX(d.full_date)
            FROM fct_holdings h
            JOIN dim_date d ON h.date_key = d.date_key
            """
        ).fetchone()
    return pd.to_datetime(row[0])


st.set_page_config(page_title="Day 17 Legal Analytics", layout="wide")

st.title("Day 17 - Multi-Jurisdictional Asset Compliance Dashboard")

# Validate database path early
if not day17_get_db_path().exists():
    st.error(f"Database not found at {day17_get_db_path()}")
    st.stop()

min_date, max_date = day17_get_date_bounds()
latest_date = day17_get_latest_date()

with st.sidebar:
    st.header("Filters")
    selected_jurisdictions = st.multiselect(
        "Jurisdictions",
        options=DAY17_JURISDICTIONS,
        default=DAY17_JURISDICTIONS,
    )
    point_in_time_date = st.date_input(
        "Point-in-time date",
        value=latest_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

st.caption(
    "Decision focus: Identify assets requiring regulatory attention this quarter based on "
    "classification changes, jurisdictional compliance status, and upcoming deadlines."
)

portfolio_df = day17_query_df("day17_QUERY_portfolio_overview.sql")

if selected_jurisdictions:
    portfolio_df = portfolio_df[portfolio_df["jurisdiction"].isin(selected_jurisdictions)]

# Section 1 - Portfolio Overview
st.subheader("Portfolio Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Assets", portfolio_df["asset_id"].nunique())
with col2:
    st.metric("Total Market Value", f"${portfolio_df['market_value'].sum():,.0f}")
with col3:
    st.metric("Latest Snapshot Date", latest_date.date().isoformat())

col4, col5 = st.columns(2)
with col4:
    assets_by_jurisdiction = (
        portfolio_df.groupby("jurisdiction")["asset_id"].nunique().reset_index()
    )
    fig_jur = px.bar(
        assets_by_jurisdiction,
        x="jurisdiction",
        y="asset_id",
        title="Assets by Jurisdiction",
        labels={"asset_id": "Asset Count"},
    )
    st.plotly_chart(fig_jur, use_container_width=True)

with col5:
    assets_by_class = (
        portfolio_df.groupby("asset_class")["asset_id"].nunique().reset_index()
    )
    fig_class = px.bar(
        assets_by_class.sort_values("asset_id", ascending=False),
        x="asset_class",
        y="asset_id",
        title="Assets by Class",
        labels={"asset_id": "Asset Count"},
    )
    st.plotly_chart(fig_class, use_container_width=True)

# Section 2 - Historical Tracking (Primary Visual)
st.subheader("Asset Classification Timeline (SCD Type 2)")
st.caption("Timeline uses synthetic history for Equipment/IP/Certification assets (change date = latest holdings date - 60 days).")
scd_df = day17_query_df("day17_QUERY_scd_timeline.sql")
scd_df["valid_from"] = pd.to_datetime(scd_df["valid_from"])
scd_df["valid_to"] = pd.to_datetime(scd_df["valid_to"]).fillna(latest_date)

fig_timeline = px.timeline(
    scd_df,
    x_start="valid_from",
    x_end="valid_to",
    y="asset_id",
    color="asset_class",
    hover_data=["asset_name", "asset_type", "version_status"],
    title="Asset Classification Changes Over Time",
)
fig_timeline.update_yaxes(autorange="reversed")
fig_timeline.update_layout(height=500)
st.plotly_chart(fig_timeline, use_container_width=True)

st.subheader("Classification Changes This Quarter")
changes_df = day17_query_df("day17_QUERY_changes_this_quarter.sql")
st.dataframe(changes_df, use_container_width=True)

# Section 3 - Compliance Status
st.subheader("Compliance Status by Jurisdiction")
compliance_df = day17_query_df("day17_QUERY_compliance_by_jurisdiction.sql")
if selected_jurisdictions:
    compliance_df = compliance_df[
        compliance_df["jurisdiction"].isin(selected_jurisdictions)
    ]

fig_compliance = px.bar(
    compliance_df,
    x="jurisdiction",
    y="asset_count",
    color="compliance_status",
    barmode="group",
    title="Compliance Status by Jurisdiction",
    labels={"asset_count": "Asset Count"},
)
st.plotly_chart(fig_compliance, use_container_width=True)

# Section 4 - Risk and Deadlines
st.subheader("Upcoming Compliance Deadlines")
deadlines_df = day17_query_df("day17_QUERY_upcoming_deadlines.sql")
if selected_jurisdictions:
    deadlines_df = deadlines_df[deadlines_df["jurisdiction"].isin(selected_jurisdictions)]

critical_days = DAY17_DEADLINE_THRESHOLDS_DAYS["critical"]
warning_days = DAY17_DEADLINE_THRESHOLDS_DAYS["warning"]

def day17_urgency_label(days: int) -> str:
    if days <= critical_days:
        return "Critical"
    if days <= warning_days:
        return "Warning"
    return "OK"


deadlines_df["urgency"] = deadlines_df["days_to_deadline"].apply(day17_urgency_label)

st.dataframe(
    deadlines_df.sort_values(["urgency", "days_to_deadline"]),
    use_container_width=True,
)

st.subheader("Point-in-Time Portfolio Composition")
point_df = day17_query_df(
    "day17_QUERY_point_in_time.sql",
    params={"as_of_date": point_in_time_date.isoformat()},
)
st.dataframe(point_df, use_container_width=True)
