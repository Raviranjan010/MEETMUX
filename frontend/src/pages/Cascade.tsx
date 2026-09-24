import React, { useState, useEffect } from 'react';
import {
  GitFork,
  AlertTriangle,
  RotateCw,
  Plane,
  DoorClosed,
  Clock,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { getCascadeAnalysis } from '../api';
import { CascadeTree, CascadeNode } from '../api/types';

export const Cascade: React.FC = () => {
  const [trees, setTrees] = useState<CascadeTree[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedNode, setSelectedNode] = useState<CascadeNode | null>(null);

  const fetchCascade = async () => {
    setLoading(true);
    try {
      const res = await getCascadeAnalysis();
      setTrees(res);
      if (res.length > 0 && res[0].nodes.length > 0) {
        setSelectedNode(res[0].nodes[0]);
      }
    } catch (err) {
      console.error('Failed to fetch cascade data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCascade();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-muted/20 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            CASCADE DELAY PROPAGATION GRAPH
          </h1>
          <p className="text-xs text-muted font-mono mt-0.5">
            Graph BFS Traversal • Tracing downstream domino delay ripple effects through turnaround buffers
          </p>
        </div>

        <button
          onClick={fetchCascade}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-elevated hover:bg-muted-dark border border-muted/30 rounded text-xs font-mono transition-colors text-white"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>Refresh Cascade</span>
        </button>
      </div>

      {/* Main Cascade Visualization & Node Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono text-xs">
        {/* Cascade Propagation Chains (2 cols) */}
        <div className="lg:col-span-2 bg-surface rounded border border-muted/20 p-5 space-y-6">
          <div className="flex items-center justify-between border-b border-muted/20 pb-3">
            <div className="flex items-center gap-2">
              <GitFork className="w-4 h-4 text-amber" />
              <h2 className="font-bold text-white uppercase">Active Propagation Trees</h2>
            </div>
            <span className="text-[11px] text-muted">{trees.length} Distinct Root Causes Detected</span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-muted">Calculating graph traversal...</div>
          ) : trees.length === 0 ? (
            <div className="p-8 text-center text-muted">No cascade chains currently propagating.</div>
          ) : (
            trees.map((tree, tIdx) => (
              <div key={tIdx} className="p-4 bg-surface-elevated rounded border border-muted/20 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red animate-ping"></span>
                    <span className="font-bold text-white text-sm">Root: Flight {tree.root_flight_id}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-red/20 text-red border border-red/30 rounded text-[10px] font-bold">
                    {tree.total_affected_flights} DOWNSTREAM FLIGHTS AFFECTED
                  </span>
                </div>

                <div className="text-[11px] text-muted">
                  Root Cause: <span className="text-white font-semibold">{tree.root_cause}</span>
                </div>

                {/* Visual Step-by-Step Node Chain */}
                <div className="space-y-3 pt-2">
                  {tree.nodes.map((node, nIdx) => (
                    <div
                      key={nIdx}
                      onClick={() => setSelectedNode(node)}
                      className={`p-3 rounded border transition-all cursor-pointer flex items-center justify-between ${
                        selectedNode?.flight_id === node.flight_id
                          ? 'bg-surface border-green text-white'
                          : 'bg-surface/50 border-muted/20 hover:border-muted/40 text-muted'
                      }`}
                      style={{ marginLeft: `${node.depth * 20}px` }}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1 font-bold text-white">
                          <Plane className="w-3.5 h-3.5 text-muted" />
                          <span>{node.flight_number || node.flight_id}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[11px] text-muted">
                          <DoorClosed className="w-3 h-3 text-muted" />
                          <span>Gate {node.gate_id}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-amber font-bold">+{node.delay_minutes}m delay</span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            node.risk_level === 'HIGH' ? 'bg-red/20 text-red' : 'bg-amber/20 text-amber'
                          }`}
                        >
                          Hop {node.depth}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Selected Cascade Node Detail */}
        <div className="bg-surface rounded border border-muted/20 p-5 font-mono text-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-muted/20 pb-3 mb-4">
              <ShieldAlert className="w-4 h-4 text-red" />
              <h2 className="font-bold text-white uppercase">Propagation Telemetry</h2>
            </div>

            {selectedNode ? (
              <div className="space-y-3">
                <div className="p-3 bg-surface-elevated rounded border border-muted/20">
                  <div className="text-[10px] text-muted">AFFECTED FLIGHT</div>
                  <div className="text-base font-bold text-white mt-1">
                    {selectedNode.flight_number || selectedNode.flight_id}
                  </div>
                  <div className="text-[11px] text-amber mt-0.5">
                    Accumulated Delay: +{selectedNode.delay_minutes} min
                  </div>
                </div>

                <div className="space-y-2 text-[11px]">
                  <div className="flex justify-between py-1 border-b border-muted/10">
                    <span className="text-muted">Assigned Stand:</span>
                    <span className="text-white font-semibold">Gate {selectedNode.gate_id}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-muted/10">
                    <span className="text-muted">Graph Depth:</span>
                    <span className="text-white font-semibold">{selectedNode.depth} hops from root</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-muted/10">
                    <span className="text-muted">Propagated From:</span>
                    <span className="text-white font-semibold">{selectedNode.propagated_from || 'Direct Root'}</span>
                  </div>
                </div>

                <div className="p-3 bg-red/10 border border-red/30 rounded text-red text-[11px]">
                  <div className="font-bold mb-1">Operational Impact:</div>
                  <div>
                    Turnaround buffer compressed below 45 min threshold. High risk of outbound gate hold.
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-muted">
                Select an affected flight node from the tree to inspect propagation metrics.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
