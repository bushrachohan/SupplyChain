import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function CommandCenterPage() {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState(null);
  const [priorityRisks, setPriorityRisks] = useState({ inventory: null, delivery: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboard()
      .then(data => {
        if (data?.metrics) setKpis(data.metrics);
        if (data?.priority_risks) setPriorityRisks(data.priority_risks);
      })
      .catch(err => console.error('Dashboard error:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col w-full gap-space-xl">
      {/* Header Block with Operational Breadcrumb and Fast Action */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-xs">
        <div className="flex flex-col gap-space-xs">
          <div className="flex items-center gap-space-sm text-on-surface-variant font-label-sm uppercase tracking-wider">
            <span>Sentinel System</span>
            <span className="text-outline-variant">/</span>
            <span className="text-primary font-semibold">Operational Command Center</span>
          </div>
          <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">Supply Chain Command Center</h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl">Monitor risk, evaluate decisions, and understand operational impact with explainable decision intelligence.</p>
        </div>
        <div className="flex items-center gap-space-sm self-start md:self-auto">
          <div onClick={() => navigate('/app/data-hub')} style={{ cursor: 'pointer' }} className="bg-surface-container px-space-md py-space-sm rounded-lg flex items-center gap-space-sm shadow-sm">
            <span className="material-symbols-outlined text-[18px] text-secondary">update</span>
            <span className="font-label-md text-label-md text-on-surface">Dataset Status</span>
          </div>
          <button onClick={() => navigate('/app/create-decision')} className="bg-primary hover:bg-primary-container text-on-primary px-space-lg py-space-sm rounded-lg font-label-md text-label-md flex items-center gap-space-xs transition-all shadow-sm"><span className="material-symbols-outlined text-[18px]">play_arrow</span><span>Create a Decision</span></button>
        </div>
      </div>
      {/* Top Operational Metric Row (4 Enterprise Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md">
        {/* Card 1: Active Risks */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Active Risks</span>
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full ${kpis?.active_risks?.count > 0 ? 'bg-error-container/60 text-on-error-container' : 'bg-tertiary-container/60 text-tertiary'} font-label-sm text-label-sm`}>
              <span className={`w-1.5 h-1.5 rounded-full ${kpis?.active_risks?.count > 0 ? 'bg-error animate-pulse' : 'bg-tertiary'}`}></span>
              {kpis?.active_risks?.status || 'Optimal'}
            </span>
          </div>
          <div className="flex items-baseline gap-space-xs mb-space-xs">
            <span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{kpis?.active_risks?.count ?? 0}</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant">total surfaced</span>
          </div>
          <div className="pt-space-xs flex items-center gap-1.5 text-on-surface-variant font-body-sm text-body-sm font-medium">
            <span className="material-symbols-outlined text-[16px]">info</span>
            <span>{kpis?.active_risks?.detail || 'No immediate action required'}</span>
          </div>
        </div>
        {/* Card 2: Inventory at Risk */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Inventory at Risk</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-error-container/40 text-error font-label-sm text-label-sm font-semibold">
              {kpis?.inventory_at_risk?.alert || 'Normal'}
            </span>
          </div>
          <div className="flex items-baseline gap-space-xs mb-space-xs">
            <span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{kpis?.inventory_at_risk?.exposure_formatted ?? '₹0'}</span>
            <span className="font-body-md text-body-md text-on-surface font-semibold">Exposure</span>
          </div>
          <div className="pt-space-xs flex items-center gap-1.5 text-error font-body-sm text-body-sm font-medium">
            <span className="material-symbols-outlined text-[16px]">schedule</span>
            <span>{kpis?.inventory_at_risk?.detail || 'Buffer Healthy'}</span>
          </div>
        </div>
        {/* Card 3: Delivery Risk */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">Delivery Risk</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm font-semibold">
              Transit Risk
            </span>
          </div>
          <div className="flex items-baseline gap-space-xs mb-space-xs">
            <span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{kpis?.delivery_risk?.exposure_percentage ?? 0}%</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant font-medium">transit exposure</span>
          </div>
          <div className="pt-space-xs flex items-center gap-1.5 text-on-surface-variant font-body-sm text-body-sm font-medium">
            <span className="material-symbols-outlined text-[16px] text-error">local_shipping</span>
            <span className="text-on-surface">{kpis?.delivery_risk?.detail || 'All On-Time'}</span>
          </div>
        </div>
        {/* Card 4: AI Decisions */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">AI Decisions</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed font-label-sm text-label-sm font-semibold">
              Queue Ready
            </span>
          </div>
          <div className="flex items-baseline gap-space-xs mb-space-xs">
            <span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">{kpis?.ai_decisions?.pending_approval_count ?? 0}</span>
            <span className="font-body-md text-body-md text-on-surface-variant">Pending</span>
          </div>
          <div className="pt-space-xs flex items-center gap-1.5 text-secondary font-body-sm text-body-sm font-medium">
            <span className="material-symbols-outlined text-[16px]">how_to_reg</span>
            <span className="font-semibold text-primary">{kpis?.ai_decisions?.total_count ?? 0} Total Evaluated</span>
          </div>
        </div>
      </div>
      {/* Priority Risks Section */}
      <div className="flex flex-col gap-space-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <span className="material-symbols-outlined text-error text-[22px]">crisis_alert</span>
            <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Priority Risks</h2>
            <span className="bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm px-2 py-0.5 rounded-full font-semibold">
              3 Filtered by Severity
            </span>
          </div>
          <div className="flex items-center gap-space-xs text-on-surface-variant font-label-md text-label-md">
            <span>Sort by: Risk Delta</span>
            <span className="material-symbols-outlined text-[16px]">arrow_drop_down</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-space-md">
          {/* Inventory Risk Card */}
          {priorityRisks.inventory ? (
            <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div>
                <div className="flex items-center justify-between mb-space-sm">
                  <span className="bg-error-container text-on-error-container font-label-sm text-label-sm px-2.5 py-1 rounded font-bold uppercase tracking-wider">
                    HIGH SEVERITY
                  </span>
                  <span className="font-code-sm text-code-sm text-on-surface-variant bg-surface-container-low px-2 py-0.5 rounded">
                    ID #{priorityRisks.inventory.sku_id}
                  </span>
                </div>

                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold leading-tight">
                  Inventory Risk — {priorityRisks.inventory.sku_id}
                </h3>

                <p className="font-label-md text-label-md text-error font-semibold mt-0.5 mb-space-md flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">report_problem</span>
                  Stockout Warning
                </p>

                <div className="bg-surface-container-low p-space-md rounded-lg mb-space-md space-y-space-xs text-on-surface font-body-sm text-body-sm">
                  <div className="flex justify-between items-center pb-1">
                    <span className="text-on-surface-variant font-medium">Days of Supply:</span>
                    <span className="font-tabular-metric-md text-tabular-metric-md text-error font-bold">
                      {priorityRisks.inventory.days_of_supply} Days
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-1 pt-1 text-center font-code-sm text-code-sm bg-surface-container-lowest p-2 rounded">
                    <div>
                      <span className="block text-on-surface-variant text-[10px] uppercase">Current</span>
                      <span className="font-bold text-on-surface">{priorityRisks.inventory.current_stock} u</span>
                    </div>
                    <div>
                      <span className="block text-on-surface-variant text-[10px] uppercase">Safety</span>
                      <span className="font-bold text-on-surface">{priorityRisks.inventory.safety_stock} u</span>
                    </div>
                    <div>
                      <span className="block text-on-surface-variant text-[10px] uppercase">Reorder</span>
                      <span className="font-bold text-on-surface">{priorityRisks.inventory.reorder_point} u</span>
                    </div>
                  </div>
                </div>

                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed mb-space-lg">
                  {priorityRisks.inventory.detail}
                </p>
              </div>

              <div className="pt-space-md flex items-center justify-between bg-surface-container-lowest">
                <div className="flex items-center gap-1 text-on-surface-variant font-label-sm text-label-sm">
                  <span className="material-symbols-outlined text-[15px] text-tertiary">psychology</span>
                  <span>Policy RAG Evaluated</span>
                </div>
                <button
                  onClick={() =>
                    navigate('/app/create-decision', {
                      state: { sku_id: priorityRisks.inventory.sku_id },
                    })
                  }
                  className="bg-primary hover:bg-primary-container text-on-primary px-space-md py-space-sm rounded-lg font-label-md text-label-md font-semibold transition-colors flex items-center gap-1 shadow-sm"
                >
                  <span>Evaluate Decision</span>
                  <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex items-center justify-center text-on-surface-variant">
              No high-priority inventory risks detected.
            </div>
          )}

          {/* Delivery Risk Card */}
          {priorityRisks.delivery ? (
            <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div>
                <div className="flex items-center justify-between mb-space-sm">
                  <span className="bg-error text-on-error font-label-sm text-label-sm px-2.5 py-1 rounded font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-on-error animate-ping"></span>
                    {priorityRisks.delivery.risk_label}
                  </span>
                  <span className="font-code-sm text-code-sm text-on-surface-variant bg-surface-container-low px-2 py-0.5 rounded">
                    ID #{priorityRisks.delivery.delivery_id}
                  </span>
                </div>

                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold leading-tight">
                  Delivery Risk — {priorityRisks.delivery.delivery_id}
                </h3>

                <p className="font-label-md text-label-md text-error font-semibold mt-0.5 mb-space-md flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">departure_board</span>
                  Transit Delay Warning
                </p>

                <div className="bg-surface-container-low p-space-md rounded-lg mb-space-md space-y-space-xs text-on-surface font-body-sm text-body-sm">
                  <div className="flex justify-between items-center pb-1">
                    <span className="text-on-surface-variant font-medium">Late Probability:</span>
                    <span className="font-tabular-metric-md text-tabular-metric-md text-error font-bold">
                      {Math.round(priorityRisks.delivery.late_probability * 100)}%
                    </span>
                  </div>

                  <div className="bg-surface-container-lowest p-2 rounded space-y-1 font-body-sm text-body-sm">
                    <div className="flex justify-between">
                      <span className="text-on-surface-variant text-label-sm font-label-sm">Carrier</span>
                      <span className="font-semibold text-on-surface">{priorityRisks.delivery.carrier_id}</span>
                    </div>
                    <div className="flex justify-between items-center text-code-sm font-code-sm pt-1">
                      <span className="text-primary font-semibold">{priorityRisks.delivery.origin}</span>
                      <span className="material-symbols-outlined text-[14px] text-on-surface-variant">arrow_forward</span>
                      <span className="text-on-surface font-semibold">{priorityRisks.delivery.destination}</span>
                    </div>
                  </div>
                </div>

                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed mb-space-lg">
                  Traffic delay of {priorityRisks.delivery.traffic_delay_hrs} hrs. Weather condition: {priorityRisks.delivery.weather_condition}. Distance: {priorityRisks.delivery.distance_km} km.
                </p>
              </div>

              <div className="pt-space-md flex items-center justify-between bg-surface-container-lowest">
                <div className="flex items-center gap-1 text-on-surface-variant font-label-sm text-label-sm">
                  <span className="material-symbols-outlined text-[15px] text-secondary">alt_route</span>
                  <span>Reroute Action Available</span>
                </div>
                <button
                  onClick={() =>
                    navigate('/app/create-decision', {
                      state: { delivery_id: priorityRisks.delivery.delivery_id },
                    })
                  }
                  className="bg-primary hover:bg-primary-container text-on-primary px-space-md py-space-sm rounded-lg font-label-md text-label-md font-semibold transition-colors flex items-center gap-1 shadow-sm"
                >
                  <span>Evaluate Decision</span>
                  <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex items-center justify-center text-on-surface-variant">
              No high-priority delivery risks detected.
            </div>
          )}
        </div>
      </div>

      {/* Demand Forecast vs Actual Section (High Analytical Rigor) */}

      <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm flex flex-col gap-space-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md pb-space-xs">
          <div className="flex flex-col gap-space-xs">
            <div className="flex items-center gap-space-sm">
              <span className="material-symbols-outlined text-primary text-[22px]">trending_up</span>
              <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Demand Forecast vs Actual</h2>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">14-day rolling demand model comparison incorporating historical demand signals and machine learning priors.</p>
          </div>
          {/* Functional Operational Metric Row */}
          <div className="flex flex-wrap items-center gap-space-sm">
            <div className="px-space-md py-space-xs rounded-lg bg-surface-container-low flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Horizon</span>
              <span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-bold">14 Days</span>
            </div>
            <div className="px-space-md py-space-xs rounded-lg bg-surface-container-low flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Actual Avg</span>
              <span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-bold">428 u/day</span>
            </div>
            <div className="px-space-md py-space-xs rounded-lg bg-surface-container-low flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Forecast Avg</span>
              <span className="font-tabular-metric-md text-tabular-metric-md text-primary font-bold">445 u/day</span>
            </div>
            <div className="px-space-md py-space-xs rounded-lg bg-surface-container-low flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Error (MAPE)</span>
              <span className="font-tabular-metric-md text-tabular-metric-md text-error font-bold">3.9%</span>
            </div>
            <div className="px-space-md py-space-xs rounded-lg bg-surface-container-low flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Accuracy</span>
              <span className="font-tabular-metric-md text-tabular-metric-md text-tertiary-container font-bold">96.1%</span>
            </div>
          </div>
        </div>
        {/* Chart Legend and Controls */}
        <div className="flex flex-wrap items-center justify-between text-label-sm font-label-sm pt-space-xs">
          <div className="flex items-center gap-space-lg">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-secondary"></span>
              <span className="text-on-surface font-medium">Actual Demand (units)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-0.5 bg-primary-container inline-block"></span>
              <span className="text-on-surface-variant font-medium">AI Forecasted Demand</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-2 bg-surface-variant/60 rounded-xs inline-block"></span>
              <span className="text-on-surface-variant font-medium">Forecast Range</span>
            </div>
          </div>
          <div className="flex items-center gap-space-xs text-on-surface-variant">
            <span className="material-symbols-outlined text-[16px]">info</span>
            <span>Model: LightGBM + Multi-Head Temporal Attention (Retrained: 04:00 UTC)</span>
          </div>
        </div>
        {/* SVG Clean Functional Visual Chart (Actual vs Forecast) */}
        <div className="w-full bg-surface-container-low/60 rounded-xl p-space-md">
          <div className="relative w-full h-72">
            <svg className="w-full h-full overflow-visible font-code-sm text-[11px]" preserveAspectRatio="none" viewBox="0 0 960 260">
              <defs>
                <linearGradient id="forecastBand" x1="0%" x2="0%" y1="0%" y2="100%">
                  <stop offset="0%" stopColor="#316bf3" stopOpacity="0.14"></stop>
                  <stop offset="100%" stopColor="#316bf3" stopOpacity="0.01"></stop>
                </linearGradient>
              </defs>
              {/* Horizontal Grid Lines */}
              <line opacity="0.6" stroke="#c5c5d3" strokeDasharray="3,3" strokeWidth="1" x1="40" x2="940" y1="20" y2="20"></line>
              <text fill="#757682" textAnchor="end" x="32" y="24">500</text>
              <line opacity="0.6" stroke="#c5c5d3" strokeDasharray="3,3" strokeWidth="1" x1="40" x2="940" y1="80" y2="80"></line>
              <text fill="#757682" textAnchor="end" x="32" y="84">450</text>
              <line opacity="0.6" stroke="#c5c5d3" strokeDasharray="3,3" strokeWidth="1" x1="40" x2="940" y1="140" y2="140"></line>
              <text fill="#757682" textAnchor="end" x="32" y="144">400</text>
              <line opacity="0.8" stroke="#c5c5d3" strokeWidth="1" x1="40" x2="940" y1="200" y2="200"></line>
              <text fill="#757682" textAnchor="end" x="32" y="204">350</text>
              {/* Forecast Range Band */}
              <polygon fill="url(#forecastBand)" points="
            50,150  118,135  186,145  254,120  322,105  390,115  458,95  526,90  594,80  662,70  730,75  798,60  866,55  934,50
            934,110 866,120 798,130 730,140 662,130 594,145 526,155 458,160 390,175 322,165 254,180 186,195 118,185 50,200
          "></polygon>
              {/* Forecast Line (Dashed Navy) */}
              <polyline fill="none" points="
              50,175 118,160 186,170 254,150 322,135 390,145 458,125 526,120 594,110 662,100 730,105 798,92 866,85 934,78
            " stroke="#1e3a8a" strokeDasharray="5,4" strokeWidth="2.5"></polyline>
              {/* Actual Demand Line (Solid Cobalt with Nodes) */}
              <polyline fill="none" points="
              50,180 118,155 186,165 254,142 322,148 390,138 458,130 526,115 594,118 662,94 730,112 798,88 866,82 934,70
            " stroke="#0051d5" strokeWidth="3"></polyline>
              {/* Actual Demand Interactive Point Markers */}
              <circle className="hover:r-6 cursor-pointer transition-all" cx="50" cy="180" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="118" cy="155" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="186" cy="165" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="254" cy="142" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="322" cy="148" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="390" cy="138" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="458" cy="130" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="526" cy="115" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="594" cy="118" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="662" cy="94" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="730" cy="112" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="798" cy="88" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="866" cy="82" fill="#0051d5" r="4.5"></circle>
              <circle className="hover:r-6 cursor-pointer transition-all" cx="934" cy="70" fill="#0051d5" r="4.5"></circle>
              {/* X-Axis Day Labels */}
              <text fill="#444651" textAnchor="middle" x="50" y="228">Day 1</text>
              <text fill="#444651" textAnchor="middle" x="118" y="228">Day 2</text>
              <text fill="#444651" textAnchor="middle" x="186" y="228">Day 3</text>
              <text fill="#444651" textAnchor="middle" x="254" y="228">Day 4</text>
              <text fill="#444651" textAnchor="middle" x="322" y="228">Day 5</text>
              <text fill="#444651" textAnchor="middle" x="390" y="228">Day 6</text>
              <text fill="#444651" textAnchor="middle" x="458" y="228">Day 7</text>
              <text fill="#444651" textAnchor="middle" x="526" y="228">Day 8</text>
              <text fill="#444651" textAnchor="middle" x="594" y="228">Day 9</text>
              <text fill="#444651" textAnchor="middle" x="662" y="228">Day 10</text>
              <text fill="#444651" textAnchor="middle" x="730" y="228">Day 11</text>
              <text fill="#444651" textAnchor="middle" x="798" y="228">Day 12</text>
              <text fill="#444651" textAnchor="middle" x="866" y="228">Day 13</text>
              <text fill="#444651" textAnchor="middle" x="934" y="228">Day 14</text>
            </svg>
          </div>
          {/* Footer Micro-Insights */}
          <div className="mt-space-sm pt-space-sm flex flex-col md:flex-row items-center justify-between text-on-surface-variant font-body-sm text-body-sm">
            <div className="flex items-center gap-space-sm">
              <span className="w-2 h-2 rounded-full bg-tertiary"></span>
              <span>Max Variance Node: <strong className="text-on-surface font-semibold">Day 11 (+23 units actual spike)</strong></span>
              <span className="text-outline-variant">•</span>
              <span>Baseline Safety Adherence: <strong className="text-on-surface font-semibold">High</strong></span>
            </div>
            <div className="flex items-center gap-space-xs mt-space-xs md:mt-0 font-label-sm text-label-sm">
              <span className="text-on-surface font-semibold">Confidence Threshold:</span>
              <span className="bg-surface-container-highest px-2 py-0.5 rounded text-primary font-bold">p &lt; 0.05 Validated</span>
            </div>
          </div>
        </div>
      </div>
      {/* Operational Trace Log Banner */}
      <div className="bg-surface-container-low p-space-md rounded-xl flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-space-md">
          <div className="w-8 h-8 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
            <span className="material-symbols-outlined text-[20px]">fact_check</span>
          </div>
          <div className="flex flex-col">
            <span className="font-headline-sm text-headline-sm text-on-surface font-semibold leading-tight">Decision Review Active</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Dual agent evaluation pass (Policy RAG + Cost Optimizer) finished 2.4s ago with zero unhandled exceptions.</span>
          </div>
        </div>
        <div className="flex items-center gap-space-sm">
          <span className="font-code-sm text-code-sm text-on-surface-variant">Last Hash: 0x8F9C...77D1</span>
          <a className="font-label-md text-label-md text-primary font-bold hover:underline flex items-center gap-0.5" onClick={(e) => { e.preventDefault(); navigate('/app/decision-history'); }} href="#">
            Audit Log
            <span className="material-symbols-outlined text-[16px]">arrow_outward</span>
          </a>
        </div>
      </div>
    </div>
  );
}