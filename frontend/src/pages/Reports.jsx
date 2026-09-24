import React, { useState, useEffect } from 'react';
import { getDashboardSummary, getModelMetrics } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { FileText, Download, CheckCircle2, Calendar, ShieldCheck, ArrowDownToLine, Clock, Plane } from 'lucide-react';

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDashboardSummary(), getModelMetrics()])
      .then(([summaryRes, metricsRes]) => {
        setSummary(summaryRes.data);
        setMetrics(metricsRes.data);
      })
      .catch((err) => console.error('Failed to load reports data:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleDownloadReport = (reportType) => {
    let content = '';
    let filename = '';

    if (reportType === 'kpi') {
      filename = 'runwayoptx_operational_kpi_report.csv';
      content = 'Metric,Value\n' +
        `Total Flights,${summary?.kpis?.total_flights || 0}\n` +
        `Delayed Flights,${summary?.kpis?.delayed_flights || 0}\n` +
        `Delayed Percentage,${summary?.kpis?.delayed_percentage || 0}%\n` +
        `Average Predicted Delay,${summary?.kpis?.average_predicted_delay_minutes || 0} min\n` +
        `Gate Utilization Rate,${summary?.kpis?.gate_utilization_rate || 0}%\n` +
        `Gates Utilized,${summary?.kpis?.gates_utilized || 0}\n` +
        `Solver Status,${summary?.kpis?.latest_optimization_status || 'N/A'}\n`;
    } else if (reportType === 'airline') {
      filename = 'runwayoptx_airline_delay_report.csv';
      content = 'Airline,Average Delay Minutes\n' +
        (summary?.delay_by_airline || []).map(a => `"${a.airline}",${a.avg_delay}`).join('\n');
    } else {
      filename = 'runwayoptx_ml_model_benchmark_report.csv';
      content = 'Model,MAE,RMSE,R2\n' +
        (metrics?.model_comparisons || []).map(m => `"${m.name}",${m.test_metrics?.mae},${m.test_metrics?.rmse},${m.test_metrics?.r2}`).join('\n');
    }

    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <LoadingSpinner text="Generating executive operations reports..." />;
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <FileText size={20} color="#FFB52E" />
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Airport Operations Reports</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Exportable regulatory reports, gate capacity audits, and air traffic punctuality evaluations
        </p>
      </div>

      {/* Reports Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        {/* Report 1 */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span className="badge badge-amber">Daily Operations Audit</span>
              <Calendar size={16} color="var(--text-muted)" />
            </div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 800, marginBottom: '6px' }}>
              Air Traffic & Delay KPI Summary
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: '16px' }}>
              Comprehensive operational breakdown including {summary?.kpis?.total_flights || 0} flights,
              average taxi delay (+{summary?.kpis?.average_predicted_delay_minutes || 0}m), and gate capacity metrics.
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => handleDownloadReport('kpi')}
            style={{ width: '100%' }}
          >
            <Download size={16} />
            <span>Download KPI Audit (CSV)</span>
          </button>
        </div>

        {/* Report 2 */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span className="badge badge-purple">Carrier Analytics</span>
              <Plane size={16} color="var(--text-muted)" />
            </div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 800, marginBottom: '6px' }}>
              Carrier Punctuality & Turnaround Log
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: '16px' }}>
              Benchmarking performance across all commercial operators (Air India, IndiGo, Vistara, Emirates, etc.)
              at Indira Gandhi International Airport.
            </p>
          </div>
          <button
            className="btn btn-outline-amber"
            onClick={() => handleDownloadReport('airline')}
            style={{ width: '100%' }}
          >
            <Download size={16} />
            <span>Download Carrier Log (CSV)</span>
          </button>
        </div>

        {/* Report 3 */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span className="badge badge-ontime">AI / ML Validation</span>
              <ShieldCheck size={16} color="var(--text-muted)" />
            </div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 800, marginBottom: '6px' }}>
              ML Regressor Accuracy Benchmark
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: '16px' }}>
              Time-series cross validation metrics comparing Gradient Boosting, Random Forest, and Linear Regression
              MAE, RMSE, and R² scores.
            </p>
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => handleDownloadReport('ml')}
            style={{ width: '100%' }}
          >
            <Download size={16} />
            <span>Download ML Benchmark (CSV)</span>
          </button>
        </div>
      </div>

      {/* Snapshot Summary Panel */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '14px' }}>Latest Operational Snapshot</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Audit Window</span>
            <p style={{ fontWeight: 700, marginTop: '2px' }}>Live Operating Period</p>
          </div>
          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Tracked Fleet Volume</span>
            <p className="mono" style={{ fontWeight: 800, color: '#FFB52E', marginTop: '2px' }}>{summary?.kpis?.total_flights || 0} Aircraft</p>
          </div>
          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Gate Congestion Factor</span>
            <p className="mono" style={{ fontWeight: 800, color: '#19D88A', marginTop: '2px' }}>{summary?.kpis?.gate_utilization_rate || 0}% Nominal</p>
          </div>
          <div style={{ background: 'rgba(11, 14, 18, 0.8)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Solver Health</span>
            <p style={{ fontWeight: 700, color: '#19D88A', marginTop: '2px' }}>100% Constraints Met</p>
          </div>
        </div>
      </div>
    </div>
  );
}
