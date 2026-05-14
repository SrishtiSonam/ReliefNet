import React, { useEffect, useState } from 'react';
import { useDistrictStore } from '../store/districtStore';
import { Search, Filter, ArrowUpRight, ShieldAlert } from 'lucide-react';

const DistrictMonitor: React.FC = () => {
  const { districts, isLoading, fetchDistricts } = useDistrictStore();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchDistricts();
  }, [fetchDistricts]);

  const filteredDistricts = districts.filter(d => 
    d.district.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'CRITICAL': return 'text-red-600 bg-red-50 border-red-100';
      case 'HIGH': return 'text-orange-600 bg-orange-50 border-orange-100';
      case 'MEDIUM': return 'text-blue-600 bg-blue-50 border-blue-100';
      default: return 'text-green-600 bg-green-50 border-green-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input 
            type="text" 
            placeholder="Search districts or states..." 
            className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl focus:ring-2 focus:ring-relief-500 outline-none transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            <Filter size={16} /> Filter
          </button>
          <button className="px-4 py-2 bg-relief-600 text-white rounded-xl text-sm font-medium hover:bg-relief-700 shadow-sm transition-colors">
            Export Report
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800">
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">District</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Vulnerability</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Risk Tier</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Pop. Density</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Infrastructure</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {isLoading ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-400">Loading district data...</td></tr>
              ) : filteredDistricts.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-400">No districts found.</td></tr>
              ) : (
                filteredDistricts.map((d) => (
                  <tr key={d.district} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors group">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-gray-900 dark:text-white">{d.district}</p>
                      <p className="text-xs text-gray-500">{d.state}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-relief-500 rounded-full" 
                            style={{ width: `${d.vulnerability_score * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{(d.vulnerability_score * 10).toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border ${getTierColor(d.vulnerability_tier)}`}>
                        {d.vulnerability_tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      {d.population_density.toFixed(0)}/km²
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <span className="p-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-md" title={`${d.num_hospitals} Hospitals`}>H</span>
                        <span className="p-1.5 bg-orange-50 dark:bg-orange-900/20 text-orange-600 rounded-md" title={`${d.num_warehouses} Warehouses`}>W</span>
                        <span className="p-1.5 bg-green-50 dark:bg-green-900/20 text-green-600 rounded-md" title={`${d.num_shelters} Shelters`}>S</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-gray-400 hover:text-relief-600 hover:bg-relief-50 dark:hover:bg-gray-800 rounded-lg transition-all">
                        <ArrowUpRight size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DistrictMonitor;
