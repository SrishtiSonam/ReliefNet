import React, { useState } from 'react';

const ControlPanel = ({ onSimulationUpdate }) => {
    const [logs, setLogs] = useState(["System initialized..."]);
    const [emergencyMode, setEmergencyMode] = useState(false);
    const [manualAllocation, setManualAllocation] = useState({
        amount: '',
        fromDistrict: 'depot',
        toDistrict: '1'
    });

    const districts = [
        { id: 0, name: 'District A' },
        { id: 1, name: 'District B' },
        { id: 2, name: 'District C' },
        { id: 3, name: 'District D' },
        { id: 4, name: 'District E' },
        { id: 5, name: 'District F' },
        { id: 6, name: 'District G' },
        { id: 7, name: 'District H' },
        { id: 8, name: 'District I' },
        { id: 9, name: 'District J' },
        { id: 10, name: 'District K' },
        { id: 11, name: 'District L' },
    ];

    const runSimulation = async () => {
        setLogs(prev => [...prev, "Running simulation step..."]);
        try {
            const res = await fetch('http://localhost:8000/api/simulate_step', { method: 'POST' });
            const data = await res.json();
            setLogs(prev => [...prev, `Step ${data.step}: Demand ${Object.values(data.demand).reduce((a, b) => a + b, 0)}`]);

            if (onSimulationUpdate) {
                onSimulationUpdate(data);
            }
        } catch (e) {
            setLogs(prev => [...prev, "Error connecting to backend"]);
        }
    };

    const optimizeRoutes = async () => {
        setLogs(prev => [...prev, "Optimizing vehicle routes..."]);
        try {
            const simRes = await fetch('http://localhost:8000/api/simulate_step', { method: 'POST' });
            const simData = await simRes.json();

            const allocRes = await fetch('http://localhost:8000/api/allocate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    demand: simData.demand,
                    inventory: simData.inventory
                })
            });
            const allocData = await allocRes.json();

            if (allocData.allocation && allocData.allocation.length > 0) {
                setLogs(prev => [...prev, `✓ Optimized ${allocData.allocation.length} deliveries`]);
                allocData.allocation.slice(0, 3).forEach(a => {
                    setLogs(prev => [...prev, `  → ${a.vehicle_type} to District ${a.district_id}: ${a.amount} units`]);
                });
            } else {
                setLogs(prev => [...prev, "⚠ No allocation (OR-Tools not available)"]);
            }
        } catch (e) {
            setLogs(prev => [...prev, "Error: " + e.message]);
        }
    };

    const emergencyOverride = () => {
        setEmergencyMode(!emergencyMode);
        if (!emergencyMode) {
            setLogs(prev => [...prev, "🚨 EMERGENCY OVERRIDE ACTIVATED"]);
            setLogs(prev => [...prev, "Manual control enabled"]);
            setLogs(prev => [...prev, "All automated allocations paused"]);
            setLogs(prev => [...prev, "Use the form below to manually allocate resources"]);
        } else {
            setLogs(prev => [...prev, "Emergency mode deactivated"]);
            setLogs(prev => [...prev, "Returning to normal operations"]);
        }
    };

    const executeManualAllocation = () => {
        if (!manualAllocation.amount || manualAllocation.amount <= 0) {
            setLogs(prev => [...prev, "⚠ Please enter a valid amount"]);
            return;
        }

        // Check if source and destination are the same
        if (manualAllocation.fromDistrict === manualAllocation.toDistrict) {
            setLogs(prev => [...prev, "⚠ Error: Source and destination cannot be the same"]);
            return;
        }

        const fromName = manualAllocation.fromDistrict === 'depot' ? 'Central Depot' : districts.find(d => d.id === parseInt(manualAllocation.fromDistrict))?.name;
        const toName = districts.find(d => d.id === parseInt(manualAllocation.toDistrict))?.name;

        setLogs(prev => [...prev, `✓ Manual allocation: ${manualAllocation.amount} units`]);
        setLogs(prev => [...prev, `  From: ${fromName} → To: ${toName}`]);
        setLogs(prev => [...prev, `  Dispatching vehicle...`]);
        setLogs(prev => [...prev, `  ETA: 15 minutes`]);

        // Reset form
        setManualAllocation({ amount: '', fromDistrict: 'depot', toDistrict: '1' });
    };

    const resetSimulation = async () => {
        setLogs(prev => [...prev, "Resetting simulation..."]);
        try {
            await fetch('http://localhost:8000/api/reset_sim', { method: 'POST' });
            setLogs(["System reset complete. Ready to start."]);
            setEmergencyMode(false);
        } catch (e) {
            setLogs(prev => [...prev, "Error resetting simulation"]);
        }
    };

    return (
        <div className="w-80 bg-gray-800 p-4 rounded-lg flex flex-col h-[600px]">
            <h2 className="text-xl font-bold mb-4">Control Center</h2>
            <div className="space-y-2 mb-4">
                <button onClick={runSimulation} className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-bold" disabled={emergencyMode}>Run Next Step</button>
                <button onClick={optimizeRoutes} className="w-full bg-yellow-600 hover:bg-yellow-700 py-2 rounded font-bold" disabled={emergencyMode}>Optimize Routes</button>
                <button onClick={emergencyOverride} className={`w-full py-2 rounded font-bold ${emergencyMode ? 'bg-red-800 hover:bg-red-900 animate-pulse' : 'bg-red-600 hover:bg-red-700'}`}>
                    {emergencyMode ? '🚨 Deactivate Override' : 'Emergency Override'}
                </button>
                <button onClick={resetSimulation} className="w-full bg-gray-600 hover:bg-gray-700 py-2 rounded font-bold text-sm">Reset Simulation</button>
            </div>

            {emergencyMode && (
                <div className="mb-3 p-3 bg-red-900 bg-opacity-30 border border-red-500 rounded">
                    <div className="text-xs font-bold text-red-400 mb-3">⚡ MANUAL ALLOCATION</div>

                    <div className="space-y-2">
                        <div>
                            <label className="text-xs text-gray-400 block mb-1">Amount (units)</label>
                            <input
                                type="number"
                                value={manualAllocation.amount}
                                onChange={(e) => setManualAllocation({ ...manualAllocation, amount: e.target.value })}
                                placeholder="Enter amount..."
                                className="w-full px-2 py-1 bg-gray-900 text-white text-sm rounded border border-red-500 focus:outline-none focus:border-red-400"
                            />
                        </div>

                        <div>
                            <label className="text-xs text-gray-400 block mb-1">From District (Source)</label>
                            <select
                                value={manualAllocation.fromDistrict}
                                onChange={(e) => setManualAllocation({ ...manualAllocation, fromDistrict: e.target.value })}
                                className="w-full px-2 py-1 bg-gray-900 text-white text-sm rounded border border-red-500 focus:outline-none focus:border-red-400"
                            >
                                <option value="depot">Central Depot</option>
                                {districts.map(d => (
                                    <option key={d.id} value={d.id}>{d.name}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="text-xs text-gray-400 block mb-1">To District (Destination)</label>
                            <select
                                value={manualAllocation.toDistrict}
                                onChange={(e) => setManualAllocation({ ...manualAllocation, toDistrict: e.target.value })}
                                className="w-full px-2 py-1 bg-gray-900 text-white text-sm rounded border border-red-500 focus:outline-none focus:border-red-400"
                            >
                                {districts.map(d => (
                                    <option key={d.id} value={d.id}>{d.name}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            onClick={executeManualAllocation}
                            className="w-full mt-2 px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm font-bold"
                        >
                            DISPATCH NOW
                        </button>
                    </div>
                </div>
            )}

            <div className="flex-grow bg-gray-900 p-2 rounded overflow-y-auto font-mono text-xs text-green-400">
                {logs.map((log, i) => (
                    <div key={i}>&gt; {log}</div>
                ))}
            </div>
        </div>
    );
};

export default ControlPanel;
