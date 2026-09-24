import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Login } from './pages/Login';
import { GenericModulePage } from './pages/GenericModulePage';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = localStorage.getItem('runwayoptx_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Login Route */}
      <Route path="/login" element={<Login />} />

      {/* Protected Command Center Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        <Route
          path="flights"
          element={
            <GenericModulePage
              title="FLIGHT SCHEDULES & PREDICTIONS"
              subtitle="Real-time flight arrival/departure queue with taxi delay risk"
              phaseRequired="Phase 3 & Phase 17"
              endpointDescription="GET /api/flights?page=1&page_size=25&route_type=&risk_level="
            />
          }
        />
        
        <Route
          path="gates"
          element={
            <GenericModulePage
              title="GATE INVENTORY & STATUS"
              subtitle="Terminal gates, compatibility matrices, and occupancy intervals"
              phaseRequired="Phase 6 & Phase 17"
              endpointDescription="GET /api/gates?status=&terminal=&gate_type="
            />
          }
        />

        <Route
          path="airport"
          element={
            <GenericModulePage
              title="AIRPORT OPERATIONS SVG MAP"
              subtitle="Interactive vector map showing runways, taxiways, gates and aircraft"
              phaseRequired="Phase 18"
              endpointDescription="GET /api/gates, GET /api/flights, GET /api/conflicts/detect"
            />
          }
        />

        <Route
          path="predictions"
          element={
            <GenericModulePage
              title="DELAY PREDICTIONS ENGINE"
              subtitle="Scikit-Learn regression model predicting actual taxi delays"
              phaseRequired="Phase 4 & Phase 5"
              endpointDescription="POST /api/predictions, GET /api/predictions/{flight_id}"
            />
          }
        />

        <Route
          path="optimizer"
          element={
            <GenericModulePage
              title="MILP GATE OPTIMIZER"
              subtitle="Gurobi / OR-Tools gate scheduling optimization solver"
              phaseRequired="Phase 9 & Phase 10"
              endpointDescription="POST /api/optimizer/run, GET /api/optimizer/{id}"
            />
          }
        />

        <Route
          path="scenarios"
          element={
            <GenericModulePage
              title="DISRUPTION SCENARIO RUNNER"
              subtitle="Simulate heavy rain, runway closure, gate blocks, and traffic surges"
              phaseRequired="Phase 12"
              endpointDescription="POST /api/scenarios/run, GET /api/scenarios"
            />
          }
        />

        <Route
          path="cascade"
          element={
            <GenericModulePage
              title="CASCADE DELAY PROPAGATION"
              subtitle="Graph BFS traversal tracing downstream delay effects"
              phaseRequired="Phase 13"
              endpointDescription="GET /api/cascade/{scenario_id}"
            />
          }
        />

        <Route
          path="timeline"
          element={
            <GenericModulePage
              title="GATE OCCUPANCY TIMELINE"
              subtitle="Gantt-chart view of gate assignments, turnaround buffers, and overlaps"
              phaseRequired="Phase 19"
              endpointDescription="GET /api/gates, GET /api/conflicts/detect"
            />
          }
        />

        <Route
          path="analytics"
          element={
            <GenericModulePage
              title="COMPARISON ANALYTICS"
              subtitle="Live fleet utilization and baseline vs optimized delta breakdown"
              phaseRequired="Phase 11 & Phase 20"
              endpointDescription="GET /api/analytics, GET /api/analytics/comparison?optimization_run_id="
            />
          }
        />

        <Route
          path="alerts"
          element={
            <GenericModulePage
              title="OPERATIONAL ALERTS"
              subtitle="Active conflicts, high delay risks, and solver warnings"
              phaseRequired="Phase 15 & Phase 20"
              endpointDescription="GET /api/alerts?resolved=false&severity="
            />
          }
        />

        <Route
          path="settings"
          element={
            <GenericModulePage
              title="SYSTEM CONFIGURATION"
              subtitle="Tune solver weights, risk thresholds, and turnaround buffer minutes"
              phaseRequired="Phase 15 & Phase 20"
              endpointDescription="GET /api/config, PUT /api/config"
            />
          }
        />
      </Route>

      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
