import enum

class RunwayStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

class GateType(str, enum.Enum):
    JETBRIDGE = "JETBRIDGE"
    REMOTE = "REMOTE"

class AircraftSizeClass(str, enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class RouteType(str, enum.Enum):
    DOMESTIC = "DOMESTIC"
    INTERNATIONAL = "INTERNATIONAL"

class GateEligibleRouteType(str, enum.Enum):
    DOMESTIC = "DOMESTIC"
    INTERNATIONAL = "INTERNATIONAL"
    BOTH = "BOTH"

class GateStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    BLOCKED = "BLOCKED"

class WeatherCondition(str, enum.Enum):
    CLEAR = "CLEAR"
    RAIN = "RAIN"
    HEAVY_RAIN = "HEAVY_RAIN"
    FOG = "FOG"
    SNOW = "SNOW"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RunType(str, enum.Enum):
    BASELINE = "BASELINE"
    MILP = "MILP"

class SolverUsed(str, enum.Enum):
    GUROBI = "GUROBI"
    ORTOOLS = "ORTOOLS"
    NONE = "NONE"

class OptimizationStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    TIMEOUT = "TIMEOUT"
    SOLVER_UNAVAILABLE = "SOLVER_UNAVAILABLE"
    ERROR = "ERROR"

class AssignmentStatus(str, enum.Enum):
    BASELINE = "BASELINE"
    PROPOSED = "PROPOSED"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"

class ScenarioType(str, enum.Enum):
    HEAVY_RAIN = "HEAVY_RAIN"
    RUNWAY_CLOSURE = "RUNWAY_CLOSURE"
    GATE_CLOSURE = "GATE_CLOSURE"
    TRAFFIC_SURGE = "TRAFFIC_SURGE"
    FLIGHT_DELAY = "FLIGHT_DELAY"
    GATE_CONFLICT = "GATE_CONFLICT"
    CASCADE_DELAY = "CASCADE_DELAY"

class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertCategory(str, enum.Enum):
    CONFLICT = "CONFLICT"
    HIGH_RISK = "HIGH_RISK"
    INFEASIBLE = "INFEASIBLE"
    SOLVER_ISSUE = "SOLVER_ISSUE"
    CASCADE = "CASCADE"

class AuditAction(str, enum.Enum):
    PREDICTION_RUN = "PREDICTION_RUN"
    OPTIMIZATION_RUN = "OPTIMIZATION_RUN"
    SCENARIO_RUN = "SCENARIO_RUN"
    ASSIGNMENT_ACCEPT = "ASSIGNMENT_ACCEPT"
    ASSIGNMENT_REJECT = "ASSIGNMENT_REJECT"
    DATA_UPLOAD = "DATA_UPLOAD"
