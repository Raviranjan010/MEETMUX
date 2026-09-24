import React from 'react';

export default function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  color = '#FFB52E', 
  trend,
  trendType = 'up', // 'up' or 'down'
  trendPositive = true, // if true, green; if false, red
  sparklineData = [12, 18, 15, 22, 28, 24, 30, 38, 35, 44]
}) {
  const isGoodTrend = trendPositive;
  const trendBg = isGoodTrend ? 'rgba(25, 216, 138, 0.14)' : 'rgba(255, 77, 77, 0.14)';
  const trendBorder = isGoodTrend ? 'rgba(25, 216, 138, 0.35)' : 'rgba(255, 77, 77, 0.35)';
  const trendColor = isGoodTrend ? '#19D88A' : '#FF4D4D';

  const maxVal = Math.max(...sparklineData, 1);

  return (
    <div
      className="glass-card glass-card-interactive"
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '20px',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background radial glow */}
      <div
        style={{
          position: 'absolute',
          top: '-30px',
          right: '-30px',
          width: '100px',
          height: '100px',
          borderRadius: '50%',
          background: color,
          opacity: 0.08,
          filter: 'blur(30px)',
          pointerEvents: 'none'
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {Icon && (
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '12px',
                background: `linear-gradient(135deg, ${color}22 0%, ${color}08 100%)`,
                border: `1px solid ${color}44`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: color,
                boxShadow: `0 0 14px ${color}22`
              }}
            >
              <Icon size={20} color={color} />
            </div>
          )}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '1.75rem',
                  fontWeight: 800,
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '-0.02em',
                  lineHeight: 1
                }}
              >
                {value}
              </span>
              {trend && (
                <span
                  style={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-pill)',
                    background: trendBg,
                    border: `1px solid ${trendBorder}`,
                    color: trendColor,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '2px'
                  }}
                >
                  {trendType === 'up' ? '↑' : '↓'} {trend}
                </span>
              )}
            </div>
            <p
              style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginTop: '4px'
              }}
            >
              {title}
            </p>
          </div>
        </div>

        {/* Mini SVG Sparkline bar chart */}
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '32px', width: '56px' }}>
          {sparklineData.map((val, idx) => {
            const heightPercent = Math.max(15, (val / maxVal) * 100);
            return (
              <div
                key={idx}
                style={{
                  flex: 1,
                  height: `${heightPercent}%`,
                  borderRadius: '1.5px',
                  background: color,
                  opacity: 0.3 + (idx / sparklineData.length) * 0.7,
                  transition: 'height 0.3s ease'
                }}
              />
            );
          })}
        </div>
      </div>

      {subtitle && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
}
