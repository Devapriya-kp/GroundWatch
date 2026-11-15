import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


DATA_PATH = "data/processed/groundwater_cleaned.csv"
OUTPUT_PATH = "data/processed/groundwater_anomalies_detected.csv"
MODEL_PATH = "models/anomaly_detector.pkl"


DATE_COL = "Data Acquisition Time"
STATION_COL = "Station_ID"
LEVEL_COL = "Groundwater Level Quarterly Manual (meter)"


def load_data():
    df = pd.read_csv(DATA_PATH)

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df[LEVEL_COL] = pd.to_numeric(df[LEVEL_COL], errors="coerce")

    df = df.dropna(subset=[DATE_COL, STATION_COL, LEVEL_COL])

    df = df.sort_values([STATION_COL, DATE_COL]).reset_index(drop=True)

    return df


def create_features(df):
    df = df.copy()

    grouped = df.groupby(STATION_COL)[LEVEL_COL]

    df["Previous_Level"] = grouped.shift(1)

    df["Level_Change"] = (
        df[LEVEL_COL] - df["Previous_Level"]
    )

    df["Rolling_Median"] = (
        df.groupby(STATION_COL)[LEVEL_COL]
        .transform(
            lambda x: x.shift(1).rolling(
                window=4, min_periods=2
            ).median()
        )
    )

    df["Rolling_Std"] = (
        df.groupby(STATION_COL)[LEVEL_COL]
        .transform(
            lambda x: x.shift(1).rolling(
                window=4, min_periods=2
            ).std()
        )
    )

    df["Deviation"] = (
        df[LEVEL_COL] - df["Rolling_Median"]
    )

    df["Deviation"] = df["Deviation"].fillna(0)
    df["Level_Change"] = df["Level_Change"].fillna(0)
    df["Rolling_Std"] = df["Rolling_Std"].fillna(0)

    return df


def detect_isolation_forest(df):
    features = [
        "Deviation",
        "Level_Change",
        "Rolling_Std"
    ]

    scaler = StandardScaler()

    X = scaler.fit_transform(df[features])

    model = IsolationForest(
        n_estimators=200,
        contamination=0.03,
        random_state=42
    )

    predictions = model.fit_predict(X)

    df["IF_Anomaly"] = np.where(
        predictions == -1, 1, 0
    )

    joblib.dump(
        {"model": model, "scaler": scaler, "features": features},
        MODEL_PATH
    )

    return df


def detect_rolling_zscore(df, threshold=3):
    df = df.copy()

    z_scores = (
        df["Deviation"] /
        df["Rolling_Std"].replace(0, np.nan)
    )

    df["Z_Score"] = z_scores.fillna(0)

    df["Z_Anomaly"] = (
        df["Z_Score"].abs() > threshold
    ).astype(int)

    return df


def classify_anomalies(df):
    df = df.copy()

    df["Anomaly_Label"] = np.where(
        (df["IF_Anomaly"] == 1) |
        (df["Z_Anomaly"] == 1),
        "Unusual",
        "Normal"
    )

    df["Anomaly_Reason"] = np.select(
        [
            (df["IF_Anomaly"] == 1) &
            (df["Z_Anomaly"] == 1),

            df["IF_Anomaly"] == 1,

            df["Z_Anomaly"] == 1
        ],
        [
            "Flagged by both methods",
            "Flagged by Isolation Forest",
            "Flagged by Rolling Z-Score"
        ],
        default="Within expected variation"
    )

    return df


def run_anomaly_detection():
    print("Loading groundwater dataset...")

    df = load_data()

    print("Creating anomaly detection features...")

    df = create_features(df)

    print("Running Isolation Forest...")

    df = detect_isolation_forest(df)

    print("Running Rolling Z-Score...")

    df = detect_rolling_zscore(df)

    print("Classifying anomalies...")

    df = classify_anomalies(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nANOMALY DETECTION COMPLETED")

    print("\nTotal records:", len(df))

    print("\nAnomaly results:")
    print(df["Anomaly_Label"].value_counts())

    print("\nDetection method comparison:")
    print("Isolation Forest:", df["IF_Anomaly"].sum())
    print("Rolling Z-Score:", df["Z_Anomaly"].sum())

    print("\nResults saved to:", OUTPUT_PATH)
    print("Model saved to:", MODEL_PATH)


if __name__ == "__main__":
    run_anomaly_detection()