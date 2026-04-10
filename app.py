# -*- coding: utf-8 -*-
"""
app.py — California Solar Initiative Dashboard
Run with:  streamlit run app.py
"""

import logging

import streamlit as st

import config
import scheduler
from components import contractors, financials, geo, overview, sectors, timeseries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="California Solar Initiative Dashboard",
    page_icon="☀️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Boot scheduler exactly once per server process
# ---------------------------------------------------------------------------
@st.cache_resource
def _start_scheduler():
    scheduler.start()
    return True

_start_scheduler()

# ---------------------------------------------------------------------------
# Load data from cache
# ---------------------------------------------------------------------------
df_full, df_filtered = scheduler.get_data()

# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("☀️ CSI Dashboard")
    st.markdown("---")

    # -- Outlier toggle -------------------------------------------------------
    show_outliers = st.toggle(
        "Include outliers",
        value=False,
        help="When off, records beyond 1 standard deviation in cost or incentive are excluded.",
    )
    base_df = df_full if show_outliers else df_filtered

    st.markdown("---")
    st.subheader("Filters")

    # -- Year range -----------------------------------------------------------
    valid_years = base_df[config.COL_YEAR].dropna()
    year_min, year_max = int(valid_years.min()), int(valid_years.max())
    year_range = st.slider(
        "Completion year",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )

    # -- County ---------------------------------------------------------------
    all_counties = sorted(base_df[config.COL_COUNTY].dropna().unique().tolist())
    selected_counties = st.multiselect(
        "County",
        options=all_counties,
        default=[],
        placeholder="All counties",
    )

    # -- Sector ---------------------------------------------------------------
    all_sectors = sorted(base_df[config.COL_OWNER_SECTOR].dropna().unique().tolist())
    selected_sectors = st.multiselect(
        "Sector",
        options=all_sectors,
        default=[],
        placeholder="All sectors",
    )

    # -- Application status ---------------------------------------------------
    all_statuses = sorted(base_df[config.COL_STATUS].dropna().unique().tolist())
    selected_statuses = st.multiselect(
        "Application status",
        options=all_statuses,
        default=[],
        placeholder="All statuses",
    )

    # -- Data freshness -------------------------------------------------------
    st.markdown("---")
    refreshed_at = scheduler.last_refreshed()
    if refreshed_at:
        st.caption(f"Data last updated: {refreshed_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.caption("Data not yet loaded.")

    if st.button("🔄 Refresh Now"):
        with st.spinner("Downloading latest data…"):
            scheduler.force_refresh()
        st.success("Data refreshed.")
        st.rerun()

# ---------------------------------------------------------------------------
# Apply filters to base DataFrame
# ---------------------------------------------------------------------------
df = base_df.copy()

df = df[df[config.COL_YEAR].between(year_range[0], year_range[1])]

if selected_counties:
    df = df[df[config.COL_COUNTY].isin(selected_counties)]

if selected_sectors:
    df = df[df[config.COL_OWNER_SECTOR].isin(selected_sectors)]

if selected_statuses:
    df = df[df[config.COL_STATUS].isin(selected_statuses)]

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("California Solar Initiative Dashboard")
st.caption(
    f"Showing **{len(df):,}** records"
    + (f" · outliers included" if show_outliers else "")
    + (f" · {year_range[0]}–{year_range[1]}" if year_range != (year_min, year_max) else "")
)

st.divider()
overview.render(df)

st.divider()
timeseries.render(df)

st.divider()
financials.render(df)

st.divider()
geo.render(df)

st.divider()
sectors.render(df)

st.divider()
contractors.render(df)
