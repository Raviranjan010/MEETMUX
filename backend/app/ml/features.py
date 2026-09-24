import math
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "is_international",
    "size_class_num",
    "airline_code_num",
    "runway_code_num",
    "weather_severity",
    "traffic_density_30m",
    "gate_type_remote",
]

AIRLINES_MAP = {"AA": 0, "DL": 1, "UA": 2, "BA": 3, "LH": 4, "AF": 5, "OTHER": 6}
RUNWAYS_MAP = {"RWY-1": 0, "RWY-2": 1, "OTHER": 2}
SIZE_CLASS_MAP = {"SMALL": 1, "MEDIUM": 2, "LARGE": 3}
WEATHER_SEVERITY_MAP = {
    "CLEAR": 0.0,
    "CLOUDY": 0.5,
    "RAIN": 2.0,
    "HEAVY_RAIN": 4.0,
    "THUNDERSTORM": 6.0,
    "FOG": 3.0,
    "WINDY": 1.5,
    "SNOW": 5.0,
}


def encode_cyclical(val: float, period: float):
    """Encodes a scalar value into sin and cos components with a given period."""
    sin_val = math.sin(2 * math.pi * val / period)
    cos_val = math.cos(2 * math.pi * val / period)
    return sin_val, cos_val


def compute_flight_features(
    scheduled_arrival: datetime,
    route_type: str,
    aircraft_size_class: str,
    airline: str,
    runway_code: str,
    weather_condition: str,
    traffic_density_30m: int,
    gate_type: Optional[str] = None,
) -> Dict[str, float]:
    """
    Computes model features available strictly at prediction time.
    No post-actual or leaky features used.
    """
    hour = scheduled_arrival.hour + scheduled_arrival.minute / 60.0
    dow = scheduled_arrival.weekday()

    hour_sin, hour_cos = encode_cyclical(hour, 24.0)
    dow_sin, dow_cos = encode_cyclical(dow, 7.0)

    is_international = 1.0 if str(route_type).upper() == "INTERNATIONAL" else 0.0
    size_class_num = float(SIZE_CLASS_MAP.get(str(aircraft_size_class).upper(), 2))
    airline_code_num = float(AIRLINES_MAP.get(str(airline).upper(), AIRLINES_MAP["OTHER"]))
    runway_code_num = float(RUNWAYS_MAP.get(str(runway_code).upper(), RUNWAYS_MAP["OTHER"]))
    weather_severity = float(WEATHER_SEVERITY_MAP.get(str(weather_condition).upper(), 0.0))
    traffic_density = float(max(0, traffic_density_30m))
    gate_type_remote = 1.0 if gate_type and str(gate_type).upper() == "REMOTE" else 0.0

    return {
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "dow_sin": dow_sin,
        "dow_cos": dow_cos,
        "is_international": is_international,
        "size_class_num": size_class_num,
        "airline_code_num": airline_code_num,
        "runway_code_num": runway_code_num,
        "weather_severity": weather_severity,
        "traffic_density_30m": traffic_density,
        "gate_type_remote": gate_type_remote,
    }


def compute_input_hash(features: Dict[str, float]) -> str:
    """Computes SHA-256 hash of the input feature vector for model provenance tracking."""
    sorted_items = sorted(features.items())
    raw = "|".join(f"{k}:{v:.4f}" for k, v in sorted_items)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
