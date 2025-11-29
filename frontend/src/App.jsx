import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DisasterPrediction from './pages/DisasterPrediction';
import ResourceMap from './pages/ResourceMap';
import DispatchRecommendation from './pages/DispatchRecommendation';

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/prediction', label: 'Disaster Prediction', icon: '🌪️' },
    { path: '/map', label: 'Resource Map', icon: '🗺️' },
    { path: '/dispatch', label: 'Dispatch Decision', icon: '🚑' }
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-primary-600">
              🇮🇳 SDPD System
            </h1>
          </div>
          <div className="flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`inline-flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 ${location.pathname === item.path
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-600 hover:text-primary-600'
                  }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/prediction" element={<DisasterPrediction />} />
            <Route path="/map" element={<ResourceMap />} />
            <Route path="/dispatch" element={<DispatchRecommendation />} />
          </Routes>
        </main>
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              Smart Disaster Prediction, Decision & Resource Allocation System for India
              <br />
              <span className="text-xs">Design Reference: /mnt/data/RG14.docx.pdf</span>
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
