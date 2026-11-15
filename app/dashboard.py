
from pathlib import Path
import sys
from datetime import timedelta

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

sys.path.insert(0, str(PROJECT_ROOT))

CLEANED_PATH = DATA_DIR / "groundwater_cleaned.csv"
ANOMALY_PATH = DATA_DIR / "groundwater_anomalies_detected.csv"
RISK_PATH = DATA_DIR / "groundwater_risk_analysis.csv"

LEVEL_COL = "Groundwater Level Quarterly Manual (meter)"
DATE_COL = "Data Acquisition Time"
STATION_COL = "Station_ID"

st.set_page_config(
    page_title="GroundWatch",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. CUSTOM STYLING
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background-color: #262730;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 19px;
        color: #94a3b8;
    }

    .section-title {
        font-size: 27px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    .metric-card {
        background-color: #11212b;
        border: 1px solid #164e63;
        border-radius: 14px;
        padding: 20px;
        min-height: 115px;
    }

    .metric-label {
        font-size: 15px;
        color: #d1d5db;
    }

    .metric-value {
        font-size: 34px;
        font-weight: 600;
        color: white;
        margin-top: 8px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        padding: 25px;
        font-size: 15px;
    }

    hr {
        border-color: #374151;
        margin-top: 35px;
        margin-bottom: 35px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if RISK_PATH.exists():
        df = pd.read_csv(RISK_PATH)

    elif ANOMALY_PATH.exists():
        df = pd.read_csv(ANOMALY_PATH)

    elif CLEANED_PATH.exists():
        df = pd.read_csv(CLEANED_PATH)

    else:
        raise FileNotFoundError(
            "No processed groundwater dataset found."
        )

    df[DATE_COL] = pd.to_datetime(
        df[DATE_COL], errors="coerce"
    )

    df[LEVEL_COL] = pd.to_numeric(
        df[LEVEL_COL], errors="coerce"
    )

    df = df.dropna(
        subset=[DATE_COL, LEVEL_COL, STATION_COL]
    )

    df["State"] = df["State"].fillna("Unknown")
    df["District"] = df["District"].fillna("Unknown")
    df["Station"] = df["Station"].fillna("Unknown")

    if "Anomaly_Label" not in df.columns:
        df["Anomaly_Label"] = "Normal"

    if "Anomaly_Reason" not in df.columns:
        df["Anomaly_Reason"] = "No anomaly information available"

    if "IF_Anomaly" not in df.columns:
        df["IF_Anomaly"] = 0

    if "Z_Anomaly" not in df.columns:
        df["Z_Anomaly"] = 0

    if "Risk_Level" not in df.columns:
        df["Risk_Level"] = "LOW"

    if "Risk_Explanation" not in df.columns:
        df["Risk_Explanation"] = "No risk information available"

    if "Recommended_Action" not in df.columns:
        df["Recommended_Action"] = "Continue routine monitoring"

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"Unable to load groundwater data: {e}")
    st.stop()


# ============================================================
# 4. SIDEBAR FILTERS
# ============================================================

st.sidebar.title("⚙️ Dashboard Filters")

# State filter

states = ["All States"] + sorted(
    df["State"].dropna().unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "Select State",
    states
)

filtered = df.copy()

if selected_state != "All States":
    filtered = filtered[
        filtered["State"] == selected_state
    ]


# District filter

districts = ["All Districts"] + sorted(
    filtered["District"].dropna().unique().tolist()
)

selected_district = st.sidebar.selectbox(
    "Select District",
    districts
)

if selected_district != "All Districts":
    filtered = filtered[
        filtered["District"] == selected_district
    ]


# Station filter

stations = ["All Stations"] + sorted(
    filtered[STATION_COL].dropna().unique().tolist()
)

selected_station = st.sidebar.selectbox(
    "Select Station",
    stations
)

if selected_station != "All Stations":
    filtered = filtered[
        filtered[STATION_COL] == selected_station
    ]


# Risk filter

risk_options = [
    "All Risks",
    "HIGH",
    "MEDIUM",
    "LOW"
]

selected_risk = st.sidebar.selectbox(
    "Select Risk Level",
    risk_options
)

if selected_risk != "All Risks":
    filtered = filtered[
        filtered["Risk_Level"] == selected_risk
    ]


# Date filter

min_date = df[DATE_COL].min().date()
max_date = df[DATE_COL].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:

    start_date, end_date = date_range

    filtered = filtered[
        (filtered[DATE_COL].dt.date >= start_date) &
        (filtered[DATE_COL].dt.date <= end_date)
    ]


# ============================================================
# 5. HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💧 GroundWatch</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Groundwater Level Prediction & Anomaly Monitoring System'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    "An intelligent groundwater monitoring platform "
    "using historical CGWB Karnataka groundwater data."
)

st.markdown("---")


# ============================================================
# 6. DASHBOARD OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📊 Dashboard Overview</div>',
    unsafe_allow_html=True
)

total_records = len(filtered)

stations_monitored = filtered[STATION_COL].nunique()

normal_readings = (
    filtered["Anomaly_Label"] == "Normal"
).sum()

unusual_readings = (
    filtered["Anomaly_Label"] == "Unusual"
).sum()

high_risk = (
    filtered["Risk_Level"] == "HIGH"
).sum()

medium_risk = (
    filtered["Risk_Level"] == "MEDIUM"
).sum()

low_risk = (
    filtered["Risk_Level"] == "LOW"
).sum()


def metric_card(label, value):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Total Records", total_records)

with c2:
    metric_card("Stations Monitored", stations_monitored)

with c3:
    metric_card("Normal Readings", int(normal_readings))

with c4:
    metric_card("Unusual Readings", int(unusual_readings))


st.markdown("")

c5, c6, c7 = st.columns(3)

with c5:
    metric_card("🔴 High Risk", int(high_risk))

with c6:
    metric_card("🟠 Medium Risk", int(medium_risk))

with c7:
    metric_card("🟢 Low Risk", int(low_risk))


if filtered.empty:
    st.warning("No records match the selected filters.")


# ============================================================
# 7. GROUNDWATER ANALYSIS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">📈 Groundwater Analysis</div>',
    unsafe_allow_html=True
)

if not filtered.empty:

    # Groundwater trend

    st.subheader("Median Groundwater Level Trend")

    trend = (
        filtered.groupby(
            filtered[DATE_COL].dt.to_period("Q")
        )[LEVEL_COL]
        .median()
        .reset_index()
    )

    trend[DATE_COL] = trend[DATE_COL].astype(str)

    trend.columns = ["Observation Date", "Median Depth"]

    fig_trend = px.line(
        trend,
        x="Observation Date",
        y="Median Depth",
        markers=True,
        title="Groundwater Depth Over Time",
        template="plotly_dark"
    )

    fig_trend.update_traces(
        line=dict(color="#7cc7ff", width=3),
        marker=dict(size=6)
    )

    fig_trend.update_layout(
        xaxis_title="Observation Date",
        yaxis_title="Groundwater Depth (m bgl)",
        height=450
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


    # District comparison

    st.subheader("District-wise Groundwater Comparison")

    district_data = (
        filtered.groupby("District")[LEVEL_COL]
        .median()
        .reset_index()
        .sort_values(LEVEL_COL, ascending=False)
    )

    fig_district = px.bar(
        district_data,
        x="District",
        y=LEVEL_COL,
        color=LEVEL_COL,
        title="Median Groundwater Depth by District",
        color_continuous_scale="Blues",
        template="plotly_dark"
    )

    fig_district.update_layout(
        xaxis_title="District",
        yaxis_title="Median Depth (m bgl)",
        height=550,
        xaxis_tickangle=-90
    )

    st.plotly_chart(
        fig_district,
        use_container_width=True
    )


# ============================================================
# 8. ANOMALY DETECTION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🚨 Anomaly Detection</div>',
    unsafe_allow_html=True
)

if not filtered.empty:

    st.subheader("Normal vs Unusual Readings")

    anomaly_counts = (
        filtered["Anomaly_Label"]
        .value_counts()
        .reindex(["Normal", "Unusual"], fill_value=0)
        .reset_index()
    )

    anomaly_counts.columns = ["Anomaly", "Records"]

    fig_anomaly = px.pie(
        anomaly_counts,
        names="Anomaly",
        values="Records",
        hole=0.48,
        color="Anomaly",
        color_discrete_map={
            "Normal": "#636efa",
            "Unusual": "#ef553b"
        },
        title="Anomaly Distribution",
        template="plotly_dark"
    )

    fig_anomaly.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )


    # Anomaly table

    st.subheader("Unusual Groundwater Readings")

    anomaly_columns = [
        "Station",
        "District",
        DATE_COL,
        LEVEL_COL,
        "Anomaly_Label",
        "Anomaly_Reason"
    ]

    anomaly_details = filtered[
        filtered["Anomaly_Label"] == "Unusual"
    ]

    st.dataframe(
        anomaly_details[anomaly_columns]
        .sort_values(DATE_COL, ascending=False)
        .head(100),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Showing up to 100 unusual readings from the selected filters."
    )


# ============================================================
# 9. RISK ANALYSIS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">⚠️ Risk Analysis</div>',
    unsafe_allow_html=True
)

if not filtered.empty:

    st.subheader("Groundwater Risk Distribution")

    risk_data = (
        filtered["Risk_Level"]
        .value_counts()
        .reindex(["LOW", "MEDIUM", "HIGH"], fill_value=0)
        .reset_index()
    )

    risk_data.columns = ["Risk Level", "Records"]

    fig_risk = px.pie(
        risk_data,
        names="Risk Level",
        values="Records",
        hole=0.48,
        color="Risk Level",
        color_discrete_map={
            "LOW": "#20c463",
            "MEDIUM": "#ffa600",
            "HIGH": "#ef4444"
        },
        title="Groundwater Risk Distribution",
        template="plotly_dark"
    )

    fig_risk.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )


    # Risk details

    st.subheader("Risk Details and Recommended Actions")

    risk_details = filtered[
        filtered["Risk_Level"].isin(["HIGH", "MEDIUM"])
    ].copy()

    risk_details = risk_details.sort_values(
        DATE_COL,
        ascending=False
    )

    risk_columns = [
        "Station",
        "District",
        DATE_COL,
        LEVEL_COL,
        "Risk_Level",
        "Risk_Explanation",
        "Recommended_Action"
    ]

    if not risk_details.empty:

        st.dataframe(
            risk_details[risk_columns].head(100),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No HIGH or MEDIUM risk readings found.")

    st.caption(
        "HIGH = both anomaly methods flagged the reading. "
        "MEDIUM = one method flagged it. "
        "LOW = neither method flagged it."
    )


# ============================================================
# 10. GROUNDWATER PREDICTION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🔮 Groundwater Prediction</div>',
    unsafe_allow_html=True
)

st.write(
    "Predict the next available groundwater depth using "
    "the trained Random Forest model."
)

if CLEANED_PATH.exists():

    prediction_df = pd.read_csv(CLEANED_PATH)

    prediction_df[DATE_COL] = pd.to_datetime(
        prediction_df[DATE_COL],
        errors="coerce"
    )

    prediction_df[LEVEL_COL] = pd.to_numeric(
        prediction_df[LEVEL_COL],
        errors="coerce"
    )

    prediction_df = prediction_df.dropna(
        subset=[DATE_COL, LEVEL_COL, STATION_COL]
    )

    prediction_df = prediction_df.sort_values(DATE_COL)

    station_options = (
        prediction_df[
            ["Station", STATION_COL, "District"]
        ]
        .drop_duplicates()
        .sort_values(["District", "Station"])
    )

    station_options["Display"] = (
        station_options["Station"].astype(str)
        + " ("
        + station_options[STATION_COL].astype(str)
        + ")"
    )

    station_mapping = dict(
        zip(
            station_options["Display"],
            station_options[STATION_COL]
        )
    )

    selected_prediction_station = st.selectbox(
        "Choose a station for prediction",
        options=list(station_mapping.keys()),
        key="prediction_station"
    )

    station_id = station_mapping[
        selected_prediction_station
    ]

    station_history = prediction_df[
        prediction_df[STATION_COL] == station_id
    ].sort_values(DATE_COL)

    if not station_history.empty:

        latest_date = station_history[DATE_COL].max()

        latest_depth = float(
            station_history.iloc[-1][LEVEL_COL]
        )

        st.write(
            f"**Latest actual observation:** "
            f"{latest_date.strftime('%d %B %Y')}"
        )

        next_date = st.date_input(
            "Expected date of next observation",
            value=latest_date.date() + timedelta(days=90),
            min_value=latest_date.date() + timedelta(days=1),
            key="prediction_date"
        )

        if st.button(
            "🔮 Predict Groundwater Level",
            type="primary"
        ):

            if len(station_history) < 3:

                st.error(
                    "At least 3 historical readings are required."
                )

            else:

                try:

                    from src.prediction import (
                        predict_groundwater_level
                    )

                    historical_readings = (
                        station_history[LEVEL_COL]
                        .astype(float)
                        .tolist()
                    )

                    predicted_depth = (
                        predict_groundwater_level(
                            historical_readings,
                            next_date
                        )
                    )

                    if not np.isfinite(predicted_depth):
                        raise ValueError(
                            "The model returned an invalid prediction."
                        )

                    change = predicted_depth - latest_depth

                    st.session_state["prediction_result"] = {
                        "station": station_id,
                        "latest_date": latest_date,
                        "next_date": next_date,
                        "latest_depth": latest_depth,
                        "predicted_depth": predicted_depth,
                        "change": change
                    }

                except Exception as e:

                    st.error(
                        f"Prediction failed: {e}"
                    )

        # Display saved prediction

        result = st.session_state.get(
            "prediction_result"
        )

        if (
            result is not None
            and result["station"] == station_id
            and result["next_date"] == next_date
        ):

            st.success(
                "Prediction generated successfully!"
            )

            p1, p2, p3 = st.columns(3)

            with p1:
                st.metric(
                    "Latest Actual Depth",
                    f"{result['latest_depth']:.2f} m"
                )

            with p2:
                st.metric(
                    "Predicted Depth",
                    f"{result['predicted_depth']:.2f} m"
                )

            with p3:
                st.metric(
                    "Change in Depth",
                    f"{result['change']:+.2f} m"
                )

            if result["change"] > 0:

                st.warning(
                    "Predicted depth is greater than the previous "
                    "reading. This indicates a deeper water table."
                )

            elif result["change"] < 0:

                st.info(
                    "Predicted depth is lower than the previous "
                    "reading. This indicates a shallower water table."
                )

            else:

                st.info(
                    "Predicted depth is approximately unchanged."
                )

            # Historical vs predicted chart

            st.subheader(
                "Historical vs Predicted Groundwater Levels"
            )

            chart_history = station_history[
                [DATE_COL, LEVEL_COL]
            ].copy()

            chart_history.columns = [
                "Observation Date",
                "Groundwater Depth"
            ]

            fig_prediction = go.Figure()

            fig_prediction.add_trace(
                go.Scatter(
                    x=chart_history["Observation Date"],
                    y=chart_history["Groundwater Depth"],
                    mode="lines+markers",
                    name="Actual",
                    line=dict(
                        color="#7cc7ff",
                        width=2
                    )
                )
            )

            fig_prediction.add_trace(
                go.Scatter(
                    x=[pd.Timestamp(result["next_date"])],
                    y=[result["predicted_depth"]],
                    mode="markers",
                    name="Predicted",
                    marker=dict(
                        color="#007bff",
                        size=13,
                        symbol="diamond"
                    )
                )
            )

            fig_prediction.update_layout(
                template="plotly_dark",
                height=450,
                xaxis_title="Observation Date",
                yaxis_title="Groundwater Depth (m bgl)",
                legend_title="Reading Type"
            )

            st.plotly_chart(
                fig_prediction,
                use_container_width=True
            )

            st.caption(
                "The prediction is an estimate for the selected "
                "next-observation date, not a guaranteed forecast."
            )

else:

    st.warning(
        "Cleaned groundwater dataset is missing. "
        "Prediction cannot be performed."
    )


# ============================================================
# 11. FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
<div class="footer">
    <h2>💧 GroundWatch</h2>
    <p>Groundwater Level Prediction & Anomaly Monitoring System</p>
    <p>Developed using Python, Streamlit, Pandas and Machine Learning.</p>
    <p>Data Source: Central Ground Water Board (CGWB), Karnataka</p>
</div>
""", unsafe_allow_html=True)
