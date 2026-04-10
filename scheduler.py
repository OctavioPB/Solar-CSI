# -*- coding: utf-8 -*-
"""
scheduler.py — Background data refresh using APScheduler.

The scheduler loads the DataFrames once at startup, then re-runs the full
download + process pipeline every REFRESH_INTERVAL_HOURS hours.
All writes to the shared cache are protected by a threading.Lock so that
Streamlit reader threads never see a partial update.

Public interface
----------------
start()           Boot the scheduler and perform the initial data load.
                  Safe to call multiple times — subsequent calls are no-ops.
get_data()        Return (df_full, df_filtered) from the cache.
last_refreshed()  Return the datetime of the last successful refresh.
force_refresh()   Trigger an immediate download + reload outside the schedule.
"""

import logging
import threading
from datetime import datetime

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

import config
from data import loader, processor

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cache (shared across all Streamlit sessions)
# ---------------------------------------------------------------------------
_lock: threading.Lock              = threading.Lock()
_df_full: pd.DataFrame | None      = None
_df_filtered: pd.DataFrame | None  = None
_last_refreshed: datetime | None   = None
_last_error: str | None            = None
_scheduler: BackgroundScheduler | None = None


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the scheduler and load data on first call. No-op on re-entry."""
    global _scheduler
    if _scheduler is not None:
        return

    logger.info("Performing initial data load …")
    _do_refresh()

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _do_refresh,
        trigger="interval",
        hours=config.REFRESH_INTERVAL_HOURS,
        id="csi_refresh",
    )
    _scheduler.start()
    logger.info(
        "Scheduler started — next auto-refresh in %d hour(s).",
        config.REFRESH_INTERVAL_HOURS,
    )


def get_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (df_full, df_filtered). Thread-safe."""
    with _lock:
        return _df_full, _df_filtered


def last_refreshed() -> datetime | None:
    """Return the datetime of the most recent successful refresh."""
    return _last_refreshed


def last_error() -> str | None:
    """Return the error message from the most recent failed refresh, or None."""
    return _last_error


def force_refresh() -> None:
    """Immediately re-download (if stale) and reload the DataFrames."""
    logger.info("Manual refresh triggered.")
    _do_refresh()


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _do_refresh() -> None:
    global _df_full, _df_filtered, _last_refreshed, _last_error
    try:
        loader.download_if_stale()
        df_full, df_filtered = processor.load()
        with _lock:
            _df_full        = df_full
            _df_filtered    = df_filtered
            _last_refreshed = datetime.now()
            _last_error     = None
        logger.info("Cache refreshed at %s — %d rows.", _last_refreshed, len(df_full))
    except Exception as exc:
        _last_error = str(exc)
        logger.error("Refresh failed: %s", exc, exc_info=True)
