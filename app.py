# -*- coding: utf-8 -*-
"""
app.py — California Solar Initiative Dashboard
Run with:  streamlit run app.py
"""

import logging

import pandas as pd
import streamlit as st

import config
import scheduler
from components import contractors, financials, geo, overview, sectors, timeseries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="California Solar Initiative Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Boot scheduler exactly once per server process
# ---------------------------------------------------------------------------
@st.cache_resource
def _start_scheduler():
    scheduler.start()
    return True

with st.spinner("Loading data…"):
    _start_scheduler()

# ---------------------------------------------------------------------------
# Load data from shared cache
# ---------------------------------------------------------------------------
df_full, df_filtered = scheduler.get_data()

if df_full is None or df_filtered is None:
    st.error(
        "Data could not be loaded. Check that `WorkingDataSet.csv` exists "
        "in the project directory and restart the app."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("☀️ CSI Dashboard")

    # -- Download error banner ------------------------------------------------
    err = scheduler.last_error()
    if err:
        st.warning(
            f"Last data refresh failed — showing cached data.\n\n`{err}`",
            icon="⚠️",
        )

    st.markdown("---")

    # -- Outlier toggle -------------------------------------------------------
    show_outliers = st.toggle(
        "Include outliers",
        value=False,
        help="When off, records beyond 1 standard deviation in cost or "
             "incentive are excluded from all charts.",
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

    # -- Data freshness + manual refresh --------------------------------------
    st.markdown("---")
    refreshed_at = scheduler.last_refreshed()
    if refreshed_at:
        st.caption(f"Data last updated: {refreshed_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.caption("Data not yet loaded.")

    if st.button("🔄 Refresh Now", use_container_width=True):
        with st.spinner("Checking for latest data…"):
            scheduler.force_refresh()
        if scheduler.last_error():
            st.error("Refresh failed. Using existing local data.")
        else:
            st.success("Data refreshed.")
        st.rerun()

    st.markdown("---")
    st.caption(
        "Source: [CA Solar Statistics](https://www.californiasolarstatistics.ca.gov/) · "
        "Program closed ~2019"
    )

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
@st.cache_data
def _apply_filters(
    base_hash: int,
    year_range: tuple,
    counties: list,
    sectors_sel: list,
    statuses: list,
) -> pd.DataFrame:
    """Cache the filter result keyed on the base DataFrame hash + filter values."""
    df = base_df.copy()
    df = df[df[config.COL_YEAR].between(year_range[0], year_range[1])]
    if counties:
        df = df[df[config.COL_COUNTY].isin(counties)]
    if sectors_sel:
        df = df[df[config.COL_OWNER_SECTOR].isin(sectors_sel)]
    if statuses:
        df = df[df[config.COL_STATUS].isin(statuses)]
    return df

df = _apply_filters(
    id(base_df),
    year_range,
    selected_counties,
    selected_sectors,
    selected_statuses,
)

# ---------------------------------------------------------------------------
# Empty-result guard
# ---------------------------------------------------------------------------
if df.empty:
    st.warning("No records match the current filters. Try broadening your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("California Solar Initiative Dashboard")

active_filters = []
if year_range != (year_min, year_max):
    active_filters.append(f"{year_range[0]}–{year_range[1]}")
if selected_counties:
    active_filters.append(", ".join(selected_counties))
if selected_sectors:
    active_filters.append(", ".join(selected_sectors))
if selected_statuses:
    active_filters.append(", ".join(selected_statuses))
if show_outliers:
    active_filters.append("outliers included")

filter_text = " · ".join(active_filters) if active_filters else "all records"
st.caption(f"Showing **{len(df):,}** of **{len(base_df):,}** records · {filter_text}")

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
