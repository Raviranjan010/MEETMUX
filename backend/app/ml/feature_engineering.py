import pandas as pd
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts time, flight, congestion, and environmental features without data leakage.
    Predicts runway/taxi delay before the arrival/departure execution.
    Features used:
    - Time features: hour, day_of_week, month, is_weekend, is_peak_hour
    - Flight features: airline, aircraft_type, origin, destination, terminal, runway, scheduled_duration, turnaround_time
    - Airport congestion: active_flights, flights_per_hour, arrivals_per_hour, departures_per_hour
    - Weather features: temperature, wind_speed, visibility, precipitation, weather_condition
    """
    data = df.copy()

    # Parse dates if they are string
    if "scheduled_arrival" in data.columns and not pd.api.types.is_datetime64_any_dtype(data["scheduled_arrival"]):
        data["scheduled_arrival"] = pd.to_datetime(data["scheduled_arrival"])
    if "scheduled_departure" in data.columns and not pd.api.types.is_datetime64_any_dtype(data["scheduled_departure"]):
        data["scheduled_departure"] = pd.to_datetime(data["scheduled_departure"])

    # Base reference datetime (arrival)
    ref_dt = data["scheduled_arrival"] if "scheduled_arrival" in data.columns else pd.to_datetime("now")

    # Time features
    data["hour"] = ref_dt.dt.hour
    data["day_of_week"] = ref_dt.dt.dayofweek
    data["month"] = ref_dt.dt.month
    data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)
    data["is_peak_hour"] = data["hour"].isin([7, 8, 9, 17, 18, 19, 20]).astype(int)

    # Duration feature (in minutes)
    if "scheduled_arrival" in data.columns and "scheduled_departure" in data.columns:
        data["scheduled_duration_minutes"] = (data["scheduled_departure"] - data["scheduled_arrival"]).dt.total_seconds() / 60.0
        data["scheduled_duration_minutes"] = data["scheduled_duration_minutes"].clip(lower=20.0, upper=720.0)
    else:
        data["scheduled_duration_minutes"] = 60.0

    # Ensure default values for missing columns
    defaults = {
        "airline": "Air India",
        "aircraft_type": "A320",
        "origin": "DEL",
        "destination": "BOM",
        "terminal": "T3",
        "runway": "RWY-09L",
        "turnaround_minutes": 45.0,
        "temperature": 25.0,
        "wind_speed": 10.0,
        "visibility": 8.0,
        "precipitation": 0.0,
        "weather_condition": "Clear",
        "active_flights": 30,
        "flights_per_hour": 25,
        "arrivals_per_hour": 14,
        "departures_per_hour": 11
    }

    for col, default_val in defaults.items():
        if col not in data.columns:
            data[col] = default_val
        else:
            data[col] = data[col].fillna(default_val)

    return data
