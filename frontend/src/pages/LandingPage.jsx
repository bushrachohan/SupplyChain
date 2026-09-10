import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();
  const handleLaunch = () => navigate('/app/command-center');

  return (
    <div className="min-h-screen flex flex-col justify-between selection:bg-teal-100 selection:text-teal-900 selection:bg-teal-100 selection:text-teal-900" style={{fontFamily: "'Plus Jakarta Sans', sans-serif", backgroundColor: '#fcfcfd', color: '#0f172a'}}>


  {/* TOP STATUS BANNER (Restrained enterprise badge) */}
  <div className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 text-[11px] font-mono py-1.5 px-4 sm:px-8 flex items-center justify-between">
    <div className="flex items-center gap-2">
      <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      <span className="tracking-wider uppercase">Operational Intelligence v2.4</span>
      <span className="text-slate-300">|</span>
      <span className="hidden sm:inline text-slate-600">Decision Telemetry Active</span>
    </div>
    <div className="flex items-center gap-4 text-slate-500">
      <span className="hidden md:inline">Deterministic Simulation Engine</span>
      <span className="text-slate-400">Decision Trace Active</span>
    </div>
  </div>

  {/* STICKY NAVBAR */}
  <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-slate-200/80 transition-all">
    <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
      {/* Left: Brand Logo & Name */}
      <a href="#" className="flex items-center gap-2.5 group">
        <div className="w-8 h-8 rounded-md bg-teal-900 flex items-center justify-center text-white shadow-xs border border-teal-800">
          <svg className="w-4 h-4 text-teal-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            <path d="m9 12 2 2 4-4"></path>
          </svg>
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-slate-900 text-sm sm:text-base tracking-tight leading-none group-hover:text-teal-900 transition-colors">
            SupplyChain Sentinel <span className="text-teal-700 font-bold">AI</span>
          </span>
          <span className="text-[10px] text-slate-400 font-medium tracking-wide uppercase mt-0.5">Decision Intelligence</span>
        </div>
      </a>

      {/* Right: Nav Links + Action */}
      <div className="flex items-center gap-1 sm:gap-6">
        <nav className="hidden md:flex items-center gap-5 text-xs sm:text-sm font-medium text-slate-600">
          <a href="#" className="hover:text-slate-900 transition-colors py-1">Intelligence</a>
          <a href="#" className="hover:text-slate-900 transition-colors py-1">Capabilities</a>
          <a href="#" className="hover:text-slate-900 transition-colors py-1">Architecture</a>
          <a href="#" className="hover:text-slate-900 transition-colors py-1">About</a>
        </nav>

        <button onClick={handleLaunch} className="inline-flex items-center gap-1.5 px-3.5 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium text-white bg-slate-900 hover:bg-teal-900 rounded-md transition-all shadow-xs active:scale-[0.98] border border-slate-800">
          <span className="">Launch Sentinel</span>
          <span className="text-teal-300">→</span>
        </button>
      </div>
    </div>
  </header>

  {/* MAIN CONTENT CONTAINER */}
  <main id="top" className="flex-grow">
    
    {/* HERO SECTION (Compact, High-Precision, No Bloat) */}
    <section className="relative pt-10 sm:pt-16 pb-12 sm:pb-16 border-b border-slate-200/70 overflow-hidden grid-subtle">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          
          {/* Hero Text (Left 7 Cols) */}
          <div className="lg:col-span-7 flex flex-col items-start">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-teal-50 border border-teal-200 text-teal-800 text-xs font-medium mb-4">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-600"></span>
              <span className="">Enterprise Decision Platform</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-bold text-slate-950 tracking-tight leading-[1.18] mb-4">
              Predict. Detect. Decide.<br className="hidden sm:inline" /> Before disruption happens.
            </h1>

            <p className="text-slate-600 text-base sm:text-lg leading-relaxed mb-7 max-w-xl font-normal">
              AI-powered supply-chain intelligence that turns operational data into explainable, actionable decisions.
            </p>

            {/* Action CTAs */}
            <div className="flex flex-wrap items-center gap-3 mb-6">
              <button onClick={handleLaunch} className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-teal-800 hover:bg-teal-900 rounded-md shadow-xs transition-colors border border-teal-700">
                <span className="">Launch Sentinel</span>
                <span className="text-teal-200 font-bold">→</span>
              </button>
              <a href="#" className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 hover:text-slate-950 bg-white hover:bg-slate-50 rounded-md border border-slate-300 transition-colors">
                <span className="">Explore Intelligence</span>
              </a>
            </div>

            {/* Subtle Capability Line */}
            <div className="pt-3 border-t border-slate-200/80 w-full">
              <p className="text-[12px] sm:text-[13px] text-slate-500 font-medium tracking-wide">
                <span className="text-slate-700 font-semibold">Core Vectors:</span> Demand Forecasting <span className="text-slate-300">·</span> Risk Detection <span className="text-slate-300">·</span> Inventory Intelligence <span className="text-slate-300">·</span> Logistics Optimization
              </p>
            </div>
          </div>

          {/* Hero Abstract Intelligence Flow Visual (Right 5 Cols - Compact & Focused) */}
          <div className="lg:col-span-5 w-full">
            <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-sm">
              {/* Window header */}
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-200"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-200"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-200"></div>
                  <span className="text-[11px] font-mono text-slate-400 ml-2">sentinel-runtime.flow</span>
                </div>
                <span className="font-mono text-[10px] text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-100">Decision Intelligence</span>
              </div>

              {/* Compact Abstract Representation: Data → AI Intelligence → Decision */}
              <div className="space-y-3">
                
                {/* Stage 1: Data Node */}
                <div className="flex items-start gap-3 p-2.5 rounded-md bg-slate-50 border border-slate-200/70">
                  <div className="w-7 h-7 rounded bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7M4 7c0-2 1.5-3 3.5-3h9c2 0 3.5 1 3.5 3M4 7s1.5 2 3.5 2h9c2 0 3.5-2 3.5-2"></path></svg>
                  </div>
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-800">1. Operational Data</span>
                      <span className="text-[10px] font-mono text-slate-500">CSV · Excel · Database · API</span>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-tight mt-0.5 truncate">Ingesting operational supply-chain data and demand signals.</p>
                  </div>
                </div>

                {/* Downlink connector */}
                <div className="flex justify-center -my-1.5">
                  <div className="w-px h-3.5 bg-slate-300"></div>
                </div>

                {/* Stage 2: AI Intelligence Node */}
                <div className="flex items-start gap-3 p-2.5 rounded-md bg-teal-50/60 border border-teal-200">
                  <div className="w-7 h-7 rounded bg-teal-700 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                  </div>
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-teal-950">2. Sentinel AI Engine</span>
                      <span className="text-[10px] font-mono text-teal-700">Predictive + Policy-Aware</span>
                    </div>
                    <p className="text-[11px] text-teal-800 leading-tight mt-0.5">Evaluating buffer risk, demand variance, and network capacity.</p>
                  </div>
                </div>

                {/* Downlink connector */}
                <div className="flex justify-center -my-1.5">
                  <div className="w-px h-3.5 bg-teal-300"></div>
                </div>

                {/* Stage 3: Explainable Decision Node */}
                <div className="flex items-start gap-3 p-2.5 rounded-md bg-white border border-slate-300 shadow-xs">
                  <div className="w-7 h-7 rounded bg-slate-900 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  </div>
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-900">3. Actionable Decision</span>
                      <span className="text-[10px] font-mono text-emerald-700 font-medium">Human-in-the-Loop</span>
                    </div>
                    <div className="mt-1 flex items-center justify-between bg-slate-50 px-2 py-1 rounded border border-slate-200/60 text-[11px]">
                      <span className="text-slate-700 truncate">Re-allocate 1,200 units to Hub B</span>
                      <span className="text-emerald-700 font-semibold shrink-0 ml-2">Awaiting Approval</span>
                    </div>
                  </div>
                </div>

              </div>

              {/* Metric footer in card */}
              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono"><span className="text-slate-600">Policy-Aware</span><span className="">Human-in-the-Loop</span></div>

            </div>
          </div>

        </div>
      </div>
    </section>

    {/* VALUE STRIP (Compact Horizontal Section - 4 Capabilities) */}
    <section id="capabilities" className="py-8 bg-white border-b border-slate-200/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          
          {/* Item 1: Demand */}
          <div className="p-4 rounded-md border border-slate-200 bg-slate-50/40 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-6 h-6 rounded bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
              </div>
              <h3 className="text-sm font-semibold text-slate-900">Demand</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">Forecast future demand across SKU clusters and identify changing demand patterns.</p>
          </div>

          {/* Item 2: Inventory */}
          <div className="p-4 rounded-md border border-slate-200 bg-slate-50/40 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-6 h-6 rounded bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
              </div>
              <h3 className="text-sm font-semibold text-slate-900">Inventory</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Detect stockout and overstock risk before safety buffers are compromised.
            </p>
          </div>

          {/* Item 3: Delivery */}
          <div className="p-4 rounded-md border border-slate-200 bg-slate-50/40 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-6 h-6 rounded bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <h3 className="text-sm font-semibold text-slate-900">Delivery</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">Identify delivery-delay risk and the factors contributing to it.</p>
          </div>

          {/* Item 4: Logistics */}
          <div className="p-4 rounded-md border border-slate-200 bg-slate-50/40 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-6 h-6 rounded bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>
              </div>
              <h3 className="text-sm font-semibold text-slate-900">Logistics</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">Evaluate routing and capacity decisions under operational constraints.</p>
          </div>

        </div>
      </div>
    </section>

    {/* INTELLIGENCE SECTION (Unified Layer + Clean Horizontal Flow) */}
    <section id="intelligence" className="py-12 sm:py-16 bg-[#fcfcfd] border-b border-slate-200/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        
        <div className="max-w-2xl mb-10">
          <span className="text-[11px] font-mono uppercase tracking-wider text-teal-700 font-semibold">Architecture</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-950 tracking-tight mt-1 mb-3">
            One intelligence layer for the supply chain.
          </h2>
          <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
            Sentinel combines predictive models, operational rules, policy knowledge and AI reasoning to help teams move from risk detection to informed action.
          </p>
        </div>

        {/* Clean Horizontal Flow Visual: DATA → PREDICT → DETECT → RECOMMEND → APPROVE */}
        <div className="bg-white rounded-lg border border-slate-200 p-5 sm:p-7 shadow-xs">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-4 sm:mb-6 flex items-center justify-between border-b border-slate-100 pb-2"><span className="">Decision Intelligence Pipeline</span><span className="text-teal-700 font-medium">Decision Workflow</span></div>

          {/* Flow Container */}
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 relative">
            
            {/* Step 1: DATA */}
            <div className="flex flex-col p-3.5 rounded bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-slate-400 font-semibold">STAGE 01</span>
                <span className="w-2 h-2 rounded-full bg-slate-400"></span>
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Data</h4>
              <p className="text-[11px] text-slate-500 leading-tight">Operational supply-chain data from supported sources.</p>
            </div>

            {/* Step 2: PREDICT */}
            <div className="flex flex-col p-3.5 rounded bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-teal-700 font-semibold">STAGE 02</span>
                <span className="w-2 h-2 rounded-full bg-teal-500"></span>
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Predict</h4>
              <p className="text-[11px] text-slate-500 leading-tight">Demand spikes, transit variance, lead times.</p>
            </div>

            {/* Step 3: DETECT */}
            <div className="flex flex-col p-3.5 rounded bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-amber-700 font-semibold">STAGE 03</span>
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Detect</h4>
              <p className="text-[11px] text-slate-500 leading-tight">Stockout thresholds, bottleneck risk markers.</p>
            </div>

            {/* Step 4: RECOMMEND */}
            <div className="flex flex-col p-3.5 rounded bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-teal-700 font-semibold">STAGE 04</span>
                <span className="w-2 h-2 rounded-full bg-teal-600"></span>
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Recommend</h4>
              <p className="text-[11px] text-slate-500 leading-tight">Candidate replenishment and logistics actions.</p>
            </div>

            {/* Step 5: APPROVE */}
            <div className="flex flex-col p-3.5 rounded bg-teal-50/50 border border-teal-300/80">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-emerald-700 font-semibold">STAGE 05</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-teal-950 mb-1">Approve</h4>
              <p className="text-[11px] text-teal-800 leading-tight">Human approval when required, verified audit trail before operational commitment.</p>
            </div>

          </div>

          {/* Flow Indicator Description */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-500 gap-2">
            <span className="flex items-center gap-1.5">
              <span className="text-emerald-600 font-bold">✓</span>
              Every recommendation is grounded in verifiable operational constraints.
            </span>
            <span className="font-mono text-slate-400">Explainable recommendations · Human approval</span>
          </div>

        </div>

      </div>
    </section>

    {/* DECISION INTELLIGENCE SECTION (More than prediction - 3 Compact Cards) */}
    <section id="architecture" className="py-12 sm:py-16 bg-white border-b border-slate-200/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        
        <div className="max-w-2xl mb-8">
          <span className="text-[11px] font-mono uppercase tracking-wider text-teal-700 font-semibold">Beyond Simple Forecasting</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-950 tracking-tight mt-1 mb-2">
            Closed-Loop Decision Intelligence
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Forecasting alone does not prevent disruptions. Sentinel pairs predictive accuracy with policy verification and simulation to deliver validated operational decisions.
          </p>
        </div>

        {/* 3 Compact Cards: Predict, Explain, Decide */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          {/* Card 1: Predict */}
          <div className="p-5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-all shadow-xs flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-slate-100 text-slate-800 flex items-center justify-center font-mono font-bold text-xs mb-3.5 border border-slate-200">
                01
              </div>
              <h3 className="text-base font-semibold text-slate-900 mb-2">Predict</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Demand and delivery risk models identify potential operational risks across SKUs, lead times, and deliveries.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">Demand &amp; Risk Models</div>
          </div>

          {/* Card 2: Explain */}
          <div className="p-5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-all shadow-xs flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-teal-50 text-teal-800 flex items-center justify-center font-mono font-bold text-xs mb-3.5 border border-teal-200">
                02
              </div>
              <h3 className="text-base font-semibold text-slate-900 mb-2">Explain</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Explainable AI and policy context show why the risk exists, surfacing specific root causes, operational constraints and relevant policy context.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-teal-700">
              Clear Attribution &amp; Audit Logs
            </div>
          </div>

          {/* Card 3: Decide */}
          <div className="p-5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-all shadow-xs flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-slate-900 text-teal-300 flex items-center justify-center font-mono font-bold text-xs mb-3.5 border border-slate-800">
                03
              </div>
              <h3 className="text-base font-semibold text-slate-900 mb-2">Decide</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Candidate actions, what-if simulation and human approval support the next decision, ensuring humans maintain full authority.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-700">
              What-If Scenarios &amp; Human Approval
            </div>
          </div>

        </div>

      </div>
    </section>

    {/* FINAL CTA (Simple Centered Section) */}
    <section className="py-14 sm:py-16 bg-[#f8fafc] border-b border-slate-200/80 text-center">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-950 tracking-tight mb-2">
          Turn supply-chain data into decisions.
        </h2>
        <p className="text-sm sm:text-base text-slate-600 mb-6 max-w-lg mx-auto">Explore the Sentinel decision platform and evaluate operational decisions with explainable recommendations.</p>
        <div>
          <button onClick={handleLaunch} className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-slate-900 hover:bg-teal-900 rounded-md transition-all shadow-xs active:scale-[0.98] border border-slate-800">
            <span className="">Launch Sentinel</span>
            <span className="text-teal-300">→</span>
          </button>
        </div>
        
      </div>
    </section>

  </main>

  {/* FOOTER (Minimal, No Sitemap) */}
  <footer id="about" className="bg-white border-t border-slate-200/80 py-6 sm:py-8 text-xs text-slate-500">
    <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 rounded bg-slate-900 text-teal-300 flex items-center justify-center text-[10px] font-bold">S</div>
        <span className="font-semibold text-slate-900">SupplyChain Sentinel AI</span>
        <span className="text-slate-300">|</span>
        <span className="text-slate-500 text-[11px] sm:text-xs">AI-powered supply-chain decision intelligence.</span>
      </div>
      <div className="text-[11px] font-mono text-slate-400">AI-Powered Supply-Chain Decision Intelligence</div>
    </div>
  </footer>







    </div>
  );
}
