export interface Flight {
  id: string;
  flight_number: string;
  airline: string;
  aircraft_type: string;
  origin: string;
  destination: string;
  route_type: 'DOMESTIC' | 'INTERNATIONAL';
  scheduled_arrival: string;
  scheduled_departure: string;
  estimated_arrival?: string;
  estimated_departure?: string;
  actual_arrival?: string;
  actual_departure?: string;
  arrival_runway_id?: string;
  departure_runway_id?: string;
  assigned_gate_id?: string;
  status: 'SCHEDULED' | 'BOARDING' | 'DEPARTED' | 'ARRIVED' | 'DELAYED' | 'CANCELLED';
  created_at?: string;
  prediction?: Prediction;
  assigned_gate?: Gate;
}

export interface Gate {
  id: string;
  terminal: string;
  gate_number: string;
  gate_type: 'DOMESTIC' | 'INTERNATIONAL' | 'SWING';
  max_aircraft_size: 'NARROW_BODY' | 'WIDE_BODY' | 'REGIONAL';
  status: 'AVAILABLE' | 'OCCUPIED' | 'RESERVED' | 'BLOCKED' | 'CONFLICT';
  current_flight_id?: string;
  latitude?: number;
  longitude?: number;
  current_flight?: Flight;
}

export interface Prediction {
  id: string;
  flight_id: string;
  predicted_taxi_out_minutes: number;
  predicted_delay_minutes: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence_score: number;
  features_used?: Record<string, any>;
  model_version: string;
  created_at: string;
}

export interface Conflict {
  gate_id: string;
  gate_number: string;
  flight_1_id: string;
  flight_1_number: string;
  flight_2_id: string;
  flight_2_number: string;
  overlap_start: string;
  overlap_end: string;
  overlap_minutes: number;
  severity: 'CRITICAL' | 'WARNING' | 'MINOR';
  reason: string;
}

export interface Assignment {
  flight_id: string;
  flight_number: string;
  assigned_gate_id: string;
  assigned_gate_number: string;
  baseline_gate_id?: string;
  baseline_gate_number?: string;
  gate_changed: boolean;
  scheduled_start: string;
  scheduled_end: string;
  status?: string;
}

export interface OptimizationRun {
  id: string;
  timestamp: string;
  solver: string;
  status: 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE' | 'REJECTED';
  objective_value: number;
  solve_time_seconds: number;
  is_valid: boolean;
  total_conflicts_before: number;
  total_conflicts_after: number;
  total_gate_changes: number;
  avg_taxi_delay_minutes: number;
  remote_stands_used: number;
  assignments: Assignment[];
  validation_errors?: string[];
}

export interface ScenarioResult {
  scenario_name: string;
  description: string;
  affected_flights_count: number;
  conflicts_detected: number;
  cascade_events_count: number;
  details: Record<string, any>;
}

export interface CascadeNode {
  flight_id: string;
  flight_number: string;
  gate_id: string;
  delay_minutes: number;
  risk_level: string;
  root_cause: string;
  depth: number;
  propagated_from?: string;
}

export interface CascadeTree {
  root_flight_id: string;
  root_cause: string;
  total_affected_flights: number;
  nodes: CascadeNode[];
}

export interface Alert {
  id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  message: string;
  timestamp: string;
  entity_type: string;
  entity_id: string;
  resolved: boolean;
}

export interface SystemConfig {
  turnaround_buffer_minutes: number;
  high_risk_delay_threshold: number;
  medium_risk_delay_threshold: number;
  solver_timeout_seconds: number;
  weight_conflicts: number;
  weight_gate_changes: number;
  weight_taxi_time: number;
  weight_towing: number;
  weight_unpreferred_gate: number;
}
