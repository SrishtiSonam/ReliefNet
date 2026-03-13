// ─── src/pages/Dashboard.jsx ─────────────────────────────────────────────────
import React, { useEffect, useState } from "react";
import { getDFSI }        from "../api/districtApi";
import { getFloodEvents } from "../api/floodEventApi";
import StatCard           from "../components/common/StatCard";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const [dfsi, setDfsi]     = useState([]);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    getDFSI().then(r => setDfsi(r.data.dfsi_scores || []));
    getFloodEvents({ limit: 500 }).then(r => setEvents(r.data.flood_events || []));
  }, []);

  const top10 = [...dfsi].sort((a, b) => b.dfsi - a.dfsi).slice(0, 10);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 text-blue-800">
        🌊 India Flood Relief — Dashboard
      </h1>
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard title="Total Districts" value={dfsi.length}        color="blue" />
        <StatCard title="Flood Events"    value={events.length}      color="red"  />
        <StatCard title="Severe Floods"   value={
          events.filter(e => e.flood_type === "Severe Flood").length} color="orange" />
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Top 10 High-Risk Districts (DFSI)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={top10}>
            <XAxis dataKey="dist_name" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="dfsi" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}