from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DashboardKPICards(BaseModel):
    total_flights: int
    delayed_flights: int
    delayed_percentage: float
    average_predicted_delay_minutes: float
    gates_available: int
    gates_utilized: int
    gates_total: int
    gate_utilization_rate: float
    active_conflicts: int
    latest_optimization_status: str
    latest_optimization_objective: Optional[float] = None
    latest_solver_runtime_seconds: Optional[float] = None


class DelayDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float
    color: str
    


class DelayByAirlineItem(BaseModel):
    airline: str
    avg_delay: float
    flight_count: int
    delayed_count: int


class CongestionByHourItem(BaseModel):
    hour: int
    time_label: str
    arrivals: int
    departures: int
    total_flights: int
    avg_delay: float


class GateOccupancyTimelineItem(BaseModel):
    gate_id: int
    gate_number: str
    terminal: str
    flight_id: int
    flight_number: str
    airline: str
    aircraft_type: str
    start_time: str
    end_time: str
    delay_minutes: float
    delay_category: str
    status: str


class WeatherImpactItem(BaseModel):
    condition: str
    avg_delay: float
    count: int


class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPICards
    delay_distribution: List[DelayDistributionItem]
    delay_by_airline: List[DelayByAirlineItem]
    congestion_by_hour: List[CongestionByHourItem]
    gate_occupancy: List[GateOccupancyTimelineItem]
    weather_impact: List[WeatherImpactItem]
    predicted_vs_actual: List[Dict[str, Any]]
