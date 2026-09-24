import React, { useState } from 'react';
import { formatDateTime, getDelayBadgeClass, getDelayColor } from '../utils/formatters';
import { 
  Layers, 
  Plane, 
  Maximize2, 
  Minimize2, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Clock, 
  DoorClosed, 
  CheckCircle2, 
  AlertTriangle,
  X,
  MapPin,
  Calendar
} from 'lucide-react';

export default function GateMap({ occupancy = [] }) {
  const [selectedTerminal, setSelectedTerminal] = useState('ALL');
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'timeline'
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedGate, setSelectedGate] = useState(null);

  // Group occupancy by gate
  const gateMap = {};
  occupancy.forEach((item) => {
    if (!gateMap[item.gate_number]) {
      gateMap[item.gate_number] = {
        gate_number: item.gate_number,
        terminal: item.terminal,
        gate_id: item.gate_id,
        flights: []
      };
    }
    gateMap[item.gate_number].flights.push(item);
  });

  const filteredGates = Object.values(gateMap).filter(
    (g) => selectedTerminal === 'ALL' || g.terminal === selectedTerminal
  );

  // Defined gate marker spatial coordinates on the aerial airport apron map
  const defaultGateCoordinates = {
    'G11': { x: 38, y: 78, defaultStatus: 'On Time' },
    'G12': { x: 26, y: 35, defaultStatus: 'On Time' },
    'G14': { x: 62, y: 38, defaultStatus: 'Delayed' },
    'G15': { x: 74, y: 64, defaultStatus: 'Boarding' },
    'G16': { x: 18, y: 68, defaultStatus: 'On Time' },
    'G17': { x: 82, y: 42, defaultStatus: 'Maintenance' },
    'G18': { x: 48, y: 22, defaultStatus: 'On Time' },
    'G21': { x: 32, y: 55, defaultStatus: 'Boarding' },
    'G22': { x: 65, y: 82, defaultStatus: 'On Time' },
    'G23': { x: 50, y: 88, defaultStatus: 'Delayed' },
  };

  // Combine real backend gate occupancy with spatial display
  const allDisplayGates = Object.keys(defaultGateCoordinates).map((gateNum) => {
    const backendData = gateMap[gateNum];
    const coords = defaultGateCoordinates[gateNum];
    const activeFlight = backendData?.flights?.[0];

    let status = coords.defaultStatus;
    if (activeFlight) {
      if (activeFlight.delay_category === 'Severe' || activeFlight.delay_minutes > 30) {
        status = 'Delayed';
      } else if (activeFlight.delay_minutes > 15) {
        status = 'Boarding';
      } else {
        status = 'On Time';
      }
    }

    return {
      gate_number: gateNum,
      terminal: backendData?.terminal || (parseInt(gateNum.replace('G', '')) < 20 ? 'T1' : 'T2'),
      x: coords.x,
      y: coords.y,
      status: status,
      activeFlight: activeFlight,
      allFlights: backendData?.flights || []
    };
  });

  const visibleGates = allDisplayGates.filter(
    (g) => selectedTerminal === 'ALL' || g.terminal === selectedTerminal
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'On Time': return '#19D88A';
      case 'Delayed': return '#FF4D4D';
      case 'Boarding': return '#FFC857';
      case 'Maintenance': return '#9B6CFF';
      default: return '#727E93';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'On Time': return 'rgba(25, 216, 138, 0.16)';
      case 'Delayed': return 'rgba(255, 77, 77, 0.2)';
      case 'Boarding': return 'rgba(255, 200, 87, 0.2)';
      case 'Maintenance': return 'rgba(155, 108, 255, 0.2)';
      default: return 'rgba(114, 126, 147, 0.2)';
    }
  };

  return (
    <div className="glass-card" style={{ padding: '20px', position: 'relative', overflow: 'hidden' }}>
      {/* Map Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Interactive Airport Map</h3>
          <span className="badge badge-live">
            <span className="live-pulse-dot" /> Live
          </span>
        </div>

        {/* View Switcher & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', background: 'rgba(17, 21, 26, 0.8)', padding: '3px', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-subtle)' }}>
            <button
              onClick={() => setViewMode('map')}
              style={{
                padding: '4px 12px',
                borderRadius: 'var(--radius-pill)',
                fontSize: '0.75rem',
                fontWeight: 700,
                border: 'none',
                cursor: 'pointer',
                background: viewMode === 'map' ? 'linear-gradient(135deg, #FFB52E, #FF9F1C)' : 'transparent',
                color: viewMode === 'map' ? '#07090C' : 'var(--text-secondary)'
              }}
            >
              Concourse Map
            </button>
            <button
              onClick={() => setViewMode('timeline')}
              style={{
                padding: '4px 12px',
                borderRadius: 'var(--radius-pill)',
                fontSize: '0.75rem',
                fontWeight: 700,
                border: 'none',
                cursor: 'pointer',
                background: viewMode === 'timeline' ? 'linear-gradient(135deg, #FFB52E, #FF9F1C)' : 'transparent',
                color: viewMode === 'timeline' ? '#07090C' : 'var(--text-secondary)'
              }}
            >
              Gantt Timeline
            </button>
          </div>

          {/* Terminal filter buttons */}
          <div style={{ display: 'flex', gap: '4px' }}>
            {['ALL', 'T1', 'T2', 'T3'].map((term) => (
              <button
                key={term}
                className={`btn ${selectedTerminal === term ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '4px 10px', fontSize: '0.75rem', borderRadius: 'var(--radius-pill)' }}
                onClick={() => setSelectedTerminal(term)}
              >
                {term === 'ALL' ? 'All Terminals' : term}
              </button>
            ))}
          </div>

          {viewMode === 'map' && (
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                onClick={() => setZoomLevel((z) => Math.min(1.4, z + 0.1))}
                style={{ background: 'rgba(17, 21, 26, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '6px', color: 'var(--text-secondary)', cursor: 'pointer' }}
                title="Zoom In"
              >
                <ZoomIn size={14} />
              </button>
              <button
                onClick={() => setZoomLevel((z) => Math.max(0.9, z - 0.1))}
                style={{ background: 'rgba(17, 21, 26, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '6px', color: 'var(--text-secondary)', cursor: 'pointer' }}
                title="Zoom Out"
              >
                <ZoomOut size={14} />
              </button>
              <button
                onClick={() => setZoomLevel(1)}
                style={{ background: 'rgba(17, 21, 26, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '6px', color: 'var(--text-secondary)', cursor: 'pointer' }}
                title="Reset Zoom"
              >
                <RotateCcw size={14} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'map' ? (
        <div style={{ position: 'relative' }}>
          {/* Map canvas container */}
          <div
            style={{
              position: 'relative',
              width: '100%',
              height: '380px',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              border: '1px solid var(--border-subtle)',
              background: '#07090C'
            }}
          >
            {/* Aerial photo overlay */}
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundImage: 'url(/images/airport-map-aerial.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                filter: 'brightness(0.7) contrast(1.15) saturate(1.1)',
                transform: `scale(${zoomLevel})`,
                transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                position: 'relative'
              }}
            >
              {/* Dark subtle vignette and grid lines */}
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'radial-gradient(ellipse at center, rgba(7, 9, 12, 0.2) 0%, rgba(7, 9, 12, 0.75) 100%)',
                  pointerEvents: 'none'
                }}
              />

              {/* Interactive Gate Markers on Map */}
              {visibleGates.map((gate) => {
                const color = getStatusColor(gate.status);
                const bg = getStatusBg(gate.status);
                const isSelected = selectedGate?.gate_number === gate.gate_number;

                return (
                  <div
                    key={gate.gate_number}
                    onClick={() => setSelectedGate(gate)}
                    style={{
                      position: 'absolute',
                      left: `${gate.x}%`,
                      top: `${gate.y}%`,
                      transform: 'translate(-50%, -50%)',
                      zIndex: isSelected ? 20 : 10,
                      cursor: 'pointer',
                      transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-pill)',
                        background: isSelected ? 'rgba(7, 9, 12, 0.95)' : 'rgba(11, 14, 18, 0.9)',
                        border: `2px solid ${isSelected ? '#FFB52E' : color}`,
                        boxShadow: isSelected 
                          ? '0 0 20px rgba(255, 181, 46, 0.8), 0 4px 12px rgba(0,0,0,0.8)' 
                          : `0 0 12px ${color}66, 0 4px 10px rgba(0,0,0,0.6)`,
                        backdropFilter: 'blur(8px)',
                        userSelect: 'none'
                      }}
                    >
                      <Plane size={12} color={color} style={{ transform: 'rotate(-45deg)' }} />
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1 }}>
                          {gate.gate_number}
                        </span>
                        <span style={{ fontSize: '0.625rem', fontWeight: 700, color: color, marginTop: '2px' }}>
                          {gate.status}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Selected Gate Inspection Floating Card / Drawer */}
            {selectedGate && (
              <div
                className="animate-slide-up"
                style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                  width: '300px',
                  background: 'rgba(11, 14, 18, 0.96)',
                  border: '1px solid rgba(255, 181, 46, 0.4)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  boxShadow: '0 12px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 181, 46, 0.15)',
                  backdropFilter: 'blur(16px)',
                  zIndex: 30
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <DoorClosed size={18} color="#FFB52E" />
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800 }}>Gate {selectedGate.gate_number}</h4>
                      <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Terminal {selectedGate.terminal}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedGate(null)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  >
                    <X size={16} />
                  </button>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 10px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.04)', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Current Status:</span>
                  <span
                    className="badge"
                    style={{
                      background: getStatusBg(selectedGate.status),
                      color: getStatusColor(selectedGate.status),
                      border: `1px solid ${getStatusColor(selectedGate.status)}`
                    }}
                  >
                    {selectedGate.status}
                  </span>
                </div>

                {selectedGate.activeFlight ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Assigned Flight:</span>
                      <span className="mono" style={{ fontWeight: 800, color: '#FFB52E' }}>
                        {selectedGate.activeFlight.flight_number}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Carrier:</span>
                      <span>{selectedGate.activeFlight.airline}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Delay Estimate:</span>
                      <span className="mono" style={{ color: '#FF4D4D', fontWeight: 700 }}>
                        +{selectedGate.activeFlight.delay_minutes.toFixed(0)} min
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Slot Window:</span>
                      <span className="mono" style={{ fontSize: '0.6875rem' }}>
                        {formatDateTime(selectedGate.activeFlight.start_time)}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '8px 0', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Gate ready for dispatch or inbound aircraft taxi. No active queue conflict.
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Map Legend (matching reference mockup) */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '20px',
              marginTop: '14px',
              padding: '8px 16px',
              background: 'rgba(11, 14, 18, 0.7)',
              borderRadius: 'var(--radius-pill)',
              border: '1px solid var(--border-subtle)',
              flexWrap: 'wrap',
              fontSize: '0.75rem'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#19D88A', boxShadow: '0 0 8px #19D88A' }} />
              <span style={{ color: 'var(--text-secondary)' }}>On Time</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#FF4D4D', boxShadow: '0 0 8px #FF4D4D' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Delayed</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#FFC857', boxShadow: '0 0 8px #FFC857' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Boarding</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#9B6CFF', boxShadow: '0 0 8px #9B6CFF' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Maintenance</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#727E93' }} />
              <span style={{ color: 'var(--text-muted)' }}>Unavailable</span>
            </div>
          </div>
        </div>
      ) : (
        /* Timeline View (Gantt Schedule) */
        <div>
          {filteredGates.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No gate assignments recorded yet. Run optimization to schedule gates.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {filteredGates.map((gate) => (
                <div
                  key={gate.gate_number}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '100px 1fr',
                    alignItems: 'center',
                    gap: '16px',
                    background: 'rgba(11, 14, 18, 0.75)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '10px 16px'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span className="mono" style={{ fontSize: '1rem', fontWeight: 800, color: '#FFB52E' }}>
                      {gate.gate_number}
                    </span>
                    <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      Terminal {gate.terminal}
                    </span>
                  </div>

                  {/* Flight occupancy blocks */}
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                    {gate.flights.map((f) => (
                      <div
                        key={f.flight_id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 12px',
                          borderRadius: 'var(--radius-sm)',
                          background: 'rgba(17, 21, 26, 0.95)',
                          borderLeft: `4px solid ${getDelayColor(f.delay_category)}`,
                          borderTop: '1px solid var(--border-subtle)',
                          borderRight: '1px solid var(--border-subtle)',
                          borderBottom: '1px solid var(--border-subtle)',
                          fontSize: '0.75rem',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.4)'
                        }}
                      >
                        <Plane size={14} color="#FFB52E" />
                        <div>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <span className="mono" style={{ fontWeight: 800, color: '#F5F7FA' }}>
                              {f.flight_number}
                            </span>
                            <span style={{ color: 'var(--text-muted)' }}>•</span>
                            <span style={{ color: 'var(--text-secondary)' }}>{f.airline}</span>
                          </div>
                          <div style={{ display: 'flex', gap: '6px', fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                            <span className="mono">{formatDateTime(f.start_time)} - {formatDateTime(f.end_time)}</span>
                            <span style={{ color: getDelayColor(f.delay_category) }}>
                              (+{f.delay_minutes.toFixed(0)}m)
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
