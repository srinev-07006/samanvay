import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid, Legend
} from 'recharts';
import { Search, Filter, AlertTriangle, CheckCircle, Clock, ArrowRightLeft, ShieldAlert, Building2 } from 'lucide-react';

const COLORS = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#9333ea', '#0891b2'];

export default function Dashboard({ onSelectInstitution, onSelectCase }) {
  const [cases, setCases] = useState([]);
  const [overlaps, setOverlaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBureau, setSelectedBureau] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');

  const token = localStorage.getItem('token');

  const fetchData = async () => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const [casesRes, overlapsRes] = await Promise.all([
        fetch('http://localhost:8000/cases/', { headers }),
        fetch('http://localhost:8000/overlaps/', { headers })
      ]);
      const casesData = await casesRes.json();
      const overlapsData = await overlapsRes.json();

      setCases(Array.isArray(casesData) ? casesData : []);
      setOverlaps(Array.isArray(overlapsData) ? overlapsData : []);
    } catch (err) {
      console.error('Failed to fetch dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // WebSocket connection for real-time alert/overlap notifications
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        fetchData();
      } catch (e) {}
    };

    return () => ws.close();
  }, []);

  // Filter cases
  const filteredCases = cases.filter(c => {
    const matchSearch = searchTerm === '' ||
      c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.institution_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchBureau = selectedBureau === '' || c.source_bureau === selectedBureau;
    const matchStatus = selectedStatus === '' || c.status === selectedStatus;
    const matchRegion = selectedRegion === '' || c.region === selectedRegion;

    return matchSearch && matchBureau && matchStatus && matchRegion;
  });

  // KPI calculations
  const totalReceived = cases.length;
  const pendingCases = cases.filter(c => c.status === 'Pending').length;
  const underProcess = cases.filter(c => c.status === 'Under Process').length;
  const disposedCases = cases.filter(c => c.status === 'Disposed').length;
  const transferredCases = cases.filter(c => c.status === 'Transferred').length;
  const activeOverlaps = overlaps.filter(o => o.state === 'Open').length;

  // Chart data preparations
  const bureauWorkloadMap = {};
  cases.forEach(c => {
    bureauWorkloadMap[c.source_bureau] = (bureauWorkloadMap[c.source_bureau] || 0) + 1;
  });
  const bureauChartData = Object.keys(bureauWorkloadMap).map(k => ({ name: k, count: bureauWorkloadMap[k] }));

  const statusMap = {};
  cases.forEach(c => {
    statusMap[c.status] = (statusMap[c.status] || 0) + 1;
  });
  const statusChartData = Object.keys(statusMap).map(k => ({ name: k, value: statusMap[k] }));

  const regionMap = {};
  cases.forEach(c => {
    regionMap[c.region || 'Unknown'] = (regionMap[c.region || 'Unknown'] || 0) + 1;
  });
  const regionChartData = Object.keys(regionMap).map(k => ({ name: k, count: regionMap[k] }));

  if (loading) {
    return <div className="p-8 text-center text-slate-500 font-medium">Loading SAMANVAY Radar...</div>;
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Overlap Radar Alert Banner */}
      {activeOverlaps > 0 && (
        <div className="bg-red-600 text-white px-6 py-4 rounded-xl shadow-lg flex items-center justify-between animate-pulse">
          <div className="flex items-center space-x-3">
            <ShieldAlert size={28} className="flex-shrink-0" />
            <div>
              <h2 className="font-bold text-lg">Potential Overlapping Cases – Coordination Required</h2>
              <p className="text-sm text-red-100">
                {activeOverlaps} institution(s) detected with simultaneous open complaints across different Bureaus/Cells.
              </p>
            </div>
          </div>
          <a
            href="#overlaps-section"
            className="bg-white text-red-600 px-4 py-2 rounded-lg font-semibold text-sm shadow hover:bg-red-50 transition-colors"
          >
            Review Overlaps ({activeOverlaps})
          </a>
        </div>
      )}

      {/* KPI Tiles */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <p className="text-xs font-semibold text-slate-500 uppercase">Total Received</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalReceived}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <p className="text-xs font-semibold text-amber-600 uppercase">Pending</p>
          <p className="text-2xl font-bold text-amber-600 mt-1">{pendingCases}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <p className="text-xs font-semibold text-blue-600 uppercase">Under Process</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{underProcess}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <p className="text-xs font-semibold text-green-600 uppercase">Disposed</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{disposedCases}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <p className="text-xs font-semibold text-purple-600 uppercase">Transferred</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">{transferredCases}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-red-200 bg-red-50/50">
          <p className="text-xs font-semibold text-red-600 uppercase">Overlap Flags</p>
          <p className="text-2xl font-bold text-red-600 mt-1">{activeOverlaps}</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-4">Bureau / Cell Workload</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bureauChartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-4">Case Status Distribution</h3>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {statusChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-4">Region-wise Case Volume</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={70} />
                <Tooltip />
                <Bar dataKey="count" fill="#16a34a" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-96">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
              <Search size={18} />
            </span>
            <input
              type="text"
              placeholder="Search by Case ID, Institution, or keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          <div className="flex flex-wrap gap-2 w-full md:w-auto">
            <select
              value={selectedBureau}
              onChange={(e) => setSelectedBureau(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All Bureaus / Cells</option>
              <option value="Regulation Bureau">Regulation Bureau</option>
              <option value="PGRC">PGRC</option>
              <option value="Academic Cell">Academic Cell</option>
              <option value="Finance Cell">Finance Cell</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Under Process">Under Process</option>
              <option value="Disposed">Disposed</option>
              <option value="Transferred">Transferred</option>
            </select>

            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All Regions</option>
              <option value="North">North</option>
              <option value="South">South</option>
              <option value="West">West</option>
              <option value="East">East</option>
              <option value="Central">Central</option>
            </select>
          </div>
        </div>

        {/* Cases Table */}
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100 text-slate-700 text-xs uppercase tracking-wider border-b border-slate-200">
                <th className="p-3">Case ID</th>
                <th className="p-3">Institution</th>
                <th className="p-3">Bureau / Cell</th>
                <th className="p-3">Category</th>
                <th className="p-3">Status</th>
                <th className="p-3">Officer</th>
                <th className="p-3">Disposal Due</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              {filteredCases.length === 0 ? (
                <tr>
                  <td colSpan="8" className="p-6 text-center text-slate-500">No cases found matching filter criteria.</td>
                </tr>
              ) : (
                filteredCases.slice(0, 50).map((c) => (
                  <tr key={c.case_id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-3 font-medium text-blue-600 cursor-pointer" onClick={() => onSelectCase(c.case_id)}>
                      {c.case_id}
                    </td>
                    <td className="p-3">
                      <span className="font-semibold cursor-pointer hover:text-blue-600" onClick={() => onSelectInstitution(c.institution_id)}>
                        {c.institution_name}
                      </span>
                      <span className="block text-xs text-slate-400">ID: {c.institution_id} ({c.region})</span>
                    </td>
                    <td className="p-3 text-slate-700">{c.source_bureau}</td>
                    <td className="p-3 text-slate-700">{c.category}</td>
                    <td className="p-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold ${
                        c.status === 'Pending' ? 'bg-amber-100 text-amber-800' :
                        c.status === 'Under Process' ? 'bg-blue-100 text-blue-800' :
                        c.status === 'Disposed' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-700">{c.assigned_officer}</td>
                    <td className="p-3 text-slate-600 text-xs">{c.expected_disposal_date}</td>
                    <td className="p-3 text-right space-x-2">
                      <button
                        onClick={() => onSelectCase(c.case_id)}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-blue-600 hover:text-white rounded text-xs font-medium transition-colors"
                      >
                        View Case
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
