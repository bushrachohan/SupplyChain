<div className="flex flex-col w-full">
<div className="flex flex-col gap-space-xl">
{/*  Top Execution & Progress Ribbon  */}
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
{/*  Linear Workflow Tracker  */}
<div className="bg-surface-container-lowest p-space-sm rounded-xl shadow-sm flex items-center gap-space-xs overflow-x-auto min-w-0">
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-surface-container-high text-primary">
<span className="font-code-sm text-code-sm font-semibold">01</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Upload</span>
<span className="material-symbols-outlined text-[14px]">check_circle</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-surface-container-high text-primary">
<span className="font-code-sm text-code-sm font-semibold">02</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Inspect</span>
<span className="material-symbols-outlined text-[14px]">check_circle</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-primary-container text-on-primary shadow-sm">
<span className="font-code-sm text-code-sm font-semibold">03</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Select Sheet</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-container text-on-secondary-container">
<span className="font-code-sm text-code-sm font-semibold">04</span>
<span className="font-label-sm text-label-sm font-semibold uppercase">Map Schema</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-surface-container text-on-surface-variant">
<span className="font-code-sm text-code-sm">05</span>
<span className="font-label-sm text-label-sm uppercase">Validate</span>
</div>
<span className="text-outline-variant text-[12px]">→</span>
<div className="flex items-center gap-space-xs px-space-sm py-1 rounded bg-surface-container text-on-surface-variant">
<span className="font-code-sm text-code-sm">06</span>
<span className="font-label-sm text-label-sm uppercase">Activate</span>
</div>
</div>
</div>
{/*  Supported Data Sources Tabs  */}
<div className="bg-surface-container-lowest p-space-xs rounded-xl shadow-sm flex items-center justify-between overflow-x-auto">
<div className="flex items-center gap-space-xs">
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md transition-all shadow-sm">
<span className="material-symbols-outlined text-[18px]">table_chart</span>
          Excel Upload
        </button>
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all">
<span className="material-symbols-outlined text-[18px]">description</span>
          CSV Upload
        </button>
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all">
<span className="material-symbols-outlined text-[18px]">database</span>
          Database Connection
        </button>
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all">
<span className="material-symbols-outlined text-[18px]">api</span>
          API Connection
        </button>
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-label-md text-label-md transition-all">
<span className="material-symbols-outlined text-[18px]">dataset</span>
          Demo Dataset
        </button>
</div>
<div className="pr-space-md hidden sm:flex items-center gap-space-xs font-label-sm text-label-sm text-on-surface-variant">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">verified_user</span>
        In-Memory RAG Parser Active
      </div>
</div>
{/*  Workbook Inspection Section  */}
<div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
{/*  File Metadata Card  */}
<div className="lg:col-span-4 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between">
<div className="flex flex-col gap-space-sm">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">Active Workbook File</span>
<span className="px-space-sm py-0.5 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm uppercase font-semibold">Ready</span>
</div>
<div className="flex items-center gap-space-md mt-space-xs">
<div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center shrink-0">
<span className="material-symbols-outlined text-secondary text-[26px]">grid_on</span>
</div>
<div className="min-w-0">
<div className="font-headline-sm text-headline-sm text-on-surface truncate font-semibold">supply_chain_operations_master.xlsx</div>
<div className="font-body-sm text-body-sm text-on-surface-variant">File size: 2.4 MB • Uploaded: Today, 09:14 AM</div>
</div>
</div>
</div>
<div className="mt-space-lg pt-space-md bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-xs">
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Workbook Hash (SHA-256)</span>
<span className="font-code-sm text-code-sm text-on-surface">d98f7e2c...41ba</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Total Parsed Rows</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">5,630 rows</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
<span>Detected Sheets</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-semibold">5 sheets</span>
</div>
</div>
</div>
{/*  Detected Sheets Selector Pills  */}
<div className="lg:col-span-8 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">Detected Sheets in Workbook</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Click to toggle active target schema</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">Select the target sheet to run the heuristic schema auto-mapping against Sentinel core entities.</p>
</div>
<div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-space-sm mt-space-md">
{/*  Sheet 1  */}
<div className="p-space-md rounded-lg bg-surface-container-low hover:bg-surface-container-high transition-all cursor-pointer flex flex-col gap-1">
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm text-on-surface font-medium">README</span>
<span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm uppercase font-semibold">Info</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">Workbook instructions &amp; legend</span>
</div>
{/*  Sheet 2  */}
<div className="p-space-md rounded-lg bg-surface-container-low hover:bg-surface-container-high transition-all cursor-pointer flex flex-col gap-1">
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm text-on-surface font-medium">historical_demand</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface-variant">3,240</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">SKU velocity by distribution tier</span>
</div>
{/*  Sheet 3  */}
<div className="p-space-md rounded-lg bg-surface-container-low hover:bg-surface-container-high transition-all cursor-pointer flex flex-col gap-1">
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm text-on-surface font-medium">inventory_snapshot</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface-variant">820</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">Current DC inventory &amp; reorder points</span>
</div>
{/*  Sheet 4 (SELECTED)  */}
<div className="p-space-md rounded-lg bg-primary-container text-on-primary shadow-sm relative flex flex-col gap-1 ring-2 ring-secondary-container">
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm font-semibold flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px]">radio_button_checked</span>
                deliveries
              </span>
<span className="px-space-xs py-0.5 rounded bg-surface-container-lowest text-primary font-label-sm text-label-sm uppercase font-bold">SELECTED</span>
</div>
<div className="flex items-center justify-between text-on-primary-container font-body-sm text-body-sm">
<span>1,450 rows ingested</span>
<span className="font-code-sm text-code-sm text-on-primary">10 Columns</span>
</div>
</div>
{/*  Sheet 5  */}
<div className="p-space-md rounded-lg bg-surface-container-low hover:bg-surface-container-high transition-all cursor-pointer flex flex-col gap-1">
<div className="flex items-center justify-between">
<span className="font-headline-sm text-headline-sm text-on-surface font-medium">demo_scenarios</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface-variant">120</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">Synthetic stress test conditions</span>
</div>
</div>
</div>
</div>
{/*  Dataset Preview Card  */}
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md">
<div className="flex items-center justify-between flex-wrap gap-space-sm">
<div className="flex items-center gap-space-sm">
<div className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
<span className="material-symbols-outlined text-[20px]">preview</span>
</div>
<div>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Dataset Preview (deliveries)</h2>
<p className="font-body-sm text-body-sm text-on-surface-variant">First 4 records of 1,450 ingested items. Showing raw source column naming.</p>
</div>
</div>
<div className="flex items-center gap-space-sm">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Displaying</span>
<span className="px-space-sm py-1 rounded bg-surface-container font-code-sm text-code-sm text-on-surface font-semibold">Rows 1 - 4 of 1,450</span>
</div>
</div>
{/*  Compact Preview Table  */}
<div className="overflow-x-auto rounded-lg bg-surface-container-low">
<table className="w-full text-left font-body-sm text-body-sm min-w-[960px]">
<thead className="bg-surface-container font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">
<tr>
<th className="py-space-sm px-space-md">delivery_id</th>
<th className="py-space-sm px-space-md">carrier_id</th>
<th className="py-space-sm px-space-md">origin_hub</th>
<th className="py-space-sm px-space-md">destination_dc</th>
<th className="py-space-sm px-space-md">distance_km</th>
<th className="py-space-sm px-space-md">sched_date</th>
<th className="py-space-sm px-space-md">actual_delivery_date</th>
<th className="py-space-sm px-space-md">is_late</th>
<th className="py-space-sm px-space-md">weather_alert_level</th>
<th className="py-space-sm px-space-md">traffic_delay_hrs</th>
</tr>
</thead>
<tbody className="divide-y-0 text-on-surface font-code-sm text-code-sm">
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-sm px-space-md font-semibold text-primary">DEL-98241</td>
<td className="py-space-sm px-space-md">CAR-PAC-04</td>
<td className="py-space-sm px-space-md">SEA-HUB-01</td>
<td className="py-space-sm px-space-md">PDX-DC-02</td>
<td className="py-space-sm px-space-md">280</td>
<td className="py-space-sm px-space-md">2024-10-24</td>
<td className="py-space-sm px-space-md">2024-10-24</td>
<td className="py-space-sm px-space-md"><span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface">FALSE</span></td>
<td className="py-space-sm px-space-md">NONE</td>
<td className="py-space-sm px-space-md text-outline">null</td>
</tr>
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-sm px-space-md font-semibold text-primary">DEL-98242</td>
<td className="py-space-sm px-space-md">CAR-LOG-12</td>
<td className="py-space-sm px-space-md">CHI-HUB-04</td>
<td className="py-space-sm px-space-md">DET-DC-01</td>
<td className="py-space-sm px-space-md">455</td>
<td className="py-space-sm px-space-md">2024-10-24</td>
<td className="py-space-sm px-space-md">2024-10-25</td>
<td className="py-space-sm px-space-md"><span className="px-space-xs py-0.5 rounded bg-error-container text-on-error-container font-semibold">TRUE</span></td>
<td className="py-space-sm px-space-md text-error">LEVEL_2_STORM</td>
<td className="py-space-sm px-space-md text-outline">null</td>
</tr>
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-sm px-space-md font-semibold text-primary">DEL-98243</td>
<td className="py-space-sm px-space-md">CAR-ATL-09</td>
<td className="py-space-sm px-space-md">ATL-HUB-02</td>
<td className="py-space-sm px-space-md">MIA-DC-03</td>
<td className="py-space-sm px-space-md">1,070</td>
<td className="py-space-sm px-space-md">2024-10-23</td>
<td className="py-space-sm px-space-md">2024-10-23</td>
<td className="py-space-sm px-space-md"><span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface">FALSE</span></td>
<td className="py-space-sm px-space-md">NONE</td>
<td className="py-space-sm px-space-md text-outline">null</td>
</tr>
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-sm px-space-md font-semibold text-primary">DEL-98244</td>
<td className="py-space-sm px-space-md">CAR-EXP-01</td>
<td className="py-space-sm px-space-md">DAL-HUB-03</td>
<td className="py-space-sm px-space-md">HOU-DC-05</td>
<td className="py-space-sm px-space-md">390</td>
<td className="py-space-sm px-space-md">2024-10-24</td>
<td className="py-space-sm px-space-md">2024-10-24</td>
<td className="py-space-sm px-space-md"><span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface">FALSE</span></td>
<td className="py-space-sm px-space-md">MODERATE_RAIN</td>
<td className="py-space-sm px-space-md text-outline">null</td>
</tr>
</tbody>
</table>
</div>
</div>
{/*  Schema Column Mapping Engine Section  */}
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-lg">
<div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
<div>
<div className="flex items-center gap-space-xs text-secondary font-label-md uppercase tracking-wider mb-space-xs">
<span className="material-symbols-outlined text-[16px]">sync_alt</span>
            Schema Mapping
          </div>
<h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Schema Column Mapping — Selected Dataset</h2>
<p className="font-body-md text-body-md text-on-surface-variant">Map source columns from <code className="font-code-sm bg-surface-container px-1 py-0.5 rounded text-primary">deliveries</code> sheet to Sentinel required model schema.</p>
</div>
{/*  Engine Score Badge  */}
<div className="flex items-center gap-space-md bg-surface-container-low px-space-md py-space-sm rounded-lg">
<div className="flex flex-col text-right">
<span className="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">Schema Mapping Status</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-on-surface font-bold">92.4%</span>
</div>
<div className="w-9 h-9 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center font-bold font-label-md">
            9/10
          </div>
</div>
</div>
{/*  Column Mapping Table  */}
<div className="overflow-x-auto rounded-lg bg-surface-container-low">
<table className="w-full text-left font-body-sm text-body-sm">
<thead className="bg-surface-container font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">
<tr>
<th className="py-space-md px-space-lg">Required Model Field</th>
<th className="py-space-md px-space-md">Requirement</th>
<th className="py-space-md px-space-lg">Source Column (Dropdown)</th>
<th className="py-space-md px-space-lg">Mapping Status</th>
</tr>
</thead>
<tbody className="divide-y-0">
{/*  Row 1: delivery_id  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">Source delivery_id</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Unique delivery tracking code</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">delivery_id</option>
<option>carrier_id</option>
<option>origin_hub</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check</span>
                  ✓ Exact Match
                </span>
</td>
</tr>
{/*  Row 2: carrier_id  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">carrier_id</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Logistics service provider ID</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">carrier_id</option>
<option>delivery_id</option>
<option>destination_dc</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check</span>
                  ✓ Exact Match
                </span>
</td>
</tr>
{/*  Row 3: origin  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">origin</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Origin dispatch terminal / airport</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">origin_hub</option>
<option>destination_dc</option>
<option>delivery_id</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">info</span>
                  ⚠ Alias Detected (origin_hub → origin)
                </span>
</td>
</tr>
{/*  Row 4: destination  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">destination</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Receiving distribution node</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">destination_dc</option>
<option>origin_hub</option>
<option>carrier_id</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">info</span>
                  ⚠ Alias Detected (destination_dc → destination)
                </span>
</td>
</tr>
{/*  Row 5: distance_km  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">distance_km</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Transit path distance in kilometers</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">distance_km</option>
<option>traffic_delay_hrs</option>
<option>actual_delivery_date</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check</span>
                  ✓ Exact Match
                </span>
</td>
</tr>
{/*  Row 6: scheduled_date  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">scheduled_date</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Committed delivery deadline</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">sched_date</option>
<option>actual_delivery_date</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">info</span>
                  ⚠ Alias Detected
                </span>
</td>
</tr>
{/*  Row 7: actual_date  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">actual_date</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Observed physical delivery timestamp</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm uppercase font-semibold">Optional</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">actual_delivery_date</option>
<option>sched_date</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check</span>
                  ✓ Matched
                </span>
</td>
</tr>
{/*  Row 8: is_late  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">is_late</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">SLA breach boolean indicator</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-primary-container text-on-primary font-label-sm text-label-sm uppercase font-semibold">Required</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">is_late</option>
<option>weather_alert_level</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check</span>
                  ✓ Exact Match
                </span>
</td>
</tr>
{/*  Row 9: weather_condition  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">weather_condition</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Route corridor atmospheric classification</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm uppercase font-semibold">Optional</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none">
<option selected="">weather_alert_level</option>
<option>traffic_delay_hrs</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">info</span>
                  ⚠ Alias Detected
                </span>
</td>
</tr>
{/*  Row 10: traffic_delay_hrs  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
<td className="py-space-md px-space-lg">
<div className="flex flex-col">
<span className="font-code-sm text-code-sm font-semibold text-on-surface">traffic_delay_hrs</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">Observed congestion variance in hours</span>
</div>
</td>
<td className="py-space-md px-space-md">
<span className="px-space-xs py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm uppercase font-semibold">Optional</span>
</td>
<td className="py-space-md px-space-lg">
<select className="w-full max-w-xs bg-surface-container-low text-on-surface rounded p-2 font-code-sm text-code-sm focus:outline-none text-outline">
<option selected="">-- Missing mapping --</option>
<option>traffic_delay_hrs</option>
<option>distance_km</option>
</select>
</td>
<td className="py-space-md px-space-lg">
<span className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded bg-error-container text-on-error-container font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">close</span>
                  ✕ Not Mapped
                </span>
</td>
</tr>
</tbody>
</table>
</div>
{/*  Validation Feedback Box & Execution Controls  */}
<div className="flex flex-col gap-space-md pt-space-sm">
{/*  Status Banner  */}
<div className="p-space-md rounded-xl bg-surface-container flex items-center justify-between flex-wrap gap-space-md">
<div className="flex items-center gap-space-md">
<div className="w-10 h-10 rounded-lg bg-tertiary-container text-tertiary-fixed flex items-center justify-center">
<span className="material-symbols-outlined text-[24px]">verified</span>
</div>
<div className="flex flex-col">
<span className="font-headline-sm text-headline-sm text-on-surface font-semibold">✓ Schema Validation Passed with Warnings</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">(All 6 Required Fields Mapped. 1 Optional Field Missing)</span>
</div>
</div>
<div className="flex items-center gap-space-sm">
<span className="px-space-sm py-1 rounded bg-surface-container-lowest text-on-surface font-code-sm text-code-sm">Non-blocking Warning</span>
</div>
</div>
{/*  Action Bar  */}
<div className="flex items-center justify-between flex-wrap gap-space-md pt-space-xs">
<div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">lock</span>
            Audited execution session • Model schema version 2.4-STABLE
          </div>
<div className="flex items-center gap-space-md">
<button className="flex items-center gap-space-sm px-space-lg py-2.5 rounded-lg bg-surface-container-lowest hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-all shadow-sm">
<span className="material-symbols-outlined text-[18px]">replay</span>
              Re-inspect Sheet
            </button>
<button className="flex items-center gap-space-sm px-space-xl py-2.5 rounded-lg bg-primary-container hover:bg-primary text-on-primary font-label-md text-label-md transition-all shadow-md" id="activate-dataset-btn">
<span className="material-symbols-outlined text-[18px]">bolt</span>
              Activate Dataset
            </button>
</div>
</div>
</div>
</div>
{/*  Bottom Section: Active Dataset Status  */}
<div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md">
<div className="flex items-center justify-between flex-wrap gap-space-sm">
<div className="flex items-center gap-space-sm">
<span className="w-3 h-3 rounded-full bg-tertiary-fixed-dim animate-ping"></span>
<h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Active Dataset Status</h2>
</div>
<div className="flex items-center gap-space-sm">
<span className="px-space-sm py-0.5 rounded bg-tertiary-container text-tertiary-fixed font-label-sm text-label-sm uppercase font-semibold">Active In Sentinel Cache</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Ref: ACT-DS-8821</span>
</div>
</div>
{/*  Detail Card Metrics  */}
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md">
{/*  Metric 1  */}
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Dataset Identifier</span>
<span className="font-headline-sm text-headline-sm text-primary font-bold">Master Supply Chain Q3</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Format: Excel</span>
</div>
{/*  Metric 2  */}
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Total Records Activated</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">1,450</span>
<div className="flex items-center gap-space-xs text-tertiary-fixed-variant font-label-sm text-label-sm font-semibold">
<span className="material-symbols-outlined text-[14px]">check_circle</span>
            100% Ingest Integrity
          </div>
</div>
{/*  Metric 3  */}
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Loaded Entities</span>
<div className="flex items-baseline gap-space-xs">
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">48</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Carriers</span>
<span className="text-outline-variant font-body-sm">•</span>
<span className="font-tabular-metric-lg text-tabular-metric-lg text-on-surface font-bold">12</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Hubs</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant">114 Active Corridors</span>
</div>
{/*  Metric 4: Inline Topology Sparkline / Visual Component  */}
<div className="p-space-md rounded-lg bg-surface-container-low flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Network Density</span>
<span className="font-tabular-metric-md text-tabular-metric-md text-secondary font-bold">114 Routes</span>
</div>
{/*  Inline Sparkline Representation  */}
<div className="h-8 flex items-end gap-1 pt-2">
<div className="bg-secondary/40 w-full h-[40%] rounded-t"></div>
<div className="bg-secondary/50 w-full h-[60%] rounded-t"></div>
<div className="bg-secondary/60 w-full h-[45%] rounded-t"></div>
<div className="bg-secondary/70 w-full h-[85%] rounded-t"></div>
<div className="bg-secondary/60 w-full h-[70%] rounded-t"></div>
<div className="bg-secondary w-full h-[95%] rounded-t"></div>
<div className="bg-secondary/80 w-full h-[65%] rounded-t"></div>
<div className="bg-secondary/50 w-full h-[50%] rounded-t"></div>
<div className="bg-secondary w-full h-[100%] rounded-t"></div>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">Strictly computed from active dataset</span>
</div>
</div>
</div>
</div>
</div>
<script>
  // Micro-interaction for dataset activation
  const activateBtn = document.getElementById('activate-dataset-btn');
  if (activateBtn) {
    activateBtn.addEventListener('click', function() {
      const originalHTML = this.innerHTML;
      this.disabled = true;
      this.innerHTML = '<span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> Activating Pipeline...';
      this.classList.add('opacity-80');
      
      setTimeout(() => {
        this.innerHTML = '<span className="material-symbols-outlined text-[18px]">done_all</span> Dataset Operational';
        this.classList.remove('bg-primary-container', 'opacity-80');
        this.classList.add('bg-tertiary-container', 'text-tertiary-fixed');
      }, 900);
    });
  }
</script>