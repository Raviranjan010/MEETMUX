import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Plane,
  DoorClosed,
  AlertTriangle,
  RotateCw,
  Info,
  CheckCircle2,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { getGates, getFlights, detectConflicts } from '../api';
import { Gate, Flight, Conflict } from '../api/types';

export const AirportMap: React.FC = () => {
  const [gates, setGates] = useState<Gate[]>([]);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedGate, setSelectedGate] = useState<Gate | null>(null);
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [activeLayer, setActiveLayer] = useState<'ALL' | 'CONFLICTS' | 'RISK'>('ALL');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [gRes, fRes, cRes] = await Promise.all([
        getGates(),
        getFlights({ page: 1, page_size: 100 }),
        detectConflicts().catch(() => ({ conflicts: [], count: 0 })),
      ]);
      setGates(gRes);
      setFlights(fRes.items);
      setConflicts(cRes.conflicts || []);
    } catch (err) {
      console.error('Failed to load map data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const conflictGateIds = new Set(conflicts.map((c) => c.gate_id));

  // Map 30 gates to SVG coordinate positions across Terminal 1 & 2 piers
  const getGateCoords = (index: number) => {
    // T1 Pier (Gates G01 - G15) on the left/top
    if (index < 15) {
      const row = Math.floor(index / 5);
      const col = index % 5;
      return { x: 180 + col * 75, y: 190 + row * 60 };
    }
    // T2 Pier (Gates G16 - G30) on the right/bottom
    const idx2 = index - 15;
    const row = Math.floor(idx2 / 5);
    const col = idx2 % 5;
    return { x: 620 + col * 75, y: 310 + row * 60 };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            AIRPORT AIRSIDE VECTOR MAP
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            VIDP / DEL Dual-Runway Layout • Terminal 1 (Gates 01-15) & Terminal 2 (Gates 16-30)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-surface-elevated p-1 rounded border border-muted/30 font-mono text-xs">
            <button
              onClick={() => setActiveLayer('ALL')}
              className={`px-2 py-1 rounded transition-colors ${
                activeLayer === 'ALL' ? 'bg-green/20 text-green font-bold' : 'text-muted'
              }`}
            >
              All Stands
            </button>
            <button
              onClick={() => setActiveLayer('CONFLICTS')}
              className={`px-2 py-1 rounded transition-colors ${
                activeLayer === 'CONFLICTS' ? 'bg-red/20 text-red font-bold' : 'text-muted'
              }`}
            >
              Conflicts ({conflicts.length})
            </button>
          </div>

          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Main Map Canvas & Details Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Airport Surface Map (3 columns) */}
        <div className="lg:col-span-3 bg-surface rounded border border-muted/20 p-4 flex flex-col justify-between overflow-hidden">
          <div className="w-full aspect-[16/9] min-h-[460px] relative bg-[#060c0a] rounded border border-muted/20">
            <svg
              viewBox="0 0 1100 620"
              className="w-full h-full select-none"
              style={{ filter: 'drop-shadow(0 0 20px rgba(0,0,0,0.5))' }}
            >
              {/* Background Airport Grid Pattern */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#0e1f1a" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="1100" height="620" fill="url(#grid)" />

              {/* Runway 09L / 27R (Northern Runway - Primary Arrivals) */}
              <g id="runway-north">
                <rect x="80" y="55" width="940" height="36" fill="#182823" rx="2" stroke="#2b3b35" strokeWidth="2" />
                {/* Centerline dashes */}
                <line x1="120" y1="73" x2="980" y2="73" stroke="#F4F1E8" strokeWidth="2.5" strokeDasharray="25,20" />
                {/* Threshold markings */}
                <text x="100" y="78" fill="#F4F1E8" fontFamily="monospace" fontSize="14" fontWeight="bold">
                  09L
                </text>
                <text x="980" y="78" fill="#F4F1E8" fontFamily="monospace" fontSize="14" fontWeight="bold">
                  27R
                </text>
                <text x="500" y="45" fill="#87938D" fontFamily="monospace" fontSize="10">
                  RUNWAY 09L/27R (3810m x 45m) • CAT III ILS ACTIVE
                </text>
              </g>

              {/* Runway 09R / 27L (Southern Runway - Primary Departures) */}
              <g id="runway-south">
                <rect x="80" y="530" width="940" height="36" fill="#182823" rx="2" stroke="#2b3b35" strokeWidth="2" />
                <line x1="120" y1="548" x2="980" y2="548" stroke="#F4F1E8" strokeWidth="2.5" strokeDasharray="25,20" />
                <text x="100" y="553" fill="#F4F1E8" fontFamily="monospace" fontSize="14" fontWeight="bold">
                  09R
                </text>
                <text x="980" y="553" fill="#F4F1E8" fontFamily="monospace" fontSize="14" fontWeight="bold">
                  27L
                </text>
                <text x="500" y="590" fill="#87938D" fontFamily="monospace" fontSize="10">
                  RUNWAY 09R/27L (4430m x 60m) • DEPARTURES ACTIVE
                </text>
              </g>

              {/* Taxiway Network Paths */}
              <path
                d="M 120 73 L 120 548 M 980 73 L 980 548 M 350 91 L 350 530 M 750 91 L 750 530 M 80 130 L 1020 130 M 80 470 L 1020 470"
                fill="none"
                stroke="#1e332c"
                strokeWidth="14"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M 120 73 L 120 548 M 980 73 L 980 548 M 350 91 L 350 530 M 750 91 L 750 530 M 80 130 L 1020 130 M 80 470 L 1020 470"
                fill="none"
                stroke="#F5A623"
                strokeWidth="1"
                strokeDasharray="6,6"
              />

              {/* Taxiway Labels */}
              <text x="135" y="270" fill="#F5A623" fontFamily="monospace" fontSize="11" fontWeight="bold">
                TWY A
              </text>
              <text x="365" y="270" fill="#F5A623" fontFamily="monospace" fontSize="11" fontWeight="bold">
                TWY B
              </text>
              <text x="765" y="270" fill="#F5A623" fontFamily="monospace" fontSize="11" fontWeight="bold">
                TWY C
              </text>
              <text x="955" y="270" fill="#F5A623" fontFamily="monospace" fontSize="11" fontWeight="bold">
                TWY D
              </text>

              {/* Terminal 1 Building Complex */}
              <g id="terminal-1">
                <rect x="150" y="160" width="410" height="200" fill="#0e1916" stroke="#2B3B35" strokeWidth="2" rx="6" />
                <text x="170" y="180" fill="#F4F1E8" fontFamily="monospace" fontSize="12" fontWeight="bold">
                  TERMINAL 1 (DOMESTIC OPERATIONS)
                </text>
              </g>

              {/* Terminal 2 Building Complex */}
              <g id="terminal-2">
                <rect x="590" y="280" width="410" height="200" fill="#0e1916" stroke="#2B3B35" strokeWidth="2" rx="6" />
                <text x="610" y="300" fill="#F4F1E8" fontFamily="monospace" fontSize="12" fontWeight="bold">
                  TERMINAL 2 (INTERNATIONAL / SWING)
                </text>
              </g>

              {/* 30 Gate Stands */}
              {gates.map((g, idx) => {
                const { x, y } = getGateCoords(idx);
                const isConflict = conflictGateIds.has(g.id) || g.status === 'CONFLICT';
                const isSelected = selectedGate?.id === g.id;

                let fill = '#152420';
                let stroke = '#39C878';
                let textColor = '#39C878';

                if (g.status === 'OCCUPIED') {
                  stroke = '#F5A623';
                  textColor = '#F5A623';
                } else if (g.status === 'BLOCKED') {
                  stroke = '#87938D';
                  textColor = '#87938D';
                }
                if (isConflict) {
                  stroke = '#EF5350';
                  textColor = '#EF5350';
                  fill = '#2a1111';
                }

                if (activeLayer === 'CONFLICTS' && !isConflict) {
                  stroke = '#2b3b35';
                  textColor = '#556660';
                }

                return (
                  <g
                    key={g.id}
                    transform={`translate(${x}, ${y})`}
                    onClick={() => {
                      setSelectedGate(g);
                      const f = flights.find((fl) => fl.assigned_gate_id === g.id);
                      setSelectedFlight(f || null);
                    }}
                    className="cursor-pointer transition-transform hover:scale-110"
                  >
                    {/* Stand outline box */}
                    <rect
                      x="-25"
                      y="-18"
                      width="50"
                      height="36"
                      rx="3"
                      fill={fill}
                      stroke={isSelected ? '#F4F1E8' : stroke}
                      strokeWidth={isSelected ? 2.5 : 1.5}
                    />
                    {/* Gate Label */}
                    <text
                      x="0"
                      y="4"
                      textAnchor="middle"
                      fill={textColor}
                      fontFamily="monospace"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      {g.gate_number}
                    </text>
                    {/* Aircraft silhouette if occupied */}
                    {g.status === 'OCCUPIED' && (
                      <circle cx="16" cy="-10" r="3" fill="#F5A623" />
                    )}
                    {isConflict && (
                      <circle cx="16" cy="-10" r="4" fill="#EF5350" className="animate-ping" />
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Map Legend */}
          <div className="mt-4 pt-3 border-t border-muted/20 flex flex-wrap items-center justify-between gap-4 font-mono text-xs text-muted">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#152420] border border-green"></span>
                <span className="text-white">Available Stand</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-[#152420] border border-amber"></span>
                <span className="text-white">Occupied</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-red/30 border border-red animate-pulse"></span>
                <span className="text-red font-bold">Conflict Overlap</span>
              </div>
            </div>
            <div className="text-[11px] text-muted">
              Click any gate stand or aircraft marker for telemetry inspection
            </div>
          </div>
        </div>

        {/* Selected Gate / Aircraft Telemetry Inspector */}
        <div className="bg-surface rounded border border-muted/20 p-4 flex flex-col justify-between font-mono text-xs">
          <div>
            <div className="flex items-center gap-2 border-b border-muted/20 pb-3 mb-4">
              <Info className="w-4 h-4 text-green" />
              <h2 className="font-bold text-white uppercase">Stand Inspector</h2>
            </div>

            {selectedGate ? (
              <div className="space-y-3">
                <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                  <div className="text-[10px] text-muted">STAND IDENTIFIER</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    GATE {selectedGate.gate_number} ({selectedGate.terminal})
                  </div>
                  <div className="text-[11px] text-green mt-1">
                    Status: <span className="font-bold">{selectedGate.status}</span>
                  </div>
                </div>

                <div className="space-y-2 text-[11px]">
                  <div className="flex justify-between py-1 border-b border-muted/10">
                    <span className="text-muted">Eligibility:</span>
                    <span className="text-white font-semibold">{selectedGate.gate_type}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-muted/10">
                    <span className="text-muted">Aircraft Capacity:</span>
                    <span className="text-white font-semibold">{selectedGate.max_aircraft_size}</span>
                  </div>
                </div>

                {conflictGateIds.has(selectedGate.id) && (
                  <div className="p-3 bg-red/15 border border-red/40 rounded text-red text-[11px] space-y-1">
                    <div className="font-bold flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>CRITICAL GATE OVERLAP</span>
                    </div>
                    <div>Multiple aircraft scheduled inside turnaround buffer window.</div>
                  </div>
                )}

                {selectedFlight ? (
                  <div className="p-3 bg-surface-elevated rounded border border-muted/20 space-y-1.5">
                    <div className="text-[10px] text-muted">OCCUPYING FLIGHT</div>
                    <div className="font-bold text-white text-sm">
                      {selectedFlight.flight_number} — {selectedFlight.airline}
                    </div>
                    <div className="text-[11px] text-muted">
                      Route: {selectedFlight.origin} → {selectedFlight.destination}
                    </div>
                    <div className="text-[11px] text-amber">
                      Est. Delay: {selectedFlight.prediction?.predicted_delay_minutes.toFixed(0) || 0} min
                    </div>
                  </div>
                ) : (
                  <div className="p-3 bg-surface-elevated/40 rounded text-muted text-center text-[11px]">
                    No active aircraft occupying this stand currently.
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-muted">
                <MapPin className="w-8 h-8 text-muted mx-auto mb-2 opacity-50" />
                Select a gate stand on the airside map to inspect its real-time status.
              </div>
            )}
          </div>

          {selectedGate && (
            <div className="pt-3 border-t border-muted/20">
              <button
                onClick={() => {
                  setSelectedGate(null);
                  setSelectedFlight(null);
                }}
                className="w-full py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-muted hover:text-white transition-colors"
              >
                Clear Selection
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
