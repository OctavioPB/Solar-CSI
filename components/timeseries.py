# -*- coding: utf-8 -*-
"""components/timeseries.py — Installation time series charts."""

import pandas as pd
import plotly.express as px
import streamlit as st

import config


def render(df: pd.DataFrame) -> None:
    st.header("Installations Over Time")

    if df.empty:
        st.warning("No records match the current filters.")
        return

    ts = df.dropna(subset=[config.COL_YEAR_MONTH, config.COL_YEAR]).copy()
    if ts.empty:
        st.warning("No dated records in this selection.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["Monthly Installations", "Cumulative Capacity", "Yearly by Status"]
    )

    with tab1:
        _monthly_installations(ts)

    with tab2:
        _cumulative_capacity(ts)

    with tab3:
        _yearly_by_status(ts)


# ---------------------------------------------------------------------------
# Tab charts
# ---------------------------------------------------------------------------

def _monthly_installations(df: pd.DataFrame) -> None:
    monthly = (
        df.groupby(config.COL_YEAR_MONTH)
        .size()
        .reset_index(name="Installations")
        .sort_values(config.COL_YEAR_MONTH)
    )
    fig = px.bar(
        monthly,
        x=config.COL_YEAR_MONTH,
        y="Installations",
        title="Completed Installations per Month",
        labels={config.COL_YEAR_MONTH: "Month", "Installations": "# Installations"},
    )
    fig.update_layout(xaxis_tickangle=-45, xaxis={"tickmode": "auto", "nticks": 20})
    st.plotly_chart(fig, use_container_width=True)


def _cumulative_capacity(df: pd.DataFrame) -> None:
    cap = (
        df.dropna(subset=[config.COL_NAMEPLATE])
        .groupby(config.COL_YEAR_MONTH)[config.COL_NAMEPLATE]
        .sum()
        .reset_index()
        .sort_values(config.COL_YEAR_MONTH)
    )
    cap["Cumulative MW"] = cap[config.COL_NAMEPLATE].cumsum() / 1_000
    fig = px.area(
        cap,
        x=config.COL_YEAR_MONTH,
        y="Cumulative MW",
        title="Cumulative Installed Capacity (MW)",
        labels={config.COL_YEAR_MONTH: "Month", "Cumulative MW": "MW"},
    )
    fig.update_layout(xaxis_tickangle=-45, xaxis={"tickmode": "auto", "nticks": 20})
    st.plotly_chart(fig, use_container_width=True)


def _yearly_by_status(df: pd.DataFrame) -> None:
    yearly = (
        df.dropna(subset=[config.COL_YEAR, config.COL_STATUS])
        .groupby([config.COL_YEAR, config.COL_STATUS])
        .size()
        .reset_index(name="Count")
    )
    yearly[config.COL_YEAR] = yearly[config.COL_YEAR].astype(int)
    fig = px.bar(
        yearly,
        x=config.COL_YEAR,
        y="Count",
        color=config.COL_STATUS,
        title="Applications by Status per Year",
        labels={config.COL_YEAR: "Year", "Count": "# Applications"},
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)
