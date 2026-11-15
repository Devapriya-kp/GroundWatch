import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/groundwater_anomalies_detected.csv"
OUTPUT_PATH = "data/processed/groundwater_risk_analysis.csv"


def classify_risk(df):

    conditions = [
        (df["IF_Anomaly"] == 1) & (df["Z_Anomaly"] == 1),
        (df["IF_Anomaly"] == 1) | (df["Z_Anomaly"] == 1)
    ]

    categories = ["HIGH", "MEDIUM"]

    df["Risk_Level"] = np.select(
        conditions,
        categories,
        default="LOW"
    )

    df["Risk_Explanation"] = np.select(
        conditions,
        [
            "Both detection methods identified an unusual reading.",
            "One detection method identified an unusual reading."
        ],
        default="Reading is within the detected normal variation."
    )

    df["Recommended_Action"] = np.select(
        conditions,
        [
            "Prioritize manual verification and investigate the station.",
            "Review the reading and monitor future measurements."
        ],
        default="Continue routine groundwater monitoring."
    )

    return df


def run_risk_analysis():

    print("Loading anomaly detection results...")

    df = pd.read_csv(INPUT_PATH)

    print("Classifying groundwater risk...")

    df = classify_risk(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nRISK ANALYSIS COMPLETED")

    print("\nRisk Distribution:")
    print(df["Risk_Level"].value_counts())

    print("\nResults saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    run_risk_analysis()