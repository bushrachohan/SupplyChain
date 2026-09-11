import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Layout from './components/Layout';
import CommandCenter from './pages/CommandCenter';
import DataHub from './pages/DataHub';
import CreateDecision from './pages/CreateDecision';
import ApprovalQueue from './pages/ApprovalQueue';
import DecisionHistory from './pages/DecisionHistory';
import Simulation from './pages/Simulation';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        <Route path="/app" element={<Layout />}>
          <Route index element={<Navigate to="/app/command-center" replace />} />
          <Route path="command-center" element={<CommandCenter />} />
          <Route path="data-hub" element={<DataHub />} />
          <Route path="create-decision" element={<CreateDecision />} />
          <Route path="approval-queue" element={<ApprovalQueue />} />
          <Route path="decision-history" element={<DecisionHistory />} />
          <Route path="simulation" element={<Simulation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
