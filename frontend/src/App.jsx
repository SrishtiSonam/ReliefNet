import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import HowAIWorks from './pages/HowAIWorks';
import Login from './pages/Login';
import StateDashboard from './pages/StateDashboard';
import DistrictDashboard from './pages/DistrictDashboard';
import PublicPortal from './pages/PublicPortal';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/how-ai-works" element={<HowAIWorks />} />
        <Route path="/login" element={<Login />} />
        <Route path="/state-dashboard" element={<StateDashboard />} />
        <Route path="/district-dashboard" element={<DistrictDashboard />} />
        <Route path="/public-portal" element={<PublicPortal />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
