import React from 'react';

export default function RunwayLogo({ size = 'default', showSubtitle = false }) {
  const isSmall = size === 'small';
  const isLarge = size === 'large';

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: isSmall ? '8px' : '12px', userSelect: 'none' }}>
      {/* Aviation Runway Mark + Jet Icon */}
      <div
        style={{
          width: isSmall ? '32px' : isLarge ? '44px' : '38px',
          height: isSmall ? '32px' : isLarge ? '44px' : '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, rgba(255, 181, 46, 0.15) 0%, rgba(255, 159, 28, 0.05) 100%)',
          border: '1px solid rgba(255, 181, 46, 0.35)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(255, 181, 46, 0.2)',
          flexShrink: 0,
          position: 'relative'
        }}
      >
        <svg
          width={isSmall ? "18" : isLarge ? "26" : "22"}
          height={isSmall ? "18" : isLarge ? "26" : "22"}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Runway stripes */}
          <line x1="4" y1="20" x2="8" y2="4" stroke="#FFB52E" strokeWidth="1.5" strokeDasharray="2 2" strokeOpacity="0.4" />
          <line x1="20" y1="20" x2="16" y2="4" stroke="#FFB52E" strokeWidth="1.5" strokeDasharray="2 2" strokeOpacity="0.4" />
          {/* Jet climbing out */}
          <path
            d="M12 3L14.5 9H21L16 13.5L18 20L12 16.5L6 20L8 13.5L3 9H9.5L12 3Z"
            fill="url(#amber-logo-gradient)"
            stroke="#FFB52E"
            strokeWidth="0.75"
            strokeLinejoin="round"
          />
          <defs>
            <linearGradient id="amber-logo-gradient" x1="3" y1="3" x2="21" y2="20" gradientUnits="userSpaceOnUse">
              <stop stopColor="#FFB52E" />
              <stop offset="1" stopColor="#FF9F1C" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{
              fontSize: isSmall ? '1.05rem' : isLarge ? '1.45rem' : '1.25rem',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: '#F5F7FA',
              fontFamily: 'var(--font-sans)',
              lineHeight: 1.1
            }}
          >
            Runway<span style={{ color: '#FFB52E' }}>Optx</span>
          </span>
        </div>
        {showSubtitle && (
          <p
            style={{
              fontSize: '0.6875rem',
              color: 'var(--text-muted)',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              fontWeight: 600,
              marginTop: '2px'
            }}
          >
            Airport Operations Platform
          </p>
        )}
      </div>
    </div>
  );
}
