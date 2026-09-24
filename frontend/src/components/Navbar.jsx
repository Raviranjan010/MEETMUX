import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  Menu, 
  Search, 
  Bell, 
  RefreshCw, 
  Clock, 
  X, 
  AlertTriangle, 
  CheckCircle2, 
  Plane, 
  DoorClosed,
  CloudSun
} from 'lucide-react';
import { getHealth } from '../services/api';
import RunwayLogo from './RunwayLogo';

export default function Navbar({ onRefresh, onToggleSidebar, sidebarOpen }) {
  const [time, setTime] = useState(new Date().toUTCString());
  const [health, setHealth] = useState({ status: 'healthy', database: 'connected', model: 'loaded' });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAlertsDropdown, setShowAlertsDropdown] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toUTCString()), 1000);
    getHealth()
      .then((res) => setHealth(res.data))
      .catch(() => setHealth({ status: 'degraded', database: 'error', model: 'error' }));
    return () => clearInterval(timer);
  }, []);

  const handleRefreshClick = async () => {
    setIsRefreshing(true);
    if (onRefresh) await onRefresh();
    setTimeout(() => setIsRefreshing(false), 600);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/flights?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/predictions', label: 'Delay Prediction' },
    { to: '/optimization', label: 'Gate Scheduling' },
    { to: '/flights', label: 'Flights' },
    { to: '/analytics', label: 'Analytics' },
    { to: '/reports', label: 'Reports' },
  ];

  const operationalAlerts = [
    { id: 1, type: 'danger', icon: AlertTriangle, title: 'AI582 predicted to be delayed by 42 minutes', time: '5 min ago', desc: 'Convective weather cell and runway queue buildup at DEL' },
    { id: 2, type: 'warning', icon: DoorClosed, title: 'Gate G14 will be free in 12 mins', time: '12 min ago', desc: 'IndiGo 6E204 boarding completed ahead of schedule' },
    { id: 3, type: 'warning', icon: AlertTriangle, title: 'High congestion at Terminal 2', time: '18 min ago', desc: 'T2 taxi-in queue exceeding nominal operational threshold by 18%' },
    { id: 4, type: 'info', icon: CloudSun, title: 'Weather change detected (DEL)', time: '25 min ago', desc: 'Surface wind shifted to 14 kts from 090°, runway 09L active' },
  ];

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 28px',
        background: 'rgba(7, 9, 12, 0.92)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        gap: '16px'
      }}
    >
      {/* Left: Hamburger and Nav Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
        <button
          onClick={onToggleSidebar}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            color: 'var(--text-secondary)',
            padding: '7px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
          title={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
        >
          <Menu size={18} />
        </button>

        {/* Brand logo shown when sidebar is collapsed or on smaller screens */}
        <div className="navbar-brand-mobile" style={{ display: !sidebarOpen ? 'block' : 'none' }}>
          <RunwayLogo size="small" />
        </div>

        {/* Top Navigation Bar Pills (matching reference mockup) */}
        <nav
          className="top-nav-pills"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(17, 21, 26, 0.7)',
            padding: '4px',
            borderRadius: 'var(--radius-pill)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-pill)',
                  textDecoration: 'none',
                  fontSize: '0.8125rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#07090C' : 'var(--text-secondary)',
                  background: isActive ? 'linear-gradient(135deg, #FFB52E 0%, #FF9F1C 100%)' : 'transparent',
                  boxShadow: isActive ? '0 2px 10px rgba(255, 181, 46, 0.35)' : 'none',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap'
                }}
              >
                {isActive && <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#07090C' }} />}
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Right: Search, Alerts, Clock, Sync & User Avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', position: 'relative' }}>
        {/* Search input bar */}
        <form onSubmit={handleSearchSubmit} style={{ position: 'relative' }} className="nav-search-form">
          <Search
            size={14}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)'
            }}
          />
          <input
            type="text"
            placeholder="Search flight, gate, airport..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              background: 'rgba(17, 21, 26, 0.9)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-pill)',
              padding: '7px 14px 7px 34px',
              fontSize: '0.8125rem',
              color: 'var(--text-primary)',
              width: '240px',
              outline: 'none',
              transition: 'all 0.2s ease'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#FFB52E';
              e.target.style.width = '280px';
              e.target.style.boxShadow = '0 0 12px rgba(255, 181, 46, 0.2)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border-subtle)';
              e.target.style.width = '240px';
              e.target.style.boxShadow = 'none';
            }}
          />
        </form>

        {/* Sync Operations Button */}
        <button
          onClick={handleRefreshClick}
          className="btn btn-secondary"
          style={{
            padding: '6px 12px',
            fontSize: '0.75rem',
            borderRadius: 'var(--radius-pill)',
            border: '1px solid var(--border-subtle)'
          }}
          title="Sync real-time telemetry from airport database"
        >
          <RefreshCw size={13} className={isRefreshing ? 'spin-animation' : ''} color="#FFB52E" />
          <span style={{ color: 'var(--text-secondary)' }}>Sync</span>
        </button>

        {/* UTC Clock */}
        <div
          className="nav-clock"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: 'var(--text-secondary)',
            fontSize: '0.75rem',
            fontFamily: 'var(--font-mono)',
            background: 'rgba(17, 21, 26, 0.6)',
            padding: '6px 10px',
            borderRadius: 'var(--radius-pill)',
            border: '1px solid var(--border-subtle)'
          }}
        >
          <Clock size={13} color="#FFB52E" />
          <span>{time.replace('GMT', 'UTC').split(' ').slice(4, 5).join(' ')} UTC</span>
        </div>

        {/* Notification Bell with Badge */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowAlertsDropdown(!showAlertsDropdown)}
            style={{
              position: 'relative',
              background: showAlertsDropdown ? 'rgba(255, 181, 46, 0.15)' : 'rgba(17, 21, 26, 0.8)',
              border: `1px solid ${showAlertsDropdown ? '#FFB52E' : 'var(--border-subtle)'}`,
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: showAlertsDropdown ? '#FFB52E' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            title="Operational Alerts"
          >
            <Bell size={16} />
            <span
              style={{
                position: 'absolute',
                top: '-2px',
                right: '-2px',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: '#FF4D4D',
                color: '#FFFFFF',
                fontSize: '0.625rem',
                fontWeight: 800,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 8px rgba(255, 77, 77, 0.6)'
              }}
            >
              1
            </span>
          </button>

          {/* Alerts Dropdown Drawer */}
          {showAlertsDropdown && (
            <div
              className="glass-card animate-slide-up"
              style={{
                position: 'absolute',
                top: '48px',
                right: 0,
                width: '360px',
                padding: '16px',
                zIndex: 200,
                background: 'rgba(11, 14, 18, 0.98)',
                border: '1px solid rgba(255, 181, 46, 0.3)',
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.9), 0 0 20px rgba(255, 181, 46, 0.15)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Bell size={16} color="#FFB52E" />
                  <h4 style={{ fontSize: '0.9375rem', fontWeight: 800 }}>Live Airport Alerts</h4>
                </div>
                <button
                  onClick={() => setShowAlertsDropdown(false)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                >
                  <X size={16} />
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {operationalAlerts.map((alert) => {
                  const Icon = alert.icon;
                  const isRed = alert.type === 'danger';
                  const isYellow = alert.type === 'warning';
                  return (
                    <div
                      key={alert.id}
                      style={{
                        padding: '10px 12px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'rgba(17, 21, 26, 0.8)',
                        borderLeft: `3px solid ${isRed ? '#FF4D4D' : isYellow ? '#FFC857' : '#FFB52E'}`,
                        borderTop: '1px solid var(--border-subtle)',
                        borderRight: '1px solid var(--border-subtle)',
                        borderBottom: '1px solid var(--border-subtle)',
                        fontSize: '0.75rem'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{alert.title}</span>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.6875rem' }}>{alert.time}</span>
                      </div>
                      <p style={{ color: 'var(--text-secondary)', lineHeight: 1.35 }}>{alert.desc}</p>
                    </div>
                  );
                })}
              </div>

              <button
                className="btn btn-secondary"
                style={{ width: '100%', marginTop: '12px', padding: '6px', fontSize: '0.75rem' }}
                onClick={() => {
                  setShowAlertsDropdown(false);
                  navigate('/flights');
                }}
              >
                Inspect Flight Schedule & Queues
              </button>
            </div>
          )}
        </div>

        {/* User Avatar (R for Ravi/RunwayOptx) */}
        <div
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #1C2430 0%, #11151A 100%)',
            border: '2px solid rgba(255, 181, 46, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.875rem',
            fontWeight: 800,
            color: '#FFB52E',
            boxShadow: '0 0 12px rgba(255, 181, 46, 0.25)',
            userSelect: 'none'
          }}
          title="RunwayOptx Command Controller"
        >
          R
        </div>
      </div>
    </header>
  );
}
