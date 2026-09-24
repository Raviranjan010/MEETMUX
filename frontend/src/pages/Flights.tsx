import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Plane,
  Search,
  Filter,
  AlertTriangle,
  RotateCw,
  Clock,
  MapPin,
  BrainCircuit,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  X,
} from 'lucide-react';
import { getFlights, getFlight, predictFlight, batchPredict } from '../api';
import { Flight } from '../api/types';

export const Flights: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [flights, setFlights] = useState<Flight[]>([]);

  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(25);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [routeFilter, setRouteFilter] = useState<string>('');
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [predictingId, setPredictingId] = useState<string | null>(null);
  const [batchPredicting, setBatchPredicting] = useState<boolean>(false);

  const fetchFlightData = async () => {
    setLoading(true);
    try {
      const res = await getFlights({
        page,
        page_size: pageSize,
        risk_level: riskFilter || undefined,
        route_type: routeFilter || undefined,
        search: searchTerm || undefined,
      });
      setFlights(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Failed to fetch flights', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlightData();
  }, [page, riskFilter, routeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchFlightData();
  };

  const handlePredictSingle = async (flightId: string) => {
    setPredictingId(flightId);
    try {
      const pred = await predictFlight(flightId);
      setFlights((prev) =>
        prev.map((f) => (f.id === flightId ? { ...f, prediction: pred } : f))
      );
      if (selectedFlight && selectedFlight.id === flightId) {
        setSelectedFlight((prev) => (prev ? { ...prev, prediction: pred } : null));
      }
    } catch (err) {
      console.error('Prediction failed', err);
    } finally {
      setPredictingId(null);
    }
  };

  const handleBatchPredict = async () => {
    setBatchPredicting(true);
    try {
      await batchPredict();
      await fetchFlightData();
    } catch (err) {
      console.error('Batch predict failed', err);
    } finally {
      setBatchPredicting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            FLIGHT SCHEDULES & TAXI DELAYS
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            100 commercial operations scheduled • ML Taxi Delay Risk Inference
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleBatchPredict}
            disabled={batchPredicting}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-xs font-mono text-green font-semibold transition-colors disabled:opacity-50"
          >
            <BrainCircuit className="w-3.5 h-3.5" />
            <span>{batchPredicting ? 'Evaluating ML...' : 'Run All ML Predictions'}</span>
          </button>
          <button
            onClick={fetchFlightData}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-3 bg-surface rounded border border-muted/20 flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-sm">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-muted" />
            <input
              type="text"
              placeholder="Search flight number, airline, aircraft..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-surface-elevated border border-muted/30 rounded text-xs text-white placeholder-muted focus:outline-none focus:border-green"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs text-white"
          >
            Filter
          </button>
        </form>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-muted text-[11px]">Risk:</span>
            <select
              value={riskFilter}
              onChange={(e) => {
                setRiskFilter(e.target.value);
                setPage(1);
              }}
              className="px-2 py-1 bg-surface-elevated border border-muted/30 rounded text-xs text-white focus:outline-none"
            >
              <option value="">All Risks</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-muted text-[11px]">Route:</span>
            <select
              value={routeFilter}
              onChange={(e) => {
                setRouteFilter(e.target.value);
                setPage(1);
              }}
              className="px-2 py-1 bg-surface-elevated border border-muted/30 rounded text-xs text-white focus:outline-none"
            >
              <option value="">All Routes</option>
              <option value="DOMESTIC">Domestic</option>
              <option value="INTERNATIONAL">International</option>
            </select>
          </div>
        </div>
      </div>

      {/* Flight Table */}
      <div className="bg-surface rounded border border-muted/20 overflow-hidden font-mono text-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-surface-elevated border-b border-muted/20 text-[10px] text-muted uppercase">
              <tr>
                <th className="p-3">Flight</th>
                <th className="p-3">Airline</th>
                <th className="p-3">Aircraft</th>
                <th className="p-3">Route</th>
                <th className="p-3">Schedule</th>
                <th className="p-3">Assigned Gate</th>
                <th className="p-3">Est. Taxi</th>
                <th className="p-3">Delay Risk</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-muted/10">
              {loading ? (
                <tr>
                  <td colSpan={9} className="p-8 text-center text-muted">
                    Loading flight telemetry...
                  </td>
                </tr>
              ) : flights.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-8 text-center text-muted">
                    No flights match the active filters.
                  </td>
                </tr>
              ) : (
                flights.map((f) => {
                  const isHigh = f.prediction?.risk_level === 'HIGH';
                  const isMed = f.prediction?.risk_level === 'MEDIUM';

                  return (
                    <tr
                      key={f.id}
                      className="hover:bg-surface-elevated/60 cursor-pointer transition-colors"
                      onClick={() => setSelectedFlight(f)}
                    >
                      <td className="p-3 font-bold text-white flex items-center gap-1.5">
                        <Plane className="w-3.5 h-3.5 text-muted" />
                        <span>{f.flight_number}</span>
                      </td>
                      <td className="p-3 text-muted">{f.airline}</td>
                      <td className="p-3 text-white">{f.aircraft_type}</td>
                      <td className="p-3 text-muted">
                        <span className="text-white">{f.origin}</span> →{' '}
                        <span className="text-white">{f.destination}</span>
                        <span className="ml-1.5 text-[9px] px-1 py-0.2 bg-surface-elevated rounded border border-muted/20">
                          {f.route_type[0]}
                        </span>
                      </td>
                      <td className="p-3 text-muted">
                        <div>
                          Arr:{' '}
                          <span className="text-white">
                            {f.scheduled_arrival ? f.scheduled_arrival.substring(11, 16) : '-'}
                          </span>
                        </div>
                        <div>
                          Dep:{' '}
                          <span className="text-white">
                            {f.scheduled_departure ? f.scheduled_departure.substring(11, 16) : '-'}
                          </span>
                        </div>
                      </td>
                      <td className="p-3 font-bold text-green">
                        {f.assigned_gate ? f.assigned_gate.gate_number : 'UNASSIGNED'}
                      </td>
                      <td className="p-3 text-white">
                        {f.prediction ? (
                          <span>{f.prediction.predicted_taxi_out_minutes.toFixed(1)}m</span>
                        ) : (
                          <span className="text-muted italic">unpredicted</span>
                        )}
                      </td>
                      <td className="p-3">
                        {f.prediction ? (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              isHigh
                                ? 'bg-red/20 text-red border border-red/30'
                                : isMed
                                ? 'bg-amber/20 text-amber border border-amber/30'
                                : 'bg-green/20 text-green border border-green/30'
                            }`}
                          >
                            {f.prediction.risk_level} ({f.prediction.predicted_delay_minutes.toFixed(0)}m)
                          </span>
                        ) : (
                          <span className="text-muted text-[10px]">-</span>
                        )}
                      </td>
                      <td className="p-3 text-right" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handlePredictSingle(f.id)}
                          disabled={predictingId === f.id}
                          className="px-2 py-1 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-[10px] text-white transition-colors"
                        >
                          {predictingId === f.id ? 'Evaluating...' : 'Predict ML'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-3 border-t border-muted/20 flex items-center justify-between text-muted text-xs">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} operations
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-2.5 py-1 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded disabled:opacity-30"
            >
              Previous
            </button>
            <span className="text-white">Page {page} of {Math.ceil(total / pageSize) || 1}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * pageSize >= total}
              className="px-2.5 py-1 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded disabled:opacity-30"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Flight Inspector Modal / Drawer */}
      {selectedFlight && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-surface border border-muted/30 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 font-mono text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-muted/20 pb-3">
              <div className="flex items-center gap-3">
                <Plane className="w-5 h-5 text-green" />
                <div>
                  <h2 className="text-base font-bold text-white">
                    {selectedFlight.flight_number} — {selectedFlight.airline}
                  </h2>
                  <p className="text-[11px] text-muted">
                    {selectedFlight.aircraft_type} • {selectedFlight.route_type} ROUTE
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedFlight(null)}
                className="p-1 rounded bg-surface-elevated hover:bg-muted-dark text-muted hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Flight Timetable Details */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                <div className="text-[10px] text-muted">ORIGIN / DESTINATION</div>
                <div className="text-sm font-bold text-white mt-1">
                  {selectedFlight.origin} → {selectedFlight.destination}
                </div>
                <div className="text-[10px] text-muted mt-1">
                  Status: <span className="text-green font-semibold">{selectedFlight.status}</span>
                </div>
              </div>

              <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                <div className="text-[10px] text-muted">GATE ASSIGNMENT</div>
                <div className="text-sm font-bold text-green mt-1">
                  {selectedFlight.assigned_gate ? `GATE ${selectedFlight.assigned_gate.gate_number}` : 'STANDBY'}
                </div>
                <div className="text-[10px] text-muted mt-1">
                  Terminal: {selectedFlight.assigned_gate?.terminal || 'T1'}
                </div>
              </div>
            </div>

            {/* ML Prediction Analysis */}
            <div className="p-4 bg-surface-elevated rounded border border-muted/20 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-white font-bold">
                  <BrainCircuit className="w-4 h-4 text-green" />
                  <span>ML TAXI DELAY RISK ASSESSMENT</span>
                </div>
                {selectedFlight.prediction && (
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      selectedFlight.prediction.risk_level === 'HIGH'
                        ? 'bg-red/20 text-red border border-red/30'
                        : selectedFlight.prediction.risk_level === 'MEDIUM'
                        ? 'bg-amber/20 text-amber border border-amber/30'
                        : 'bg-green/20 text-green border border-green/30'
                    }`}
                  >
                    {selectedFlight.prediction.risk_level} RISK
                  </span>
                )}
              </div>

              {selectedFlight.prediction ? (
                <div className="grid grid-cols-3 gap-2 pt-2 text-center">
                  <div className="p-2 bg-surface rounded">
                    <div className="text-[9px] text-muted">PREDICTED TAXI TIME</div>
                    <div className="text-sm font-bold text-white mt-1">
                      {selectedFlight.prediction.predicted_taxi_out_minutes.toFixed(1)} min
                    </div>
                  </div>
                  <div className="p-2 bg-surface rounded">
                    <div className="text-[9px] text-muted">DERIVED TAXI DELAY</div>
                    <div className="text-sm font-bold text-amber mt-1">
                      {selectedFlight.prediction.predicted_delay_minutes.toFixed(1)} min
                    </div>
                  </div>
                  <div className="p-2 bg-surface rounded">
                    <div className="text-[9px] text-muted">CONFIDENCE SCORE</div>
                    <div className="text-sm font-bold text-green mt-1">
                      {(selectedFlight.prediction.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-3 text-center text-muted">
                  No prediction calculated yet for this flight slot.
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => handlePredictSingle(selectedFlight.id)}
                disabled={predictingId === selectedFlight.id}
                className="px-4 py-2 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-green font-semibold transition-colors"
              >
                {predictingId === selectedFlight.id ? 'Recalculating...' : 'Recalculate ML Risk'}
              </button>
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
