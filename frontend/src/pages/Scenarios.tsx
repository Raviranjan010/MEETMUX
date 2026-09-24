import React, { useState, useEffect } from 'react';
import {
  Flame,
  CloudRain,
  AlertOctagon,
  DoorClosed,
  TrendingUp,
  Clock,
  GitFork,
  RotateCw,
  Cpu,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { runScenario, resetScenario, runReoptimization, getScenarios } from '../api';
import { ScenarioResult } from '../api/types';

export const Scenarios: React.FC = () => {
  const [running, setRunning] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [reoptimizing, setReoptimizing] = useState<boolean>(false);
  const [activeResult, setActiveResult] = useState<ScenarioResult | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scenarioCards = [
    {
      id: 'heavy_rain',
      name: 'Heavy Rain Storm',
      icon: CloudRain,
      desc: 'Reduces runway acceptance rates by 40%, increases taxi durations and elevates delay risks.',
      severity: 'WARNING',
    },
    {
      id: 'runway_closure',
      name: 'Runway 09R/27L Closure',
      icon: AlertOctagon,
      desc: 'Single runway operations mode. Shifts all departure traffic onto 09L/27R creating severe queue congestion.',
      severity: 'CRITICAL',
    },
    {
      id: 'gate_closure',
      name: 'Gate Stand Maintenance Closure',
      icon: DoorClosed,
      desc: 'Blocks contact stands G04, G05, and G12 due to ground equipment failure. Forces gate reallocations.',
      severity: 'WARNING',
    },
    {
      id: 'traffic_surge',
      name: 'Peak Hour Traffic Surge',
      icon: TrendingUp,
      desc: 'Simulates sudden +40% inbound flight compression during evening bank.',
      severity: 'WARNING',
    },
    {
      id: 'flight_delay',
      name: 'Inbound Flight Major Delay',
      icon: Clock,
      desc: 'Injects +75 min delay into major hub flight AI-204, extending gate occupancy into next flight slot.',
      severity: 'CRITICAL',
    },
    {
      id: 'gate_conflict',
      name: 'Direct Gate Conflict',
      icon: AlertTriangle,
      desc: 'Induces deliberate overlapping arrival reservation on Gate G15 with zero buffer.',
      severity: 'CRITICAL',
    },
    {
      id: 'cascade_delay',
      name: 'Downstream Delay Cascade',
      icon: GitFork,
      desc: 'Triggers multi-hop delay chain across 8 connecting aircraft turnarounds.',
      severity: 'CRITICAL',
    },
  ];

  const handleRunScenario = async (type: string) => {
    setRunning(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await runScenario(type);
      setActiveResult(res);
      setSuccessMsg(`Simulated scenario: ${res.scenario_name}`);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || err?.message || 'Scenario execution failed');
    } finally {
      setRunning(false);
    }
  };

  const handleReset = async () => {
    setResetting(true);
    setError(null);
    try {
      await resetScenario();
      setActiveResult(null);
      setSuccessMsg('Airport state successfully reset to nominal baseline.');
    } catch (err: any) {
      setError('Reset failed');
    } finally {
      setResetting(false);
    }
  };

  const handleReoptimize = async () => {
    setReoptimizing(true);
    setError(null);
    try {
      await runReoptimization();
      setSuccessMsg('Full re-optimization completed across disrupted airport state.');
    } catch (err: any) {
      setError('Re-optimization failed');
    } finally {
      setReoptimizing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            WHAT-IF DISRUPTION SIMULATOR
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            Inject stochastic operational shocks, observe conflict propagation, and evaluate re-optimization
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white disabled:opacity-50"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>{resetting ? 'Resetting...' : 'Reset to Baseline'}</span>
          </button>
        </div>
      </div>

      {successMsg && (
        <div className="p-3.5 bg-green/10 border border-green/30 rounded text-xs text-green font-mono flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-red/10 border border-red/30 rounded text-xs text-red font-mono flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Disruption Scenarios Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-mono text-xs">
        {scenarioCards.map((sc) => {
          const Icon = sc.icon;
          const isCrit = sc.severity === 'CRITICAL';

          return (
            <div
              key={sc.id}
              className="p-4 bg-surface rounded border border-muted/20 flex flex-col justify-between hover:border-muted/40 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded bg-surface-elevated ${isCrit ? 'text-red' : 'text-amber'}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-bold text-white text-sm">{sc.name}</span>
                  </div>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                      isCrit ? 'bg-red/20 text-red' : 'bg-amber/20 text-amber'
                    }`}
                  >
                    {sc.severity}
                  </span>
                </div>
                <p className="text-[11px] text-muted leading-relaxed mt-2">{sc.desc}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-muted/20">
                <button
                  onClick={() => handleRunScenario(sc.id)}
                  disabled={running}
                  className="w-full py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs text-white transition-colors disabled:opacity-50"
                >
                  {running ? 'Injecting Disruption...' : 'Simulate Shock'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Scenario Impact Breakdown */}
      {activeResult && (
        <div className="bg-surface rounded border border-amber/40 p-5 font-mono text-xs space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-muted/20 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-amber" />
                <h2 className="text-base font-bold text-white uppercase">
                  SIMULATION ACTIVE: {activeResult.scenario_name}
                </h2>
              </div>
              <p className="text-[11px] text-muted mt-0.5">{activeResult.description}</p>
            </div>

            <button
              onClick={handleReoptimize}
              disabled={reoptimizing}
              className="flex items-center gap-2 px-4 py-2 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-green font-bold transition-colors disabled:opacity-50"
            >
              <Cpu className="w-4 h-4" />
              <span>{reoptimizing ? 'Re-optimizing...' : 'Resolve Shock with Re-optimizer'}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
            <div className="p-3 bg-surface-elevated rounded border border-muted/20">
              <div className="text-[10px] text-muted">AFFECTED FLIGHT OPERATIONS</div>
              <div className="text-2xl font-bold text-amber mt-1">
                {activeResult.affected_flights_count} Flights
              </div>
            </div>

            <div className="p-3 bg-surface-elevated rounded border border-muted/20">
              <div className="text-[10px] text-muted">NEW GATE OVERLAPS DETECTED</div>
              <div className="text-2xl font-bold text-red mt-1">
                {activeResult.conflicts_detected} Conflicts
              </div>
            </div>

            <div className="p-3 bg-surface-elevated rounded border border-muted/20">
              <div className="text-[10px] text-muted">CASCADE PROPAGATIONS</div>
              <div className="text-2xl font-bold text-white mt-1">
                {activeResult.cascade_events_count} Nodes
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
