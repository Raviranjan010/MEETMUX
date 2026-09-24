import React, { useState, useEffect } from 'react';
import {
  CalendarDays,
  DoorClosed,
  Clock,
  RotateCw,
  AlertTriangle,
  Plane,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { getGates, getFlights, detectConflicts } from '../api';
import { Gate, Flight, Conflict } from '../api/types';

export const Timeline: React.FC = () => {
  const [gates, setGates] = useState<Gate[]>([]);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);

  // Time window: 06:00 to 22:00 (16 hours = 960 minutes)
  const startHour = 6;
  const endHour = 22;
  const totalMinutes = (endHour - startHour) * 60;

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
      console.error('Failed to load timeline data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const conflictGateIds = new Set(conflicts.map((c) => c.gate_id));

  // Compute block position (left % and width %)
  const getFlightBlockStyle = (flight: Flight) => {
    if (!flight.scheduled_arrival || !flight.scheduled_departure) {
      return null;
    }
    const arrDate = new Date(flight.scheduled_arrival);
    const depDate = new Date(flight.scheduled_departure);

    const arrMins = arrDate.getHours() * 60 + arrDate.getMinutes() - startHour * 60;
    const depMins = depDate.getHours() * 60 + depDate.getMinutes() - startHour * 60;

    const left = Math.max(0, (arrMins / totalMinutes) * 100);
    const width = Math.max(2, ((depMins - arrMins) / totalMinutes) * 100);

    return { left: `${left}%`, width: `${width}%` };
  };

  const hoursArray = Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            GATE OCCUPANCY GANTT TIMELINE
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            Real-time visual schedule across all 30 gates • Turnaround intervals & overlap conflict detection
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>Refresh Timeline</span>
        </button>
      </div>

      {/* Gantt Timeline Board */}
      <div className="bg-surface rounded border border-muted/20 p-4 font-mono text-xs overflow-x-auto">
        <div className="min-w-[900px]">
          {/* Time Header Scale */}
          <div className="flex border-b border-muted/20 pb-2 mb-2 text-[10px] text-muted">
            <div className="w-24 shrink-0 font-bold text-white uppercase">Gate Stand</div>
            <div className="flex-1 flex justify-between">
              {hoursArray.map((hour) => (
                <span key={hour} className="text-center">
                  {hour.toString().padStart(2, '0')}:00
                </span>
              ))}
            </div>
          </div>

          {/* Gate Rows */}
          <div className="space-y-1.5 max-h-[550px] overflow-y-auto pr-2">
            {gates.map((g) => {
              const gateFlights = flights.filter((f) => f.assigned_gate_id === g.id);
              const hasConflict = conflictGateIds.has(g.id);

              return (
                <div
                  key={g.id}
                  className={`flex items-center h-8 rounded border transition-colors ${
                    hasConflict
                      ? 'bg-red/10 border-red/30'
                      : 'bg-surface-elevated/40 border-muted/10 hover:bg-surface-elevated'
                  }`}
                >
                  {/* Gate Label */}
                  <div className="w-24 shrink-0 px-2 flex items-center justify-between border-r border-muted/20">
                    <span className="font-bold text-white">{g.gate_number}</span>
                    <span className="text-[9px] text-muted">{g.terminal}</span>
                  </div>

                  {/* Schedule Timeline Track */}
                  <div className="flex-1 h-full relative">
                    {/* Background grid lines */}
                    <div className="absolute inset-0 flex justify-between pointer-events-none">
                      {hoursArray.map((hour) => (
                        <div key={hour} className="w-px h-full bg-muted/10"></div>
                      ))}
                    </div>

                    {/* Flight Reservation Blocks */}
                    {gateFlights.map((f) => {
                      const style = getFlightBlockStyle(f);
                      if (!style) return null;
                      const isHigh = f.prediction?.risk_level === 'HIGH';

                      return (
                        <div
                          key={f.id}
                          onClick={() => setSelectedFlight(f)}
                          style={style}
                          className={`absolute top-1 bottom-1 rounded px-1.5 flex items-center justify-between text-[10px] font-bold text-white cursor-pointer shadow-sm transition-transform hover:scale-y-110 select-none ${
                            isHigh
                              ? 'bg-red/80 border border-red'
                              : 'bg-green/80 border border-green'
                          }`}
                          title={`${f.flight_number} (${f.airline}) - ${f.scheduled_arrival?.substring(11, 16)} to ${f.scheduled_departure?.substring(11, 16)}`}
                        >
                          <span className="truncate">{f.flight_number}</span>
                          <span className="text-[8px] opacity-80">{f.airline.substring(0, 2)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 pt-3 border-t border-muted/20 flex flex-wrap items-center gap-4 text-muted text-[11px]">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-green/80 border border-green"></span>
            <span className="text-white">Scheduled Flight (Normal Risk)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red/80 border border-red"></span>
            <span className="text-white">High Delay Risk (&gt;30m)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red/20 border border-red/50"></span>
            <span className="text-red font-bold">Gate Stand Conflict Row</span>
          </div>
        </div>
      </div>

      {/* Flight Detail Modal */}
      {selectedFlight && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-surface border border-muted/30 rounded-lg max-w-md w-full p-6 font-mono text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-muted/20 pb-3">
              <div className="flex items-center gap-2">
                <Plane className="w-4 h-4 text-green" />
                <h2 className="text-base font-bold text-white">{selectedFlight.flight_number}</h2>
              </div>
              <button
                onClick={() => setSelectedFlight(null)}
                className="px-2 py-1 bg-surface-elevated hover:bg-muted-dark rounded text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2">
              <div className="p-2.5 bg-surface-elevated rounded flex justify-between">
                <span className="text-muted">Airline:</span>
                <span className="font-bold text-white">{selectedFlight.airline}</span>
              </div>
              <div className="p-2.5 bg-surface-elevated rounded flex justify-between">
                <span className="text-muted">Route:</span>
                <span className="font-bold text-white">
                  {selectedFlight.origin} → {selectedFlight.destination}
                </span>
              </div>
              <div className="p-2.5 bg-surface-elevated rounded flex justify-between">
                <span className="text-muted">Arrival Window:</span>
                <span className="font-bold text-white">
                  {selectedFlight.scheduled_arrival?.substring(11, 16)} - {selectedFlight.scheduled_departure?.substring(11, 16)}
                </span>
              </div>
              <div className="p-2.5 bg-surface-elevated rounded flex justify-between">
                <span className="text-muted">Delay Risk:</span>
                <span className="font-bold text-amber">
                  {selectedFlight.prediction?.risk_level || 'LOW'} ({selectedFlight.prediction?.predicted_delay_minutes.toFixed(0) || 0}m)
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedFlight(null)}
                className="px-4 py-2 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
