import React, { useState } from 'react';

interface Allocation {
  id: string;
  district: string;
  trucks: number;
  uavs: number;
  confidence: number;
  reasoning: string[];
}

export const HumanOverrideDashboard: React.FC = () => {
  const [allocations, setAllocations] = useState<Allocation[]>([
    {
      id: 'alloc_1',
      district: 'Mandi',
      trucks: 5,
      uavs: 2,
      confidence: 0.91,
      reasoning: ["High flood severity", "Road disconnection", "Medicine shortage"]
    },
    {
      id: 'alloc_2',
      district: 'Kullu',
      trucks: 8,
      uavs: 0,
      confidence: 0.85,
      reasoning: ["High demand", "Roads fully accessible"]
    }
  ]);

  const [selectedAlloc, setSelectedAlloc] = useState<Allocation | null>(null);
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideTrucks, setOverrideTrucks] = useState(0);
  const [overrideUavs, setOverrideUavs] = useState(0);

  const handleOverrideSubmit = () => {
    // In reality, this would POST to /api/v1/allocation/override
    alert(`Override Submitted for ${selectedAlloc?.district}! Re-optimizing...`);
    setSelectedAlloc(null);
  };

  return (
    <div className="p-6 bg-slate-900 rounded-xl text-white mt-6">
      <h2 className="text-2xl font-bold mb-4">Human-in-the-Loop Operations</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-3">AI Recommendations</h3>
          <div className="space-y-4">
            {allocations.map(alloc => (
              <div key={alloc.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold">{alloc.district}</h4>
                  <span className="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">
                    {Math.round(alloc.confidence * 100)}% Conf
                  </span>
                </div>
                <p className="text-sm">Trucks: {alloc.trucks} | UAVs: {alloc.uavs}</p>
                <div className="mt-2 mb-3">
                  <p className="text-xs text-slate-400 mb-1">AI Reasoning:</p>
                  <ul className="text-xs list-disc list-inside text-slate-300">
                    {alloc.reasoning.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
                <button 
                  onClick={() => {
                    setSelectedAlloc(alloc);
                    setOverrideTrucks(alloc.trucks);
                    setOverrideUavs(alloc.uavs);
                  }}
                  className="w-full bg-slate-700 hover:bg-slate-600 text-sm py-1 rounded transition-colors"
                >
                  Override Decision
                </button>
              </div>
            ))}
          </div>
        </div>

        {selectedAlloc && (
          <div className="bg-slate-800 p-6 rounded-lg border border-orange-500/30">
            <h3 className="text-lg font-semibold mb-4 text-orange-400">
              Override Allocation: {selectedAlloc.district}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm mb-1">Adjust Trucks</label>
                <input 
                  type="number" 
                  value={overrideTrucks}
                  onChange={e => setOverrideTrucks(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm mb-1">Adjust UAVs</label>
                <input 
                  type="number" 
                  value={overrideUavs}
                  onChange={e => setOverrideUavs(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Reason for Override (Required)</label>
                <textarea 
                  value={overrideReason}
                  onChange={e => setOverrideReason(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white h-24"
                  placeholder="e.g., Bridge collapsed, truck route unsafe..."
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button 
                  onClick={handleOverrideSubmit}
                  disabled={!overrideReason}
                  className="flex-1 bg-orange-600 hover:bg-orange-500 disabled:opacity-50 py-2 rounded font-medium transition-colors"
                >
                  Submit & Re-Optimize
                </button>
                <button 
                  onClick={() => setSelectedAlloc(null)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
