import axios from 'axios';

const getBaseURL = () => {
  const customUrl = typeof window !== 'undefined' ? localStorage.getItem('runwayoptx_api_url') : null;
  const envUrl = customUrl || import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL;
  if (envUrl && envUrl.trim()) {
    const cleanUrl = envUrl.trim().replace(/\/+$/, '');
    return cleanUrl.endsWith('/api') ? cleanUrl : `${cleanUrl}/api`;
  }
  return '/api';
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flights API
export const getFlights = (params) => api.get('/flights', { params });
export const getFlightById = (id) => api.get(`/flights/${id}`);
export const createFlight = (data) => api.post('/flights', data);
export const uploadFlightsCSV = (formData) => api.post('/flights/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

// Gates API
export const getGates = (params) => api.get('/gates', { params });
export const getGateById = (id) => api.get(`/gates/${id}`);

// Predictions API
export const predictDelay = (flightData) => api.post('/predictions/predict', flightData);
export const predictBatch = (data) => api.post('/predictions/batch', data);
export const getFeatureImportance = () => api.get('/predictions/feature-importance');
export const getModelMetrics = () => api.get('/predictions/metrics');
export const getFlightPrediction = (flightId) => api.get(`/predictions/${flightId}`);

// Optimization API
export const runOptimization = (payload) => api.post('/optimization/run', payload);
export const getOptimizationRun = (runId) => api.get(`/optimization/${runId}`);
export const getOptimizationAssignments = (runId) => api.get(`/optimization/${runId}/assignments`);

// Dashboard API
export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getHealth = () => api.get('/health');

export default api;
