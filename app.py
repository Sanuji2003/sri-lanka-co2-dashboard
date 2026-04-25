from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Sri Lanka CO2 Emissions Dashboard",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# THEME
# =========================
BG_COLOR = "#081722"
PANEL_BG = "#0B1E2B"
PANEL_BG_ALT = "#102938"
PANEL_BORDER = "#1A4254"
TEXT_PRIMARY = "#F3F7FA"
TEXT_MUTED = "#AFC1CB"

TEAL = "#1FB5AE"
CYAN = "#56B6FF"
GREEN = "#7CC457"
YELLOW = "#D9A72C"
RED = "#E95B5B"
PURPLE = "#CBB8F6"
PINK = "#F05B93"

SECTOR_COLORS = {
    "Transportation": TEAL,
    "Power": GREEN,
    "Buildings": YELLOW,
    "Manufacturing": RED,
}

CHART_CONFIG = {"displayModeBar": False}

# =========================
# HELPERS
# =========================
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("clean_data.csv")


def labelize(value) -> str:
    return str(value).replace("-", " ").replace("_", " ").title()


def compact_text(value: str, limit: int = 24) -> str:
    text = str(value)
    return text if len(text) <= limit else f"{text[:limit - 3]}..."


def format_mt(value: float) -> str:
    return f"{float(value):.2f} Mt"


def format_year_span(years: list) -> str:
    if not years:
        return "N/A"
    years = sorted(int(y) for y in years)
    return str(years[0]) if len(years) == 1 else f"{years[0]} - {years[-1]}"


def format_mt_precise(value: float) -> str:
    value = float(value)
    if 0 < abs(value) < 0.01:
        return f"{value:.3f} Mt"
    return f"{value:.2f} Mt"


def lighten_hex(hex_color: str, factor: float = 0.12) -> str:
    hex_color = hex_color.lstrip("#")
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    red = min(255, int(red + (255 - red) * factor))
    green = min(255, int(green + (255 - green) * factor))
    blue = min(255, int(blue + (255 - blue) * factor))
    return f"#{red:02X}{green:02X}{blue:02X}"


def wrap_treemap_label(value: str) -> str:
    words = str(value).split()
    if len(words) <= 1:
        return str(value)
    split_at = max(1, len(words) // 2)
    return "<br>".join([" ".join(words[:split_at]), " ".join(words[split_at:])])


def style_figure(fig, height: int, showlegend: bool = False) -> None:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=6, t=18, b=4),
        font=dict(color=TEXT_PRIMARY, size=10),
        legend_title_text="",
        coloraxis_showscale=False,
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=TEXT_MUTED, size=9),
        title_font=dict(color=TEXT_MUTED, size=9),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=TEXT_MUTED, size=9),
        title_font=dict(color=TEXT_MUTED, size=9),
    )
    if showlegend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10, color=TEXT_PRIMARY),
            )
        )


def render_kpi(col, icon: str, label: str, value: str, note: str, icon_color: str):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-head">
                <div class="kpi-icon" style="color:{icon_color};">{icon}</div>
                <div class="kpi-copy">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-note">{note}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dataset_row(icon: str, label: str, value: str):
    st.markdown(
        f"""
        <div class="dataset-item">
            <div class="dataset-left">
                <span class="dataset-icon">{icon}</span>
                <span class="dataset-label">{label}</span>
            </div>
            <div class="dataset-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_title(title: str):
    st.markdown(f"<div class='panel-title'>{title}</div>", unsafe_allow_html=True)


def render_insight(col, accent: str, icon: str, headline: str, value: str, body: str):
    col.markdown(
        f"""
        <div class="insight-card" style="border-left-color:{accent};">
            <div class="insight-icon" style="color:{accent};">{icon}</div>
            <div class="insight-headline">{headline}</div>
            <div class="insight-value" style="color:{accent};">{value}</div>
            <div class="insight-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# CSS
# =========================
st.markdown(
    f"""
    <style>
    [data-testid="stHeader"] {{
        display: none !important;
        height: 0 !important;
    }}

    [data-testid="stToolbar"] {{
        display: none !important;
    }}

    [data-testid="stAppToolbar"] {{
        display: none !important;
    }}

    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    [data-testid="stDecoration"] {{
        display: none;
    }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: {BG_COLOR};
        color: {TEXT_PRIMARY};
    }}

    .block-container {{
        max-width: 100% !important;
        padding: 0.14rem 0.28rem 0.18rem;
    }}

    div[data-testid="stHorizontalBlock"] {{
        gap: 0.32rem !important;
    }}

    div[data-testid="stVerticalBlock"] > div:empty {{
        display: none;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {PANEL_BG};
        border: 1px solid {PANEL_BORDER};
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.16);
        padding-top: 0.02rem;
        padding-bottom: 0.02rem;
        overflow: hidden;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        overflow: hidden;
        padding-top: 0.02rem;
        padding-bottom: 0.02rem;
    }}

    [data-baseweb="select"] > div,
    [data-baseweb="base-input"],
    [data-baseweb="base-input"] > div,
    .stTextInput > div > div {{
        background: {PANEL_BG_ALT} !important;
        border: 1px solid #2B5165 !important;
        color: {TEXT_PRIMARY} !important;
        min-height: 1.74rem;
        border-radius: 8px !important;
    }}

    [data-baseweb="select"] svg {{
        fill: {TEXT_MUTED};
    }}

    input,
    [data-baseweb="base-input"] input {{
        color: {TEXT_PRIMARY} !important;
        background: transparent !important;
        caret-color: {TEXT_PRIMARY} !important;
        font-size: 0.78rem !important;
    }}

    input::placeholder {{
        color: {TEXT_MUTED} !important;
        opacity: 1 !important;
    }}

    .stSelectbox label,
    .stTextInput label,
    .stSlider label {{
        display: none !important;
    }}

    .stSlider [data-baseweb="slider"] {{
        padding-top: 0.04rem;
        padding-bottom: 0.04rem;
    }}

    .stDownloadButton button {{
        width: 100%;
        min-height: 1.75rem;
        border-radius: 9px;
        background: {PANEL_BG_ALT};
        border: 1px solid #31576B;
        color: {TEXT_PRIMARY};
        font-weight: 700;
        font-size: 0.74rem;
    }}

    /* ---- Brand / Sidebar ---- */
    .brand-head {{
        display: flex;
        gap: 0.48rem;
        align-items: flex-start;
        padding: 0.02rem 0.02rem 0;
    }}
    .brand-icon {{
        width: 34px; height: 34px; flex: 0 0 34px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.28rem; color: #B7DC61;
    }}
    .brand-title {{
        color: {TEXT_PRIMARY}; font-size: 0.88rem; font-weight: 800; line-height: 1.12;
    }}
    .brand-subtitle {{
        color: #D7E3EA; font-size: 0.64rem; margin-top: 0.16rem; line-height: 1.24;
    }}
    .green-accent {{ color: #2CD1C4; font-weight: 800; }}
    .sidebar-title {{
        color: #2CD1C4; font-size: 0.78rem; font-weight: 800;
        text-transform: uppercase; margin-bottom: 0.16rem;
    }}
    .filter-label {{
        color: {TEXT_PRIMARY}; font-size: 0.68rem; font-weight: 700; margin: 0.1rem 0 0.03rem;
    }}
    .sidebar-subsection {{
        color: #8EDBE0; font-size: 0.68rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 0.04em; margin: 0.14rem 0 0.02rem;
    }}
    .slider-ends {{
        display: flex; justify-content: space-between;
        color: {TEXT_MUTED}; font-size: 0.62rem; margin-top: -0.18rem;
    }}

    /* ---- Dataset overview ---- */
    .dataset-item {{
        display: flex; justify-content: space-between; align-items: center;
        gap: 0.32rem; padding: 0.18rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .dataset-item:last-child {{ border-bottom: none; }}
    .dataset-left {{ display: flex; align-items: center; gap: 0.3rem; min-width: 0; }}
    .dataset-icon {{ font-size: 0.74rem; line-height: 1; }}
    .dataset-label {{ color: #D3E1E8; font-size: 0.68rem; }}
    .dataset-value {{
        color: #8EDBE0; font-size: 0.72rem; font-weight: 800;
        text-align: right; white-space: nowrap;
    }}

    /* ---- KPI cards ---- */
    .kpi-card {{
        background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid #295162; border-radius: 12px;
        padding: 0.34rem 0.42rem; min-height: 62px;
    }}
    .kpi-head {{ display: flex; gap: 0.42rem; align-items: flex-start; }}
    .kpi-icon {{
        width: 28px; height: 28px; flex: 0 0 28px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.96rem; line-height: 1; margin-top: 0.02rem;
    }}
    .kpi-label {{ color: #DCE7ED; font-size: 0.62rem; font-weight: 700; line-height: 1.12; }}
    .kpi-value {{
        color: white; font-size: 0.84rem; font-weight: 800;
        margin-top: 0.04rem; line-height: 1.08; white-space: normal; word-break: break-word;
    }}
    .kpi-note {{ color: #BFD0D9; font-size: 0.62rem; margin-top: 0.08rem; line-height: 1.12; }}

    /* ---- Panel titles ---- */
    .panel-title {{
        color: white; font-size: 0.84rem; font-weight: 800;
        margin-bottom: 0.05rem; line-height: 1.16;
    }}

    /* ---- View Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.42rem;
        margin: 0.04rem 0 0.18rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {PANEL_BG_ALT};
        border: 1px solid #31576B;
        border-radius: 10px;
        color: {TEXT_MUTED};
        min-height: 2rem;
        padding: 0 0.95rem;
        font-size: 0.78rem;
        font-weight: 700;
    }}
    .stTabs [aria-selected="true"] {{
        background: rgba(44, 209, 196, 0.14);
        border-color: #2CD1C4;
        color: {TEXT_PRIMARY};
    }}

    /* ---- Key Insight cards ---- */
    .insight-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid #1E3F52;
        border-left: 3px solid;
        border-radius: 11px;
        padding: 0.44rem 0.54rem;
        height: 100%;
        min-height: 96px;
    }}
    .insight-icon {{
        font-size: 0.96rem; line-height: 1; margin-bottom: 0.12rem;
    }}
    .insight-headline {{
        color: {TEXT_MUTED}; font-size: 0.62rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.04em;
        margin-bottom: 0.08rem; line-height: 1.16;
    }}
    .insight-value {{
        font-size: 0.88rem; font-weight: 800;
        line-height: 1.1; margin-bottom: 0.12rem;
    }}
    .insight-body {{
        color: #A8BCC6; font-size: 0.64rem; line-height: 1.34;
    }}

    /* ---- Insights section header ---- */
    .insights-section-header {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.1rem 0 0.05rem;
    }}
    .insights-section-title {{
        color: #2CD1C4; font-size: 0.88rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 0.06em;
    }}
    .insights-section-line {{
        flex: 1; height: 1px;
        background: linear-gradient(90deg, #1A4254 0%, transparent 100%);
    }}

    /* ---- Data table ---- */
    .table-scroll-wrapper {{
        overflow-x: auto; overflow-y: auto;
        max-height: 180px; border-radius: 10px;
        border: 1px solid #31576B;
    }}
    .data-table {{
        width: 100%; border-collapse: collapse;
        min-width: 620px; font-size: 0.76rem;
    }}
    .data-table thead th {{
        background: #143247; color: white; text-align: left;
        padding: 0.48rem 0.55rem; border-bottom: 1px solid #31576B;
        position: sticky; top: 0; z-index: 2;
    }}
    .data-table tbody td {{
        color: #DAE4EA; padding: 0.45rem 0.55rem;
        border-bottom: 1px solid rgba(255,255,255,0.06); white-space: nowrap;
    }}
    .data-table tbody tr:nth-child(odd) {{ background: #132C3D; }}
    .data-table tbody tr:nth-child(even) {{ background: #102635; }}

    .footnote {{
        color: {TEXT_MUTED}; font-size: 0.72rem;
        margin-top: 0.18rem; padding-left: 0.1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# LOAD DATA
# =========================
try:
    df = load_data()
except FileNotFoundError:
    st.error("clean_data.csv was not found. Put clean_data.csv in the same folder as app.py.")
    st.stop()

for col in ["year", "emissions_mt", "emissionsQuantity", "activity", "capacity"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "sector_label" not in df.columns:
    if "sector" in df.columns:
        df["sector_label"] = df["sector"].map(labelize)
    else:
        df["sector_label"] = "Unknown"

if "subsector_label" not in df.columns:
    if "subsector" in df.columns:
        df["subsector_label"] = df["subsector"].map(labelize)
    else:
        df["subsector_label"] = "Unknown"

all_years = sorted(df["year"].dropna().astype(int).unique().tolist()) if "year" in df.columns else []
all_sectors = sorted(df["sector_label"].dropna().unique().tolist())
all_locations = df["name"].nunique() if "name" in df.columns else 0
all_subsectors = df["subsector_label"].nunique()

year_filter_options = ["All Years"] + [str(y) for y in all_years]
sector_filter_options = ["All Sectors"] + all_sectors

csv_path = Path("clean_data.csv")
last_updated = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime("%b %d, %Y") if csv_path.exists() else "N/A"

# =========================
# LAYOUT
# =========================
left_col, right_col = st.columns([0.165, 0.835], gap="small")

with left_col:
    with st.container(border=True):
        st.markdown(
            """
            <div class="brand-head">
                <div class="brand-icon">🌿</div>
                <div>
                    <div class="brand-title">Sri Lanka CO₂<br>Emissions Dashboard</div>
                    <div class="brand-subtitle">
                        CO₂ emissions by sector, subsector,
                        <span class="green-accent">location</span> and year.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("<div class='sidebar-title'>Filters</div>", unsafe_allow_html=True)

        st.markdown("<div class='filter-label'>Year</div>", unsafe_allow_html=True)
        selected_year = st.selectbox("Year", options=year_filter_options, label_visibility="collapsed")

        st.markdown("<div class='filter-label'>Sector</div>", unsafe_allow_html=True)
        selected_sector = st.selectbox("Sector", options=sector_filter_options, label_visibility="collapsed")

        if selected_sector == "All Sectors":
            subsector_options = ["All Subsectors"] + sorted(df["subsector_label"].dropna().unique().tolist())
        else:
            subsector_options = ["All Subsectors"] + sorted(
                df.loc[df["sector_label"] == selected_sector, "subsector_label"].dropna().unique().tolist()
            )

        st.markdown("<div class='filter-label'>Subsector</div>", unsafe_allow_html=True)
        selected_subsector = st.selectbox("Subsector", options=subsector_options, label_visibility="collapsed")

        st.markdown("<div class='sidebar-subsection'>Top N Locations</div>", unsafe_allow_html=True)
        max_top_n = min(30, max(5, int(all_locations))) if all_locations > 0 else 5
        top_n = st.slider("Top N", min_value=5, max_value=max_top_n, value=min(10, max_top_n), label_visibility="collapsed")
        st.markdown("<div class='slider-ends'><span>5</span><span>30</span></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='sidebar-title'>Dataset Overview</div>", unsafe_allow_html=True)
        dataset_col1, dataset_col2 = st.columns(2, gap="small")
        with dataset_col1:
            render_dataset_row("🗂️", "Records", f"{len(df):,}")
            render_dataset_row("📍", "Locations", f"{all_locations:,}")
            render_dataset_row("🧩", "Sectors", f"{df['sector_label'].nunique()}")
        with dataset_col2:
            render_dataset_row("🏭", "Subsectors", f"{all_subsectors}")
            render_dataset_row("📅", "Years", format_year_span(all_years))
            render_dataset_row("🕒", "Updated", last_updated)

# =========================
# FILTER DATA
# =========================
filtered_df = df.copy()

if selected_year != "All Years" and "year" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["year"] == int(selected_year)].copy()

if selected_sector != "All Sectors":
    filtered_df = filtered_df[filtered_df["sector_label"] == selected_sector].copy()

if selected_subsector != "All Subsectors":
    filtered_df = filtered_df[filtered_df["subsector_label"] == selected_subsector].copy()

if filtered_df.empty:
    with right_col:
        st.warning("No records match the selected filters.")
    st.stop()

# =========================
# AGGREGATIONS
# =========================
total_emissions_mt = filtered_df["emissions_mt"].sum()

sector_totals = (
    filtered_df.groupby("sector_label", dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
    .sort_values("emissions_mt", ascending=False)
)

location_totals = (
    filtered_df.groupby("name", dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
    .sort_values("emissions_mt", ascending=False)
)

year_sector = (
    filtered_df.groupby(["year", "sector_label"], dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
    .sort_values(["year", "sector_label"])
)

selected_years = sorted(filtered_df["year"].dropna().astype(int).unique().tolist()) if "year" in filtered_df.columns else []
top_sector_name = sector_totals.iloc[0]["sector_label"] if not sector_totals.empty else "N/A"
top_sector_value = sector_totals.iloc[0]["emissions_mt"] if not sector_totals.empty else 0.0
top_sector_share = (top_sector_value / total_emissions_mt * 100) if total_emissions_mt else 0.0
top_location_name = str(location_totals.iloc[0]["name"]) if not location_totals.empty else "N/A"
top_location_value = location_totals.iloc[0]["emissions_mt"] if not location_totals.empty else 0.0
filtered_locations = filtered_df["name"].nunique() if "name" in filtered_df.columns else 0
filtered_subsectors = filtered_df["subsector_label"].nunique()

# =========================
# KEY INSIGHTS COMPUTATION
# =========================
# YoY change per sector (only when both years are present)
yoy_df = filtered_df.copy()
year_list = sorted(yoy_df["year"].dropna().astype(int).unique().tolist())
has_two_years = len(year_list) == 2

if has_two_years:
    yr_a, yr_b = year_list[0], year_list[1]
    pivot_yoy = (
        yoy_df.groupby(["year", "sector_label"])["emissions_mt"]
        .sum()
        .unstack(level=0)
        .fillna(0)
    )
    pivot_yoy.columns = [str(c) for c in pivot_yoy.columns]
    yoy_changes = {}
    if str(yr_a) in pivot_yoy.columns and str(yr_b) in pivot_yoy.columns:
        for sector in pivot_yoy.index:
            v_a = float(pivot_yoy.loc[sector, str(yr_a)])
            v_b = float(pivot_yoy.loc[sector, str(yr_b)])
            if v_a > 0:
                yoy_changes[sector] = (v_b - v_a) / v_a * 100
    # Fastest growing sector
    fastest_sector = max(yoy_changes, key=yoy_changes.get) if yoy_changes else None
    fastest_pct = yoy_changes.get(fastest_sector, 0) if fastest_sector else 0
    overall_a = float(yoy_df[yoy_df["year"] == yr_a]["emissions_mt"].sum())
    overall_b = float(yoy_df[yoy_df["year"] == yr_b]["emissions_mt"].sum())
    overall_yoy_pct = (overall_b - overall_a) / overall_a * 100 if overall_a > 0 else 0
else:
    fastest_sector = None
    fastest_pct = 0.0
    overall_yoy_pct = 0.0

# Top-2 location concentration
top2_share = 0.0
top2_names = ""
if len(location_totals) >= 2:
    top2_val = location_totals.head(2)["emissions_mt"].sum()
    top2_share = (top2_val / total_emissions_mt * 100) if total_emissions_mt else 0
    top2_names = " & ".join(compact_text(n, 18) for n in location_totals.head(2)["name"].tolist())

# Dominant subsector
subsector_totals = (
    filtered_df.groupby("subsector_label", dropna=False)["emissions_mt"]
    .sum()
    .sort_values(ascending=False)
)
dom_sub = subsector_totals.index[0] if not subsector_totals.empty else "N/A"
dom_sub_share = (float(subsector_totals.iloc[0]) / total_emissions_mt * 100) if total_emissions_mt and not subsector_totals.empty else 0

# Smallest sector
smallest_sector_name = sector_totals.iloc[-1]["sector_label"] if not sector_totals.empty else "N/A"
smallest_sector_val = sector_totals.iloc[-1]["emissions_mt"] if not sector_totals.empty else 0.0
smallest_sector_share = (float(smallest_sector_val) / total_emissions_mt * 100) if total_emissions_mt else 0.0

compact_chart_height = 188
treemap_chart_height = 184

# =========================
# MAIN CONTENT
# =========================
with right_col:
    # ---- KPI Row ----
    kpi_cols = st.columns(6, gap="small")
    render_kpi(kpi_cols[0], "☁", "Total CO₂ Emissions", format_mt(total_emissions_mt), "Million Tonnes CO₂", TEAL)
    render_kpi(kpi_cols[1], "◔", "Top Emitting Sector", top_sector_name, f"{top_sector_share:.1f}% of total", CYAN)
    render_kpi(kpi_cols[2], "▥", "Top Emitting Location", compact_text(top_location_name, 16), format_mt(top_location_value), "#8FEFE0")
    render_kpi(kpi_cols[3], "🗓", "Years Covered", format_year_span(selected_years), f"{len(selected_years)} Year(s)", "#98E7E0")
    render_kpi(kpi_cols[4], "📍", "Total Locations", f"{filtered_locations:,}", "Unique Sources", PINK)
    render_kpi(kpi_cols[5], "🏭", "Total Subsectors", f"{filtered_subsectors}", f"Across {filtered_df['sector_label'].nunique()} Sectors", PURPLE)

    overview_tab, more_plots_tab = st.tabs(["Overview", "More Plots"])

    with overview_tab:
        row1 = st.columns([1.0, 1.0, 1.2], gap="small")

        with row1[0]:
            with st.container(border=True):
                panel_title("1. Share of CO2 Emissions by Sector")
                fig_share = px.pie(
                    sector_totals,
                    names="sector_label",
                    values="emissions_mt",
                    hole=0.42,
                    color="sector_label",
                    color_discrete_map=SECTOR_COLORS,
                )
                fig_share.update_traces(textposition="inside", textinfo="percent")
                fig_share.add_annotation(
                    text=f"<b>{total_emissions_mt:.2f} Mt</b><br>Total",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(color="white", size=12),
                )
                fig_share.update_layout(
                    legend=dict(
                        orientation="v",
                        x=0.82,
                        y=0.5,
                        xanchor="left",
                        yanchor="middle",
                        font=dict(color=TEXT_PRIMARY, size=10),
                    )
                )
                style_figure(fig_share, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_share, use_container_width=True, config=CHART_CONFIG)

        with row1[1]:
            with st.container(border=True):
                panel_title("2. Total CO2 Emissions by Sector")
                fig_sector = px.bar(
                    sector_totals,
                    x="sector_label",
                    y="emissions_mt",
                    color="sector_label",
                    color_discrete_map=SECTOR_COLORS,
                    text_auto=".2f",
                    labels={"sector_label": "", "emissions_mt": "Emissions (Mt CO2)"},
                )
                fig_sector.update_traces(width=0.42)
                fig_sector.update_layout(showlegend=False, bargap=0.52)
                fig_sector.update_xaxes(title_text=None)
                style_figure(fig_sector, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_sector, use_container_width=True, config=CHART_CONFIG)

        with row1[2]:
            with st.container(border=True):
                panel_title("3. Year-on-Year Emissions Trend by Sector")
                fig_trend = px.line(
                    year_sector,
                    x="year",
                    y="emissions_mt",
                    color="sector_label",
                    markers=True,
                    color_discrete_map=SECTOR_COLORS,
                    labels={"year": "", "emissions_mt": "Emissions (Mt CO2)", "sector_label": ""},
                )
                fig_trend.update_xaxes(type="category")
                fig_trend.update_layout(
                    legend=dict(
                        orientation="v",
                        x=1.01,
                        y=0.5,
                        xanchor="left",
                        yanchor="middle",
                        font=dict(color=TEXT_PRIMARY, size=10),
                    )
                )
                style_figure(fig_trend, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_trend, use_container_width=True, config=CHART_CONFIG)

        treemap_row = st.columns([1.22, 0.78], gap="small")

        with treemap_row[0]:
            with st.container(border=True):
                panel_title("4. Emissions Hierarchy Treemap (Sector > Subsector)")
                treemap_df = (
                    filtered_df.groupby(["sector_label", "subsector_label"], dropna=False)["emissions_mt"]
                    .sum()
                    .reset_index()
                )
                sector_tree_totals = (
                    treemap_df.groupby("sector_label", dropna=False)["emissions_mt"]
                    .sum()
                    .sort_values(ascending=False)
                )
                ordered_sectors = [s for s in SECTOR_COLORS if s in sector_tree_totals.index]
                ordered_sectors += [s for s in sector_tree_totals.index if s not in ordered_sectors]

                ids, labels, parents, values = [], [], [], []
                node_text, hover_text, colors = [], [], []
                total_tree_emissions = float(treemap_df["emissions_mt"].sum())

                for sector in ordered_sectors:
                    sector_total = float(sector_tree_totals.get(sector, 0))
                    if sector_total <= 0:
                        continue
                    sector_id = f"sector::{sector}"
                    sector_share = (sector_total / total_tree_emissions * 100) if total_tree_emissions else 0
                    sector_color = SECTOR_COLORS.get(sector, CYAN)

                    ids.append(sector_id)
                    labels.append(sector)
                    parents.append("")
                    values.append(sector_total)
                    node_text.append(f"{format_mt_precise(sector_total)}<br>({sector_share:.1f}%)")
                    hover_text.append(
                        f"<b>{sector}</b><br>{format_mt_precise(sector_total)}<br>{sector_share:.1f}% of total<extra></extra>"
                    )
                    colors.append(sector_color)

                    child_color = lighten_hex(sector_color, 0.10)
                    for _, row_s in treemap_df[treemap_df["sector_label"] == sector].sort_values("emissions_mt", ascending=False).iterrows():
                        child_total = float(row_s["emissions_mt"])
                        child_label = str(row_s["subsector_label"])
                        child_share = (child_total / sector_total * 100) if sector_total else 0
                        ids.append(f"{sector_id}::{child_label}")
                        labels.append(wrap_treemap_label(child_label))
                        parents.append(sector_id)
                        values.append(child_total)
                        node_text.append(format_mt_precise(child_total))
                        hover_text.append(
                            f"<b>{child_label}</b><br>{format_mt_precise(child_total)}<br>{child_share:.1f}% of {sector}<extra></extra>"
                        )
                        colors.append(child_color)

                fig_tree = go.Figure(
                    go.Treemap(
                        ids=ids,
                        labels=labels,
                        parents=parents,
                        values=values,
                        branchvalues="total",
                        sort=False,
                        text=node_text,
                        texttemplate="<b>%{label}</b><br>%{text}",
                        textposition="middle center",
                        hovertemplate=hover_text,
                        marker=dict(colors=colors, line=dict(color="rgba(255,255,255,0.28)", width=1.4)),
                        pathbar=dict(visible=False),
                        root_color="rgba(0,0,0,0)",
                        tiling=dict(pad=3, packing="squarify"),
                    )
                )
                style_figure(fig_tree, height=treemap_chart_height, showlegend=False)
                fig_tree.update_layout(
                    margin=dict(l=4, r=4, t=4, b=4),
                    uniformtext=dict(minsize=10, mode="hide"),
                    hoverlabel=dict(
                        bgcolor=PANEL_BG_ALT,
                        bordercolor=PANEL_BORDER,
                        font=dict(color=TEXT_PRIMARY, size=10),
                    ),
                )
                fig_tree.update_traces(textfont=dict(color=TEXT_PRIMARY, family="Segoe UI Semibold"))
                st.plotly_chart(fig_tree, use_container_width=True, config=CHART_CONFIG)

        with treemap_row[1]:
            with st.container(border=True):
                header_cols = st.columns([0.68, 0.32], gap="small")
                with header_cols[0]:
                    panel_title("Raw Data Preview")
                with header_cols[1]:
                    export_cols = ["name", "sector_label", "subsector_label", "emissions_mt", "year"]
                    export_cols = [c for c in export_cols if c in filtered_df.columns]
                    export_df = filtered_df[export_cols].copy()
                    st.download_button(
                        label="Download CSV",
                        data=export_df.to_csv(index=False).encode("utf-8"),
                        file_name="filtered_sri_lanka_emissions.csv",
                        mime="text/csv",
                    )
                preview_cols = ["name", "sector_label", "subsector_label", "emissions_mt", "year"]
                preview_cols = [c for c in preview_cols if c in filtered_df.columns]
                preview_df = filtered_df[preview_cols].sort_values("emissions_mt", ascending=False).head(6).copy()
                preview_df["emissions_mt"] = preview_df["emissions_mt"].map(lambda x: f"{x:,.3f}")
                st.markdown(
                    f"<div class='table-scroll-wrapper'>{preview_df.to_html(index=False, classes='data-table', border=0)}</div>",
                    unsafe_allow_html=True,
                )

    with more_plots_tab:
        row2 = st.columns([1.0, 1.0, 1.2], gap="small")

        with row2[0]:
            with st.container(border=True):
                panel_title("5. Top N Emitting Locations")
                top_locations = location_totals.head(top_n).copy()
                top_locations["location_label"] = top_locations["name"].map(lambda x: compact_text(x, 28))
                fig_top = px.bar(
                    top_locations.sort_values("emissions_mt"),
                    x="emissions_mt",
                    y="location_label",
                    orientation="h",
                    text_auto=".2f",
                    color_discrete_sequence=[TEAL],
                    labels={"emissions_mt": "Emissions (Mt CO2)", "location_label": ""},
                )
                fig_top.update_traces(width=0.46)
                fig_top.update_layout(showlegend=False, bargap=0.4)
                fig_top.update_yaxes(title_text=None)
                style_figure(fig_top, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_top, use_container_width=True, config=CHART_CONFIG)

        breakdown_options = sorted(filtered_df["sector_label"].dropna().unique().tolist())
        default_breakdown = selected_sector if selected_sector in breakdown_options else breakdown_options[0]

        with row2[1]:
            with st.container(border=True):
                panel_title("6. Subsector Breakdown")
                selected_breakdown_sector = st.selectbox(
                    "Breakdown Sector",
                    options=breakdown_options,
                    index=breakdown_options.index(default_breakdown),
                    label_visibility="collapsed",
                )
                breakdown_df = filtered_df[filtered_df["sector_label"] == selected_breakdown_sector].copy()
                breakdown_totals = (
                    breakdown_df.groupby("subsector_label", dropna=False)["emissions_mt"]
                    .sum()
                    .reset_index()
                    .sort_values("emissions_mt", ascending=False)
                )
                breakdown_totals["subsector_short"] = breakdown_totals["subsector_label"].map(lambda x: compact_text(x, 20))
                fig_break = px.bar(
                    breakdown_totals,
                    x="subsector_short",
                    y="emissions_mt",
                    color_discrete_sequence=[SECTOR_COLORS.get(selected_breakdown_sector, CYAN)],
                    text_auto=".2f",
                    labels={"subsector_short": "", "emissions_mt": "Emissions (Mt CO2)"},
                )
                fig_break.update_traces(width=0.4)
                fig_break.update_layout(showlegend=False, bargap=0.5)
                fig_break.update_xaxes(tickangle=0)
                style_figure(fig_break, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_break, use_container_width=True, config=CHART_CONFIG)

        with row2[2]:
            with st.container(border=True):
                panel_title("7. Subsector Emissions: 2024 vs 2025")
                breakdown_year = (
                    breakdown_df.groupby(["subsector_label", "year"], dropna=False)["emissions_mt"]
                    .sum()
                    .reset_index()
                    .sort_values(["subsector_label", "year"])
                )
                breakdown_year["subsector_short"] = breakdown_year["subsector_label"].map(lambda x: compact_text(x, 16))
                breakdown_year["year"] = breakdown_year["year"].astype("Int64").astype(str)
                fig_compare = px.bar(
                    breakdown_year,
                    x="subsector_short",
                    y="emissions_mt",
                    color="year",
                    barmode="group",
                    text_auto=".2f",
                    color_discrete_sequence=[TEAL, GREEN],
                    labels={"subsector_short": "", "emissions_mt": "Emissions (Mt CO2)", "year": ""},
                )
                fig_compare.update_layout(
                    bargap=0.45,
                    bargroupgap=0.2,
                    legend=dict(
                        orientation="h",
                        x=0,
                        y=1.02,
                        xanchor="left",
                        yanchor="bottom",
                        font=dict(color=TEXT_PRIMARY, size=10),
                    ),
                )
                fig_compare.update_traces(width=0.22)
                fig_compare.update_xaxes(tickangle=-35)
                style_figure(fig_compare, height=compact_chart_height, showlegend=False)
                st.plotly_chart(fig_compare, use_container_width=True, config=CHART_CONFIG)

        st.markdown(
            """
            <div class="insights-section-header">
                <div class="insights-section-title">Key Insights</div>
                <div class="insights-section-line"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ins_cols = st.columns(4, gap="small")

        render_insight(
            ins_cols[0],
            accent=TEAL,
            icon="S",
            headline="Dominant Sector",
            value=f"{top_sector_name} - {top_sector_share:.1f}%",
            body=(
                f"{top_sector_name} contributes <b>{top_sector_share:.1f}%</b> of total emissions "
                f"({format_mt(top_sector_value)}), making it by far the largest source of CO2 in the dataset."
            ),
        )

        render_insight(
            ins_cols[1],
            accent=CYAN,
            icon="L",
            headline="Emission Hotspot Concentration",
            value=f"Top 2 = {top2_share:.1f}% of total",
            body=(
                f"<b>{top2_names}</b> together account for <b>{top2_share:.1f}%</b> of all emissions "
                f"- a high geographic concentration that signals priority intervention points."
            ),
        )

        if has_two_years and fastest_sector:
            render_insight(
                ins_cols[2],
                accent=YELLOW,
                icon="Y",
                headline="Year-on-Year Growth",
                value=f"+{overall_yoy_pct:.1f}% overall ({yr_a}->{yr_b})",
                body=(
                    f"Total emissions rose by <b>{overall_yoy_pct:.1f}%</b> from {yr_a} to {yr_b}. "
                    f"<b>{fastest_sector}</b> was the fastest-growing sector at <b>+{fastest_pct:.1f}%</b>."
                ),
            )
        else:
            render_insight(
                ins_cols[2],
                accent=YELLOW,
                icon="D",
                headline="Dominant Subsector",
                value=f"{compact_text(dom_sub, 22)} - {dom_sub_share:.1f}%",
                body=(
                    f"<b>{dom_sub}</b> is the single largest subsector, contributing <b>{dom_sub_share:.1f}%</b> "
                    f"of filtered total emissions."
                ),
            )

        render_insight(
            ins_cols[3],
            accent=RED,
            icon="M",
            headline="Lowest Emitting Sector",
            value=f"{smallest_sector_name} - {smallest_sector_share:.1f}%",
            body=(
                f"<b>{smallest_sector_name}</b> contributes only <b>{smallest_sector_share:.1f}%</b> "
                f"({format_mt(float(smallest_sector_val))}) of total emissions - the smallest sectoral share, "
                f"suggesting relatively limited industrial CO2 output."
            ),
        )

    st.markdown(
        "<div class='footnote'>All emissions are measured in Million Tonnes of CO2 (Mt CO2). Insights are computed dynamically from the filtered dataset.</div>",
        unsafe_allow_html=True,
    )
