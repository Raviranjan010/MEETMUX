import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchHealth, HealthResponse } from '../api/health';
import { StatusPill } from '../components/StatusPill';
import {
  Activity,
  Database,
  BrainCircuit,
  Cpu,
  Plane,
  DoorClosed,
  ArrowRight,
  AlertTriangle,
  RotateCw,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || err?.message || 'Unable to connect to backend service');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse" data-testid="dashboard-loading">
        <div className="h-8 w-64 bg-surface rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-surface rounded border border-muted/20"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-surface border border-red/30 rounded" data-testid="dashboard-error">
        <div className="flex items-center gap-3 text-red mb-3">
          <AlertTriangle className="w-6 h-6" />
          <h2 className="text-lg font-semibold">Backend Service Unreachable</h2>
        </div>
        <p className="text-sm text-muted mb-6">{error}</p>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors"
        >
          <RotateCw className="w-4 h-4" />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-view">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white font-mono">OPERATIONS OVERVIEW</h1>
        <p className="text-xs text-muted">RunwayOptX Airport Traffic & Gate Scheduling Decision-Support System</p>
      </div>

      {/* Core Health Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* API Health */}
        <div className="p-4 bg-surface rounded border border-muted/20 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-muted uppercase">Backend Engine</span>
            <Activity className="w-4 h-4 text-green" />
          </div>
          <div>
            <div className="text-lg font-bold font-mono text-white mb-1">
              {health?.status.toUpperCase()}
            </div>
            <StatusPill
              label={health?.status === 'ok' ? 'NOMINAL' : 'DEGRADED'}
              status={health?.status === 'ok' ? 'ok' : 'warning'}
            />
          </div>
        </div>

        {/* Database Health */}
        <div className="p-4 bg-surface rounded border border-muted/20 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-muted uppercase">Database Layer</span>
            <Database className="w-4 h-4 text-green" />
          </div>
          <div>
            <div className="text-lg font-bold font-mono text-white mb-1">
              {health?.database ? 'CONNECTED' : 'DISCONNECTED'}
            </div>
            <StatusPill
              label={health?.database ? 'ONLINE' : 'OFFLINE'}
              status={health?.database ? 'ok' : 'error'}
            />
          </div>
        </div>

        {/* ML Model Health */}
        <div className="p-4 bg-surface rounded border border-muted/20 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-muted uppercase">Delay Predictor (ML)</span>
            <BrainCircuit className="w-4 h-4 text-amber" />
          </div>
          <div>
            <div className="text-lg font-bold font-mono text-white mb-1">
              {health?.ml_model_loaded ? 'LOADED' : 'NOT TRAINED'}
            </div>
            <StatusPill
              label={health?.ml_model_loaded ? 'ACTIVE' : 'PENDING P4'}
              status={health?.ml_model_loaded ? 'ok' : 'neutral'}
            />
          </div>
        </div>

        {/* Solver Health */}
        <div className="p-4 bg-surface rounded border border-muted/20 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-muted uppercase">MILP Solver</span>
            <Cpu className="w-4 h-4 text-green" />
          </div>
          <div>
            <div className="text-lg font-bold font-mono text-white mb-1">
              {health?.optimizer.gurobi_available
                ? 'GUROBI'
                : health?.optimizer.ortools_available
                ? 'OR-TOOLS CP-SAT'
                : 'UNAVAILABLE'}
            </div>
            <StatusPill
              label={health?.optimizer.gurobi_available ? 'PRIMARY' : 'FALLBACK ACTIVE'}
              status={health?.optimizer.gurobi_available || health?.optimizer.ortools_available ? 'ok' : 'error'}
              subtext={health?.optimizer.gurobi_available ? 'Gurobi' : health?.optimizer.ortools_available ? 'OR-Tools, no license required' : 'None'}
            />
          </div>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <div className="mt-8">
        <h2 className="text-sm font-mono uppercase text-muted mb-4">Command Center Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/flights"
            className="p-4 bg-surface hover:bg-surface-elevated rounded border border-muted/20 transition-colors flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-surface-elevated border border-muted/20 text-white">
                <Plane className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-white group-hover:text-green transition-colors">Flight Operations</div>
                <div className="text-xs text-muted">Inspect flight schedules & taxi delay risk</div>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-green transition-transform group-hover:translate-x-1" />
          </Link>

          <Link
            to="/gates"
            className="p-4 bg-surface hover:bg-surface-elevated rounded border border-muted/20 transition-colors flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-surface-elevated border border-muted/20 text-white">
                <DoorClosed className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-white group-hover:text-green transition-colors">Gate Inventory</div>
                <div className="text-xs text-muted">View terminal gates, statuses & occupancy</div>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-green transition-transform group-hover:translate-x-1" />
          </Link>

          <Link
            to="/optimizer"
            className="p-4 bg-surface hover:bg-surface-elevated rounded border border-muted/20 transition-colors flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-surface-elevated border border-muted/20 text-white">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-white group-hover:text-green transition-colors">Gate Optimizer</div>
                <div className="text-xs text-muted">Solve MILP schedule optimization</div>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-green transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </div>
  );
};
