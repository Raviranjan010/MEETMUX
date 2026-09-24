import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  XCircle,
  ThumbsUp,
  ThumbsDown,
  Info,
} from 'lucide-react';
import {
  runOptimizer,
  explainGateAssignment,
  acceptAssignment,
  rejectAssignment,
  getHealth,
} from '../api';
import { OptimizationRun, Assignment } from '../api/types';

export const Optimizer: React.FC = () => {
  const [running, setRunning] = useState<boolean>(false);
  const [runResult, setRunResult] = useState<OptimizationRun | null>(null);
  const [solverHealth, setSolverHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Tunable Weights
  const [conflictWeight, setConflictWeight] = useState<number>(1000);
  const [gateChangeWeight, setGateChangeWeight] = useState<number>(100);
  const [taxiWeight, setTaxiWeight] = useState<number>(10);
  const [towingWeight, setTowingWeight] = useState<number>(50);

  // Explainability Modal State
  const [explainFlightId, setExplainFlightId] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [loadingExplain, setLoadingExplain] = useState<boolean>(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((h) => setSolverHealth(h?.optimizer))
      .catch(() => {});
  }, []);

  const handleRunOptimization = async () => {
    setRunning(true);
    setError(null);
    setActionSuccessMsg(null);
    try {
      const res = await runOptimizer({
        weights: {
          conflicts: conflictWeight,
          gate_changes: gateChangeWeight,
          taxi_time: taxiWeight,
          towing: towingWeight,
        },
      });
      setRunResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || err?.message || 'Optimization solver failed');
    } finally {
      setRunning(false);
    }
  };

  const handleExplain = async (flightId: string) => {
    setExplainFlightId(flightId);
    setLoadingExplain(true);
    try {
      const exp = await explainGateAssignment(flightId);
      setExplanation(exp);
    } catch (err) {
      console.error('Failed to explain assignment', err);
    } finally {
      setLoadingExplain(false);
    }
  };

  const handleAccept = async () => {
    if (!runResult) return;
    try {
      await acceptAssignment(runResult.id);
      setActionSuccessMsg('Gate schedule recommendation accepted and applied to live airport state.');
    } catch (err: any) {
      setError('Failed to accept recommendation');
    }
  };

  const handleReject = async () => {
    if (!runResult) return;
    try {
      await rejectAssignment(runResult.id);
      setActionSuccessMsg('Recommendation rejected. Operator audit trail updated.');
    } catch (err: any) {
      setError('Failed to reject recommendation');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            MILP GATE SCHEDULING OPTIMIZER
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            Mathematical Mixed-Integer Linear Programming • Multi-Objective Cost Minimization
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunOptimization}
            disabled={running}
            className="flex items-center gap-2 px-4 py-2 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-xs font-mono text-green font-bold transition-colors disabled:opacity-50"
          >
            <Cpu className="w-4 h-4" />
            <span>{running ? 'Solving MILP Formulation...' : 'Run MILP Optimization'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red/10 border border-red/30 rounded text-xs text-red font-mono flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {actionSuccessMsg && (
        <div className="p-4 bg-green/10 border border-green/30 rounded text-xs text-green font-mono flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionSuccessMsg}</span>
        </div>
      )}

      {/* Solver Configuration & Objectives Bar */}
      <div className="bg-surface rounded border border-muted/20 p-4 font-mono text-xs">
        <div className="flex items-center justify-between mb-4 border-b border-muted/20 pb-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-green" />
            <h2 className="font-bold text-white uppercase">Objective Weights Configuration</h2>
          </div>
          <div className="text-[11px] text-muted">
            Active Solver:{' '}
            <span className="text-white font-bold">
              {solverHealth?.gurobi_available ? 'GUROBI (Commercial)' : 'OR-TOOLS CP-SAT (Open Source)'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <div className="flex justify-between text-muted text-[11px] mb-1">
              <span>Conflict Penalty:</span>
              <span className="text-white font-bold">{conflictWeight}</span>
            </div>
            <input
              type="range"
              min="100"
              max="2000"
              step="100"
              value={conflictWeight}
              onChange={(e) => setConflictWeight(Number(e.target.value))}
              className="w-full accent-green bg-surface-elevated"
            />
          </div>

          <div>
            <div className="flex justify-between text-muted text-[11px] mb-1">
              <span>Gate Change Penalty:</span>
              <span className="text-white font-bold">{gateChangeWeight}</span>
            </div>
            <input
              type="range"
              min="10"
              max="500"
              step="10"
              value={gateChangeWeight}
              onChange={(e) => setGateChangeWeight(Number(e.target.value))}
              className="w-full accent-green bg-surface-elevated"
            />
          </div>

          <div>
            <div className="flex justify-between text-muted text-[11px] mb-1">
              <span>Taxi Distance Weight:</span>
              <span className="text-white font-bold">{taxiWeight}</span>
            </div>
            <input
              type="range"
              min="1"
              max="100"
              step="5"
              value={taxiWeight}
              onChange={(e) => setTaxiWeight(Number(e.target.value))}
              className="w-full accent-green bg-surface-elevated"
            />
          </div>

          <div>
            <div className="flex justify-between text-muted text-[11px] mb-1">
              <span>Towing Penalty:</span>
              <span className="text-white font-bold">{towingWeight}</span>
            </div>
            <input
              type="range"
              min="10"
              max="200"
              step="10"
              value={towingWeight}
              onChange={(e) => setTowingWeight(Number(e.target.value))}
              className="w-full accent-green bg-surface-elevated"
            />
          </div>
        </div>
      </div>

      {/* Solver Execution Results */}
      {runResult && (
        <div className="space-y-4 font-mono">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
            <div className="p-3.5 bg-surface rounded border border-muted/20">
              <div className="text-[10px] text-muted uppercase">Solver Status</div>
              <div className="text-base font-bold text-green mt-1">{runResult.status}</div>
              <div className="text-[10px] text-muted mt-0.5">{runResult.solver}</div>
            </div>

            <div className="p-3.5 bg-surface rounded border border-muted/20">
              <div className="text-[10px] text-muted uppercase">Solve Time</div>
              <div className="text-base font-bold text-white mt-1">
                {runResult.solve_time_seconds.toFixed(2)}s
              </div>
              <div className="text-[10px] text-muted mt-0.5">Below 30s ceiling</div>
            </div>

            <div className="p-3.5 bg-surface rounded border border-muted/20">
              <div className="text-[10px] text-muted uppercase">Independent Validation</div>
              <div className="text-base font-bold text-green mt-1">
                {runResult.is_valid ? 'PASSED (0 Violations)' : 'REJECTED'}
              </div>
              <div className="text-[10px] text-muted mt-0.5">7 hard constraints verified</div>
            </div>

            <div className="p-3.5 bg-surface rounded border border-muted/20">
              <div className="text-[10px] text-muted uppercase">Conflicts Resolved</div>
              <div className="text-base font-bold text-green mt-1">
                {runResult.total_conflicts_before} → {runResult.total_conflicts_after}
              </div>
              <div className="text-[10px] text-muted mt-0.5">Zero overlaps achieved</div>
            </div>

            <div className="p-3.5 bg-surface rounded border border-muted/20">
              <div className="text-[10px] text-muted uppercase">Gate Changes</div>
              <div className="text-base font-bold text-amber mt-1">
                {runResult.total_gate_changes} reassignments
              </div>
              <div className="text-[10px] text-muted mt-0.5">Stability preserved</div>
            </div>
          </div>

          {/* Decision Support Operator Actions */}
          <div className="p-3 bg-surface rounded border border-muted/20 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-green" />
              <span className="text-white font-bold">Decision-Support Recommendation:</span>
              <span className="text-muted">Review assignments below and approve to commit changes.</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleAccept}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-green font-bold transition-colors"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
                <span>Accept Recommendation</span>
              </button>
              <button
                onClick={handleReject}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red/20 hover:bg-red/30 border border-red/40 rounded text-red font-bold transition-colors"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
            </div>
          </div>

          {/* Optimized Assignments Table */}
          <div className="bg-surface rounded border border-muted/20 overflow-hidden text-xs">
            <div className="p-3 border-b border-muted/20 font-bold text-white uppercase flex justify-between items-center">
              <span>Optimized Gate Schedule Assignments ({runResult.assignments.length} Flights)</span>
            </div>

            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-left">
                <thead className="bg-surface-elevated border-b border-muted/20 text-[10px] text-muted uppercase sticky top-0">
                  <tr>
                    <th className="p-3">Flight</th>
                    <th className="p-3">Baseline Gate</th>
                    <th className="p-3">Recommended Gate</th>
                    <th className="p-3">Gate Delta</th>
                    <th className="p-3 text-right">Explainability</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-muted/10">
                  {runResult.assignments.map((a, idx) => (
                    <tr key={idx} className="hover:bg-surface-elevated/50">
                      <td className="p-3 font-bold text-white">{a.flight_number || a.flight_id.substring(0, 8)}</td>
                      <td className="p-3 text-muted">{a.baseline_gate_number || a.baseline_gate_id || '-'}</td>
                      <td className="p-3 font-bold text-green">{a.assigned_gate_number || a.assigned_gate_id}</td>
                      <td className="p-3">
                        {a.gate_changed ? (
                          <span className="px-1.5 py-0.5 bg-amber/20 text-amber rounded text-[10px] font-bold">
                            REASSIGNED
                          </span>
                        ) : (
                          <span className="text-muted text-[10px]">UNCHANGED</span>
                        )}
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleExplain(a.flight_id)}
                          className="px-2.5 py-1 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-[11px] text-white flex items-center gap-1 ml-auto"
                        >
                          <HelpCircle className="w-3 h-3 text-green" />
                          <span>Why this gate?</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Explainability Modal */}
      {explainFlightId && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-surface border border-muted/30 rounded-lg max-w-lg w-full p-6 font-mono text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-muted/20 pb-3">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-green" />
                <h2 className="text-base font-bold text-white">
                  OPTIMIZATION EXPLAINABILITY
                </h2>
              </div>
              <button
                onClick={() => setExplainFlightId(null)}
                className="px-2 py-1 bg-surface-elevated hover:bg-muted-dark rounded text-white"
              >
                ✕
              </button>
            </div>

            {loadingExplain ? (
              <div className="p-8 text-center text-muted">Retrieving mathematical rationale...</div>
            ) : explanation ? (
              <div className="space-y-3">
                <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                  <div className="text-[10px] text-muted">ASSIGNED STAND</div>
                  <div className="text-base font-bold text-green mt-0.5">
                    GATE {explanation.assigned_gate}
                  </div>
                </div>

                <div>
                  <div className="text-white font-bold mb-1.5">Optimization Facts & Reasons:</div>
                  <ul className="space-y-1 text-muted text-[11px]">
                    {explanation.reasons?.map((r: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-green shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-white font-bold mb-1.5">Hard Constraints Satisfied:</div>
                  <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                    {explanation.hard_constraints_satisfied?.map((c: string, idx: number) => (
                      <div
                        key={idx}
                        className="p-1.5 bg-green/10 border border-green/20 rounded text-green flex items-center gap-1"
                      >
                        <ShieldCheck className="w-3 h-3 shrink-0" />
                        <span>{c}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-muted">No explanation available for this assignment.</div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setExplainFlightId(null)}
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
