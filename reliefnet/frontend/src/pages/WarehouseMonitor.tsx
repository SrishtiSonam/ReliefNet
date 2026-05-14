import React, { useEffect, useState } from 'react';
import { getWarehouses } from '../api/warehouseApi';
import apiClient from '../api/client';
import { Package, Truck, AlertCircle, TrendingDown, History, Plus, Minus, X } from 'lucide-react';
import { clsx } from 'clsx';

const WarehouseMonitor: React.FC = () => {
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [activePlanIds, setActivePlanIds] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'ALL' | 'ACTIVE'>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedWarehouse, setSelectedWarehouse] = useState<any | null>(null);

  const fetchWarehouses = async () => {
    try {
      const [data, planResponse] = await Promise.all([
        getWarehouses(),
        apiClient.get('/allocation/latest?limit=1')
      ]);
      setWarehouses(data);
      
      const plans = planResponse.data;
      if (plans && plans.length > 0) {
        setActivePlanIds(new Set(plans[0].items.map((i: any) => i.source_warehouse_id)));
      }
      
      if (selectedWarehouse) {
        setSelectedWarehouse(data.find((w: any) => w.warehouse_id === selectedWarehouse.warehouse_id));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const displayWarehouses = viewMode === 'ALL' 
    ? warehouses 
    : warehouses.filter(w => activePlanIds.has(w.warehouse_id));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white dark:bg-gray-900 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
        <h2 className="font-bold text-lg">Warehouse Logistics Network</h2>
        <div className="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-xl">
          <button 
            onClick={() => setViewMode('ALL')}
            className={clsx("px-4 py-2 rounded-lg text-sm font-bold transition-all", viewMode === 'ALL' ? "bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white" : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300")}
          >
            Global Network
          </button>
          <button 
            onClick={() => setViewMode('ACTIVE')}
            className={clsx("px-4 py-2 rounded-lg text-sm font-bold transition-all", viewMode === 'ACTIVE' ? "bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white" : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300")}
          >
            Active in Simulation
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative">
        {isLoading ? (
          <div className="col-span-full py-12 text-center text-gray-400">Loading warehouses...</div>
        ) : displayWarehouses.map((w) => (
          <div key={w.warehouse_id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white text-lg">{w.name}</h3>
                <p className="text-sm text-gray-500">{w.district}, {w.state}</p>
              </div>
              <div className="p-2 bg-relief-50 dark:bg-relief-900/20 text-relief-600 rounded-xl">
                <Package size={20} />
              </div>
            </div>

            <div className="space-y-4 flex-1">
              <ResourceBar label="Rice" current={w.stock_rice_tons} total={w.capacity_tons / 2} unit="Tons" />
              <ResourceBar label="Wheat" current={w.stock_wheat_tons} total={w.capacity_tons / 2} unit="Tons" />
              <ResourceBar label="Med Kits" current={w.stock_medicine_kits} total={5000} unit="Kits" />
            </div>

            <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
                <History size={14} />
                <span>{w.transactions?.length || 0} Transactions</span>
              </div>
              <button 
                onClick={() => setSelectedWarehouse(w)}
                className="text-xs font-bold px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                Manage Stock
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedWarehouse && (
        <ManageStockModal 
          warehouse={selectedWarehouse} 
          onClose={() => setSelectedWarehouse(null)} 
          onSuccess={fetchWarehouses}
        />
      )}
    </div>
  );
};

const ManageStockModal = ({ warehouse, onClose, onSuccess }: any) => {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ resource: 'rice', amount: 0, type: 'ADD', reason: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post(`/warehouses/${warehouse.warehouse_id}/transaction`, form);
      onSuccess();
      setForm({ ...form, amount: 0, reason: '' }); // reset
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in">
      <div className="bg-white dark:bg-gray-900 rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex shadow-2xl border border-gray-200 dark:border-gray-800">
        
        {/* Left Side: Ledger */}
        <div className="flex-1 border-r border-gray-100 dark:border-gray-800 flex flex-col bg-gray-50 dark:bg-gray-800/30">
          <div className="p-6 border-b border-gray-100 dark:border-gray-800">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <History size={18} /> Transaction Ledger
            </h3>
            <p className="text-sm text-gray-500">Immutable history of inventory changes</p>
          </div>
          <div className="p-6 flex-1 overflow-y-auto space-y-3">
            {(!warehouse.transactions || warehouse.transactions.length === 0) ? (
              <p className="text-gray-400 text-sm italic">No transactions recorded yet.</p>
            ) : (
              [...warehouse.transactions].reverse().map((txn: any, i: number) => (
                <div key={i} className="p-4 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl">
                  <div className="flex justify-between items-start mb-2">
                    <span className={clsx("text-xs font-bold px-2 py-0.5 rounded", txn.type === 'ADD' ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700")}>
                      {txn.type}
                    </span>
                    <span className="text-[10px] text-gray-400">{new Date(txn.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-sm font-medium">
                    {txn.type === 'ADD' ? '+' : '-'}{txn.amount} <span className="uppercase">{txn.resource}</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Reason: {txn.reason}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="w-[400px] flex flex-col">
          <div className="p-6 flex justify-between items-center border-b border-gray-100 dark:border-gray-800">
            <h2 className="font-bold text-xl">{warehouse.name}</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors">
              <X size={20} />
            </button>
          </div>
          <div className="p-6 flex-1 overflow-y-auto">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Resource Type</label>
                <select className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" value={form.resource} onChange={e => setForm({...form, resource: e.target.value})}>
                  <option value="rice">Rice (Tons)</option>
                  <option value="wheat">Wheat (Tons)</option>
                  <option value="medicine">Medicine (Kits)</option>
                  <option value="tarpaulin">Tarpaulin (Units)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Transaction Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button type="button" onClick={() => setForm({...form, type: 'ADD'})} className={clsx("py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 border-2 transition-all", form.type === 'ADD' ? "border-green-500 bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400" : "border-transparent bg-gray-50 dark:bg-gray-800 text-gray-400")}>
                    <Plus size={16} /> Restock
                  </button>
                  <button type="button" onClick={() => setForm({...form, type: 'SUBTRACT'})} className={clsx("py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 border-2 transition-all", form.type === 'SUBTRACT' ? "border-red-500 bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400" : "border-transparent bg-gray-50 dark:bg-gray-800 text-gray-400")}>
                    <Minus size={16} /> Deduct
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Amount</label>
                <input type="number" step="any" required min="0.1" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" value={form.amount || ''} onChange={e => setForm({...form, amount: parseFloat(e.target.value)})} />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Reason / Auth Code</label>
                <input type="text" required placeholder="e.g. Received from FEMA" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" value={form.reason} onChange={e => setForm({...form, reason: e.target.value})} />
              </div>

              <button type="submit" disabled={loading} className="w-full py-4 mt-4 bg-relief-600 hover:bg-relief-700 text-white font-bold rounded-2xl shadow-lg transition-all disabled:opacity-50">
                {loading ? 'Processing...' : 'Execute Transaction'}
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}

const ResourceBar = ({ label, current, total, unit }: { label: string, current: number, total: number, unit: string }) => {
  const pct = Math.min((current / total) * 100, 100);
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs font-medium">
        <span className="text-gray-500">{label}</span>
        <span className="text-gray-900 dark:text-white">{current.toFixed(0)} / {total.toFixed(0)} {unit}</span>
      </div>
      <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div 
          className={clsx("h-full rounded-full transition-all duration-500", 
            pct < 20 ? "bg-red-500" : pct < 50 ? "bg-orange-500" : "bg-green-500"
          )} 
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
};

export default WarehouseMonitor;
