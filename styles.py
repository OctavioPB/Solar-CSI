# -*- coding: utf-8 -*-
"""
styles.py — OPB Brand Design System for the CSI Dashboard.

Public interface
----------------
inject_brand()          Inject CSS variables, Google Fonts, and Streamlit overrides.
navbar()                Render the OPB sticky navigation bar.
hero(subtitle)          Render the dark hero header.
section_eyebrow(label)  Render a gold eyebrow label before a section.
section_divider()       Render a gradient section divider.
section_title(text)     Render a Fraunces section heading.
chart_layout()          Return a Plotly layout dict applying brand typography/colors.

BRAND_COLORS            Ordered list of brand colors for multi-series charts.
BRAND_SCALE             Two-stop continuous scale [light→primary].
STATUS_COLORS           Semantic color map for CSI application statuses.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

BRAND_COLORS = ["#003366", "#27B97C", "#7C4DBD", "#F07020", "#E05080"]

BRAND_SCALE  = [[0.0, "#E0EAF4"], [1.0, "#003366"]]   # light blue → primary
GOLD_SCALE   = [[0.0, "#FDF6E3"], [1.0, "#C8982A"]]

STATUS_COLORS = {
    "Completed":             "#27B97C",
    "Cancelled":             "#E03448",
    "Wait List":             "#F07020",
    "Withdrawn":             "#7C4DBD",
    "Site Transferred":      "#003366",
    "Confirmed Reservation": "#E05080",
}

# ---------------------------------------------------------------------------
# Plotly chart layout (apply to every figure)
# ---------------------------------------------------------------------------

def chart_layout(**overrides) -> dict:
    """Return a Plotly update_layout dict with OPB brand typography and colors."""
    base = dict(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color="#1C1C2E",
            size=12,
        ),
        title=dict(
            font=dict(family="Fraunces, Georgia, serif", size=17, color="#1C1C2E"),
            x=0,
            pad=dict(b=12),
        ),
        xaxis=dict(gridcolor="#E0EAF4", linecolor="#E0EAF4", zerolinecolor="#E0EAF4"),
        yaxis=dict(gridcolor="#E0EAF4", linecolor="#E0EAF4", zerolinecolor="#E0EAF4"),
        legend=dict(
            bgcolor="white",
            bordercolor="#E0EAF4",
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(t=52, r=16, b=24, l=16),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#E0EAF4",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#1C1C2E"),
        ),
    )
    base.update(overrides)
    return base

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300;1,9..144,400&display=swap');

/* ── Variables ── */
:root {
  --primary:    #003366;
  --primary-80: #1A4D80;
  --primary-60: #336699;
  --primary-30: #99BBDD;
  --primary-10: #E0EAF4;
  --gold:       #C8982A;
  --gold-light: #E8C46A;
  --dark:       #1C1C2E;
  --mid:        #6B7280;
  --light:      #F4F6F9;
  --white:      #FFFFFF;
}

/* ── Base ── */
html, body, .stApp {
    background-color: var(--light) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
header[data-testid="stHeader"]    { display: none !important; }
#MainMenu                          { visibility: hidden !important; }
footer                             { visibility: hidden !important; }
.stDeployButton                    { display: none !important; }

/* ── Main block ── */
.main > .block-container {
    padding-top: 0 !important;
    padding-left: 48px !important;
    padding-right: 48px !important;
    max-width: 1440px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--primary) !important;
}
[data-testid="stSidebar"] section { background: var(--primary) !important; }

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stCaption { color: rgba(255,255,255,0.80) !important; }

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white !important;
    font-family: 'Fraunces', Georgia, serif !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
    margin: 12px 0 !important;
}

/* Sidebar controls */
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: rgba(255,255,255,0.5) !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(200,152,42,0.25) !important;
    color: var(--gold-light) !important;
}

/* Sidebar toggle */
[data-testid="stSidebar"] [data-baseweb="checkbox"] + div { background: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] input[type="checkbox"]:checked + div { background: var(--gold) !important; }

/* Sidebar button */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.85) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: background 0.2s !important;
    padding: 8px 16px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: var(--gold) !important;
}

/* Sidebar slider */
[data-testid="stSidebar"] .stSlider > div > div > div:nth-child(1) {
    background: rgba(255,255,255,0.2) !important;
}

/* ── Typography ── */
h1 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 32px !important;
    font-weight: 400 !important;
    color: var(--dark) !important;
    line-height: 1.2 !important;
}
h2 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 22px !important;
    font-weight: 300 !important;
    color: var(--dark) !important;
}
h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: var(--dark) !important;
}
p, li { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 15px !important; line-height: 1.7 !important; }
.stCaption, caption { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 12px !important; color: var(--mid) !important; }

/* ── KPI metric cards ── */
[data-testid="metric-container"] {
    background: var(--white) !important;
    border-radius: 12px !important;
    padding: 24px 28px 20px !important;
    border-top: 3px solid !important;
    border-image: linear-gradient(90deg, var(--primary), var(--gold)) 1 !important;
    box-shadow: 0 1px 6px rgba(0,51,102,0.08) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 30px !important;
    font-weight: 300 !important;
    color: var(--dark) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: var(--mid) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--primary-10) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: var(--mid) !important;
    padding: 10px 20px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 6px 6px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--gold) !important;
    background: transparent !important;
}

/* ── Buttons (main) ── */
.stButton > button {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
}
.stButton > button:hover { background: var(--primary-80) !important; }

/* ── Sliders (main) ── */
[data-testid="stSlider"] > div > div > div > div { background: var(--primary) !important; }

/* ── Multiselect tags (main) ── */
[data-baseweb="tag"] {
    background: var(--primary-10) !important;
    color: var(--primary) !important;
    border-radius: 20px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11px !important;
}

/* ── Alerts / banners ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}

/* ── Dataframe table ── */
[data-testid="stDataFrame"] table thead tr th {
    background-color: var(--primary) !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    padding: 12px 16px !important;
}
[data-testid="stDataFrame"] table tbody tr:nth-child(even) td {
    background-color: var(--primary-10) !important;
}

/* ── Dividers ── */
hr {
    height: 1px !important;
    background: linear-gradient(90deg, var(--primary-10), transparent) !important;
    border: none !important;
    margin: 8px 0 !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] { accent-color: var(--gold) !important; }

/* ── Spinner ── */
.stSpinner > div > div { border-top-color: var(--gold) !important; }
</style>
"""

# ---------------------------------------------------------------------------
# HTML components
# ---------------------------------------------------------------------------

_NAVBAR_HTML = """
<div style="
    position: sticky; top: 0; z-index: 999;
    height: 52px;
    background: rgba(0,51,102,0.97);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 48px;
    margin: 0 -48px 0 -48px;
">
    <span style="font-family:'Fraunces',Georgia,serif; font-size:22px; color:white;
                 letter-spacing:-0.5px; line-height:1;">
        O<em style="color:#E8C46A; font-style:italic;">PB</em>
    </span>
    <span style="font-family:'Plus Jakarta Sans',sans-serif; font-size:9px;
                 letter-spacing:3px; text-transform:uppercase;
                 color:rgba(255,255,255,0.4);">
        California Solar Initiative &nbsp;·&nbsp; Analysis
    </span>
</div>
"""

_HERO_TEMPLATE = """
<div style="
    background-color: #003366;
    background-image:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
    background-size: 48px 48px;
    border-radius: 16px;
    padding: 56px 48px 48px;
    margin: 24px 0 40px 0;
    position: relative;
    overflow: hidden;
">
    <div style="
        height: 3px;
        background: linear-gradient(90deg, #003366, #C8982A);
        position: absolute; top: 0; left: 0; right: 0;
        border-radius: 16px 16px 0 0;
    "></div>

    <p style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-size:9px; letter-spacing:4px; text-transform:uppercase;
        color:#C8982A; margin:0 0 20px 0;
    ">OPB &nbsp;·&nbsp; Data &amp; AI Strategy</p>

    <h1 style="
        font-family:'Fraunces',Georgia,serif;
        font-size:48px;
        font-weight:300;
        color:white;
        margin:0 0 16px 0;
        line-height:1.15;
    ">
        <span style="color:white;">California</span>
        <em style="color:#E8C46A; font-style:italic;">Solar</em>
        <span style="color:white;">Initiative</span>
    </h1>

    <p style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-size:15px; font-weight:400; line-height:1.7;
        color:rgba(255,255,255,0.6); margin:0;
    ">{subtitle}</p>
</div>
"""

_EYEBROW_TEMPLATE = """
<div style="display:flex; align-items:center; gap:12px; margin:48px 0 6px 0;">
    <div style="width:24px; height:1px; background:#C8982A; flex-shrink:0;"></div>
    <span style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-size:9px; letter-spacing:4px; text-transform:uppercase; color:#C8982A;
    ">{label}</span>
</div>
"""

_DIVIDER_HTML = """
<div style="height:1px; background:linear-gradient(90deg,#E0EAF4,transparent);
            margin:6px 0 28px 0;"></div>
"""

_SECTION_TITLE_TEMPLATE = """
<h1 style="
    font-family:'Fraunces',Georgia,serif;
    font-size:32px; font-weight:400;
    color:#1C1C2E; margin:8px 0 24px 0; line-height:1.2;
">{title}</h1>
"""

# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def inject_brand() -> None:
    """Inject CSS variables, Google Fonts, and Streamlit style overrides.
    Uses st.markdown so the <style> block is injected into the parent page DOM,
    not sandboxed — st.html() iframes its content and would isolate the styles.
    """
    st.markdown(_CSS, unsafe_allow_html=True)


def navbar() -> None:
    """Render the OPB sticky navigation bar."""
    st.html(_NAVBAR_HTML)


def hero(subtitle: str = "") -> None:
    """Render the dark blue hero header with grid texture."""
    st.html(_HERO_TEMPLATE.format(subtitle=subtitle))


def section_eyebrow(label: str) -> None:
    """Render a gold eyebrow label with leading horizontal rule."""
    st.html(_EYEBROW_TEMPLATE.format(label=label))


def section_divider() -> None:
    """Render a branded gradient section divider."""
    st.html(_DIVIDER_HTML)


def section_title(title: str, emphasis: str = "") -> None:
    """
    Render a Fraunces section heading.
    Optionally italicise one key word by passing it as `emphasis`.
    """
    if emphasis:
        title = title.replace(
            emphasis,
            f'<em style="font-style:italic;">{emphasis}</em>',
        )
    st.html(_SECTION_TITLE_TEMPLATE.format(title=title))
