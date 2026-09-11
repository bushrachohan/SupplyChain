import { useState, useEffect } from 'react';
import axios from 'axios';
import DecisionDetail from '../components/DecisionDetail';

function Badge({ level }: { level: string }) {
  const lvl = level.toLowerCase();
  if (["high", "critical", "rejected"].includes(lvl)) return <span className="bg-red-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  if (["medium", "warning"].includes(lvl)) return <span className="bg-orange-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  if (["low", "ok", "approved"].includes(lvl)) return <span className="bg-emerald-500 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
  return <span className="bg-slate-800 text-white px-2 py-0.5 rounded text-[10px] font-bold">{level.toUpperCase()}</span>;
}

export default function DecisionHistory() {
  const [traces, setTraces] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    axios.get('/api/traces').then(res => {
      const history = res.data.filter((t: any) => t.human_approval?.status === 'approved' || t.human_approval?.status === 'rejected');
      setTraces(history);
    });
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Decision History</h1>
      <p className="text-slate-600 mb-8">Audit trail of approved and rejected decisions.</p>

      {traces.length === 0 ? (
        <div className="bg-slate-50 text-slate-500 p-4 rounded-md border border-slate-200">
          No historical decisions found.
        </div>
      ) : (
        <div className="space-y-4">
          {traces.map(trace => {
            const status = trace.human_approval?.status?.toUpperCase() || 'UNKNOWN';
            const sitStr = String(trace.inputs?.situation || "");
            const shortSit = sitStr.length > 60 ? sitStr.substring(0, 60) + "..." : sitStr;
            const recActionObj = trace.consensus_result?.recommendation;
            const recAction = typeof recActionObj === 'object' ? recActionObj?.action : (recActionObj || "Unknown");
            const dateStr = new Date(trace.timestamp).toLocaleString();

            return (
              <div key={trace.trace_id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
                <div 
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
                  onClick={() => setExpanded({ ...expanded, [trace.trace_id]: !expanded[trace.trace_id] })}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-semibold text-slate-700 w-36">{dateStr}</span>
                    <Badge level={status} />
                    <span className="text-sm text-slate-800">{shortSit}</span>
                  </div>
                  <span className="text-slate-400">
                    {expanded[trace.trace_id] ? '▲' : '▼'}
                  </span>
                </div>
                {expanded[trace.trace_id] && (
                  <div className="p-6 bg-slate-50/50 border-t border-slate-100">
                    <div className="mb-4 text-sm text-slate-700">
                      <strong>Recommendation:</strong> {recAction} <br/>
                      <strong>Reviewer:</strong> {trace.human_approval?.approver} | <strong>Notes:</strong> {trace.human_approval?.notes}
                    </div>
                    <hr className="mb-4 border-slate-200" />
                    <DecisionDetail trace={trace} isPending={false} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
