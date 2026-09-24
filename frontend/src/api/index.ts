import { apiClient } from './client';
import {
  Flight,
  Gate,
  Prediction,
  Conflict,
  OptimizationRun,
  ScenarioResult,
  CascadeTree,
  Alert,
  SystemConfig,
} from './types';

export * from './types';
export { apiClient };

// Health
export const getHealth = async () => {
  const { data } = await apiClient.get('/api/health');
  return data;
};

// Flights
export const getFlights = async (params?: {
  page?: number;
  page_size?: number;
  route_type?: string;
  risk_level?: string;
  status?: string;
  search?: string;
  airline?: string;
}) => {
  const { data } = await apiClient.get('/api/flights', { params });
  return data as { total: number; page: number; page_size: number; items: Flight[] };
};

export const getFlight = async (id: string) => {
  const { data } = await apiClient.get(`/api/flights/${id}`);
  return data as Flight;
};

export const predictFlight = async (flightId: string) => {
  const { data } = await apiClient.post('/api/predictions', { flight_id: flightId });
  return data as Prediction;
};

export const batchPredict = async () => {
  const { data } = await apiClient.post('/api/predictions/batch');
  return data as { count: number; predictions: Prediction[] };
};

export const getPredictions = async () => {
  const { data } = await apiClient.get('/api/predictions');
  return data as Prediction[];
};

export const getPredictionMetrics = async () => {
  const { data } = await apiClient.get('/api/predictions/metrics');
  return data as {
    model_version: string;
    model_type: string;
    mae: number;
    rmse: number;
    r2: number;
    training_samples: number;
  };
};

// Gates
export const getGates = async (params?: {
  terminal?: string;
  gate_type?: string;
  status?: string;
}) => {
  const { data } = await apiClient.get('/api/gates', { params });
  return data as Gate[];
};

export const getGate = async (id: string) => {
  const { data } = await apiClient.get(`/api/gates/${id}`);
  return data as Gate;
};

// Conflicts
export const detectConflicts = async () => {
  const { data } = await apiClient.post('/api/conflicts/detect');
  return data as { count: number; conflicts: Conflict[] };
};

// Optimizer
export const runOptimizer = async (params?: {
  solver_choice?: string;
  timeout_seconds?: number;
  weights?: {
    conflicts?: number;
    gate_changes?: number;
    taxi_time?: number;
    towing?: number;
  };
}) => {
  const { data } = await apiClient.post('/api/optimizer/run', params || {});
  return data as OptimizationRun;
};

export const getOptimizationRun = async (id: string) => {
  const { data } = await apiClient.get(`/api/optimizer/${id}`);
  return data as OptimizationRun;
};

export const explainGateAssignment = async (flightId: string) => {
  const { data } = await apiClient.get(`/api/explain/${flightId}`);
  return data as {
    flight_id: string;
    assigned_gate: string;
    reasons: string[];
    hard_constraints_satisfied: string[];
    soft_score_breakdown: Record<string, number>;
    alternatives_evaluated: Array<{ gate: string; rank: number; score: number; reason: string }>;
  };
};

export const acceptAssignment = async (runId: string) => {
  const { data } = await apiClient.post(`/api/optimizer/${runId}/accept`);
  return data;
};

export const rejectAssignment = async (runId: string) => {
  const { data } = await apiClient.post(`/api/optimizer/${runId}/reject`);
  return data;
};

// Scenarios
export const getScenarios = async () => {
  const { data } = await apiClient.get('/api/scenarios');
  return data as Array<{ id: string; name: string; description: string; type: string }>;
};

export const runScenario = async (scenarioType: string, params?: Record<string, any>) => {
  const { data } = await apiClient.post('/api/scenarios/run', { scenario_type: scenarioType, ...(params || {}) });
  return data as ScenarioResult;
};

export const resetScenario = async () => {
  const { data } = await apiClient.post('/api/scenarios/reset');
  return data;
};

// Cascade
export const getCascadeAnalysis = async (scenarioId?: string) => {
  const { data } = await apiClient.get('/api/cascade', { params: { scenario_id: scenarioId } });
  return data as CascadeTree[];
};

// Re-optimize
export const runReoptimization = async () => {
  const { data } = await apiClient.post('/api/reoptimize');
  return data as {
    scenario_acknowledged: boolean;
    predictions_updated: number;
    conflicts_detected: number;
    optimization_run: OptimizationRun;
  };
};

// Analytics
export const getAnalytics = async () => {
  const { data } = await apiClient.get('/api/analytics');
  return data;
};

export const getComparisonAnalytics = async (optimizationRunId?: string) => {
  const { data } = await apiClient.get('/api/analytics/comparison', {
    params: { optimization_run_id: optimizationRunId },
  });
  return data;
};

// Alerts
export const getAlerts = async (params?: { resolved?: boolean; severity?: string }) => {
  const { data } = await apiClient.get('/api/alerts', { params });
  return data as Alert[];
};

export const resolveAlert = async (id: string) => {
  const { data } = await apiClient.post(`/api/alerts/${id}/resolve`);
  return data;
};

// Config
export const getConfig = async () => {
  const { data } = await apiClient.get('/api/config');
  return data as SystemConfig;
};

export const updateConfig = async (config: Partial<SystemConfig>) => {
  const { data } = await apiClient.put('/api/config', config);
  return data as SystemConfig;
};
