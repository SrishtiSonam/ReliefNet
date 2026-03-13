// ─── src/pages/Simulation.jsx ─────────────────────────────────────────────────
import React, { useState, useEffect } from "react";
import { getDistricts }  from "../api/districtApi";
import { runSimulation, getSimStatus } from "../api/simulationApi";
import { useNavigate }   from "react-router-dom";

const METHODS = ["dl_vfa", "nn_vfa", "ppo", "rule_based"];

export default function Simulation() {
  const [districts, setDistricts] = useState([]);
  const [selected,  setSelected]  = useState([]);
  const [methods,   setMethods]   = useState(["dl_vfa", "rule_based"]);
  const [config,    setConfig]    = useState({
    name: "New Simulation", case_study: "custom",
    n_periods: 30, period_hours: 6,
    truck_capacity: 5000, uav_capacity: 200,
    supply_cov: 0.2, demand_cov: 0.2, n_training_episodes: 500
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getDistricts().then(r => setDistricts(r.data.districts || []));
  }, []);

  const toggleDistrict = (name) =>
    setSelected(s => s.includes(name) ? s.filter(x => x !== name) : [...s, name]);

  const toggleMethod = (m) =>
    setMethods(ms => ms.includes(m) ? ms.filter(x => x !== m) : [...ms, m]);

  const submit = async () => {
    if (!selected.length || !methods.length) return;
    setLoading(true);
    try {
      const { data } = await runSimulation({
        ...config, selected_districts: selected, methods,
        warehouse_id: "default"
      });
      navigate(`/results/${data.fastapi_id}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6 text-blue-800">⚙️ Configure Simulation</h1>

      <div className="bg-white rounded-xl shadow p-4 mb-4">
        <h2 className="font-semibold mb-2">Simulation Name</h2>
        <input className="border rounded px-3 py-2 w-full"
          value={config.name}
          onChange={e => setConfig(c => ({ ...c, name: e.target.value }))} />
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-4">
        <h2 className="font-semibold mb-2">Select Districts</h2>
        <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
          {districts.slice(0, 60).map(d => (
            <label key={d.dist_name} className="flex items-center gap-2 text-sm">
              <input type="checkbox"
                checked={selected.includes(d.dist_name)}
                onChange={() => toggleDistrict(d.dist_name)} />
              {d.dist_name}
            </label>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-4">
        <h2 className="font-semibold mb-2">Select Methods</h2>
        <div className="flex gap-4">
          {METHODS.map(m => (
            <label key={m} className="flex items-center gap-2">
              <input type="checkbox"
                checked={methods.includes(m)}
                onChange={() => toggleMethod(m)} />
              <span className="capitalize">{m.replace("_", "-")}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-4 grid grid-cols-2 gap-4">
        {[
          ["Periods",       "n_periods",           30],
          ["Period Hours",  "period_hours",          6],
          ["Truck Cap.",    "truck_capacity",      5000],
          ["UAV Cap.",      "uav_capacity",         200],
          ["Training Eps.", "n_training_episodes",  500],
        ].map(([label, key, def]) => (
          <div key={key}>
            <label className="text-sm font-medium">{label}</label>
            <input type="number" className="border rounded px-3 py-2 w-full mt-1"
              value={config[key]}
              onChange={e => setConfig(c => ({ ...c, [key]: +e.target.value }))} />
          </div>
        ))}
      </div>

      <button onClick={submit} disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold
                   hover:bg-blue-700 disabled:opacity-50">
        {loading ? "Running..." : "🚀 Run Simulation"}
      </button>
    </div>
  );
}