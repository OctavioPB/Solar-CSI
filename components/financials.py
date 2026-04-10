# -*- coding: utf-8 -*-
"""components/financials.py — Cost and incentive distribution charts."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import config


def render(df: pd.DataFrame) -> None:
    st.header("Financials")

    if df.empty:
        st.warning("No records match the current filters.")
        return

    fin = df.dropna(subset=[config.COL_TOTAL_COST, config.COL_INCENTIVE]).copy()
    if fin.empty:
        st.warning("No financial records in this selection.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["Distributions", "Boxplots", "Cost vs Incentive"]
    )

    with tab1:
        _histograms(fin)

    with tab2:
        _boxplots(fin)

    with tab3:
        _scatter(fin)


# ---------------------------------------------------------------------------
# Tab charts
# ---------------------------------------------------------------------------

def _histograms(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x=config.COL_TOTAL_COST,
            nbins=40,
            title="Total Cost Distribution",
            labels={config.COL_TOTAL_COST: "Total Cost (USD)"},
            color_discrete_sequence=["#2ecc71"],
        )
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            df,
            x=config.COL_INCENTIVE,
            nbins=40,
            title="Incentive Amount Distribution",
            labels={config.COL_INCENTIVE: "Incentive Amount (USD)"},
            color_discrete_sequence=["#3498db"],
        )
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)


def _boxplots(df: pd.DataFrame) -> None:
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Total Cost (USD)", "Incentive Amount (USD)"])

    fig.add_trace(
        go.Box(y=df[config.COL_TOTAL_COST], name="Total Cost",
               marker_color="#2ecc71", boxmean=True),
        row=1, col=1,
    )
    fig.add_trace(
        go.Box(y=df[config.COL_INCENTIVE], name="Incentive Amount",
               marker_color="#3498db", boxmean=True),
        row=1, col=2,
    )
    fig.update_layout(title_text="Cost & Incentive Boxplots", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _scatter(df: pd.DataFrame) -> None:
    avg_pct = df[config.COL_INCENTIVE_PCT].dropna().mean()
    st.metric(
        "Average Incentive as % of Total Cost",
        f"{avg_pct:.1f}%" if pd.notna(avg_pct) else "—",
    )

    fig = px.scatter(
        df.dropna(subset=[config.COL_OWNER_SECTOR]),
        x=config.COL_TOTAL_COST,
        y=config.COL_INCENTIVE,
        color=config.COL_OWNER_SECTOR,
        opacity=0.5,
        title="Incentive Amount vs. Total Cost by Sector",
        labels={
            config.COL_TOTAL_COST: "Total Cost (USD)",
            config.COL_INCENTIVE:  "Incentive Amount (USD)",
        },
        hover_data=[config.COL_CONTRACTOR, config.COL_COUNTY],
    )
    fig.update_traces(marker={"size": 4})
    st.plotly_chart(fig, use_container_width=True)
