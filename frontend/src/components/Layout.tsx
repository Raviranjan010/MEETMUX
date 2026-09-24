import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';
import { StatusPill } from './StatusPill';
import { fetchHealth, HealthResponse } from '../api/health';
import { Clock } from 'lucide-react';

export const Layout: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    // Update live clock
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + ' UTC');
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Check API health
    fetchHealth()
      .then((data) => setHealth(data))
      .catch(() => {
        setHealth({
          status: 'degraded',
          database: false,
          ml_model_loaded: false,
          optimizer: { gurobi_available: false, ortools_available: false },
        });
      });
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg">
      <Navigation />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Command Bar */}
        <header className="h-16 border-b border-muted/20 bg-surface/80 backdrop-blur px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <span className="text-xs uppercase tracking-wider font-mono text-muted">RunwayOptX v1.0</span>
            <div className="px-2 py-0.5 rounded bg-amber/10 border border-amber/30 text-amber text-[11px] font-mono font-medium">
              SYNTHETIC DEMO DATA
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-mono text-muted bg-surface-elevated px-2.5 py-1 rounded border border-muted/20">
              <Clock className="w-3.5 h-3.5 text-muted" />
              <span>{timeStr || '00:00:00 UTC'}</span>
            </div>

            {health && (
              <div className="flex items-center gap-2">
                <StatusPill
                  label={health.status === 'ok' ? 'API READY' : 'DEGRADED'}
                  status={health.status === 'ok' ? 'ok' : 'warning'}
                  subtext={health.optimizer.ortools_available ? 'OR-Tools' : 'No Solver'}
                />
              </div>
            )}
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-bg">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
