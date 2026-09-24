from datetime import datetime, timedelta
from typing import Tuple
from app.core.config import settings


def categorize_delay(delay_minutes: float) -> str:
    """
    Categorizes a delay in minutes into standard airport operational tiers:
    - On Time: <= DELAY_THRESHOLD_ON_TIME (default <= 5 min)
    - Low: (5, 15] min
    - Moderate: (15, 30] min
    - High: (30, 60] min
    - Severe: > 60 min
    """
    if delay_minutes <= settings.DELAY_THRESHOLD_ON_TIME:
        return "On Time"
    elif delay_minutes <= settings.DELAY_THRESHOLD_LOW:
        return "Low"
    elif delay_minutes <= settings.DELAY_THRESHOLD_MODERATE:
        return "Moderate"
    elif delay_minutes <= settings.DELAY_THRESHOLD_HIGH:
        return "High"
    else:
        return "Severe"


def get_delay_category_color(category: str) -> str:
    palette = {
        "On Time": "#10B981",   # emerald green
        "Low": "#3B82F6",       # blue
        "Moderate": "#F59E0B",  # amber/yellow
        "High": "#F97316",      # orange
        "Severe": "#EF4444",    # red
    }
    return palette.get(category, "#6B7280")


def check_time_overlap(
    start1: datetime, end1: datetime,
    start2: datetime, end2: datetime,
    buffer_minutes: float = 0.0
) -> bool:
    """
    Checks if two intervals [start1, end1 + buffer] and [start2, end2 + buffer] overlap.
    Intervals strictly overlap if: start1 < end2 + buffer and start2 < end1 + buffer.
    """
    buffered_end1 = end1 + timedelta(minutes=buffer_minutes)
    buffered_end2 = end2 + timedelta(minutes=buffer_minutes)
    return max(start1, start2) < min(buffered_end1, buffered_end2)


def get_occupancy_interval(
    arrival: datetime,
    departure: datetime,
    predicted_delay: float = 0.0,
    turnaround_minutes: float = 45.0
) -> Tuple[datetime, datetime]:
    """
    Computes expected gate occupancy start and end times, factoring in predicted delay and minimum turnaround.
    """
    effective_arrival = arrival + timedelta(minutes=max(0.0, predicted_delay))
    min_departure = effective_arrival + timedelta(minutes=turnaround_minutes)
    effective_departure = max(departure, min_departure)
    return effective_arrival, effective_departure
