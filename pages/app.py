from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="서울시 증상별 응급출동 현황",
    page_icon="🚑",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load and preprocess the daily emergency dispatch dataset."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"데이터 파일을 찾을 수 없습니다: {csv_path}\n"
            "GitHub 저장소에 data/daily_emergency.csv가 있는지 확인하세요."
        )

    data = pd.read_csv(csv_path)

    required_date_column = "accident_ymd"
    if required_date_column not in data.columns:
        raise ValueError(f"날짜 열 '{required_date_column}'이 CSV에 없습니다.")

    # The source date is stored as YYYYMMDD, such as 20200101.
    data[required_date_column] = pd.to_datetime(
        data[required_date_column].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    if data[required_date_column].isna().any():
        invalid_rows = int(data[required_date_column].isna().sum())
        raise ValueError(f"날짜로 변환할 수 없는 행이 {invalid_rows}개 있습니다.")

    symptom_columns = [
        column for column in data.columns if column != required_date_column
    ]

    if not symptom_columns:
        raise ValueError("시각화할 증상 열이 없습니다.")

    # Convert symptom values to numbers. Invalid values become missing values.
    data[symptom_columns] = data[symptom_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    return data.sort_values(required_date_column).reset_index(drop=True)


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "daily_emergency.csv"

try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()

DATE_COLUMN = "accident_ymd"
SYMPTOM_COLUMNS = [column for column in df.columns if column != DATE_COLUMN]


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("🚑 서울시 증상별 응급출동 현황")
st.caption(
    "2020년 1월 1일부터 2022년 12월 31일까지의 일별 응급출동 횟수입니다. "
    "아래 토글을 사용하여 그래프에 표시할 증상을 선택하세요."
)


# -----------------------------------------------------------------------------
# Symptom toggle controls
# -----------------------------------------------------------------------------
st.subheader("증상 선택")

# Keep toggle states across Streamlit reruns.
for symptom in SYMPTOM_COLUMNS:
    state_key = f"show_{symptom}"
    if state_key not in st.session_state:
        st.session_state[state_key] = True

control_left, control_right, spacer = st.columns([1, 1, 6])

with control_left:
    if st.button("전체 선택", use_container_width=True):
        for symptom in SYMPTOM_COLUMNS:
            st.session_state[f"show_{symptom}"] = True
        st.rerun()

with control_right:
    if st.button("전체 해제", use_container_width=True):
        for symptom in SYMPTOM_COLUMNS:
            st.session_state[f"show_{symptom}"] = False
        st.rerun()

# Display up to five toggles per row.
TOGGLES_PER_ROW = 5
for start_index in range(0, len(SYMPTOM_COLUMNS), TOGGLES_PER_ROW):
    symptoms_in_row = SYMPTOM_COLUMNS[
        start_index : start_index + TOGGLES_PER_ROW
    ]
    toggle_columns = st.columns(TOGGLES_PER_ROW)

    for column, symptom in zip(toggle_columns, symptoms_in_row):
        with column:
            st.toggle(symptom, key=f"show_{symptom}")

selected_symptoms = [
    symptom
    for symptom in SYMPTOM_COLUMNS
    if st.session_state[f"show_{symptom}"]
]


# -----------------------------------------------------------------------------
# Plotly line chart
# -----------------------------------------------------------------------------
st.divider()
st.subheader("일별 응급출동 추이")

if not selected_symptoms:
    st.info("표시할 증상을 한 개 이상 선택하세요.")
else:
    figure = go.Figure()

    for symptom in selected_symptoms:
        figure.add_trace(
            go.Scatter(
                x=df[DATE_COLUMN],
                y=df[symptom],
                mode="lines",
                name=symptom,
                connectgaps=False,
                hovertemplate=(
                    f"증상: {symptom}<br>"
                    "날짜: %{x|%Y-%m-%d}<br>"
                    "출동 횟수: %{y:,.0f}회"
                    "<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        xaxis_title="날짜",
        yaxis_title="응급출동 횟수 (회)",
        hovermode="x unified",
        legend_title_text="증상",
        height=650,
        margin=dict(l=20, r=20, t=30, b=20),
    )

    figure.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1개월", step="month", stepmode="backward"),
                dict(count=3, label="3개월", step="month", stepmode="backward"),
                dict(count=6, label="6개월", step="month", stepmode="backward"),
                dict(count=1, label="1년", step="year", stepmode="backward"),
                dict(label="전체", step="all"),
            ]
        ),
    )

    figure.update_yaxes(rangemode="tozero", tickformat=",")

    st.plotly_chart(figure, use_container_width=True)

    st.caption(
        f"현재 {len(selected_symptoms)}개 증상을 표시하고 있습니다: "
        + ", ".join(selected_symptoms)
    )
