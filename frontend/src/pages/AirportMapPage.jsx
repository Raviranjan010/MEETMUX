import React, { useState, useEffect } from 'react';
import { getDashboardSummary } from '../services/api';
import GateMap from '../components/GateMap';
import LoadingSpinner from '../components/LoadingSpinner';
import { MapPin, Info } from 'lucide-react';

import { DEFAULT_DASHBOARD_DATA } from '../utils/mockData';

export default function AirportMapPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardSummary()
      .then((res) => {
        if (res?.data && res.data.gate_occupancy) {
          setData(res.data);
        } else {
          setData(DEFAULT_DASHBOARD_DATA);
        }
      })
      .catch((err) => {
        console.warn('Failed to load map data from live backend, using demo layout:', err);
        setData(DEFAULT_DASHBOARD_DATA);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading && !data) {
    return <LoadingSpinner text="Rendering airport concourse apron and live telemetry..." />;
  }

  const activeData = data || DEFAULT_DASHBOARD_DATA;

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <MapPin size={20} color="#FFB52E" />
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Airport Apron & Gate Concourse Map</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Real-time interactive aerial layout of Terminals 1, 2, and 3 with active aircraft docking states
        </p>
      </div>

      {/* Main Full-Size Map Component */}
      <div style={{ marginBottom: '24px' }}>
        <GateMap occupancy={activeData.gate_occupancy} />
      </div>

      {/* Airport Concourse Specification Panel */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Info size={18} color="#FFB52E" />
          <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Apron Facility Specifications</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', fontSize: '0.8125rem' }}>
          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="form-label">Terminal 1 (Domestic LCC)</span>
            <p style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Gates G11 – G18</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Narrowbody contact stands (A320, B737)</p>
          </div>

          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="form-label">Terminal 2 (Domestic & Regional)</span>
            <p style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Gates G21 – G26</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Mixed narrowbody & widebody stands</p>
          </div>

          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="form-label">Terminal 3 (International Hub)</span>
            <p style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Gates G31 – G38</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Heavy widebody dual-jetway stands (B777, A350, B787)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
