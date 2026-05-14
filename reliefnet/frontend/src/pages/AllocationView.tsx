import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Truck, Package, MapPin, CheckCircle, Navigation } from 'lucide-react';

const AllocationView: React.FC = () => {
  const [plans, setPlans] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await apiClient.get('/allocation/latest?limit=1');
        setPlans(response.data);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPlans();
  }, []);

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Loading allocations...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Relief Distribution Plans</h2>
          <p className="text-gray-500">AI-optimized logistics and dispatch schedules</p>
        </div>
      </div>

      <div className="space-y-6">
        {plans.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 text-center text-gray-500">
            No allocations found. Run a simulation first!
          </div>
        ) : (
          plans.map((plan: any) => (
            <div key={plan.allocation_id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl overflow-hidden shadow-sm">
              <div className="bg-gray-50 dark:bg-gray-800/50 px-8 py-6 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-relief-600 text-white rounded-2xl">
                    <Navigation size={24} />
                  </div>
                  <div>
                    <h3 className="font-bold">Plan #{plan.allocation_id}</h3>
                    <p className="text-xs text-gray-500">Optimized by {plan.optimized_by.replace('_', ' ')}</p>
                  </div>
                </div>
                <div className="text-right flex items-center gap-4">
                  <div className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-bold">{plan.status || 'ACTIVE'}</div>
                  <div>
                    <p className="text-sm font-bold text-relief-600">${plan.total_cost_estimated.toLocaleString()}</p>
                    <p className="text-[10px] uppercase text-gray-400">Est. Logistics Cost</p>
                  </div>
                </div>
              </div>

              <div className="p-8">
                <div className="space-y-4">
                  {plan.items.map((item: any, idx: number) => (
                    <AllocationRow 
                      key={idx}
                      source={item.source_warehouse_id} 
                      dest={item.destination_district} 
                      item={item.item_type} 
                      qty={`${item.quantity.toFixed(1)} ${item.item_type === 'medicine' ? 'Kits' : 'T'}`} 
                      mode={item.delivery_mode.toUpperCase()} 
                      status={plan.status === 'DISPATCHED' ? 'Dispatched' : 'Ready'} 
                    />
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const AllocationRow = ({ source, dest, item, qty, mode, status }: any) => (
  <div className="flex items-center justify-between p-4 border border-gray-100 dark:border-gray-800 rounded-2xl hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
    <div className="flex items-center gap-6 flex-1">
      <div className="flex items-center gap-3 min-w-[200px]">
        <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-400"><WarehouseIcon size={16} /></div>
        <span className="text-sm font-semibold">{source}</span>
      </div>
      <div className="flex items-center gap-2 text-gray-300">
        <div className="w-8 h-px bg-current" />
        <Truck size={16} className={mode === 'UAV' ? 'rotate-[-20deg] text-relief-500' : 'text-blue-500'} />
        <div className="w-8 h-px bg-current" />
      </div>
      <div className="flex items-center gap-3 min-w-[200px]">
        <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-400"><MapPin size={16} /></div>
        <span className="text-sm font-semibold">{dest}</span>
      </div>
    </div>
    
    <div className="flex items-center gap-8">
      <div className="text-right min-w-[100px]">
        <p className="text-sm font-bold text-gray-900 dark:text-white">{qty}</p>
        <p className="text-[10px] text-gray-400 uppercase">{item}</p>
      </div>
      <div className="flex items-center gap-2 px-3 py-1 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
        <CheckCircle size={14} />
        <span className="text-[10px] font-bold uppercase">{status}</span>
      </div>
    </div>
  </div>
);

const WarehouseIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M3 7v1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7H3Z"/><path d="M9 17h6"/><path d="M10 21V13h4v8"/></svg>
);

export default AllocationView;
