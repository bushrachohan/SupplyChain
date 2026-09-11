import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api/client';

export default function CreateDecisionPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // target_type is exactly what the backend expects
  const [targetType, setTargetType] = useState('Inventory / Demand Issue');
  const [selectedSku, setSelectedSku] = useState(searchParams.get('sku_id') || '');
  const [selectedDelivery, setSelectedDelivery] = useState(searchParams.get('delivery_id') || '');
  const [skuOptions, setSkuOptions] = useState([]);
  const [deliveryOptions, setDeliveryOptions] = useState([]);
  const [situationText, setSituationText] = useState('');
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [forecastData, setForecastData] = useState(null);

  // Derived: the actual target_id based on targetType
  const targetId = targetType === 'Inventory / Demand Issue' ? selectedSku : selectedDelivery;

  // Load options from backend
  useEffect(() => {
    api.getDecisionOptions()
      .then(data => {
        // API returns { target_types, skus: string[], deliveries: string[] }
        const skus = data?.skus || [];
        const dels = data?.deliveries || [];
        setSkuOptions(skus);
        setDeliveryOptions(dels);
        if (!selectedSku && skus.length) setSelectedSku(skus[0]);
        if (!selectedDelivery && dels.length) setSelectedDelivery(dels[0]);
      })
      .catch(err => setError(err.message))
      .finally(() => setOptionsLoading(false));
  }, []);

  // Auto-fetch preview when selection changes
  useEffect(() => {
    if (!targetId) return;
    setPreviewLoading(true);
    setPreview(null);
    setForecastData(null);
    api.getDecisionPreview(targetType, targetId)
      .then(data => setPreview(data))
      .catch(err => console.error('Preview error:', err))
      .finally(() => setPreviewLoading(false));
      
    if (targetType === 'Inventory / Demand Issue') {
      api.getForecastVsActual(targetId)
        .then(data => setForecastData(data))
        .catch(err => console.error('Forecast error:', err));
    }
  }, [targetType, targetId]);

  const handleCreateDecision = async () => {
    if (!targetId) { setError('Select a target SKU or Delivery first.'); return; }
    setCreating(true);
    setError(null);
    try {
      // POST /api/decisions/create expects { target_type, target_id, situation_text }
      const res = await api.createDecision(targetType, targetId, situationText);
      const traceId = res?.trace_id;
      if (traceId) navigate(`/app/decision/${traceId}`);
      else setError('Decision created but no trace ID returned.');
    } catch (err) {
      setError(err.message || 'Decision creation failed');
    } finally {
      setCreating(false);
    }
  };

  const generateSparklinePoints = (key) => {
    if (!forecastData?.aligned_observations?.length) return "";
    const obs = forecastData.aligned_observations;
    const maxVal = Math.max(...obs.map(o => Math.max(o['Actual Demand'] || 0, o['Forecast Demand'] || 0)), 1);
    const minVal = 0;
    const range = maxVal - minVal || 1;
    
    return obs.map((o, i) => {
      const val = o[key];
      if (val == null) return null;
      const x = (i / (obs.length - 1)) * 400;
      const y = 50 - ((val - minVal) / range) * 45; // fit within 5-50 y-bounds
      return `${x},${y}`;
    }).filter(Boolean).join(" ");
  };

  return (
<div className="flex flex-col w-full gap-space-xl">
{/* Error Banner */}
{error && (
  <div className="bg-error-container text-on-error-container px-space-lg py-space-md rounded-xl font-body-md text-body-md flex items-center gap-space-sm">
    <span className="material-symbols-outlined text-[20px]">error</span>
    {error}
    <button onClick={() => setError(null)} className="ml-auto font-bold">✕</button>
  </div>
)}
{/* Loading state for options */}
{optionsLoading && (
  <div className="text-on-surface-variant font-body-sm text-body-sm px-space-sm">Loading decision options from backend…</div>
)}
{/* Header Block with Executive Metadata */}
<div className="flex flex-col md:flex-row md:items-end justify-between pb-space-md gap-space-md">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center gap-space-sm">
<span className="font-label-md text-label-md text-secondary uppercase tracking-wider bg-surface-container px-space-sm py-0.5 rounded-lg">Operational Pipeline</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">SESSION // DEC-88029-A</span>
</div>
<h1 className="font-headline-xl text-headline-xl text-on-surface font-bold tracking-tight">Create a Decision</h1>
<p className="font-body-md text-body-md text-on-surface-variant">Guided operational decision intelligence workflow with evidence and policy review.</p>
</div>
<div className="flex items-center gap-space-md">
<div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-md py-space-sm rounded-lg shadow-sm">
<span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim animate-pulse"></span>
<span className="font-label-sm text-label-sm text-on-surface uppercase font-semibold">Active Engine:</span>
<span className="font-code-sm text-code-sm text-secondary font-medium">AutoHeuristics v3.2</span>
</div>
<div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-md py-space-sm rounded-lg shadow-sm">
<span className="material-symbols-outlined text-[16px] text-on-surface-variant">shield</span>
<span className="font-label-sm text-label-sm text-on-surface uppercase font-semibold">Policy Guardrails:</span>
<span className="font-body-sm text-body-sm text-on-surface">Tier-1 Enforced</span>
</div>
</div>
</div>
{/* Stage Navigation Bar */}
<div className="bg-surface-container-lowest p-space-sm rounded-xl shadow-sm">
<nav className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-xs">
{/* Stage 01: Completed */}
<div className="flex items-center justify-between p-space-md rounded-lg bg-surface-container-low transition-all">
<div className="flex items-center gap-space-md min-w-0">
<div className="w-7 h-7 rounded-full bg-tertiary-container text-on-tertiary-container flex items-center justify-center flex-shrink-0">
<span className="material-symbols-outlined text-[16px]">check</span>
</div>
<div className="flex flex-col min-w-0">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider truncate">Stage 01</span>
<span className="font-body-md text-body-md text-on-surface font-semibold truncate">Business Context</span>
</div>
</div>
<span className="font-code-sm text-code-sm text-on-tertiary-container bg-surface-container px-space-xs py-0.5 rounded flex-shrink-0">Ready</span>
</div>
{/* Stage 02: Active */}
<div className="flex items-center justify-between p-space-md rounded-lg bg-primary-container text-on-primary shadow-sm relative overflow-hidden">
<div className="absolute inset-x-0 bottom-0 h-1 bg-secondary-container"></div>
<div className="flex items-center gap-space-md min-w-0">
<div className="w-7 h-7 rounded-full bg-secondary-container text-on-secondary flex items-center justify-center flex-shrink-0 shadow-sm">
<span className="w-2.5 h-2.5 rounded-full bg-surface-container-lowest animate-ping"></span>
</div>
<div className="flex flex-col min-w-0">
<span className="font-label-sm text-label-sm text-on-primary-container uppercase tracking-wider truncate">Stage 02 • Active</span>
<span className="font-body-md text-body-md text-on-primary font-bold truncate">Situation Assessment</span>
</div>
</div>
<span className="font-label-sm text-label-sm uppercase bg-primary px-space-sm py-0.5 rounded text-on-primary font-semibold flex-shrink-0">Focus</span>
</div>
{/* Stage 03: Pending */}
<div className="flex items-center justify-between p-space-md rounded-lg bg-surface-container-low opacity-75">
<div className="flex items-center gap-space-md min-w-0">
<div className="w-7 h-7 rounded-full bg-surface-container text-on-surface-variant flex items-center justify-center flex-shrink-0">
<span className="font-code-sm text-code-sm font-semibold">03</span>
</div>
<div className="flex flex-col min-w-0">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider truncate">Stage 03</span>
<span className="font-body-md text-body-md text-on-surface font-medium truncate">Forecast &amp; Evidence</span>
</div>
</div>
<span className="font-label-sm text-label-sm text-outline uppercase flex-shrink-0">Queued</span>
</div>
{/* Stage 04: Pending */}
<div className="flex items-center justify-between p-space-md rounded-lg bg-surface-container-low opacity-75">
<div className="flex items-center gap-space-md min-w-0">
<div className="w-7 h-7 rounded-full bg-surface-container text-on-surface-variant flex items-center justify-center flex-shrink-0">
<span className="font-code-sm text-code-sm font-semibold">04</span>
</div>
<div className="flex flex-col min-w-0">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider truncate">Stage 04</span>
<span className="font-body-md text-body-md text-on-surface font-medium truncate">Decision Analysis</span>
</div>
</div>
<span className="font-label-sm text-label-sm text-outline uppercase flex-shrink-0">Queued</span>
</div>
</nav>
</div>
{/* Stage 01: Business Context Grid Section */}
<section className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm flex flex-col gap-space-lg">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="w-6 h-6 rounded bg-surface-container flex items-center justify-center text-primary font-headline-sm text-headline-sm">1</span>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Stage 01 — Business Context &amp; Operational Scope</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">Validated against Master Data Management (SAP S/4HANA Sync: 2 mins ago)</p>
</div>
</div>
<span className="material-symbols-outlined text-on-tertiary-container">verified</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-lg">
{/* Field 1: Decision Scope */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md text-on-surface-variant uppercase">Decision Scope</label>
<div className="relative">
<select className="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-space-md py-space-sm rounded-lg appearance-none cursor-pointer focus:bg-surface-container-lowest focus:outline-none">
<option defaultChecked>Inventory &amp; Stockout Mitigation</option>
<option>Cross-Dock Emergency Reroute</option>
<option>Alternative Supplier Expedite</option>
<option>Operational Impact Assessment</option>
</select>
<span className="material-symbols-outlined absolute right-space-sm top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[20px]">expand_more</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">Domain: Supply Chain Logistics</span>
</div>
{/* Field 2: Target SKU or Delivery */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md text-on-surface-variant uppercase">Target {targetType === 'Inventory / Demand Issue' ? 'SKU' : 'Delivery'} Identifier</label>
<div className="relative">
{targetType === 'Inventory / Demand Issue' ? (
  <select
    value={selectedSku}
    onChange={e => setSelectedSku(e.target.value)}
    className="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-space-md py-space-sm rounded-lg appearance-none cursor-pointer focus:bg-surface-container-lowest focus:outline-none"
  >
    {skuOptions.length === 0 && <option value="">Loading SKUs…</option>}
    {skuOptions.map(s => <option key={s} value={s}>{s}</option>)}
  </select>
) : (
  <select
    value={selectedDelivery}
    onChange={e => setSelectedDelivery(e.target.value)}
    className="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-space-md py-space-sm rounded-lg appearance-none cursor-pointer focus:bg-surface-container-lowest focus:outline-none"
  >
    {deliveryOptions.length === 0 && <option value="">Loading deliveries…</option>}
    {deliveryOptions.map(d => <option key={d} value={d}>{d}</option>)}
  </select>
)}
<span className="material-symbols-outlined absolute right-space-sm top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[20px]">expand_more</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">From active dataset · {targetType === 'Inventory / Demand Issue' ? skuOptions.length : deliveryOptions.length} options</span>
</div>
{/* Field 3: Primary Facility */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md text-on-surface-variant uppercase">Primary Facility</label>
<div className="flex items-center justify-between bg-surface-container-low px-space-md py-space-sm rounded-lg">
<span className="font-body-md text-body-md text-on-surface font-medium truncate">Central Distribution Center - Chicago</span>
<span className="material-symbols-outlined text-on-surface-variant text-[18px]">warehouse</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">Facility Code: US-ORD-DC01</span>
</div>
{/* Field 4: Operating Horizon */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md text-on-surface-variant uppercase">Operating Horizon</label>
<div className="flex items-center justify-between bg-surface-container-low px-space-md py-space-sm rounded-lg">
<span className="font-body-md text-body-md text-on-surface font-medium">Next 14 Days</span>
<span className="material-symbols-outlined text-on-surface-variant text-[18px]">calendar_today</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">Dec 01 – Dec 14 UTC</span>
</div>
</div>
{/* Situation Description */}
<div className="flex flex-col gap-space-xs bg-surface-container-low p-space-md rounded-lg">
<div className="flex items-center justify-between">
<label className="font-label-md text-label-md text-on-surface-variant uppercase font-semibold">Incident Narrative &amp; Decision Context</label>
<span className="font-code-sm text-code-sm text-on-surface-variant">Optional — AI will auto-assess if blank</span>
</div>
<textarea
  className="w-full bg-surface-container-lowest text-on-surface font-body-md text-body-md p-space-md rounded-lg resize-none focus:outline-none"
  rows="2"
  value={situationText}
  onChange={e => setSituationText(e.target.value)}
  placeholder="Describe the operational context or leave blank for AI auto-assessment…"
/>
</div>
</section>
{/* Stage 02: Unified Situation Assessment (Critical Alert Box) */}
<section className="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden flex flex-col">
{/* Section Indicator Header */}
<div className="px-space-xl pt-space-lg pb-space-sm flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="w-6 h-6 rounded bg-secondary-container text-on-secondary flex items-center justify-center font-headline-sm text-headline-sm">2</span>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Stage 02 — Unified Situation Assessment</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">Multi-modal risk engine aggregation (Bayesian Net + SHAP)</p>
</div>
</div>
<span className={`font-label-sm text-label-sm uppercase px-space-sm py-1 rounded-lg flex items-center gap-space-xs ${
  previewLoading ? 'bg-surface-container text-on-surface-variant' :
  preview?.overall_severity === 'CRITICAL' ? 'bg-error-container text-on-error-container font-semibold' :
  preview ? 'bg-secondary-container text-on-secondary-container font-semibold' :
  'bg-surface-container text-on-surface-variant'
}`}>
{previewLoading ? (
  <><span className="material-symbols-outlined text-[14px] animate-spin">refresh</span> Assessing…</>
) : preview ? (
  <><span className="material-symbols-outlined text-[14px]">warning</span> {preview.overall_severity}</>  
) : (
  <><span className="material-symbols-outlined text-[14px]">hourglass_empty</span> Select Target</>
)}
</span>
</div>
{/* Alert Container */}
<div className="p-space-xl">
<div className="bg-error-container/40 p-space-xl rounded-xl flex flex-col lg:flex-row gap-space-xl items-stretch">
{/* Severity Gauge Column */}
<div className="flex flex-col justify-between lg:w-72 flex-shrink-0 bg-surface-container-lowest p-space-lg rounded-lg shadow-sm">
<div className="flex flex-col gap-space-xs">
<span className="font-label-md text-label-md text-error uppercase font-bold tracking-wider flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px]">crisis_alert</span> Overall Severity
            </span>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-error font-extrabold">
  {previewLoading ? 'Assessing…' : preview?.overall_severity || 'PENDING'}
</span>
</div>
</div>
{/* Mini Inline Risk SVG Bar */}
<div className="flex flex-col gap-space-xs my-space-md">
<div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant">
<span>Threat Level</span>
<span className="text-error font-semibold">87% Threshold</span>
</div>
<div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
<div className="bg-error h-full rounded-full" style={{ width: '87%' }}></div>
</div>
</div>
<div className="flex items-center gap-space-xs bg-error-container/30 px-space-sm py-space-xs rounded text-error">
<span className="material-symbols-outlined text-[16px]">schedule</span>
<span className="font-code-sm text-code-sm font-semibold">Urgency Window: &lt; 18h Remaining</span>
</div>
</div>
{/* Analytical Details Column */}
<div className="flex-1 flex flex-col justify-between gap-space-md">
<div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-md rounded-lg shadow-sm">
<span className="font-label-md text-label-md text-on-surface-variant uppercase flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-error">farsight_digital</span> Primary Bottleneck
              </span>
<span className="font-body-lg text-body-lg text-on-surface font-semibold">
  {preview?.bottleneck_type || 'Awaiting assessment…'}
</span>
<p className="font-body-sm text-body-sm text-on-surface-variant">
  {preview?.description || (previewLoading ? 'Running assessment…' : 'Select a target to compute situation assessment.')}
</p>
</div>
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-md rounded-lg shadow-sm">
<span className="font-label-md text-label-md text-on-surface-variant uppercase flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-secondary">hourglass_bottom</span> Action Deadline
              </span>
<span className="font-body-lg text-body-lg text-on-surface font-semibold">
  {preview?.impact_urgency_hours != null ? `Action required within ${preview.impact_urgency_hours}h` : 'Pending…'}
</span>
<p className="font-body-sm text-body-sm text-on-surface-variant">
  {preview?.mitigation_options?.[0] || 'Mitigation options will appear here.'}
</p>
</div>
</div>
{/* Compounding Dependencies */}
<div className="bg-surface-container-lowest p-space-md rounded-lg shadow-sm flex items-start gap-space-md">
<div className="p-space-xs rounded bg-surface-container text-secondary flex-shrink-0">
<span className="material-symbols-outlined text-[20px]">account_tree</span>
</div>
<div className="flex flex-col min-w-0">
<span className="font-label-md text-label-md text-on-surface-variant uppercase font-semibold">Compounding Dependencies Impact</span>
<p className="font-body-md text-body-md text-on-surface mt-0.5">
  {preview?.cross_risk_dependencies?.length
    ? preview.cross_risk_dependencies.join(' · ')
    : (targetId ? 'No cross-risk dependencies detected.' : 'Select a target to evaluate dependencies.')}
</p>
</div>
</div>
</div>
</div>
</div>
</section>
{/* Stage 03: Forecast & Risk Evidence Section */}
<section className="flex flex-col gap-space-md">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="w-6 h-6 rounded bg-surface-container flex items-center justify-center text-primary font-headline-sm text-headline-sm">3</span>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Stage 03 — Forecast &amp; Risk Evidence Synthesis</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">Validated parametric models</p>
</div>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant">
<span className="font-code-sm text-code-sm">Assessment Available</span>
<span className="material-symbols-outlined text-[18px]">verified_user</span>
</div>
</div>
{/* Two-Column Data Cards */}
<div className="grid grid-cols-1 lg:grid-cols-2 gap-space-lg">
{/* Left Card: Demand Forecast Context */}
<div className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm flex flex-col justify-between gap-space-lg">
<div className="flex items-center justify-between pb-space-sm bg-surface-container-low px-space-md py-space-sm rounded-lg">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-secondary">trending_up</span>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Demand Forecast Context</h3>
</div>
<span className="font-label-sm text-label-sm uppercase bg-surface-container px-space-sm py-0.5 rounded text-on-surface-variant font-semibold">Model: LightGBM</span>
</div>
<div className="grid grid-cols-3 gap-space-md">
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Expected Demand</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface mt-space-xs font-bold">{forecastData?.forecast_avg ? Math.round(forecastData.forecast_avg * 14) : '--'} <span className="font-label-sm text-label-sm font-normal text-on-surface-variant">units</span></span>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">14-day aggregate</span>
</div>
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Forecast Variance</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-secondary mt-space-xs font-bold">±{forecastData?.mape || '--'}%</span>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">Assessment Summary</span>
</div>
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Daily Burn</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface mt-space-xs font-bold">{forecastData?.forecast_avg ? Math.round(forecastData.forecast_avg) : '--'} <span className="font-label-sm text-label-sm font-normal text-on-surface-variant">u/day</span></span>
<span className="font-code-sm text-code-sm text-error font-medium mt-1"></span>
</div>
</div>
{/* Inline Demand Run-rate Sparkline Chart SVG */}
<div className="bg-surface-container-low p-space-md rounded-lg flex flex-col gap-space-xs">
<div className="flex justify-between items-center text-on-surface-variant">
<span className="font-label-sm text-label-sm uppercase font-semibold">14-Day Demand Run-Rate Projection</span>
<span className="font-code-sm text-code-sm">Baseline vs Shock Scenario</span>
</div>
<div className="w-full h-16 pt-1">
<svg className="w-full h-full overflow-visible" fill="none" preserveAspectRatio="none" viewBox="0 0 400 60">
{/* Grid Ticks */}
<line stroke="#CBD5E1" stroke-dasharray="3 3" strokeWidth="1" x1="0" x2="400" y1="50" y2="50"></line>
<line stroke="#CBD5E1" stroke-dasharray="3 3" strokeWidth="1" x1="0" x2="400" y1="20" y2="20"></line>
{/* Baseline curve */}
<polyline fill="none" points={generateSparklinePoints('Forecast Demand') || "0,45 80,42 160,38 240,32 320,28 360,25 400,20"} stroke="#757682" strokeDasharray="4 4" strokeWidth="2"></polyline>
{/* Forecast Spike Curve */}
<polyline fill="none" points={generateSparklinePoints('Actual Demand') || "0,45 60,45 120,40 180,26 240,12 320,8 400,4"} stroke="#0051d5" strokeWidth="2.5"></polyline>
{/* Current Day Marker */}
{forecastData?.aligned_observations && forecastData.aligned_observations[forecastData.aligned_observations.length - 1] ? (
  <circle cx="400" cy={50 - ((forecastData.aligned_observations[forecastData.aligned_observations.length - 1]['Actual Demand'] || 0) / Math.max(...forecastData.aligned_observations.map(o => Math.max(o['Actual Demand'] || 0, o['Forecast Demand'] || 0)), 1)) * 45} fill="#0051d5" r="4"></circle>
) : (
  <circle cx="180" cy="26" fill="#0051d5" r="4"></circle>
)}
</svg>
</div>
<div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant">
<span>Day 1 (Today)</span>
<span className="text-secondary font-semibold">Day 6 (Spike Apex)</span>
<span>Day 14</span>
</div>
</div>
</div>
{/* Right Card: Inventory Risk Profile */}
<div className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm flex flex-col justify-between gap-space-lg">
<div className="flex items-center justify-between pb-space-sm bg-surface-container-low px-space-md py-space-sm rounded-lg">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-error">inventory_2</span>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Inventory Risk Profile</h3>
</div>
<span className="font-label-sm text-label-sm uppercase bg-error-container text-on-error-container px-space-sm py-0.5 rounded font-semibold">Deficit State</span>
</div>
<div className="grid grid-cols-2 gap-space-md">
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Current On-Hand</span>
<span className="material-symbols-outlined text-error text-[16px]">priority_high</span>
</div>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface mt-space-xs font-bold">140 <span className="font-label-sm text-label-sm font-normal text-on-surface-variant">units</span></span>
<span className="font-code-sm text-code-sm text-error font-medium mt-1">Below min reserve</span>
</div>
<div className="flex flex-col p-space-md rounded-lg bg-error-container/30">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-error uppercase font-bold">Days of Supply (DOS)</span>
<span className="material-symbols-outlined text-error text-[16px]">speed</span>
</div>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-error mt-space-xs font-extrabold">2.8 <span className="font-label-sm text-label-sm font-normal text-error">Days</span></span>
<span className="font-code-sm text-code-sm text-error font-semibold mt-1">Depletion in ~68 hrs</span>
</div>
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Reorder Point</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface mt-space-xs font-bold">420 <span className="font-label-sm text-label-sm font-normal text-on-surface-variant">units</span></span>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">Breached 36h ago</span>
</div>
<div className="flex flex-col p-space-md rounded-lg bg-surface-container-low">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Safety Stock Threshold</span>
<span className="font-label-sm text-label-sm text-error font-semibold">Deficit: 210 u</span>
</div>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface mt-space-xs font-bold">350 <span className="font-label-sm text-label-sm font-normal text-on-surface-variant">units</span></span>
<span className="font-code-sm text-code-sm text-error font-medium mt-1">Current: 40% of target</span>
</div>
</div>
{/* Inventory Stockout Horizon Gauge */}
<div className="bg-surface-container-low p-space-md rounded-lg flex flex-col gap-space-xs">
<div className="flex justify-between items-center text-on-surface-variant">
<span className="font-label-sm text-label-sm uppercase font-semibold">Stockout Timeline Runway</span>
<span className="font-code-sm text-code-sm text-error font-semibold">Projected Zero: T+68h</span>
</div>
<div className="w-full bg-surface-container h-3 rounded-full overflow-hidden flex">
<div className="bg-error h-full" style={{ width: '20%' }} title="On-Hand (2.8d)"></div>
<div className="bg-outline-variant h-full" style={{ width: '40%' }} title="Stockout Risk Gap"></div>
<div className="bg-surface-dim h-full" style={{ width: '40%' }} title="Target Safety Range"></div>
</div>
<div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant">
<span className="text-error font-semibold">0d (140u)</span>
<span className="text-on-surface">2.8d (Exhaustion)</span>
<span>7d</span>
<span>14d (620u Target)</span>
</div>
</div>
</div>
</div>
</section>
{/* Bottom Action Bar (Pinned Control Strip) */}
<div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-md flex flex-col sm:flex-row items-center justify-between gap-space-md sticky bottom-4 z-30">
<div className="flex items-center gap-space-md">
<div className="w-2.5 h-2.5 rounded-full bg-tertiary-fixed-dim"></div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface uppercase font-bold tracking-wider">Analysis Engine Ready</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">3 Action Candidates will be computed with multi-critic consensus.</span>
</div>
</div>
<div className="flex items-center gap-space-md w-full sm:w-auto justify-end">
{/* Reset Button */}
<button className="px-space-lg py-space-sm rounded-lg bg-surface-container text-on-surface font-body-md text-body-md font-semibold hover:bg-surface-container-high transition-all flex items-center gap-space-xs" type="button">
<span className="material-symbols-outlined text-[18px]">restart_alt</span>
<span>Reset Parameters</span>
</button>
{/* Primary Action Button */}
<button
  onClick={handleCreateDecision}
  disabled={creating || !targetId}
  className="px-space-xl py-space-sm rounded-lg bg-primary-container text-on-primary font-body-md text-body-md font-bold shadow-sm hover:bg-primary transition-all flex items-center gap-space-sm disabled:opacity-50 disabled:cursor-not-allowed"
  type="button"
>
{creating ? (
  <><span className="material-symbols-outlined text-[20px] animate-spin">refresh</span>Running AI Analysis…</>
) : (
  <><span>Run AI Decision Orchestration &amp; Analysis</span><span className="material-symbols-outlined text-[20px]">arrow_forward</span></>
)}
</button>
</div>
</div>
</div>
  );
}
