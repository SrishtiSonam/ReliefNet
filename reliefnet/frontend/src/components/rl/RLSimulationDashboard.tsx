import React, { useState } from 'react';
import { motion } from 'framer-motion';

export const RLSimulationDashboard: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [step, setStep] = useState(0);

  const startSimulation = () => {
    setIsRunning(true);
    // In a real app, this would connect to a WebSocket or poll the API
    const interval = setInterval(() => {
      setStep(s => {
        if (s >= 30) {
          clearInterval(interval);
          setIsRunning(false);
          return 30;
        }
        return s + 1;
      });
    }, 1000);
  };

  return (
    <div className="p-6 bg-slate-900 rounded-xl text-white">
      <h2 className="text-2xl font-bold mb-4">RL Logistics Simulation</h2>
      
      <div className="flex gap-4 mb-8">
        <button 
          onClick={startSimulation}
          disabled={isRunning || step >= 30}
          className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {isRunning ? 'Simulating...' : 'Start Simulation'}
        </button>
        <button 
          onClick={() => setStep(0)}
          className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Reset
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* State Metrics */}
        <div className="bg-slate-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Environment State</h3>
          <p>Time Step: {step} / 30</p>
          <p>Total Deprivation Cost: {(Math.random() * 100 * (1 - step/30)).toFixed(2)}</p>
          <p>Active Road Failures: {Math.floor(step * 1.5)}</p>
        </div>

        {/* Agent Actions */}
        <div className="bg-slate-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">PPO Agent Actions</h3>
          <p>Trucks Dispatched: {Math.floor(Math.random() * 10 + 5)}</p>
          <p>UAVs Dispatched: {Math.floor(Math.random() * 5 + 2)}</p>
          <div className="mt-2 h-2 w-full bg-slate-700 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-green-500"
              initial={{ width: '0%' }}
              animate={{ width: `${(step / 30) * 100}%` }}
            />
          </div>
        </div>

        {/* Fairness Metrics */}
        <div className="bg-slate-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Fairness Constraints</h3>
          <p>Gini Coefficient: {(0.4 - step * 0.01).toFixed(3)}</p>
          <p>Max-Min Shortage: {(0.8 - step * 0.02).toFixed(2)}</p>
          <p className="text-sm text-slate-400 mt-2">Optimization: Constrained MAPPO</p>
        </div>
      </div>
    </div>
  );
};
