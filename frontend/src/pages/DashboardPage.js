import React, { useState, useEffect } from 'react';
import MapView from '../components/MapView';
import RecommendationCard from '../components/RecommendationCard';
import ExplanationPanel from '../components/ExplanationPanel';
import WhatIfPanel from '../components/WhatIfPanel';

const DashboardPage = ({ user, sessionId, apiBase, mlApiBase }) => {
  const [districts, setDistricts] = useState([]);
  const [forecasts, setForecasts] = useState({});
  const [recommendations, setRecommendations] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const authHeaders = {
    'Authorization': `Bearer ${sessionId}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load configuration
      const configResponse = await fetch(`${apiBase}/config`, {
        headers: authHeaders
      });
      const configData = await configResponse.json();
      setConfig(configData);

      // Initialize district data
      const initialDistricts = configData.districts.map(d => ({
        ...d,
        inventory: Math.random() * 200,
        demand_last_period: Math.random() * 50,
        backlog: Math.random() * 30,
        avg_deprivation_time: Math.random() * 10,
        road_access: 'open'
      }));
      setDistricts(initialDistricts);

      // Load forecasts
      await loadForecasts(initialDistricts.map(d => d.id));
      
    } catch (err) {
      setError(`Failed to load data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadForecasts = async (districtIds) => {
    try {
      const forecastData = {};
      districtIds.forEach(id => {
        forecastData[id] = {
          demand_forecast: Math.random() * 100,
          surge_prob: Math.random() * 0.5,
          confidence: 0.8 + Math.random() * 0.2
        };
      });
      setForecasts(forecastData);
    } catch (err) {
      console.error('Failed to load forecasts:', err);
    }
  };

  const generateRecommendations = async (constraints = {}) => {
    try {
      setLoading(true);

      // Create current state from districts
      const currentState = districts.reduce((acc, d) => {
        acc[d.id] = {
          inventory: d.inventory,
          backlog: d.backlog,
          demand_last_period: d.demand_last_period,
          avg_deprivation_time: d.avg_deprivation_time,
          road_access: d.road_access
        };
        return acc;
      }, {});

      // Get VFA estimates
      const vfaResponse = await fetch(`${mlApiBase}/forecast/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_decision_state: currentState,
          forecast_features: forecasts,
          model: 'dl_vfa'
        })
      });

      let vfaEstimates = {};
      if (vfaResponse.ok) {
        const vfaData = await vfaResponse.json();
        setExplanation(vfaData.explanation);
        
        // Simple VFA estimates per district (in real app, get per-district estimates)
        districts.forEach(d => {
          vfaEstimates[d.id] = vfaData.vfa_value / districts.length;
        });
      }

      // Get optimization recommendations
      const optResponse = await fetch(`${mlApiBase}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_state: currentState,
          vfa_estimates: vfaEstimates,
          fleet: config?.fleetConfig || [],
          constraints
        })
      });

      if (optResponse.ok) {
        const optData = await optResponse.json();
        setRecommendations(optData);
      }

    } catch (err) {
      setError(`Failed to generate recommendations: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const acceptRecommendations = async () => {
    try {
      // Log the acceptance
      await fetch(`${apiBase}/audit-log`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          action: 'accept_recommendations',
          details: {
            allocations: recommendations?.allocations || [],
            objective: recommendations?.objective || 0
          }
        })
      });

      // Update district states based on allocations
      const updatedDistricts = [...districts];
      recommendations?.allocations?.forEach(allocation => {
        const district = updatedDistricts.find(d => d.id === allocation.district);
        if (district) {
          const capacity = allocation.truck_class === 'small_truck' ? 100 : 10;
          const totalCapacity = capacity * allocation.count;
          
          district.inventory += Math.max(0, totalCapacity - district.backlog);
          district.backlog = Math.max(0, district.backlog - totalCapacity);
        }
      });
      
      setDistricts(updatedDistricts);
      
      // Clear current recommendations
      setRecommendations(null);
      setExplanation(null);

    } catch (err) {
      setError(`Failed to accept recommendations: ${err.message}`);
    }
  };

  const handleConstraintsChange = (newConstraints) => {
    generateRecommendations(newConstraints);
  };

  if (loading && !districts.length) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Operations Dashboard</h1>
        <p className="text-gray-600">Real-time district monitoring and allocation recommendations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map View */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h2 className="text-xl font-semibold mb-4">District Map</h2>
            <MapView 
              districts={districts}
              forecasts={forecasts}
              recommendations={recommendations}
              config={config}
            />
          </div>
        </div>

        {/* Control Panel */}
        <div className="space-y-6">
          {/* Generate Recommendations Button */}
          <div className="bg-white rounded-lg shadow-lg p-4">
            <button
              onClick={() => generateRecommendations()}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Generating...' : 'Generate Recommendations'}
            </button>
          </div>

          {/* Recommendations Card */}
          {recommendations && (
            <RecommendationCard 
              recommendations={recommendations}
              onAccept={acceptRecommendations}
              loading={loading}
            />
          )}

          {/* What-If Panel */}
          <WhatIfPanel 
            onConstraintsChange={handleConstraintsChange}
            districts={districts}
            fleet={config?.fleetConfig || []}
          />

          {/* Explanation Panel */}
          {explanation && (
            <ExplanationPanel explanation={explanation} />
          )}
        </div>
      </div>

      {/* District Status Table */}
      <div className="mt-8 bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">District Status</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">District</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Inventory</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Backlog</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deprivation</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Surge Prob</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {districts.map(district => {
                const forecast = forecasts[district.id] || {};
                const status = district.backlog > 20 ? 'Critical' : 
                              district.backlog > 10 ? 'Warning' : 'Good';
                const statusColor = status === 'Critical' ? 'text-red-600' : 
                                  status === 'Warning' ? 'text-yellow-600' : 'text-green-600';

                return (
                  <tr key={district.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{district.name}</td>
                    <td className="px-6 py-4 text-gray-700">{district.inventory.toFixed(0)}</td>
                    <td className="px-6 py-4 text-gray-700">{district.backlog.toFixed(0)}</td>
                    <td className="px-6 py-4 text-gray-700">{district.avg_deprivation_time.toFixed(1)}h</td>
                    <td className="px-6 py-4 text-gray-700">{(forecast.surge_prob * 100 || 0).toFixed(1)}%</td>
                    <td className={`px-6 py-4 font-medium ${statusColor}`}>{status}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;