import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function AppLayout() {
  return (
    <div className="bg-surface font-body-md text-on-surface antialiased min-h-screen">
      <Sidebar />
      <div className="pl-72">
        <Header />
        <main className="relative pt-16 bg-surface min-h-screen w-full px-space-xl py-space-xl">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
