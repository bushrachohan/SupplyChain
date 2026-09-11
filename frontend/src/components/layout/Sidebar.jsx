import React from 'react';
import { NavLink, Link } from 'react-router-dom';

const NAV_BASE = "flex items-center gap-space-md px-space-md py-space-sm rounded-lg transition-all";
const NAV_INACTIVE = "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface";
const NAV_ACTIVE = "bg-primary-container text-on-primary font-semibold shadow-sm";

function navClass({ isActive }) {
  return NAV_BASE + " " + (isActive ? NAV_ACTIVE : NAV_INACTIVE);
}

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest border-r border-outline-variant/30 z-50 flex flex-col justify-between shadow-[0_1px_8px_rgba(0,0,0,0.02)]">
      <div className="flex flex-col">
        <div className="px-space-xl pt-space-xl pb-space-lg border-b border-outline-variant/20">
          <Link to="/" className="flex items-center gap-space-sm mb-space-xs hover:opacity-80 transition-opacity">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-on-primary text-[18px]">shield_with_house</span>
            </div>
            <span className="font-headline-sm text-headline-sm text-primary font-bold tracking-tight">SupplyChain Sentinel AI</span>
          </Link>
          <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider pl-9">AI Decision Intelligence</p>
        </div>
        <div className="px-space-lg py-space-sm m-space-md rounded-lg bg-surface-container-low border border-outline-variant/30 flex items-center gap-space-sm">
          <span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim animate-pulse"></span>
          <div className="flex flex-col min-w-0">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wide font-semibold">DATA SOURCE</span>
            <span className="font-body-sm text-body-sm text-on-surface truncate font-medium">Company Supply Chain &mdash; Connected</span>
          </div>
        </div>
        <nav className="flex flex-col gap-space-xs px-space-md py-space-sm overflow-y-auto">
          <div className="px-space-sm pt-space-xs pb-space-xs">
            <NavLink className={navClass} to="/app/command-center">
              <span className="material-symbols-outlined text-[20px]">grid_view</span>
              <span className="font-body-md text-body-md">Command Center</span>
            </NavLink>
          </div>
          <div className="pt-space-md px-space-sm pb-space-xs font-label-md text-label-md text-on-surface-variant/80 uppercase tracking-wider">Data</div>
          <NavLink className={navClass} to="/app/data-hub">
            <span className="material-symbols-outlined text-[20px]">hub</span>
            <span className="font-body-md text-body-md">Data Hub</span>
          </NavLink>
          <div className="pt-space-md px-space-sm pb-space-xs font-label-md text-label-md text-on-surface-variant/80 uppercase tracking-wider">Decisions</div>
          <NavLink className={navClass} to="/app/create-decision">
            <span className="material-symbols-outlined text-[20px]">add_task</span>
            <span className="font-body-md text-body-md">Create a Decision</span>
          </NavLink>
          <NavLink className={navClass} to="/app/approval-queue">
            <span className="material-symbols-outlined text-[20px]">assignment_turned_in</span>
            <span className="font-body-md text-body-md">Approval Queue</span>
          </NavLink>
          <NavLink className={navClass} to="/app/decision-history">
            <span className="material-symbols-outlined text-[20px]">history</span>
            <span className="font-body-md text-body-md">Decision History</span>
          </NavLink>
          <div className="pt-space-md px-space-sm pb-space-xs font-label-md text-label-md text-on-surface-variant/80 uppercase tracking-wider">Analysis</div>
          <NavLink className={navClass} to="/app/simulation">
            <span className="material-symbols-outlined text-[20px]">query_stats</span>
            <span className="font-body-md text-body-md">What-If Simulation</span>
          </NavLink>
        </nav>
      </div>
      <div className="p-space-md border-t border-outline-variant/20 bg-surface-container-lowest">
        <div className="flex items-center justify-between px-space-sm py-space-xs text-on-surface-variant">
          <span className="font-code-sm text-code-sm">v2.4.1-rc</span>
          <span className="font-label-sm text-label-sm uppercase bg-surface-container px-space-xs py-0.5 rounded text-on-surface font-semibold">Audited</span>
        </div>
      </div>
    </aside>
  );
}
