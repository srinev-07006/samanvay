import React, { useState } from 'react';
import { ShieldCheck, Lock, User } from 'lucide-react';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('rb_admin');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');

      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (uname, pwd) => {
    setUsername(uname);
    setPassword(pwd);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-slate-900 to-indigo-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border border-slate-100">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-blue-100 text-blue-700 rounded-full mb-3 shadow-inner">
            <ShieldCheck size={36} />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">SAMANVAY</h1>
          <p className="text-sm text-slate-500 mt-1">Unified Institution Complaint Radar (AICTE SIH 2026)</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Username</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <User size={18} />
              </span>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition-all"
                placeholder="Enter username"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Lock size={18} />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-100">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3 text-center">Quick Demo Accounts</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleQuickLogin('rb_admin', 'password123')}
              className="text-xs p-2 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 rounded border border-slate-200 font-medium text-left transition-colors"
            >
              <span className="font-bold block">RB Admin</span>Regulation Bureau
            </button>
            <button
              onClick={() => handleQuickLogin('pgrc_admin', 'password123')}
              className="text-xs p-2 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 rounded border border-slate-200 font-medium text-left transition-colors"
            >
              <span className="font-bold block">PGRC Admin</span>PGRC Cell
            </button>
            <button
              onClick={() => handleQuickLogin('ro_west', 'password123')}
              className="text-xs p-2 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 rounded border border-slate-200 font-medium text-left transition-colors"
            >
              <span className="font-bold block">RO West</span>Regional Office
            </button>
            <button
              onClick={() => handleQuickLogin('senior_mgmt', 'password123')}
              className="text-xs p-2 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 rounded border border-slate-200 font-medium text-left transition-colors"
            >
              <span className="font-bold block">Senior Mgmt</span>Executive Board
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
