import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime

st.set_page_config(
    page_title="Global Earthquake Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Earthquake Dashboard")
st.caption("USGS Earthquake Data Visualization")

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("Filters")

year = st.sidebar.selectbox(
    "Select Year",
    list(range(2000, datetime.now().year + 1))[::-1]
)

min_mag = st.sidebar.slider(
    "Minimum Magnitude",
    min_value=1.0,
    max_value=9.0,
    value=4.5,
    step=0.1
)

region_filter = st.sidebar.selectbox(
    "Region",
    [
        "Global",
        "Asia",
        "North America",
        "South America",
        "Europe",
        "Africa",
        "Oceania",
        "Pacific Ring of Fire"
    ]
)


# =========================
# Data Loader
# =========================
@st.cache_data(show_spinner=False)
def load_data(year, min_mag):
    start = f"{year}-01-01"
    end = f"{year}-12-31"

    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson"
        f"&starttime={start}"
        f"&endtime={end}"
        f"&minmagnitude={min_mag}"
        f"&limit=20000"
    )

    response = requests.get(url)
    data = response.json()

    rows = []

    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        rows.append({
            "place": props["place"],
            "mag": props["mag"],
            "time": pd.to_datetime(props["time"], unit="ms"),
            "lon": coords[0],
            "lat": coords[1],
            "depth": coords[2]
        })

    return pd.DataFrame(rows)


# =========================
# Region Filter Logic
# =========================
REGIONS = {
    "Asia": {"lat": (5, 55), "lon": (60, 150)},
    "North America": {"lat": (10, 75), "lon": (-170, -50)},
    "South America": {"lat": (-60, 15), "lon": (-90, -30)},
    "Europe": {"lat": (35, 70), "lon": (-10, 40)},
    "Africa": {"lat": (-35, 38), "lon": (-20, 55)},
    "Oceania": {"lat": (-50, 0), "lon": (110, 180)},
    "Pacific Ring of Fire": {"lat": (-60, 60), "lon": (-180, 180)},
}

def filter_region(df, region):
    if region == "Global":
        return df

    if region == "Pacific Ring of Fire":
        return df[
            (
                ((df["lon"] >= 120) & (df["lon"] <= 180)) |
                ((df["lon"] >= -180) & (df["lon"] <= -70))
            )
        ]

    bounds = REGIONS[region]
    return df[
        (df["lat"] >= bounds["lat"][0]) &
        (df["lat"] <= bounds["lat"][1]) &
        (df["lon"] >= bounds["lon"][0]) &
        (df["lon"] <= bounds["lon"][1])
    ]


# =========================
# Load Data
# =========================
with st.spinner("Loading earthquake data..."):
    df = load_data(year, min_mag)

df = filter_region(df, region_filter)

if df.empty:
    st.warning("No data found.")
    st.stop()


# =========================
# Data Processing
# =========================
df["month"] = df["time"].dt.month

def extract_region(place):
    if "," in place:
        return place.split(",")[-1].strip()
    return "Unknown"

df["region_name"] = df["place"].apply(extract_region)

def mag_color(m):
    if m >= 7:
        return [255, 0, 0]
    elif m >= 6:
        return [255, 140, 0]
    elif m >= 5:
        return [255, 215, 0]
    return [0, 191, 255]

df["color"] = df["mag"].apply(mag_color)


# =========================
# KPI Cards
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("🌎 Total", f"{len(df):,}")
col2.metric("⚡ Max Mag", round(df["mag"].max(), 2))
col3.metric("📈 Avg Mag", round(df["mag"].mean(), 2))
col4.metric("🌍 Regions", df["region_name"].nunique())


# =========================
# Map
# =========================
st.subheader(f"🗺 Earthquake Map - {region_filter}")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius='mag * 15000',
    pickable=True,
    opacity=0.55
)

center_lat = df["lat"].mean()
center_lon = df["lon"].mean()

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=2 if region_filter != "Global" else 1
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "text": "Location: {place}\nMagnitude: {mag}\nDepth: {depth} km"
    }
)

st.pydeck_chart(deck)


# =========================
# Charts
# =========================
left, right = st.columns(2)

with left:
    st.subheader("📊 Monthly Earthquake Count")
    monthly = df.groupby("month").size()
    st.line_chart(monthly)

with right:
    st.subheader("📈 Magnitude Distribution")
    bins = pd.cut(df["mag"], bins=[0, 4, 5, 6, 7, 10])
    mag_dist = bins.value_counts().sort_index()
    st.bar_chart(mag_dist)


# =========================
# Top Regions
# =========================
st.subheader("🌎 Top 10 Most Active Regions")
region_stats = df.groupby("region_name").size().sort_values(ascending=False).head(10)
st.bar_chart(region_stats)


# =========================
# Raw Data
# =========================
with st.expander("Show Raw Data"):
    st.dataframe(df, use_container_width=True)
