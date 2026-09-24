from typing import List, Tuple, Dict, Set
from datetime import datetime, timedelta
from app.optimization.models import FlightOptInput, GateOptInput
from app.utils.time_utils import check_time_overlap, get_occupancy_interval
from app.utils.validation import is_aircraft_compatible, is_terminal_compatible


def check_flight_gate_feasibility(flight: FlightOptInput, gate: GateOptInput) -> bool:
    """
    Evaluates hard feasibility constraints:
    - Gate must be operational and available
    - Aircraft type must be supported by gate
    - Terminal must match
    """
    if not gate.is_available:
        return False
    if not is_terminal_compatible(flight.terminal, gate.terminal):
        return False
    if not is_aircraft_compatible(flight.aircraft_type, gate.supported_aircraft_types):
        return False
    return True


def identify_overlapping_pairs(
    flights: List[FlightOptInput],
    buffer_minutes: float = 15.0
) -> List[Tuple[int, int]]:
    """
    Identifies all pairs of flights (f1, f2) where occupancy intervals overlap.
    Occupancy interval includes scheduled arrival + predicted delay to departure + turnaround.
    """
    overlapping_pairs = []
    n = len(flights)

    for i in range(n):
        f1 = flights[i]
        start1, end1 = get_occupancy_interval(
            f1.arrival_time, f1.departure_time,
            f1.predicted_delay_minutes, f1.turnaround_minutes
        )
        for j in range(i + 1, n):
            f2 = flights[j]
            start2, end2 = get_occupancy_interval(
                f2.arrival_time, f2.departure_time,
                f2.predicted_delay_minutes, f2.turnaround_minutes
            )
            if check_time_overlap(start1, end1, start2, end2, buffer_minutes):
                overlapping_pairs.append((f1.id, f2.id))

    return overlapping_pairs
