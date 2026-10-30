import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchInstitutionDetails, fetchCaseHistory } from '../services/api';
import { ArrowLeft, Building2, ShieldAlert } from 'lucide-react';

export default function InstitutionProfile({ institutionId, onBack }) {
  const [institution, setInstitution] = useState(null);
  const [caseHistory, setCaseHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const loadData = async () => {
      try {
        const [institutionData, casesData] = await Promise.all([
          fetchInstitutionDetails(institutionId),
          fetchCaseHistory(institutionId)
        ]);
        setInstitution(institutionData);
        setCaseHistory(casesData);
      } catch (err) {
        console.error('Failed to load institution data', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [institutionId]);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500 font-medium">
        Loading institution details...
      </div>
    );
  }

  if (!institution) {
    return (
      <div className="p-8 text-center text-red-500 font-medium">
        Institution not found
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header Section */}
      <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              {institution.name}
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Permanent ID: {institution.permanent_id} | Region: {institution.region} | Pincode: {institution.pincode}
            </p>
          </div>
          <button
            onClick={onBack}
            className="flex items-center space-x-1 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors"
          >
            <ArrowLeft size={16} />
            <span>Back</span>
          </button>
        </div>

        <div className="border-t border-slate-200 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase">Address</span>
              <p className="mt-1 text-sm text-slate-700">{institution.address}</p>
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase">Category</span>
              <p className="mt-1 text-sm text-slate-700 font-medium">{institution.category}</p>
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase">Permanent ID</span>
              <p className="mt-1 text-sm text-slate-700 font-mono">{institution.permanent_id}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Cases List */}
      <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Case History</h2>

        {caseHistory.length === 0 ? (
          <p className="text-center text-slate-500 py-6">No case history found for this institution.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 text-xs uppercase tracking-wider border-b border-slate-200">
                  <th className="p-3">Case ID</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Bureau / Cell</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Officer</th>
                  <th className="p-3">Disposal Due</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-sm">
                {caseHistory.map((c) => (
                  <tr key={c.case_id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-3 font-medium text-blue-600">{c.case_id}</td>
                    <td className="p-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold ${
                        c.status === 'Pending' ? 'bg-amber-100 text-amber-800' :
                        c.status === 'Under Process' ? 'bg-blue-100 text-blue-800' :
                        c.status === 'Disposed' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-600">{c.source_bureau}</td>
                    <td className="p-3 text-slate-600">{c.category}</td>
                    <td className="p-3 text-slate-600">{c.assigned_officer}</td>
                    <td className="p-3 text-slate-600">{c.expected_disposal_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Overlap Flags */}
      {institution.overlap_flags && institution.overlap_flags.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
          <div className="flex items-center space-x-2 mb-4">
            <ShieldAlert className="text-red-600" size={22} />
            <h2 className="text-xl font-bold text-slate-900">Overlap Flags & Coordination Status</h2>
          </div>
          <div className="space-y-3">
            {institution.overlap_flags.map((flag) => (
              <div key={flag.id} className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-semibold text-red-900 text-sm">
                    Cases {flag.case_a_id} ↔ {flag.case_b_id} (Confidence: {flag.confidence_score.toFixed(1)}%)
                  </p>
                  <p className="text-xs text-red-700 mt-1">{flag.reason}</p>
                </div>
                <span className="px-3 py-1 bg-red-600 text-white rounded-full text-xs font-bold uppercase">
                  {flag.state}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
