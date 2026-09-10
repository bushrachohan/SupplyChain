import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function ApprovalQueuePage() {
  const navigate = useNavigate();
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getApprovals()
      .then(data => setApprovals(data?.approvals || data || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleApprove = async (traceId) => {
    try {
      await api.submitApproval(traceId, { decision: 'approved', reviewer: 'Ops Lead' });
      setApprovals(prev => prev.filter(a => a.trace_id !== traceId));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
<div className="flex flex-col w-full">

<section className="flex flex-col gap-space-lg mb-space-xl">
<div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center gap-space-sm text-on-surface-variant">
<span className="font-code-sm text-code-sm uppercase tracking-widest text-secondary">Queue Management</span>
<span className="text-outline-variant">/</span>
<span className="font-label-md text-label-md">Decision Review</span>
</div>
<h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight">Operational Approval Queue</h1>
<p className="font-body-md text-body-md text-on-surface-variant">AI-generated decision recommendations awaiting human sign-off and policy governance.</p>
</div>
<div className="flex items-center gap-space-md self-start md:self-auto">
<div className="bg-surface-container-lowest px-space-md py-space-sm rounded-lg shadow-sm flex items-center gap-space-md">
<div className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Engine State</span>
<span className="font-label-md text-label-md text-on-surface font-semibold">Policy Review Applied</span>
</div>
</div>
<button className="flex items-center gap-space-xs bg-surface-container px-space-md py-2 rounded-lg text-on-surface font-label-md text-label-md hover:bg-surface-container-high transition-colors shadow-sm">
<span className="material-symbols-outlined text-[18px]">tune</span>
<span>Filter Queue</span>
</button>
</div>
</div>
<div className="grid grid-cols-1 md:grid-cols-5 gap-space-sm">
<button className="flex flex-col text-left p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition-all relative overflow-hidden group">
<div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>
<div className="flex items-center justify-between w-full mb-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-primary font-semibold">All Pending</span>
<span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
</div>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{approvals.length}</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">actions</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">100% evaluated</span>
</button>
<button className="flex flex-col text-left p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition-all group">
<div className="flex items-center justify-between w-full mb-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-error font-semibold">Critical Severity</span>
<span className="w-2 h-2 rounded-full bg-error"></span>
</div>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-error font-bold">2</span>
<span className="font-label-sm text-label-sm text-error/80">urgent</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">&lt; 18h buffer expiry</span>
</button>
<button className="flex flex-col text-left p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition-all group">
<div className="flex items-center justify-between w-full mb-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-on-surface-variant font-semibold">High Severity</span>
<span className="w-2 h-2 rounded-full bg-secondary-container"></span>
</div>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">1</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">item</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">Imbalance risk</span>
</button>
<button className="flex flex-col text-left p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition-all group">
<div className="flex items-center justify-between w-full mb-space-xs">
<span className="font-label-md text-label-md uppercase tracking-wider text-on-surface-variant font-semibold">Medium Severity</span>
<span className="w-2 h-2 rounded-full bg-outline"></span>
</div>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">1</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">item</span>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant mt-1">Lead time drift</span>
</button>
<div className="flex flex-col justify-between p-space-md rounded-xl bg-surface-container-low shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">Review Queue</span>
<span className="material-symbols-outlined text-[16px] text-tertiary">verified</span>
</div>
<div>
<div className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold text-tertiary">Pending</div>
<div className="w-full bg-surface-container-high rounded-full h-1 mt-1 overflow-hidden">
<div className="bg-tertiary-container h-full rounded-full" style={{ width: '100%' }}></div>
</div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Human review required</span>
</div>
</div>
</section>
<div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-md mb-space-lg flex flex-col md:flex-row items-center justify-between gap-space-md">
<div className="flex items-center gap-space-md w-full md:w-auto flex-1 max-w-2xl">
<div className="relative w-full">
<span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
<input className="w-full pl-9 pr-4 py-2 bg-surface-container-low rounded-lg text-body-sm font-body-sm text-on-surface placeholder:text-on-surface-variant/70 focus:outline-none focus:bg-surface-container-lowest focus:ring-1 focus:ring-secondary transition-all" placeholder="Filter by SKU, Delivery ID, PO, or Decision Ref (e.g. DEC-88029-A, SKU_104)..." type="text" />
</div>
<div className="relative min-w-[180px]">
<select className="w-full appearance-none bg-surface-container-low px-3 py-2 pr-8 rounded-lg text-body-sm font-body-sm text-on-surface focus:outline-none focus:ring-1 focus:ring-secondary cursor-pointer">
<option value="all">All Facilities (4)</option>
<option value="chicago">Chicago DC (2)</option>
<option value="central">Central DC (1)</option>
<option value="midwest">Midwest Hub (1)</option>
</select>
<span className="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant text-[18px]">expand_more</span>
</div>
</div>
<div className="flex items-center gap-space-sm w-full md:w-auto justify-end">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Sort By</span>
<button className="flex items-center gap-1 px-space-sm py-1.5 rounded-lg bg-surface-container text-body-sm font-body-sm text-on-surface font-medium hover:bg-surface-container-high transition-colors">
<span>Risk Severity</span>
<span className="material-symbols-outlined text-[16px]">arrow_downward</span>
</button>
<button className="p-1.5 rounded-lg bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors">
<span className="material-symbols-outlined text-[20px]">refresh</span>
</button>
</div>
</div>
<div className="flex flex-col gap-space-md">
{approvals.length === 0 ? (
  <div className="bg-surface-container-lowest rounded-xl p-space-xl text-center text-on-surface-variant">
    No pending decisions in approval queue. All decisions evaluated and signed off.
  </div>
) : (
  approvals.map((item) => {
    const isCritical = item.severity === 'CRITICAL' || item.severity === 'STOCKOUT_RISK';
    return (
      <div key={item.trace_id} className="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden transition-all hover:shadow-md">
        <div className="p-space-lg flex flex-col xl:flex-row items-start xl:items-center justify-between gap-space-lg">
          <div className="flex flex-col gap-space-sm w-full xl:max-w-xl">
            <div className="flex flex-wrap items-center gap-space-sm">
              <span className={`px-2 py-0.5 rounded text-label-sm font-label-sm uppercase font-bold tracking-wider flex items-center gap-1 ${
                isCritical ? 'bg-error-container text-on-error-container' : 'bg-secondary-fixed text-on-secondary-fixed'
              }`}>
                {isCritical && <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>}
                {item.severity}
              </span>
              <span className="font-code-sm text-code-sm font-semibold text-primary">{item.trace_id}</span>
              <span className="text-outline-variant text-[12px]">|</span>
              <span className="font-label-sm text-label-sm text-on-surface-variant">Reviewer: {item.reviewer || 'Ops Lead'}</span>
              <span className="text-outline-variant text-[12px]">|</span>
              <span className="font-code-sm text-code-sm text-on-surface-variant">{item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : 'Recent'}</span>
            </div>
            <div className="flex flex-col">
              <p className="font-body-md text-body-md text-on-surface mt-0.5 font-medium">
                {item.situation_summary || 'Operational decision review required.'}
              </p>
            </div>
            <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
              <div className="flex items-center gap-1.5 font-label-sm text-label-sm uppercase text-secondary font-semibold">
                <span className="material-symbols-outlined text-[16px]">psychology</span>
                Sentinel Recommended Intervention
              </div>
              <p className="font-body-md text-body-md text-on-surface font-medium">
                {item.recommended_action || 'Review details and evaluate options'}
              </p>
            </div>
          </div>
          <div className="flex flex-col md:flex-row items-start md:items-center gap-space-lg w-full xl:w-auto xl:justify-end">
            <div className="flex flex-col gap-space-xs min-w-[200px]">
              <div className="flex items-center justify-between">
                <span className="font-label-sm text-label-sm uppercase text-on-surface-variant">Critic Consensus</span>
                <span className="font-label-sm text-label-sm font-semibold text-tertiary bg-tertiary-container/10 px-1.5 py-0.5 rounded">Evaluated</span>
              </div>
              <div className="grid grid-cols-4 gap-1 w-full">
                <div className="h-1.5 rounded-full bg-tertiary" title="Primary AI"></div>
                <div className="h-1.5 rounded-full bg-tertiary" title="Policy Critic"></div>
                <div className="h-1.5 rounded-full bg-tertiary" title="Business Critic"></div>
                <div className="h-1.5 rounded-full bg-tertiary" title="Consensus"></div>
              </div>
              <div className="flex items-center justify-between text-code-sm font-code-sm text-on-surface-variant">
                <span>Primary</span>
                <span>Policy</span>
                <span>Biz</span>
                <span>Risk</span>
              </div>
            </div>
            <div className="flex items-center gap-space-sm w-full md:w-auto mt-2 xl:mt-0">
              <button onClick={() => navigate(`/app/decision/${item.trace_id}`)} className="w-full md:w-auto px-space-lg py-2.5 rounded-lg bg-primary hover:bg-secondary text-on-primary font-headline-sm text-body-md font-semibold transition-all shadow-sm flex items-center justify-center gap-space-xs">
                <span>Review Decision</span>
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>
            </div>
          </div>
        </div>
        <div className="px-space-lg py-space-xs bg-surface-container flex items-center justify-between text-code-sm font-code-sm text-on-surface-variant">
          <div className="flex items-center gap-space-md">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px] text-tertiary">check_circle</span>
              Trace Status: {item.status || 'pending'}
            </span>
            <span className="text-outline-variant">|</span>
            <span>Trace Ref: {item.trace_id}</span>
          </div>
          <button onClick={() => navigate(`/app/decision/${item.trace_id}`)} className="hover:text-primary flex items-center gap-1 transition-colors">
            <span>View Decision Evidence</span>
            <span className="material-symbols-outlined text-[14px]">unfold_more</span>
          </button>
        </div>
      </div>
    );
  })
)}
</div>
<div className="mt-space-lg bg-surface-container-lowest px-space-lg py-space-md rounded-xl shadow-sm flex flex-col sm:flex-row items-center justify-between gap-space-md">
<div className="flex items-center gap-space-md">
<span className="font-body-sm text-body-sm text-on-surface-variant">
        Showing <span className="font-semibold text-on-surface">1 - {approvals.length}</span> of <span className="font-semibold text-on-surface">{approvals.length}</span> pending decisions
      </span>
<span className="text-outline-variant">|</span>
<span className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-1">
<span className="w-1.5 h-1.5 rounded-full bg-tertiary-fixed-dim"></span>
        All critic verification matrices up to date
      </span>
</div>
<div className="flex items-center gap-space-xs">
<button className="px-space-md py-1.5 rounded-lg text-on-surface-variant/40 bg-surface-container-low font-body-sm text-body-sm cursor-not-allowed flex items-center gap-1" disabled="">
<span className="material-symbols-outlined text-[16px]">chevron_left</span>
<span>Previous</span>
</button>
<div className="px-space-md py-1.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md">
        1
      </div>
<button className="px-space-md py-1.5 rounded-lg text-on-surface-variant/40 bg-surface-container-low font-body-sm text-body-sm cursor-not-allowed flex items-center gap-1" disabled="">
<span>Next</span>
<span className="material-symbols-outlined text-[16px]">chevron_right</span>
</button>
</div>
</div>
</div>
  );
}
