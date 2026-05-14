import React, { useState, useEffect } from 'react';
import { runSimulation } from '../api/simulationApi';
import { optimizeAllocation, dispatchAllocation } from '../api/allocationApi';
import { getWarehouses } from '../api/warehouseApi';
import { Zap, Play, CheckCircle, AlertTriangle, Truck, MapPin, ShieldAlert, Crosshair, Users, Navigation } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import ReliefMap from '../components/map/ReliefMap';

const SimulationPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [result, setResult] = useState<any>(null);
  const [allocationPlan, setAllocationPlan] = useState<any>(null);
  const [allWarehouses, setAllWarehouses] = useState<any[]>([]);

  useEffect(() => {
    getWarehouses().then(setAllWarehouses).catch(console.error);
  }, []);

  const [params, setParams] = useState({
    disaster_type: 'Flood',
    severity: 0.8,
    impact_radius_km: 150,
    center_lat: 19.0760,
    center_lon: 72.8777,
    budget_limit: 50000,
    priority_focus: 'balanced',
    max_warehouses: 6,
    excluded_warehouses: [] as string[]
  });

  const handleRun = async () => {
    setLoading(true);
    try {
      const data = await runSimulation(params);
      setResult(data);
      setStep(2);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    setLoading(true);
    try {
      const plan = await optimizeAllocation(result.run_id, {
        budget_limit: params.budget_limit,
        priority_focus: params.priority_focus,
        max_warehouses: params.max_warehouses,
        excluded_warehouses: params.excluded_warehouses
      });
      setAllocationPlan(plan);
      setStep(3);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      await dispatchAllocation(allocationPlan.allocation_id, allocationPlan);
      setStep(4);
      setTimeout(() => {
        navigate('/allocations');
      }, 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleDeliveryMode = (index: number) => {
    const updatedPlan = { ...allocationPlan };
    const currentMode = updatedPlan.items[index].delivery_mode;
    updatedPlan.items[index].delivery_mode = currentMode === 'truck' ? 'uav' : 'truck';
    setAllocationPlan(updatedPlan);
  };

  const updateQuantity = (index: number, newQuantity: number) => {
    if (newQuantity < 0) return;
    const updatedPlan = { ...allocationPlan };
    updatedPlan.items[index].quantity = newQuantity;
    setAllocationPlan(updatedPlan);
  };

  // Build Map Data
  const mapMarkers: any[] = [];
  const mapCircles: any[] = [];

  // Always show disaster epicenter if we are running or have results
  if (step >= 1) {
    mapMarkers.push({
      position: [params.center_lat, params.center_lon],
      label: `${params.disaster_type} Epicenter`,
      type: 'disaster',
      details: `Severity: ${params.severity}`
    });

    mapCircles.push({
      center: [params.center_lat, params.center_lon],
      radius: params.impact_radius_km * 1000,
      color: '#ef4444',
      fillColor: '#ef4444',
      fillOpacity: 0.15
    });
  }

  // Show affected districts
  if (step >= 2 && result) {
    result.affected_districts.forEach((d: any) => {
      // Generate a stable deterministic fallback based on district name length if exact coords are missing
      const stableOffsetLat = Math.sin(d.district.length * 13.5) * 1.2;
      const stableOffsetLon = Math.cos(d.district.length * 13.5) * 1.2;
      mapMarkers.push({
        position: [d.latitude || (params.center_lat + stableOffsetLat), d.longitude || (params.center_lon + stableOffsetLon)],
        label: d.district,
        type: 'impacted',
        details: `Damage: ${(d.estimated_damage_score * 10).toFixed(1)}/10`
      });
    });
  }

  // Show warehouses during Review
  if (step === 3 && allocationPlan) {
    // Collect unique warehouses
    const warehouseIds = new Set(allocationPlan.items.map((i: any) => i.source_warehouse_id));
    warehouseIds.forEach((wId) => {
      const wh = allWarehouses.find(w => w.warehouse_id === wId);
      if (wh) {
        mapMarkers.push({
          position: [wh.latitude, wh.longitude],
          label: wh.name,
          type: 'warehouse',
          details: 'Active Dispatch Hub'
        });
      }
    });
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6 overflow-hidden">

      {/* LEFT PANEL: Workflow & Controls */}
      <div className="w-full lg:w-[450px] flex flex-col h-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl shadow-sm overflow-hidden flex-shrink-0">

        {/* Header / Step Indicator */}
        <div className="p-6 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
          <h2 className="text-xl font-bold mb-4">Command Center</h2>
          <div className="flex items-center justify-between">
            <Step idx={1} active={step >= 1} current={step === 1} label="Config" />
            <div className={`flex-1 h-1 mx-2 rounded-full ${step >= 2 ? 'bg-relief-500' : 'bg-gray-200 dark:bg-gray-700'}`} />
            <Step idx={2} active={step >= 2} current={step === 2} label="Impact" />
            <div className={`flex-1 h-1 mx-2 rounded-full ${step >= 3 ? 'bg-relief-500' : 'bg-gray-200 dark:bg-gray-700'}`} />
            <Step idx={3} active={step >= 3} current={step === 3} label="Review" />
          </div>
        </div>

        {/* Scrolling Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">

          {/* STEP 1: CONFIG */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="flex items-center gap-2 text-relief-600 mb-2">
                <Crosshair size={20} />
                <h3 className="font-bold text-lg">Scenario Parameters</h3>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1.5 text-gray-700 dark:text-gray-300">Disaster Type</label>
                    <select
                      className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-relief-500"
                      value={params.disaster_type}
                      onChange={e => setParams({ ...params, disaster_type: e.target.value })}
                    >
                      <option>Flood</option>
                      <option>Cyclone</option>
                      <option>Earthquake</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1.5 text-gray-700 dark:text-gray-300">AI Priority Strategy</label>
                    <select
                      className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-relief-500"
                      value={params.priority_focus}
                      onChange={e => setParams({ ...params, priority_focus: e.target.value })}
                    >
                      <option value="balanced">Balanced</option>
                      <option value="medical">Medical Surge</option>
                      <option value="food_security">Food Security</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700 dark:text-gray-300">Severity: {(params.severity * 10).toFixed(1)}/10</label>
                  <input
                    type="range" min="0" max="1" step="0.1"
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-relief-600"
                    value={params.severity}
                    onChange={e => setParams({ ...params, severity: parseFloat(e.target.value) })}
                  />
                  <div className="flex justify-between text-[10px] text-gray-400 mt-1 uppercase font-bold">
                    <span>Minor</span>
                    <span>Catastrophic</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700 dark:text-gray-300">Impact Radius: {params.impact_radius_km} km</label>
                  <input
                    type="range" min="10" max="500" step="10"
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-relief-600"
                    value={params.impact_radius_km}
                    onChange={e => setParams({ ...params, impact_radius_km: parseInt(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700 dark:text-gray-300">Logistics Budget Cap ($)</label>
                  <input
                    type="number"
                    className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-relief-500"
                    value={params.budget_limit}
                    onChange={e => setParams({ ...params, budget_limit: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              {/* WAREHOUSE DESTRUCTION SIMULATION */}
              <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                <div className="flex items-center gap-2 text-red-600 mb-2">
                  <ShieldAlert size={20} />
                  <h3 className="font-bold text-lg">Infrastructure Constraints</h3>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Active Warehouse Pool</label>
                    <span className="text-xs font-bold bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">{params.max_warehouses} Hubs</span>
                  </div>
                  <input
                    type="range" min="1" max={Math.max(1, allWarehouses.length)} step="1"
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-red-500"
                    value={params.max_warehouses}
                    onChange={e => setParams({ ...params, max_warehouses: parseInt(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Simulate Hub Destruction</label>
                  <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto pr-2 custom-scrollbar">
                    {allWarehouses.map(wh => {
                      const isExcluded = params.excluded_warehouses.includes(wh.warehouse_id);
                      return (
                        <div
                          key={wh.warehouse_id}
                          onClick={() => {
                            if (isExcluded) {
                              setParams({ ...params, excluded_warehouses: params.excluded_warehouses.filter((id: string) => id !== wh.warehouse_id) });
                            } else {
                              setParams({ ...params, excluded_warehouses: [...params.excluded_warehouses, wh.warehouse_id] });
                            }
                          }}
                          className={`cursor-pointer border p-2 rounded-lg text-xs font-medium flex justify-between items-center transition-all ${isExcluded
                              ? 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-900/50 dark:text-red-400'
                              : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300'
                            }`}
                        >
                          <span className="truncate pr-2">{wh.name}</span>
                          {isExcluded && <span className="text-[10px] uppercase font-bold bg-red-100 text-red-600 px-1 rounded">Destroyed</span>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-800">
                <button
                  onClick={handleRun}
                  disabled={loading}
                  className="w-full py-4 bg-relief-600 hover:bg-relief-700 text-black font-bold rounded-2xl shadow-lg shadow-relief-500/30 transition-all flex items-center justify-center gap-3 disabled:opacity-70"
                >
                  {loading ? 'Simulating Impact...' : <><Zap size={20} fill="black" /> Run AI Simulation</>}
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: IMPACT ANALYSIS */}
          {step === 2 && result && (
            <div className="space-y-6 animate-in slide-in-from-right-8 duration-500">
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-2xl flex items-start gap-4">
                <ShieldAlert className="text-red-500 shrink-0" size={24} />
                <div>
                  <h3 className="font-bold text-red-900 dark:text-red-400">{result.affected_districts.length} Districts Affected</h3>
                  <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                    Simulation indicates severe infrastructure damage and immediate supply shortages.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-gray-500 tracking-wider">Most Vulnerable Areas</h4>
                {result.affected_districts.slice(0, 4).map((d: any) => (
                  <div key={d.district} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                    <div>
                      <p className="font-bold text-sm">{d.district}</p>
                      <p className="text-[10px] text-gray-500 mt-0.5">Shortage: {(d.estimated_shortage_rice_tons + d.estimated_shortage_wheat_tons).toFixed(1)}T food</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-bold text-red-500">{(d.estimated_damage_score * 10).toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-800">
                <button
                  onClick={handleOptimize}
                  disabled={loading}
                  className="w-full py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold rounded-2xl shadow-lg transition-all flex items-center justify-center gap-3 disabled:opacity-70 hover:opacity-90"
                >
                  {loading ? 'Running Router AI...' : <><Truck size={20} /> Generate Allocation Plan</>}
                </button>
                <button onClick={() => setStep(1)} className="w-full mt-2 py-3 text-sm font-semibold text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Adjust Parameters
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: HUMAN IN THE LOOP REVIEW */}
          {step === 3 && allocationPlan && (
            <div className="space-y-6 animate-in slide-in-from-right-8 duration-500">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/30 rounded-2xl">
                <h3 className="font-bold text-blue-900 dark:text-blue-400 flex items-center gap-2 mb-2">
                  <Users size={20} /> Human-in-the-Loop Review
                </h3>
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  The AI has generated an optimal supply route based on your parameters. <b>Review and edit the quantities or delivery modes</b> before finalizing the dispatch.
                </p>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-2xl space-y-4">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Logistics Cost:</span>
                  <span className="font-bold">${allocationPlan.total_cost_estimated.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">AI Optimization:</span>
                  <span className="font-bold text-relief-600 uppercase text-xs">{allocationPlan.optimized_by.replace('_', ' ')}</span>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-gray-500 tracking-wider">AI Suggested Routes (Editable)</h4>
                <div className="max-h-64 overflow-y-auto pr-2 space-y-3">
                  {allocationPlan.items.map((item: any, idx: number) => (
                    <div key={idx} className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-bold text-gray-900 dark:text-white">{item.destination_district}</span>
                        <span className="text-[10px] font-bold px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-md text-gray-500 uppercase">{item.item_type}</span>
                      </div>

                      <div className="flex items-center justify-between gap-4">
                        <div className="flex-1">
                          <label className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Quantity ({item.item_type === 'medicine' ? 'Kits' : 'Tons'})</label>
                          <input
                            type="number"
                            className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 text-sm font-bold focus:ring-2 focus:ring-relief-500 outline-none"
                            value={item.quantity.toFixed(1)}
                            onChange={(e) => updateQuantity(idx, parseFloat(e.target.value))}
                          />
                        </div>

                        <div>
                          <label className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Delivery Mode</label>
                          <button
                            onClick={() => toggleDeliveryMode(idx)}
                            className={clsx(
                              "text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1.5 transition-colors w-full justify-center",
                              item.delivery_mode === 'uav'
                                ? "bg-relief-100 text-relief-700 dark:bg-relief-900/30 dark:text-relief-400"
                                : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                            )}
                          >
                            {item.delivery_mode === 'uav' ? <Navigation size={14} /> : <Truck size={14} />}
                            {item.delivery_mode.toUpperCase()}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-800 flex gap-3">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 py-4 border border-red-200 dark:border-red-900/30 text-red-600 bg-red-50 dark:bg-red-900/10 font-bold rounded-2xl hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                >
                  Reject
                </button>
                <button
                  onClick={handleApprove}
                  disabled={loading}
                  className="flex-[2] py-4 bg-green-600 hover:bg-green-700 text-white font-bold rounded-2xl shadow-lg shadow-green-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                >
                  {loading ? 'Dispatching...' : <><CheckCircle size={20} /> Approve & Dispatch</>}
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: DISPATCHED */}
          {step === 4 && (
            <div className="space-y-6 text-center animate-in zoom-in-95 duration-500 pt-10">
              <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle size={40} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Assets Dispatched!</h3>
              <p className="text-gray-500">Warehouse stock reduced. The field units have been notified. Redirecting...</p>
            </div>
          )}

        </div>
      </div>

      {/* RIGHT PANEL: Live Map */}
      <div className="flex-1 relative rounded-3xl overflow-hidden shadow-sm border border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-gray-900">
        {/* Map UI Overlay Elements */}
        <div className="absolute top-6 left-6 z-10 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md px-4 py-2 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${loading ? 'bg-orange-500 animate-ping' : 'bg-green-500'}`} />
          <span className="text-sm font-bold text-gray-800 dark:text-white">
            {step === 1 ? 'Simulation Setup' : step === 2 ? 'Impact Analysis Live' : step === 3 ? 'Reviewing Routes' : 'Live Tracking'}
          </span>
        </div>

        <ReliefMap
          center={[params.center_lat, params.center_lon]}
          zoom={step === 1 ? 6 : 7}
          markers={mapMarkers}
          circles={mapCircles}
        />
      </div>

    </div>
  );
};

const Step = ({ idx, active, current, label }: { idx: number, active: boolean, current: boolean, label: string }) => (
  <div className="flex flex-col items-center gap-1.5 z-10 relative">
    <div className={clsx(
      "w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300",
      current ? "bg-relief-600 text-white scale-110 shadow-lg shadow-relief-500/40 ring-4 ring-relief-100 dark:ring-relief-900/30" :
        active ? "bg-relief-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-400 border border-gray-200 dark:border-gray-700"
    )}>
      {active && !current ? <CheckCircle size={14} /> : idx}
    </div>
    <span className={clsx("text-[10px] font-bold uppercase tracking-wider", current ? "text-relief-600" : active ? "text-gray-900 dark:text-white" : "text-gray-400")}>
      {label}
    </span>
  </div>
);

export default SimulationPage;
