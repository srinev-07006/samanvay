import React from 'react';
import { ShieldAlert, Bell, LogOut, FileText, Download, Activity, Building, Search } from 'lucide-react';

export default function Navbar({ user, onLogout, activeTab, setActiveTab, unreadAlertsCount }) {
  const handleDownloadExcel = () => {
    window.open('http://localhost:8000/reports/excel', '_blank');
  };

  const handleDownloadPdf = () => {
    window.open('http://localhost:8000/reports/pdf', '_blank');
  };

  return (
    <header className="bg-slate-900 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white shadow">
            <Activity size={22} />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight">SAMANVAY</span>
            <span className="hidden sm:inline-block ml-2 text-xs bg-blue-900 text-blue-200 px-2 py-0.5 rounded-full font-medium">SIH 2026</span>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            KPI Dashboard
          </button>
          <button
            onClick={() => setActiveTab('overlaps')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${activeTab === 'overlaps' ? 'bg-red-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            <ShieldAlert size={16} />
            <span>Overlap Radar</span>
          </button>
          <button
            onClick={() => setActiveTab('institutions')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'institutions' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            Institutions
          </button>
          <button
            onClick={() => setActiveTab('new_case')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'new_case' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            + Log Complaint
          </button>
        </nav>

        <div className="flex items-center space-x-3">
          <div className="hidden lg:flex items-center space-x-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <div className="text-right">
              <p className="text-xs font-semibold text-white">{user.username}</p>
              <p className="text-[10px] text-blue-400">{user.bureau_cell || user.role} {user.region && `(${user.region})`}</p>
            </div>
          </div>

          <div className="flex items-center space-x-1 border-l border-slate-700 pl-3">
            <button
              onClick={handleDownloadExcel}
              title="Download Excel Report"
              className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Download size={18} />
            </button>
            <button
              onClick={handleDownloadPdf}
              title="Download PDF Report"
              className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <FileText size={18} />
            </button>
            <button
              onClick={onLogout}
              title="Sign Out"
              className="p-2 text-red-400 hover:text-red-300 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
