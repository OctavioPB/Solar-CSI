# -*- coding: utf-8 -*-
"""components/contractors.py — Contractor leaderboard."""

import pandas as pd
import plotly.express as px
import streamlit as st

import config

_DEFAULT_TOP_N = 10
_MAX_TOP_N = 50


def render(df: pd.DataFrame) -> None:
    st.header("Contractor Leaderboard")

    if df.empty:
        st.warning("No records match the current filters.")
        return

    valid = df.dropna(subset=[config.COL_CONTRACTOR])
    if valid.empty:
        st.warning("No contractor data in this selection.")
        return

    top_n = st.slider("Show top N contractors", min_value=5, max_value=_MAX_TOP_N,
                      value=_DEFAULT_TOP_N, step=5)

    tab1, tab2, tab3 = st.tabs(["By Project Count", "By Total Capacity", "By Total Incentive"])

    with tab1:
        _leaderboard(valid, metric="count", top_n=top_n)

    with tab2:
        _leaderboard(valid, metric="capacity", top_n=top_n)

    with tab3:
        _leaderboard(valid, metric="incentive", top_n=top_n)


# ---------------------------------------------------------------------------
# Shared leaderboard renderer
# ---------------------------------------------------------------------------

def _leaderboard(df: pd.DataFrame, metric: str, top_n: int) -> None:
    agg = (
        df.groupby(config.COL_CONTRACTOR)
        .agg(
            Projects=(config.COL_APPLICATION, "count"),
            Capacity_kW=(config.COL_NAMEPLATE, "sum"),
            Total_Incentive=(config.COL_INCENTIVE, "sum"),
            Total_Cost=(config.COL_TOTAL_COST, "sum"),
        )
        .reset_index()
    )
    agg["Capacity (MW)"] = (agg["Capacity_kW"] / 1_000).round(3)
    agg["Total Incentive ($)"] = agg["Total_Incentive"].round(0).astype(int)
    agg["Total Cost ($)"] = agg["Total_Cost"].round(0).astype(int)
    agg = agg.rename(columns={config.COL_CONTRACTOR: "Contractor"})

    sort_col, bar_col, bar_label = {
        "count":     ("Projects",         "Projects",        "# Projects"),
        "capacity":  ("Capacity (MW)",    "Capacity (MW)",   "Capacity (MW)"),
        "incentive": ("Total Incentive ($)", "Total Incentive ($)", "Total Incentive (USD)"),
    }[metric]

    top = agg.nlargest(top_n, sort_col).sort_values(sort_col, ascending=True)

    fig = px.bar(
        top,
        x=bar_col,
        y="Contractor",
        orientation="h",
        title=f"Top {top_n} Contractors — {bar_label}",
        text=top[bar_col].apply(lambda v: _fmt(v, metric)),
        color=bar_col,
        color_continuous_scale="Blues",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        yaxis_title="",
        height=max(350, top_n * 30),
    )
    st.plotly_chart(fig, use_container_width=True)

    display_cols = ["Contractor", "Projects", "Capacity (MW)", "Total Incentive ($)", "Total Cost ($)"]
    st.dataframe(
        top[display_cols].sort_values(sort_col, ascending=False).reset_index(drop=True),
        use_container_width=True,
        column_config={
            "Total Incentive ($)": st.column_config.NumberColumn(format="$%d"),
            "Total Cost ($)":      st.column_config.NumberColumn(format="$%d"),
            "Capacity (MW)":       st.column_config.NumberColumn(format="%.3f MW"),
        },
    )


def _fmt(value: float, metric: str) -> str:
    if metric == "count":
        return f"{int(value):,}"
    if metric == "capacity":
        return f"{value:.2f} MW"
    return f"${value:,.0f}"
