# -*- coding: utf-8 -*-
"""components/overview.py — KPI summary cards."""

import pandas as pd
import streamlit as st

import config


def render(df: pd.DataFrame) -> None:
    st.header("Overview")

    if df.empty:
        st.warning("No records match the current filters.")
        return

    # --- Compute KPIs -------------------------------------------------------
    total_apps      = len(df)
    total_capacity  = df[config.COL_NAMEPLATE].sum() / 1_000          # kW → MW
    total_incentive = df[config.COL_INCENTIVE].sum()
    total_cost      = df[config.COL_TOTAL_COST].sum()

    completed = df[config.COL_DATE_COMPLETED].dropna()
    date_min  = completed.min().strftime("%b %Y") if not completed.empty else "—"
    date_max  = completed.max().strftime("%b %Y") if not completed.empty else "—"

    avg_incentive_pct = df[config.COL_INCENTIVE_PCT].dropna().mean()

    # --- Layout: 3 columns × 2 rows -----------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Applications",         f"{total_apps:,}")
    c2.metric("Installed Capacity",         f"{total_capacity:,.1f} MW")
    c3.metric("Total Project Cost",         _fmt_dollars(total_cost))

    c4, c5, c6 = st.columns(3)
    c4.metric("Total Incentives Paid",      _fmt_dollars(total_incentive))
    c5.metric("Avg Incentive / Cost",       f"{avg_incentive_pct:.1f}%" if pd.notna(avg_incentive_pct) else "—")
    c6.metric("Date Range",                 f"{date_min} – {date_max}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_dollars(value: float) -> str:
    """Format a dollar amount as $XM or $XB for readability."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"
