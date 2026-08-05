import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "dong_emergency_count.geojson"
SEOUL_CITY_HALL = {"lat": 37.5663, "lon": 126.9779}
MOKDONG_PREFIX = "목"

st.set_page_config(
    page_title="서울시 행정동별 출동건수",
    page_icon="🚨",
    layout="wide",
)


@st.cache_data

def load_geojson(path: Path) -> tuple[dict, pd.DataFrame]:
    """Load GeoJSON and convert feature properties to a DataFrame."""
    with path.open("r", encoding="utf-8") as file:
        geojson = json.load(file)

    records = [feature.get("properties", {}) for feature in geojson["features"]]
    df = pd.DataFrame(records)

    required_columns = {"ADM_NM", "ADM_CD", "emergency_count"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"GeoJSON에 필요한 속성이 없습니다: {missing}")

    df["ADM_CD"] = df["ADM_CD"].astype(str)
    df["emergency_count"] = pd.to_numeric(
        df["emergency_count"], errors="coerce"
    ).fillna(0)

    return geojson, df


def filter_geojson(geojson: dict, adm_codes: set[str]) -> dict:
    """Return a GeoJSON containing only the selected administrative codes."""
    return {
        "type": "FeatureCollection",
        "features": [
            feature
            for feature in geojson["features"]
            if str(feature.get("properties", {}).get("ADM_CD")) in adm_codes
        ],
    }


def iter_positions(coordinates):
    """Yield all [longitude, latitude] positions from nested GeoJSON coordinates."""
    if (
        isinstance(coordinates, list)
        and len(coordinates) >= 2
        and isinstance(coordinates[0], (int, float))
        and isinstance(coordinates[1], (int, float))
    ):
        yield coordinates[0], coordinates[1]
        return

    if isinstance(coordinates, list):
        for item in coordinates:
            yield from iter_positions(item)


def calculate_center(geojson: dict) -> dict[str, float]:
    """Calculate the center of the selected polygons from their bounding box."""
    positions = []
    for feature in geojson.get("features", []):
        positions.extend(iter_positions(feature["geometry"]["coordinates"]))

    if not positions:
        return SEOUL_CITY_HALL

    longitudes, latitudes = zip(*positions)
    return {
        "lat": (min(latitudes) + max(latitudes)) / 2,
        "lon": (min(longitudes) + max(longitudes)) / 2,
    }


try:
    full_geojson, full_df = load_geojson(DATA_PATH)
except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
    st.error(f"데이터를 불러오지 못했습니다: {error}")
    st.stop()

st.title("서울시 행정동별 출동건수")

# Toggle placed at the top of the page.
show_only_mokdong = st.toggle(
    "목동만 보기",
    value=False,
    help="켜면 목1동~목5동만 지도에 표시합니다.",
)

if show_only_mokdong:
    map_df = full_df[full_df["ADM_NM"].str.startswith(MOKDONG_PREFIX)].copy()
    selected_codes = set(map_df["ADM_CD"])
    map_geojson = filter_geojson(full_geojson, selected_codes)
    map_center = calculate_center(map_geojson)
    map_zoom = 12.2
else:
    map_df = full_df.copy()
    map_geojson = full_geojson
    map_center = SEOUL_CITY_HALL
    map_zoom = 9.7

if map_df.empty:
    st.warning("선택 조건에 해당하는 행정동이 없습니다.")
    st.stop()

# Keep a common color range so colors remain comparable when the toggle changes.
color_max = float(full_df["emergency_count"].max())
if color_max <= 0:
    color_max = 1.0

fig = px.choropleth_map(
    map_df,
    geojson=map_geojson,
    locations="ADM_CD",
    featureidkey="properties.ADM_CD",
    color="emergency_count",
    color_continuous_scale=[
        [0.0, "#ffffff"],
        [1.0, "#ff0000"],
    ],
    range_color=(0, color_max),
    hover_name="ADM_NM",
    hover_data={
        "ADM_CD": True,
        "emergency_count": ":,.0f",
    },
    center=map_center,
    zoom=map_zoom,
    map_style="carto-positron",
    opacity=0.82,
    labels={
        "ADM_CD": "행정동 코드",
        "emergency_count": "출동건수",
    },
)

fig.update_traces(
    marker_line_width=0.7,
    marker_line_color="#666666",
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "행정동 코드: %{location}<br>"
        "출동건수: %{z:,.0f}건"
        "<extra></extra>"
    ),
)

fig.update_layout(
    height=760,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    coloraxis_colorbar={
        "title": "출동건수",
        "ticksuffix": "건",
        "thickness": 16,
    },
    uirevision="mokdong-filter",
)

st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

scope_label = "목동" if show_only_mokdong else "서울 전체"
st.caption(
    f"표시 범위: {scope_label} · 행정동 {len(map_df):,}개 · "
    f"총 출동건수 {map_df['emergency_count'].sum():,.0f}건"
)
