import { useState, useEffect } from 'react';
import axios from 'axios';

const SCHEMAS = {
  demand: ["sku_id", "date", "quantity_demanded", "location_id"],
  inventory: ["sku_id", "current_stock", "reorder_point", "safety_stock", "unit_cost", "lead_time_days", "location_id"],
  deliveries: ["delivery_id", "carrier_id", "origin", "destination", "distance_km", "scheduled_date", "actual_date", "is_late", "weather_condition", "traffic_delay_hrs"]
};

export default function DataHub() {
  const [status, setStatus] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'csv' | 'excel' | 'db' | 'demo'>('csv');

  // Shared Upload State
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [mappings, setMappings] = useState<Record<string, any>>({});
  const [validationResults, setValidationResults] = useState<any>(null);
  const [validating, setValidating] = useState(false);

  // DB State
  const [dbUrl, setDbUrl] = useState('');

  const fetchStatus = () => {
    axios.get('/api/data/status').then(res => setStatus(res.data));
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleUseDemo = async () => {
    await axios.post('/api/data/use_demo');
    fetchStatus();
    alert('Switched to Synthetic Demo Dataset.');
  };

  const handleFileUpload = async (files: FileList | null, isExcel: boolean = false) => {
    if (!files || !files.length) return;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      if (isExcel) {
        formData.append('file', files[i]);
      } else {
        formData.append('files', files[i]);
      }
    }

    try {
      const endpoint = isExcel ? '/api/data/upload_excel' : '/api/data/upload_csv';
      const res = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data.status === 'error') {
        alert("Error: " + res.data.message);
        return;
      }

      setUploadedFiles(res.data.uploaded);
      
      const initialMap: any = {};
      res.data.uploaded.forEach((f: any) => {
        let schemaType = 'demand';
        const lowerName = f.filename.toLowerCase();
        if (lowerName.includes('inv')) schemaType = 'inventory';
        if (lowerName.includes('del')) schemaType = 'deliveries';
        
        const colMap: any = {};
        SCHEMAS[schemaType as keyof typeof SCHEMAS].forEach(req => {
          colMap[req] = f.columns.includes(req) ? req : f.columns[0];
        });
        
        initialMap[f.file_id] = { schema_type: schemaType, mapping: colMap };
      });
      setMappings(initialMap);
      setValidationResults(null);
    } catch (err) {
      alert("Failed to upload files");
    }
  };

  const handleValidateMap = async () => {
    setValidating(true);
    try {
      const res = await axios.post('/api/data/validate_map', { files_mapping: mappings });
      setValidationResults(res.data);
      if (res.data.activated) {
        alert("Dataset successfully activated! The backend AI pipeline will now consume this data.");
        fetchStatus();
      }
    } catch (e) {
      alert("Validation failed");
    } finally {
      setValidating(false);
    }
  };

  const handleDbConnect = async () => {
    if (!dbUrl) return alert("Please enter a database URL");
    try {
      const res = await axios.post('/api/data/connect_db', { db_url: dbUrl });
      if (res.data.status === 'success') {
        alert('Database connection activated!');
        fetchStatus();
      } else {
        alert('Error: ' + res.data.message);
      }
    } catch (e) {
      alert("Failed to connect to database");
    }
  };

  const renderMappingWorkflow = () => {
    if (uploadedFiles.length === 0) return null;

    return (
      <div className="mt-8">
        <h3 className="text-lg font-bold text-slate-900 mb-2">Interactive Column Mapping & Canonical Validation</h3>
        <p className="mb-6 text-sm text-slate-600">Review how your dataset's columns map to Sentinel AI model requirements. Adjust any dropdown to match your schema.</p>
        
        {uploadedFiles.map(file => (
          <div key={file.file_id} className="mb-6 bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
            <div className="bg-slate-900 text-slate-100 px-4 py-3 flex items-center justify-between">
              <h4 className="font-semibold text-sm">📄 Configure & Map: {file.filename}</h4>
            </div>
            
            <div className="p-5">
              {/* Data Preview */}
              <div className="overflow-x-auto mb-6 rounded border border-slate-200">
                <table className="min-w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                    <tr>
                      {file.columns.map((c: string) => <th key={c} className="p-2 whitespace-nowrap border-r border-slate-200">{c}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {file.preview?.map((row: any, i: number) => (
                      <tr key={i} className="border-b border-slate-100 last:border-0">
                        {file.columns.map((c: string) => <td key={c} className="p-2 whitespace-nowrap border-r border-slate-100 text-slate-700">{row[c] !== null ? String(row[c]) : ''}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Dataset Type Assignment */}
              <div className="mb-6 bg-slate-50 p-4 rounded border border-slate-200">
                <label className="block text-sm font-semibold text-slate-800 mb-2">Assign to Dataset Type</label>
                <select 
                  value={mappings[file.file_id]?.schema_type || 'demand'}
                  onChange={e => {
                    const newType = e.target.value;
                    const newMapping = { ...mappings };
                    newMapping[file.file_id].schema_type = newType;
                    const colMap: any = {};
                    SCHEMAS[newType as keyof typeof SCHEMAS].forEach(req => {
                      colMap[req] = file.columns.includes(req) ? req : file.columns[0];
                    });
                    newMapping[file.file_id].mapping = colMap;
                    setMappings(newMapping);
                  }}
                  className="w-full max-w-md border-slate-300 rounded-md shadow-sm p-2 text-sm border focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="demand">historical_demand.csv (Demand Forecasting Model)</option>
                  <option value="inventory">inventory_snapshot.csv (Inventory Risk Model)</option>
                  <option value="deliveries">deliveries.csv (Delivery Routing Model)</option>
                </select>
              </div>

              {/* Mapping Dropdowns */}
              <div className="mb-6">
                <h5 className="font-bold text-slate-800 text-sm mb-4">Map Dataset Fields to Model Requirements</h5>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-4">
                  {SCHEMAS[mappings[file.file_id]?.schema_type as keyof typeof SCHEMAS]?.map(req => (
                    <div key={req}>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Model: {req}</label>
                      <select 
                        value={mappings[file.file_id]?.mapping[req] || ''}
                        onChange={e => {
                          const newMapping = { ...mappings };
                          newMapping[file.file_id].mapping[req] = e.target.value;
                          setMappings(newMapping);
                        }}
                        className="w-full border-slate-300 rounded shadow-sm p-2 text-sm border focus:ring-teal-500 focus:border-teal-500"
                      >
                        {file.columns.map((c: string) => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </div>
                  ))}
                </div>
              </div>

              {/* Validation Result block */}
              {validationResults?.results?.[file.file_id] && (
                <div className="mb-6">
                  {validationResults.results[file.file_id].is_valid ? (
                    <div className="bg-[#1b4332] text-emerald-100 p-3 rounded flex items-center gap-2">
                      <span className="font-bold bg-emerald-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">✓</span>
                      <span className="text-sm">Validation Passed: <strong>{file.filename}</strong> is canonicalized ({validationResults.results[file.file_id].profiling?.total_rows || 0} valid rows).</span>
                    </div>
                  ) : (
                    <div className="bg-red-50 text-red-900 p-4 rounded border border-red-200">
                      <strong className="flex items-center gap-2 mb-2">❌ Validation Failed (Blocking):</strong>
                      <ul className="list-disc pl-5 text-sm space-y-1 text-red-800">
                        {validationResults.results[file.file_id].errors.map((err: string, i: number) => <li key={i}>{err}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Dataset Profile block */}
              {validationResults?.results?.[file.file_id]?.profiling && validationResults.results[file.file_id].is_valid && (
                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex items-center justify-between cursor-pointer">
                    <span className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                      📊 Dataset Understanding Profile: {file.filename}
                    </span>
                  </div>
                  <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-6 bg-white">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Total Rows</p>
                      <p className="text-xl font-bold text-slate-900">{validationResults.results[file.file_id].profiling.total_rows}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Date Range</p>
                      <p className="text-lg font-bold text-slate-900">
                        {validationResults.results[file.file_id].profiling.date_min ? 
                         `${validationResults.results[file.file_id].profiling.date_min} → ${validationResults.results[file.file_id].profiling.date_max}` : 
                         'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Unique SKUs</p>
                      <p className="text-xl font-bold text-slate-900">{validationResults.results[file.file_id].profiling.unique_skus_count || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Locations / Carriers</p>
                      <p className="text-xl font-bold text-slate-900">
                        {validationResults.results[file.file_id].profiling.unique_locations_count || validationResults.results[file.file_id].profiling.unique_carriers_count || 'N/A'}
                      </p>
                    </div>
                  </div>
                  {validationResults.results[file.file_id].profiling.forecasting_suitability && (
                    <div className="bg-blue-50 text-blue-800 p-3 text-sm font-medium border-t border-blue-100 flex items-center gap-2">
                      🤖 ML Forecasting Readiness: {validationResults.results[file.file_id].profiling.forecasting_suitability}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        <div className="mt-8 flex items-center gap-4">
          <button 
            onClick={handleValidateMap} 
            disabled={validating} 
            className="bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 px-6 rounded-md shadow-sm transition-colors disabled:opacity-50"
          >
            {validating ? 'Validating...' : 'Use This Dataset'}
          </button>
          
          {validationResults && validationResults.status === 'incomplete' && (
            <div className="text-orange-600 text-sm font-medium flex items-center gap-2">
              ⚠️ Please upload and map all 3 required files (Demand, Inventory, Deliveries) to proceed.
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Enterprise Data Hub</h1>
      <p className="text-slate-600 mb-8">Connect, map, and validate your supply chain datasets.</p>

      {status && (
        <div className="bg-emerald-50 border border-emerald-200 p-5 rounded-lg mb-8 shadow-sm">
          <p className="font-semibold text-emerald-900 mb-2 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 block"></span>
            DATA SOURCE: Active Dataset Connected
          </p>
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1 font-semibold">Inventory SKUs</p>
              <p className="text-xl font-bold text-slate-900">{status.inventory_skus}</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1 font-semibold">Deliveries Loaded</p>
              <p className="text-xl font-bold text-slate-900">{status.deliveries}</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm border border-emerald-100">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1 font-semibold">Demand Records</p>
              <p className="text-xl font-bold text-slate-900">{status.demand_records}</p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-6 flex gap-2 border-b border-slate-200">
        <button onClick={() => { setActiveTab('csv'); setUploadedFiles([]); setValidationResults(null); }} className={`px-4 py-2 font-medium text-sm transition-colors ${activeTab === 'csv' ? 'border-b-2 border-teal-600 text-teal-800' : 'text-slate-500 hover:text-slate-800'}`}>CSV Upload</button>
        <button onClick={() => { setActiveTab('excel'); setUploadedFiles([]); setValidationResults(null); }} className={`px-4 py-2 font-medium text-sm transition-colors ${activeTab === 'excel' ? 'border-b-2 border-teal-600 text-teal-800' : 'text-slate-500 hover:text-slate-800'}`}>Excel Upload</button>
        <button onClick={() => { setActiveTab('db'); setUploadedFiles([]); setValidationResults(null); }} className={`px-4 py-2 font-medium text-sm transition-colors ${activeTab === 'db' ? 'border-b-2 border-teal-600 text-teal-800' : 'text-slate-500 hover:text-slate-800'}`}>Database Connection</button>
        <button onClick={() => { setActiveTab('demo'); setUploadedFiles([]); setValidationResults(null); }} className={`px-4 py-2 font-medium text-sm transition-colors ${activeTab === 'demo' ? 'border-b-2 border-teal-600 text-teal-800' : 'text-slate-500 hover:text-slate-800'}`}>Demo Dataset</button>
      </div>

      {activeTab === 'csv' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-2">CSV Ingestion</h2>
          <p className="text-slate-600 text-sm mb-6">Upload CSV files for Demand, Inventory, and Deliveries.</p>
          <input type="file" multiple accept=".csv" onChange={(e) => handleFileUpload(e.target.files, false)} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100" />
        </div>
      )}

      {activeTab === 'excel' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-2">Excel Ingestion</h2>
          <p className="text-slate-600 text-sm mb-6">Upload an Excel workbook containing sheets: historical_demand, inventory_snapshot, deliveries.</p>
          <input type="file" accept=".xlsx" onChange={(e) => handleFileUpload(e.target.files, true)} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100" />
        </div>
      )}

      {/* Shared Mapping Workflow for both CSV and Excel */}
      {(activeTab === 'csv' || activeTab === 'excel') && renderMappingWorkflow()}

      {activeTab === 'db' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Database Connection</h2>
          <p className="mb-4 text-sm text-slate-600">Supported Connections: PostgreSQL (Neon), SQLite.</p>
          <input type="text" value={dbUrl} onChange={e => setDbUrl(e.target.value)} placeholder="postgresql://user:pass@host/db" className="w-full border-slate-300 rounded p-2 mb-4 border shadow-sm focus:ring-teal-500 focus:border-teal-500" />
          <button onClick={handleDbConnect} className="bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded transition-colors shadow-sm">
            Test Connection & Use
          </button>
        </div>
      )}

      {activeTab === 'demo' && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Synthetic Demo Dataset</h2>
          <p className="text-slate-600 text-sm mb-6">Use the synthetic data bundled with the application to safely test Sentinel's AI decision-making capabilities.</p>
          <button 
            onClick={handleUseDemo}
            className="bg-slate-800 hover:bg-slate-900 text-white font-medium px-4 py-2 rounded shadow-sm transition-colors"
          >
            Use Demo Dataset
          </button>
        </div>
      )}
    </div>
  );
}
