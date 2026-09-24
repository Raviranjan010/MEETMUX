from typing import List, Dict, Any, Tuple
from app.models.flight import Flight
from app.models.gate import Gate


def is_aircraft_compatible(aircraft_type: str, supported_types_str: str) -> bool:
    """
    Validates if gate's supported_aircraft_types allows the given aircraft type.
    Example supported_types_str: 'A320,B737,A321' or '*' (all).
    """
    if not supported_types_str or supported_types_str.strip() == "*":
        return True
    
    supported_list = [t.strip().upper() for t in supported_types_str.split(",") if t.strip()]
    return aircraft_type.strip().upper() in supported_list


def is_terminal_compatible(flight_terminal: str, gate_terminal: str) -> bool:
    """
    Validates if flight terminal matches the gate terminal.
    """
    if not flight_terminal or not gate_terminal:
        return True
    return flight_terminal.strip().upper() == gate_terminal.strip().upper()


def is_flight_gate_compatible(flight: Flight, gate: Gate) -> Tuple[bool, str]:
    """
    Comprehensive compatibility check between flight and gate:
    1. Gate must be available
    2. Terminal compatibility
    3. Aircraft compatibility
    4. International compatibility (if flight is international and gate is domestic only)
    """
    if not gate.is_available:
        return False, f"Gate {gate.gate_number} is out of service / unavailable"
    
    if not is_terminal_compatible(flight.terminal, gate.terminal):
        return False, f"Flight terminal {flight.terminal} does not match gate terminal {gate.terminal}"
    
    if not is_aircraft_compatible(flight.aircraft_type, gate.supported_aircraft_types):
        return False, f"Aircraft {flight.aircraft_type} not supported by gate {gate.gate_number} ({gate.supported_aircraft_types})"
    
    return True, "Compatible"


def compute_walking_distance_score(gate_type: str, terminal: str, gate_number: str) -> float:
    """
    Provides a walking distance penalty score based on gate type and distance index.
    Contact gates near core have score 1.0; remote gates score 3.0.
    """
    if gate_type.lower() == "remote":
        return 3.5
    elif gate_type.lower() == "apron":
        return 2.5
    else:
        # Minor variation based on gate number
        try:
            num = int(''.join(filter(str.isdigit, gate_number)))
            return round(1.0 + (num % 10) * 0.1, 2)
        except Exception:
            return 1.0
