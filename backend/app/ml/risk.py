"""
Risk classification per docs/ML.md §Risk classification.
FR-4: Classify predicted delay into LOW/MEDIUM/HIGH risk using configurable thresholds.
"""
from typing import Optional
from app.models.enums import RiskLevel
from app.models.config import SystemConfig


def classify_risk(
    predicted_delay_minutes: float,
    risk_low_max: float = 5.0,
    risk_medium_max: float = 15.0,
) -> RiskLevel:
    """
    Pure function classifying operational delay risk into LOW, MEDIUM, HIGH.
    Uses configurable thresholds per REQUIREMENTS R9 and docs/ML.md.
    delay <= risk_low_max -> LOW
    risk_low_max < delay <= risk_medium_max -> MEDIUM
    delay > risk_medium_max -> HIGH
    """
    delay = float(predicted_delay_minutes)
    if delay <= risk_low_max:
        return RiskLevel.LOW
    elif delay <= risk_medium_max:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.HIGH


def classify_flight_risk(
    predicted_delay_minutes: float,
    config: Optional[SystemConfig] = None,
) -> RiskLevel:
    """Classifies risk level dynamically using SystemConfig thresholds from database."""
    low_max = float(config.risk_low_max_minutes) if config else 5.0
    medium_max = float(config.risk_medium_max_minutes) if config else 15.0
    return classify_risk(predicted_delay_minutes, low_max, medium_max)
