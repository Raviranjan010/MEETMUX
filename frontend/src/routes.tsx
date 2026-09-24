import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Flights } from './pages/Flights';
import { Gates } from './pages/Gates';
import { AirportMap } from './pages/AirportMap';
import { Predictions } from './pages/Predictions';
import { Optimizer } from './pages/Optimizer';
import { Scenarios } from './pages/Scenarios';
import { Cascade } from './pages/Cascade';
import { Timeline } from './pages/Timeline';
import { Analytics } from './pages/Analytics';
import { Alerts } from './pages/Alerts';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';

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
        <Route path="flights" element={<Flights />} />
        <Route path="gates" element={<Gates />} />
        <Route path="airport" element={<AirportMap />} />
        <Route path="predictions" element={<Predictions />} />
        <Route path="optimizer" element={<Optimizer />} />
        <Route path="scenarios" element={<Scenarios />} />
        <Route path="cascade" element={<Cascade />} />
        <Route path="timeline" element={<Timeline />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
