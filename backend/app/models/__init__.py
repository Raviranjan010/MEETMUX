from app.models.base import Base, GUID, CommonMixin
from app.models.enums import (
    RunwayStatus,
    GateType,
    AircraftSizeClass,
    RouteType,
    GateEligibleRouteType,
    GateStatus,
    WeatherCondition,
    RiskLevel,
    RunType,
    SolverUsed,
    OptimizationStatus,
    AssignmentStatus,
    ScenarioType,
    AlertSeverity,
    AlertCategory,
    AuditAction,
)
from app.models.airport import Airport, Terminal, Runway
from app.models.gate import Gate
from app.models.flight import Aircraft, Flight, WeatherRecord
from app.models.prediction import Prediction
from app.models.optimization import OptimizationRun, GateAssignment
from app.models.scenario import Scenario, CascadeEvent
from app.models.alert import Alert
from app.models.audit import AuditRecord
from app.models.config import SystemConfig

__all__ = [
    "Base",
    "GUID",
    "CommonMixin",
    # Enums
    "RunwayStatus",
    "GateType",
    "AircraftSizeClass",
    "RouteType",
    "GateEligibleRouteType",
    "GateStatus",
    "WeatherCondition",
    "RiskLevel",
    "RunType",
    "SolverUsed",
    "OptimizationStatus",
    "AssignmentStatus",
    "ScenarioType",
    "AlertSeverity",
    "AlertCategory",
    "AuditAction",
    # 14 Entities
    "Airport",
    "Terminal",
    "Runway",
    "Gate",
    "Aircraft",
    "Flight",
    "WeatherRecord",
    "Prediction",
    "OptimizationRun",
    "GateAssignment",
    "Scenario",
    "Alert",
    "CascadeEvent",
    "AuditRecord",
    # Config
    "SystemConfig",
]
