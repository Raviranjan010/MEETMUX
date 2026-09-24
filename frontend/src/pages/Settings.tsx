import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Save,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  Sliders,
  ShieldCheck,
} from 'lucide-react';
import { getConfig, updateConfig } from '../api';
import { SystemConfig } from '../api/types';

export const Settings: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const res = await getConfig();
      setConfig(res);
    } catch (err: any) {
      // Provide defaults if DB config is empty
      setConfig({
        turnaround_buffer_minutes: 45,
        high_risk_delay_threshold: 30,
        medium_risk_delay_threshold: 15,
        solver_timeout_seconds: 30,
        weight_conflicts: 1000,
        weight_gate_changes: 100,
        weight_taxi_time: 10,
        weight_towing: 50,
        weight_unpreferred_gate: 25,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;
    setSaving(true);
    setError(null);
    setSavedSuccess(false);
    try {
      const updated = await updateConfig(config);
      setConfig(updated);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || err?.message || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return <div className="p-8 text-center text-muted font-mono text-xs">Loading configuration...</div>;
  }

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            SYSTEM PARAMETERS & CONFIGURATION
          </h1>
          <p className="text-muted text-[11px] mt-0.5">
            Turnaround buffer intervals, ML risk threshold limits, and optimizer cost weightings
          </p>
        </div>

        <button
          onClick={fetchConfig}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-white transition-colors"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>Reload</span>
        </button>
      </div>

      {savedSuccess && (
        <div className="p-3.5 bg-green/10 border border-green/30 rounded text-green flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>System configuration saved and re-applied to operational engine.</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-red/10 border border-red/30 rounded text-red flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Operational Constraints */}
        <div className="bg-surface rounded border border-muted/20 p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-muted/20 pb-3">
            <ShieldCheck className="w-4 h-4 text-green" />
            <h2 className="font-bold text-white uppercase text-sm">Gate Buffers & Risk Thresholds</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-muted text-[11px] mb-1">
                Turnaround Buffer (Minutes):
              </label>
              <input
                type="number"
                min="15"
                max="120"
                value={config.turnaround_buffer_minutes}
                onChange={(e) =>
                  setConfig({ ...config, turnaround_buffer_minutes: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
              <span className="text-[10px] text-muted mt-0.5 block">Minimum separation between flights</span>
            </div>

            <div>
              <label className="block text-muted text-[11px] mb-1">
                High Risk Threshold (Minutes):
              </label>
              <input
                type="number"
                min="15"
                max="90"
                value={config.high_risk_delay_threshold}
                onChange={(e) =>
                  setConfig({ ...config, high_risk_delay_threshold: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
              <span className="text-[10px] text-muted mt-0.5 block">Flags flight as HIGH delay risk</span>
            </div>

            <div>
              <label className="block text-muted text-[11px] mb-1">
                Medium Risk Threshold (Minutes):
              </label>
              <input
                type="number"
                min="5"
                max="45"
                value={config.medium_risk_delay_threshold}
                onChange={(e) =>
                  setConfig({ ...config, medium_risk_delay_threshold: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
              <span className="text-[10px] text-muted mt-0.5 block">Flags flight as MEDIUM delay risk</span>
            </div>
          </div>
        </div>

        {/* MILP Optimization Solver Weights */}
        <div className="bg-surface rounded border border-muted/20 p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-muted/20 pb-3">
            <Sliders className="w-4 h-4 text-green" />
            <h2 className="font-bold text-white uppercase text-sm">MILP Solver Objective Weights</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-muted text-[11px] mb-1">Conflict Avoidance Penalty:</label>
              <input
                type="number"
                value={config.weight_conflicts}
                onChange={(e) =>
                  setConfig({ ...config, weight_conflicts: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
            </div>

            <div>
              <label className="block text-muted text-[11px] mb-1">Gate Change Penalty:</label>
              <input
                type="number"
                value={config.weight_gate_changes}
                onChange={(e) =>
                  setConfig({ ...config, weight_gate_changes: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
            </div>

            <div>
              <label className="block text-muted text-[11px] mb-1">Taxi Distance Weight:</label>
              <input
                type="number"
                value={config.weight_taxi_time}
                onChange={(e) =>
                  setConfig({ ...config, weight_taxi_time: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
            </div>

            <div>
              <label className="block text-muted text-[11px] mb-1">Towing / Remote Stand Penalty:</label>
              <input
                type="number"
                value={config.weight_towing}
                onChange={(e) =>
                  setConfig({ ...config, weight_towing: Number(e.target.value) })
                }
                className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none focus:border-green"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 bg-green/20 hover:bg-green/30 border border-green/40 rounded text-green font-bold transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save & Commit Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
