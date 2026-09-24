import pytest
from datetime import datetime, timezone
from app.ml.features import (
    FEATURE_COLUMNS,
    compute_flight_features,
    compute_input_hash,
    encode_cyclical,
)


def test_feature_columns_defined():
    # AC-P4: Required feature columns per docs/ML.md
    expected = [
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
    for col in expected:
        assert col in FEATURE_COLUMNS, f"Missing feature column: {col}"


def test_cyclical_encoding():
    # Hour 0 and Hour 24 should have same cyclical encoding
    sin_0, cos_0 = encode_cyclical(0.0, 24.0)
    sin_12, cos_12 = encode_cyclical(12.0, 24.0)
    assert abs(sin_0) < 1e-6
    assert abs(cos_0 - 1.0) < 1e-6
    assert abs(cos_12 - (-1.0)) < 1e-6


def test_compute_flight_features():
    arr_dt = datetime(2026, 10, 1, 14, 30, tzinfo=timezone.utc)
    features = compute_flight_features(
        scheduled_arrival=arr_dt,
        route_type="INTERNATIONAL",
        aircraft_size_class="LARGE",
        airline="BA",
        runway_code="RWY-2",
        weather_condition="HEAVY_RAIN",
        traffic_density_30m=8,
        gate_type="REMOTE",
    )

    assert features["is_international"] == 1
    assert features["size_class_num"] == 3.0  # LARGE -> 3.0
    assert features["traffic_density_30m"] == 8
    assert features["gate_type_remote"] == 1
    assert features["weather_severity"] == 4.0  # HEAVY_RAIN -> 4.0


def test_compute_input_hash_deterministic():
    features = {
        "hour_sin": 0.5,
        "hour_cos": 0.866,
        "dow_sin": 0.0,
        "dow_cos": 1.0,
        "is_international": 0,
        "size_class_num": 1,
        "airline_code_num": 1,
        "runway_code_num": 0,
        "weather_severity": 0,
        "traffic_density_30m": 4,
        "gate_type_remote": 0,
    }
    hash1 = compute_input_hash(features)
    hash2 = compute_input_hash(features)
    assert hash1 == hash2
    assert len(hash1) == 12

