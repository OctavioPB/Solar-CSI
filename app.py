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
import styles
from components import contractors, financials, geo, overview, sectors, timeseries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CSI Dashboard · OPB",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Brand injection (second call — before any visible output)
# ---------------------------------------------------------------------------
styles.inject_brand()

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
        "Data could not be loaded. Ensure `WorkingDataSet.csv` exists in the "
        "project root and restart the app."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.html(
        "<p style='font-family:Fraunces,Georgia,serif; font-size:22px; "
        "color:white; letter-spacing:-0.5px; margin:8px 0 4px;'>"
        "O<em style='color:#E8C46A;'>PB</em></p>"
        "<p style='font-family:Plus Jakarta Sans,sans-serif; font-size:9px; "
        "letter-spacing:3px; text-transform:uppercase; "
        "color:rgba(255,255,255,0.4); margin:0 0 12px;'>CSI Analysis</p>"
    )

    # -- Download error banner -----------------------------------------------
    err = scheduler.last_error()
    if err:
        st.warning(f"Last refresh failed — using cached data.\n\n`{err}`", icon="⚠️")

    st.markdown("---")

    # -- Outlier toggle -------------------------------------------------------
    show_outliers = st.toggle(
        "Include outliers",
        value=False,
        help="When off, records with |z-score| > 1 on cost or incentive are excluded.",
    )
    base_df = df_full if show_outliers else df_filtered

    st.markdown("---")
    st.markdown(
        "<p style='font-family:Plus Jakarta Sans,sans-serif; font-size:9px; "
        "letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.4); "
        "margin:0 0 12px;'>Filters</p>",
        unsafe_allow_html=True,
    )

    # -- Year range ----------------------------------------------------------
    valid_years = base_df[config.COL_YEAR].dropna()
    year_min, year_max = int(valid_years.min()), int(valid_years.max())
    year_range = st.slider("Completion year", min_value=year_min,
                           max_value=year_max, value=(year_min, year_max))

    # -- County --------------------------------------------------------------
    all_counties = sorted(base_df[config.COL_COUNTY].dropna().unique().tolist())
    selected_counties = st.multiselect("County", options=all_counties,
                                       default=[], placeholder="All counties")

    # -- Sector --------------------------------------------------------------
    all_sectors = sorted(base_df[config.COL_OWNER_SECTOR].dropna().unique().tolist())
    selected_sectors = st.multiselect("Sector", options=all_sectors,
                                      default=[], placeholder="All sectors")

    # -- Status --------------------------------------------------------------
    all_statuses = sorted(base_df[config.COL_STATUS].dropna().unique().tolist())
    selected_statuses = st.multiselect("Application status", options=all_statuses,
                                       default=[], placeholder="All statuses")

    # -- Refresh + timestamp -------------------------------------------------
    st.markdown("---")
    refreshed_at = scheduler.last_refreshed()
    if refreshed_at:
        st.caption(f"Updated: {refreshed_at.strftime('%Y-%m-%d %H:%M')}")

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
        "[californiasolarstatistics.ca.gov](https://www.californiasolarstatistics.ca.gov/) "
        "· Program closed 2019"
    )

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
@st.cache_data
def _apply_filters(base_id, year_range, counties, sectors_sel, statuses):
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
    id(base_df), year_range, selected_counties, selected_sectors, selected_statuses
)

if df.empty:
    st.warning("No records match the current filters. Try broadening your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
styles.navbar()
styles.hero(
    subtitle=(
        f"Showing <strong>{len(df):,}</strong> of <strong>{len(base_df):,}</strong> "
        f"records &nbsp;·&nbsp; {year_range[0]}–{year_range[1]} &nbsp;·&nbsp; "
        f"{'Outliers included' if show_outliers else 'Outliers excluded'}"
    )
)

# -- 01 Overview -------------------------------------------------------------
styles.section_eyebrow("01 · Overview")
styles.section_title("Program at a glance", emphasis="glance")
styles.section_divider()
overview.render(df)

# -- 02 Time Series ----------------------------------------------------------
styles.section_eyebrow("02 · Time Series")
styles.section_title("Installations over time", emphasis="time")
styles.section_divider()
timeseries.render(df)

# -- 03 Financials -----------------------------------------------------------
styles.section_eyebrow("03 · Financials")
styles.section_title("Cost & incentive distribution", emphasis="incentive")
styles.section_divider()
financials.render(df)

# -- 04 Geography ------------------------------------------------------------
styles.section_eyebrow("04 · Geography")
styles.section_title("Regional deployment", emphasis="deployment")
styles.section_divider()
geo.render(df)

# -- 05 Sectors --------------------------------------------------------------
styles.section_eyebrow("05 · Sectors")
styles.section_title("Sector breakdown", emphasis="breakdown")
styles.section_divider()
sectors.render(df)

# -- 06 Contractors ----------------------------------------------------------
styles.section_eyebrow("06 · Contractors")
styles.section_title("Contractor leaderboard", emphasis="leaderboard")
styles.section_divider()
contractors.render(df)

# -- Footer ------------------------------------------------------------------
st.html(
    "<div style='background:#003366; border-radius:12px; "
    "padding:24px 40px; margin-top:64px; display:flex; justify-content:space-between; "
    "align-items:center;'>"
    "<span style='font-family:Fraunces,Georgia,serif; font-size:18px; color:white;'>"
    "O<em style='color:#E8C46A;'>PB</em></span>"
    "<span style='font-family:Plus Jakarta Sans,sans-serif; font-size:9px; "
    "letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.4);'>"
    "Octavio Pérez Bravo &nbsp;·&nbsp; Data &amp; AI Strategy &nbsp;·&nbsp; "
    "California Solar Initiative</span>"
    "</div>"
)
