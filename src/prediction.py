import joblib
import pandas as pd
from pathlib import Path


# Locate the GroundWatch project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "groundwater_predictor.pkl"


# Load the trained Random Forest model
model = joblib.load(MODEL_PATH)


def predict_groundwater_level(historical_readings, next_date):
    """
    Predict the next available groundwater depth
    using historical readings from a single station.

    Parameters:
        historical_readings: List of previous groundwater readings
        next_date: Expected date of the next observation

    Returns:
        Predicted groundwater depth in metres below ground level.
    """

    if len(historical_readings) < 3:
        raise ValueError(
            "At least 3 historical readings are required."
        )

    readings = pd.Series(
        historical_readings,
        dtype=float
    )

    if readings.isna().any():
        raise ValueError("Historical readings cannot contain missing values.")

    next_date = pd.to_datetime(next_date)

    features = pd.DataFrame([{
        "Previous_Groundwater_Level": readings.iloc[-1],
        "Previous_2_Groundwater_Level": readings.iloc[-2],
        "Previous_3_Groundwater_Level": readings.iloc[-3],
        "Rolling_Average_3": readings.tail(3).mean(),
        "Month": next_date.month,
        "Year": next_date.year
    }])

    prediction = model.predict(features)

    return float(prediction[0])