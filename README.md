# California Solar Initiative Dashboard

An interactive analytics dashboard for the **California Solar Initiative (CSI)** program — a $2.17 billion CPUC incentive program that ran from 2007 to 2019. The dashboard visualizes ~23,500 solar installations across Southern California, covering financial distributions, time series trends, geographic breakdowns, sector analysis, and contractor leaderboards.

Built with **Streamlit** and **Plotly**. Data refreshes automatically in the background from the California Solar Statistics website.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Using the Dashboard](#using-the-dashboard)
- [Data Pipeline](#data-pipeline)
- [Auto-Update Behavior](#auto-update-behavior)
- [Configuration](#configuration)
- [Dataset](#dataset)
- [Troubleshooting](#troubleshooting)

---

## Features

| Section | What it shows |
|---|---|
| **Overview** | KPI cards — total applications, installed capacity (MW), total project cost, total incentives paid, average incentive %, date range |
| **Installations Over Time** | Monthly completions (bar), cumulative capacity (area), yearly breakdown by application status (stacked bar) |
| **Financials** | Total Cost and Incentive Amount distributions (histograms + boxplots), cost vs. incentive scatter plot colored by sector |
| **Geographic Breakdown** | Top N cities by installation count, county-level installations and capacity side by side |
| **Sector Analysis** | Donut charts for System Owner and Host Customer sectors, average system size (kW) per sector |
| **Contractor Leaderboard** | Top N contractors ranked by project count, total installed capacity, or total incentive value — with sortable data table |

**Sidebar controls:**

- Outlier toggle — include or exclude statistical outliers (z-score > 1 on cost/incentive)
- Completion year range slider
- County multi-select
- Sector multi-select
- Application status filter
- Manual "Refresh Now" button + last-updated timestamp

---

## Project Structure

```
Solar-CSI/
│
├── app.py                      # Streamlit entry point
├── config.py                   # All constants: column names, URLs, thresholds
├── scheduler.py                # APScheduler background refresh + thread-safe cache
├── requirements.txt            # Pinned dependencies
│
├── data/
│   ├── loader.py               # CSV download with stale-check and zip extraction
│   └── processor.py            # Cleaning pipeline → df_full and df_filtered
│
├── components/
│   ├── overview.py             # KPI cards
│   ├── timeseries.py           # Time series charts (3 tabs)
│   ├── financials.py           # Distribution charts (3 tabs)
│   ├── geo.py                  # Geographic charts (2 tabs)
│   ├── sectors.py              # Sector analysis (2 tabs)
│   └── contractors.py          # Contractor leaderboard (3 tabs)
│
└── WorkingDataSet.csv          # Seed dataset (CSI all-data extract)
```

---

## Requirements

- **Python 3.11+**
- Dependencies listed in `requirements.txt`:

| Package | Version | Purpose |
|---|---|---|
| streamlit | 1.56.0 | Web framework and UI |
| plotly | 6.7.0 | Interactive charts |
| APScheduler | 3.11.2 | Background data refresh |
| pandas | 3.0.1 | Data processing |
| numpy | 2.3.5 | Numerical operations |
| scipy | 1.17.1 | Z-score outlier detection |
| requests | 2.32.5 | CSV download |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Solar-CSI.git
cd Solar-CSI
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify the seed dataset is present

`WorkingDataSet.csv` must exist in the project root. It is the seed data file used when no internet connection is available. If it is missing, download it from [californiasolarstatistics.ca.gov](https://www.californiasolarstatistics.ca.gov/data_downloads/) and place it in the project root as `WorkingDataSet.csv`.

---

## Running the App

```bash
streamlit run app.py
```

Streamlit will print a local URL (default: `http://localhost:8501`). Open it in your browser.

On first launch the app will:
1. Attempt to download the latest CSV from the CPUC website
2. Fall back to `WorkingDataSet.csv` if the download fails (no internet, URL change, etc.)
3. Clean and process the data
4. Start a background scheduler that repeats the download check every 24 hours

---

## Using the Dashboard

### Sidebar filters

All filters are applied globally — every section of the dashboard updates simultaneously.

| Control | Description |
|---|---|
| **Include outliers** toggle | Off by default. When off, records with a z-score > 1 on Total Cost or Incentive Amount are excluded. Affects distribution charts most visibly. |
| **Completion year** slider | Filters records by the year the installation was completed (`First Completed Date`). Range: 2007–2019. |
| **County** multi-select | Restrict to one or more of the 20 counties in the dataset. Leave blank for all counties. |
| **Sector** multi-select | Filter by system owner sector: Residential, Commercial, Government, Non-Profit. |
| **Application status** filter | Filter by final application status: Completed, Cancelled, Wait List, Withdrawn, etc. |

### Refresh button

The **🔄 Refresh Now** button in the sidebar triggers an immediate check against the remote source. If the remote file is newer than the local copy it will be downloaded and the data reloaded. If the refresh fails (network error, URL change), a warning banner appears and the existing cached data continues to be shown.

### Record count

The subtitle below the page title always shows how many records are currently visible vs. the total, along with a summary of active filters:

```
Showing 6,735 of 22,946 records · San Diego · 2010–2015
```

### Contractor leaderboard

Use the **Top N** slider (5–50) to control how many contractors appear in the chart and table. Switch between the three tabs to rank by project count, total installed capacity (MW), or total incentive value ($).

### Geographic breakdown

The **By City** tab has its own slider to control how many cities to display. The **By County** tab always shows all counties present in the current filter selection.

---

## Data Pipeline

```
WorkingDataSet.csv (or fresh download)
        │
        ▼
  data/loader.py
  ┌─────────────────────────────────────────┐
  │ HEAD request → check Last-Modified      │
  │ Download only if remote is newer        │
  │ Unzip if .zip response                  │
  │ Fallback to local file on any error     │
  └─────────────────────────────────────────┘
        │
        ▼
  data/processor.py
  ┌─────────────────────────────────────────┐
  │ Coerce numeric columns                  │
  │ Parse date columns                      │
  │ Drop rows missing Incentive / Cost      │
  │ Add derived columns:                    │
  │   Incentive %  = Incentive / Cost × 100 │
  │   Year, Month, Year-Month               │
  │                                         │
  │ → df_full     (all cleaned records)     │
  │ → df_filtered (outliers removed,        │
  │                |z-score| < 1.0)         │
  └─────────────────────────────────────────┘
        │
        ▼
  scheduler.py  (thread-safe module cache)
        │
        ▼
  app.py  (sidebar filters → df)
        │
        ▼
  components/*  (each receives the filtered df)
```

**Two DataFrames are always maintained:**

| DataFrame | Records | Used for |
|---|---|---|
| `df_full` | ~23,504 | Counts, maps, leaderboards, sector breakdowns |
| `df_filtered` | ~22,946 | Financial distributions, boxplots, histograms |

The **Include outliers** toggle in the sidebar selects which one becomes the base before user filters are applied.

---

## Auto-Update Behavior

The scheduler runs in a daemon background thread (will not block app shutdown):

1. **On startup** — immediately attempts `download_if_stale()`
2. **Every 24 hours** — repeats the check automatically
3. **On manual trigger** — the "Refresh Now" button calls `force_refresh()`

The stale-check issues an HTTP `HEAD` request to compare the remote `Last-Modified` header against the local file's modification time. A full download only occurs when the remote file is actually newer, keeping bandwidth usage minimal.

> **Note:** The CSI program closed in 2019. The remote dataset is historical and unlikely to change. The auto-update is primarily a safety net to capture any late corrections published by the CPUC.

---

## Configuration

All configurable values live in `config.py`. Edit this file to change behavior without touching application logic.

| Constant | Default | Description |
|---|---|---|
| `CSI_DOWNLOAD_URL` | CPUC zip URL | Remote source for the latest CSI data |
| `LOCAL_CSV_PATH` | `WorkingDataSet.csv` | Path to the local seed/cache file |
| `REFRESH_INTERVAL_HOURS` | `24` | How often the background scheduler checks for new data |
| `ZSCORE_THRESHOLD` | `1.0` | Z-score cutoff for outlier removal |
| `OUTLIER_COLUMNS` | `[Total Cost, Incentive Amount]` | Columns used for z-score calculation |
| `CRITICAL_COLUMNS` | `[Incentive Amount, Total Cost]` | Rows missing these are dropped at load time |

---

## Dataset

| Field | Value |
|---|---|
| Source | California Public Utilities Commission (CPUC) |
| Program | California Solar Initiative (CSI) |
| Records | ~23,504 applications |
| Time span | June 2007 – November 2019 |
| Geography | Southern California (20 counties, primarily San Diego) |
| Key columns | Application Number, Program, Incentive Amount, Total Cost, Nameplate Rating, System Owner Sector, City, County, First Completed Date, Solar Contractor Company Name |

The dataset represents completed, cancelled, and in-progress applications submitted to the CSI program through its three program administrators: CSE (California Solar Energy), PG&E, and SCE.

---

## Troubleshooting

**App shows "Data could not be loaded"**
- Ensure `WorkingDataSet.csv` exists in the project root.
- Check that all dependencies are installed: `pip install -r requirements.txt`.

**Sidebar shows a yellow warning about refresh failure**
- The CPUC download URL may have changed. Verify the URL at [californiasolarstatistics.ca.gov/data_downloads](https://www.californiasolarstatistics.ca.gov/data_downloads/) and update `CSI_DOWNLOAD_URL` in `config.py`.
- The app continues to work normally using the last successfully loaded local file.

**Charts appear empty after applying filters**
- The selected combination of filters returns zero records. The app shows a warning and stops rendering. Broaden the filters (e.g., widen the year range or deselect some counties).

**`ModuleNotFoundError` on launch**
- Activate your virtual environment before running: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux), then re-run `pip install -r requirements.txt`.

**Port already in use**
- Streamlit defaults to port 8501. Run on a different port with:
  ```bash
  streamlit run app.py --server.port 8502
  ```
