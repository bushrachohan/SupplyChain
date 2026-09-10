/**
 * SentinelFlow API Client Layer
 * Interacts with the FastAPI backend.
 * Uses relative paths by default (proxied via Vite in dev, or VITE_API_BASE_URL if set).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = options.headers || {};

  // If body is not FormData, default to application/json
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      // response wasn't JSON
    }
    throw new Error(errorDetail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health & Dashboard
  getHealth: () => request('/api/health'),
  getDashboard: () => request('/api/dashboard'),

  // Data Hub
  getDataStatus: () => request('/api/data/status'),

  /**
   * Upload one or more CSV/Excel files.
   * Backend parameter name is "files" (List[UploadFile]).
   * Returns: { file_token, files: [{filename, columns, sheets, row_count, preview_rows}], schemas }
   */
  uploadData: (files) => {
    const formData = new FormData();
    if (Array.isArray(files)) {
      files.forEach(f => formData.append('files', f));
    } else {
      formData.append('files', files);
    }
    return request('/api/data/upload', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Suggest column mapping.
   * POST /api/data/suggest-mapping
   * Body: { existing_columns: string[], schema_type: "demand"|"inventory"|"deliveries" }
   * Returns: { schema_type, required_columns, optional_columns, suggested_mapping }
   */
  suggestMapping: (existingColumns, schemaType) => request('/api/data/suggest-mapping', {
    method: 'POST',
    body: { existing_columns: existingColumns, schema_type: schemaType },
  }),

  /**
   * Validate uploaded dataset against schema.
   * POST /api/data/validate
   * Body: { file_token, filename, schema_type, column_mapping, sheet_name? }
   * Returns: { is_valid, errors, warnings, profiling, row_count }
   */
  validateData: (fileToken, filename, schemaType, columnMapping, sheetName) => request('/api/data/validate', {
    method: 'POST',
    body: {
      file_token: fileToken,
      filename: filename,
      schema_type: schemaType,
      column_mapping: columnMapping,
      sheet_name: sheetName || null,
    },
  }),

  /**
   * Activate uploaded dataset.
   * POST /api/data/activate
   * Body: { file_token, source_type: "csv"|"excel", excel_sheet_mapping? }
   * Returns: { message, status }
   */
  activateDataset: (fileToken, sourceType, excelSheetMapping) => request('/api/data/activate', {
    method: 'POST',
    body: {
      file_token: fileToken,
      source_type: sourceType,
      excel_sheet_mapping: excelSheetMapping || null,
    },
  }),

  /**
   * Connect a relational database.
   * POST /api/data/connect-db
   * Body: { connection_url: string }
   * Returns: { message, status } or 400 on failure
   */
  connectDb: (connectionUrl) => request('/api/data/connect-db', {
    method: 'POST',
    body: { connection_url: connectionUrl },
  }),

  activateDemo: () => request('/api/data/activate-demo', { method: 'POST' }),

  // Decisions
  /**
   * GET /api/decisions/options
   * Returns: { target_types, skus: string[], deliveries: string[] }
   */
  getDecisionOptions: () => request('/api/decisions/options'),

  /**
   * POST /api/decisions/preview
   * Body: { target_type: string, target_id: string }
   * Returns: { overall_severity, bottleneck_type, impact_urgency_hours, description, cross_risk_dependencies, mitigation_options }
   */
  getDecisionPreview: (targetType, targetId) => request('/api/decisions/preview', {
    method: 'POST',
    body: { target_type: targetType, target_id: targetId },
  }),

  /**
   * GET /api/decisions/forecast-vs-actual/{sku_id}
   */
  getForecastVsActual: (skuId) => request(`/api/decisions/forecast-vs-actual/${encodeURIComponent(skuId)}`),

  /**
   * POST /api/decisions/create
   * Body: { target_type: string, target_id: string, situation_text?: string }
   * Returns: { trace_id, message }
   */
  createDecision: (targetType, targetId, situationText) => request('/api/decisions/create', {
    method: 'POST',
    body: {
      target_type: targetType,
      target_id: targetId,
      situation_text: situationText || '',
    },
  }),

  // Traces & Approvals
  getTraces: () => request('/api/traces'),
  getTrace: (traceId) => request(`/api/traces/${encodeURIComponent(traceId)}`),

  /**
   * POST /api/traces/{trace_id}/approval
   * Body: { status: "approved"|"rejected", approver?: string, notes?: string }
   */
  submitApproval: (traceId, status, approver, notes) => request(`/api/traces/${encodeURIComponent(traceId)}/approval`, {
    method: 'POST',
    body: { status, approver: approver || 'Ops Lead', notes: notes || null },
  }),

  /**
   * GET /api/approvals
   * Returns: Array of { trace_id, timestamp, severity, situation_summary, recommended_action, reviewer, status }
   */
  getApprovals: () => request('/api/approvals'),
  getRecommendations: () => request('/api/recommendations'),

  // History
  getHistory: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/history${query ? `?${query}` : ''}`);
  },
  exportHistoryCsvUrl: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return `${API_BASE}/api/history/export${query ? `?${query}` : ''}`;
  },

  // What-If Simulation
  getSimulationOptions: () => request('/api/simulations/options'),
  simulateInventory: (payload) => request('/api/simulations/inventory', {
    method: 'POST',
    body: payload,
  }),
  simulateDelivery: (payload) => request('/api/simulations/delivery', {
    method: 'POST',
    body: payload,
  }),
  simulateLogistics: (payload) => request('/api/simulations/logistics', {
    method: 'POST',
    body: payload,
  }),
};
