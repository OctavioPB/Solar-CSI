# -*- coding: utf-8 -*-
"""components/sectors.py — Sector analysis charts."""

import pandas as pd
import plotly.express as px
import streamlit as st

import config
import styles


def render(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No records match the current filters.")
        return

    tab1, tab2 = st.tabs(["Sector Breakdown", "Average System Size"])
    with tab1:
        _sector_pies(df)
    with tab2:
        _avg_system_size(df)


def _sector_pies(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        owner = df[config.COL_OWNER_SECTOR].dropna().value_counts().reset_index()
        owner.columns = ["Sector", "Count"]
        fig = px.pie(
            owner,
            names="Sector",
            values="Count",
            title="System owner sector",
            hole=0.45,
            color_discrete_sequence=styles.BRAND_COLORS,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          textfont=dict(family="Plus Jakarta Sans, sans-serif", size=11))
        fig.update_layout(**styles.chart_layout())
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        customer = df[config.COL_CUSTOMER_SECTOR].dropna().value_counts().reset_index()
        customer.columns = ["Sector", "Count"]
        fig = px.pie(
            customer,
            names="Sector",
            values="Count",
            title="Host customer sector",
            hole=0.45,
            color_discrete_sequence=styles.BRAND_COLORS,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          textfont=dict(family="Plus Jakarta Sans, sans-serif", size=11))
        fig.update_layout(**styles.chart_layout())
        st.plotly_chart(fig, use_container_width=True)


def _avg_system_size(df: pd.DataFrame) -> None:
    agg = (
        df.dropna(subset=[config.COL_OWNER_SECTOR, config.COL_NAMEPLATE])
        .groupby(config.COL_OWNER_SECTOR)
        .agg(
            avg_kw=(config.COL_NAMEPLATE, "mean"),
            median_kw=(config.COL_NAMEPLATE, "median"),
            count=(config.COL_NAMEPLATE, "count"),
        )
        .reset_index()
        .sort_values("avg_kw", ascending=True)
    )
    agg.columns = ["Sector", "Avg (kW)", "Median (kW)", "# Systems"]

    fig = px.bar(
        agg,
        x="Avg (kW)",
        y="Sector",
        orientation="h",
        title="Average installed system size by sector (kW)",
        text=agg["Avg (kW)"].apply(lambda v: f"{v:,.1f} kW"),
        color="Sector",
        color_discrete_sequence=styles.BRAND_COLORS,
        hover_data=["Median (kW)", "# Systems"],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        **styles.chart_layout(),
        showlegend=False,
        xaxis_title="kW",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)
