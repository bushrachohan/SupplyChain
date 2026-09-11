import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function SimulationPage() {
  const [simType, setSimType] = useState('inventory');
  const [params, setParams] = useState({
    sku_id: 'SKU_104',
    demand_multiplier: 1.35,
    stock_override: 260,
    lead_time_override: 4,
  });
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  const handleRunSimulation = async () => {
    setRunning(true);
    setError(null);
    try {
      let res;
      if (simType === 'inventory') {
        res = await api.simulateInventory(params);
      } else if (simType === 'delivery') {
        res = await api.simulateDelivery(params);
      } else {
        res = await api.simulateLogistics(params);
      }
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
<div className="flex flex-col w-full">
<div className="flex flex-col gap-space-xs pb-space-lg">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="font-code-sm text-code-sm text-on-surface-variant uppercase tracking-wider">SIM-ID: 2024-SIM-8821</span>
<span className="text-outline-variant">/</span>
<span className="font-label-sm text-label-sm bg-surface-container px-space-xs py-0.5 rounded text-primary font-semibold">Scenario Engine v1.0</span>
</div>
<div className="flex items-center gap-space-sm">
<span className="font-label-sm text-label-sm text-on-surface-variant">Last Compute: Today, 14:22:08 UTC</span>
<div className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></div>
</div>
</div>
<div className="flex flex-col">
<h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight">What-If Scenario Simulation</h1>
<p className="font-body-md text-body-md text-on-surface-variant mt-0.5">Test operational interventions across inventory buffers, transit disruptions, and logistics fleet allocation before committing real decisions.</p>
</div>
</div>
{/* Domain Navigation Tabs */}
<div className="flex border-b border-outline-variant/30 mb-space-xl">
<button className="flex items-center gap-space-sm px-space-lg py-space-md border-b-2 border-primary text-primary font-body-md text-body-md font-semibold -mb-px transition-all">
<span className="material-symbols-outlined text-[18px]">inventory_2</span>
<span>Inventory Risk &amp; Stockout</span>
<span className="font-label-sm text-label-sm bg-primary-container text-on-primary px-1.5 py-0.5 rounded-full">Active Mode</span>
</button>
<button className="flex items-center gap-space-sm px-space-lg py-space-md text-on-surface-variant hover:text-on-surface font-body-md text-body-md transition-all">
<span className="material-symbols-outlined text-[18px]">local_shipping</span>
<span>Delivery Risk &amp; Transit Delay</span>
<span className="font-label-sm text-label-sm bg-surface-container text-on-surface-variant px-1.5 py-0.5 rounded-full">Queue: 4</span>
</button>
<button className="flex items-center gap-space-sm px-space-lg py-space-md text-on-surface-variant hover:text-on-surface font-body-md text-body-md transition-all">
<span className="material-symbols-outlined text-[18px]">alt_route</span>
<span>Logistics Fleet &amp; Routing Capacity</span>
<span className="font-label-sm text-label-sm bg-surface-container text-on-surface-variant px-1.5 py-0.5 rounded-full">Queue: 1</span>
</button>
</div>
{/* Main Simulator Workbench (Domain 1) */}
<div className="grid grid-cols-12 gap-gutter-desktop mb-space-xl">
{/* LEFT COLUMN: Parameter Overrides */}
<div className="col-span-12 lg:col-span-5 flex flex-col gap-space-lg">
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-lg flex flex-col shadow-sm">
<div className="flex items-center justify-between border-b border-outline-variant/20 pb-space-md mb-space-lg">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-primary text-[20px]">tune</span>
<span className="font-headline-sm text-headline-sm text-on-surface">Scenario Overrides</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant bg-surface-container-low px-space-xs py-0.5 rounded">Scenario Analysis</span>
</div>
<form className="flex flex-col gap-space-lg" onSubmit={(e) => e.preventDefault()}>
{/* Target SKU Selector */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md text-on-surface uppercase tracking-wider flex items-center justify-between">
<span>Target SKU Node</span>
<span className="text-on-surface-variant font-normal">DC Code: ORD-04</span>
</label>
<div className="relative">
<select 
  value={params.sku_id} 
  onChange={(e) => setParams({...params, sku_id: e.target.value})} 
  className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded-lg py-space-sm px-space-md font-body-md text-body-md text-on-surface appearance-none focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary">
<option value="SKU_104">SKU_104 (Micro-controller Chipset — Chicago DC)</option>
<option value="SKU_208">SKU_208 (Lithium Cell Module — Dallas Hub)</option>
<option value="SKU_312">SKU_312 (Fiber Optic Transceiver — Newark DC)</option>
</select>
<span className="material-symbols-outlined absolute right-space-md top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant text-[18px]">unfold_more</span>
</div>
<p className="font-code-sm text-code-sm text-on-surface-variant">Active Consumption Rate: 50.0 units/day | SLA Buffer Target: &gt;5.0 days</p>
</div>
{/* Demand Surge Multiplier Slider */}
<div className="flex flex-col gap-space-xs bg-surface-container-low/60 p-space-md rounded-lg border border-outline-variant/20">
<div className="flex items-center justify-between">
<label className="font-label-md text-label-md text-on-surface uppercase tracking-wider">Demand Surge Multiplier</label>
<span className="font-tabular-metric-md text-tabular-metric-md text-primary font-bold">{params.demand_multiplier}x</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">+{(params.demand_multiplier - 1) * 100}% spike over 30-day baseline historical burn</p>
<input 
  className="w-full h-1.5 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary mt-space-xs" 
  max="2.50" min="1.00" step="0.05" type="range" 
  value={params.demand_multiplier}
  onChange={(e) => setParams({...params, demand_multiplier: parseFloat(e.target.value)})}
/>
<div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant">
<span>1.00x (Baseline)</span>
<span>1.50x</span>
<span>2.00x</span>
<span>2.50x (Severe)</span>
</div>
</div>
{/* Current On-Hand Stock Override */}
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<label className="font-label-md text-label-md text-on-surface uppercase tracking-wider">On-Hand Stock Override</label>
<span className="font-code-sm text-code-sm text-on-surface-variant">Baseline: 140 units</span>
</div>
<div className="flex items-center gap-space-sm">
<div className="flex-1 flex items-center border border-outline-variant/40 rounded-lg overflow-hidden bg-surface-container-lowest">
<button onClick={() => setParams({...params, stock_override: Math.max(0, params.stock_override - 10)})} className="px-space-md py-space-sm text-on-surface hover:bg-surface-container transition-colors text-headline-sm" type="button">−</button>
<input 
  className="w-full text-center py-space-sm font-tabular-metric-md text-tabular-metric-md font-semibold text-on-surface bg-transparent focus:outline-none" 
  type="number" 
  value={params.stock_override}
  onChange={(e) => setParams({...params, stock_override: parseInt(e.target.value) || 0})}
/>
<button onClick={() => setParams({...params, stock_override: params.stock_override + 10})} className="px-space-md py-space-sm text-on-surface hover:bg-surface-container transition-colors text-headline-sm" type="button">+</button>
</div>
<span className="font-body-sm text-body-sm text-on-surface font-medium whitespace-nowrap">Tested Units</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">Simulating temporary cross-dock replenishment injection.</p>
</div>
{/* Lead Time Drift Override */}
<div className="flex flex-col gap-space-xs bg-surface-container-low/60 p-space-md rounded-lg border border-outline-variant/20">
<div className="flex items-center justify-between">
<label className="font-label-md text-label-md text-on-surface uppercase tracking-wider">Inbound Lead Time Drift</label>
<span className="font-tabular-metric-md text-tabular-metric-md text-error font-semibold">+{params.lead_time_override} Days</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">Calculated Total Lead Window: {6 + params.lead_time_override} Days (Baseline: 6 Days)</p>
<input 
  className="w-full h-1.5 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary mt-space-xs" 
  max="14" min="0" step="1" type="range" 
  value={params.lead_time_override}
  onChange={(e) => setParams({...params, lead_time_override: parseInt(e.target.value)})}
/>
<div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant">
<span>+0d (Nominal)</span>
<span>+4d</span>
<span>+8d</span>
<span>+14d (Port Congestion)</span>
</div>
</div>
{/* Parameter Summary Matrix */}
<div className="bg-surface-container-low border border-outline-variant/20 rounded-lg p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center text-body-sm">
<span className="text-on-surface-variant">Assumed Daily Consumption</span>
<span className="font-code-sm text-code-sm font-semibold text-on-surface">67.5 units/day</span>
</div>
<div className="flex justify-between items-center text-body-sm">
<span className="text-on-surface-variant">Inbound Pipeline In-Transit</span>
<span className="font-code-sm text-code-sm font-semibold text-on-surface">300 units (PO-88192)</span>
</div>
</div>
{/* Action Buttons */}
<div className="flex items-center gap-space-md pt-space-xs">
<button onClick={handleRunSimulation} className="flex-1 bg-primary text-on-primary hover:bg-primary-container px-space-md py-space-sm rounded-lg font-body-md text-body-md font-semibold flex items-center justify-center gap-space-sm transition-all shadow-sm" type="button">
<span className="material-symbols-outlined text-[18px]">{running ? 'refresh' : 'play_arrow'}</span>
<span>{running ? 'Running Simulation...' : 'Run Scenario Simulation'}</span>
</button>
<button className="bg-surface-container-lowest border border-outline-variant/40 hover:bg-surface-container-low text-on-surface px-space-md py-space-sm rounded-lg font-body-md text-body-md font-medium flex items-center gap-space-xs transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">restart_alt</span>
<span>Reset</span>
</button>
</div>
</form>
</div>
{/* Seed & Constraint Diagnostic Pill */}
<div className="border border-outline-variant/20 rounded-lg p-space-md bg-surface-container-lowest flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-outline text-[18px]">verified_user</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Deterministic Mode: Enabled</span>
</div>
<span className="font-label-sm text-label-sm text-on-tertiary-container bg-tertiary-fixed/30 px-space-xs py-0.5 rounded font-medium">Scenario Assessment</span>
</div>
</div>
{/* RIGHT COLUMN: Simulation Results & Impact Delta */}
<div className="col-span-12 lg:col-span-7 flex flex-col gap-space-lg">
{/* Status Delta Banner */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-md flex items-center justify-between shadow-sm">
<div className="flex items-center gap-space-md">
<div className="w-8 h-8 rounded-lg bg-tertiary-fixed/40 flex items-center justify-center text-on-tertiary-fixed-variant">
<span className="material-symbols-outlined text-[20px]">verified</span>
</div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">DECISION DELTA STATUS</span>
<div className="flex items-center gap-space-sm">
<span className="font-headline-sm text-headline-sm text-error line-through decoration-1 opacity-70">{result ? result.before?.risk_level : 'HIGH RISK'}</span>
<span className="material-symbols-outlined text-[16px] text-on-surface-variant">arrow_forward</span>
<span className="font-headline-sm text-headline-sm text-tertiary font-bold">{result ? result.after?.risk_level : 'MITIGATED'}</span>
</div>
</div>
</div>
<div className="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container-low rounded border border-outline-variant/20">
<span className="font-label-md text-label-md text-on-surface font-semibold">Run Mode:</span>
<span className="font-code-sm text-code-sm text-primary font-bold">What-If Scenario</span>
</div>
</div>
{/* Before vs. Scenario Comparative Metric Grid */}
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
{/* Metric 1: Days of Supply */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-md flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Days of Supply (DOS)</span>
<span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></span>
</div>
<div className="flex items-baseline gap-space-xs my-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{result ? result.after?.days_of_supply?.toFixed(1) : '5.4'}</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Days</span>
</div>
<div className="flex flex-col gap-0.5 border-t border-outline-variant/20 pt-space-xs mt-space-xs">
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Baseline:</span>
<span className="text-error font-medium">{result ? result.before?.days_of_supply?.toFixed(1) : '2.8'} Days</span>
</div>
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Threshold:</span>
<span className="text-on-surface">5.0d Safe Line</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm font-semibold text-tertiary mt-0.5">
<span>Net Delta:</span>
<span>{result ? (result.deltas?.days_of_supply_delta > 0 ? '▲ +' : '▼ ') + result.deltas?.days_of_supply_delta?.toFixed(1) + ' Days' : '▲ +2.6 Days'}</span>
</div>
</div>
</div>
{/* Metric 2: Stockout Probability */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-md flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Stockout Risk Prob.</span>
<span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></span>
</div>
<div className="flex items-baseline gap-space-xs my-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{result ? Math.round(result.after?.stockout_probability * 100) : '18'}%</span>
<span className="font-body-sm text-body-sm text-tertiary font-semibold">{result ? (result.after?.stockout_probability < 0.2 ? 'Low Risk' : 'High Risk') : 'Low Risk'}</span>
</div>
<div className="flex flex-col gap-0.5 border-t border-outline-variant/20 pt-space-xs mt-space-xs">
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Baseline:</span>
<span className="text-error font-medium">{result ? Math.round(result.before?.stockout_probability * 100) : '87'}%</span>
</div>
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Target SLA:</span>
<span className="text-on-surface">&lt; 20%</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm font-semibold text-tertiary mt-0.5">
<span>Net Delta:</span>
<span>{result ? (result.deltas?.stockout_probability_delta > 0 ? '▲ +' : '▼ ') + Math.round(result.deltas?.stockout_probability_delta * 100) + '%' : '▼ -69% Risk'}</span>
</div>
</div>
</div>
{/* Metric 3: Reorder Point Req */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-md flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Reorder Requirement</span>
<span className="w-2 h-2 rounded-full bg-secondary-container"></span>
</div>
<div className="flex items-baseline gap-space-xs my-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{result ? Math.round(result.after?.reorder_point_units) : '560'}</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Units</span>
</div>
<div className="flex flex-col gap-0.5 border-t border-outline-variant/20 pt-space-xs mt-space-xs">
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Baseline:</span>
<span className="text-on-surface">{result ? Math.round(result.before?.reorder_point_units) : '420'} Units</span>
</div>
<div className="flex justify-between font-code-sm text-code-sm">
<span className="text-on-surface-variant">Drift Offset:</span>
<span className="text-on-surface">+{params.lead_time_override}d Vendor Drift</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm font-semibold text-primary mt-0.5">
<span>Net Delta:</span>
<span>{result ? (result.deltas?.reorder_point_delta > 0 ? '▲ +' : '▼ ') + Math.round(result.deltas?.reorder_point_delta) + ' Units' : '▲ +140 Units Buffer'}</span>
</div>
</div>
</div>
</div>
{/* Comparative Run-Rate Chart / Vector Visualization */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-lg flex flex-col shadow-sm">
<div className="flex items-center justify-between border-b border-outline-variant/20 pb-space-sm mb-space-md">
<div className="flex flex-col">
<span className="font-headline-sm text-headline-sm text-on-surface">14-Day Trajectory Projection</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Depletion vs Replenishment Velocity</span>
</div>
<div className="flex items-center gap-space-lg">
<div className="flex items-center gap-space-xs">
<span className="w-3 h-0.5 border-t-2 border-dashed border-error"></span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Baseline (Depletes D3)</span>
</div>
<div className="flex items-center gap-space-xs">
<span className="w-3 h-1 bg-primary rounded-full"></span>
<span className="font-label-sm text-label-sm text-primary font-semibold">Simulated Scenario</span>
</div>
</div>
</div>
{/* Inline SVG Visualization */}
<div className="relative w-full h-56 bg-surface-container-low/40 rounded-lg p-space-sm border border-outline-variant/20">
<svg className="w-full h-full" fill="none" viewBox="0 0 700 200" xmlns="http://www.w3.org/2000/svg">
{/* Grid Lines */}
<line stroke="#c5c5d3" stroke-dasharray="2 2" stroke-opacity="0.3" x1="40" x2="680" y1="20" y2="20"></line>
<line stroke="#c5c5d3" stroke-dasharray="2 2" stroke-opacity="0.3" x1="40" x2="680" y1="60" y2="60"></line>
<line stroke="#c5c5d3" stroke-dasharray="2 2" stroke-opacity="0.3" x1="40" x2="680" y1="100" y2="100"></line>
<line stroke="#c5c5d3" stroke-dasharray="2 2" stroke-opacity="0.3" x1="40" x2="680" y1="140" y2="140"></line>
<line stroke="#757682" strokeWidth="1.2" x1="40" x2="680" y1="175" y2="175"></line>
{/* Zero Stockout Horizon Shading */}
<rect fill="#ffdad6" fill-opacity="0.3" height="20" width="640" x="40" y="174"></rect>
<text className="font-code-sm" fill="#ba1a1a" font-size="10" text-anchor="end" x="675" y="170">CRITICAL STOCKOUT LEVEL (0 Units)</text>
{/* Safe Buffer Line (100 units = Y=115) */}
<line stroke="#004a32" stroke-dasharray="4 4" stroke-opacity="0.5" strokeWidth="1" x1="40" x2="680" y1="115" y2="115"></line>
<text className="font-code-sm" fill="#004a32" font-size="9" x="45" y="110">Safety Buffer Threshold: 100u</text>
{/* Line A (Dotted Red): Baseline Depletion Curve reaching 0 at Day 3 (approx X=180) */}
<path d="M 50 85 L 115 130 L 180 175 L 245 175 L 310 175 L 375 175 L 440 175 L 505 175 L 570 175 L 635 175" fill="none" stroke="#ba1a1a" stroke-dasharray="5 5" strokeWidth="2"></path>
<circle cx="180" cy="175" fill="#ba1a1a" r="4"></circle>
<text fill="#ba1a1a" font-size="10" font-weight="600" text-anchor="middle" x="180" y="165">Day 3: Stockout</text>
{/* Line B (Solid Blue): Simulated Scenario Trajectory with cross-dock injection and stabilizing at 120u */}
{/* Day 0: 260 units (Y=30), Day 2: 125u, Day 4 (PO arrival): jumps to 240u, then tapers to 120u stable */}
<path d="M 50 35 L 115 75 L 180 110 L 245 95 L 310 40 L 375 65 L 440 85 L 505 105 L 570 110 L 635 112" fill="none" stroke="#00236f" strokeLinecap="round" strokeWidth="2.5"></path>
{/* Nodes on Simulated Path */}
<circle cx="50" cy="35" fill="#00236f" r="3.5"></circle>
<circle cx="310" cy="40" fill="#00236f" r="3.5"></circle>
<circle cx="635" cy="112" fill="#004a32" r="4"></circle>
{/* Label for stabilizing point */}
<rect fill="#ffffff" height="20" rx="4" stroke="#c5c5d3" strokeWidth="1" width="130" x="540" y="85"></rect>
<text fill="#00236f" font-size="9.5" font-weight="600" text-anchor="middle" x="605" y="98">Stabilized ~120 Units</text>
{/* Inbound PO marker */}
<line stroke="#0051d5" stroke-dasharray="2 2" stroke-opacity="0.4" strokeWidth="1" x1="310" x2="310" y1="40" y2="175"></line>
<text fill="#0051d5" font-size="9" x="315" y="55">Day 6 (+4d drift arrival)</text>
{/* X Axis Days */}
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="50" y="192">D0</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="115" y="192">D2</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="180" y="192">D4</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="245" y="192">D6</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="310" y="192">D8</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="375" y="192">D10</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="440" y="192">D12</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="505" y="192">D14</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="570" y="192">D16</text>
<text className="font-code-sm" fill="#757682" font-size="10" text-anchor="middle" x="635" y="192">D18</text>
</svg>
</div>
<div className="flex items-center justify-between pt-space-md mt-space-xs text-on-surface-variant font-code-sm text-code-sm">
<span>*Calculated using expected variance</span>
<span className="text-primary font-medium">Forecast Range</span>
</div>
</div>
{/* Triggered System Recommendation Card */}
<div className="bg-surface-container-low border border-outline-variant/30 rounded-lg p-space-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-space-lg">
<div className="flex items-start gap-space-md">
<div className="w-9 h-9 rounded-lg bg-primary text-on-primary flex items-center justify-center shrink-0 mt-0.5">
<span className="material-symbols-outlined text-[20px]">smart_toy</span>
</div>
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="font-label-md text-label-md text-primary font-bold uppercase tracking-wide">Sentinel System Recommendation</span>
<span className="font-label-sm text-label-sm bg-surface-container-highest px-1.5 py-0.5 rounded text-on-surface">Policy RAG Match</span>
</div>
<p className="font-body-md text-body-md text-on-surface mt-0.5 font-medium">
              Expedite 300 units via Air Charter to offset supplier lead-time drift.
            </p>
<p className="font-body-sm text-body-sm text-on-surface-variant">
              Estimated cost impact: +$4,200 | Estimated exposure avoided: $38,500. Meets configured policy constraints.
            </p>
</div>
</div>
<button className="w-full md:w-auto shrink-0 bg-primary text-on-primary hover:bg-primary-container px-space-lg py-space-sm rounded-lg font-body-md text-body-md font-semibold flex items-center justify-center gap-space-sm transition-all shadow-sm" type="button">
<span>Send Scenario to Decision Workflow</span>
<span className="material-symbols-outlined text-[18px]">arrow_forward</span>
</button>
</div>
</div>
</div>
{/* Domain Previews Section */}
<div className="flex flex-col gap-space-md mt-space-sm">
<div className="flex items-center justify-between border-b border-outline-variant/20 pb-space-xs">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-outline text-[18px]">alt_route</span>
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Other Simulation Capabilities (Idle Workbenches)</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">Switch active domain above to configure</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 gap-gutter-desktop">
{/* Domain 2 Preview: Delivery Risk & Transit Delay */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-lg flex flex-col justify-between hover:border-outline-variant transition-colors shadow-sm">
<div className="flex flex-col gap-space-md">
<div className="flex items-center justify-between border-b border-outline-variant/20 pb-space-sm">
<div className="flex items-center gap-space-sm">
<div className="w-7 h-7 rounded bg-surface-container flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[18px]">local_shipping</span>
</div>
<span className="font-headline-sm text-headline-sm text-on-surface">Delivery Risk &amp; Transit Delay</span>
</div>
<span className="font-label-sm text-label-sm bg-surface-container px-space-xs py-0.5 rounded text-on-surface-variant font-medium">Domain 02</span>
</div>
{/* Mini Scenario Setup Preview */}
<div className="grid grid-cols-2 gap-space-md font-body-sm text-body-sm">
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Target Delivery ID</span>
<span className="font-code-sm text-code-sm text-on-surface font-semibold mt-0.5">SHP-902-TRUCK-88</span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">Route: Detroit → Chicago</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Weather Condition</span>
<span className="font-body-sm text-body-sm text-on-surface font-medium mt-0.5 flex items-center gap-1">
<span className="material-symbols-outlined text-[16px] text-primary">ac_unit</span> Winter Gale (+3h)
              </span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">I-94 Corridor Warning</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Simulated Traffic Delay</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-error font-semibold mt-0.5">+4.5 Hours</span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">Total Transit: 11.2 hrs</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Late Probability Output</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-error font-bold mt-0.5">74.2%</span>
<span className="font-label-sm text-label-sm text-error font-medium mt-1">SLA Breach Expected</span>
</div>
</div>
</div>
<div className="flex items-center justify-between pt-space-md mt-space-sm border-t border-outline-variant/20">
<span className="font-code-sm text-code-sm text-on-surface-variant">Recommended Action: Re-dispatch via Carrier B</span>
<button className="text-primary font-body-sm text-body-sm font-semibold flex items-center gap-0.5 hover:underline" type="button">
<span>Open Simulator</span>
<span className="material-symbols-outlined text-[16px]">chevron_right</span>
</button>
</div>
</div>
{/* Domain 3 Preview: Logistics Fleet & Routing Capacity */}
<div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-space-lg flex flex-col justify-between hover:border-outline-variant transition-colors shadow-sm">
<div className="flex flex-col gap-space-md">
<div className="flex items-center justify-between border-b border-outline-variant/20 pb-space-sm">
<div className="flex items-center gap-space-sm">
<div className="w-7 h-7 rounded bg-surface-container flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[18px]">forklift</span>
</div>
<span className="font-headline-sm text-headline-sm text-on-surface">Logistics Fleet &amp; Routing Capacity</span>
</div>
<span className="font-label-sm text-label-sm bg-surface-container px-space-xs py-0.5 rounded text-on-surface-variant font-medium">Domain 03</span>
</div>
{/* Mini Scenario Setup Preview */}
<div className="grid grid-cols-2 gap-space-md font-body-sm text-body-sm">
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Deliveries to Route</span>
<span className="font-code-sm text-code-sm text-on-surface font-semibold mt-0.5">42 Dispatches / 6 Hubs</span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">Total Weight: 18.4 tons</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Available Fleet Units</span>
<span className="font-body-sm text-body-sm text-on-surface font-medium mt-0.5 flex items-center gap-1">
<span className="material-symbols-outlined text-[16px] text-tertiary">local_shipping</span> 8 Heavy / 4 Light
              </span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">2 Vehicles in Maintenance</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Payload Capacity Multiplier</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-primary font-semibold mt-0.5">0.90x (Volume Limit)</span>
<span className="text-on-surface-variant font-code-sm text-code-sm mt-1">Density Bottleneck</span>
</div>
<div className="flex flex-col p-space-sm bg-surface-container-low rounded border border-outline-variant/20">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">Simulated Route Cost Delta</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-tertiary font-bold mt-0.5">-$2,140 (-8.4%)</span>
<span className="font-label-sm text-label-sm text-tertiary font-medium mt-1">Dynamic Clustering Gain</span>
</div>
</div>
</div>
<div className="flex items-center justify-between pt-space-md mt-space-sm border-t border-outline-variant/20">
<span className="font-code-sm text-code-sm text-on-surface-variant">Recommended Action: Dynamic Cluster Optimization</span>
<button className="text-primary font-body-sm text-body-sm font-semibold flex items-center gap-0.5 hover:underline" type="button">
<span>Open Simulator</span>
<span className="material-symbols-outlined text-[16px]">chevron_right</span>
</button>
</div>
</div>
</div>
</div>
</div>
  );
}
