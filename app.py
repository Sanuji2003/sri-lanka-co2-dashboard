import pandas as pd
import plotly.express as px
import streamlit as st


# st.set_page_config must be the first Streamlit command.
st.set_page_config(
    page_title="Sri Lanka CO2 Emissions Dashboard",
    page_icon="\U0001F331",
    layout="wide",
)


# Load the cleaned CSV once and reuse it during interaction.
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("clean_data.csv")


try:
    df = load_data()
except FileNotFoundError:
    st.error("clean_data.csv was not found. Run clean_data.py first.")
    st.stop()


all_years = sorted(df["year"].dropna().astype(int).unique().tolist())
all_sectors = sorted(df["sector"].dropna().unique().tolist())


# Everything in st.sidebar appears in the left panel.
st.sidebar.title("\U0001F50D Filter the Data")
st.sidebar.markdown("Use these controls to explore the data.")

selected_years = st.sidebar.multiselect(
    label="Select Year(s)",
    options=all_years,
    default=all_years,
)

selected_sectors = st.sidebar.multiselect(
    label="Select Sector(s)",
    options=all_sectors,
    default=all_sectors,
)


# Apply both filters together.
filtered_df = df[
    (df["year"].isin(selected_years)) &
    (df["sector"].isin(selected_sectors))
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(f"Records shown: {len(filtered_df):,}")


st.title("\U0001F331 Sri Lanka CO2 Emissions Dashboard")
st.markdown(
    """
    This dashboard explores **CO2 equivalent emissions** across Sri Lanka.
    Data covers complete years **2024 and 2025** only.
    2026 data was excluded as it covers only ~9% of a full year.
    Use the filters on the left to explore different sectors and years.
    """
)

if filtered_df.empty:
    st.warning("No records match the current filters.")


st.subheader("\U0001F4CA Key Numbers at a Glance")
col1, col2, col3, col4 = st.columns(4)

total_emissions = filtered_df["emissions_mt"].sum()

if not filtered_df.empty:
    top_sector = filtered_df.groupby("sector")["emissions_mt"].sum().idxmax()
    top_location = filtered_df.groupby("name")["emissions_mt"].sum().idxmax()
    num_locations = filtered_df["name"].nunique()
else:
    top_sector = "No data"
    top_location = "No data"
    num_locations = 0

top_location_display = (
    top_location if len(str(top_location)) <= 24 else f"{str(top_location)[:21]}..."
)

col1.metric("Total CO2 Emissions", f"{total_emissions:.1f}M tonnes")
col2.metric("Top Emitting Sector", str(top_sector).replace("-", " ").title())
col3.metric("Top Emitting Location", top_location_display)
col4.metric("Locations Tracked", f"{num_locations:,}")

st.divider()


st.subheader("\U0001F3ED Which Sector Emits the Most CO2?")

sector_totals = (
    filtered_df.groupby("sector", dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
    .sort_values("emissions_mt", ascending=False)
)
sector_totals.columns = ["Sector", "Emissions (Million Tonnes CO2)"]
sector_totals["Sector"] = sector_totals["Sector"].str.replace("-", " ").str.title()

if sector_totals.empty:
    st.warning("No sector totals are available for the current filters.")
else:
    fig1 = px.bar(
        sector_totals,
        x="Sector",
        y="Emissions (Million Tonnes CO2)",
        color="Sector",
        title="Total CO2 Emissions by Sector",
        color_discrete_sequence=["#2E8B57", "#1E90FF", "#FF6347", "#FFD700"],
    )
    fig1.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)

    transport_total = filtered_df.loc[
        filtered_df["sector"] == "transportation", "emissions_mt"
    ].sum()
    if total_emissions > 0 and transport_total > 0:
        transport_share = transport_total / total_emissions * 100
        st.info(
            "Key Insight: Transportation is Sri Lanka's largest emitter "
            f"({transport_share:.1f}% of the filtered total)."
        )

st.divider()


st.subheader("\U0001F50D What Activities Are Causing Emissions?")

subsector_totals = (
    filtered_df.groupby("subsector", dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
    .sort_values("emissions_mt")
)
subsector_totals.columns = ["Subsector", "Emissions (Million Tonnes CO2)"]
subsector_totals["Subsector"] = (
    subsector_totals["Subsector"].str.replace("-", " ").str.title()
)

if subsector_totals.empty:
    st.warning("No subsector totals are available for the current filters.")
else:
    fig2 = px.bar(
        subsector_totals,
        x="Emissions (Million Tonnes CO2)",
        y="Subsector",
        orientation="h",
        title="CO2 Emissions by Subsector",
        color="Emissions (Million Tonnes CO2)",
        color_continuous_scale="Reds",
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()


st.subheader("\U0001F4C8 How Have Emissions Changed Year by Year?")

year_sector = (
    filtered_df.groupby(["year", "sector"], dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
)
year_sector.columns = ["Year", "Sector", "Emissions (Million Tonnes CO2)"]
year_sector["Sector"] = year_sector["Sector"].str.replace("-", " ").str.title()

if year_sector.empty:
    st.warning("No year-by-year trend is available for the current filters.")
else:
    fig3 = px.line(
        year_sector,
        x="Year",
        y="Emissions (Million Tonnes CO2)",
        color="Sector",
        markers=True,
        title="CO2 Emissions Trend by Sector (2024-2025)",
        line_shape="spline",
    )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()


st.subheader("\U0001F3C6 Which Specific Locations Emit the Most?")

location_count = filtered_df["name"].nunique()
if location_count == 0:
    st.warning("No locations are available for the current filters.")
else:
    slider_min = 5 if location_count >= 5 else 1
    slider_max = min(30, location_count)
    slider_value = min(15, slider_max)

    n_top = st.slider(
        label="How many top locations to show?",
        min_value=slider_min,
        max_value=slider_max,
        value=slider_value,
    )

    top_locations = (
        filtered_df.groupby("name", dropna=False)["emissions_mt"]
        .sum()
        .reset_index()
        .sort_values("emissions_mt", ascending=False)
        .head(n_top)
    )
    top_locations.columns = ["Location", "Emissions (Million Tonnes CO2)"]

    fig4 = px.bar(
        top_locations,
        x="Emissions (Million Tonnes CO2)",
        y="Location",
        orientation="h",
        title=f"Top {n_top} CO2 Emitting Locations",
        color="Emissions (Million Tonnes CO2)",
        color_continuous_scale="Oranges",
    )
    fig4.update_yaxes(autorange="reversed")
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()


st.subheader("\U0001F967 What Share of Total Emissions Does Each Sector Have?")

sector_share = (
    filtered_df.groupby("sector", dropna=False)["emissions_mt"]
    .sum()
    .reset_index()
)
sector_share.columns = ["Sector", "Emissions"]
sector_share["Sector"] = sector_share["Sector"].str.replace("-", " ").str.title()

if sector_share.empty:
    st.warning("No sector share is available for the current filters.")
else:
    fig5 = px.pie(
        sector_share,
        names="Sector",
        values="Emissions",
        title="Share of Total CO2 Emissions by Sector",
        hole=0.35,
        color_discrete_sequence=["#2E8B57", "#1E90FF", "#FF6347", "#FFD700"],
    )
    st.plotly_chart(fig5, use_container_width=True)

st.divider()


st.subheader("\U0001F50E Explore a Specific Sector in Detail")

detail_options = selected_sectors if selected_sectors else all_sectors
selected_sector_detail = st.selectbox(
    label="Choose a sector to explore:",
    options=detail_options,
    format_func=lambda x: x.replace("-", " ").title(),
)

sector_detail_df = filtered_df[filtered_df["sector"] == selected_sector_detail]

if sector_detail_df.empty:
    st.warning("No data for this sector with current filters.")
else:
    col_left, col_right = st.columns(2)

    with col_left:
        top_in = (
            sector_detail_df.groupby("name", dropna=False)["emissions_mt"]
            .sum()
            .reset_index()
            .sort_values("emissions_mt", ascending=False)
            .head(10)
        )
        top_in.columns = ["Location", "Emissions (M Tonnes)"]
        fig_l = px.bar(
            top_in,
            x="Emissions (M Tonnes)",
            y="Location",
            orientation="h",
            title=f"Top 10: {selected_sector_detail.replace('-', ' ').title()}",
        )
        fig_l.update_yaxes(autorange="reversed")
        fig_l.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_l, use_container_width=True)

    with col_right:
        sub_in = (
            sector_detail_df.groupby("subsector", dropna=False)["emissions_mt"]
            .sum()
            .reset_index()
        )
        sub_in.columns = ["Subsector", "Emissions (M Tonnes)"]
        sub_in["Subsector"] = sub_in["Subsector"].str.replace("-", " ").str.title()
        fig_r = px.pie(
            sub_in,
            names="Subsector",
            values="Emissions (M Tonnes)",
            title=f"Subsectors: {selected_sector_detail.replace('-', ' ').title()}",
            hole=0.3,
        )
        st.plotly_chart(fig_r, use_container_width=True)

st.divider()


st.subheader("\U0001F4CB View the Raw Data")
st.markdown("Browse the filtered data in table form.")

display_df = filtered_df[
    ["name", "sector", "subsector", "emissionsQuantity", "emissions_mt", "year"]
].copy()
display_df.columns = [
    "Location",
    "Sector",
    "Subsector",
    "Emissions (Tonnes)",
    "Emissions (M Tonnes)",
    "Year",
]
display_df["Sector"] = display_df["Sector"].str.replace("-", " ").str.title()
display_df["Subsector"] = display_df["Subsector"].str.replace("-", " ").str.title()
display_df = display_df.sort_values("Emissions (Tonnes)", ascending=False)

st.dataframe(display_df, use_container_width=True, height=300)

st.divider()
st.caption("Data: Sri Lanka CO2 Equivalent Emissions | Gas: CO2e (20yr GWP) | Sri Lanka")
st.caption("Dashboard: 5DATA004C - University of Westminster")
