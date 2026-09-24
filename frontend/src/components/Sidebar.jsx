import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Sparkles, 
  Split, 
  Plane, 
  BarChart3, 
  FileText, 
  MapPin, 
  Settings as SettingsIcon,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import RunwayLogo from './RunwayLogo';

export default function Sidebar({ isOpen = true, onCloseMobile }) {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/predictions', label: 'Delay Prediction', icon: Sparkles },
    { to: '/optimization', label: 'Gate Scheduling', icon: Split },
    { to: '/flights', label: 'Flights', icon: Plane },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/reports', label: 'Reports', icon: FileText },
    { to: '/map', label: 'Airport Map', icon: MapPin },
    { to: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside
      style={{
        width: '260px',
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '20px 14px',
        flexShrink: 0,
        height: '100vh',
        zIndex: 50,
        transition: 'transform 0.25s ease',
        transform: isOpen ? 'translateX(0)' : 'translateX(-100%)',
      }}
    >
      <div>
        {/* Brand Logo Header */}
        <div style={{ padding: '0 8px 18px', borderBottom: '1px solid var(--border-subtle)', marginBottom: '16px' }}>
          <RunwayLogo size="default" showSubtitle={true} />
        </div>

        {/* Navigation Section */}
        <div style={{ padding: '0 8px 8px' }}>
          <p style={{ 
            fontSize: '0.6875rem', 
            fontWeight: 700, 
            color: 'var(--text-muted)', 
            textTransform: 'uppercase', 
            letterSpacing: '0.08em',
            marginBottom: '8px'
          }}>
            Operations Navigation
          </p>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  textDecoration: 'none',
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#FFB52E' : 'var(--text-secondary)',
                  background: isActive ? 'linear-gradient(90deg, rgba(255, 181, 46, 0.14) 0%, rgba(255, 181, 46, 0.04) 100%)' : 'transparent',
                  border: isActive ? '1px solid rgba(255, 181, 46, 0.28)' : '1px solid transparent',
                  boxShadow: isActive ? '0 0 16px rgba(255, 181, 46, 0.1)' : 'none',
                  transition: 'all 0.15s ease'
                })}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Icon size={18} color="currentColor" />
                  <span>{item.label}</span>
                </div>
                <ChevronRight size={14} style={{ opacity: 0.4 }} />
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Operations Inspiration Banner Card */}
      <div
        style={{
          position: 'relative',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid rgba(255, 181, 46, 0.2)',
          boxShadow: '0 4px 18px rgba(0, 0, 0, 0.6)',
          height: '160px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          padding: '14px',
          background: '#0B0E12'
        }}
      >
        <img
          src="/images/sidebar-quote.jpg"
          alt="RunwayOptx Control Tower"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.65,
            filter: 'contrast(1.1) brightness(0.85)'
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(to top, rgba(7, 9, 12, 0.95) 0%, rgba(7, 9, 12, 0.4) 60%, transparent 100%)'
          }}
        />

        <div style={{ position: 'relative', zIndex: 2 }}>
          <p
            style={{
              fontSize: '0.8125rem',
              fontWeight: 700,
              color: '#FFB52E',
              lineHeight: 1.35,
              fontStyle: 'italic',
              textShadow: '0 2px 8px rgba(0,0,0,0.8)',
              marginBottom: '6px'
            }}
          >
            "Optimizing Today for Smoother Tomorrows"
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.6875rem', color: 'var(--text-secondary)' }}>
            <span className="live-pulse-dot" style={{ width: '6px', height: '6px' }} />
            <span>MILP & ML Fleet Engines Active</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
