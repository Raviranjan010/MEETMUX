import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.ml.feature_engineering import extract_features
from app.ml.preprocessing import build_preprocessor, ALL_FEATURE_COLUMNS
from app.ml.predict import predict_delay
from app.utils.time_utils import categorize_delay
from app.utils.metrics import calculate_regression_metrics


def test_feature_engineering_no_leakage():
    df = pd.DataFrame([{
        "flight_number": "AI101",
        "airline": "Air India",
        "aircraft_type": "A320",
        "origin": "DEL",
        "destination": "BOM",
        "terminal": "T3",
        "scheduled_arrival": datetime(2026, 9, 24, 14, 30),
        "scheduled_departure": datetime(2026, 9, 24, 16, 0),
        "active_flights": 40,
        "wind_speed": 12.0,
        "visibility": 6.0,
        "temperature": 28.0,
        "precipitation": 0.0,
        "weather_condition": "Clear"
    }])

    feat_df = extract_features(df)
    assert "hour" in feat_df.columns
    assert feat_df["hour"].iloc[0] == 14
    assert feat_df["is_peak_hour"].iloc[0] == 0
    assert "scheduled_duration_minutes" in feat_df.columns
    assert feat_df["scheduled_duration_minutes"].iloc[0] == 90.0


def test_delay_categorization_thresholds():
    assert categorize_delay(0.0) == "On Time"
    assert categorize_delay(5.0) == "On Time"
    assert categorize_delay(12.0) == "Low"
    assert categorize_delay(22.5) == "Moderate"
    assert categorize_delay(45.0) == "High"
    assert categorize_delay(75.0) == "Severe"


def test_regression_metrics_calculation():
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 31.0, 39.0])
    metrics = calculate_regression_metrics(y_true, y_pred)

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2" in metrics
    assert metrics["mae"] == 1.5
    assert metrics["r2"] > 0.95


def test_predict_delay_inference():
    input_data = {
        "flight_number": "6E202",
        "airline": "IndiGo",
        "aircraft_type": "A320",
        "origin": "BLR",
        "destination": "DEL",
        "terminal": "T1",
        "scheduled_arrival": datetime(2026, 9, 24, 8, 0),
        "scheduled_departure": datetime(2026, 9, 24, 9, 30),
        "active_flights": 50,
        "wind_speed": 15.0,
        "visibility": 4.0,
        "temperature": 26.0,
        "precipitation": 0.0,
        "weather_condition": "Clear"
    }

    results = predict_delay(input_data)
    assert len(results) == 1
    res = results[0]
    assert "predicted_delay_minutes" in res
    assert res["predicted_delay_minutes"] >= 0.0
    assert res["delay_category"] in ["On Time", "Low", "Moderate", "High", "Severe"]
