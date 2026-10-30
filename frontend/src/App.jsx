import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import InstitutionProfile from './components/InstitutionProfile';
import OverlapPanel from './components/OverlapPanel';
import { ShieldAlert, AlertTriangle, Building2, PlusCircle, CheckCircle, Clock } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedInstitutionId, setSelectedInstitutionId] = useState(null);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [overlaps, setOverlaps] = useState([]);
  const [institutions, setInstitutions] = useState([]);
  const [newCaseForm, setNewCaseForm] = useState({
    institution_id: '',
    source_bureau: 'Regulation Bureau',
    category: 'Faculty Shortage',
    description: '',
    region: 'North',
    assigned_officer: 'Officer Sharma',
    expected_disposal_date: '2026-12-31'
  });
  const [caseSuccess, setCaseSuccess] = useState('');

  const token = localStorage.getItem('token');

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.clear();
      }
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchOverlaps();
      fetchInstitutions();
    }
  }, [token]);

  const fetchOverlaps = async () => {
    try {
      const res = await fetch('http://localhost:8000/overlaps/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (Array.isArray(data)) setOverlaps(data);
    } catch (e) {}
  };

  const fetchInstitutions = async () => {
    try {
      const res = await fetch('http://localhost:8000/institutions/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (Array.isArray(data)) setInstitutions(data);
    } catch (e) {}
  };

  const handleLogin = (authData) => {
    localStorage.setItem('token', authData.access_token);
    const userData = { username: authData.username, role: authData.role, bureau_cell: authData.bureau_cell, region: authData.region };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setActiveTab('dashboard');
    setSelectedInstitutionId(null);
    setSelectedCaseId(null);
  };

  const handleCreateCase = async (e) => {
    e.preventDefault();
    setCaseSuccess('');
    try {
      const res = await fetch('http://localhost:8000/cases/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newCaseForm)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to log complaint');
      setCaseSuccess(`Complaint successfully logged! Case ID: ${data.case_id}`);
      setNewCaseForm({
        institution_id: '',
        source_bureau: 'Regulation Bureau',
        category: 'Faculty Shortage',
        description: '',
        region: 'North',
        assigned_officer: 'Officer Sharma',
        expected_disposal_date: '2026-12-31'
      });
      fetchOverlaps();
    } catch (err) {
      alert(err.message);
    }
  };

  if (!user || !token) {
    return <Login onLogin={handleLogin} />;
  }

  const activeOverlaps = overlaps.filter(o => o.state === 'Open');

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 font-sans">
      <Navbar
        user={user}
        onLogout={handleLogout}
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setSelectedInstitutionId(null);
          setSelectedCaseId(null);
        }}
        unreadAlertsCount={activeOverlaps.length}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedInstitutionId ? (
          <InstitutionProfile
            institutionId={selectedInstitutionId}
            onBack={() => setSelectedInstitutionId(null)}
          />
        ) : activeTab === 'dashboard' ? (
          <Dashboard
            onSelectInstitution={(id) => setSelectedInstitutionId(id)}
            onSelectCase={(id) => setSelectedCaseId(id)}
          />
        ) : activeTab === 'overlaps' ? (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
              <div className="flex items-center space-x-3 mb-4">
                <ShieldAlert className="text-red-600" size={28} />
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Overlap Radar – Conflict Resolution Center</h2>
                  <p className="text-sm text-slate-500">
                    Detects simultaneous open complaints across different Bureaus/Cells for the same institution.
                  </p>
                </div>
              </div>

              {activeOverlaps.length === 0 ? (
                <div className="p-12 text-center text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                  <CheckCircle className="mx-auto text-green-600 mb-2" size={36} />
                  <p className="font-semibold text-slate-700">No active case overlaps detected!</p>
                  <p className="text-xs text-slate-400 mt-1">All institution complaints are currently coordinated or distinct.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeOverlaps.map(overlap => (
                    <OverlapPanel
                      key={overlap.id}
                      caseAId={overlap.case_a_id}
                      caseBId={overlap.case_b_id}
                      onSelectCase={(id) => setSelectedCaseId(id)}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : activeTab === 'institutions' ? (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Registered Institutions Directory</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {institutions.map(inst => (
                <div
                  key={inst.id}
                  onClick={() => setSelectedInstitutionId(inst.id)}
                  className="p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all bg-slate-50/50 hover:bg-white"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-bold text-slate-800 text-base">{inst.name}</h3>
                      <p className="text-xs text-slate-500 mt-1">ID: {inst.permanent_id} | Region: {inst.region}</p>
                    </div>
                    <Building2 className="text-blue-600 flex-shrink-0" size={22} />
                  </div>
                  <p className="text-xs text-slate-600 mt-3 line-clamp-2">{inst.address}</p>
                  <div className="mt-4 flex items-center justify-between text-xs font-semibold text-blue-600">
                    <span>View Profile & Cases →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : activeTab === 'new_case' ? (
          <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-100 text-blue-700 rounded-lg">
                <PlusCircle size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Log New Institution Complaint</h2>
                <p className="text-sm text-slate-500">File a complaint or case into Regulation Bureau or PGRC.</p>
              </div>
            </div>

            {caseSuccess && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-800 rounded-lg text-sm font-medium flex items-center space-x-2">
                <CheckCircle size={20} className="text-green-600 flex-shrink-0" />
                <span>{caseSuccess}</span>
              </div>
            )}

            <form onSubmit={handleCreateCase} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Institution ID / Permanent ID</label>
                <select
                  required
                  value={newCaseForm.institution_id}
                  onChange={(e) => setNewCaseForm({...newCaseForm, institution_id: e.target.value})}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">Select Institution...</option>
                  {institutions.map(inst => (
                    <option key={inst.id} value={inst.id}>
                      {inst.name} ({inst.permanent_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Source Bureau / Cell</label>
                  <select
                    value={newCaseForm.source_bureau}
                    onChange={(e) => setNewCaseForm({...newCaseForm, source_bureau: e.target.value})}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="Regulation Bureau">Regulation Bureau</option>
                    <option value="PGRC">PGRC</option>
                    <option value="Academic Cell">Academic Cell</option>
                    <option value="Finance Cell">Finance Cell</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Category</label>
                  <select
                    value={newCaseForm.category}
                    onChange={(e) => setNewCaseForm({...newCaseForm, category: e.target.value})}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="Faculty Shortage">Faculty Shortage</option>
                    <option value="Fee Overcharging">Fee Overcharging</option>
                    <option value="Infrastructure Deficit">Infrastructure Deficit</option>
                    <option value="Ragging / Harassment">Ragging / Harassment</option>
                    <option value="Approval Non-Compliance">Approval Non-Compliance</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Region</label>
                  <select
                    value={newCaseForm.region}
                    onChange={(e) => setNewCaseForm({...newCaseForm, region: e.target.value})}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="North">North</option>
                    <option value="South">South</option>
                    <option value="West">West</option>
                    <option value="East">East</option>
                    <option value="Central">Central</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Assigned Officer</label>
                  <input
                    type="text"
                    required
                    value={newCaseForm.assigned_officer}
                    onChange={(e) => setNewCaseForm({...newCaseForm, assigned_officer: e.target.value})}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Disposal Due Date</label>
                  <input
                    type="date"
                    required
                    value={newCaseForm.expected_disposal_date}
                    onChange={(e) => setNewCaseForm({...newCaseForm, expected_disposal_date: e.target.value})}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Complaint Description & Details</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Enter detailed description of the grievance or regulatory inspection finding..."
                  value={newCaseForm.description}
                  onChange={(e) => setNewCaseForm({...newCaseForm, description: e.target.value})}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-md transition-colors"
              >
                Submit & Check Overlap Radar
              </button>
            </form>
          </div>
        ) : null}
      </main>
    </div>
  );
}
