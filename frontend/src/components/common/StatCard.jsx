// ─── src/components/common/StatCard.jsx ──────────────────────────────────────
import React from "react";
const colors = { blue:"bg-blue-100 text-blue-800", red:"bg-red-100 text-red-800",
                 orange:"bg-orange-100 text-orange-800" };
export default function StatCard({ title, value, color = "blue" }) {
  return (
    <div className={`rounded-xl p-4 shadow ${colors[color]}`}>
      <p className="text-sm font-medium opacity-70">{title}</p>
      <p className="text-3xl font-bold mt-1">{value?.toLocaleString() || 0}</p>
    </div>
  );
}