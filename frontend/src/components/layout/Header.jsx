import React from 'react';

export default function Header() {
  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-md border-b border-outline-variant/30 z-40 px-space-xl flex items-center justify-between shadow-[0_1px_6px_rgba(0,0,0,0.02)]"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm px-space-md py-1.5 rounded-lg bg-surface-container-low border border-outline-variant/20"><span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></span><span className="font-body-sm text-body-sm text-on-surface font-medium">Engine Status: Nominal</span><span className="text-outline-variant">|</span><span className="font-body-sm text-body-sm text-on-surface-variant">SHAP &amp; Policy RAG Active</span></div></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm text-right"><div className="flex flex-col"><span className="font-body-sm text-body-sm font-semibold text-on-surface">Ops Lead</span><span className="font-label-sm text-label-sm text-on-surface-variant">(Reviewer)</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header>
  );
}
