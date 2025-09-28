// pages/SimulationPage.js
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar } from 'recharts';

const SimulationPage = ({ user, sessionId, apiBase, mlApiBase }) => {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('');
  const [selectedPolicy, setSelectedPolicy] = useState('dl_vfa');
  const [episodes, setEpisodes] = useState(10);
  const [results, setResults] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const authHeaders = {
    'Authorization': `Bearer ${sessionId}`,
    'Content-Type': 'application/json'
  };

  const policies = [
    { value: 'dl_vfa', label: 'DL-VFA + MIP' },
    { value: 'nn_vfa', label: 'NN-VFA + MIP' },
    { value: 'heuristic', label: 'Pro-rata Heuristic' }
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load scenarios
      const scenariosResponse = await fetch(`${apiBase}/scenarios`, {
        headers: authHeaders
      });
      if (scenariosResponse.ok) {
        const scenariosData = await scenariosResponse.json();
        setScenarios(scenariosData.scenarios);
        if (scenariosData.scenarios.length > 0) {
          setSelectedScenario(scenariosData.scenarios[0].filename);
        }
      }

      // Load past experiments
      const experimentsResponse = await fetch(`${apiBase}/experiments`, {
        headers: authHeaders
      });
      if (experimentsResponse.ok) {
        const experimentsData = await experimentsResponse.json();
        setExperiments(experimentsData.experiments);
      }

    } catch (err) {
      setError(`Failed to load data: ${err.message}`);
    }
  };

  const runSimulation = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${mlApiBase}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario: selectedScenario.replace('.json', ''),
          policy: selectedPolicy,
          n_episodes: episodes
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
        
        // Log the experiment
        await fetch(`${apiBase}/audit-log`, {
          method: 'POST',
          headers: authHeaders,
          body: JSON.stringify({
            action: 'run_simulation',
            details: {
              scenario: selectedScenario,
              policy: selectedPolicy,
              episodes,
              results: data.results_summary
            }
          })
        });

        // Reload experiments list
        loadData();
      } else {
        setError('Simulation failed');
      }

    } catch (err) {
      setError(`Simulation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Simulation & Experiments</h1>
        <p className="text-gray-600">Run offline policy comparisons and analyze results</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation Setup */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">New Simulation</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Scenario
              </label>
              <select
                value={selectedScenario}
                onChange={(e) => setSelectedScenario(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">Select scenario...</option>
                {scenarios.map(scenario => (
                  <option key={scenario.filename} value={scenario.filename}>
                    {scenario.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Policy
              </label>
              <select
                value={selectedPolicy}
                onChange={(e) => setSelectedPolicy(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                {policies.map(policy => (
                  <option key={policy.value} value={policy.value}>
                    {policy.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Episodes
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={episodes}
                onChange={(e) => setEpisodes(parseInt(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>

            <button
              onClick={runSimulation}
              disabled={loading || !selectedScenario}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Running Simulation...' : 'Run Simulation'}
            </button>
          </div>

          {error && (
            <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Latest Results</h2>
          
          {results ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Mean Cost</div>
                  <div className="text-lg font-semibold">
                    {results.results_summary.mean_cost.toFixed(1)}
                  </div>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Coverage</div>
                  <div className="text-lg font-semibold">
                    {(results.results_summary.demand_coverage * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-yellow-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Mean Deprivation</div>
                  <div className="text-lg font-semibold">
                    {results.results_summary.mean_deprivation.toFixed(1)}h
                  </div>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Episodes</div>
                  <div className="text-lg font-semibold">
                    {results.results_summary.episodes || episodes}
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                <strong>Output file:</strong> {results.output_file.split('/').pop()}
              </div>
            </div>
          ) : (
            <div className="text-gray-500">No simulation results yet. Run a simulation to see results.</div>
          )}
        </div>
      </div>

      {/* Past Experiments */}
      <div className="mt-8 bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">Past Experiments</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Policy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  File
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {experiments.map((experiment, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {experiment.policy}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {experiment.timestamp.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {experiment.filename}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button className="text-blue-600 hover:text-blue-800">
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SimulationPage;