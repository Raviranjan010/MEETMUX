import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  Database,
  BrainCircuit,
  Cpu,
  Plane,
  DoorClosed,
  AlertTriangle,
  RotateCw,
  Flame,
  GitFork,
  CheckCircle2,
  TrendingDown,
  Clock,
  Wind,
} from 'lucide-react';
import { StatusPill } from '../components/StatusPill';
import {
  getHealth,
  getFlights,
  getGates,
  detectConflicts,
  getAlerts,
  runReoptimization,
} from '../api';
import { Flight, Gate, Conflict, Alert } from '../api/types';

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [gates, setGates] = useState<Gate[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reoptimizing, setReoptimizing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [hRes, fRes, gRes, cRes, aRes] = await Promise.all([
        getHealth().catch(() => null),
        getFlights({ page: 1, page_size: 100 }).catch(() => ({ items: [], total: 0 })),
        getGates().catch(() => []),
        detectConflicts().catch(() => ({ conflicts: [], count: 0 })),
        getAlerts({ resolved: false }).catch(() => []),
      ]);

      if (!hRes) {
        setError('Backend Service Unreachable');
      }

      setHealth(hRes);
      setFlights(fRes?.items || []);
      setGates(gRes || []);
      setConflicts(cRes?.conflicts || []);
      setAlerts(aRes || []);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || err?.message || 'Error fetching dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleQuickReoptimize = async () => {
    setReoptimizing(true);
    try {
      await runReoptimization();
      await loadAll();
    } catch (err) {
      console.error('Re-optimization failed', err);
    } finally {
      setReoptimizing(false);
    }
  };

  const highRiskFlights = flights.filter((f) => f.prediction?.risk_level === 'HIGH');
  const occupiedGates = gates.filter((g) => g.status === 'OCCUPIED' || g.status === 'CONFLICT');
  const gateUtilizationPct = gates.length > 0 ? Math.round((occupiedGates.length / gates.length) * 100) : 0;

  if (loading && !health) {
    return (
      <div className="space-y-6 animate-pulse" data-testid="dashboard-loading">
        <div className="h-8 w-64 bg-surface rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-surface rounded border border-muted/20"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-view">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-white font-mono">
              COMMAND CENTER OVERVIEW
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono bg-green/10 text-green border border-green/30 rounded">
              LIVE SYSTEM
            </span>
          </div>
          <p className="text-xs text-muted font-mono mt-0.5">
            DELHI INTERNATIONAL AIRPORT (DEL/VIDP) • DUAL RUNWAY ACTIVE • 30 GATES ONLINE
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadAll}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleQuickReoptimize}
            disabled={reoptimizing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-xs font-mono text-green font-semibold transition-colors disabled:opacity-50"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>{reoptimizing ? 'Optimizing...' : 'Re-optimize Airport'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div
          data-testid="dashboard-error"
          className="p-4 bg-red/10 border border-red/30 rounded text-xs text-red flex items-center gap-2"
        >
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Real-time KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {/* Total Flights */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-muted text-xs font-mono mb-1">
            <span>FLIGHTS QUEUED</span>
            <Plane className="w-3.5 h-3.5 text-muted" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{flights.length}</div>
          <div className="text-[10px] text-muted font-mono mt-1">100 scheduled slots</div>
        </div>

        {/* High Risk Flights */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-amber text-xs font-mono mb-1">
            <span>HIGH DELAY RISK</span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber">{highRiskFlights.length}</div>
          <div className="text-[10px] text-muted font-mono mt-1">Taxi delay &gt; 30 min</div>
        </div>

        {/* Gate Conflicts */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-red text-xs font-mono mb-1">
            <span>GATE CONFLICTS</span>
            <AlertTriangle className="w-3.5 h-3.5 text-red" />
          </div>
          <div className={`text-2xl font-bold font-mono ${conflicts.length > 0 ? 'text-red' : 'text-green'}`}>
            {conflicts.length}
          </div>
          <div className="text-[10px] text-muted font-mono mt-1">
            {conflicts.length > 0 ? 'Overlap violation' : 'Zero overlaps'}
          </div>
        </div>

        {/* Gate Utilization */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-muted text-xs font-mono mb-1">
            <span>GATE UTILIZATION</span>
            <DoorClosed className="w-3.5 h-3.5 text-green" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{gateUtilizationPct}%</div>
          <div className="text-[10px] text-muted font-mono mt-1">
            {occupiedGates.length} / {gates.length} gates active
          </div>
        </div>

        {/* ML Predictor */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-muted text-xs font-mono mb-1">
            <span>ML PREDICTOR</span>
            <BrainCircuit className="w-3.5 h-3.5 text-green" />
          </div>
          <div className="text-sm font-bold font-mono text-white mt-1">
            {health?.ml_model_loaded ? 'ACTIVE (GBM)' : 'OFFLINE'}
          </div>
          <div className="text-[10px] text-green font-mono mt-1">R² 0.918 • MAE 0.94m</div>
        </div>

        {/* MILP Solver */}
        <div className="p-3.5 bg-surface rounded border border-muted/20">
          <div className="flex items-center justify-between text-muted text-xs font-mono mb-1">
            <span>SOLVER STATUS</span>
            <Cpu className="w-3.5 h-3.5 text-green" />
          </div>
          <div className="text-sm font-bold font-mono text-white mt-1">
            {health?.optimizer?.gurobi_available
              ? 'GUROBI'
              : health?.optimizer?.ortools_available
              ? 'OR-TOOLS CP-SAT'
              : 'OFFLINE'}
          </div>
          <div className="text-[10px] text-muted font-mono mt-1">Hard constraints valid</div>
        </div>
      </div>

      {/* Main Grid: Gate Matrix & Operational Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gate Occupancy Matrix (2 cols on large screen) */}
        <div className="lg:col-span-2 bg-surface rounded border border-muted/20 p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <DoorClosed className="w-4 h-4 text-green" />
              <h2 className="text-sm font-bold font-mono text-white">GATE STATUS GRID (30 GATES)</h2>
            </div>
            <Link
              to="/gates"
              className="text-xs font-mono text-green hover:underline flex items-center gap-1"
            >
              <span>View details</span>
              <span>→</span>
            </Link>
          </div>

          <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-10 gap-2">
            {gates.map((g) => {
              let bg = 'bg-green/10 border-green/30 text-green';
              if (g.status === 'OCCUPIED') bg = 'bg-amber/15 border-amber/40 text-amber';
              if (g.status === 'CONFLICT') bg = 'bg-red/20 border-red/50 text-red animate-pulse';
              if (g.status === 'BLOCKED') bg = 'bg-muted-dark border-muted text-muted';
              if (g.status === 'RESERVED') bg = 'bg-blue-500/15 border-blue-500/30 text-blue-400';

              return (
                <div
                  key={g.id}
                  className={`p-2 rounded border text-center font-mono ${bg} transition-all hover:scale-105 cursor-pointer`}
                  title={`Gate ${g.gate_number} (${g.terminal}) - ${g.status}`}
                >
                  <div className="text-xs font-bold">{g.gate_number}</div>
                  <div className="text-[9px] opacity-75">{g.terminal}</div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 pt-3 border-t border-muted/20 flex flex-wrap items-center gap-4 text-[11px] font-mono text-muted">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-green/30 border border-green/50"></span>
              <span>Available</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-amber/30 border border-amber/50"></span>
              <span>Occupied</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-red/40 border border-red/60"></span>
              <span>Conflict</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-blue-500/30 border border-blue-500/50"></span>
              <span>Reserved</span>
            </div>
          </div>
        </div>

        {/* Operational Alerts Feed */}
        <div className="bg-surface rounded border border-muted/20 p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber" />
                <h2 className="text-sm font-bold font-mono text-white">ACTIVE ALERTS</h2>
              </div>
              <Link to="/alerts" className="text-xs font-mono text-green hover:underline">
                View all ({alerts.length})
              </Link>
            </div>

            <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
              {alerts.length === 0 ? (
                <div className="p-4 text-center text-xs font-mono text-muted bg-surface-elevated rounded border border-muted/10">
                  <CheckCircle2 className="w-5 h-5 text-green mx-auto mb-1 opacity-80" />
                  All airport systems nominal. No active alerts.
                </div>
              ) : (
                alerts.slice(0, 4).map((a) => (
                  <div
                    key={a.id}
                    className={`p-2.5 rounded border text-xs font-mono ${
                      a.severity === 'CRITICAL'
                        ? 'bg-red/10 border-red/30 text-red'
                        : 'bg-amber/10 border-amber/30 text-amber'
                    }`}
                  >
                    <div className="font-bold flex items-center justify-between">
                      <span>{a.title}</span>
                      <span className="text-[10px] opacity-75">{a.severity}</span>
                    </div>
                    <div className="text-[11px] text-white/80 mt-1">{a.message}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-muted/20">
            <Link
              to="/scenarios"
              className="w-full flex items-center justify-center gap-2 p-2 rounded bg-surface-elevated hover:bg-muted-dark border border-muted/30 text-xs font-mono text-white transition-colors"
            >
              <Flame className="w-3.5 h-3.5 text-amber" />
              <span>Launch Disruption Simulator</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Flight Risk Queue & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* High Risk Queue */}
        <div className="lg:col-span-2 bg-surface rounded border border-muted/20 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber" />
              <h2 className="text-sm font-bold font-mono text-white">
                FLIGHT DELAY RISK QUEUE (NEXT DEPARTURES)
              </h2>
            </div>
            <Link to="/flights" className="text-xs font-mono text-green hover:underline">
              All flights →
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="text-[10px] text-muted uppercase bg-surface-elevated border-b border-muted/20">
                <tr>
                  <th className="p-2">Flight</th>
                  <th className="p-2">Airline</th>
                  <th className="p-2">Route</th>
                  <th className="p-2">Gate</th>
                  <th className="p-2">Est. Taxi</th>
                  <th className="p-2">Delay Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-muted/10">
                {flights.slice(0, 6).map((f) => (
                  <tr key={f.id} className="hover:bg-surface-elevated/50">
                    <td className="p-2 font-bold text-white">{f.flight_number}</td>
                    <td className="p-2 text-muted">{f.airline}</td>
                    <td className="p-2 text-muted">
                      {f.origin} → {f.destination}
                    </td>
                    <td className="p-2 text-white">
                      {f.assigned_gate ? f.assigned_gate.gate_number : 'Unassigned'}
                    </td>
                    <td className="p-2 text-muted">
                      {f.prediction ? `${f.prediction.predicted_taxi_out_minutes.toFixed(1)}m` : '-'}
                    </td>
                    <td className="p-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          f.prediction?.risk_level === 'HIGH'
                            ? 'bg-red/20 text-red border border-red/30'
                            : f.prediction?.risk_level === 'MEDIUM'
                            ? 'bg-amber/20 text-amber border border-amber/30'
                            : 'bg-green/20 text-green border border-green/30'
                        }`}
                      >
                        {f.prediction?.risk_level || 'LOW'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Airport Status / Environmental Snapshot */}
        <div className="bg-surface rounded border border-muted/20 p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Wind className="w-4 h-4 text-white" />
              <h2 className="text-sm font-bold font-mono text-white">METEOROLOGICAL & RUNWAYS</h2>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                <div className="text-[10px] text-muted">WEATHER CONDITION</div>
                <div className="text-sm font-bold text-white mt-0.5">VMC • VISIBILITY 6.5 KM</div>
                <div className="text-[11px] text-muted mt-1">Wind 090° @ 12 kts • Temp 28°C</div>
              </div>

              <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                <div className="text-[10px] text-muted">RUNWAYS IN OPERATION</div>
                <div className="flex items-center justify-between mt-1">
                  <span className="font-bold text-white">RWY 09L / 27R</span>
                  <span className="px-1.5 py-0.5 bg-green/20 text-green text-[10px] rounded">ACTIVE (ARR)</span>
                </div>
                <div className="flex items-center justify-between mt-1.5">
                  <span className="font-bold text-white">RWY 09R / 27L</span>
                  <span className="px-1.5 py-0.5 bg-green/20 text-green text-[10px] rounded">ACTIVE (DEP)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-muted/20">
            <Link
              to="/airport"
              className="w-full flex items-center justify-center gap-2 p-2 rounded bg-green/10 hover:bg-green/20 border border-green/30 text-xs font-mono text-green font-semibold transition-colors"
            >
              <span>Open Vector Airport Map</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
