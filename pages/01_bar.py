from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="증상별 응급출동 건수",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "daily_emergency.csv"
DATE_COLUMN = "accident_ymd"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Load the emergency-call data and convert the date column."""
    if not path.exists():
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {path}")

    data = pd.read_csv(path)

    if DATE_COLUMN not in data.columns:
        raise ValueError(f"CSV에 '{DATE_COLUMN}' 열이 없습니다.")

    data[DATE_COLUMN] = pd.to_datetime(
        data[DATE_COLUMN].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    data = data.dropna(subset=[DATE_COLUMN]).sort_values(DATE_COLUMN)

    symptom_columns = [column for column in data.columns if column != DATE_COLUMN]
    if not symptom_columns:
        raise ValueError("시각화할 증상 열이 없습니다.")

    data[symptom_columns] = data[symptom_columns].apply(
        pd.to_numeric,
        errors="coerce",
    ).fillna(0)

    return data


st.title("날짜별 증상별 응급출동 건수")
st.caption("날짜를 선택하면 해당 날짜의 증상별 응급출동 건수를 막대그래프로 보여줍니다.")

try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()

min_date = df[DATE_COLUMN].min().date()
max_date = df[DATE_COLUMN].max().date()

selected_date = st.date_input(
    "조회 날짜",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
    format="YYYY-MM-DD",
)

selected_timestamp = pd.Timestamp(selected_date)
selected_rows = df.loc[df[DATE_COLUMN] == selected_timestamp]

if selected_rows.empty:
    st.warning("선택한 날짜에 해당하는 데이터가 없습니다.")
    st.stop()

symptom_columns = [column for column in df.columns if column != DATE_COLUMN]
chart_data = (
    selected_rows[symptom_columns]
    .sum()
    .rename_axis("증상")
    .reset_index(name="출동 건수")
)

figure = px.bar(
    chart_data,
    x="증상",
    y="출동 건수",
    text="출동 건수",
    title=f"{selected_date:%Y년 %m월 %d일} 증상별 응급출동 건수",
    labels={"증상": "증상명", "출동 건수": "출동 건수"},
)
figure.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    hovertemplate="증상: %{x}<br>출동 건수: %{y:,.0f}건<extra></extra>",
)
figure.update_layout(
    xaxis_title="증상명",
    yaxis_title="출동 건수",
    yaxis_tickformat=",",
    margin=dict(t=70, r=30, b=40, l=50),
)

st.plotly_chart(figure, use_container_width=True)
st.metric("선택 날짜의 전체 출동 건수", f"{chart_data['출동 건수'].sum():,.0f}건")
