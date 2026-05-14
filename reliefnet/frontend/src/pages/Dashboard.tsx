import React, { useEffect } from 'react';
import StatCard from '../components/cards/StatCard';
import ReliefMap from '../components/map/ReliefMap';
import { AlertTriangle, MapPin, Warehouse, Zap } from 'lucide-react';
import { useDistrictStore } from '../store/districtStore';

const Dashboard: React.FC = () => {
  const { districts, fetchDistricts } = useDistrictStore();

  useEffect(() => {
    fetchDistricts({ limit: 10 });
  }, [fetchDistricts]);

  // Mock markers for the map
  const markers = districts.map(d => ({
    position: [d.latitude, d.longitude] as [number, number],
    label: d.district,
    type: 'district' as const
  }));

  return (
    <div className="space-y-6">
      {/* Stat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Active Disasters" 
          value="0" 
          icon={AlertTriangle} 
          color="red"
        />
        <StatCard 
          title="High Risk Districts" 
          value={districts.filter(d => d.vulnerability_tier === 'CRITICAL').length} 
          icon={MapPin} 
          color="orange"
          trend="+2"
        />
        <StatCard 
          title="Total Warehouses" 
          value="24" 
          icon={Warehouse} 
          color="blue"
        />
        <StatCard 
          title="Avg Vulnerability" 
          value="0.42" 
          icon={Zap} 
          color="green"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Section */}
        <div className="lg:col-span-2 h-[600px] bg-white dark:bg-gray-900 p-4 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
          <div className="flex justify-between items-center mb-4 px-2">
            <h3 className="font-bold text-gray-800 dark:text-white">Regional Risk Monitor</h3>
            <button className="text-xs text-relief-600 font-semibold hover:underline">View Full Map</button>
          </div>
          <ReliefMap markers={markers} />
        </div>

        {/* Sidebar Info Section */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
            <h3 className="font-bold text-gray-800 dark:text-white mb-4">Top Vulnerable Districts</h3>
            <div className="space-y-4">
              {districts.slice(0, 5).map((d, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{d.district}</p>
                      <p className="text-xs text-gray-500">{d.state}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-red-500">{(d.vulnerability_score * 10).toFixed(1)}</p>
                    <p className="text-[10px] text-gray-400 uppercase tracking-wider">Score</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-6 py-2 text-sm font-semibold text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 transition-colors">
              View All Districts
            </button>
          </div>

          <div className="bg-relief-600 p-6 rounded-2xl text-white shadow-lg shadow-relief-200">
            <h3 className="font-bold mb-2">Ready for Simulation?</h3>
            <p className="text-sm text-relief-50 opacity-90 mb-4">
              Run a disaster scenario to estimate impact and optimize resource distribution.
            </p>
            <button className="w-full py-2 bg-white text-relief-600 rounded-lg font-bold shadow-sm hover:bg-relief-50 transition-colors">
              New Simulation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
