# -*- coding: utf-8 -*-
"""
data/processor.py — Load, clean, and enrich the CSI dataset.

Public interface
----------------
load() -> tuple[pd.DataFrame, pd.DataFrame]
    Returns (df_full, df_filtered).

    df_full     All records that pass basic cleaning (nulls in critical
                columns removed, numerics coerced, dates parsed).
                Used for counts, maps, and leaderboards.

    df_filtered Subset of df_full with outliers removed via z-score on
                Total Cost and Incentive Amount (|z| < ZSCORE_THRESHOLD).
                Used for distribution charts.
"""

import logging

import numpy as np
import pandas as pd
import scipy.stats as st

import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the local CSV and return (df_full, df_filtered)."""
    logger.info("Loading CSV from %s …", config.LOCAL_CSV_PATH)
    raw = pd.read_csv(config.LOCAL_CSV_PATH, low_memory=False)
    logger.info("Raw rows: %d", len(raw))

    df = _coerce_numerics(raw)
    df = _parse_dates(df)
    df = _drop_critical_nulls(df)
    df = _add_derived_columns(df)

    df_full     = df.reset_index(drop=True)
    df_filtered = _remove_outliers(df_full)

    logger.info(
        "Processing complete — df_full: %d rows, df_filtered: %d rows.",
        len(df_full), len(df_filtered),
    )
    return df_full, df_filtered


# ---------------------------------------------------------------------------
# Internal steps
# ---------------------------------------------------------------------------

def _coerce_numerics(df: pd.DataFrame) -> pd.DataFrame:
    for col in config.NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in config.DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _drop_critical_nulls(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    present_critical = [c for c in config.CRITICAL_COLUMNS if c in df.columns]
    df = df.dropna(subset=present_critical)
    logger.info("Dropped %d rows with nulls in critical columns.", before - len(df))
    return df


def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Incentive as a percentage of total cost
    if config.COL_INCENTIVE in df.columns and config.COL_TOTAL_COST in df.columns:
        df[config.COL_INCENTIVE_PCT] = (
            df[config.COL_INCENTIVE] / df[config.COL_TOTAL_COST].replace(0, np.nan)
        ) * 100

    # Year, Month, Year-Month extracted from completion date
    if config.COL_DATE_COMPLETED in df.columns:
        completed = df[config.COL_DATE_COMPLETED]
        df[config.COL_YEAR]       = completed.dt.year
        df[config.COL_MONTH]      = completed.dt.month
        df[config.COL_YEAR_MONTH] = completed.dt.to_period("M").astype(str)

    return df


def _remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows where |z-score| < threshold for all outlier columns."""
    outlier_cols = [c for c in config.OUTLIER_COLUMNS if c in df.columns]
    if not outlier_cols:
        return df

    z_scores     = st.zscore(df[outlier_cols], nan_policy="omit")
    abs_z        = np.abs(z_scores)
    mask         = (abs_z < config.ZSCORE_THRESHOLD).all(axis=1)
    filtered     = df[mask]
    logger.info(
        "Outlier removal: kept %d / %d rows (|z| < %.1f on %s).",
        len(filtered), len(df), config.ZSCORE_THRESHOLD, outlier_cols,
    )
    return filtered.reset_index(drop=True)
