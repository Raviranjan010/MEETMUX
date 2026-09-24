import React, { useState, useEffect } from 'react';
import {
  Bell,
  AlertTriangle,
  CheckCircle2,
  RotateCw,
  Info,
  ShieldAlert,
  Clock,
} from 'lucide-react';
import { getAlerts, resolveAlert } from '../api';
import { Alert } from '../api/types';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await getAlerts({
        resolved: false,
        severity: severityFilter || undefined,
      });
      setAlerts(res);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter]);

  const handleResolve = async (id: string) => {
    setResolvingId(id);
    try {
      await resolveAlert(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error('Failed to resolve alert', err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            OPERATIONAL ALERTS & NOTIFICATIONS
          </h1>
          <p className="text-muted text-[11px] mt-0.5">
            Real-time feed of gate overlaps, high delay predictions, and airside disruption events
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-2.5 py-1.5 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="WARNING">Warnings</option>
            <option value="INFO">Info</option>
          </select>

          <button
            onClick={fetchAlerts}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-white transition-colors"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-8 text-center text-muted bg-surface rounded">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="p-8 text-center text-muted bg-surface rounded border border-muted/20">
            <CheckCircle2 className="w-8 h-8 text-green mx-auto mb-2 opacity-80" />
            No active unresolved alerts. Airport operations nominal.
          </div>
        ) : (
          alerts.map((a) => {
            const isCrit = a.severity === 'CRITICAL';
            const isWarn = a.severity === 'WARNING';

            return (
              <div
                key={a.id}
                className={`p-4 bg-surface rounded border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors ${
                  isCrit
                    ? 'border-red/40 bg-red/5'
                    : isWarn
                    ? 'border-amber/40 bg-amber/5'
                    : 'border-muted/20'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isCrit
                          ? 'bg-red/20 text-red border border-red/30'
                          : isWarn
                          ? 'bg-amber/20 text-amber border border-amber/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {a.severity}
                    </span>
                    <span className="font-bold text-white text-sm">{a.title}</span>
                  </div>
                  <p className="text-muted text-[11px]">{a.message}</p>
                  <div className="text-[10px] text-muted flex items-center gap-2 pt-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(a.timestamp).toLocaleTimeString()}</span>
                    <span>•</span>
                    <span>Entity: {a.entity_type} ({a.entity_id})</span>
                  </div>
                </div>

                <button
                  onClick={() => handleResolve(a.id)}
                  disabled={resolvingId === a.id}
                  className="px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-white self-start md:self-center transition-colors disabled:opacity-50"
                >
                  {resolvingId === a.id ? 'Resolving...' : 'Acknowledge / Resolve'}
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
