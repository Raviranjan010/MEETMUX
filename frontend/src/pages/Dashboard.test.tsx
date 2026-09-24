import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from './Dashboard';
import * as api from '../api';

vi.mock('../api', () => ({
  getHealth: vi.fn(),
  getFlights: vi.fn().mockResolvedValue({ items: [], total: 0 }),
  getGates: vi.fn().mockResolvedValue([]),
  detectConflicts: vi.fn().mockResolvedValue({ conflicts: [], total: 0 }),
  getAlerts: vi.fn().mockResolvedValue([]),
  runReoptimization: vi.fn().mockResolvedValue({}),
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    vi.spyOn(api, 'getHealth').mockReturnValue(new Promise(() => {}));
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
    expect(screen.getByTestId('dashboard-loading')).toBeInTheDocument();
  });

  it('renders success state with system health data', async () => {
    vi.spyOn(api, 'getHealth').mockResolvedValue({
      status: 'ok',
      database: true,
      ml_model_loaded: true,
      optimizer: {
        gurobi_available: false,
        ortools_available: true,
      },
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-view')).toBeInTheDocument();
    });

    expect(screen.getByText('COMMAND CENTER OVERVIEW')).toBeInTheDocument();
    expect(screen.getByText('LIVE SYSTEM')).toBeInTheDocument();
    expect(screen.getByText(/OR-TOOLS CP-SAT/i)).toBeInTheDocument();
  });

  it('renders error state when backend is unreachable', async () => {
    vi.spyOn(api, 'getHealth').mockRejectedValue(new Error('Network Error'));

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-error')).toBeInTheDocument();
    });

    expect(screen.getByText('Backend Service Unreachable')).toBeInTheDocument();
  });
});
