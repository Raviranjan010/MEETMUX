import pytest
from datetime import datetime, timezone, timedelta
from app.services.conflict import (
    compute_occupied_interval,
    intervals_overlap,
    detect_conflicts_for_assignments,
)


def test_compute_occupied_interval():
    arr = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    dep = datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc)
    buffer = 15

    start, end = compute_occupied_interval(arr, dep, buffer)
    assert start == arr
    assert end == dep + timedelta(minutes=15)


def test_intervals_overlap():
    t0 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc)
    t3 = datetime(2026, 10, 1, 11, 30, tzinfo=timezone.utc)
    t4 = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)

    # Overlapping intervals
    assert intervals_overlap(t0, t1, t2, t3) is True
    assert intervals_overlap(t2, t3, t0, t1) is True

    # Non-overlapping intervals
    assert intervals_overlap(t0, t1, t3, t4) is False
    # Touching boundary with buffer (not strictly interior overlap)
    assert intervals_overlap(t0, t1, t1, t3) is False


def test_detect_conflicts_structure():
    t1 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc)
    t4 = datetime(2026, 10, 1, 11, 30, tzinfo=timezone.utc)

    assignments = [
        {
            "flight_id": "f1",
            "gate_id": "g1",
            "gate_code": "A1",
            "gate_status": "AVAILABLE",
            "arrival": t1,
            "departure": t2,
        },
        {
            "flight_id": "f2",
            "gate_id": "g1",
            "gate_code": "A1",
            "gate_status": "AVAILABLE",
            "arrival": t3,
            "departure": t4,
        },
    ]

    conflicts = detect_conflicts_for_assignments(assignments, buffer_minutes=15)
    assert len(conflicts) == 1

    c = conflicts[0]
    assert c["type"] == "TIME_OVERLAP"
    assert c["flight_id"] == "f1"
    assert c["conflicting_flight_id"] == "f2"
    assert c["gate_code"] == "A1"
    assert c["overlap_minutes"] > 0
    assert c["severity"] in ["CRITICAL", "HIGH", "WARNING"]
