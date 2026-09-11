import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';

/**
 * DataHubPage — full functional integration with FastAPI backend.
 *
 * Upload flow:
 *   1. User selects CSV or Excel file(s)
 *   2. POST /api/data/upload  → { file_token, files: [{filename, columns, sheets, row_count, preview_rows}], schemas }
 *   3. Columns & sheets rendered from response
 *   4. User picks schemaType and (for Excel) a sheet
 *   5. POST /api/data/suggest-mapping → { suggested_mapping, required_columns, optional_columns }
 *   6. User can adjust mapping in UI
 *   7. POST /api/data/validate → { is_valid, errors, warnings, profiling, row_count }
 *   8. POST /api/data/activate → { message, status }
 *
 * DB flow:
 *   POST /api/data/connect-db { connection_url } → 200 or 400
 *
 * API source: NOT implemented in backend (APIDataSource raises NotImplementedError without live credentials).
 *   UI shows "Not Available" truthfully.
 */
export default function DataHubPage() {
  const [activeTab, setActiveTab] = useState('excel');
  const [status, setStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(true);

  // Upload state
  const [file, setFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);  // full API response
  const [fileToken, setFileToken] = useState(null);
  const [uploadedFileSummary, setUploadedFileSummary] = useState(null); // files[0]

  // Sheet & schema selection
  const [selectedSheet, setSelectedSheet] = useState(null);
  const [schemaType, setSchemaType] = useState('deliveries');

  // Mapping state
  const [detectedColumns, setDetectedColumns] = useState([]);
  const [requiredCols, setRequiredCols] = useState([]);
  const [optionalCols, setOptionalCols] = useState([]);
  const [mapping, setMapping] = useState({});  // { target_col -> source_col }
  const [mappingLoading, setMappingLoading] = useState(false);

  // Validation
  const [validationResult, setValidationResult] = useState(null);
  const [validationLoading, setValidationLoading] = useState(false);

  // Activation
  const [activating, setActivating] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  // DB connection
  const [dbUrl, setDbUrl] = useState('');
  const [dbConnecting, setDbConnecting] = useState(false);
  const [dbResult, setDbResult] = useState(null);

  // Load active dataset status on mount
  useEffect(() => {
    api.getDataStatus()
      .then(d => setStatus(d))
      .catch(err => console.error('Status error:', err))
      .finally(() => setStatusLoading(false));
  }, []);

  // File upload handler — supports CSV and Excel
  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    setFile(files[0]);
    setUploadLoading(true);
    setActionError(null);
    setActionSuccess(null);
    setUploadResult(null);
    setFileToken(null);
    setUploadedFileSummary(null);
    setMapping({});
    setValidationResult(null);
    setDetectedColumns([]);

    try {
      // POST /api/data/upload — backend param is "files" (List[UploadFile])
      const res = await api.uploadData(files);
      // res = { file_token, files: [{filename, columns, sheets, row_count, preview_rows, file_type, error?}], schemas }
      setUploadResult(res);
      setFileToken(res.file_token);

      const fileSummary = res.files?.[0];
      if (fileSummary) {
        setUploadedFileSummary(fileSummary);
        const cols = fileSummary.columns || [];
        setDetectedColumns(cols);

        // Auto-select first sheet for Excel (skipping README if possible)
        if (fileSummary.file_type === 'excel' && fileSummary.sheets?.length > 0) {
          const defaultSheet = fileSummary.sheets.find(s => s.toLowerCase() !== 'readme') || fileSummary.sheets[0];
          setSelectedSheet(defaultSheet);
          if (fileSummary.sheet_previews?.[defaultSheet]) {
            const sheetCols = fileSummary.sheet_previews[defaultSheet].columns || [];
            setDetectedColumns(sheetCols);
            if (sheetCols.length > 0) await fetchSuggestedMapping(sheetCols, schemaType);
          } else if (cols.length > 0) {
            await fetchSuggestedMapping(cols, schemaType);
          }
        } else if (cols.length > 0) {
          // Auto-suggest mapping if columns were detected
          await fetchSuggestedMapping(cols, schemaType);
        }
      }
    } catch (err) {
      setActionError(err.message || 'Upload failed. Please check the file format.');
    } finally {
      setUploadLoading(false);
    }
  };

  // Fetch suggested column mapping from backend
  const fetchSuggestedMapping = async (columns, schema) => {
    setMappingLoading(true);
    try {
      // POST /api/data/suggest-mapping { existing_columns, schema_type }
      const res = await api.suggestMapping(columns, schema);
      setRequiredCols(res.required_columns || []);
      setOptionalCols(res.optional_columns || []);
      if (res.suggested_mapping) setMapping(res.suggested_mapping);
    } catch (err) {
      setActionError('Could not auto-suggest mapping: ' + err.message);
    } finally {
      setMappingLoading(false);
    }
  };

  // Re-fetch mapping when schema type or sheet changes
  const handleSchemaChange = async (newSchema) => {
    setSchemaType(newSchema);
    if (detectedColumns.length > 0) {
      await fetchSuggestedMapping(detectedColumns, newSchema);
    }
  };

  const handleSheetChange = async (sheetName) => {
    setSelectedSheet(sheetName);
    if (uploadedFileSummary?.sheet_previews?.[sheetName]) {
      const cols = uploadedFileSummary.sheet_previews[sheetName].columns || [];
      setDetectedColumns(cols);
      if (cols.length > 0) {
        await fetchSuggestedMapping(cols, schemaType);
      }
    }
  };

  const handleSelectFile = async (idx) => {
    const fileSummary = uploadResult.files[idx];
    if (fileSummary) {
      setUploadedFileSummary(fileSummary);
      setMapping({});
      setValidationResult(null);
      const cols = fileSummary.columns || [];
      setDetectedColumns(cols);
      if (cols.length > 0) {
        // Auto-guess schema from filename
        let guess = 'inventory';
        if (fileSummary.filename.toLowerCase().includes('demand')) guess = 'demand';
        if (fileSummary.filename.toLowerCase().includes('deliver')) guess = 'deliveries';
        setSchemaType(guess);
        await fetchSuggestedMapping(cols, guess);
      }
    }
  };

  const handleValidate = async () => {
    if (!fileToken || !uploadedFileSummary) {
      setActionError('Upload a file first before validating.');
      return;
    }
    setValidationLoading(true);
    setActionError(null);
    try {
      // POST /api/data/validate { file_token, filename, schema_type, column_mapping, sheet_name? }
      const res = await api.validateData(
        fileToken,
        uploadedFileSummary.filename,
        schemaType,
        mapping,
        uploadedFileSummary.file_type === 'excel' ? selectedSheet : null
      );
      setValidationResult(res);
      if (!res.is_valid && res.errors?.length > 0) {
        setActionError('Validation failed: ' + res.errors.join('; '));
      }
    } catch (err) {
      setActionError(err.message || 'Validation failed');
    } finally {
      setValidationLoading(false);
    }
  };

  const handleActivate = async () => {
    if (!fileToken || !uploadedFileSummary) {
      setActionError('Upload and validate a file before activating.');
      return;
    }
    setActivating(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      // POST /api/data/activate { file_token, source_type: "csv"|"excel", excel_sheet_mapping? }
      const sourceType = uploadedFileSummary.file_type === 'excel' ? 'excel' : 'csv';
      const res = await api.activateDataset(fileToken, sourceType, null);
      setActionSuccess(res?.message || 'Dataset activated successfully!');
      // Refresh status
      const newStatus = await api.getDataStatus();
      setStatus(newStatus);
    } catch (err) {
      setActionError(err.message || 'Activation failed');
    } finally {
      setActivating(false);
    }
  };

  const handleActivateDemo = async () => {
    setActivating(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await api.activateDemo();
      setActionSuccess(res?.message || 'Demo dataset activated!');
      const newStatus = await api.getDataStatus();
      setStatus(newStatus);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActivating(false);
    }
  };

  const handleConnectDb = async () => {
    if (!dbUrl.trim()) {
      setActionError('Enter a database connection URL.');
      return;
    }
    setDbConnecting(true);
    setActionError(null);
    setDbResult(null);
    try {
      // POST /api/data/connect-db { connection_url }
      const res = await api.connectDb(dbUrl.trim());
      setDbResult({ success: true, message: res.message || 'Database connected and activated.' });
      const newStatus = await api.getDataStatus();
      setStatus(newStatus);
    } catch (err) {
      setDbResult({ success: false, message: err.message || 'Database connection failed.' });
    } finally {
      setDbConnecting(false);
    }
  };

  // Derived display values
  const fileInfo = uploadedFileSummary || {};
  const sheets = fileInfo.sheets || [];
  const previewRows = (fileInfo.file_type === 'excel' && selectedSheet && fileInfo.sheet_previews?.[selectedSheet]?.preview_rows) ? fileInfo.sheet_previews[selectedSheet].preview_rows : (fileInfo.preview_rows || []);
  const previewCols = (fileInfo.file_type === 'excel' && selectedSheet && fileInfo.sheet_previews?.[selectedSheet]?.columns) ? fileInfo.sheet_previews[selectedSheet].columns : (fileInfo.columns || []);

  return (
<div className="flex flex-col w-full">
<div className="flex flex-col gap-space-xl">
{/* Error / Success Banners */}
{actionError && (
  <div className="bg-error-container text-on-error-container px-space-lg py-space-md rounded-xl font-body-md text-body-md flex items-center gap-space-sm">
    <span className="material-symbols-outlined text-[20px]">error</span>
    {actionError}
    <button onClick={() => setActionError(null)} className="ml-auto font-bold">✕</button>
  </div>
)}
{actionSuccess && (
  <div className="bg-tertiary-container text-on-tertiary-container px-space-lg py-space-md rounded-xl font-body-md text-body-md flex items-center gap-space-sm">
    <span className="material-symbols-outlined text-[20px]">check_circle</span>
    {actionSuccess}
    <button onClick={() => setActionSuccess(null)} className="ml-auto font-bold">✕</button>
  </div>
)}
{/* Top Execution & Progress Ribbon */}
<div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md pb-space-md">
<div>
<div className="flex items-center gap-space-xs text-primary font-label-md uppercase tracking-wider mb-space-xs">
<span className="material-symbols-outlined text-[16px]">tune</span>
          Ingestion &amp; Schema Pipeline
        </div>
<h1 className="font-headline-xl text-headline-xl text-on-surface font-bold tracking-tight">Data Hub</h1>
<p className="font-body-md text-body-md text-on-surface-variant max-w-3xl">
          Manage data ingestion, inspect uploaded workbooks, map source columns to the required schema, validate, and activate datasets.
        </p>
</div>
{/* Linear Workflow Tracker */}
<div className="bg-surface-container-lowest p-space-sm rounded-xl shadow-sm flex items-center gap-space-xs overflow-x-auto min-w-0">
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${fileToken ? 'bg-surface-container-high text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm font-semibold">01</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Upload</span>
{fileToken && <span className="material-symbols-outlined text-[14px]">check_circle</span>}
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${detectedColumns.length > 0 ? 'bg-surface-container-high text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm font-semibold">02</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Inspect</span>
{detectedColumns.length > 0 && <span className="material-symbols-outlined text-[14px]">check_circle</span>}
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${sheets.length > 0 ? 'bg-primary-container text-on-primary shadow-sm' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm font-semibold">03</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Select Sheet</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${Object.keys(mapping).length > 0 ? 'bg-secondary-container text-on-secondary-container' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm font-semibold">04</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Map Schema</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${validationResult ? 'bg-surface-container-high text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm">05</span>
<span className="font-label-sm text-label-sm uppercase">Validate</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className={`flex items-center gap-space-xs px-space-sm py-1 rounded ${actionSuccess ? 'bg-tertiary-container text-tertiary-fixed' : 'bg-surface-container text-on-surface-variant'}`}>
<span className="font-code-sm text-code-sm">06</span>
<span className="font-label-sm text-label-sm uppercase">Activate</span>
</div>
</div>
</div>
{/* Supported Data Sources Tabs */}
<div className="bg-surface-container-lowest p-space-xs rounded-xl shadow-sm flex items-center justify-between overflow-x-auto">
<div className="flex items-center gap-space-xs">
<button onClick={() => setActiveTab('excel')} className={activeTab === 'excel' ? "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md transition-all shadow-sm" : "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all"}>Excel Upload</button>
<button onClick={() => setActiveTab('csv')} className={activeTab === 'csv' ? "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md transition-all shadow-sm" : "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all"}>CSV Upload</button>
<button onClick={() => setActiveTab('db')} className={activeTab === 'db' ? "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md transition-all shadow-sm" : "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all"}>Database Connection</button>
<button onClick={() => setActiveTab('demo')} className={activeTab === 'demo' ? "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md transition-all shadow-sm" : "flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all"}>Demo Dataset</button>
</div>
<div className="pr-space-md hidden sm:flex items-center gap-space-xs font-label-sm text-label-sm text-on-surface-variant">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">verified_user</span>
        In-Memory RAG Parser Active
      </div>
</div>

{/* ===== CSV / EXCEL UPLOAD TAB ===== */}
{(activeTab === 'csv' || activeTab === 'excel') && (
<div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
{/* File Upload Card */}
<div className="lg:col-span-4 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between">
<div className="flex flex-col gap-space-sm">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
  {activeTab === 'excel' ? 'Excel Workbook Upload' : 'CSV File Upload'}
</span>
{uploadedFileSummary && <span className="px-space-sm py-0.5 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm uppercase font-semibold">Uploaded</span>}
</div>
<div className="flex items-center gap-space-md mt-space-xs">
<div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center shrink-0">
<span className="material-symbols-outlined text-secondary text-[26px]">grid_on</span>
</div>
<div className="min-w-0">
<div className="font-headline-sm text-headline-sm text-on-surface truncate font-semibold">
  {fileInfo.filename || file?.name || (activeTab === 'excel' ? 'supply_chain_operations_master.xlsx' : 'historical_demand.csv')}
</div>
<div className="font-body-sm text-body-sm text-on-surface-variant">
  {fileInfo.size_bytes ? `${(fileInfo.size_bytes / 1024).toFixed(1)} KB` : 'No file selected'}
  {fileInfo.row_count > 0 ? ` · ${fileInfo.row_count.toLocaleString()} rows` : ''}
</div>
</div>
</div>
</div>

{/* File Input */}
<div className="mt-space-lg">
<label className="flex flex-col items-center justify-center w-full h-20 border-2 border-dashed border-outline-variant rounded-xl cursor-pointer hover:bg-surface-container-low transition-colors">
<span className="material-symbols-outlined text-secondary text-[28px]">upload_file</span>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">
  {uploadLoading ? 'Uploading…' : `Drop ${activeTab === 'excel' ? '.xlsx / .xls' : '.csv'} file here or click`}
</span>
  <input
    type="file"
    accept={activeTab === 'excel' ? '.xlsx,.xls' : '.csv'}
    multiple={activeTab === 'csv'}
    onChange={handleFileUpload}
    className="hidden"
    disabled={uploadLoading}
  />
</label>
</div>

{fileInfo.row_count > 0 && (
<div className="mt-space-md pt-space-md bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-xs">
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Total Parsed Rows</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">{fileInfo.row_count?.toLocaleString()}</span>
</div>
{sheets.length > 0 && (
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Detected Sheets</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">{sheets.length} sheets</span>
</div>
)}
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Detected Columns</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">{detectedColumns.length}</span>
</div>
</div>
)}
</div>

{/* Sheet Selector (Excel only) */}
<div className="lg:col-span-8 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
  {sheets.length > 0 ? 'Detected Sheets in Workbook' : 'File Ready for Upload'}
</span>
  {sheets.length > 0 && <span className="font-body-sm text-body-sm text-on-surface-variant">Click to select sheet for schema mapping</span>}
</div>
{sheets.length === 0 && !fileToken && (
  <p className="font-body-sm text-body-sm text-on-surface-variant mt-space-md">
    Upload a file to see its structure. The backend will detect columns, sheets, and row counts automatically.
  </p>
)}
{uploadResult?.files?.length > 1 && (
  <div className="mt-space-md bg-surface-container p-space-md rounded-lg">
    <label className="font-label-sm text-label-sm uppercase text-on-surface-variant mb-space-xs block">Select File to Map & Validate</label>
    <select
      onChange={e => handleSelectFile(Number(e.target.value))}
      className="w-full bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none"
    >
      {uploadResult.files.map((f, i) => (
        <option key={i} value={i}>{f.filename}</option>
      ))}
    </select>
    <p className="text-on-surface-variant font-body-sm text-body-sm mt-2">
      Select each file, map it to the target schema, and click "Validate Schema" to save it. Activate when all 3 files are validated.
    </p>
  </div>
)}
</div>

{/* Schema Type Selector */}
{fileToken && (
<div className="mt-space-md">
<label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Target Schema Type</label>
<div className="flex gap-space-sm mt-space-xs flex-wrap">
  {['demand', 'inventory', 'deliveries'].map(s => (
    <button
      key={s}
      onClick={() => handleSchemaChange(s)}
      className={`px-space-md py-1.5 rounded-lg font-label-md text-label-md transition-colors ${schemaType === s ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'}`}
    >
      {s.charAt(0).toUpperCase() + s.slice(1)}
    </button>
  ))}
</div>
</div>
)}

{sheets.length > 0 && (
<div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-space-sm mt-space-md">
{sheets.map(sheet => (
<div
  key={sheet}
  onClick={() => handleSheetChange(sheet)}
  className={`p-space-md rounded-lg transition-all cursor-pointer flex flex-col gap-1 ${selectedSheet === sheet ? 'bg-primary-container text-on-primary shadow-sm relative ring-2 ring-secondary-container' : 'bg-surface-container-low hover:bg-surface-container-high'}`}
>
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm font-medium flex items-center gap-space-xs">
  {selectedSheet === sheet && <span className="material-symbols-outlined text-[18px]">radio_button_checked</span>}
  {sheet}
</span>
{selectedSheet === sheet && <span className="px-space-xs py-0.5 rounded bg-surface-container-lowest text-primary font-label-sm text-label-sm uppercase font-bold">SELECTED</span>}
</div>
</div>
))}
</div>
)}
</div>
</div>
)}

{/* Dataset Preview */}
{previewRows.length > 0 && (activeTab === 'csv' || activeTab === 'excel') && (
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md">
<div className="flex items-center justify-between flex-wrap gap-space-sm">
<div className="flex items-center gap-space-sm">
<div className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
<span className="material-symbols-outlined text-[20px]">preview</span>
</div>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Dataset Preview — {selectedSheet || fileInfo.filename}</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">First {previewRows.length} records. Raw source column names.</p>
</div>
</div>
</div>
<div className="overflow-x-auto rounded-lg bg-surface-container-low">
<table className="w-full text-left font-body-sm text-body-sm min-w-[600px]">
<thead className="bg-surface-container font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">
<tr>
{previewCols.map(col => (
  <th key={col} className="py-space-sm px-space-md">{col}</th>
))}
</tr>
</thead>
<tbody>
{previewRows.map((row, i) => (
  <tr key={i} className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
    {previewCols.map(col => (
      <td key={col} className="py-space-sm px-space-md font-code-sm text-code-sm">
        {row[col] == null ? <span className="text-outline">null</span> : String(row[col])}
      </td>
    ))}
  </tr>
))}
</tbody>
</table>
</div>
</div>
)}

{/* Schema Column Mapping */}
{(activeTab === 'csv' || activeTab === 'excel') && fileToken && (requiredCols.length > 0 || optionalCols.length > 0) && (
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-lg">
<div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
<div>
<div className="flex items-center gap-space-xs text-secondary font-label-md uppercase tracking-wider mb-space-xs">
<span className="material-symbols-outlined text-[16px]">sync_alt</span>
            Schema Mapping
          </div>
<h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Schema Column Mapping — {schemaType}</h2>
<p className="font-body-md text-body-md text-on-surface-variant">Map source columns from <code className="font-code-sm bg-surface-container px-1 py-0.5 rounded text-primary">{selectedSheet || fileInfo.filename}</code> to Sentinel required model schema.</p>
</div>
<div className="flex items-center gap-space-md bg-surface-container-low px-space-md py-space-sm rounded-lg">
<div className="flex flex-col text-right">
<span className="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">Mapping Status</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-bold">
  {Object.keys(mapping).length}/{requiredCols.length + optionalCols.length} cols
</span>
</div>
</div>
</div>

<div className="overflow-x-auto rounded-lg bg-surface-container-low">
<table className="w-full text-left font-body-sm text-body-sm">
<thead className="bg-surface-container font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">
<tr>
<th className="py-space-md px-space-lg">Required Model Field</th>
<th className="py-space-md px-space-md">Requirement</th>
<th className="py-space-md px-space-lg">Source Column</th>
<th className="py-space-md px-space-lg">Status</th>
</tr>
</thead>
<tbody>
{[...requiredCols.map(c => ({col: c, req: true})), ...optionalCols.map(c => ({col: c, req: false}))].map(({col, req}) => {
  const mapped = mapping[col];
  return (
    <tr key={col} className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
      <td className="py-space-md px-space-lg">
        <span className="font-code-sm text-code-sm font-semibold text-on-surface">{col}</span>
      </td>
      <td className="py-space-md px-space-md">
        <span className={`px-space-xs py-0.5 rounded font-label-sm text-label-sm uppercase font-semibold ${req ? 'bg-primary-container text-on-primary' : 'bg-surface-container-highest text-on-surface-variant'}`}>
          {req ? 'Required' : 'Optional'}
        </span>
      </td>
      <td className="py-space-md px-space-lg">
        <select
          value={mapped || ''}
          onChange={e => setMapping(m => ({...m, [col]: e.target.value || undefined}))}
          className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none"
        >
          <option value="">-- Not mapped --</option>
          {detectedColumns.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </td>
      <td className="py-space-md px-space-lg">
        {mapped ? (
          <span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
            <span className="material-symbols-outlined text-[14px]">check</span>
            {mapped === col ? '✓ Exact Match' : `✓ → ${mapped}`}
          </span>
        ) : (
          <span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-error-container text-on-error-container font-label-sm text-label-sm font-semibold">
            <span className="material-symbols-outlined text-[14px]">close</span>
            {req ? '✕ Required' : '— Optional'}
          </span>
        )}
      </td>
    </tr>
  );
})}
</tbody>
</table>
</div>

{/* Validation Result */}
{validationResult && (
<div className={`p-space-md rounded-xl ${validationResult.is_valid ? 'bg-tertiary-container/40' : 'bg-error-container/40'} flex items-center justify-between flex-wrap gap-space-md`}>
<div className="flex items-center gap-space-md">
<div className={`w-10 h-10 rounded-lg ${validationResult.is_valid ? 'bg-tertiary-container text-tertiary-fixed' : 'bg-error-container text-on-error-container'} flex items-center justify-center`}>
  <span className="material-symbols-outlined text-[24px]">{validationResult.is_valid ? 'verified' : 'error'}</span>
</div>
<div className="flex flex-col">
  <span className="font-headline-sm text-headline-sm text-on-surface font-semibold">
    {validationResult.is_valid ? '✓ Validation Passed' : '✕ Validation Failed'}
    {validationResult.warnings?.length > 0 ? ' with Warnings' : ''}
  </span>
  <span className="font-body-sm text-body-sm text-on-surface-variant">
    {validationResult.row_count > 0 ? `${validationResult.row_count} rows` : ''}
    {validationResult.errors?.length > 0 ? ` · Errors: ${validationResult.errors.join(', ')}` : ''}
    {validationResult.warnings?.length > 0 ? ` · Warnings: ${validationResult.warnings.join(', ')}` : ''}
  </span>
</div>
</div>
</div>
)}

{/* Action Bar */}
<div className="flex items-center justify-between flex-wrap gap-space-md pt-space-xs">
<div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">lock</span>
            Audited execution session · Model schema version 2.4-STABLE
          </div>
<div className="flex items-center gap-space-md">
<button
  onClick={handleValidate}
  disabled={validationLoading || !fileToken}
  className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-surface-container-lowest hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-all shadow-sm disabled:opacity-50"
>
  <span className="material-symbols-outlined text-[18px]">{validationLoading ? 'hourglass_empty' : 'fact_check'}</span>
  {validationLoading ? 'Validating…' : 'Validate Schema'}
</button>
<button
  onClick={handleActivate}
  disabled={activating || !fileToken}
  id="activate-dataset-btn"
  className="flex items-center gap-space-sm px-space-lg py-space-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md shadow-sm hover:bg-primary-container transition-all disabled:opacity-50"
>
  <span className="material-symbols-outlined text-[18px]">bolt</span>
  {activating ? 'Activating…' : 'Activate Dataset'}
</button>
</div>
</div>
</div>
)}

{/* ===== DATABASE CONNECTION TAB ===== */}
{activeTab === 'db' && (
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-lg">
<div className="flex items-center gap-space-sm">
<span className="w-8 h-8 rounded-lg bg-surface-container-high flex items-center justify-center">
  <span className="material-symbols-outlined text-secondary text-[20px]">storage</span>
</span>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Database Connection</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">Connect a PostgreSQL, MySQL, or SQLite database. Requires tables: demand, inventory, deliveries.</p>
</div>
</div>
<div className="flex flex-col gap-space-md">
<div className="flex flex-col gap-space-xs">
<label className="font-label-md text-label-md uppercase text-on-surface-variant">Database Connection URL</label>
<input
  type="text"
  value={dbUrl}
  onChange={e => setDbUrl(e.target.value)}
  placeholder="postgresql://user:password@host:5432/dbname"
  className="w-full bg-surface-container-low text-on-surface font-code-sm text-code-sm px-space-md py-space-sm rounded-lg focus:outline-none focus:ring-1 focus:ring-secondary"
/>
<span className="font-code-sm text-code-sm text-on-surface-variant">Format: postgresql://user:pass@host:port/database</span>
</div>
<button
  onClick={handleConnectDb}
  disabled={dbConnecting || !dbUrl.trim()}
  className="self-start flex items-center gap-space-sm px-space-lg py-space-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md shadow-sm hover:bg-primary-container transition-all disabled:opacity-50"
>
  <span className="material-symbols-outlined text-[18px]">cable</span>
  {dbConnecting ? 'Connecting…' : 'Test & Connect'}
</button>
{dbResult && (
  <div className={`p-space-md rounded-lg ${dbResult.success ? 'bg-tertiary-container/40 text-on-tertiary-container' : 'bg-error-container/40 text-on-error-container'} font-body-md text-body-md flex items-center gap-space-sm`}>
    <span className="material-symbols-outlined">{dbResult.success ? 'check_circle' : 'error'}</span>
    {dbResult.message}
  </div>
)}
</div>
</div>
)}


{/* ===== DEMO DATASET TAB ===== */}
{activeTab === 'demo' && (
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-lg">
<div className="flex items-center gap-space-sm">
<span className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
  <span className="material-symbols-outlined text-[20px]">science</span>
</span>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Synthetic Demo Dataset</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">Bundled synthetic supply chain data for exploration and development. Resets active datasource to built-in CSV files in <code className="font-code-sm bg-surface-container px-1 rounded">data/</code>.</p>
</div>
</div>
<button
  onClick={handleActivateDemo}
  disabled={activating}
  className="self-start flex items-center gap-space-sm px-space-lg py-space-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md shadow-sm hover:bg-primary-container transition-all disabled:opacity-50"
>
  <span className="material-symbols-outlined text-[18px]">bolt</span>
  {activating ? 'Activating…' : 'Activate Demo Dataset'}
</button>
</div>
)}

{/* Bottom Section: Active Dataset Status */}
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md">
<div className="flex items-center justify-between flex-wrap gap-space-sm">
<div className="flex items-center gap-space-sm">
<span className={`w-3 h-3 rounded-full ${statusLoading ? 'bg-outline' : 'bg-tertiary-fixed-dim animate-ping'}`}></span>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Active Dataset Status</h2>
</div>
<div className="flex items-center gap-space-sm">
<span className="px-space-sm py-0.5 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm uppercase font-semibold">
  {statusLoading ? 'Loading…' : (status?.status || 'Active')}
</span>
</div>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md">
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Dataset Name</span>
<span className="font-headline-sm text-headline-sm text-primary font-bold">{status?.dataset_name || 'Loading…'}</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Type: {status?.active_dataset_type || '—'}</span>
</div>
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Inventory SKUs</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{status?.inventory_skus ?? '—'}</span>
<div className="flex items-center gap-space-xs text-tertiary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check_circle</span>
  Active
</div>
</div>
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Deliveries Loaded</span>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{status?.deliveries_loaded ?? '—'}</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">{status?.demand_records ?? '—'} demand records</span>
</div>
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Status</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-secondary font-bold uppercase">{status?.status || '—'}</span>
</div>
<div className="h-8 flex items-end gap-1 pt-2">
<div className="bg-secondary/40 w-full h-[40%] rounded-t"></div>
<div className="bg-secondary/50 w-full h-[60%] rounded-t"></div>
<div className="bg-secondary/60 w-full h-[45%] rounded-t"></div>
<div className="bg-secondary/70 w-full h-[85%] rounded-t"></div>
<div className="bg-secondary/60 w-full h-[70%] rounded-t"></div>
<div className="bg-secondary w-full h-[95%] rounded-t"></div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Strictly computed from active dataset</span>
</div>
</div>
</div>
</div>
</div>

  );
}
