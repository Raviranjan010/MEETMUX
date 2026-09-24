import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Plane,
  DoorClosed,
  MapPin,
  LineChart,
  Cpu,
  Flame,
  GitFork,
  CalendarDays,
  BarChart3,
  Bell,
  Settings,
  LogOut,
  ShieldCheck,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Flights', path: '/flights', icon: Plane },
  { name: 'Gates', path: '/gates', icon: DoorClosed },
  { name: 'Airport Map', path: '/airport', icon: MapPin },
  { name: 'Predictions', path: '/predictions', icon: LineChart },
  { name: 'Optimizer', path: '/optimizer', icon: Cpu },
  { name: 'Scenarios', path: '/scenarios', icon: Flame },
  { name: 'Cascade', path: '/cascade', icon: GitFork },
  { name: 'Timeline', path: '/timeline', icon: CalendarDays },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Alerts', path: '/alerts', icon: Bell },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Navigation: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('runwayoptx_token');
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-surface border-r border-muted/20 flex flex-col h-screen shrink-0 select-none">
      {/* Brand header */}
      <div className="h-16 px-5 border-b border-muted/20 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-green/10 border border-green/30 flex items-center justify-center text-green font-mono font-bold text-sm">
            RX
          </div>
          <div>
            <div className="font-bold tracking-wider text-sm text-white font-mono">RUNWAYOPTX</div>
            <div className="text-[10px] text-muted tracking-tight">AIRPORT OPS COMMAND</div>
          </div>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-green/15 text-green border border-green/30 font-semibold'
                    : 'text-muted hover:text-white hover:bg-surface-elevated'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Operator status & logout footer */}
      <div className="p-3 border-t border-muted/20 bg-surface">
        <div className="flex items-center justify-between px-2 py-1.5 rounded bg-surface-elevated border border-muted/20 mb-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-green" />
            <span className="text-[11px] font-mono text-muted">operator</span>
          </div>
          <span className="w-1.5 h-1.5 rounded-full bg-green"></span>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs text-muted hover:text-red hover:bg-red/10 rounded transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Exit Session</span>
        </button>
      </div>
    </aside>
  );
};
