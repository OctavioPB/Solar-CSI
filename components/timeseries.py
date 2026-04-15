# -*- coding: utf-8 -*-
"""components/timeseries.py — Installation time series charts."""

import pandas as pd
import plotly.express as px
import streamlit as st

import config
import styles


def render(df: pd.DataFrame) -> None:
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
        title="Completed installations per month",
        labels={config.COL_YEAR_MONTH: "Month", "Installations": "# Installations"},
        color_discrete_sequence=["#003366"],
    )
    fig.update_layout(**styles.chart_layout(), xaxis_tickangle=-45)
    fig.update_xaxes(tickmode="auto", nticks=20, gridcolor="#E0EAF4")
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
        title="Cumulative installed capacity (MW)",
        labels={config.COL_YEAR_MONTH: "Month", "Cumulative MW": "MW"},
        color_discrete_sequence=["#003366"],
    )
    fig.update_traces(fillcolor="rgba(0,51,102,0.12)", line_color="#003366")
    fig.update_layout(**styles.chart_layout(), xaxis_tickangle=-45)
    fig.update_xaxes(tickmode="auto", nticks=20, gridcolor="#E0EAF4")
    st.plotly_chart(fig, use_container_width=True)


def _yearly_by_status(df: pd.DataFrame) -> None:
    yearly = (
        df.dropna(subset=[config.COL_YEAR, config.COL_STATUS])
        .groupby([config.COL_YEAR, config.COL_STATUS])
        .size()
        .reset_index(name="Count")
    )
    yearly[config.COL_YEAR] = yearly[config.COL_YEAR].astype(int)

    # Semantic color map — status → brand color
    color_map = styles.STATUS_COLORS

    fig = px.bar(
        yearly,
        x=config.COL_YEAR,
        y="Count",
        color=config.COL_STATUS,
        title="Applications by status per year",
        labels={config.COL_YEAR: "Year", "Count": "# Applications"},
        barmode="stack",
        color_discrete_map=color_map,
    )
    fig.update_layout(**styles.chart_layout())
    st.plotly_chart(fig, use_container_width=True)
