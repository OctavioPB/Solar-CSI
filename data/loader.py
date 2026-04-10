# -*- coding: utf-8 -*-
"""
data/loader.py — CSV download with stale-check and local fallback.

Public interface
----------------
download_if_stale()   Check the remote file's Last-Modified header; download
                      only when the local CSV is older. Falls back silently to
                      the existing local file on any network error.

last_updated()        Return the modification datetime of the local CSV, or
                      None if it does not exist.
"""

import io
import logging
import os
import zipfile
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests

import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def last_updated() -> datetime | None:
    """Return the mtime of the local CSV, or None if it does not exist."""
    if os.path.exists(config.LOCAL_CSV_PATH):
        return datetime.fromtimestamp(os.path.getmtime(config.LOCAL_CSV_PATH))
    return None


def download_if_stale() -> bool:
    """
    Download the remote CSV only when it is newer than the local copy.

    Returns True if a fresh file was downloaded, False otherwise.
    Falls back to the existing local file on any network or parsing error.
    """
    local_mtime = last_updated()

    try:
        remote_mtime = _get_remote_mtime()
    except Exception as exc:
        logger.warning("Could not reach remote source: %s — using local file.", exc)
        return False

    if local_mtime and remote_mtime and remote_mtime <= local_mtime:
        logger.info("Local CSV is up to date (local: %s, remote: %s).", local_mtime, remote_mtime)
        return False

    logger.info("Downloading fresh CSV from %s …", config.CSI_DOWNLOAD_URL)
    try:
        _download_csv()
        logger.info("Download complete. Local CSV updated.")
        return True
    except Exception as exc:
        logger.error("Download failed: %s — keeping existing local file.", exc)
        return False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_remote_mtime() -> datetime | None:
    """
    Issue a HEAD request and parse the Last-Modified header.
    Returns None if the header is absent.
    """
    response = requests.head(config.CSI_DOWNLOAD_URL, timeout=10, allow_redirects=True)
    response.raise_for_status()
    last_modified = response.headers.get("Last-Modified")
    if last_modified:
        return parsedate_to_datetime(last_modified)
    return None


def _download_csv() -> None:
    """
    Download the remote file, unzip if necessary, and write the CSV to
    LOCAL_CSV_PATH. Supports both raw .csv and .zip responses.
    """
    response = requests.get(config.CSI_DOWNLOAD_URL, timeout=120, stream=True)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    raw_bytes = response.content

    if "zip" in content_type or config.CSI_DOWNLOAD_URL.endswith(".zip"):
        raw_bytes = _extract_csv_from_zip(raw_bytes)

    with open(config.LOCAL_CSV_PATH, "wb") as f:
        f.write(raw_bytes)


def _extract_csv_from_zip(zip_bytes: bytes) -> bytes:
    """Return the contents of the first .csv file found inside a zip archive."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError("No CSV file found inside the downloaded zip archive.")
        # Pick the largest CSV if there are multiple (usually the all-data file)
        csv_name = max(csv_names, key=lambda n: zf.getinfo(n).file_size)
        logger.info("Extracting '%s' from zip archive.", csv_name)
        return zf.read(csv_name)
