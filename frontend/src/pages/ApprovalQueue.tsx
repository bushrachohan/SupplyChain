import { useState, useEffect } from 'react';
import axios from 'axios';
import DecisionDetail from '../components/DecisionDetail';

function Badge({ level }: { level: string }) {
  const lvl = level.toLowerCase();
  if (["high", "critical"].includes(lvl)) return <span className="bg-red-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  if (["medium", "warning"].includes(lvl)) return <span className="bg-orange-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  if (["low", "ok"].includes(lvl)) return <span className="bg-emerald-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  return <span className="bg-slate-800 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
}

export default function ApprovalQueue() {
  const [traces, setTraces] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const fetchQueue = () => {
    axios.get('/api/traces').then(res => {
      const pending = res.data.filter((t: any) => t.human_approval?.status === 'pending');
      setTraces(pending);
    });
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  if (traces.length === 0) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Decision Approval Queue</h1>
        <p className="text-slate-600 mb-8">AI-generated decisions waiting for human review.</p>
        <div className="bg-emerald-50 text-emerald-800 p-4 rounded-md border border-emerald-200">
          All caught up! No pending recommendations require approval right now.
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Decision Approval Queue</h1>
      <p className="text-slate-600 mb-8">AI-generated decisions waiting for human review.</p>

      <div className="space-y-4">
        {traces.map(trace => {
          const recActionObj = trace.consensus_result?.recommendation;
          const recAction = typeof recActionObj === 'object' ? recActionObj?.action : (recActionObj || "Review needed");
          
          let traceRisk = "HIGH";
          if (trace.predictions?.risk_level) traceRisk = trace.predictions.risk_level;
          else if (trace.predictions?.overall_severity) traceRisk = trace.predictions.overall_severity;
          
          const sitStr = String(trace.inputs?.situation || "Unknown Situation");
          const shortSit = sitStr.length > 50 ? sitStr.substring(0, 50) + "..." : sitStr;

          return (
            <div key={trace.trace_id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="p-4 flex items-center justify-between border-b border-slate-100">
                <div className="flex-1 grid grid-cols-4 items-center gap-4">
                  <div className="col-span-1"><Badge level={traceRisk} /></div>
                  <div className="col-span-1 text-sm text-slate-800 font-medium"><strong>Issue:</strong> {shortSit}</div>
                  <div className="col-span-1 text-sm text-slate-800 font-medium"><strong>Recommended:</strong> {recAction}</div>
                  <div className="col-span-1 text-xs text-slate-500">{new Date(trace.timestamp).toLocaleDateString()}</div>
                </div>
                <button 
                  onClick={() => setExpanded({ ...expanded, [trace.trace_id]: !expanded[trace.trace_id] })}
                  className="ml-4 bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded text-sm font-medium transition-colors"
                >
                  {expanded[trace.trace_id] ? 'Hide Details' : 'Review Decision'}
                </button>
              </div>
              {expanded[trace.trace_id] && (
                <div className="p-6 bg-slate-50/50">
                  <DecisionDetail trace={trace} isPending={true} onUpdate={fetchQueue} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
