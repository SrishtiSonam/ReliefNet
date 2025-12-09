import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import StateDashboard from './pages/StateDashboard';
import DistrictDashboard from './pages/DistrictDashboard';
import PublicPortal from './pages/PublicPortal';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/state" element={<StateDashboard />} />
        <Route path="/district" element={<DistrictDashboard />} />
        <Route path="/public" element={<PublicPortal />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
