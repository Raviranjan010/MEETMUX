import React, { useEffect, useState } from 'react';
import { StatusPill } from '../components/StatusPill';
import { Layers } from 'lucide-react';

interface GenericModulePageProps {
  title: string;
  subtitle: string;
  phaseRequired: string;
  endpointDescription: string;
}

export const GenericModulePage: React.FC<GenericModulePageProps> = ({
  title,
  subtitle,
  phaseRequired,
  endpointDescription,
}) => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 200);
    return () => clearTimeout(t);
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 w-48 bg-surface rounded"></div>
        <div className="h-64 bg-surface rounded border border-muted/20"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">{title}</h1>
          <p className="text-xs text-muted">{subtitle}</p>
        </div>
        <StatusPill label={phaseRequired} status="neutral" />
      </div>

      <div className="p-8 bg-surface border border-muted/20 rounded flex flex-col items-center justify-center text-center max-w-2xl mx-auto my-8">
        <div className="w-12 h-12 rounded bg-surface-elevated border border-muted/30 flex items-center justify-center text-muted mb-4">
          <Layers className="w-6 h-6 text-green" />
        </div>
        <h2 className="text-base font-bold font-mono text-white mb-2">Module Initialized (Phase 1 Foundation)</h2>
        <p className="text-xs text-muted max-w-md mb-6">
          This route is registered in navigation and wired to the application router. Full operational business logic will be attached in <span className="text-white font-mono">{phaseRequired}</span>.
        </p>
        <div className="p-3 bg-surface-elevated border border-muted/20 rounded text-left w-full text-xs font-mono text-muted">
          <div className="text-green mb-1">// API Interface:</div>
          <div>{endpointDescription}</div>
        </div>
      </div>
    </div>
  );
};
