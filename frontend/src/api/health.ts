import { apiClient } from './client';

export interface HealthResponse {
  status: 'ok' | 'degraded';
  database: boolean;
  ml_model_loaded: boolean;
  optimizer: {
    gurobi_available: boolean;
    ortools_available: boolean;
  };
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/api/health');
  return response.data;
}
