import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import MapPlanner from './pages/MapPlanner';
import AllocationConsole from './pages/AllocationConsole';
import FleetRoads from './pages/FleetRoads';
import Forecasts from './pages/Forecasts';
import Explainability from './pages/Explainability.tsx';
import Scenarios from './pages/Scenarios';
import Logs from './pages/Logs';
import './App.css';

function App() {
  const [currentEpoch, setCurrentEpoch] = useState(6);
  const [currentScenario, setCurrentScenario] = useState('baseline');

  return (
    <Router>
      <div className="app">
        <Header 
          currentEpoch={currentEpoch}
          currentScenario={currentScenario}
          onScenarioChange={setCurrentScenario}
        />
        <div className="app-content">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/map" element={<MapPlanner />} />
              <Route path="/allocation" element={<AllocationConsole />} />
              <Route path="/fleet" element={<FleetRoads />} />
              <Route path="/forecasts" element={<Forecasts />} />
              <Route path="/explainability" element={<Explainability />} />
              <Route path="/scenarios" element={<Scenarios />} />
              <Route path="/logs" element={<Logs />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;