import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getFlights, uploadFlightsCSV } from '../services/api';
import FlightTable from '../components/FlightTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { Search, Filter, Upload, ChevronLeft, ChevronRight, CheckCircle2, AlertCircle, Plane } from 'lucide-react';

export default function Flights() {
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';

  const [flights, setFlights] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState(initialSearch);
  const [airline, setAirline] = useState('');
  const [terminal, setTerminal] = useState('');
  const [delayCategory, setDelayCategory] = useState('');

  // CSV Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const fetchFlights = async () => {
    try {
      setLoading(true);
      const res = await getFlights({
        page,
        page_size: 15,
        search: search || undefined,
        airline: airline || undefined,
        terminal: terminal || undefined,
        delay_category: delayCategory || undefined,
      });
      setFlights(res.data.items);
      setTotal(res.data.total);
      setTotalPages(res.data.total_pages);
    } catch (err) {
      console.error('Failed to load flights:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlights();
  }, [page, airline, terminal, delayCategory]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchFlights();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setUploadResult(null);
      const res = await uploadFlightsCSV(formData);
      setUploadResult(res.data);
      fetchFlights();
    } catch (err) {
      setUploadResult({
        total_rows: 0,
        successful_rows: 0,
        failed_rows: 1,
        errors: [err.response?.data?.error?.message || 'CSV upload failed'],
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Plane size={20} color="#FFB52E" />
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Flight Operations Registry</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Live fleet schedules, taxi delay predictions, and real-time gate bindings ({total} flights monitored)
          </p>
        </div>

        {/* CSV Import */}
        <div>
          <label className="btn btn-outline-amber" style={{ cursor: 'pointer' }}>
            <Upload size={16} />
            <span>{uploading ? 'Importing CSV...' : 'Import Flight Schedule (CSV)'}</span>
            <input
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      {/* Upload Notification */}
      {uploadResult && (
        <div
          className="animate-slide-up"
          style={{
            marginBottom: '20px',
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            background: uploadResult.successful_rows > 0 ? 'rgba(25, 216, 138, 0.12)' : 'rgba(255, 77, 77, 0.12)',
            border: `1px solid ${uploadResult.successful_rows > 0 ? 'rgba(25, 216, 138, 0.35)' : 'rgba(255, 77, 77, 0.35)'}`,
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          {uploadResult.successful_rows > 0 ? <CheckCircle2 color="#19D88A" size={20} /> : <AlertCircle color="#FF4D4D" size={20} />}
          <div>
            <p style={{ fontWeight: 800, fontSize: '0.875rem', color: '#F5F7FA' }}>
              Imported {uploadResult.successful_rows} of {uploadResult.total_rows} flights successfully.
            </p>
            {uploadResult.errors?.length > 0 && (
              <p style={{ fontSize: '0.75rem', color: '#FF6B6B', marginTop: '2px' }}>
                Errors: {uploadResult.errors.join(', ')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr)) 110px', gap: '12px', alignItems: 'end' }}>
          <div>
            <label className="form-label">Flight or Route</label>
            <input
              type="text"
              className="form-input"
              placeholder="Flight, airline, airport..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Airline Carrier</label>
            <select className="form-select" value={airline} onChange={(e) => { setAirline(e.target.value); setPage(1); }}>
              <option value="">All Airlines</option>
              <option value="Air India">Air India</option>
              <option value="IndiGo">IndiGo</option>
              <option value="Vistara">Vistara</option>
              <option value="SpiceJet">SpiceJet</option>
              <option value="Emirates">Emirates</option>
              <option value="British Airways">British Airways</option>
              <option value="Lufthansa">Lufthansa</option>
            </select>
          </div>

          <div>
            <label className="form-label">Terminal</label>
            <select className="form-select" value={terminal} onChange={(e) => { setTerminal(e.target.value); setPage(1); }}>
              <option value="">All Terminals</option>
              <option value="T1">Terminal 1</option>
              <option value="T2">Terminal 2</option>
              <option value="T3">Terminal 3</option>
            </select>
          </div>

          <div>
            <label className="form-label">Delay Severity Tier</label>
            <select className="form-select" value={delayCategory} onChange={(e) => { setDelayCategory(e.target.value); setPage(1); }}>
              <option value="">All Categories</option>
              <option value="On Time">On Time (&le; 5m)</option>
              <option value="Low">Low (6-15m)</option>
              <option value="Moderate">Moderate (16-30m)</option>
              <option value="High">High (31-60m)</option>
              <option value="Severe">Severe (&gt; 60m)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ height: '42px' }}>
            <Search size={16} />
            <span>Search</span>
          </button>
        </form>
      </div>

      {/* Flight Table Card */}
      <div className="glass-card">
        {loading ? (
          <LoadingSpinner text="Retrieving operational flight records..." />
        ) : (
          <>
            <FlightTable flights={flights} />

            {/* Pagination Controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '12px' }}>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                Showing page <strong style={{ color: '#F5F7FA' }}>{page}</strong> of <strong style={{ color: '#F5F7FA' }}>{totalPages}</strong> ({total} total flights)
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className="btn btn-secondary"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  style={{ opacity: page <= 1 ? 0.4 : 1, padding: '7px 14px', fontSize: '0.8125rem' }}
                >
                  <ChevronLeft size={16} />
                  <span>Previous</span>
                </button>
                <button
                  className="btn btn-secondary"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  style={{ opacity: page >= totalPages ? 0.4 : 1, padding: '7px 14px', fontSize: '0.8125rem' }}
                >
                  <span>Next</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
