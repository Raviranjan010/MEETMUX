import React, { useState, useEffect } from 'react';
import { predictDelay, predictBatch, getFeatureImportance, getModelMetrics } from '../services/api';
import { getDelayBadgeClass, getDelayColor } from '../utils/formatters';
import { Sparkles, Play, RefreshCw, BarChart2, ShieldCheck, CheckCircle2, Plane, CloudSun, Gauge } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function Predictions() {
  const [formData, setFormData] = useState({
    flight_number: 'AI101',
    airline: 'Air India',
    aircraft_type: 'A320',
    origin: 'DEL',
    destination: 'BOM',
    terminal: 'T3',
    runway: 'RWY-09L',
    scheduled_arrival: new Date().toISOString().slice(0, 16),
    scheduled_departure: new Date(Date.now() + 90 * 60000).toISOString().slice(0, 16),
    temperature: 30.5,
    wind_speed: 14.0,
    visibility: 5.5,
    precipitation: 0.0,
    weather_condition: 'Clear',
    active_flights: 45,
    turnaround_minutes: 45.0,
  });

  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchSummary, setBatchSummary] = useState(null);

  useEffect(() => {
    getFeatureImportance()
      .then((res) => setFeatureImportance(res.data.features || []))
      .catch((err) => console.error('Failed to fetch feature importance:', err));

    getModelMetrics()
      .then((res) => setModelMetrics(res.data))
      .catch((err) => console.error('Failed to fetch model metrics:', err));
  }, []);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await predictDelay({
        ...formData,
        scheduled_arrival: new Date(formData.scheduled_arrival).toISOString(),
        scheduled_departure: new Date(formData.scheduled_departure).toISOString(),
      });
      setPredictionResult(res.data);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchPredict = async () => {
    try {
      setBatchLoading(true);
      const res = await predictBatch({});
      setBatchSummary(res.data);
    } catch (err) {
      console.error('Batch prediction failed:', err);
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Sparkles size={20} color="#FFB52E" />
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Delay Prediction (ML Engine)</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            RunwayOptx gradient-boosted regression estimating arrival taxi queue delays before gate assignment
          </p>
        </div>

        <button
          className="btn btn-emerald"
          onClick={handleBatchPredict}
          disabled={batchLoading}
        >
          <RefreshCw size={16} className={batchLoading ? 'spin-animation' : ''} />
          <span>{batchLoading ? 'Inferring Entire Fleet...' : 'Re-Predict Entire Fleet'}</span>
        </button>
      </div>

      {batchSummary && (
        <div
          className="animate-slide-up"
          style={{
            marginBottom: '20px',
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(25, 216, 138, 0.12)',
            border: '1px solid rgba(25, 216, 138, 0.35)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <CheckCircle2 color="#19D88A" size={22} />
          <div>
            <p style={{ fontWeight: 800, fontSize: '0.875rem', color: '#F5F7FA' }}>
              Successfully generated predictions for {batchSummary.total_processed} flights.
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Fleet Average Predicted Delay: +{batchSummary.average_delay_minutes} minutes across active runway queues.
            </p>
          </div>
        </div>
      )}

      {/* Main Grid: Form on Left, Output & Metrics on Right */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(360px, 1.15fr) minmax(340px, 1fr)', gap: '24px' }}>
        {/* Form Card */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
            <Plane size={18} color="#FFB52E" />
            <h3 style={{ fontSize: '1.125rem', fontWeight: 800 }}>Single Flight Delay Inference</h3>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div className="form-group">
                <label className="form-label">Flight Number</label>
                <input
                  type="text"
                  name="flight_number"
                  className="form-input mono"
                  value={formData.flight_number}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Airline Carrier</label>
                <select name="airline" className="form-select" value={formData.airline} onChange={handleChange}>
                  <option value="Air India">Air India</option>
                  <option value="IndiGo">IndiGo</option>
                  <option value="Vistara">Vistara</option>
                  <option value="SpiceJet">SpiceJet</option>
                  <option value="Emirates">Emirates</option>
                  <option value="British Airways">British Airways</option>
                  <option value="Lufthansa">Lufthansa</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Aircraft Type</label>
                <select name="aircraft_type" className="form-select mono" value={formData.aircraft_type} onChange={handleChange}>
                  <option value="A320">Airbus A320</option>
                  <option value="A321">Airbus A321</option>
                  <option value="B737">Boeing 737</option>
                  <option value="B777">Boeing 777 (Widebody)</option>
                  <option value="B787">Boeing 787 Dreamliner</option>
                  <option value="A350">Airbus A350</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Target Terminal</label>
                <select name="terminal" className="form-select" value={formData.terminal} onChange={handleChange}>
                  <option value="T1">Terminal 1</option>
                  <option value="T2">Terminal 2</option>
                  <option value="T3">Terminal 3</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Origin Airport</label>
                <input type="text" name="origin" className="form-input mono" value={formData.origin} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label className="form-label">Destination</label>
                <input type="text" name="destination" className="form-input mono" value={formData.destination} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label className="form-label">Scheduled Arrival</label>
                <input
                  type="datetime-local"
                  name="scheduled_arrival"
                  className="form-input"
                  value={formData.scheduled_arrival}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Scheduled Departure</label>
                <input
                  type="datetime-local"
                  name="scheduled_departure"
                  className="form-input"
                  value={formData.scheduled_departure}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Active Airspace Flights</label>
                <input
                  type="number"
                  name="active_flights"
                  className="form-input mono"
                  value={formData.active_flights}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Wind Speed (knots)</label>
                <input
                  type="number"
                  step="0.1"
                  name="wind_speed"
                  className="form-input mono"
                  value={formData.wind_speed}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Visibility (km)</label>
                <input
                  type="number"
                  step="0.1"
                  name="visibility"
                  className="form-input mono"
                  value={formData.visibility}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Atmospheric Condition</label>
                <select name="weather_condition" className="form-select" value={formData.weather_condition} onChange={handleChange}>
                  <option value="Clear">Clear</option>
                  <option value="Rain">Rain</option>
                  <option value="Fog">Fog</option>
                  <option value="Thunderstorm">Thunderstorm</option>
                  <option value="Overcast">Overcast</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '16px' }} disabled={loading}>
              <Play size={16} />
              <span>{loading ? 'Computing Predictive Regression...' : 'Run Delay Prediction'}</span>
            </button>
          </form>
        </div>

        {/* Prediction Results & Feature Importance */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Result Card */}
          {predictionResult ? (
            <div
              className="glass-card animate-slide-up"
              style={{
                border: '1px solid rgba(255, 181, 46, 0.45)',
                background: 'linear-gradient(135deg, rgba(14, 18, 24, 0.98) 0%, rgba(22, 28, 38, 0.92) 100%)',
                boxShadow: '0 8px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 181, 46, 0.15)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="form-label" style={{ color: '#FFB52E', margin: 0 }}>Model Inference Output</span>
                <span className="badge badge-amber">Production ML Model</span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '18px 0' }}>
                <div>
                  <h4 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#F5F7FA', fontFamily: 'var(--font-mono)', lineHeight: 1 }}>
                    +{predictionResult.predicted_delay_minutes.toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>min</span>
                  </h4>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Predicted Taxi-In & Runway Delay
                  </p>
                </div>
                <span className={`badge ${getDelayBadgeClass(predictionResult.delay_category)}`} style={{ fontSize: '0.875rem', padding: '8px 16px' }}>
                  {predictionResult.delay_category}
                </span>
              </div>

              {/* Progress bar */}
              <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', marginBottom: '16px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, (predictionResult.predicted_delay_minutes / 60) * 100)}%`,
                    background: 'linear-gradient(90deg, #FFB52E 0%, #FF4D4D 100%)',
                    borderRadius: '3px'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Model Architecture</span>
                  <p style={{ fontWeight: 700, marginTop: '2px' }}>{predictionResult.model_name}</p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Pipeline Version</span>
                  <p className="mono" style={{ fontWeight: 700, marginTop: '2px', color: '#FFB52E' }}>v{predictionResult.model_version}</p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Confidence Score</span>
                  <p className="mono" style={{ fontWeight: 800, marginTop: '2px', color: '#19D88A' }}>
                    {((predictionResult.confidence_score || 0.88) * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center', padding: '48px 20px', color: 'var(--text-muted)' }}>
              <Sparkles size={36} color="#FFB52E" style={{ margin: '0 auto 12px', opacity: 0.6 }} />
              <p style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>Ready for Delay Inference</p>
              <p style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                Select flight parameters on the left and click "Run Delay Prediction".
              </p>
            </div>
          )}

          {/* Feature Importance Chart */}
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <BarChart2 size={18} color="#FFB52E" />
              <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Model Feature Importance</h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Relative contribution of operational variables in Gradient Boosting tree splits
            </p>

            <div style={{ width: '100%', height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={featureImportance} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis type="number" stroke="#727E93" fontSize={10} domain={[0, 'auto']} />
                  <YAxis type="category" dataKey="name" stroke="#727E93" fontSize={11} width={130} />
                  <Tooltip contentStyle={{ backgroundColor: '#0B0E12', borderColor: 'rgba(255,181,46,0.3)', borderRadius: '8px' }} />
                  <Bar dataKey="importance" fill="#FFB52E" radius={[0, 4, 4, 0]} name="Importance" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
