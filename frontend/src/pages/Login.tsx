import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Single-operator validation (per docs/AUTH.md)
    if (username.trim() === 'operator' && password === 'runwayoptx2026') {
      // In production API, this calls /api/auth/login to retrieve signed JWT
      localStorage.setItem('runwayoptx_token', 'operator_authenticated_session_token');
      navigate('/dashboard');
    } else {
      setError('Invalid operator credentials. Default: operator / runwayoptx2026');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-bg p-4">
      <div className="w-full max-w-md bg-surface border border-muted/20 rounded p-8 shadow-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded bg-green/10 border border-green/30 flex items-center justify-center text-green font-mono font-bold">
            RX
          </div>
          <div>
            <h1 className="text-lg font-bold font-mono tracking-wider text-white">RUNWAYOPTX</h1>
            <p className="text-xs text-muted">Airport Operations Access Gate</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded bg-red/10 border border-red/30 flex items-start gap-2.5 text-xs text-red">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-muted uppercase mb-1">Operator ID</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="operator"
              required
              className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-sm text-white font-mono focus:outline-none focus:border-green transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-muted uppercase mb-1">Passphrase</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              className="w-full px-3 py-2 bg-surface-elevated border border-muted/30 rounded text-sm text-white font-mono focus:outline-none focus:border-green transition-colors"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-green hover:bg-green/90 text-bg font-semibold rounded text-xs font-mono tracking-wider uppercase transition-colors flex items-center justify-center gap-2"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>{loading ? 'Authenticating...' : 'Enter Command Center'}</span>
            </button>
          </div>
        </form>

        <div className="mt-6 pt-6 border-t border-muted/20 text-center">
          <p className="text-[11px] text-muted font-mono">
            RunwayOptX v1.0 • Authorized Personnel Only
          </p>
        </div>
      </div>
    </div>
  );
};
