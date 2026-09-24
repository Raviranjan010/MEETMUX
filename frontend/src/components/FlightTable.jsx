import React, { useState } from 'react';
import { formatDateTime, getDelayBadgeClass } from '../utils/formatters';
import { Info, Plane, X, AlertTriangle, ArrowRight, Clock, ShieldCheck, DoorClosed } from 'lucide-react';

export default function FlightTable({ flights = [], onSelectFlight }) {
  const [selectedFlight, setSelectedFlight] = useState(null);

  const handleRowClick = (flight) => {
    setSelectedFlight(flight);
    if (onSelectFlight) onSelectFlight(flight);
  };

  return (
    <div>
      <div className="table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Flight</th>
              <th>Airline</th>
              <th>Aircraft</th>
              <th>Route</th>
              <th>Arrival (UTC)</th>
              <th>Departure (UTC)</th>
              <th>Terminal</th>
              <th>Gate</th>
              <th>Predicted Delay</th>
              <th>Status</th>
              <th style={{ textAlign: 'center' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {flights.length === 0 ? (
              <tr>
                <td colSpan="11" style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--text-muted)' }}>
                  <Plane size={32} color="#FFB52E" style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                  <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No flights matching current filter criteria.</p>
                  <p style={{ fontSize: '0.75rem', marginTop: '4px' }}>Try adjusting your airline or delay search filters above.</p>
                </td>
              </tr>
            ) : (
              flights.map((f) => {
                const delayMin = f.latest_predicted_delay ?? f.taxi_in_minutes ?? 0;
                const category = f.latest_delay_category || (delayMin > 30 ? 'High' : delayMin > 15 ? 'Moderate' : delayMin > 5 ? 'Low' : 'On Time');
                const isDelayed = delayMin > 15;

                return (
                  <tr 
                    key={f.id} 
                    style={{ cursor: 'pointer' }} 
                    onClick={() => handleRowClick(f)}
                  >
                    <td className="mono" style={{ fontWeight: 800, color: '#FFB52E', fontSize: '0.9375rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Plane size={14} color="#FFB52E" style={{ transform: 'rotate(-45deg)' }} />
                        <span>{f.flight_number}</span>
                      </div>
                    </td>
                    <td style={{ fontWeight: 600 }}>{f.airline}</td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      <span style={{ padding: '2px 6px', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.05)', fontSize: '0.75rem' }}>
                        {f.aircraft_type}
                      </span>
                    </td>
                    <td className="mono">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 700 }}>{f.origin}</span>
                        <ArrowRight size={12} color="var(--text-muted)" />
                        <span style={{ color: 'var(--text-primary)', fontWeight: 700 }}>{f.destination}</span>
                      </div>
                    </td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      {formatDateTime(f.scheduled_arrival)}
                    </td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      {formatDateTime(f.scheduled_departure)}
                    </td>
                    <td>
                      <span style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(255, 181, 46, 0.08)', border: '1px solid rgba(255, 181, 46, 0.2)', fontWeight: 700, fontSize: '0.75rem', color: '#FFB52E' }}>
                        {f.terminal}
                      </span>
                    </td>
                    <td className="mono" style={{ fontWeight: 800, color: f.assigned_gate ? '#19D88A' : 'var(--text-muted)' }}>
                      {f.assigned_gate || '—'}
                    </td>
                    <td>
                      <span className={`badge ${getDelayBadgeClass(category)}`}>
                        +{delayMin.toFixed(1)}m • {category}
                      </span>
                    </td>
                    <td>
                      <span
                        style={{
                          fontSize: '0.8125rem',
                          fontWeight: 700,
                          color: isDelayed ? '#FF4D4D' : '#19D88A',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: isDelayed ? '#FF4D4D' : '#19D88A' }} />
                        {f.status || (isDelayed ? 'Delayed' : 'On Time')}
                      </span>
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '5px 10px', fontSize: '0.75rem', borderRadius: 'var(--radius-pill)' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFlight(f);
                        }}
                        title="View Flight Telemetry"
                      >
                        <Info size={13} color="#FFB52E" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Flight Detail Modal / Drawer */}
      {selectedFlight && (
        <div
          className="animate-fade-in"
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(7, 9, 12, 0.85)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 999,
            padding: '20px'
          }}
          onClick={() => setSelectedFlight(null)}
        >
          <div
            className="glass-card animate-slide-up"
            style={{
              maxWidth: '580px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              background: '#0B0E12',
              border: '1px solid rgba(255, 181, 46, 0.35)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 181, 46, 0.2)',
              padding: '24px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '10px',
                    background: 'rgba(255, 181, 46, 0.15)',
                    border: '1px solid rgba(255, 181, 46, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <Plane size={20} color="#FFB52E" />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
                    Flight {selectedFlight.flight_number}
                  </h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Aviation Operations Telemetry Record
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedFlight(null)}
                style={{
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  color: 'var(--text-secondary)',
                  padding: '6px',
                  cursor: 'pointer'
                }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Operating Carrier</span>
                <p style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{selectedFlight.airline}</p>
              </div>

              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Aircraft Type</span>
                <p className="mono" style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{selectedFlight.aircraft_type}</p>
              </div>

              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Flight Route</span>
                <p className="mono" style={{ fontWeight: 700, color: '#FFB52E' }}>
                  {selectedFlight.origin} → {selectedFlight.destination}
                </p>
              </div>

              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Terminal / Active Runway</span>
                <p className="mono" style={{ fontWeight: 700 }}>{selectedFlight.terminal} • {selectedFlight.runway || 'RWY-09L'}</p>
              </div>

              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Turnaround Buffer</span>
                <p className="mono" style={{ fontWeight: 700 }}>{selectedFlight.turnaround_minutes || 45} mins</p>
              </div>

              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span className="form-label">Assigned Gate</span>
                <p className="mono" style={{ fontWeight: 800, color: selectedFlight.assigned_gate ? '#19D88A' : 'var(--text-muted)' }}>
                  {selectedFlight.assigned_gate || 'Pending Optimization'}
                </p>
              </div>
            </div>

            {/* Delay Prediction Box */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(255, 181, 46, 0.1) 0%, rgba(255, 159, 28, 0.04) 100%)',
                border: '1px solid rgba(255, 181, 46, 0.3)',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                marginBottom: '20px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="form-label" style={{ color: '#FFB52E', margin: 0 }}>ML Queue & Taxi Inference</span>
                <span className={`badge ${getDelayBadgeClass(selectedFlight.latest_delay_category)}`}>
                  {selectedFlight.latest_delay_category || 'On Time'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#F5F7FA' }}>
                  +{(selectedFlight.latest_predicted_delay ?? 0).toFixed(1)}
                </span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>minutes predicted delay</span>
              </div>
            </div>

            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              onClick={() => setSelectedFlight(null)}
            >
              Dismiss View
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
