import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';



export default function CommandCenter() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [risks, setRisks] = useState<any>(null);

  useEffect(() => {
    axios.get('/api/dashboard_stats').then(res => setStats(res.data));
    axios.get('/api/priority_risks').then(res => setRisks(res.data));
  }, []);

  if (!stats || !risks) return <div className="text-slate-500">Loading Command Center...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Supply Chain Command Center</h1>
      <p className="text-slate-600 mb-8">Monitor risk, evaluate decisions, and understand operational impact.</p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">ACTIVE RISKS</p>
          <h2 className="text-3xl font-bold text-slate-900">{stats.active_inventory_risks === 0 ? "0" : stats.active_inventory_risks}</h2>
          <p className="text-sm font-medium mt-2 text-red-600 bg-red-50 px-2 py-1 inline-block rounded">
            {stats.active_inventory_risks > 0 ? `${stats.active_inventory_risks} below ROP` : "All Stock Healthy"}
          </p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">INVENTORY AT RISK</p>
          <h2 className="text-3xl font-bold text-slate-900">{stats.exposure_val > 0 ? `₹${stats.exposure_val.toLocaleString()}` : "₹0"}</h2>
          <p className="text-sm font-medium mt-2 text-red-600 bg-red-50 px-2 py-1 inline-block rounded">
            {stats.exposure_val > 0 ? `Deficit on ${stats.exposure_skus} SKUs` : "Buffer Healthy"}
          </p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">DELIVERY RISK</p>
          <h2 className="text-3xl font-bold text-slate-900">{stats.high_delivery_risks}</h2>
          <p className="text-sm font-medium mt-2 text-orange-600 bg-orange-50 px-2 py-1 inline-block rounded">
            {stats.high_delivery_risks > 0 ? `${stats.high_delivery_risks} of ${stats.total_deliveries} shipments` : "All On-Time"}
          </p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">AI DECISIONS</p>
          <h2 className="text-3xl font-bold text-slate-900">{stats.total_decisions}</h2>
          <p className="text-sm font-medium mt-2 text-slate-600 bg-slate-100 px-2 py-1 inline-block rounded">
            {stats.week_decisions} in last 7 days
          </p>
        </div>
      </div>

      <h2 className="text-xl font-bold text-slate-900 mb-4 border-b pb-2">Priority Risks (Active System State)</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {risks.top_inventory_risk ? (
          <div className="bg-[#1e1e1e] text-white p-6 rounded-lg border border-slate-700">
            <h4 className="text-lg font-bold flex items-center gap-2 mb-2">🔴 TOP INVENTORY RISK: {risks.top_inventory_risk.sku_id}</h4>
            <p className="text-slate-400 text-sm mb-4">Location: {risks.top_inventory_risk.location_id} | Unit Cost: ₹{risks.top_inventory_risk.unit_cost.toFixed(2)} | Lead Time: {risks.top_inventory_risk.lead_time_days}d</p>
            <h3 className="text-xl font-bold text-red-500 mb-2">Stockout Warning: {risks.top_inventory_risk.days_of_supply.toFixed(1)} Days of Supply</h3>
            <p className="text-slate-300 text-sm mb-6">{risks.top_inventory_risk.detail}</p>
            <button 
              onClick={() => {
                 sessionStorage.setItem('target_type', 'Inventory / Demand Issue');
                 sessionStorage.setItem('target_id', risks.top_inventory_risk.sku_id);
                 navigate('/app/create-decision');
              }}
              className="bg-white text-slate-900 px-4 py-2 rounded font-semibold text-sm hover:bg-slate-200 transition-colors">
              Evaluate Decision for {risks.top_inventory_risk.sku_id} →
            </button>
          </div>
        ) : (
          <div className="bg-[#1e1e1e] text-white p-6 rounded-lg border border-slate-700">
            <h4 className="text-lg font-bold mb-2">🟢 INVENTORY OPTIMAL</h4>
            <p className="text-slate-400 text-sm mb-4">All monitored SKUs</p>
            <h3 className="text-xl font-bold text-emerald-500 mb-2">All Stock Levels Healthy</h3>
            <p className="text-slate-300 text-sm">No SKU has current inventory below its reorder point threshold.</p>
          </div>
        )}

        {risks.top_delivery_risk ? (
          <div className="bg-[#1e1e1e] text-white p-6 rounded-lg border border-slate-700">
            <h4 className="text-lg font-bold flex items-center gap-2 mb-2">🟠 TOP DELIVERY RISK: {risks.top_delivery_risk.delivery_id}</h4>
            <p className="text-slate-400 text-sm mb-4">Carrier: {risks.top_delivery_risk.carrier_id} | Route: {risks.top_delivery_risk.origin} ➔ {risks.top_delivery_risk.destination} ({risks.top_delivery_risk.distance_km} km)</p>
            <h3 className="text-xl font-bold mb-2" style={{ color: risks.top_delivery_risk.risk_label === 'HIGH' ? '#ef4444' : '#f97316' }}>
              Late Probability: {(risks.top_delivery_risk.risk_score * 100).toFixed(1)}% ({risks.top_delivery_risk.risk_label})
            </h3>
            <p className="text-slate-300 text-sm mb-6">Traffic Congestion: {risks.top_delivery_risk.traffic_delay_hrs.toFixed(1)} hrs delay | Weather: {risks.top_delivery_risk.weather_condition}</p>
            <button 
              onClick={() => {
                 sessionStorage.setItem('target_type', 'Delivery / Routing Issue');
                 sessionStorage.setItem('target_id', risks.top_delivery_risk.delivery_id);
                 navigate('/app/create-decision');
              }}
              className="bg-white text-slate-900 px-4 py-2 rounded font-semibold text-sm hover:bg-slate-200 transition-colors">
              Investigate Delivery {risks.top_delivery_risk.delivery_id} →
            </button>
          </div>
        ) : (
          <div className="bg-[#1e1e1e] text-white p-6 rounded-lg border border-slate-700">
            <h4 className="text-lg font-bold mb-2">🟢 LOGISTICS OPTIMAL</h4>
            <p className="text-slate-400 text-sm mb-4">All active shipments</p>
            <h3 className="text-xl font-bold text-emerald-500 mb-2">No Delivery Risks Detected</h3>
            <p className="text-slate-300 text-sm">All shipments are currently projected to arrive on time.</p>
          </div>
        )}
      </div>
    </div>
  );
}
