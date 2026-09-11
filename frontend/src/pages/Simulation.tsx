import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Simulation() {
  const [simMode, setSimMode] = useState('inventory');
  const [options, setOptions] = useState<{skus: string[], deliveries: string[]}>({ skus: [], deliveries: [] });

  // Inventory state
  const [invSku, setInvSku] = useState('');
  const [demandMult, setDemandMult] = useState(1.5);
  const [invResult, setInvResult] = useState<any>(null);

  // Delivery state
  const [delId, setDelId] = useState('');
  const [weather, setWeather] = useState('CLEAR');
  const [traffic, setTraffic] = useState(0.0);
  const [delResult, setDelResult] = useState<any>(null);

  // Logistics state
  const [logIds, setLogIds] = useState<string[]>([]);
  const [numVehicles, setNumVehicles] = useState(2);
  const [capMult, setCapMult] = useState(1.0);
  const [logResult, setLogResult] = useState<any>(null);

  useEffect(() => {
    axios.get('/api/options').then(res => {
      setOptions(res.data);
      if (res.data.skus.length > 0) setInvSku(res.data.skus[0]);
      if (res.data.deliveries.length > 0) {
        setDelId(res.data.deliveries[0]);
        setLogIds(res.data.deliveries.slice(0, 5));
      }
    });
  }, []);

  const runInventory = async () => {
    const res = await axios.post('/api/simulate/inventory', {
      sku_id: invSku,
      demand_multiplier: demandMult,
    });
    setInvResult(res.data);
  };

  const runDelivery = async () => {
    const res = await axios.post('/api/simulate/delivery', {
      delivery_id: delId,
      weather_override: weather,
      traffic_override: traffic,
    });
    setDelResult(res.data);
  };

  const runLogistics = async () => {
    const res = await axios.post('/api/simulate/logistics', {
      delivery_ids: logIds,
      num_vehicles: numVehicles,
      capacity_multiplier: capMult,
    });
    setLogResult(res.data);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">What-If Simulation & Business Intelligence</h1>
      <p className="text-slate-600 mb-8">Stress-test supply-chain operations under shifting market conditions, disruptions, and capacity constraints.</p>

      <div className="bg-[#1a1a2e] border border-[#30363d] rounded-lg p-4 mb-8 flex justify-between text-sm text-[#c9d1d9] font-medium">
        <span>🔍 <b>1. Identify Operational Risk</b></span>
        <span className="text-[#58a6ff]">➔</span>
        <span>⚙️ <b>2. Configure Stress Test Overrides</b></span>
        <span className="text-[#58a6ff]">➔</span>
        <span>📊 <b>3. Compare Baseline vs. Scenario</b></span>
        <span className="text-[#58a6ff]">➔</span>
        <span>🛡️ <b>4. Evaluate Action Delta (Do Nothing vs. Act)</b></span>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-slate-700 mb-2">Select Simulation Domain</label>
        <select 
          value={simMode}
          onChange={(e) => setSimMode(e.target.value)}
          className="w-full max-w-md border-slate-300 rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 p-2 border"
        >
          <option value="inventory">📦 Inventory Risk & Stockout</option>
          <option value="delivery">🚚 Delivery Risk & Transit Delay</option>
          <option value="logistics">🗺️ Logistics Fleet & Routing Capacity</option>
        </select>
      </div>

      <hr className="mb-8" />

      {simMode === 'inventory' && (
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">📦 Inventory Stress-Testing: Demand Shocks & Supplier Delays</h2>
          <p className="text-slate-600 mb-6">Simulate how demand spikes or supplier lead time extensions impact Days of Supply and Stockout exposure.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
              <h4 className="font-bold mb-4 border-b pb-2">Scenario Controls</h4>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Select Target SKU</label>
                <select value={invSku} onChange={e => setInvSku(e.target.value)} className="w-full border-slate-300 rounded-md p-2 border">
                  {options.skus.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-1">Demand Surge Multiplier ({demandMult.toFixed(1)}x)</label>
                <input 
                  type="range" min="0.5" max="3.0" step="0.1" 
                  value={demandMult} onChange={e => setDemandMult(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <button onClick={runInventory} className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded transition-colors">
                ⚡ Run Inventory Simulation
              </button>
            </div>

            <div>
              <h4 className="font-bold mb-4">Projected Business Impact</h4>
              {invResult ? (
                <div>
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-white p-4 rounded border border-slate-200 text-center">
                      <p className="text-xs text-slate-500 uppercase">Days of Supply</p>
                      <p className="text-xl font-bold">{invResult.after.days_of_supply.toFixed(1)} d</p>
                      <p className={`text-xs ${invResult.deltas.days_of_supply_delta < 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                        {invResult.deltas.days_of_supply_delta > 0 ? '+' : ''}{invResult.deltas.days_of_supply_delta.toFixed(1)} d
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded border border-slate-200 text-center">
                      <p className="text-xs text-slate-500 uppercase">Reorder Point</p>
                      <p className="text-xl font-bold">{invResult.after.reorder_point_units.toFixed(0)} u</p>
                      <p className={`text-xs ${invResult.deltas.reorder_point_delta > 0 ? 'text-orange-500' : 'text-slate-500'}`}>
                        +{invResult.deltas.reorder_point_delta.toFixed(0)} u
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded border border-slate-200 text-center flex flex-col justify-center">
                      <p className="text-xs text-slate-500 uppercase mb-1">Risk Level</p>
                      <div className="flex flex-col gap-1 items-center">
                         <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[10px] font-bold">{invResult.before.risk_level}</span>
                         <span className="text-slate-400 text-xs">⬇</span>
                         <span className={`px-2 py-0.5 rounded text-[10px] font-bold text-white ${invResult.after.risk_level.includes('STOCKOUT') ? 'bg-red-500' : 'bg-emerald-500'}`}>{invResult.after.risk_level}</span>
                      </div>
                    </div>
                  </div>

                  <h5 className="font-bold mb-2">🛡️ Decision Delta: Do Nothing vs. Recommended Action</h5>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-red-50 border border-red-200 text-red-900 p-4 rounded text-sm">
                      <strong>❌ Do Nothing Scenario</strong>
                      <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                        <li>Buffer depleted within {invResult.after.days_of_supply.toFixed(1)} days.</li>
                        <li>Stockout penalty incurred; customer fulfillments backlogged.</li>
                      </ul>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded text-sm">
                      <strong>✅ Recommended Action (AI Decision)</strong>
                      <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                        <li>Issue replenishment PO for {Math.max(0, invResult.after.reorder_point_units - invResult.after.current_stock).toFixed(0)} units.</li>
                        <li>Enforce expedited supplier dispatch to hold lead time to {invResult.after.lead_time_days} days.</li>
                        <li>Preserves service level stability.</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-slate-400 italic">Configure scenario and run simulation to view results.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {simMode === 'delivery' && (
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">🚚 Delivery Risk: Severe Weather & Traffic Bottlenecks</h2>
          <p className="text-slate-600 mb-6">Simulate how severe weather disruptions or extreme highway congestion elevate delivery delay probability.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
              <h4 className="font-bold mb-4 border-b pb-2">Scenario Controls</h4>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Select Target Delivery ID</label>
                <select value={delId} onChange={e => setDelId(e.target.value)} className="w-full border-slate-300 rounded-md p-2 border">
                  {options.deliveries.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Simulate Weather Condition</label>
                <select value={weather} onChange={e => setWeather(e.target.value)} className="w-full border-slate-300 rounded-md p-2 border">
                  <option value="CLEAR">CLEAR</option>
                  <option value="RAIN">RAIN</option>
                  <option value="FOG">FOG</option>
                  <option value="STORM">STORM</option>
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-1">Simulate Traffic Delay ({traffic.toFixed(1)} hrs)</label>
                <input 
                  type="range" min="0.0" max="12.0" step="0.5" 
                  value={traffic} onChange={e => setTraffic(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <button onClick={runDelivery} className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded transition-colors">
                ⚡ Run Delivery Simulation
              </button>
            </div>

            <div>
              <h4 className="font-bold mb-4">Projected Business Impact</h4>
              {delResult ? (
                <div>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white p-4 rounded border border-slate-200 text-center">
                      <p className="text-xs text-slate-500 uppercase">Late Delivery Probability</p>
                      <p className="text-xl font-bold">{(delResult.after.risk_score * 100).toFixed(1)}%</p>
                      <p className={`text-xs ${delResult.deltas.risk_score_delta > 0 ? 'text-red-500' : 'text-slate-500'}`}>
                        {delResult.deltas.risk_score_delta > 0 ? '+' : ''}{(delResult.deltas.risk_score_delta * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded border border-slate-200 text-center flex flex-col justify-center">
                      <p className="text-xs text-slate-500 uppercase mb-1">Risk Classification</p>
                      <div className="flex items-center gap-2 justify-center">
                         <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[10px] font-bold">{delResult.before.risk_label}</span>
                         <span className="text-slate-400 text-xs">➔</span>
                         <span className={`px-2 py-0.5 rounded text-[10px] font-bold text-white ${delResult.after.risk_label === 'HIGH' ? 'bg-red-500' : (delResult.after.risk_label === 'MEDIUM' ? 'bg-orange-500' : 'bg-emerald-500')}`}>{delResult.after.risk_label}</span>
                      </div>
                    </div>
                  </div>

                  <h5 className="font-bold mb-2">🛡️ Decision Delta: Do Nothing vs. Recommended Action</h5>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-red-50 border border-red-200 text-red-900 p-4 rounded text-sm">
                      <strong>❌ Do Nothing Scenario</strong>
                      <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                        <li>Shipment stuck in severe weather / congestion corridor.</li>
                        <li>On-time delivery SLA breach penalty applied.</li>
                      </ul>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded text-sm">
                      <strong>✅ Recommended Action (AI Decision)</strong>
                      <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                        <li>Reroute shipment via alternate regional bypass to circumvent bottlenecks.</li>
                        <li>Pre-notify receiving facility for dynamic cross-dock priority staging.</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-slate-400 italic">Configure scenario and run simulation to view results.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {simMode === 'logistics' && (
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">🗺️ Logistics Routing: Fleet Capacity & Vehicle Constraints</h2>
          <p className="text-slate-600 mb-6">Simulate how fleet availability and vehicle payload capacity affect route efficiency and fuel costs.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
              <h4 className="font-bold mb-4 border-b pb-2">Scenario Controls</h4>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Select Deliveries to Route</label>
                <select multiple value={logIds} onChange={e => {
                  const opts = Array.from(e.target.selectedOptions, option => option.value);
                  setLogIds(opts);
                }} className="w-full border-slate-300 rounded-md p-2 border h-32 text-sm">
                  {options.deliveries.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
                <p className="text-[10px] text-slate-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Available Delivery Vehicles ({numVehicles})</label>
                <input 
                  type="range" min="1" max="5" step="1" 
                  value={numVehicles} onChange={e => setNumVehicles(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-1">Vehicle Payload Capacity Multiplier ({capMult.toFixed(1)}x)</label>
                <input 
                  type="range" min="0.5" max="2.0" step="0.1" 
                  value={capMult} onChange={e => setCapMult(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <button onClick={runLogistics} className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded transition-colors">
                ⚡ Run Routing Simulation
              </button>
            </div>

            <div>
              <h4 className="font-bold mb-4">Projected Business Impact</h4>
              {logResult ? (
                <div>
                  {logResult.after.status !== 'Success' ? (
                    <div className="bg-orange-50 text-orange-800 p-4 rounded border border-orange-200">
                      ⚠️ <strong>Routing Constraint Alert:</strong> {logResult.after.status}. Fleet capacity is insufficient to deliver all assigned shipments. Increase vehicle count or payload multiplier.
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="bg-white p-4 rounded border border-slate-200 text-center">
                          <p className="text-xs text-slate-500 uppercase">Total Transit Distance</p>
                          <p className="text-xl font-bold">{logResult.after.total_distance_km.toFixed(0)} km</p>
                          <p className={`text-xs ${logResult.deltas.total_distance_delta > 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                            {logResult.deltas.total_distance_delta > 0 ? '+' : ''}{logResult.deltas.total_distance_delta.toFixed(0)} km
                          </p>
                        </div>
                        <div className="bg-white p-4 rounded border border-slate-200 text-center">
                          <p className="text-xs text-slate-500 uppercase">Estimated Route Cost</p>
                          <p className="text-xl font-bold">₹{logResult.after.total_cost.toLocaleString()}</p>
                          <p className={`text-xs ${logResult.deltas.total_cost_delta > 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                            {logResult.deltas.total_cost_delta > 0 ? '+' : ''}₹{logResult.deltas.total_cost_delta.toLocaleString()}
                          </p>
                        </div>
                        <div className="bg-white p-4 rounded border border-slate-200 text-center">
                          <p className="text-xs text-slate-500 uppercase">Dispatched Routes</p>
                          <p className="text-xl font-bold">{logResult.after.routes.length} vehicles</p>
                        </div>
                      </div>

                      <h5 className="font-bold mb-2 text-sm">Optimized Vehicle Allocations</h5>
                      <div className="bg-slate-50 p-4 rounded border border-slate-200 mb-6 text-sm">
                        {logResult.after.routes.map((r: any, i: number) => (
                          <div key={i} className="mb-2 last:mb-0">
                            <strong>Vehicle #{r.vehicle_id + 1}:</strong> {r.stops.map((s:any)=>s.delivery_id).join(' ➔ ')} <br/>
                            <span className="text-slate-500 text-xs">Distance: {r.route_distance_km} km | Load: {r.route_load} kg</span>
                          </div>
                        ))}
                      </div>

                      <h5 className="font-bold mb-2">🛡️ Decision Delta: Do Nothing vs. Recommended Action</h5>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-red-50 border border-red-200 text-red-900 p-4 rounded text-sm">
                          <strong>❌ Do Nothing (Fixed Dispatch)</strong>
                          <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                            <li>Underutilized vehicles run redundant cross-city mileage.</li>
                            <li>Overloaded vehicles risk safety compliance breach.</li>
                          </ul>
                        </div>
                        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded text-sm">
                          <strong>✅ Recommended Action (VRP Optimization)</strong>
                          <ul className="list-disc pl-4 mt-2 text-xs space-y-1">
                            <li>Re-cluster shipments into optimal density zones.</li>
                            <li>Minimize total fleet transit kilometers and expenses.</li>
                          </ul>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="text-slate-400 italic">Configure scenario and run simulation to view results.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
