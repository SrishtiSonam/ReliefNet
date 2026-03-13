// ─── src/pages/Results.jsx ────────────────────────────────────────────────────
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSimStatus } from "../api/simulationApi";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = { dl_vfa:"#3b82f6", nn_vfa:"#10b981", ppo:"#f59e0b", rule_based:"#ef4444" };

export default function Results() {
  const { id }  = useParams();
  const [sim, setSim] = useState(null);

  useEffect(() => {
    const poll = setInterval(async () => {
      const { data } = await getSimStatus(id);
      setSim(data);
      if (data.status === "completed" || data.status === "failed") clearInterval(poll);
    }, 3000);
    return () => clearInterval(poll);
  }, [id]);

  if (!sim) return <div className="p-6">Loading...</div>;
  if (sim.status === "running" || sim.status === "pending")
    return <div className="p-6 text-blue-600">⏳ Simulation {sim.status}... auto-refreshing</div>;
  if (sim.status === "failed")
    return <div className="p-6 text-red-600">❌ Simulation failed: {sim.error}</div>;

  const results = sim.results || [];
  const chartData = [
    { metric: "Total Cost",        ...Object.fromEntries(results.map(r => [r.method, r.total_cost])) },
    { metric: "Deprivation Cost",  ...Object.fromEntries(results.map(r => [r.method, r.deprivation_cost])) },
    { metric: "Transport Cost",    ...Object.fromEntries(results.map(r => [r.method, r.transport_cost])) },
    { metric: "Max Dep. Time (h)", ...Object.fromEntries(results.map(r => [r.method, r.max_deprivation_time])) },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4 text-blue-800">📊 Simulation Results</h1>
      <p className="text-gray-500 mb-6">ID: {id}</p>

      {/* Summary Table */}
      <div className="bg-white rounded-xl shadow p-4 mb-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              <th className="p-2 text-left">Method</th>
              <th className="p-2">Total Cost</th>
              <th className="p-2">Deprivation Cost</th>
              <th className="p-2">Transport Cost</th>
              <th className="p-2">Max Dep. Time</th>
            </tr>
          </thead>
          <tbody>
            {results.map(r => (
              <tr key={r.method} className="border-t">
                <td className="p-2 font-semibold capitalize">{r.method.replace("_", "-")}</td>
                <td className="p-2 text-center">{r.total_cost?.toFixed(0)}</td>
                <td className="p-2 text-center">{r.deprivation_cost?.toFixed(0)}</td>
                <td className="p-2 text-center">{r.transport_cost?.toFixed(0)}</td>
                <td className="p-2 text-center">{r.max_deprivation_time}h</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Comparison Bar Chart */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="font-semibold mb-4">Method Comparison</h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData}>
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />
            <Legend />
            {results.map(r => (
              <Bar key={r.method} dataKey={r.method}
                   fill={COLORS[r.method] || "#6b7280"} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}