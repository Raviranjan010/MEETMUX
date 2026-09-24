from app.optimization.models import FlightOptInput, GateOptInput, OptWeights
from app.utils.validation import compute_walking_distance_score


def compute_assignment_cost(
    flight: FlightOptInput,
    gate: GateOptInput,
    weights: OptWeights
) -> float:
    """
    Computes the scalar cost c[f, g] of assigning flight f to gate g based on:
    1. Passenger walking distance penalty (e.g. remote gate penalty)
    2. Delay propagation vulnerability (delayed flights assigned to critical contact gates)
    3. Gate reassignment penalty (if assigned gate differs from initially planned preferred gate)
    4. Terminal matching penalty
    """
    cost = 0.0

    # 1. Walking Distance penalty
    walk_score = compute_walking_distance_score(gate.gate_type, gate.terminal, gate.gate_number)
    cost += weights.walking_distance * walk_score

    # 2. Delay propagation penalty: If incoming flight has moderate/high delay, penalize tight turnarounds on core gates
    if flight.predicted_delay_minutes > 15.0:
        cost += weights.delay_propagation * (flight.predicted_delay_minutes / 10.0)

    # 3. Gate reassignment penalty
    if flight.preferred_gate_id is not None and flight.preferred_gate_id != gate.id:
        cost += weights.reassignment * 1.5

    # 4. Inconvenience factor for terminal cross-over if applicable
    if flight.terminal != gate.terminal:
        cost += 50.0  # Significant soft penalty if not strictly filtered

    return round(cost, 3)
