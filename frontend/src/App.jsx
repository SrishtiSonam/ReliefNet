import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ControlPanel from './components/ControlPanel';
import AwarenessPortal from './components/AwarenessPortal';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [simulationData, setSimulationData] = useState(null);

  const handleSimulationUpdate = (data) => {
    setSimulationData(data);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <nav className="bg-gray-800 p-4 shadow-lg flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-400">Disaster Relief AI</h1>
        <div className="space-x-4">
          <button onClick={() => setActiveTab('dashboard')} className={`px-4 py-2 rounded ${activeTab === 'dashboard' ? 'bg-blue-600' : 'bg-gray-700'}`}>Dashboard</button>
          <button onClick={() => setActiveTab('map')} className={`px-4 py-2 rounded ${activeTab === 'map' ? 'bg-blue-600' : 'bg-gray-700'}`}>Live Map</button>
          <button onClick={() => setActiveTab('portal')} className={`px-4 py-2 rounded ${activeTab === 'portal' ? 'bg-blue-600' : 'bg-gray-700'}`}>Awareness</button>
        </div>
      </nav>

      <main className="p-6">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'map' && <div className="flex gap-4"><MapView simulationData={simulationData} /><ControlPanel onSimulationUpdate={handleSimulationUpdate} /></div>}
        {activeTab === 'portal' && <AwarenessPortal />}
      </main>
    </div>
  );
}

export default App;
