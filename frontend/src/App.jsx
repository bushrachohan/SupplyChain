import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import AppLayout from './components/layout/AppLayout';
import CommandCenterPage from './pages/CommandCenterPage';
import DataHubPage from './pages/DataHubPage';
import CreateDecisionPage from './pages/CreateDecisionPage';
import DecisionResultPage from './pages/DecisionResultPage';
import ApprovalQueuePage from './pages/ApprovalQueuePage';
import DecisionHistoryPage from './pages/DecisionHistoryPage';
import SimulationPage from './pages/SimulationPage';

export default function App() {
  return (
    <Routes>
      {/* Public Landing Page */}
      <Route path="/" element={<LandingPage />} />

      {/* Internal Protected Application Screens */}
      <Route path="/app" element={<AppLayout />}>
        <Route index element={<Navigate to="/app/command-center" replace />} />
        <Route path="command-center" element={<CommandCenterPage />} />
        <Route path="data-hub" element={<DataHubPage />} />
        <Route path="create-decision" element={<CreateDecisionPage />} />
        <Route path="decision/:traceId" element={<DecisionResultPage />} />
        <Route path="approval-queue" element={<ApprovalQueuePage />} />
        <Route path="decision-history" element={<DecisionHistoryPage />} />
        <Route path="simulation" element={<SimulationPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
