# -*- coding: utf-8 -*-
"""components/overview.py — KPI summary cards."""

import pandas as pd
import streamlit as st

import config

_CARD = """
<div style="
    background: #FFFFFF;
    border-radius: 12px;
    padding: 28px 28px 24px;
    box-shadow: 0 1px 6px rgba(0,51,102,0.08);
    position: relative;
    overflow: hidden;
    height: 100%;
">
    <div style="
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #003366, #C8982A);
        border-radius: 12px 12px 0 0;
    "></div>
    <p style="
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 10px; font-weight: 500;
        text-transform: uppercase; letter-spacing: 2px;
        color: #6B7280; margin: 0 0 10px 0;
    ">{label}</p>
    <p style="
        font-family: 'Fraunces', Georgia, serif;
        font-size: 32px; font-weight: 300;
        color: #1C1C2E; margin: 0; line-height: 1.1;
    ">{value}</p>
</div>
"""


def render(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No records match the current filters.")
        return

    total_apps        = len(df)
    total_capacity    = df[config.COL_NAMEPLATE].sum() / 1_000
    total_incentive   = df[config.COL_INCENTIVE].sum()
    total_cost        = df[config.COL_TOTAL_COST].sum()
    avg_incentive_pct = df[config.COL_INCENTIVE_PCT].dropna().mean()

    completed = df[config.COL_DATE_COMPLETED].dropna()
    date_min  = completed.min().strftime("%b %Y") if not completed.empty else "—"
    date_max  = completed.max().strftime("%b %Y") if not completed.empty else "—"

    kpis = [
        ("Total Applications",  f"{total_apps:,}"),
        ("Installed Capacity",  f"{total_capacity:,.1f} MW"),
        ("Total Project Cost",  _fmt_dollars(total_cost)),
        ("Total Incentives Paid", _fmt_dollars(total_incentive)),
        ("Avg Incentive / Cost",  f"{avg_incentive_pct:.1f}%" if pd.notna(avg_incentive_pct) else "—"),
        ("Date Range",            f"{date_min} – {date_max}"),
    ]

    cols = st.columns(3)
    for i, (label, value) in enumerate(kpis):
        with cols[i % 3]:
            st.html(_CARD.format(label=label, value=value))


def _fmt_dollars(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"
