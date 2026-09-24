import React from 'react';
import { Plane } from 'lucide-react';

export default function LoadingSpinner({ text = 'Querying airport operations telemetry...' }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '64px 20px',
        width: '100%'
      }}
    >
      <div style={{ position: 'relative', width: '56px', height: '56px', marginBottom: '20px' }}>
        {/* Radar sweep circle */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '50%',
            border: '2px solid rgba(255, 181, 46, 0.2)',
            borderTopColor: '#FFB52E',
            borderRightColor: '#FF9F1C',
            animation: 'spin 1s linear infinite'
          }}
        />
        {/* Inner center plane */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Plane size={20} color="#FFB52E" />
        </div>
      </div>
      <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
        {text}
      </p>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
        RunwayOptx Real-Time Inference & Solver Bridge
      </p>
    </div>
  );
}
