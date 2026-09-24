import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Flights from './pages/Flights';
import Predictions from './pages/Predictions';
import GateOptimization from './pages/GateOptimization';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import AirportMapPage from './pages/AirportMapPage';
import Settings from './pages/Settings';

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleGlobalRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const toggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        {sidebarOpen && (
          <Sidebar isOpen={sidebarOpen} onCloseMobile={() => setSidebarOpen(false)} />
        )}
        <div className="main-content">
          <Navbar 
            onRefresh={handleGlobalRefresh} 
            onToggleSidebar={toggleSidebar} 
            sidebarOpen={sidebarOpen} 
          />
          <Routes key={refreshKey}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/flights" element={<Flights />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/optimization" element={<GateOptimization />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/map" element={<AirportMapPage />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
