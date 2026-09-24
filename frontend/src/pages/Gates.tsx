import React, { useState, useEffect } from 'react';
import {
  DoorClosed,
  Plane,
  AlertTriangle,
  RotateCw,
  CheckCircle2,
  SlidersHorizontal,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { getGates, detectConflicts } from '../api';
import { Gate, Conflict } from '../api/types';

export const Gates: React.FC = () => {
  const [gates, setGates] = useState<Gate[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [terminalFilter, setTerminalFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [selectedGate, setSelectedGate] = useState<Gate | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [gRes, cRes] = await Promise.all([
        getGates({
          terminal: terminalFilter || undefined,
          status: statusFilter || undefined,
          gate_type: typeFilter || undefined,
        }),
        detectConflicts().catch(() => ({ conflicts: [], count: 0 })),
      ]);
      setGates(gRes);
      setConflicts(cRes.conflicts || []);
    } catch (err) {
      console.error('Failed to load gate data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [terminalFilter, statusFilter, typeFilter]);

  const gateConflictsMap = new Map<string, Conflict[]>();
  conflicts.forEach((c) => {
    const list = gateConflictsMap.get(c.gate_id) || [];
    list.push(c);
    gateConflictsMap.set(c.gate_id, list);
  });

  const availableCount = gates.filter((g) => g.status === 'AVAILABLE').length;
  const occupiedCount = gates.filter((g) => g.status === 'OCCUPIED').length;
  const conflictCount = gates.filter((g) => g.status === 'CONFLICT' || (gateConflictsMap.get(g.id)?.length || 0) > 0).length;
  const blockedCount = gates.filter((g) => g.status === 'BLOCKED').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            GATE INVENTORY & OCCUPANCY
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            30 contact and remote stands across Terminals 1 & 2 • Aircraft Compatibility & Buffers
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white self-start md:self-auto"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>Refresh Gates</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono">
        <div className="p-3 bg-surface rounded border border-muted/20">
          <div className="text-[10px] text-muted">TOTAL GATES</div>
          <div className="text-2xl font-bold text-white mt-1">{gates.length}</div>
        </div>
        <div className="p-3 bg-surface rounded border border-green/30">
          <div className="text-[10px] text-green">AVAILABLE</div>
          <div className="text-2xl font-bold text-green mt-1">{availableCount}</div>
        </div>
        <div className="p-3 bg-surface rounded border border-amber/30">
          <div className="text-[10px] text-amber">OCCUPIED / RESERVED</div>
          <div className="text-2xl font-bold text-amber mt-1">{occupiedCount}</div>
        </div>
        <div className="p-3 bg-surface rounded border border-red/30">
          <div className="text-[10px] text-red">CONFLICTS / BLOCKED</div>
          <div className="text-2xl font-bold text-red mt-1">{conflictCount + blockedCount}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="p-3 bg-surface rounded border border-muted/20 flex flex-wrap items-center gap-4 font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="text-muted text-[11px]">Terminal:</span>
          <select
            value={terminalFilter}
            onChange={(e) => setTerminalFilter(e.target.value)}
            className="px-2.5 py-1 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none"
          >
            <option value="">All Terminals</option>
            <option value="T1">Terminal 1 (Domestic)</option>
            <option value="T2">Terminal 2 (International/Swing)</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-muted text-[11px]">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">Available</option>
            <option value="OCCUPIED">Occupied</option>
            <option value="CONFLICT">Conflict</option>
            <option value="BLOCKED">Blocked</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-muted text-[11px]">Gate Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-2.5 py-1 bg-surface-elevated border border-muted/30 rounded text-white focus:outline-none"
          >
            <option value="">All Types</option>
            <option value="DOMESTIC">Domestic Only</option>
            <option value="INTERNATIONAL">International Only</option>
            <option value="SWING">Swing (Both)</option>
          </select>
        </div>
      </div>

      {/* Gate Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 font-mono text-xs">
        {loading ? (
          <div className="col-span-full p-8 text-center text-muted bg-surface rounded">
            Loading gate telemetry...
          </div>
        ) : (
          gates.map((g) => {
            const hasConflict = (gateConflictsMap.get(g.id)?.length || 0) > 0;
            let statusColor = 'text-green border-green/30 bg-green/10';
            if (g.status === 'OCCUPIED') statusColor = 'text-amber border-amber/30 bg-amber/10';
            if (g.status === 'BLOCKED') statusColor = 'text-muted border-muted bg-muted-dark';
            if (hasConflict || g.status === 'CONFLICT')
              statusColor = 'text-red border-red/50 bg-red/20 animate-pulse';

            return (
              <div
                key={g.id}
                onClick={() => setSelectedGate(g)}
                className={`p-3.5 bg-surface hover:bg-surface-elevated rounded border transition-all cursor-pointer flex flex-col justify-between ${
                  hasConflict ? 'border-red/50' : 'border-muted/20'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1.5">
                      <DoorClosed className="w-4 h-4 text-muted" />
                      <span className="text-sm font-bold text-white">GATE {g.gate_number}</span>
                    </div>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${statusColor}`}>
                      {hasConflict ? 'CONFLICT' : g.status}
                    </span>
                  </div>

                  <div className="space-y-1 text-[11px] text-muted">
                    <div className="flex justify-between">
                      <span>Terminal:</span>
                      <span className="text-white font-semibold">{g.terminal}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Eligibility:</span>
                      <span className="text-white">{g.gate_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Max Aircraft:</span>
                      <span className="text-white">{g.max_aircraft_size}</span>
                    </div>
                  </div>
                </div>

                {hasConflict && (
                  <div className="mt-2 pt-2 border-t border-red/30 text-[10px] text-red flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3 shrink-0" />
                    <span>Double-booked overlap!</span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Gate Detail Drawer / Modal */}
      {selectedGate && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-surface border border-muted/30 rounded-lg max-w-lg w-full p-6 font-mono text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-muted/20 pb-3">
              <div className="flex items-center gap-2">
                <DoorClosed className="w-5 h-5 text-green" />
                <h2 className="text-base font-bold text-white">
                  GATE {selectedGate.gate_number} ({selectedGate.terminal})
                </h2>
              </div>
              <button
                onClick={() => setSelectedGate(null)}
                className="px-2 py-1 bg-surface-elevated hover:bg-muted-dark rounded text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2">
              <div className="p-3 bg-surface-elevated rounded border border-muted/20 flex justify-between">
                <span className="text-muted">Current Operational Status:</span>
                <span className="font-bold text-white">{selectedGate.status}</span>
              </div>
              <div className="p-3 bg-surface-elevated rounded border border-muted/20 flex justify-between">
                <span className="text-muted">Route Eligibility:</span>
                <span className="font-bold text-white">{selectedGate.gate_type}</span>
              </div>
              <div className="p-3 bg-surface-elevated rounded border border-muted/20 flex justify-between">
                <span className="text-muted">Maximum Wingspan / Size:</span>
                <span className="font-bold text-white">{selectedGate.max_aircraft_size}</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedGate(null)}
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
