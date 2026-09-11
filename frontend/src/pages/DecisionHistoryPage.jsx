import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function DecisionHistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getHistory()
      .then(data => setHistory(data?.history || data || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleExportCsv = () => {
    window.location.href = api.exportHistoryCsvUrl();
  };

  const downloadCSVReport = () => {
    if (api.exportHistoryCsvUrl) {
      window.location.href = api.exportHistoryCsvUrl();
    } else {
      window.location.href = '/api/history/export';
    }
  };

  const toggleDetails = (id) => {
    const el = document.getElementById(id);
    const icon = document.getElementById(`icon-${id}`);
    if (el) {
      if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        if (icon) icon.textContent = 'expand_less';
      } else {
        el.classList.add('hidden');
        if (icon) icon.textContent = 'expand_more';
      }
    }
  };

  const filterStatus = (status) => {
    const cards = document.querySelectorAll('.audit-card');
    cards.forEach(card => {
      if (status === 'ALL' || card.dataset.status === status) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  };

  return (
<div className="flex flex-col w-full">
<div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md mb-space-lg">
<div>
<div className="flex items-center gap-space-sm mb-1">
<span className="font-label-sm text-label-sm uppercase tracking-wider text-primary font-bold bg-primary-fixed px-2 py-0.5 rounded">Decision History</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">SHA-256 Verified Chain</span>
</div>
<h1 className="font-headline-xl text-headline-xl text-on-surface font-bold tracking-tight">Decision History &amp; Audit Trail</h1>
<p className="font-body-md text-body-md text-on-surface-variant mt-0.5">Comprehensive audit log of human-approved and rejected AI decision recommendations with full policy traces.</p>
</div>
<div className="flex items-center gap-space-sm shrink-0">
<button className="flex items-center gap-space-xs px-space-md py-2 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm font-semibold rounded shadow-sm hover:bg-surface-container transition-all" onClick={downloadCSVReport}>
<span className="material-symbols-outlined text-[18px] text-secondary">download</span>
        Export Audit Log (CSV)
      </button>
<button className="flex items-center gap-space-xs px-space-md py-2 bg-primary text-on-primary font-body-sm text-body-sm font-semibold rounded shadow-sm hover:bg-secondary transition-all">
<span className="material-symbols-outlined text-[18px]">verified</span>
        Verify Merkle Root
      </button>
</div>
</div>
{/* Top Metrics Bar */}
<div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-space-md mb-space-lg">
<div className="p-space-md bg-surface-container-lowest rounded shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-1">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Total Audited Decisions</span>
<span className="material-symbols-outlined text-primary text-[20px]">fact_check</span>
</div>
<div className="flex items-baseline gap-space-sm mt-1">
<span className="font-tabular-metric-lg text-tabular-metric-lg font-bold text-on-surface">1,420</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">All time</span>
</div>
<div className="mt-2 flex items-center gap-1 text-primary">
<span className="font-code-sm text-code-sm font-medium">100% cryptographic trace retention</span>
</div>
</div>
<div className="p-space-md bg-surface-container-lowest rounded shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-1">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Human Approved</span>
<span className="w-2.5 h-2.5 rounded-full bg-tertiary-fixed-dim"></span>
</div>
<div className="flex items-baseline gap-space-sm mt-1">
<span className="font-tabular-metric-lg text-tabular-metric-lg font-bold text-on-surface">1,288</span>
<span className="font-code-sm text-code-sm font-semibold text-tertiary-container bg-tertiary-fixed/30 px-1.5 py-0.5 rounded">90.7%</span>
</div>
<div className="mt-2 text-on-surface-variant font-body-sm text-body-sm flex items-center gap-1">
<span>▲ 1.4% vs prev 30d baseline</span>
</div>
</div>
<div className="p-space-md bg-surface-container-lowest rounded shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-1">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Rejected / Overridden</span>
<span className="w-2.5 h-2.5 rounded-full bg-error"></span>
</div>
<div className="flex items-baseline gap-space-sm mt-1">
<span className="font-tabular-metric-lg text-tabular-metric-lg font-bold text-on-surface">132</span>
<span className="font-code-sm text-code-sm font-semibold text-error bg-error-container/40 px-1.5 py-0.5 rounded">9.3%</span>
</div>
<div className="mt-2 text-on-surface-variant font-body-sm text-body-sm flex items-center gap-1">
<span>Primary cause: Local buffer reallocation</span>
</div>
</div>
<div className="p-space-md bg-surface-container-lowest rounded shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between mb-1">
<span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Regulatory Compliance Mode</span>
<span className="material-symbols-outlined text-secondary text-[20px]">policy</span>
</div>
<div className="mt-1">
<span className="font-body-md text-body-md font-bold text-primary">Tier-1 SOX / Ops Audit</span>
<p className="font-code-sm text-code-sm text-on-surface-variant mt-0.5 truncate">PCAOB &amp; ISO 27001 Validated</p>
</div>
<div className="mt-2 flex items-center gap-1 text-on-surface font-label-sm text-label-sm">
<span className="w-1.5 h-1.5 rounded-full bg-tertiary-fixed-dim"></span>
<span>Decision Trace Recorded</span>
</div>
</div>
</div>
{/* Filter & Control Panel */}
<div className="bg-surface-container-lowest rounded shadow-sm p-space-md mb-space-lg">
<div className="grid grid-cols-1 md:grid-cols-12 gap-space-sm items-center">
{/* Search Input */}
<div className="md:col-span-4 relative">
<span className="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-[18px]">search</span>
<input value={search} onChange={e => setSearch(e.target.value)} className="w-full pl-9 pr-3 py-2 bg-surface-container-low text-on-surface font-body-sm text-body-sm rounded outline-none focus:bg-surface-container-lowest focus:ring-1 focus:ring-secondary transition-all" id="record-search" placeholder="Search by SKU, PO, or Decision ID..." type="text" />
</div>
{/* Date Range Filter */}
<div className="md:col-span-3 flex items-center gap-2 bg-surface-container-low px-3 py-2 rounded">
<span className="material-symbols-outlined text-on-surface-variant text-[18px]">calendar_today</span>
<select className="w-full bg-transparent font-body-sm text-body-sm text-on-surface outline-none cursor-pointer">
<option value="30">Last 30 Days</option>
<option value="7">Last 7 Days</option>
<option value="90">Last Quarter (90 Days)</option>
<option value="365">Trailing 12 Months</option>
</select>
</div>
{/* Decision Status */}
<div className="md:col-span-2 flex items-center gap-2 bg-surface-container-low px-3 py-2 rounded">
<span className="material-symbols-outlined text-on-surface-variant text-[18px]">tune</span>
<select className="w-full bg-transparent font-body-sm text-body-sm text-on-surface outline-none cursor-pointer" id="status-filter" onChange={(e) => filterStatus(e.target.value)}>
<option value="ALL">Status: All</option>
<option value="APPROVED">Approved Only</option>
<option value="REJECTED">Rejected Only</option>
</select>
</div>
{/* Facility Filter */}
<div className="md:col-span-3 flex items-center gap-2 bg-surface-container-low px-3 py-2 rounded">
<span className="material-symbols-outlined text-on-surface-variant text-[18px]">warehouse</span>
<select className="w-full bg-transparent font-body-sm text-body-sm text-on-surface outline-none cursor-pointer">
<option value="ALL">Facility: All Facilities</option>
<option value="CENTRAL">Central DC</option>
<option value="CHICAGO">Chicago Hub</option>
<option value="DALLAS">Dallas DC</option>
</select>
</div>
</div>
</div>
{/* Audit Records List */}
<div className="flex flex-col gap-space-md" id="records-container">
  {history.length === 0 && !loading && (
    <div className="bg-surface-container-lowest rounded-xl p-space-xl text-center text-on-surface-variant">
      No decision history found.
    </div>
  )}
  {history.map((item, index) => {
    const isApproved = item.status === 'APPROVED';
    return (
      <div key={item.trace_id} className="audit-card bg-surface-container-lowest rounded shadow-sm overflow-hidden" data-status={item.status}>
        <div className="p-space-md bg-surface-container-low/50 flex flex-col xl:flex-row xl:items-center justify-between gap-space-sm cursor-pointer hover:bg-surface-container-low transition-colors" onClick={() => toggleDetails(item.trace_id)}>
          <div className="flex flex-wrap items-center gap-space-sm">
            <span className="font-code-sm text-code-sm font-semibold bg-surface-container px-2 py-1 rounded text-primary">{item.trace_id}</span>
            <span className={`font-label-sm text-label-sm uppercase font-bold px-2 py-0.5 rounded flex items-center gap-1 ${isApproved ? 'text-tertiary-container bg-tertiary-fixed/40' : 'text-error-container bg-error/20'}`}>
              <span className="material-symbols-outlined text-[14px]">
                {isApproved ? 'check_circle' : 'cancel'}
              </span> {item.status}
            </span>
            <span className="text-outline-variant">•</span>
            <span className="font-body-sm text-body-sm font-semibold text-on-surface">{item.situation}</span>
            <span className="text-outline-variant">•</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Recommended Action: <strong className="text-on-surface">{item.recommended_action}</strong></span>
          </div>
          <div className="flex items-center gap-space-md justify-between xl:justify-end">
            <div className="flex items-center gap-2 text-on-surface-variant font-code-sm text-code-sm">
              <span className="material-symbols-outlined text-[16px]">schedule</span> {new Date(item.timestamp).toLocaleString()}
            </div>
            <span className="font-label-sm text-label-sm bg-primary-container text-on-primary px-2 py-0.5 rounded font-medium">{item.consensus_status || 'Consensus Passed'}</span>
            <span className="material-symbols-outlined text-on-surface-variant text-[20px] transition-transform duration-200" id={`icon-${item.trace_id}`}>expand_more</span>
          </div>
        </div>
        <div className="p-space-lg flex flex-col gap-space-md hidden" id={item.trace_id}>
          <div className={`p-space-md ${isApproved ? 'bg-surface-container-lowest' : 'bg-error-container/10'} rounded shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md`}>
            <div className="flex items-start gap-space-sm">
              <div className={`w-8 h-8 rounded-full ${isApproved ? 'bg-primary' : 'bg-error'} flex items-center justify-center shrink-0`}>
                <span className={`material-symbols-outlined ${isApproved ? 'text-on-primary' : 'text-on-error'} text-[18px]`}>
                  {isApproved ? 'verified_user' : 'block'}
                </span>
              </div>
              <div>
                <div className="flex items-center gap-space-xs">
                  <span className="font-body-sm text-body-sm font-semibold text-on-surface">{item.approver}</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant">(Reviewer Authorization)</span>
                  <span className="text-outline-variant">•</span>
                  <span className="font-code-sm text-code-sm text-on-surface-variant">Action Timestamp: {new Date(item.approval_timestamp).toLocaleString()}</span>
                </div>
                <p className="font-body-md text-body-md text-on-surface mt-1 italic">
                  "{item.notes || (isApproved ? 'Approved by Reviewer' : 'Rejected by Reviewer')}"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  })}
</div>
{/* Pagination & Ledger Summary Controls */}
<div className="mt-space-lg bg-surface-container-lowest rounded shadow-sm p-space-md flex flex-col sm:flex-row items-center justify-between gap-space-md">
<div className="flex items-center gap-space-sm text-on-surface-variant font-code-sm text-code-sm">
<span>Showing <strong>1-4</strong> of <strong>1,420</strong> verified decision events</span>
<span className="text-outline-variant">|</span>
<span>Ledger Hash: <strong className="text-primary font-mono">0x4a18..bb90</strong></span>
</div>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-1.5 rounded bg-surface-container-low text-on-surface-variant hover:bg-surface-container font-code-sm text-code-sm flex items-center gap-1 cursor-pointer">
<span className="material-symbols-outlined text-[16px]">chevron_left</span> Previous
      </button>
<button className="px-space-md py-1.5 rounded bg-primary text-on-primary font-code-sm text-code-sm font-bold shadow-sm">1</button>
<button className="px-space-md py-1.5 rounded bg-surface-container-low text-on-surface hover:bg-surface-container font-code-sm text-code-sm">2</button>
<button className="px-space-md py-1.5 rounded bg-surface-container-low text-on-surface hover:bg-surface-container font-code-sm text-code-sm">3</button>
<span className="px-1 text-on-surface-variant font-code-sm text-code-sm">...</span>
<button className="px-space-md py-1.5 rounded bg-surface-container-low text-on-surface hover:bg-surface-container font-code-sm text-code-sm">355</button>
<button className="px-space-sm py-1.5 rounded bg-surface-container-low text-on-surface-variant hover:bg-surface-container font-code-sm text-code-sm flex items-center gap-1 cursor-pointer">
        Next <span className="material-symbols-outlined text-[16px]">chevron_right</span>
</button>
</div>
</div>
</div>

  );
}
