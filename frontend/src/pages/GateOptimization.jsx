import React, { useState } from 'react';
import { runOptimization } from '../services/api';
import { formatDateTime, getDelayBadgeClass } from '../utils/formatters';
import { 
  Split, 
  Play, 
  RotateCcw, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  Cpu, 
  Clock, 
  Sliders,
  DoorClosed,
  ChevronRight,
  ShieldCheck,
  Check
} from 'lucide-react';

export default function GateOptimization() {
  const [solver, setSolver] = useState('ortools');
  const [timeLimit, setTimeLimit] = useState(60);
  const [bufferMinutes, setBufferMinutes] = useState(15.0);
  const [weights, setWeights] = useState({
    conflict: 1000.0,
    walking_distance: 1.0,
    delay_propagation: 10.0,
    reassignment: 5.0,
    unused_gate: 1.0,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [filterTerminal, setFilterTerminal] = useState('ALL');

  const handleWeightChange = (key, val) => {
    setWeights((prev) => ({
      ...prev,
      [key]: parseFloat(val) || 0,
    }));
  };

  const handleReset = () => {
    setWeights({
      conflict: 1000.0,
      walking_distance: 1.0,
      delay_propagation: 10.0,
      reassignment: 5.0,
      unused_gate: 1.0,
    });
    setSolver('ortools');
    setTimeLimit(60);
    setBufferMinutes(15.0);
  };

  const handleRunOptimization = async () => {
    try {
      setLoading(true);
      const res = await runOptimization({
        solver,
        time_limit_seconds: timeLimit,
        buffer_minutes: bufferMinutes,
        weights,
      });
      setResult(res.data);
    } catch (err) {
      console.error('Optimization failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!result || !result.assignments) return;

    const headers = ['Flight,Airline,Aircraft,Terminal,Gate,Gate Terminal,Arrival,Departure,Delay Min,Status\n'];
    const rows = result.assignments.map((a) =>
      `"${a.flight_number}","${a.airline}","${a.aircraft_type}","${a.terminal}","${a.gate_number}","${a.gate_terminal}","${a.arrival_time}","${a.departure_time}","${a.predicted_delay_minutes}","${a.assignment_status}"`
    );

    const blob = new Blob([headers.concat(rows.join('\n')).join('')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `runwayoptx_gate_assignments_${result.optimization_run_id || 'latest'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const displayedAssignments = result?.assignments
    ? result.assignments.filter((a) => filterTerminal === 'ALL' || a.terminal === filterTerminal)
    : [];

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Split size={20} color="#FFB52E" />
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Gate Scheduling (MILP Optimizer)</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Mixed Integer Linear Programming with Google OR-Tools optimizing gate allocations & turnaround intervals
          </p>
        </div>

        {result && (
          <button className="btn btn-outline-amber" onClick={handleExportCSV}>
            <Download size={16} />
            <span>Export Assignments CSV</span>
          </button>
        )}
      </div>

      {/* Solver Configuration Panel */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
          <Sliders size={18} color="#FFB52E" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Solver Engine & Objective Weight Penalties</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          <div>
            <label className="form-label">Solver Engine</label>
            <select className="form-select" value={solver} onChange={(e) => setSolver(e.target.value)}>
              <option value="ortools">Google OR-Tools (CBC/SCIP)</option>
              <option value="gurobi">Gurobi MILP Engine</option>
            </select>
          </div>

          <div>
            <label className="form-label">Time Limit (seconds)</label>
            <input
              type="number"
              className="form-input mono"
              value={timeLimit}
              onChange={(e) => setTimeLimit(parseInt(e.target.value) || 60)}
            />
          </div>

          <div>
            <label className="form-label">Turnaround Buffer (min)</label>
            <input
              type="number"
              className="form-input mono"
              value={bufferMinutes}
              onChange={(e) => setBufferMinutes(parseFloat(e.target.value) || 15.0)}
            />
          </div>

          <div>
            <label className="form-label">Conflict Penalty (w1)</label>
            <input
              type="number"
              className="form-input mono"
              value={weights.conflict}
              onChange={(e) => handleWeightChange('conflict', e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Walking Distance (w2)</label>
            <input
              type="number"
              step="0.5"
              className="form-input mono"
              value={weights.walking_distance}
              onChange={(e) => handleWeightChange('walking_distance', e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Delay Propagation (w3)</label>
            <input
              type="number"
              step="0.5"
              className="form-input mono"
              value={weights.delay_propagation}
              onChange={(e) => handleWeightChange('delay_propagation', e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Reassignment (w4)</label>
            <input
              type="number"
              step="0.5"
              className="form-input mono"
              value={weights.reassignment}
              onChange={(e) => handleWeightChange('reassignment', e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Unused Gate (w5)</label>
            <input
              type="number"
              step="0.5"
              className="form-input mono"
              value={weights.unused_gate}
              onChange={(e) => handleWeightChange('unused_gate', e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={handleRunOptimization} disabled={loading}>
            <Play size={16} />
            <span>{loading ? 'Solving Mixed Integer Program...' : 'Run MILP Optimization'}</span>
          </button>
          <button className="btn btn-secondary" onClick={handleReset}>
            <RotateCcw size={16} />
            <span>Reset Defaults</span>
          </button>
        </div>
      </div>

      {/* Optimization Summary KPIs */}
      {result && (
        <div className="animate-slide-up" style={{ marginBottom: '24px' }}>
          <div className="kpi-grid">
            <div className="glass-card" style={{ borderLeft: '4px solid #19D88A' }}>
              <span className="form-label">Solver Status</span>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#19D88A', lineHeight: 1.2 }}>
                {result.status.toUpperCase()}
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Backend: {result.solver}
              </p>
            </div>

            <div className="glass-card" style={{ borderLeft: '4px solid #FFB52E' }}>
              <span className="form-label">Execution Time</span>
              <h3 className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFB52E', lineHeight: 1.2 }}>
                {result.execution_time_seconds}s
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Time limit: {timeLimit}s
              </p>
            </div>

            <div className="glass-card" style={{ borderLeft: '4px solid #9B6CFF' }}>
              <span className="form-label">Objective Value</span>
              <h3 className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#9B6CFF', lineHeight: 1.2 }}>
                {result.objective_value ?? 'N/A'}
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Global operational penalty minimized
              </p>
            </div>

            <div className="glass-card" style={{ borderLeft: '4px solid #19D88A' }}>
              <span className="form-label">Flights Assigned</span>
              <h3 className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#19D88A', lineHeight: 1.2 }}>
                {result.assigned_flights} / {result.total_flights}
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {result.unassigned_flights} unassigned
              </p>
            </div>
          </div>

          {/* Diagnostics Message */}
          {result.diagnostics?.errors?.length > 0 ? (
            <div style={{ padding: '14px 18px', borderRadius: '8px', background: 'rgba(255, 77, 77, 0.12)', border: '1px solid rgba(255, 77, 77, 0.35)', marginBottom: '20px' }}>
              <p style={{ fontWeight: 700, color: '#FF4D4D' }}>Validation Errors Detected:</p>
              <ul style={{ fontSize: '0.8125rem', marginTop: '6px', paddingLeft: '20px', color: '#FF8080' }}>
                {result.diagnostics.errors.map((err, idx) => <li key={idx}>{err}</li>)}
              </ul>
            </div>
          ) : (
            <div style={{ padding: '14px 18px', borderRadius: '8px', background: 'rgba(25, 216, 138, 0.12)', border: '1px solid rgba(25, 216, 138, 0.35)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle2 color="#19D88A" size={20} />
              <p style={{ fontSize: '0.875rem', fontWeight: 700, color: '#19D88A' }}>
                Assignment mathematically validated: Zero overlapping intervals, 100% aircraft & terminal constraints respected.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Assignments Table */}
      {result && (
        <div className="glass-card animate-slide-up">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Optimal Gate Assignments</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Flight to gate mapping optimized for minimum delay propagation
              </p>
            </div>
            
            <div style={{ display: 'flex', gap: '6px' }}>
              {['ALL', 'T1', 'T2', 'T3'].map((t) => (
                <button
                  key={t}
                  className={`btn ${filterTerminal === t ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '4px 12px', fontSize: '0.75rem', borderRadius: 'var(--radius-pill)' }}
                  onClick={() => setFilterTerminal(t)}
                >
                  {t === 'ALL' ? 'All Terminals' : t}
                </button>
              ))}
            </div>
          </div>

          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Flight</th>
                  <th>Airline</th>
                  <th>Aircraft</th>
                  <th>Flight Terminal</th>
                  <th>Assigned Gate</th>
                  <th>Gate Terminal</th>
                  <th>Arrival (UTC)</th>
                  <th>Departure (UTC)</th>
                  <th>Predicted Delay</th>
                  <th>Walk Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {displayedAssignments.map((a) => (
                  <tr key={a.flight_id}>
                    <td className="mono" style={{ fontWeight: 800, color: '#FFB52E' }}>{a.flight_number}</td>
                    <td style={{ fontWeight: 600 }}>{a.airline}</td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>{a.aircraft_type}</td>
                    <td><span style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(255, 181, 46, 0.08)', color: '#FFB52E', fontWeight: 700, fontSize: '0.75rem' }}>{a.terminal}</span></td>
                    <td className="mono" style={{ fontWeight: 800, color: '#19D88A', fontSize: '0.9375rem' }}>{a.gate_number}</td>
                    <td><span style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(25, 216, 138, 0.1)', color: '#19D88A', fontWeight: 700, fontSize: '0.75rem' }}>{a.gate_terminal}</span></td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>{formatDateTime(a.arrival_time)}</td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>{formatDateTime(a.departure_time)}</td>
                    <td><span className={`badge ${getDelayBadgeClass(a.delay_category)}`}>+{a.predicted_delay_minutes.toFixed(0)}m</span></td>
                    <td className="mono" style={{ color: '#F5F7FA' }}>{a.walking_distance_score.toFixed(1)}x</td>
                    <td><span style={{ color: '#19D88A', fontWeight: 700, fontSize: '0.8125rem' }}>{a.assignment_status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
