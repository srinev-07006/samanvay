import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchOverlapDetails } from '../services/api';
import { ShieldAlert, CheckCircle, ArrowRight, ExternalLink } from 'lucide-react';

export default function OverlapPanel({ caseAId, caseBId, onSelectCase }) {
  const [overlaps, setOverlaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchOverlapDetails(caseAId, caseBId);
        setOverlaps(data);
      } catch (err) {
        console.error('Failed to load overlap data', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [caseAId, caseBId]);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500 font-medium">
        Loading overlap details...
      </div>
    );
  }

  if (overlaps.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <p className="text-center text-slate-500">No overlapping cases found between these institutions.</p>
      </div>
    );
  }

  const overlap = overlaps[0];

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 border-b border-slate-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-red-100 text-red-600 rounded-lg">
            <ShieldAlert size={24} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Overlap Radar Match</h3>
            <p className="text-xs text-slate-500">Confidence Score: <span className="font-semibold text-slate-700">{overlap.confidence_score?.toFixed(1)}%</span></p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
          overlap.state === 'Open' ? 'bg-red-100 text-red-800' :
          overlap.state === 'Linked' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
        }`}>
          {overlap.state}
        </span>
      </div>

      {/* Cases Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-blue-600 uppercase">Case A</span>
            <span className="text-xs font-mono text-slate-500">{overlap.case_a_id}</span>
          </div>
          <button
            onClick={() => onSelectCase && onSelectCase(overlap.case_a_id)}
            className="text-base font-bold text-slate-900 hover:text-blue-600 flex items-center space-x-1 transition-colors"
          >
            <span>View Case {overlap.case_a_id}</span>
            <ExternalLink size={14} />
          </button>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-blue-600 uppercase">Case B</span>
            <span className="text-xs font-mono text-slate-500">{overlap.case_b_id}</span>
          </div>
          <button
            onClick={() => onSelectCase && onSelectCase(overlap.case_b_id)}
            className="text-base font-bold text-slate-900 hover:text-blue-600 flex items-center space-x-1 transition-colors"
          >
            <span>View Case {overlap.case_b_id}</span>
            <ExternalLink size={14} />
          </button>
        </div>
      </div>

      {/* Reasoning */}
      <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
        <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-1">Overlap Detection Reasoning</h4>
        <p className="text-sm text-amber-800">{overlap.reason}</p>
      </div>

      {/* Action Banner */}
      {overlap.state === 'Open' && (
        <div className="bg-red-600 text-white p-4 rounded-xl flex items-center justify-between shadow">
          <div>
            <p className="font-bold">Coordination Required Between Bureaus</p>
            <p className="text-xs text-red-100 mt-0.5">Simultaneous open complaints detected on the same institution ID.</p>
          </div>
          <button
            onClick={() => {
              // Action handler or link case
              alert(`Coordinating overlap between ${overlap.case_a_id} and ${overlap.case_b_id}`);
            }}
            className="px-4 py-2 bg-white text-red-600 rounded-lg font-semibold text-xs hover:bg-red-50 transition-colors shadow-sm"
          >
            Initiate Joint Review
          </button>
        </div>
      )}
    </div>
  );
}
