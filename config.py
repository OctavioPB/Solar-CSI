# -*- coding: utf-8 -*-
"""
config.py — Central configuration for the CSI Dashboard.
Update CSI_DOWNLOAD_URL if the CPUC changes the file location.
"""

import os

# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------
# TODO: verify URL against californiasolarstatistics.ca.gov/data_downloads/
CSI_DOWNLOAD_URL = (
    "https://www.californiasolarstatistics.ca.gov/"
    "wp-content/uploads/DataFiles/CSIFiles/CSI_AllData.zip"
)

# Path to the local CSV (used as seed data and download target)
LOCAL_CSV_PATH = os.path.join(os.path.dirname(__file__), "WorkingDataSet.csv")

# How often to check for a fresher file (hours)
REFRESH_INTERVAL_HOURS = 24

# ---------------------------------------------------------------------------
# Column names (exact strings from the CSV header)
# ---------------------------------------------------------------------------
COL_APPLICATION      = "Application Number"
COL_PROGRAM_ADMIN    = "Program Administrator"
COL_PROGRAM          = "Program"
COL_INCENTIVE        = "Incentive Amount"
COL_TOTAL_COST       = "Total Cost"
COL_NAMEPLATE        = "Nameplate Rating"
COL_CEC_PTC          = "CEC PTC Rating"
COL_DESIGN_FACTOR    = "Design Factor"
COL_CSI_RATING       = "CSI Rating"
COL_STATUS           = "Current Incentive Application Status"
COL_OWNER_SECTOR     = "System Owner Sector"
COL_CUSTOMER_SECTOR  = "Host Customer Sector"
COL_CITY             = "Host Customer Physical Address City"
COL_COUNTY           = "Host Customer Physical Address County"
COL_STATE            = "Host Customer Physical Address State"
COL_ZIP              = "Host Customer Physical Zip Code"
COL_DATE_RESERVED    = "First Confirmed Reservation Date"
COL_DATE_COMPLETED   = "First Completed Date"
COL_CONTRACTOR       = "Solar Contractor Company Name"
COL_LICENSE          = "Contractor License Number"
COL_SELLER           = "Seller Company Name"
COL_THIRD_PARTY      = "3rd Party Owner"
COL_PBI_BUYOUT       = "Is a PBI Buyout Application"
COL_MODULE_QTY       = "PV Module#1 Quantity"
COL_INSTALLED_STATUS = "Installed Status"
COL_PAYMENT_STATUS   = "Completed/PBI-In Payment Status"
COL_TILT             = "CSI Project Tilt"
COL_CEC_PTC_FIXED    = "CEC PTC Rating Fixed"
COL_CSI_RATING_FIXED = "CSI Rating Fixed"

# ---------------------------------------------------------------------------
# Derived column names (added by processor.py)
# ---------------------------------------------------------------------------
COL_INCENTIVE_PCT = "Incentive %"
COL_YEAR          = "Year"
COL_MONTH         = "Month"
COL_YEAR_MONTH    = "Year-Month"

# ---------------------------------------------------------------------------
# Column groups used across the pipeline
# ---------------------------------------------------------------------------
NUMERIC_COLUMNS = [
    COL_INCENTIVE, COL_TOTAL_COST, COL_NAMEPLATE,
    COL_CEC_PTC, COL_DESIGN_FACTOR, COL_CSI_RATING,
    COL_MODULE_QTY, COL_TILT, COL_CEC_PTC_FIXED, COL_CSI_RATING_FIXED,
]

DATE_COLUMNS = [COL_DATE_RESERVED, COL_DATE_COMPLETED]

# Records missing any of these columns are dropped in df_full
CRITICAL_COLUMNS = [COL_INCENTIVE, COL_TOTAL_COST]

# ---------------------------------------------------------------------------
# Outlier filtering (z-score, applied to df_filtered only)
# ---------------------------------------------------------------------------
ZSCORE_THRESHOLD  = 1.0
OUTLIER_COLUMNS   = [COL_TOTAL_COST, COL_INCENTIVE]
