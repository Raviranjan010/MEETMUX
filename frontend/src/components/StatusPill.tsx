import React from 'react';

interface StatusPillProps {
  label: string;
  status: 'ok' | 'warning' | 'error' | 'neutral';
  subtext?: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({ label, status, subtext }) => {
  const getColors = () => {
    switch (status) {
      case 'ok':
        return 'bg-green/10 text-green border-green/30';
      case 'warning':
        return 'bg-amber/10 text-amber border-amber/30';
      case 'error':
        return 'bg-red/10 text-red border-red/30';
      default:
        return 'bg-muted-dark text-muted border-muted/30';
    }
  };

  const getDotColor = () => {
    switch (status) {
      case 'ok':
        return 'bg-green';
      case 'warning':
        return 'bg-amber';
      case 'error':
        return 'bg-red';
      default:
        return 'bg-muted';
    }
  };

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-medium border ${getColors()}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${getDotColor()}`}></span>
      <span>{label}</span>
      {subtext && <span className="opacity-70 text-[10px]">({subtext})</span>}
    </div>
  );
};
