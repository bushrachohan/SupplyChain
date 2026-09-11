import { useState, useEffect } from 'react';
import axios from 'axios';

export default function DataHub() {
  const [status, setStatus] = useState<any>(null);

  const fetchStatus = () => {
    axios.get('/api/data/status').then(res => setStatus(res.data));
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleUseDemo = async () => {
    await axios.post('/api/data/use_demo');
    fetchStatus();
    alert('Switched to Synthetic Demo Dataset.');
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Enterprise Data Hub</h1>
      <p className="text-slate-600 mb-8">Connect, map, and validate your supply chain datasets.</p>

      <div className="bg-emerald-50 border border-emerald-200 p-5 rounded-lg mb-8">
        <p className="font-semibold text-emerald-900 mb-2">● DATA SOURCE: Company Dataset — Connected</p>
        <p className="text-emerald-800 text-sm mb-4">Active Status: Active dataset is dynamically ingested and powering Sentinel AI decisions.</p>
        
        {status && (
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Active Format</p>
              <p className="text-xl font-bold text-slate-900">CSV</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Inventory SKUs</p>
              <p className="text-xl font-bold text-slate-900">{status.inventory_skus}</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Deliveries Loaded</p>
              <p className="text-xl font-bold text-slate-900">{status.deliveries}</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Demand Records</p>
              <p className="text-xl font-bold text-slate-900">{status.demand_records}</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Synthetic Demo Dataset</h2>
        <p className="text-slate-600 text-sm mb-6">Use the synthetic data bundled with the application to safely test Sentinel's AI decision-making capabilities without connecting your own systems.</p>
        
        <button 
          onClick={handleUseDemo}
          className="bg-teal-700 hover:bg-teal-800 text-white font-medium px-4 py-2 rounded shadow-sm transition-colors"
        >
          Use Demo Dataset
        </button>
      </div>

      <div className="mt-8 text-sm text-slate-500">
        <p>CSV / Excel Upload and Database Integration are supported via the Backend Pipeline API.</p>
      </div>
    </div>
  );
}
