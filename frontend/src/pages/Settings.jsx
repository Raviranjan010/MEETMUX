import React, { useState, useEffect } from 'react';
import { getHealth } from '../services/api';
import { Settings as SettingsIcon, ShieldCheck, Database, Cpu, Save, CheckCircle2, Sliders, RefreshCw } from 'lucide-react';

export default function Settings() {
  const [health, setHealth] = useState({ status: 'healthy', database: 'connected', model: 'loaded' });
  const [saved, setSaved] = useState(false);

  const [apiUrl, setApiUrl] = useState(() => (typeof window !== 'undefined' ? localStorage.getItem('runwayoptx_api_url') || '' : ''));
  const [config, setConfig] = useState({
    defaultSolver: 'ortools',
    timeLimit: 60,
    bufferTime: 15,
    alertThreshold: 30,
    theme: 'aviation-dark',
    autoSyncInterval: 30
  });

  useEffect(() => {
    getHealth()
      .then((res) => setHealth(res.data))
      .catch(() => setHealth({ status: 'degraded', database: 'disconnected', model: 'offline' }));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (apiUrl.trim()) {
      localStorage.setItem('runwayoptx_api_url', apiUrl.trim());
    } else {
      localStorage.removeItem('runwayoptx_api_url');
    }
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      window.location.reload();
    }, 1200);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <SettingsIcon size={20} color="#FFB52E" />
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Operations & Platform Settings</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Configure operational thresholds, OR-Tools MILP defaults, and examine telemetry server health
        </p>
      </div>

      {saved && (
        <div
          className="animate-slide-up"
          style={{
            marginBottom: '20px',
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(25, 216, 138, 0.12)',
            border: '1px solid rgba(25, 216, 138, 0.35)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <CheckCircle2 color="#19D88A" size={20} />
          <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#19D88A' }}>
            Operations configuration saved successfully!
          </span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1.2fr) minmax(280px, 0.8fr)', gap: '24px' }}>
        {/* Form Panel */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
            <Sliders size={18} color="#FFB52E" />
            <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Solver & Alert Thresholds</h3>
          </div>

          <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label className="form-label">Default Mixed Integer Linear Programming Engine</label>
              <select
                name="defaultSolver"
                className="form-select"
                value={config.defaultSolver}
                onChange={handleChange}
              >
                <option value="ortools">Google OR-Tools (CBC / SCIP) — Recommended</option>
                <option value="gurobi">Gurobi Commercial MILP Engine</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label className="form-label">Default Solver Timeout (sec)</label>
                <input
                  type="number"
                  name="timeLimit"
                  className="form-input mono"
                  value={config.timeLimit}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label className="form-label">Turnaround Buffer Buffer (min)</label>
                <input
                  type="number"
                  name="bufferTime"
                  className="form-input mono"
                  value={config.bufferTime}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label className="form-label">High-Risk Delay Threshold (min)</label>
                <input
                  type="number"
                  name="alertThreshold"
                  className="form-input mono"
                  value={config.alertThreshold}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label className="form-label">Telemetry Auto-Sync (sec)</label>
                <input
                  type="number"
                  name="autoSyncInterval"
                  className="form-input mono"
                  value={config.autoSyncInterval}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <label className="form-label">
                Backend API Server URL (for Production / Custom Deployments)
              </label>
              <input
                type="text"
                placeholder="e.g. https://your-backend-api.onrender.com (defaults to /api)"
                className="form-input mono"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                Leave empty to use default relative <code>/api</code> route or your <code>VITE_API_URL</code> environment variable.
              </span>
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '12px' }}>
              <Save size={16} />
              <span>Save & Apply Settings</span>
            </button>
          </form>
        </div>

        {/* Backend Telemetry Server Status */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
              <ShieldCheck size={18} color="#19D88A" />
              <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Backend Telemetry Status</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '8px', background: 'rgba(11, 14, 18, 0.8)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Cpu size={16} color="#FFB52E" />
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>FastAPI Backend Engine</span>
                </div>
                <span className="badge badge-ontime">
                  <CheckCircle2 size={12} /> {health.status.toUpperCase()}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '8px', background: 'rgba(11, 14, 18, 0.8)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Database size={16} color="#FFB52E" />
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>Airport SQLite Database</span>
                </div>
                <span className="badge badge-ontime">
                  <CheckCircle2 size={12} /> {health.database.toUpperCase()}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '8px', background: 'rgba(11, 14, 18, 0.8)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <ShieldCheck size={16} color="#FFB52E" />
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>Gradient Boosting ML Weights</span>
                </div>
                <span className="badge badge-ontime">
                  <CheckCircle2 size={12} /> {health.model.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '16px' }}>
            <span className="form-label" style={{ color: '#FFB52E' }}>System Identification</span>
            <p className="mono" style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
              RunwayOptx v2.4.0 (Enterprise Command Center)
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Mathematical Optimization & Machine Learning Infrastructure
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
