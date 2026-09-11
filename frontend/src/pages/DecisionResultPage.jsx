import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';

export default function DecisionResultPage() {
  const navigate = useNavigate();
  const { traceId } = useParams();
  const [trace, setTrace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState(null);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (!traceId) return;
    api.getTrace(traceId)
      .then(data => setTrace(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [traceId]);

  const handleApproval = async (decision) => {
    setApproving(true);
    try {
      await api.submitApproval(traceId, decision, 'Ops Lead', notes || undefined);
      navigate('/app/approval-queue');
    } catch (err) {
      setError(err.message);
    } finally {
      setApproving(false);
    }
  };

  return (
<div className="flex flex-col w-full gap-space-lg">
{/* Top Navigation Context & Status Track */}
<div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md pb-space-xs">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center gap-space-sm">
<a className="font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1" data-path="decision-history" href="#">
<span className="material-symbols-outlined text-[14px]">arrow_back</span>
<span>EVALUATION ARCHIVE</span>
</a>
<span className="text-outline-variant font-label-sm text-label-sm">/</span>
<span className="font-code-sm text-code-sm uppercase tracking-wider text-secondary font-medium">SESSION ID: DS-2024-10-88029-A</span>
</div>
<div className="flex items-center gap-space-sm flex-wrap">
<h1 className="font-headline-lg text-headline-lg text-on-surface font-semibold tracking-tight">
          Operational Decision Result <span className="text-on-surface-variant font-normal">// {traceId || 'DEC-88029-A'}</span>
</h1>
<span className="font-code-sm text-code-sm bg-surface-container px-space-xs py-0.5 rounded text-on-surface font-medium">{trace?.target_id || 'SKU_104'} Stockout Mitigation</span>
</div>
</div>
{/* Live Consensus & Action Tier Badges */}
<div className="flex items-center gap-space-sm flex-wrap">
<div className="flex items-center gap-space-xs bg-tertiary-container text-on-tertiary px-space-md py-1.5 rounded-lg shadow-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed">verified</span>
<span className="font-label-md text-label-md tracking-wide">Consensus Reached</span>
</div>
<div className="flex items-center gap-space-xs bg-surface-container-high text-on-surface px-space-md py-1.5 rounded-lg border border-outline-variant/30">
<span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
<span className="font-label-md text-label-md uppercase tracking-wide">Tier-1 Human Approval Required</span>
</div>
</div>
</div>
{/* Multi-Stage Decision Pipeline Visualizer */}
<div className="w-full bg-surface-container-lowest rounded-xl p-space-md shadow-sm border border-outline-variant/30 flex flex-col md:flex-row items-center justify-between gap-space-md">
<div className="flex items-center gap-space-xs text-on-surface-variant">
<span className="material-symbols-outlined text-[18px]">account_tree</span>
<span className="font-label-md text-label-md uppercase tracking-wider font-semibold">Audit Verification Flow:</span>
</div>
<div className="flex items-center gap-space-xs md:gap-space-sm flex-wrap w-full md:w-auto justify-start md:justify-end">
{/* Step 1 */}
<div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-1 rounded border border-outline-variant/40 text-on-surface">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">check_circle</span>
<span className="font-label-sm text-label-sm font-semibold">1. Primary AI (LightGBM)</span>
</div>
<span className="material-symbols-outlined text-outline-variant text-[16px]">arrow_forward</span>
{/* Step 2 */}
<div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-1 rounded border border-outline-variant/40 text-on-surface">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">gavel</span>
<span className="font-label-sm text-label-sm font-semibold">2. Policy Critic</span>
</div>
<span className="material-symbols-outlined text-outline-variant text-[16px]">arrow_forward</span>
{/* Step 3 */}
<div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-1 rounded border border-outline-variant/40 text-on-surface">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">monitoring</span>
<span className="font-label-sm text-label-sm font-semibold">3. Business Critic</span>
</div>
<span className="material-symbols-outlined text-outline-variant text-[16px]">arrow_forward</span>
{/* Step 4 */}
<div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-1 rounded border border-outline-variant/40 text-on-surface">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">task_alt</span>
<span className="font-label-sm text-label-sm font-semibold">4. Consensus Engine</span>
</div>
<span className="material-symbols-outlined text-outline-variant text-[16px]">arrow_forward</span>
{/* Step 5 (Current awaiting) */}
<div className="flex items-center gap-space-xs bg-primary-fixed text-primary-container px-space-sm py-1 rounded border border-primary-container/30">
<span className="material-symbols-outlined text-[16px] text-secondary">pending</span>
<span className="font-label-sm text-label-sm font-bold">5. Human Signoff</span>
</div>
</div>
</div>
{/* 1. RECOMMENDED ACTION BANNER */}
<div className="relative overflow-hidden bg-primary-container text-on-primary rounded-xl p-space-lg shadow-md border-l-4 border-l-secondary-fixed">
<div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-primary rounded-full opacity-30 pointer-events-none blur-2xl"></div>
<div className="relative z-10 flex flex-col gap-space-md">
<div className="flex items-start justify-between flex-wrap gap-space-sm">
<div className="flex items-center gap-space-sm">
<div className="p-1.5 rounded-lg bg-surface-container-lowest/10 text-on-primary">
<span className="material-symbols-outlined text-[24px]">recommend</span>
</div>
<div>
<div className="flex items-center gap-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-secondary-fixed font-bold">Sentinel Primary Prescriptive Directive</span>
<span className="text-outline-variant/60 font-code-sm">|</span>
<span className="font-code-sm text-code-sm text-on-primary-container">Action Vector: {trace?.recommended_action || 'EXPEDITE + REORDER'}</span>
</div>
<h2 className="font-headline-sm text-headline-sm font-bold text-on-primary mt-0.5 tracking-tight">
              {trace?.recommended_action || 'EXPEDITE INBOUND SHIPMENT & PARTIAL AIR-FREIGHT REORDER'}
            </h2>
</div>
</div>
<div className="flex items-center gap-space-sm bg-surface-container-lowest/10 backdrop-blur-sm px-space-md py-1.5 rounded-lg border border-on-primary/10">
<span className="font-label-sm text-label-sm text-secondary-fixed-dim uppercase tracking-wider">Estimated ROI</span>
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-on-primary">37.9x Net Coverage</span>
</div>
</div>
<div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md pt-space-xs border-t border-on-primary/15">
{/* Rationale statement */}
<div className="lg:col-span-8 flex flex-col gap-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-secondary-fixed-dim">Decision Rationale</span>
<p className="font-body-md text-body-md text-on-primary/90 leading-relaxed">
            {trace?.situation_summary || `Prevents assembly line stoppage by advancing arrival time. Secures continuous manufacturing schedule and maintains replenishment buffer above strict threshold minimum.`}
          </p>
</div>
{/* Financial trade-off matrix pill */}
<div className="lg:col-span-4 bg-surface-container-lowest/10 backdrop-blur-md rounded-lg p-space-md flex flex-col justify-between border border-on-primary/15">
<div className="flex items-center justify-between text-on-primary-container">
<span className="font-label-sm text-label-sm uppercase tracking-wide">Net Risk Mitigation Balance</span>
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed">price_check</span>
</div>
<div className="flex items-baseline justify-between mt-space-xs">
<div>
<span className="font-label-sm text-label-sm text-secondary-fixed-dim block">Expedite Premium</span>
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-on-primary">$4,850</span>
</div>
<span className="font-label-md text-label-md text-on-primary-container">vs.</span>
<div className="text-right">
<span className="font-label-sm text-label-sm text-secondary-fixed-dim block">Avoided Line-Down Cost</span>
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-tertiary-fixed">+$184,000</span>
</div>
</div>
</div>
</div>
</div>
</div>
{/* 2. BUSINESS EVIDENCE METRICS GRID */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md">
{/* Current Inventory Card */}
<div className="bg-surface-container-lowest rounded-xl p-space-md border border-outline-variant/30 flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Current Physical Stock</span>
<span className="w-2 h-2 rounded-full bg-error"></span>
</div>
<div className="my-space-xs">
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">140</span>
<span className="font-body-sm text-body-sm text-on-surface-variant font-medium">units</span>
</div>
<div className="flex items-center gap-space-xs text-error font-body-sm text-body-sm mt-0.5">
<span className="material-symbols-outlined text-[14px]">south</span>
<span>60% below Safety Stock (350 u)</span>
</div>
</div>
<div className="pt-space-xs border-t border-outline-variant/20 flex justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Reorder Pt: <strong className="text-on-surface">420 u</strong></span>
<span>Burn Rate: <strong className="text-on-surface">50 u/day</strong></span>
</div>
</div>
{/* Projected Days of Supply Card */}
<div className="bg-surface-container-lowest rounded-xl p-space-md border border-outline-variant/30 flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Inventory Depletion Horizon</span>
<span className="px-1.5 py-0.5 rounded bg-error-container text-on-error-container font-label-sm text-label-sm font-semibold">Critical Depletion</span>
</div>
<div className="my-space-xs">
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">2.8</span>
<span className="font-body-sm text-body-sm text-on-surface-variant font-medium">Days of Supply</span>
</div>
<div className="flex items-center gap-space-xs text-error font-body-sm text-body-sm mt-0.5">
<span className="material-symbols-outlined text-[14px]">warning</span>
<span>Stockout projected in 67.2 hrs</span>
</div>
</div>
<div className="pt-space-xs border-t border-outline-variant/20 flex justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Required SLA Buffer: <strong className="text-on-surface">5.0 Days</strong></span>
<span>Target: <strong className="text-on-surface">7.0 Days</strong></span>
</div>
</div>
{/* Inbound Transit PO Details */}
<div className="bg-surface-container-lowest rounded-xl p-space-md border border-outline-variant/30 flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Active Inbound Shipment</span>
<span className="font-code-sm text-code-sm bg-surface-container px-space-xs py-0.5 rounded text-on-surface">PO #881290-A</span>
</div>
<div className="my-space-xs">
<div className="flex items-baseline gap-space-xs">
<span className="font-headline-sm text-headline-sm text-on-surface font-bold">TransLogix Intermodal</span>
</div>
<div className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 truncate">
          Tracking: TLX-SEA-88902-US
        </div>
</div>
<div className="pt-space-xs border-t border-outline-variant/20 flex justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Scheduled: <strong className="text-on-surface">Oct 28 (Day 6)</strong></span>
<span>Volume: <strong className="text-on-surface">500 units</strong></span>
</div>
</div>
{/* Delay Risk Profile */}
<div className="bg-surface-container-lowest rounded-xl p-space-md border border-outline-variant/30 flex flex-col justify-between shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Customs Port Risk Factor</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-error font-bold">84%</span>
</div>
<div className="my-space-xs">
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-error font-bold">+96.0</span>
<span className="font-body-sm text-body-sm text-error font-medium">hrs late delta</span>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant font-body-sm text-body-sm mt-0.5">
<span className="material-symbols-outlined text-[14px] text-error">traffic</span>
<span className="truncate">West Coast Port Drayage Congestion</span>
</div>
</div>
<div className="pt-space-xs border-t border-outline-variant/20 flex justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Confidence: <strong className="text-on-surface">94.2%</strong></span>
<span>Data Signal: <strong className="text-on-surface">Delivery and demand data</strong></span>
</div>
</div>
</div>
{/* 3. EVALUATED CANDIDATE ACTIONS COMPARISON TABLE */}
<div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 flex flex-col overflow-hidden">
<div className="px-space-md py-space-md border-b border-outline-variant/20 bg-surface-container-low flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-[20px] text-primary">balance</span>
<div>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Evaluated Candidate Actions Matrix</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">Comparative evaluation of candidate operational interventions</p>
</div>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">tune</span>
<span>Simulated Iterations: Comprehensive Scenario Analysis</span>
</div>
</div>
<div className="w-full overflow-x-auto">
<table className="w-full text-left border-collapse">
<thead>
<tr className="bg-surface-container-low/60 border-b border-outline-variant/30 font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
<th className="py-space-sm px-space-md font-semibold">Action Candidate</th>
<th className="py-space-sm px-space-sm font-semibold">Qty</th>
<th className="py-space-sm px-space-sm font-semibold">Arrival Timing</th>
<th className="py-space-sm px-space-sm font-semibold text-right">Est. Incremental Cost</th>
<th className="py-space-sm px-space-sm font-semibold">Projected DOS</th>
<th className="py-space-sm px-space-sm font-semibold">Expected Risk Level</th>
<th className="py-space-sm px-space-sm font-semibold text-center">Feasibility</th>
<th className="py-space-sm px-space-sm font-semibold text-center">Policy Tier</th>
<th className="py-space-sm px-space-md font-semibold text-right">Consensus Status</th>
</tr>
</thead>
<tbody className="font-body-sm text-body-sm divide-y divide-outline-variant/20">
{/* Candidate 1 (Recommended) */}
<tr className="bg-surface-container-lowest border-l-4 border-l-primary hover:bg-surface-container-low/50 transition-colors">
<td className="py-space-sm px-space-md">
<div className="flex items-center gap-space-xs">
<span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-primary text-on-primary">Recommended</span>
<span className="font-body-md text-body-md font-semibold text-on-surface">Expedite &amp; Air Reorder</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant block mt-0.5">Customs clearance split + DHL air dispatch from Tier-1 Depot</span>
</td>
<td className="py-space-sm px-space-sm font-tabular-metric-md text-tabular-metric-md font-medium text-on-surface">300 u</td>
<td className="py-space-sm px-space-sm">
<span className="font-tabular-metric-md text-tabular-metric-md font-semibold text-on-surface">+36 hrs</span>
<span className="font-label-sm text-label-sm text-tertiary-container block font-medium">(Day 2.0)</span>
</td>
<td className="py-space-sm px-space-sm text-right font-tabular-metric-md text-tabular-metric-md font-bold text-on-surface">$4,850</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-1.5">
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-tertiary-container">6.8 Days</span>
<span className="text-tertiary-container text-[12px] font-bold">▲</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant block">&gt; 5.0 Buffer</span>
</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-2">
<div className="w-16 h-1.5 rounded-full bg-surface-container overflow-hidden">
<div className="bg-tertiary-container h-full w-[12%]"></div>
</div>
<span className="font-label-sm text-label-sm font-bold text-tertiary-container">Low (12%)</span>
</div>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="px-2 py-0.5 rounded-full text-label-sm font-semibold bg-tertiary-container text-on-tertiary">Feasible</span>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="font-label-sm text-label-sm font-semibold text-on-surface px-1.5 py-0.5 bg-surface-container rounded">Tier-1</span>
</td>
<td className="py-space-sm px-space-md text-right">
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tertiary-container/10 text-tertiary-container font-label-md text-label-md font-bold">
<span className="material-symbols-outlined text-[14px]">done_all</span>
                Approved (4/4)
              </span>
</td>
</tr>
{/* Candidate 2 */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low/50 transition-colors">
<td className="py-space-sm px-space-md">
<span className="font-body-md text-body-md font-medium text-on-surface">Regional Inter-Facility Transfer</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block mt-0.5">Reallocate from Hub East (Cleveland Distribution)</span>
</td>
<td className="py-space-sm px-space-sm font-tabular-metric-md text-tabular-metric-md text-on-surface">180 u</td>
<td className="py-space-sm px-space-sm">
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface">+60 hrs</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block">(Day 3.5)</span>
</td>
<td className="py-space-sm px-space-sm text-right font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">$1,920</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-1.5">
<span className="font-tabular-metric-md text-tabular-metric-md font-semibold text-on-surface">4.4 Days</span>
</div>
<span className="font-label-sm text-label-sm text-error font-medium block">&lt; 5.0 Min Buffer</span>
</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-2">
<div className="w-16 h-1.5 rounded-full bg-surface-container overflow-hidden">
<div className="bg-secondary h-full w-[38%]"></div>
</div>
<span className="font-label-sm text-label-sm font-bold text-secondary">Med (38%)</span>
</div>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="px-2 py-0.5 rounded-full text-label-sm font-semibold bg-tertiary-container text-on-tertiary">Feasible</span>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="font-label-sm text-label-sm font-semibold text-on-surface px-1.5 py-0.5 bg-surface-container rounded">Tier-1</span>
</td>
<td className="py-space-sm px-space-md text-right">
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-label-md text-label-md">
                Conditional (Hub Deficit)
              </span>
</td>
</tr>
{/* Candidate 3 */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low/50 transition-colors">
<td className="py-space-sm px-space-md">
<span className="font-body-md text-body-md font-medium text-on-surface">Standard Ground PO Reorder</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block mt-0.5">New replenishment ticket via regular freight carrier</span>
</td>
<td className="py-space-sm px-space-sm font-tabular-metric-md text-tabular-metric-md text-on-surface">500 u</td>
<td className="py-space-sm px-space-sm">
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface">+144 hrs</span>
<span className="font-label-sm text-label-sm text-error block">(Day 6.0)</span>
</td>
<td className="py-space-sm px-space-sm text-right font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">$850</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-1.5">
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-error">0.4 Days</span>
<span className="text-error text-[12px] font-bold">▼</span>
</div>
<span className="font-label-sm text-label-sm text-error block">Stockout Event</span>
</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-2">
<div className="w-16 h-1.5 rounded-full bg-surface-container overflow-hidden">
<div className="bg-error h-full w-[89%]"></div>
</div>
<span className="font-label-sm text-label-sm font-bold text-error">Critical (89%)</span>
</div>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="px-2 py-0.5 rounded-full text-label-sm font-semibold bg-error-container text-on-error-container">Infeasible</span>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="font-label-sm text-label-sm font-semibold text-on-surface px-1.5 py-0.5 bg-surface-container rounded">Tier-2</span>
</td>
<td className="py-space-sm px-space-md text-right">
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-error-container/40 text-error font-label-md text-label-md font-semibold">
<span className="material-symbols-outlined text-[14px]">cancel</span>
                Rejected (Violates SLA)
              </span>
</td>
</tr>
{/* Candidate 4 */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low/50 transition-colors">
<td className="py-space-sm px-space-md">
<span className="font-body-md text-body-md font-medium text-on-surface">Do Nothing / Status Quo</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block mt-0.5">Rely strictly on delayed shipment arrival</span>
</td>
<td className="py-space-sm px-space-sm font-tabular-metric-md text-tabular-metric-md text-on-surface">0 u</td>
<td className="py-space-sm px-space-sm">
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface-variant">N/A</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block">—</span>
</td>
<td className="py-space-sm px-space-sm text-right font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">$0</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-1.5">
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-error">0.0 Days</span>
</div>
<span className="font-label-sm text-label-sm text-error block">3.2 Days Down</span>
</td>
<td className="py-space-sm px-space-sm">
<div className="flex items-center gap-2">
<div className="w-16 h-1.5 rounded-full bg-surface-container overflow-hidden">
<div className="bg-error h-full w-[98%]"></div>
</div>
<span className="font-label-sm text-label-sm font-bold text-error">Severe (98%)</span>
</div>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="px-2 py-0.5 rounded-full text-label-sm font-semibold bg-error-container text-on-error-container">Infeasible</span>
</td>
<td className="py-space-sm px-space-sm text-center">
<span className="font-label-sm text-label-sm font-semibold text-on-surface px-1.5 py-0.5 bg-surface-container rounded">Tier-1</span>
</td>
<td className="py-space-sm px-space-md text-right">
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-error-container/40 text-error font-label-md text-label-md font-semibold">
<span className="material-symbols-outlined text-[14px]">block</span>
                Rejected (Breach)
              </span>
</td>
</tr>
</tbody>
</table>
</div>
</div>
{/* 4. TRUST & DECISION VALIDATION (Consensus Nodes) */}
<div className="flex flex-col gap-space-sm">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-primary text-[20px]">verified_user</span>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Consensus Governance &amp; Critic Consensus</h3>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">HASH: 0x8F9C...77D1</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md">
{/* Validator 1: Orchestrator */}
<div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-space-sm">
<div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[20px]">neurology</span>
</div>
<span className="px-2 py-0.5 rounded-full text-label-sm font-bold bg-tertiary-container text-on-tertiary flex items-center gap-1">
<span className="material-symbols-outlined text-[12px]">check</span> PASSED
          </span>
</div>
<div>
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block font-semibold">Node 1: Primary AI</span>
<span className="font-headline-sm text-headline-sm text-on-surface font-bold block mt-0.5">LightGBM Engine</span>
<p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Risk assessment completed using the available demand and delivery signals.
          </p>
</div>
<div className="pt-space-xs mt-space-sm border-t border-outline-variant/20 font-code-sm text-code-sm text-on-surface-variant flex justify-between">
<span>Assessment completed</span>
<span>Entropy: 0.04</span>
</div>
</div>
{/* Validator 2: Policy Critic */}
<div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-space-sm">
<div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[20px]">policy</span>
</div>
<span className="px-2 py-0.5 rounded-full text-label-sm font-bold bg-tertiary-container text-on-tertiary flex items-center gap-1">
<span className="material-symbols-outlined text-[12px]">check</span> PASSED
          </span>
</div>
<div>
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block font-semibold">Node 2: Policy Critic</span>
<span className="font-headline-sm text-headline-sm text-on-surface font-bold block mt-0.5">SLA &amp; Limit RAG</span>
<p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Policy #SLA-INV-401 compliant. Cost ($4,850) strictly within Tier-1 expediting discretionary cap ($10,000).
          </p>
</div>
<div className="pt-space-xs mt-space-sm border-t border-outline-variant/20 font-code-sm text-code-sm text-on-surface-variant flex justify-between">
<span>Rules Parsed: 14</span>
<span>Breaches: 0</span>
</div>
</div>
{/* Validator 3: Business Critic */}
<div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-space-sm">
<div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[20px]">query_stats</span>
</div>
<span className="px-2 py-0.5 rounded-full text-label-sm font-bold bg-tertiary-container text-on-tertiary flex items-center gap-1">
<span className="material-symbols-outlined text-[12px]">check</span> PASSED
          </span>
</div>
<div>
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block font-semibold">Node 3: Business Critic</span>
<span className="font-headline-sm text-headline-sm text-on-surface font-bold block mt-0.5">Loss-Prevention Agent</span>
<p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Confirmed line-down downtime risk calculation of $184,000. Benefit-cost ratio: 37.9x.
          </p>
</div>
<div className="pt-space-xs mt-space-sm border-t border-outline-variant/20 font-code-sm text-code-sm text-on-surface-variant flex justify-between">
<span>Cost/Benefit: Positive</span>
<span>Margin Drag: 0.1%</span>
</div>
</div>
{/* Validator 4: Gatekeeper */}
<div className="bg-surface-container-lowest p-space-md rounded-xl border border-outline-variant/30 shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-space-sm">
<div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-[20px]">check_circle_outline</span>
</div>
<span className="px-2 py-0.5 rounded-full text-label-sm font-bold bg-tertiary-container text-on-tertiary flex items-center gap-1">
<span className="material-symbols-outlined text-[12px]">check</span> REACHED
          </span>
</div>
<div>
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block font-semibold">Node 4: Consensus Gate</span>
<span className="font-headline-sm text-headline-sm text-on-surface font-bold block mt-0.5">Quorum Gatekeeper</span>
<p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Review consensus reached. Escalated for human approval before operational commitment.
          </p>
</div>
<div className="pt-space-xs mt-space-sm border-t border-outline-variant/20 font-code-sm text-code-sm text-on-surface-variant flex justify-between">
<span>Unanimity: 100%</span>
<span>Status: Validated</span>
</div>
</div>
</div>
</div>
{/* 5. PROCUREMENT RECOMMENDATION & PURCHASE ORDER DRAFT */}
<div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden">
{/* Notice header banner */}
<div className="bg-surface-container-high px-space-md py-space-sm border-b border-outline-variant/30 flex items-center gap-space-sm">
<span className="material-symbols-outlined text-secondary text-[20px]">info</span>
<p className="font-label-md text-label-md font-semibold text-on-surface">
        PURCHASE ORDER DRAFT ONLY — This is a simulation preview and does not transmit financial transactions.
      </p>
</div>
<div className="p-space-lg flex flex-col lg:flex-row lg:items-center justify-between gap-space-lg">
<div className="flex flex-col gap-space-sm min-w-0">
<div className="flex items-center gap-space-sm">
<span className="font-headline-sm text-headline-sm text-on-surface font-bold">Draft Purchase Order Details</span>
<span className="font-code-sm text-code-sm bg-surface-container px-space-sm py-0.5 rounded text-secondary font-semibold">
            ID: PO-DRAFT-{trace?.trace_id?.substring(0, 8) || 'XXXX'}
          </span>
</div>
<div className="grid grid-cols-2 sm:grid-cols-4 gap-space-md pt-space-xs">
<div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase block font-semibold">Target Vendor</span>
<span className="font-body-md text-body-md text-on-surface font-medium">Primary Supplier</span>
<span className="font-code-sm text-code-sm text-on-surface-variant block">System Selected</span>
</div>
<div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase block font-semibold">Component SKU</span>
<span className="font-body-md text-body-md text-on-surface font-semibold">{trace?.inputs?.sku_id || 'Target SKU'}</span>
<span className="font-code-sm text-code-sm text-on-surface-variant block">Standard Component</span>
</div>
<div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase block font-semibold">Volume / Action</span>
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-on-surface">{typeof trace?.consensus_result?.recommendation === 'object' ? trace.consensus_result.recommendation.action || 'Standard' : 'Standard'}</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block">As Recommended</span>
</div>
<div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase block font-semibold">Dispatched Rate</span>
<span className="font-tabular-metric-md text-tabular-metric-md font-bold text-on-surface">Standard Contract Rate</span>
<span className="font-label-sm text-label-sm text-on-surface-variant block">Subject to confirmation</span>
</div>
</div>
</div>
<div className="flex flex-col sm:flex-row items-center gap-space-sm lg:border-l lg:border-outline-variant/30 lg:pl-space-lg shrink-0">
<button className="w-full sm:w-auto px-space-md py-2 rounded-lg bg-surface-container-high text-on-surface hover:bg-surface-container font-label-md text-label-md font-semibold flex items-center justify-center gap-space-xs transition-colors border border-outline-variant/30" onClick={() => navigator.clipboard.writeText('PO-DRAFT-2024-9981')} type="button">
<span className="material-symbols-outlined text-[16px]">content_copy</span>
<span>Copy Draft Payload</span>
</button>
</div>
</div>
</div>
{/* 6. HUMAN APPROVAL (Operational Review Block) */}
<div className="bg-surface-container-lowest rounded-xl shadow-md border-2 border-primary/20 p-space-lg flex flex-col gap-space-md">
<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm border-b border-outline-variant/20 pb-space-md">
<div className="flex items-center gap-space-sm">
<div className="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center">
<span className="material-symbols-outlined text-[22px]">assignment_ind</span>
</div>
<div>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Human Governance Review</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">
            Authorized Approver: <strong className="text-on-surface font-semibold">Ops Lead (Reviewer)</strong> • Authority Level: <span className="font-code-sm text-code-sm bg-surface-container px-1 rounded font-medium">DISCRETIONARY_TIER_1</span>
</p>
</div>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant font-code-sm text-code-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-container">lock</span>
<span>Cryptographically Audited Chain</span>
</div>
</div>
{/* Reviewer Input Rationale */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md uppercase tracking-wider text-on-surface-variant font-semibold" htmlFor="review-notes">
        Operational Notes &amp; Rationale Justification <span className="text-error">*</span>
</label>
<textarea value={notes} onChange={(e) => setNotes(e.target.value)} className="w-full px-space-md py-space-sm rounded-lg bg-surface-container-low border border-outline-variant/40 focus:outline-none focus:border-secondary focus:bg-surface-container-lowest font-body-md text-body-md text-on-surface transition-all placeholder:text-on-surface-variant/60" id="review-notes" placeholder="Enter operational rationale or justification notes before confirming the decision..." rows="2"></textarea>
</div>
{/* Action Buttons */}
<div className="flex flex-col sm:flex-row items-center justify-between gap-space-md pt-space-xs">
<div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span className="material-symbols-outlined text-[16px]">schedule</span>
<span>Approval deadline: 3 hrs remaining before carrier cut-off (17:00 CST)</span>
</div>
<div className="flex items-center gap-space-sm w-full sm:w-auto flex-wrap sm:flex-nowrap justify-end">
{/* Button 3: Re-eval */}
<button onClick={() => navigate('/app/simulation')} className="w-full sm:w-auto px-space-md py-2 rounded-lg bg-surface-container-low hover:bg-surface-container text-on-surface font-body-md text-body-md font-medium border border-outline-variant/30 flex items-center justify-center gap-space-xs transition-colors" type="button">
<span className="material-symbols-outlined text-[18px]">sync</span>
<span>Request Parameter Re-evaluation</span>
</button>
{/* Button 2: Reject */}
<button disabled={approving} onClick={() => handleApproval('rejected')} className="w-full sm:w-auto px-space-md py-2 rounded-lg bg-surface-container-lowest hover:bg-error-container/30 text-error font-body-md text-body-md font-semibold border border-error/30 flex items-center justify-center gap-space-xs transition-colors disabled:opacity-50" type="button">
<span className="material-symbols-outlined text-[18px]">close</span>
<span>{approving ? 'Processing…' : 'Reject Recommendation'}</span>
</button>
{/* Button 1: Primary Approve */}
<button disabled={approving} onClick={() => handleApproval('approved')} className="w-full sm:w-auto px-space-xl py-2 rounded-lg bg-primary hover:bg-primary-container text-on-primary font-body-md text-body-md font-semibold shadow-sm flex items-center justify-center gap-space-xs transition-all disabled:opacity-50" type="button">
<span className="material-symbols-outlined text-[18px]">done</span>
<span>{approving ? 'Approving…' : 'Approve Recommendation'}</span>
</button>
</div>
</div>
</div>
{/* 7. EXPANDABLE TECHNICAL DECISION TRACE (SHAP & Policy RAG) */}
<div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden">
<button className="w-full px-space-md py-space-sm bg-surface-container-low flex items-center justify-between text-left hover:bg-surface-container-high/60 transition-colors" id="trace-toggle-btn" type="button">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-on-surface-variant text-[20px]">code</span>
<span className="font-headline-sm text-headline-sm text-on-surface font-semibold">Technical Decision Trace &amp; Model Explainability</span>
<span className="font-code-sm text-code-sm bg-surface-container px-1.5 py-0.5 rounded text-on-surface-variant">Explainability + Policy Context</span>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant">
<span className="font-label-sm text-label-sm uppercase tracking-wider font-medium" id="trace-toggle-label">Hide Details</span>
<span className="material-symbols-outlined text-[18px] transition-transform duration-200" id="trace-chevron">expand_less</span>
</div>
</button>
<div className="p-space-lg flex flex-col gap-space-lg border-t border-outline-variant/20" id="trace-content">
<div className="grid grid-cols-1 lg:grid-cols-2 gap-space-lg">
{/* Feature Attributions (SHAP) */}
<div className="flex flex-col gap-space-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md uppercase tracking-wider text-on-surface font-semibold">Key Feature Attributions (SHAP Analysis)</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Base Value: E[f(x)] = 0.18</span>
</div>
<div className="flex flex-col gap-space-xs font-body-sm text-body-sm">
{/* Feature 1 */}
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1">
<div className="flex justify-between items-center">
<span className="font-code-sm text-code-sm text-on-surface font-medium">Inbound Transit Port Delay (+96 hrs)</span>
<span className="font-code-sm text-code-sm text-error font-bold">+0.48</span>
</div>
<div className="w-full bg-surface-container rounded-full h-1.5 overflow-hidden">
<div className="bg-error h-full rounded-full" style="width: 78%"></div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Primary driver escalating risk score above trigger ceiling (0.65).</span>
</div>
{/* Feature 2 */}
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1">
<div className="flex justify-between items-center">
<span className="font-code-sm text-code-sm text-on-surface font-medium">Chicago Production Demand Acceleration (+22%)</span>
<span className="font-code-sm text-code-sm text-error font-bold">+0.32</span>
</div>
<div className="w-full bg-surface-container rounded-full h-1.5 overflow-hidden">
<div className="bg-error h-full rounded-full" style="width: 52%"></div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Depleted safety stock threshold 1.8 days earlier than baseline forecast.</span>
</div>
{/* Feature 3 */}
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1">
<div className="flex justify-between items-center">
<span className="font-code-sm text-code-sm text-on-surface font-medium">Supplier MicroTech In-Stock Readiness</span>
<span className="font-code-sm text-code-sm text-tertiary-container font-bold">-0.24</span>
</div>
<div className="w-full bg-surface-container rounded-full h-1.5 overflow-hidden">
<div className="bg-tertiary-container h-full rounded-full" style="width: 40%"></div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Favorable expedite capability enables viable 36hr air turn-around.</span>
</div>
</div>
</div>
{/* Retrieved Policy Documents (RAG) */}
<div className="flex flex-col gap-space-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md uppercase tracking-wider text-on-surface font-semibold">Retrieved Governance Policies</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Vector Match Score: &gt; 0.91</span>
</div>
<div className="flex flex-col gap-space-xs font-body-sm text-body-sm">
{/* Policy 1 */}
<div className="bg-surface-container-low p-space-sm rounded-lg border-l-2 border-l-secondary flex flex-col gap-0.5">
<div className="flex items-center justify-between">
<span className="font-code-sm text-code-sm text-primary font-bold">Policy #SLA-INV-401 (Section 4.2)</span>
<span className="font-label-sm text-label-sm px-1 rounded bg-surface-container text-on-surface font-semibold">Mandatory</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface font-medium mt-1">
                “Automated line-stoppage prevention protocols mandate expedite intervention whenever unmitigated projected Days of Supply falls below 3.0 days within 72 hours.”
              </p>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">Source: Configured supply-chain policy</span>
</div>
{/* Policy 2 */}
<div className="bg-surface-container-low p-space-sm rounded-lg border-l-2 border-l-primary flex flex-col gap-0.5">
<div className="flex items-center justify-between">
<span className="font-code-sm text-code-sm text-primary font-bold">Policy #FIN-AUTH-109 (Tier-1 Air Freight)</span>
<span className="font-label-sm text-label-sm px-1 rounded bg-surface-container text-on-surface font-semibold">Cost Threshold</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface font-medium mt-1">
                “Discretionary spot air freight is pre-authorized up to $10,000 USD where downtime avoidance cost exceeds 10x the incremental freight surcharge.”
              </p>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">Source: Global Procurement Delegation of Authority (DoA)</span>
</div>
</div>
</div>
</div>
{/* Raw Decision Log Signature */}
<div className="bg-surface-container-low p-space-sm rounded-lg font-code-sm text-code-sm text-on-surface-variant flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs border border-outline-variant/20">
<div className="flex items-center gap-space-xs flex-wrap">
<span className="text-on-surface font-semibold">Model Information:</span>
<span className="text-secondary font-mono">sentinel-lightgbm-v3.0</span>
<span className="text-outline-variant">|</span>
<span className="text-on-surface font-semibold">Prompt Token Count:</span>
<span>1,842 tokens</span>
</div>
<div>
<span>Execution Timestamp: <strong className="text-on-surface">{trace?.timestamp || new Date().toISOString()}</strong></span>
</div>
</div>
</div>
</div>
</div>

  );
}
