import pytest
from app.models import SystemConfig
from app.models.enums import RiskLevel
from app.ml.risk import classify_flight_risk


def test_risk_classification_defaults():
    config = SystemConfig(
        risk_low_max_minutes=5.0,
        risk_medium_max_minutes=15.0,
    )

    # <= 5 is LOW
    assert classify_flight_risk(0.0, config) == RiskLevel.LOW
    assert classify_flight_risk(4.9, config) == RiskLevel.LOW
    assert classify_flight_risk(5.0, config) == RiskLevel.LOW

    # > 5 and <= 15 is MEDIUM
    assert classify_flight_risk(5.1, config) == RiskLevel.MEDIUM
    assert classify_flight_risk(10.0, config) == RiskLevel.MEDIUM
    assert classify_flight_risk(15.0, config) == RiskLevel.MEDIUM

    # > 15 is HIGH
    assert classify_flight_risk(15.1, config) == RiskLevel.HIGH
    assert classify_flight_risk(45.0, config) == RiskLevel.HIGH


def test_risk_classification_custom_config():
    config = SystemConfig(
        risk_low_max_minutes=3.0,
        risk_medium_max_minutes=10.0,
    )

    assert classify_flight_risk(3.0, config) == RiskLevel.LOW
    assert classify_flight_risk(3.5, config) == RiskLevel.MEDIUM
    assert classify_flight_risk(10.0, config) == RiskLevel.MEDIUM
    assert classify_flight_risk(10.1, config) == RiskLevel.HIGH
