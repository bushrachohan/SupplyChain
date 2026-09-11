import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Database, BrainCircuit, CheckSquare, Clock, Activity, LogOut } from 'lucide-react';
import clsx from 'clsx';

export default function Layout() {
  const navigate = useNavigate();

  const navItems = [
    { name: 'Command Center', path: '/app/command-center', icon: LayoutDashboard },
    { name: 'Data Hub', path: '/app/data-hub', icon: Database },
    { name: 'Create a Decision', path: '/app/create-decision', icon: BrainCircuit },
    { name: 'Approval Queue', path: '/app/approval-queue', icon: CheckSquare },
    { name: 'Decision History', path: '/app/decision-history', icon: Clock },
    { name: 'What-If Simulation', path: '/app/simulation', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-[#fcfcfd] flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col h-screen sticky top-0">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-md bg-teal-900 flex items-center justify-center text-white shadow-xs border border-teal-800">
              <svg className="w-4 h-4 text-teal-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <path d="m9 12 2 2 4-4"></path>
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-slate-900 text-sm tracking-tight leading-none">
                Sentinel <span className="text-teal-700">AI</span>
              </span>
            </div>
          </div>
          <div className="text-[11px] font-mono text-slate-500 uppercase tracking-wider font-semibold mb-6">
            Decision Intelligence
          </div>

          <div className="bg-teal-50 border border-teal-100 rounded-md p-3 mb-6">
            <p className="text-[10px] font-mono font-semibold text-teal-800 uppercase tracking-wider mb-1">Data Source</p>
            <p className="text-xs text-teal-900 font-medium">● Connected</p>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-slate-100 text-slate-900'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                )
              }
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 transition-colors w-full px-3 py-2"
          >
            <LogOut className="w-4 h-4" />
            Back to Landing
          </button>
          <div className="text-center mt-4">
            <p className="text-[10px] text-slate-400">© 2026 Sentinel Corp.</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        {/* Top bar */}
        <header className="h-14 border-b border-slate-200 bg-white flex items-center px-8 shrink-0">
          <div className="flex items-center gap-2 text-[11px] font-mono text-slate-500">
             <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
             SYSTEM ONLINE | DECISION TELEMETRY ACTIVE
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-8">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
