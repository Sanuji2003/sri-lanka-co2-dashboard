import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Sri Lanka CO2 Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


SECTOR_COLORS = {
    "Buildings": "#214F7D",
    "Manufacturing": "#6F9BC8",
    "Power": "#3C7A57",
    "Transportation": "#E07A00",
}
SOURCE_COLORS = {
    "Gadm Aggregation": "#214F7D",
    "Point Source": "#2F9E8F",
}
CHART_CONFIG = {"displayModeBar": False}


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("clean_data.csv")


def labelize(value: str) -> str:
    return str(value).replace("-", " ").title()


def compact_text(value: str, limit: int = 24) -> str:
    value = str(value)
    return value if len(value) <= limit else f"{value[: limit - 3]}..."


def style_figure(fig, height: int, showlegend: bool = True) -> None:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=30, b=8),
        font=dict(color="#143a5c"),
        legend_title_text="",
    )
    if showlegend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="left",
                x=0,
                font=dict(size=11),
            )
        )


def metric_block(label: str, value: str, note: str) -> str:
    return f"""
    <div class="metric-block">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    .block-container {
        max-width: 100% !important;
        width: 100%;
        padding-top: 0.32rem;
        padding-bottom: 0.3rem;
        padding-left: 0.35rem;
        padding-right: 0.35rem;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #edf4f9 0%, #f7fbfd 58%, #edf4f9 100%);
        overflow: hidden;
    }
    body {
        overflow: hidden;
    }
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }
    .top-band {
        background: linear-gradient(135deg, #114c7a 0%, #225d8b 100%);
        border-radius: 18px;
        color: white;
        box-shadow: 0 14px 32px rgba(17, 76, 122, 0.18);
        padding: 0.68rem 0.95rem;
        margin-bottom: 0.05rem;
        min-height: 94px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .top-title {
        font-size: 1.72rem;
        font-weight: 800;
        line-height: 1.05;
    }
    .top-subtitle {
        font-size: 0.8rem;
        margin-top: 0.12rem;
        opacity: 0.95;
    }
    .top-meta {
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 0.24rem;
        opacity: 0.9;
    }
    .filter-card-label {
        color: #60788e;
        font-size: 0.71rem;
        font-weight: 700;
        margin-bottom: 0.07rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .card-title {
        color: #143a5c;
        font-size: 0.98rem;
        font-weight: 800;
        margin-bottom: 0.08rem;
    }
    .card-subtitle {
        color: #6d8296;
        font-size: 0.8rem;
        margin-bottom: 0.22rem;
    }
    div[data-testid="stSelectbox"] {
        margin-bottom: 0 !important;
    }
    div[data-baseweb="select"] > div {
        min-height: 2.18rem !important;
        border-radius: 12px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    div[data-baseweb="select"] span {
        font-size: 0.93rem !important;
    }
    .metric-block {
        background: white;
        border: 1px solid #cedde9;
        border-radius: 16px;
        box-shadow: 0 9px 20px rgba(18, 60, 91, 0.06);
        min-height: 92px;
        padding: 0.62rem 0.76rem;
    }
    .metric-label {
        color: #567086;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .metric-value {
        color: #143a5c;
        font-size: 1.48rem;
        font-weight: 800;
        line-height: 1.08;
        margin-top: 0.22rem;
    }
    .metric-note {
        color: #6f8397;
        font-size: 0.74rem;
        margin-top: 0.15rem;
    }
    .spotlight-card {
        background: white;
        border: 1px solid #cedde9;
        border-radius: 16px;
        box-shadow: 0 9px 20px rgba(18, 60, 91, 0.06);
        min-height: 224px;
        padding: 0.72rem 0.84rem;
    }
    .spotlight-title {
        color: #143a5c;
        font-size: 1rem;
        font-weight: 800;
    }
    .spotlight-total {
        color: #143a5c;
        font-size: 1.58rem;
        font-weight: 800;
        margin-top: 0.24rem;
        line-height: 1.06;
    }
    .spotlight-note {
        color: #6f8397;
        font-size: 0.8rem;
        margin-top: 0.12rem;
        margin-bottom: 0.48rem;
    }
    .spotlight-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.42rem;
        margin-bottom: 0.65rem;
    }
    .spotlight-box {
        background: #f5f9fc;
        border-radius: 12px;
        padding: 0.48rem 0.55rem;
    }
    .spotlight-box-label {
        color: #6f8397;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .spotlight-box-value {
        color: #143a5c;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 0.16rem;
        line-height: 1.14;
    }
    .mini-row {
        display: grid;
        grid-template-columns: 1.15fr 1fr auto;
        gap: 0.36rem;
        align-items: center;
        margin-top: 0.36rem;
    }
    .mini-label {
        color: #143a5c;
        font-size: 0.77rem;
        font-weight: 600;
        line-height: 1.15;
    }
    .mini-bar {
        background: #e5eef6;
        border-radius: 999px;
        height: 7px;
        overflow: hidden;
    }
    .mini-fill {
        background: linear-gradient(90deg, #1f6fb2 0%, #4fa5d4 100%);
        display: block;
        height: 100%;
        border-radius: 999px;
    }
    .mini-value {
        color: #60788e;
        font-size: 0.76rem;
        font-weight: 700;
        white-space: nowrap;
    }
    [data-testid="stExpander"] details {
        background: white;
        border: 1px solid #cedde9;
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


try:
    df = load_data()
except FileNotFoundError:
    st.error("clean_data.csv was not found. Run clean_data.py first.")
    st.stop()


all_years = sorted(df["year"].dropna().astype(int).unique().tolist())
all_sectors = sorted(df["sector"].dropna().unique().tolist())
all_sources = sorted(df["sourceType"].dropna().unique().tolist())

sector_label_map = {labelize(value): value for value in all_sectors}
source_label_map = {labelize(value): value for value in all_sources}


top_row = st.columns([1.85, 1.05, 1.05, 1.05, 1.05], gap="small")

with top_row[0]:
    st.markdown(
        """
        <div class="top-band">
            <div class="top-title">Sri Lanka CO2 Emissions Dashboard</div>
            <div class="top-subtitle">
                Compact dashboard view of national emissions by sector, source type,
                subsector, and location.
            </div>
            <div class="top-meta">Coverage: 2024 and 2025 only | Gas: CO2e (20yr GWP) | Country: Sri Lanka | Single-page layout</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_row[1]:
    st.markdown("<div class='filter-card-label'>Year</div>", unsafe_allow_html=True)
    year_choice = st.selectbox(
        "Year",
        options=["All"] + [str(year) for year in all_years],
        index=0,
        label_visibility="collapsed",
    )
with top_row[2]:
    st.markdown("<div class='filter-card-label'>Sector</div>", unsafe_allow_html=True)
    sector_choice = st.selectbox(
        "Sector",
        options=["All sectors"] + list(sector_label_map.keys()),
        index=0,
        label_visibility="collapsed",
    )
with top_row[3]:
    st.markdown("<div class='filter-card-label'>Source Type</div>", unsafe_allow_html=True)
    source_choice = st.selectbox(
        "Source Type",
        options=["All sources"] + list(source_label_map.keys()),
        index=0,
        label_visibility="collapsed",
    )

selected_years = all_years if year_choice == "All" else [int(year_choice)]
selected_sectors = all_sectors if sector_choice == "All sectors" else [sector_label_map[sector_choice]]
selected_sources = all_sources if source_choice == "All sources" else [source_label_map[source_choice]]

filtered_df = df[
    (df["year"].isin(selected_years)) &
    (df["sector"].isin(selected_sectors)) &
    (df["sourceType"].isin(selected_sources))
].copy()

spotlight_options = sorted(filtered_df["sector"].dropna().unique().tolist())
if not spotlight_options:
    spotlight_options = selected_sectors if selected_sectors else all_sectors

default_spotlight = selected_sectors[0] if len(selected_sectors) == 1 else spotlight_options[0]
spotlight_index = spotlight_options.index(default_spotlight) if default_spotlight in spotlight_options else 0
with top_row[4]:
    st.markdown("<div class='filter-card-label'>Spotlight</div>", unsafe_allow_html=True)
    spotlight_sector = st.selectbox(
        "Sector Spotlight",
        options=spotlight_options,
        index=spotlight_index,
        format_func=labelize,
        label_visibility="collapsed",
    )

st.caption(
    f"Rows: {len(filtered_df):,} | Locations: {filtered_df['name'].nunique():,} | "
    f"Years: {', '.join(str(year) for year in selected_years)} | "
    f"Sector: {sector_choice} | Source: {source_choice}"
)


if filtered_df.empty:
    st.warning("No records match the current filter selection.")
    with st.expander("View filtered raw data", expanded=False):
        st.dataframe(filtered_df, use_container_width=True, height=240)
    st.stop()


total_emissions = filtered_df["emissions_mt"].sum()
location_count = filtered_df["name"].nunique()
row_count = len(filtered_df)

sector_summary = (
    filtered_df.groupby("sector", dropna=False)["emissions_mt"]
    .sum()
    .sort_values(ascending=False)
)
subsector_summary = (
    filtered_df.groupby("subsector", dropna=False)["emissions_mt"]
    .sum()
    .sort_values(ascending=False)
)
location_summary = (
    filtered_df.groupby("name", dropna=False)["emissions_mt"]
    .sum()
    .sort_values(ascending=False)
)
source_summary = (
    filtered_df.groupby("sourceType", dropna=False)["emissions_mt"]
    .sum()
    .sort_values(ascending=False)
)

top_sector_raw = sector_summary.index[0]
top_sector_value = float(sector_summary.iloc[0])
top_sector_share = (top_sector_value / total_emissions * 100) if total_emissions else 0

top_subsector_raw = subsector_summary.index[0]
top_subsector_value = float(subsector_summary.iloc[0])

top_location_raw = str(location_summary.index[0])
top_location_value = float(location_summary.iloc[0])

dominant_source_raw = source_summary.index[0]
dominant_source_share = (float(source_summary.iloc[0]) / total_emissions * 100) if total_emissions else 0

year_totals = (
    filtered_df.groupby("year", dropna=False)["emissions_mt"]
    .sum()
    .sort_index()
)
if len(year_totals) >= 2 and year_totals.iloc[0] != 0:
    year_change = ((year_totals.iloc[-1] - year_totals.iloc[0]) / year_totals.iloc[0]) * 100
    year_change_display = f"{year_change:+.1f}%"
    year_change_note = f"Latest selected year vs {int(year_totals.index[0])}"
else:
    year_change_display = "N/A"
    year_change_note = "Requires at least two selected years"


sector_totals = (
    sector_summary.reset_index()
    .rename(columns={"sector": "Category", "emissions_mt": "Emissions"})
)
sector_totals["Category"] = sector_totals["Category"].map(labelize)

subsector_totals = (
    subsector_summary.reset_index()
    .rename(columns={"subsector": "Category", "emissions_mt": "Emissions"})
    .head(6)
)
subsector_totals["Category"] = subsector_totals["Category"].map(labelize)

mix_chart_df = sector_totals if len(sector_totals) > 1 else subsector_totals
mix_chart_title = "Sector Emission Mix" if len(sector_totals) > 1 else "Subsector Emission Mix"
mix_chart_df["Share"] = (mix_chart_df["Emissions"] / mix_chart_df["Emissions"].sum()) * 100

source_type_share = (
    source_summary.reset_index()
    .rename(columns={"sourceType": "Source Type", "emissions_mt": "Emissions"})
)
source_type_share["Source Type"] = source_type_share["Source Type"].map(labelize)

source_type_trend = (
    filtered_df.groupby(["year", "sourceType"], dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
)
source_type_trend.columns = ["Year", "Source Type", "Emissions (Million Tonnes CO2)"]
source_type_trend["Year"] = source_type_trend["Year"].astype(int).astype(str)
source_type_trend["Source Type"] = source_type_trend["Source Type"].map(labelize)

year_sector = (
    filtered_df.groupby(["year", "sector"], dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
)
year_sector.columns = ["Year", "Sector", "Emissions (Million Tonnes CO2)"]
year_sector["Year"] = year_sector["Year"].astype(int).astype(str)
year_sector["Sector"] = year_sector["Sector"].map(labelize)

top_location_names = location_summary.head(6).index.tolist()
location_breakdown = (
    filtered_df[filtered_df["name"].isin(top_location_names)]
    .groupby(["name", "sector"], dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
)
location_breakdown.columns = ["Location", "Sector", "Emissions (Million Tonnes CO2)"]
ordered_names = [str(name) for name in top_location_names]
location_breakdown["Location"] = pd.Categorical(
    location_breakdown["Location"].astype(str),
    categories=ordered_names,
    ordered=True,
)
location_breakdown["Sector"] = location_breakdown["Sector"].map(labelize)

spotlight_df = filtered_df[filtered_df["sector"] == spotlight_sector].copy()
spotlight_total = spotlight_df["emissions_mt"].sum()
spotlight_share = (spotlight_total / total_emissions * 100) if total_emissions else 0

spotlight_location = "No data"
spotlight_source = "No data"
spotlight_subsector = "No data"
spotlight_rows = ""
if not spotlight_df.empty:
    spotlight_location = str(
        spotlight_df.groupby("name", dropna=False)["emissions_mt"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )
    spotlight_source = labelize(
        spotlight_df.groupby("sourceType", dropna=False)["emissions_mt"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )
    spotlight_subsector_series = (
        spotlight_df.groupby("subsector", dropna=False)["emissions_mt"]
        .sum()
        .sort_values(ascending=False)
    )
    spotlight_subsector = labelize(spotlight_subsector_series.index[0])
    max_value = float(spotlight_subsector_series.iloc[0]) if not spotlight_subsector_series.empty else 0
    for subsector_name, value in spotlight_subsector_series.head(4).items():
        width = 0 if max_value == 0 else (float(value) / max_value) * 100
        spotlight_rows += f"""
        <div class="mini-row">
            <div class="mini-label">{compact_text(labelize(subsector_name), 23)}</div>
            <div class="mini-bar"><span class="mini-fill" style="width:{max(width, 10):.1f}%"></span></div>
            <div class="mini-value">{float(value):.2f}M</div>
        </div>
        """


left_col, mid_col, right_col = st.columns([1.08, 0.84, 1.68], gap="small")

with left_col:
    with st.container(border=True):
        st.markdown(f"<div class='card-title'>{mix_chart_title}</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Largest contributors in the filtered view</div>", unsafe_allow_html=True)
        fig_mix = px.bar(
            mix_chart_df.sort_values("Emissions", ascending=True),
            x="Share",
            y="Category",
            orientation="h",
            text=mix_chart_df.sort_values("Emissions", ascending=True)["Share"].map(lambda x: f"{x:.1f}%"),
            color="Category",
            color_discrete_sequence=["#214F7D", "#3C7A57", "#6F9BC8", "#E07A00", "#8F5EA7", "#4C956C"],
        )
        fig_mix.update_layout(showlegend=False)
        fig_mix.update_traces(textposition="inside")
        fig_mix.update_xaxes(title_text=None, showgrid=False, visible=False)
        fig_mix.update_yaxes(title_text=None)
        style_figure(fig_mix, height=145, showlegend=False)
        st.plotly_chart(fig_mix, use_container_width=True, config=CHART_CONFIG)

    left_metrics = st.columns(2, gap="small")
    with left_metrics[0]:
        st.markdown(
            metric_block("Total CO2", f"{total_emissions:.1f}M", f"{row_count:,} filtered rows"),
            unsafe_allow_html=True,
        )
    with left_metrics[1]:
        st.markdown(
            metric_block("Locations", f"{location_count:,}", f"{top_location_value:.2f}M at {compact_text(top_location_raw, 14)}"),
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("<div class='card-title'>Emissions by Source Type</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Trend of aggregated versus point-source emissions</div>", unsafe_allow_html=True)
        if len(source_type_trend["Year"].unique()) > 1:
            fig_source = px.area(
                source_type_trend,
                x="Year",
                y="Emissions (Million Tonnes CO2)",
                color="Source Type",
                color_discrete_map=SOURCE_COLORS,
                markers=True,
            )
            fig_source.update_traces(mode="lines+markers")
            fig_source.update_xaxes(type="category")
        else:
            fig_source = px.bar(
                source_type_share,
                x="Source Type",
                y="Emissions",
                color="Source Type",
                color_discrete_map=SOURCE_COLORS,
            )
            fig_source.update_layout(showlegend=False)
        style_figure(fig_source, height=235, showlegend=True)
        st.plotly_chart(fig_source, use_container_width=True, config=CHART_CONFIG)

with mid_col:
    mid_metrics = st.columns(2, gap="small")
    with mid_metrics[0]:
        st.markdown(
            metric_block("Top Sector", compact_text(labelize(top_sector_raw), 13), f"{top_sector_share:.1f}% of filtered emissions"),
            unsafe_allow_html=True,
        )
    with mid_metrics[1]:
        st.markdown(
            metric_block("Year Change", year_change_display, year_change_note),
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("<div class='card-title'>Source Type Share</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>How the filtered total is split by source type</div>", unsafe_allow_html=True)
        fig_source_share = px.pie(
            source_type_share,
            names="Source Type",
            values="Emissions",
            hole=0.52,
            color="Source Type",
            color_discrete_map=SOURCE_COLORS,
        )
        fig_source_share.update_traces(textposition="inside", textinfo="percent")
        style_figure(fig_source_share, height=150, showlegend=True)
        st.plotly_chart(fig_source_share, use_container_width=True, config=CHART_CONFIG)

    st.markdown(
        f"""
        <div class="spotlight-card">
            <div class="spotlight-title">{labelize(spotlight_sector)} Spotlight</div>
            <div class="spotlight-total">{spotlight_total:.2f}M tonnes</div>
            <div class="spotlight-note">{spotlight_share:.1f}% of the filtered dashboard total</div>
            <div class="spotlight-grid">
                <div class="spotlight-box">
                    <div class="spotlight-box-label">Top Subsector</div>
                    <div class="spotlight-box-value">{compact_text(spotlight_subsector, 22)}</div>
                </div>
                <div class="spotlight-box">
                    <div class="spotlight-box-label">Top Location</div>
                    <div class="spotlight-box-value">{compact_text(spotlight_location, 22)}</div>
                </div>
                <div class="spotlight-box">
                    <div class="spotlight-box-label">Main Source</div>
                    <div class="spotlight-box-value">{compact_text(spotlight_source, 22)}</div>
                </div>
                <div class="spotlight-box">
                    <div class="spotlight-box-label">Coverage</div>
                    <div class="spotlight-box-value">{len(spotlight_df):,} rows</div>
                </div>
            </div>
            <div class="card-title" style="margin-bottom:0.05rem;">Leading Subsectors</div>
            {spotlight_rows if spotlight_rows else '<div class="card-subtitle">No spotlight breakdown available.</div>'}
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    with st.container(border=True):
        st.markdown("<div class='card-title'>Emissions Trend by Sector</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Movement across selected years</div>", unsafe_allow_html=True)
        fig_trend = px.line(
            year_sector,
            x="Year",
            y="Emissions (Million Tonnes CO2)",
            color="Sector",
            markers=True,
            line_shape="spline",
            color_discrete_map=SECTOR_COLORS,
        )
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_trend.update_xaxes(type="category")
        style_figure(fig_trend, height=220, showlegend=True)
        st.plotly_chart(fig_trend, use_container_width=True, config=CHART_CONFIG)

    with st.container(border=True):
        st.markdown("<div class='card-title'>Top Locations by Sector</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Largest emitting locations with sector breakdown</div>", unsafe_allow_html=True)
        fig_breakdown = px.bar(
            location_breakdown.sort_values("Location"),
            x="Location",
            y="Emissions (Million Tonnes CO2)",
            color="Sector",
            barmode="group",
            color_discrete_map=SECTOR_COLORS,
        )
        fig_breakdown.update_xaxes(title_text=None, tickangle=-22, categoryorder="array", categoryarray=ordered_names)
        fig_breakdown.update_yaxes(title_text="Emissions (Million Tonnes CO2)")
        style_figure(fig_breakdown, height=245, showlegend=True)
        st.plotly_chart(fig_breakdown, use_container_width=True, config=CHART_CONFIG)


st.caption("Data: Sri Lanka CO2 Equivalent Emissions | CO2e (20yr GWP) | 5DATA004C")
