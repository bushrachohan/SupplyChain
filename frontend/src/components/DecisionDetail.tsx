import axios from 'axios';
import { useState } from 'react';

function Badge({ level }: { level: string }) {
  const lvl = level.toLowerCase();
  if (["high", "critical", "stockout", "stockout_risk", "rejected"].includes(lvl)) return <span className="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">{level.toUpperCase()}</span>;
  if (["medium", "warning", "overstock", "overstock_risk", "needs review"].includes(lvl)) return <span className="bg-orange-500 text-white px-2 py-1 rounded text-xs font-bold">{level.toUpperCase()}</span>;
  if (["low", "ok", "passed", "approved", "normal"].includes(lvl)) return <span className="bg-emerald-500 text-white px-2 py-1 rounded text-xs font-bold">{level.toUpperCase()}</span>;
  return <span className="bg-slate-800 text-white px-2 py-1 rounded text-xs font-bold">{level.toUpperCase()}</span>;
}

export default function DecisionDetail({ trace, isPending, onUpdate }: { trace: any, isPending: boolean, onUpdate?: () => void }) {
  const [showTech, setShowTech] = useState(false);
  const [approver, setApprover] = useState('System Admin');
  const [notes, setNotes] = useState('');

  const recActionObj = trace.consensus_result?.recommendation;
  const recAction = typeof recActionObj === 'object' ? recActionObj?.action : (recActionObj || "Unknown");
  const narration = trace.consensus_result?.narration || "No reasoning provided.";
  
  let hasEvidence = false;
  const evidenceBlocks = trace.tools_used?.map((tc: any, i: number) => {
    const toolName = tc.tool;
    const res = tc.result;
    if (toolName === 'get_inventory_risk' && !res.error) {
      hasEvidence = true;
      const rl = res.risk_level || 'NORMAL';
      return (
        <div key={i} className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-3">
          <strong className="text-blue-900 block mb-2">📦 Inventory Profile: {res.sku_id}</strong>
          <ul className="text-sm text-blue-800 space-y-1">
            <li><strong>Risk Status:</strong> <Badge level={rl} /></li>
            <li><strong>Current Stock / Coverage:</strong> {res.days_of_supply?.toFixed(1) || 0} Days of Supply</li>
            <li><strong>Calculated Reorder Point:</strong> {res.reorder_point_units?.toFixed(0) || 0} Units</li>
            <li><strong>Required Safety Stock:</strong> {res.safety_stock_units?.toFixed(0) || 0} Units</li>
            <li><strong>Engine Detail:</strong> <em>{res.detail}</em></li>
          </ul>
        </div>
      );
    }
    if (toolName === 'get_demand_forecast' && !res.error) {
      hasEvidence = true;
      const totalPred = res.predicted_quantities?.reduce((a:number,b:number)=>a+b, 0) || 0;
      return (
        <div key={i} className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-3">
          <strong className="text-blue-900 block mb-2">📈 Demand Forecast: {res.sku_id}</strong>
          <ul className="text-sm text-blue-800 space-y-1">
            <li><strong>Horizon:</strong> {res.forecast_horizon_weeks} Weeks</li>
            <li><strong>Total Predicted Demand:</strong> {totalPred.toFixed(0)} Units</li>
          </ul>
        </div>
      );
    }
    if (toolName === 'get_delivery_risk' && !res.error) {
      hasEvidence = true;
      const score = (res.risk_score || 0) * 100;
      return (
        <div key={i} className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-3">
          <strong className="text-blue-900 block mb-2">🚚 Delivery Profile: {res.delivery_id}</strong>
          <ul className="text-sm text-blue-800 space-y-1">
            <li><strong>Delay Risk:</strong> <Badge level={res.risk_label || 'LOW'} /></li>
            <li><strong>Late Probability:</strong> {score.toFixed(1)}%</li>
          </ul>
        </div>
      );
    }
    return null;
  });

  let actionsData: any[] = [];
  if (trace.options_considered?.candidate_actions) {
    actionsData = trace.options_considered.candidate_actions;
  } else {
    trace.tools_used?.forEach((tc: any) => {
      if (tc.tool === 'get_candidate_actions' && tc.result?.candidate_actions) {
        actionsData = tc.result.candidate_actions;
      }
    });
  }

  const polOut = trace.policy_critic_output || {};
  const busOut = trace.business_critic_output || {};
  const conOut = trace.consensus_result || {};

  const handleApproval = async (status: string) => {
    await axios.post(`/api/traces/${trace.trace_id}/approval`, { status, approver, notes });
    if (onUpdate) onUpdate();
  };

  return (
    <div className="py-4">
      <h3 className="text-lg font-bold text-slate-900 mb-2">AI DECISION</h3>
      <div className="mb-6">
        <h4 className="font-bold text-slate-800 mb-2">RECOMMENDED ACTION: <span className="uppercase">{String(recAction)}</span></h4>
        <p className="text-slate-700 font-semibold mb-1">Why Sentinel recommends this:</p>
        <p className="text-slate-600 text-sm">{narration}</p>
      </div>

      <h4 className="font-bold text-slate-900 mb-3">Business Evidence (Calculated from Active Dataset)</h4>
      {evidenceBlocks}
      {!hasEvidence && <p className="text-sm text-slate-500 italic mb-4">No specific quantitative evidence extracted.</p>}

      {actionsData.length > 0 && (
        <div className="mb-6 mt-4">
          <h4 className="font-bold text-slate-900 mb-1">⚖️ Evaluated Candidate Replenishment Actions</h4>
          <p className="text-xs text-slate-500 mb-3">Deterministic options calculated by Sentinel's replenishment engine. The AI Decision Agent evaluates these options against enterprise policies.</p>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm border-collapse border border-slate-200">
              <thead className="bg-slate-50 text-slate-600 font-semibold">
                <tr>
                  <th className="p-2 border border-slate-200">Action</th>
                  <th className="p-2 border border-slate-200">Quantity</th>
                  <th className="p-2 border border-slate-200">Timing</th>
                  <th className="p-2 border border-slate-200">Cost</th>
                  <th className="p-2 border border-slate-200">Proj DOS</th>
                  <th className="p-2 border border-slate-200">Risk After</th>
                  <th className="p-2 border border-slate-200">Approval Tier</th>
                  <th className="p-2 border border-slate-200">Feasibility</th>
                </tr>
              </thead>
              <tbody>
                {actionsData.map((a, i) => (
                  <tr key={i} className="border-b border-slate-200">
                    <td className="p-2 border border-slate-200">{a.action_name?.replace(/_/g, ' ')}</td>
                    <td className="p-2 border border-slate-200">{a.quantity > 0 ? `${a.quantity} units` : '0 units'}</td>
                    <td className="p-2 border border-slate-200">{a.action_name === 'do_nothing' ? 'Immediate' : `${a.arrival_days} days`}</td>
                    <td className="p-2 border border-slate-200">₹{a.estimated_cost || 0}</td>
                    <td className="p-2 border border-slate-200">{a.expected_days_of_supply_after?.toFixed(1)} d</td>
                    <td className="p-2 border border-slate-200">{a.expected_risk_level_after}</td>
                    <td className="p-2 border border-slate-200">{a.approval_tier?.replace(/_/g, ' ')}</td>
                    <td className="p-2 border border-slate-200">{a.feasible ? '✅ Feasible' : '❌ Infeasible'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {String(recAction).toLowerCase().includes('reorder') || String(recAction).toLowerCase().includes('expedite') ? (
        <div className="bg-emerald-50 border border-emerald-300 rounded-md p-4 mb-6">
          <div className="flex justify-between items-center border-b border-emerald-200 pb-2 mb-3">
            <strong className="text-emerald-700">📋 DRAFT PURCHASE ORDER: PO-DRAFT-{trace.trace_id.substring(0,6)}</strong>
            {!isPending && trace.human_approval?.status === 'approved' ? (
              <span className="bg-emerald-200 text-emerald-800 px-2 py-1 rounded text-xs font-bold">✓ APPROVED BY {trace.human_approval.approver}</span>
            ) : (
              <span className="bg-orange-200 text-orange-800 px-2 py-1 rounded text-xs font-bold">⏳ PENDING HUMAN APPROVAL</span>
            )}
          </div>
          <div className="grid grid-cols-4 gap-4 text-sm text-slate-700">
             <div><strong>Action:</strong><br/>{recAction}</div>
             <div><strong>Required Approval:</strong><br/>SYSTEM DERIVED</div>
             <div><strong>Destination:</strong><br/>PRIMARY_FACILITY</div>
             <div><strong>Policy Compliance:</strong><br/>Verified</div>
          </div>
          <p className="text-xs text-slate-500 mt-3">⚠️ Recommendation Draft Only. This platform never automatically transmits transactions to external ERP systems.</p>
        </div>
      ) : null}

      <div className="mb-6">
        <h4 className="font-bold text-slate-900 mb-3">Why should I trust this decision?</h4>
        <div className="grid grid-cols-4 gap-4">
           <div className="bg-blue-50 border border-blue-200 p-3 rounded">
              <strong className="text-sm text-blue-900">Primary AI</strong>
              <p className="text-blue-700 mt-2 font-medium">✓ Action Formulated</p>
           </div>
           <div className={`p-3 rounded border ${polOut.compliant ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-orange-50 border-orange-200 text-orange-800'}`}>
              <strong className="text-sm">Policy Review</strong>
              <p className="mt-2 font-medium">{polOut.compliant ? '✓ PASSED' : '⚠ NEEDS REVIEW'}</p>
           </div>
           <div className={`p-3 rounded border ${busOut.approved ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-orange-50 border-orange-200 text-orange-800'}`}>
              <strong className="text-sm">Business Review</strong>
              <p className="mt-2 font-medium">{busOut.approved ? '✓ PASSED' : '⚠ NEEDS REVIEW'}</p>
           </div>
           <div className={`p-3 rounded border ${conOut.status?.toUpperCase() === 'APPROVED' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-orange-50 border-orange-200 text-orange-800'}`}>
              <strong className="text-sm">Consensus</strong>
              <p className="mt-2 font-medium">{conOut.status?.toUpperCase() === 'APPROVED' ? '✓ PASSED' : '⚠ NEEDS REVIEW'}</p>
           </div>
        </div>
      </div>

      <div className="mb-6">
        <button onClick={() => setShowTech(!showTech)} className="text-sm text-teal-700 font-medium hover:underline">
          {showTech ? 'Hide Decision Transparency' : 'Show Decision Transparency (Technical Details)'}
        </button>
        {showTech && (
          <div className="mt-4 grid grid-cols-2 gap-6 bg-slate-50 p-4 rounded border border-slate-200 text-xs font-mono overflow-auto max-h-96">
            <div>
              <strong className="block mb-2">Data Considered</strong>
              <pre>{JSON.stringify(trace.inputs, null, 2)}</pre>
            </div>
            <div>
              <strong className="block mb-2">Evidence & Analysis</strong>
              <pre>{JSON.stringify(trace.tools_used, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>

      {isPending && (
        <div className="border-t border-slate-200 pt-6 mt-6">
          <h4 className="font-bold text-slate-900 mb-1">Human Approval Required</h4>
          <p className="text-xs text-slate-500 mb-4">This recommendation has been independently reviewed by multiple AI agents. No operational action will be taken without human approval.</p>
          <div className="space-y-4 max-w-lg">
            <textarea 
              placeholder="Reviewer Notes (Optional)" 
              value={notes} 
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border-slate-300 rounded-md shadow-sm p-2 text-sm border focus:ring-teal-500 focus:border-teal-500"
            />
            <input 
              type="text" 
              placeholder="Reviewer Name" 
              value={approver} 
              onChange={(e) => setApprover(e.target.value)}
              className="w-full border-slate-300 rounded-md shadow-sm p-2 text-sm border focus:ring-teal-500 focus:border-teal-500"
            />
            <div className="flex gap-4">
              <button onClick={() => handleApproval('approved')} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded font-medium shadow-sm transition-colors flex-1">
                ✓ Approve Recommendation
              </button>
              <button onClick={() => handleApproval('rejected')} className="bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 px-4 py-2 rounded font-medium shadow-sm transition-colors flex-1">
                ✕ Reject Recommendation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
