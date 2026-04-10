# -*- coding: utf-8 -*-
"""components/geo.py — Geographic breakdown charts."""

import pandas as pd
import plotly.express as px
import streamlit as st

import config

_DEFAULT_TOP_N = 10


def render(df: pd.DataFrame) -> None:
    st.header("Geographic Breakdown")

    if df.empty:
        st.warning("No records match the current filters.")
        return

    tab1, tab2 = st.tabs(["By City", "By County"])

    with tab1:
        _city_chart(df)

    with tab2:
        _county_chart(df)


# ---------------------------------------------------------------------------
# Tab charts
# ---------------------------------------------------------------------------

def _city_chart(df: pd.DataFrame) -> None:
    top_n = st.slider("Top N cities", min_value=5, max_value=30,
                      value=_DEFAULT_TOP_N, step=5, key="city_slider")

    city_agg = (
        df.dropna(subset=[config.COL_CITY])
        .groupby(config.COL_CITY)
        .agg(
            Installations=(config.COL_APPLICATION, "count"),
            Capacity_MW=(config.COL_NAMEPLATE, lambda x: x.sum() / 1_000),
            Avg_Cost=(config.COL_TOTAL_COST, "mean"),
        )
        .reset_index()
        .nlargest(top_n, "Installations")
        .sort_values("Installations", ascending=True)
        .rename(columns={config.COL_CITY: "City"})
    )

    fig = px.bar(
        city_agg,
        x="Installations",
        y="City",
        orientation="h",
        title=f"Top {top_n} Cities by Installation Count",
        text="Installations",
        color="Capacity_MW",
        color_continuous_scale="YlOrRd",
        hover_data={"Avg_Cost": ":$,.0f", "Capacity_MW": ":.2f"},
        labels={"Capacity_MW": "Capacity (MW)", "Avg_Cost": "Avg Cost (USD)"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis_title="",
        coloraxis_colorbar_title="MW",
        height=max(350, top_n * 30),
    )
    st.plotly_chart(fig, use_container_width=True)


def _county_chart(df: pd.DataFrame) -> None:
    county_agg = (
        df.dropna(subset=[config.COL_COUNTY])
        .groupby(config.COL_COUNTY)
        .agg(
            Installations=(config.COL_APPLICATION, "count"),
            Capacity_MW=(config.COL_NAMEPLATE, lambda x: x.sum() / 1_000),
            Total_Incentive=(config.COL_INCENTIVE, "sum"),
        )
        .reset_index()
        .sort_values("Installations", ascending=False)
        .rename(columns={config.COL_COUNTY: "County"})
    )
    county_agg["Total Incentive ($M)"] = (county_agg["Total_Incentive"] / 1_000_000).round(2)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            county_agg.sort_values("Installations", ascending=True),
            x="Installations",
            y="County",
            orientation="h",
            title="Installations by County",
            text="Installations",
            color="Installations",
            color_continuous_scale="Blues",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            yaxis_title="",
            coloraxis_showscale=False,
            height=max(400, len(county_agg) * 28),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            county_agg.sort_values("Capacity_MW", ascending=True),
            x="Capacity_MW",
            y="County",
            orientation="h",
            title="Installed Capacity by County (MW)",
            text=county_agg.sort_values("Capacity_MW", ascending=True)["Capacity_MW"].apply(
                lambda v: f"{v:.1f} MW"
            ),
            color="Capacity_MW",
            color_continuous_scale="Oranges",
            hover_data={"Total Incentive ($M)": True},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            yaxis_title="",
            xaxis_title="MW",
            coloraxis_showscale=False,
            height=max(400, len(county_agg) * 28),
        )
        st.plotly_chart(fig, use_container_width=True)
