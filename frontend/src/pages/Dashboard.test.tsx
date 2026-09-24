import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from './Dashboard';
import * as healthApi from '../api/health';

vi.mock('../api/health', () => ({
  fetchHealth: vi.fn(),
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    vi.spyOn(healthApi, 'fetchHealth').mockReturnValue(new Promise(() => {}));
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
    expect(screen.getByTestId('dashboard-loading')).toBeInTheDocument();
  });

  it('renders success state with system health data', async () => {
    vi.spyOn(healthApi, 'fetchHealth').mockResolvedValue({
      status: 'ok',
      database: true,
      ml_model_loaded: false,
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

    expect(screen.getByText('OPERATIONS OVERVIEW')).toBeInTheDocument();
    expect(screen.getByText('CONNECTED')).toBeInTheDocument();
    expect(screen.getByText('OR-TOOLS CP-SAT')).toBeInTheDocument();
    expect(screen.getByText('PENDING P4')).toBeInTheDocument();
  });

  it('renders error state when backend is unreachable', async () => {
    vi.spyOn(healthApi, 'fetchHealth').mockRejectedValue(new Error('Network Error'));

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-error')).toBeInTheDocument();
    });

    expect(screen.getByText('Backend Service Unreachable')).toBeInTheDocument();
    expect(screen.getByText('Network Error')).toBeInTheDocument();
  });
});
