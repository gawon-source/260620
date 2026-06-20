
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Earthquake Education Dashboard", layout="wide")
st.title("🌍 Earthquake Education Dashboard")
st.caption("USGS Earthquake Data + Scientific Insights")

REGIONS = {
    "Global": None,
    "Asia": {"lat": (5, 55), "lon": (60, 150)},
    "North America": {"lat": (10, 75), "lon": (-170, -50)},
    "South America": {"lat": (-60, 15), "lon": (-90, -30)},
    "Europe": {"lat": (35, 70), "lon": (-10, 40)},
    "Africa": {"lat": (-35, 38), "lon": (-20, 55)},
    "Oceania": {"lat": (-50, 0), "lon": (110, 180)}
}

@st.cache_data
def load_data(year, min_mag):
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start}&endtime={end}&minmagnitude={min_mag}&limit=5000"
    r = requests.get(url, timeout=30)
    data = r.json()
    rows = []
    for f in data.get("features", []):
        p = f["properties"]
        c = f["geometry"]["coordinates"]
        rows.append({
            "place": p["place"],
            "mag": p["mag"],
            "time": pd.to_datetime(p["time"], unit="ms"),
            "lon": c[0],
            "lat": c[1],
            "depth": c[2]
        })
    return pd.DataFrame(rows)

def filter_region(df, region):
    if region == "Global":
        return df
    b = REGIONS[region]
    return df[(df.lat>=b["lat"][0])&(df.lat<=b["lat"][1])&(df.lon>=b["lon"][0])&(df.lon<=b["lon"][1])]

year = st.sidebar.selectbox("Year", list(range(2000, datetime.now().year+1))[::-1])
min_mag = st.sidebar.slider("Min Magnitude", 4.0, 9.0, 4.5, 0.1)
region = st.sidebar.selectbox("Region", list(REGIONS.keys()))

df = load_data(year, min_mag)
if df.empty:
    st.warning("No data")
    st.stop()

df = filter_region(df, region)
if df.empty:
    st.warning("No data after filter")
    st.stop()

df["month"] = df["time"].dt.month

c1,c2,c3 = st.columns(3)
c1.metric("Earthquakes", len(df))
c2.metric("Max Magnitude", round(df.mag.max(),2))
c3.metric("Avg Magnitude", round(df.mag.mean(),2))

st.subheader("🗺 Map")
layer = pdk.Layer("ScatterplotLayer", data=df, get_position='[lon, lat]', get_radius='mag*12000', get_fill_color='[255,80,0,140]')
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(latitude=float(df.lat.mean()), longitude=float(df.lon.mean()), zoom=1.5)))

col1,col2 = st.columns(2)
with col1:
    monthly = df.groupby("month").size().reset_index(name="count")
    fig = px.line(monthly, x="month", y="count", title="Monthly Trend")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x="mag", nbins=20, title="Magnitude Distribution")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🧠 Educational Insights")
st.markdown("""
### Plate Tectonics
Most earthquakes occur near tectonic plate boundaries.

### Depth Analysis
- Shallow: 0–70 km  
- Intermediate: 70–300 km  
- Deep: 300+ km
""")

depth_bins = pd.cut(df["depth"], bins=[0,70,300,1000], labels=["Shallow","Intermediate","Deep"])
depth_df = depth_bins.value_counts().reset_index()
depth_df.columns=["depth_type","count"]
fig = px.bar(depth_df, x="depth_type", y="count", title="Depth Analysis")
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### Magnitude vs Energy Release
Each +1 magnitude ≈ 32x more energy.
- M5 = 1x
- M6 = 32x
- M7 = 1,000x
- M8 = 32,000x
""")

energy = pd.DataFrame({"Magnitude":["5","6","7","8"],"Energy":[1,32,1000,32000]})
fig = px.bar(energy, x="Magnitude", y="Energy", title="Energy Release")
st.plotly_chart(fig, use_container_width=True)
