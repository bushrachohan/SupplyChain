import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function CreateDecision() {
  const navigate = useNavigate();
  const [options, setOptions] = useState<{skus: string[], deliveries: string[]}>({ skus: [], deliveries: [] });
  
  const initialType = sessionStorage.getItem('target_type') || 'Inventory / Demand Issue';
  const initialId = sessionStorage.getItem('target_id') || '';
  
  const [targetType, setTargetType] = useState(initialType);
  const [targetId, setTargetId] = useState(initialId);
  const [situation, setSituation] = useState('');
  
  const [preview, setPreview] = useState<any>(null);

  
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState('');

  useEffect(() => {
    axios.get('/api/options').then(res => {
      setOptions(res.data);
      if (!targetId) {
        if (targetType === 'Inventory / Demand Issue' && res.data.skus.length > 0) setTargetId(res.data.skus[0]);
        if (targetType === 'Delivery / Routing Issue' && res.data.deliveries.length > 0) setTargetId(res.data.deliveries[0]);
      }
    });
  }, [targetType]);

  useEffect(() => {
    if (targetId) {
      const req = targetType === 'Inventory / Demand Issue' ? { sku_id: targetId } : { delivery_id: targetId };
      axios.post('/api/unified_situation', req)
        .then(res => setPreview(res.data))
        .catch(() => setPreview(null));
    }
  }, [targetId, targetType]);

  const handleRunAnalysis = async () => {
    if (!targetId) return alert('Please specify a Target ID to proceed.');
    setAnalyzing(true);
    setAnalysisStatus('Synthesizing unified supply-chain situation...');
    
    try {
      const fullSituation = `Target ID: ${targetId}. User context: ${situation || 'Evaluate the operational risk and provide the optimal recommended action.'}`;
      
      const res = await axios.post('/api/orchestrate', { situation: fullSituation });
      setAnalysisStatus('Analysis Complete');
      setTimeout(() => {
        alert(`Decision created successfully (ID: ${res.data.trace_id}). Please go to the Approval Queue to review.`);
        navigate('/app/approval-queue');
      }, 500);
    } catch (e) {
      alert('Error during analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Create a Decision</h1>
      <p className="text-slate-600 mb-8">Tell Sentinel what supply-chain situation you want to evaluate. Sentinel will automatically fetch the latest numbers from your active dataset.</p>

      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm mb-8">
        <h2 className="text-lg font-bold text-slate-900 mb-4 border-b pb-2">BUSINESS CONTEXT</h2>
        
        <div className="grid grid-cols-2 gap-8 mb-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">What does this concern?</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" checked={targetType === 'Inventory / Demand Issue'} onChange={() => { setTargetType('Inventory / Demand Issue'); setTargetId(options.skus[0] || ''); }} className="text-teal-600 focus:ring-teal-500" />
                <span className="text-sm">Inventory / Demand Issue</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" checked={targetType === 'Delivery / Routing Issue'} onChange={() => { setTargetType('Delivery / Routing Issue'); setTargetId(options.deliveries[0] || ''); }} className="text-teal-600 focus:ring-teal-500" />
                <span className="text-sm">Delivery / Routing Issue</span>
              </label>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {targetType === 'Inventory / Demand Issue' ? 'Select Product (SKU)' : 'Select Delivery (Shipment ID)'}
            </label>
            <select 
              value={targetId} 
              onChange={e => setTargetId(e.target.value)}
              className="w-full border-slate-300 rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2 border"
            >
              {(targetType === 'Inventory / Demand Issue' ? options.skus : options.deliveries).map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">Describe the situation or business constraints (Optional)</label>
          <textarea 
            value={situation}
            onChange={e => setSituation(e.target.value)}
            placeholder="e.g., We just landed a huge enterprise client and demand is going to double. Do we have enough stock, or should we expedite shipments?"
            className="w-full border-slate-300 rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-3 border min-h-[100px]"
          />
        </div>

        {preview && !preview.error && (
          <div className="mt-8 border-t pt-6">
            <h4 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">🛡️ Unified Situation Assessment (Pre-Analysis)</h4>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <p className="text-xs text-slate-500 mb-1 uppercase">Overall Severity</p>
                <p className="font-bold text-lg">{preview.overall_severity}</p>
              </div>
              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <p className="text-xs text-slate-500 mb-1 uppercase">Primary Bottleneck</p>
                <p className="font-bold text-lg">{preview.bottleneck_type}</p>
              </div>
              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <p className="text-xs text-slate-500 mb-1 uppercase">Urgency Window</p>
                <p className="font-bold text-lg">~{preview.impact_urgency_hours} hrs</p>
              </div>
            </div>
            <div className="bg-blue-50 text-blue-800 p-3 rounded text-sm mb-2 border border-blue-200">
              <strong>Bottleneck Discovery:</strong> {preview.description}
            </div>
            {preview.cross_risk_dependencies && preview.cross_risk_dependencies.map((dep: string, i: number) => (
              <div key={i} className="bg-orange-50 text-orange-800 p-3 rounded text-sm mt-2 border border-orange-200">
                ⚠️ <strong>Compounding Dependency:</strong> {dep}
              </div>
            ))}
          </div>
        )}
      </div>

      <button 
        onClick={handleRunAnalysis}
        disabled={analyzing}
        className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 px-4 rounded shadow transition-colors disabled:opacity-50"
      >
        {analyzing ? `Analyzing... (${analysisStatus})` : 'Run AI Decision Analysis'}
      </button>
    </div>
  );
}
