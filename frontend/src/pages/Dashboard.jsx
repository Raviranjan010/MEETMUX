import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboardSummary } from '../services/api';
import StatCard from '../components/StatCard';
import GateMap from '../components/GateMap';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Plane, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  DoorClosed, 
  Cpu, 
  TrendingUp,
  CloudSun,
  Play,
  ArrowRight,
  ShieldCheck,
  Activity,
  Layers,
  Sparkles,
  Users,
  ChevronRight,
  X
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
  AreaChart,
  Area
} from 'recharts';

import { DEFAULT_DASHBOARD_DATA } from '../utils/mockData';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [showDemoModal, setShowDemoModal] = useState(false);
  const navigate = useNavigate();

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const res = await getDashboardSummary();
      if (res?.data && res.data.kpis) {
        setData(res.data);
        setIsDemoMode(false);
      } else {
        setData(DEFAULT_DASHBOARD_DATA);
        setIsDemoMode(true);
      }
    } catch (err) {
      console.warn('Backend telemetry unavailable, using operational demo snapshot:', err);
      setData(DEFAULT_DASHBOARD_DATA);
      setIsDemoMode(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading && !data) {
    return <LoadingSpinner text="Aggregating airport operations telemetry and MILP outputs..." />;
  }

  const activeData = data || DEFAULT_DASHBOARD_DATA;
  const { 
    kpis, 
    delay_distribution, 
    delay_by_airline, 
    congestion_by_hour, 
    gate_occupancy, 
    weather_impact, 
    predicted_vs_actual 
  } = activeData;

  const onTimeFlights = Math.max(0, kpis.total_flights - kpis.delayed_flights);
  const onTimePercentage = kpis.total_flights > 0 
    ? Math.round((onTimeFlights / kpis.total_flights) * 100) 
    : 94;

  // Custom colors for delay categories in aviation theme
  const getCategoryThemeColor = (cat) => {
    switch (cat) {
      case 'On Time': return '#19D88A';
      case 'Low': return '#FFC857';
      case 'Moderate': return '#FF9F1C';
      case 'High': return '#FF4D4D';
      case 'Severe': return '#FF3333';
      default: return '#FFB52E';
    }
  };

  const formattedDelayDistribution = (delay_distribution || []).map(item => ({
    ...item,
    color: getCategoryThemeColor(item.category)
  }));

  // Sample recent scheduled flights for compact table derived from real occupancy
  const recentAssignments = (gate_occupancy || []).slice(0, 5).map((occ, idx) => ({
    flight: occ.flight_number,
    aircraft: occ.flight_number.startsWith('AI') ? 'A320' : occ.flight_number.startsWith('6E') ? 'A321' : 'B737',
    scheduled: new Date(occ.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
    gate: occ.gate_number,
    status: occ.delay_minutes > 20 ? 'Delayed' : occ.delay_minutes > 10 ? 'Boarding' : 'On Time'
  }));

  // Fallback if occupancy is empty before first run
  const displayAssignments = recentAssignments.length > 0 ? recentAssignments : [
    { flight: 'AI501', aircraft: 'A320', scheduled: '10:00', gate: 'G12', status: 'On Time' },
    { flight: '6E204', aircraft: 'A321', scheduled: '10:20', gate: 'G14', status: 'Delayed' },
    { flight: 'SG612', aircraft: 'B737', scheduled: '10:45', gate: 'G15', status: 'Boarding' },
    { flight: 'UK953', aircraft: 'A320', scheduled: '11:10', gate: 'G11', status: 'On Time' },
    { flight: 'AI782', aircraft: 'B787', scheduled: '11:40', gate: 'G16', status: 'On Time' },
  ];

  return (
    <div className="page-container">
      {isDemoMode && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 18px',
            marginBottom: '16px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(255, 181, 46, 0.1)',
            border: '1px solid rgba(255, 181, 46, 0.3)',
            color: '#FFB52E',
            fontSize: '0.8125rem',
            flexWrap: 'wrap',
            gap: '10px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={16} />
            <span>
              <strong>Operational Snapshot Mode:</strong> Live backend server is booting or unconfigured. Displaying cached airport telemetry.
            </span>
          </div>
          <button
            onClick={fetchSummary}
            className="btn btn-secondary"
            style={{
              padding: '4px 12px',
              fontSize: '0.75rem',
              height: 'auto',
              background: 'rgba(255, 181, 46, 0.2)',
              borderColor: '#FFB52E',
              color: '#FFB52E'
            }}
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* ========================================================
          HERO BANNER SECTION (MATCHING RUNWAYOPTX REFERENCE MOCKUP)
          ======================================================== */}
      <div
        style={{
          position: 'relative',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          marginBottom: '24px',
          boxShadow: '0 12px 36px rgba(0, 0, 0, 0.75)',
          border: '1px solid rgba(255, 181, 46, 0.25)',
          minHeight: '340px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          background: '#07090C'
        }}
      >
        {/* Background Airport Apron Sunset Image */}
        <img
          src="/images/hero-airport.jpg"
          alt="RunwayOptx Airport Apron Operations"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.75,
            filter: 'contrast(1.15) brightness(0.85)'
          }}
        />

        {/* Ambient Dark Gradient Overlays for High-Contrast Readability */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(90deg, rgba(7, 9, 12, 0.94) 0%, rgba(7, 9, 12, 0.78) 45%, rgba(7, 9, 12, 0.4) 100%)'
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(0deg, rgba(7, 9, 12, 0.85) 0%, transparent 60%)'
          }}
        />

        {/* Top Floating Widgets (Weather & Live Overview) */}
        <div
          style={{
            position: 'relative',
            zIndex: 10,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            padding: '28px 32px 0',
            flexWrap: 'wrap',
            gap: '16px'
          }}
        >
          {/* Tagline Pill */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: 'var(--radius-pill)',
              background: 'rgba(255, 77, 77, 0.16)',
              border: '1px solid rgba(255, 77, 77, 0.4)',
              backdropFilter: 'blur(10px)'
            }}
          >
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#FF4D4D' }} />
            <span
              style={{
                fontSize: '0.6875rem',
                fontWeight: 800,
                color: '#FF6B6B',
                letterSpacing: '0.08em',
                textTransform: 'uppercase'
              }}
            >
              AI-POWERED AIRPORT OPERATIONS
            </span>
          </div>

          {/* Right Top Status (Weather & Live Airport Overview) */}
          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Weather Widget */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(11, 14, 18, 0.82)',
                border: '1px solid var(--border-subtle)',
                backdropFilter: 'blur(12px)',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)'
              }}
            >
              <CloudSun size={18} color="#FFB52E" />
              <div>
                <span style={{ fontSize: '0.875rem', fontWeight: 800, color: '#F5F7FA' }}>28°C</span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginLeft: '6px' }}>Partly Cloudy</span>
              </div>
            </div>

            {/* Live Airport Overview Card */}
            <div
              style={{
                padding: '12px 18px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(11, 14, 18, 0.88)',
                border: '1px solid rgba(255, 181, 46, 0.3)',
                backdropFilter: 'blur(16px)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
                minWidth: '280px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Live Airport Overview
                </span>
                <span className="badge badge-live">
                  <span className="live-pulse-dot" /> Live
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '2px' }}>
                <span style={{ fontSize: '1.125rem', fontWeight: 800, color: '#F5F7FA' }}>DEL → BOM</span>
                <span style={{ fontSize: '0.6875rem', color: '#FFB52E' }}>Indira Gandhi Intl. Airport</span>
              </div>

              {/* 4 Micro Stat Columns */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '8px',
                  paddingTop: '8px',
                  marginTop: '8px',
                  borderTop: '1px solid var(--border-subtle)',
                  textAlign: 'center'
                }}
              >
                <div>
                  <p className="mono" style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FFB52E' }}>
                    {kpis.total_flights}
                  </p>
                  <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Total</span>
                </div>
                <div>
                  <p className="mono" style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#19D88A' }}>
                    {onTimeFlights}
                  </p>
                  <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>On Time</span>
                </div>
                <div>
                  <p className="mono" style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FF4D4D' }}>
                    {kpis.delayed_flights}
                  </p>
                  <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Delayed</span>
                </div>
                <div>
                  <p className="mono" style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--text-secondary)' }}>
                    0
                  </p>
                  <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Canceled</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Hero Title & Primary CTAs */}
        <div
          style={{
            position: 'relative',
            zIndex: 10,
            padding: '24px 32px 32px',
            maxWidth: '680px'
          }}
        >
          <h1
            style={{
              fontSize: '2.5rem',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: '#F5F7FA',
              marginBottom: '8px',
              lineHeight: 1.1
            }}
          >
            Runway<span style={{ color: '#FFB52E' }}>Optx</span>
          </h1>

          <p
            style={{
              fontSize: '1rem',
              fontWeight: 700,
              color: '#FFB52E',
              marginBottom: '8px',
              letterSpacing: '0.01em'
            }}
          >
            Predict Delays &nbsp;|&nbsp; Optimize Gates &nbsp;|&nbsp; Ensure Smoother Skies
          </p>

          <p
            style={{
              fontSize: '0.875rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.5,
              marginBottom: '20px'
            }}
          >
            An intelligent platform for predictive flight delay analysis and optimized gate scheduling,
            helping airports operate smarter, safer, and more efficiently.
          </p>

          {/* Action CTAs */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/predictions')}
              style={{ padding: '11px 22px', fontSize: '0.9375rem' }}
            >
              <span>Get Started</span>
              <ArrowRight size={16} />
            </button>
            <button
              className="btn btn-outline-amber"
              onClick={() => setShowDemoModal(true)}
              style={{ padding: '11px 20px', fontSize: '0.9375rem' }}
            >
              <Play size={16} fill="currentColor" />
              <span>Watch Demo</span>
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================
          KPI STAT CARDS ROW (4 CARDS MATCHING REFERENCE MOCKUP)
          ======================================================== */}
      <div className="kpi-grid">
        <StatCard
          title="Total Flights"
          value={kpis.total_flights}
          subtitle="Monitored in current window"
          icon={Plane}
          color="#FFB52E"
          trend="12%"
          trendType="up"
          trendPositive={true}
          sparklineData={[32, 38, 42, 40, 48, 52, 58, 64, 70, 78]}
        />
        <StatCard
          title="Predicted Delays"
          value={kpis.delayed_flights}
          subtitle={`${kpis.delayed_percentage}% of total operations`}
          icon={Clock}
          color="#FF4D4D"
          trend="25%"
          trendType="up"
          trendPositive={false}
          sparklineData={[14, 20, 18, 25, 30, 28, 35, 42, 38, 46]}
        />
        <StatCard
          title="Active Gates"
          value={`${kpis.gates_utilized}`}
          subtitle={`${kpis.gate_utilization_rate}% nominal capacity utilization`}
          icon={DoorClosed}
          color="#19D88A"
          trend="6%"
          trendType="up"
          trendPositive={true}
          sparklineData={[22, 24, 25, 26, 28, 28, 30, 31, 32, 32]}
        />
        <StatCard
          title="On-Time Performance"
          value={`${onTimePercentage}%`}
          subtitle="Fleet schedule reliability rating"
          icon={Users}
          color="#9B6CFF"
          trend="5%"
          trendType="up"
          trendPositive={true}
          sparklineData={[82, 84, 85, 88, 89, 90, 92, 91, 93, 94]}
        />
      </div>

      {/* ========================================================
          MIDDLE OPERATIONS GRID:
          - Column 1: Interactive Airport Map
          - Column 2: Delay Prediction widget + Gate Scheduling (Optimized) table
          - Column 3: Live Alerts + Optimization Insights
          ======================================================== */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(420px, 1.35fr) minmax(340px, 1fr) minmax(280px, 0.9fr)',
          gap: '20px',
          marginBottom: '24px'
        }}
        className="dashboard-middle-grid"
      >
        {/* Column 1: Interactive Airport Map */}
        <div>
          <GateMap occupancy={gate_occupancy} />
        </div>

        {/* Column 2: Delay Prediction Widget + Gate Scheduling Table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Delay Prediction Card */}
          <div className="glass-card" style={{ padding: '18px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Delay Prediction</h3>
              <button
                onClick={() => navigate('/predictions')}
                style={{ background: 'transparent', border: 'none', color: '#FFB52E', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <span>Full Predictor</span>
                <ChevronRight size={14} />
              </button>
            </div>

            {/* Monitored Sample Flight */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-amber" style={{ padding: '3px 8px' }}>
                  <Plane size={12} /> AI582
                </span>
                <span className="mono" style={{ fontSize: '0.8125rem', fontWeight: 700 }}>DEL → BOM</span>
              </div>
              <span className="badge badge-high" style={{ fontSize: '0.6875rem' }}>
                High Risk
              </span>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Predicted Delay</span>
                <span style={{ fontSize: '0.75rem', color: '#19D88A', fontWeight: 700 }}>78% Confidence</span>
              </div>
              <h4 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FF4D4D', fontFamily: 'var(--font-mono)', lineHeight: 1 }}>
                42 minutes
              </h4>
              
              {/* Progress delay gauge bar */}
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', marginTop: '8px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: '70%', background: 'linear-gradient(90deg, #FFB52E 0%, #FF4D4D 100%)', borderRadius: '3px' }} />
              </div>
            </div>

            {/* Contributing Delay Factors */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              <span style={{ fontSize: '0.6875rem', padding: '3px 8px', borderRadius: 'var(--radius-pill)', background: 'rgba(255, 181, 46, 0.1)', color: '#FFB52E', border: '1px solid rgba(255, 181, 46, 0.2)' }}>
                Weather 32%
              </span>
              <span style={{ fontSize: '0.6875rem', padding: '3px 8px', borderRadius: 'var(--radius-pill)', background: 'rgba(255, 77, 77, 0.1)', color: '#FF4D4D', border: '1px solid rgba(255, 77, 77, 0.2)' }}>
                Congestion 24%
              </span>
              <span style={{ fontSize: '0.6875rem', padding: '3px 8px', borderRadius: 'var(--radius-pill)', background: 'rgba(25, 216, 138, 0.1)', color: '#19D88A', border: '1px solid rgba(25, 216, 138, 0.2)' }}>
                Carrier 18%
              </span>
              <span style={{ fontSize: '0.6875rem', padding: '3px 8px', borderRadius: 'var(--radius-pill)', background: 'rgba(155, 108, 255, 0.1)', color: '#9B6CFF', border: '1px solid rgba(155, 108, 255, 0.2)' }}>
                Historical 16%
              </span>
              <span style={{ fontSize: '0.6875rem', padding: '3px 8px', borderRadius: 'var(--radius-pill)', background: 'rgba(255, 255, 255, 0.06)', color: 'var(--text-muted)' }}>
                Other 10%
              </span>
            </div>
          </div>

          {/* Gate Scheduling (Optimized) Compact Table */}
          <div className="glass-card" style={{ padding: '18px 20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Gate Scheduling (Optimized)</h3>
              <button
                onClick={() => navigate('/optimization')}
                style={{ background: 'transparent', border: 'none', color: '#FFB52E', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <span>View Solver</span>
                <ChevronRight size={14} />
              </button>
            </div>

            <div className="table-container" style={{ flex: 1 }}>
              <table className="custom-table" style={{ fontSize: '0.8125rem' }}>
                <thead>
                  <tr>
                    <th>Flight</th>
                    <th>Aircraft</th>
                    <th>Scheduled</th>
                    <th>Assigned Gate</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {displayAssignments.map((row, idx) => (
                    <tr key={idx}>
                      <td className="mono" style={{ fontWeight: 800, color: '#FFB52E' }}>{row.flight}</td>
                      <td className="mono" style={{ color: 'var(--text-secondary)' }}>{row.aircraft}</td>
                      <td className="mono">{row.scheduled}</td>
                      <td className="mono" style={{ fontWeight: 800, color: '#19D88A' }}>{row.gate}</td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            fontSize: '0.6875rem',
                            padding: '2px 8px',
                            background: row.status === 'Delayed' ? 'rgba(255, 77, 77, 0.15)' : row.status === 'Boarding' ? 'rgba(255, 200, 87, 0.15)' : 'rgba(25, 216, 138, 0.15)',
                            color: row.status === 'Delayed' ? '#FF4D4D' : row.status === 'Boarding' ? '#FFC857' : '#19D88A',
                            border: `1px solid ${row.status === 'Delayed' ? '#FF4D4D44' : row.status === 'Boarding' ? '#FFC85744' : '#19D88A44'}`
                          }}
                        >
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Column 3: Live Alerts + Optimization Insights */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Live Alerts Panel */}
          <div className="glass-card" style={{ padding: '18px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#FF4D4D', boxShadow: '0 0 8px #FF4D4D' }} />
                <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Live Alerts</h3>
              </div>
              <button
                onClick={() => navigate('/flights')}
                style={{ background: 'transparent', border: 'none', color: '#FFB52E', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}
              >
                View All
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ padding: '8px 10px', borderRadius: '8px', background: 'rgba(255, 77, 77, 0.08)', borderLeft: '3px solid #FF4D4D', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 700, color: '#F5F7FA' }}>AI582 predicted delay +42m</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.6875rem' }}>5 min ago</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.6875rem' }}>Runway 09L taxi queue congestion</p>
              </div>

              <div style={{ padding: '8px 10px', borderRadius: '8px', background: 'rgba(255, 200, 87, 0.08)', borderLeft: '3px solid #FFC857', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 700, color: '#F5F7FA' }}>Gate G14 free in 12 mins</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.6875rem' }}>12 min ago</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.6875rem' }}>Ready for inbound assignment</p>
              </div>

              <div style={{ padding: '8px 10px', borderRadius: '8px', background: 'rgba(255, 159, 28, 0.08)', borderLeft: '3px solid #FF9F1C', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 700, color: '#F5F7FA' }}>High congestion at Terminal 2</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.6875rem' }}>18 min ago</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.6875rem' }}>Reallocating narrowbody apron slots</p>
              </div>

              <div style={{ padding: '8px 10px', borderRadius: '8px', background: 'rgba(25, 216, 138, 0.08)', borderLeft: '3px solid #19D88A', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 700, color: '#F5F7FA' }}>Weather change (DEL)</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.6875rem' }}>25 min ago</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.6875rem' }}>Wind 14 kts, clear visibility</p>
              </div>
            </div>
          </div>

          {/* Optimization Insights with 3 Radial Percentage Rings */}
          <div className="glass-card" style={{ padding: '18px 20px', flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Optimization Insights</h3>
              <ChevronRight size={16} color="var(--text-muted)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center' }}>
              {/* Metric 1 */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'conic-gradient(#19D88A 65deg, rgba(255,255,255,0.06) 0deg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '8px',
                    position: 'relative'
                  }}
                >
                  <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#0B0E12', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 800, color: '#19D88A' }}>18%</span>
                  </div>
                </div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', lineHeight: 1.25 }}>
                  Reduction in Gate Conflicts
                </span>
              </div>

              {/* Metric 2 */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'conic-gradient(#FFB52E 97deg, rgba(255,255,255,0.06) 0deg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '8px',
                    position: 'relative'
                  }}
                >
                  <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#0B0E12', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 800, color: '#FFB52E' }}>27%</span>
                  </div>
                </div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', lineHeight: 1.25 }}>
                  Improved Turnaround Time
                </span>
              </div>

              {/* Metric 3 */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'conic-gradient(#9B6CFF 43deg, rgba(255,255,255,0.06) 0deg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '8px',
                    position: 'relative'
                  }}
                >
                  <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#0B0E12', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 800, color: '#9B6CFF' }}>12%</span>
                  </div>
                </div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', lineHeight: 1.25 }}>
                  Higher On-Time Rate
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================
          DEEP TELEMETRY CHARTS SECTION
          ======================================================== */}
      {/* Row 1: Hourly Congestion & Delay Category Pie */}
      <div className="charts-grid-2">
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Hourly Traffic Congestion & Delay</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Arrivals vs Departures vs Average Delay</p>
            </div>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <AreaChart data={congestion_by_hour}>
                <defs>
                  <linearGradient id="colorArrivals" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FFB52E" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#FFB52E" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDepartures" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#9B6CFF" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#9B6CFF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="time_label" stroke="#727E93" fontSize={11} />
                <YAxis stroke="#727E93" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0B0E12', borderColor: 'rgba(255,181,46,0.3)', borderRadius: '8px', color: '#F5F7FA' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Area type="monotone" dataKey="arrivals" stroke="#FFB52E" strokeWidth={2} fillOpacity={1} fill="url(#colorArrivals)" name="Arrivals" />
                <Area type="monotone" dataKey="departures" stroke="#9B6CFF" strokeWidth={2} fillOpacity={1} fill="url(#colorDepartures)" name="Departures" />
                <Line type="monotone" dataKey="avg_delay" stroke="#FF4D4D" strokeWidth={2} name="Avg Delay (m)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Predicted Delay Distribution</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Flight volume categorized by operational impact tier</p>
            </div>
          </div>
          <div style={{ width: '100%', height: 260, display: 'flex', alignItems: 'center' }}>
            <ResponsiveContainer width="55%" height="100%">
              <PieChart>
                <Pie
                  data={formattedDelayDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {formattedDelayDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0B0E12', borderColor: 'rgba(255,181,46,0.3)', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>

            <div style={{ width: '45%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {formattedDelayDistribution.map((item) => (
                <div key={item.category} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '3px', backgroundColor: item.color }}></span>
                    <span style={{ color: 'var(--text-secondary)' }}>{item.category}</span>
                  </div>
                  <span className="mono" style={{ fontWeight: 700 }}>{item.count} ({item.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Carrier Delay Benchmarks & Inference Accuracy */}
      <div className="charts-grid-2">
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '4px' }}>Average Delay by Airline</h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Carrier operational taxi and turnaround performance</p>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer>
              <BarChart data={delay_by_airline}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="airline" stroke="#727E93" fontSize={10} angle={-15} textAnchor="end" height={45} />
                <YAxis stroke="#727E93" fontSize={11} unit="m" />
                <Tooltip contentStyle={{ backgroundColor: '#0B0E12', borderColor: 'rgba(255,181,46,0.3)', borderRadius: '8px' }} />
                <Bar dataKey="avg_delay" fill="#FFB52E" radius={[4, 4, 0, 0]} name="Avg Delay (min)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '4px' }}>Predicted vs Actual Delay Correlation</h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Validating Gradient Boosting inference against historical actuals</p>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer>
              <LineChart data={predicted_vs_actual}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="flight_number" stroke="#727E93" fontSize={10} />
                <YAxis stroke="#727E93" fontSize={11} unit="m" />
                <Tooltip contentStyle={{ backgroundColor: '#0B0E12', borderColor: 'rgba(255,181,46,0.3)', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="predicted" stroke="#FFB52E" strokeWidth={2} name="Predicted (m)" />
                <Line type="monotone" dataKey="actual" stroke="#19D88A" strokeWidth={2} strokeDasharray="4 4" name="Actual (m)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Watch Demo Modal */}
      {showDemoModal && (
        <div
          className="animate-fade-in"
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(7, 9, 12, 0.88)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px'
          }}
          onClick={() => setShowDemoModal(false)}
        >
          <div
            className="glass-card animate-slide-up"
            style={{
              maxWidth: '680px',
              width: '100%',
              background: '#0B0E12',
              border: '1px solid rgba(255, 181, 46, 0.4)',
              boxShadow: '0 24px 60px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 181, 46, 0.2)',
              padding: '28px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Play size={20} color="#FFB52E" fill="#FFB52E" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>RunwayOptx Operations Walkthrough</h3>
              </div>
              <button
                onClick={() => setShowDemoModal(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ position: 'relative', borderRadius: 'var(--radius-md)', overflow: 'hidden', marginBottom: '20px', border: '1px solid var(--border-subtle)' }}>
              <img
                src="/images/airport-map-aerial.jpg"
                alt="RunwayOptx Airport Walkthrough"
                style={{ width: '100%', height: '240px', objectFit: 'cover', filter: 'brightness(0.8)' }}
              />
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.4)' }}>
                <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'linear-gradient(135deg, #FFB52E, #FF9F1C)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(255, 181, 46, 0.6)' }}>
                  <Play size={26} color="#07090C" fill="#07090C" style={{ marginLeft: '4px' }} />
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#FFB52E' }}>1. Predictive Delay Engine</span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Gradient Boosting models compute arrival taxi delays before gate assignment to avoid apron gridlock.
                </p>
              </div>
              <div style={{ background: 'rgba(17, 21, 26, 0.8)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#19D88A' }}>2. MILP Gate Scheduling</span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Mixed Integer Linear Programming with Google OR-Tools assigns aircraft to minimize turnaround delays and passenger walking distance.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button className="btn btn-secondary" onClick={() => setShowDemoModal(false)}>
                Close
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  setShowDemoModal(false);
                  navigate('/optimization');
                }}
              >
                <span>Launch Gate Optimizer</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
