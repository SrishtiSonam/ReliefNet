// ─── src/components/layout/Layout.jsx ────────────────────────────────────────
import React from "react";
import { Link, useLocation } from "react-router-dom";

const NAV = [
  { path: "/",             label: "Dashboard",    icon: "🏠" },
  { path: "/districts",    label: "Districts",    icon: "🗺️" },
  { path: "/flood-events", label: "Flood Events", icon: "🌊" },
  { path: "/simulation",   label: "Simulation",   icon: "⚙️" },
  { path: "/case-study",   label: "Kerala 2018",  icon: "🔬" },
  { path: "/data",         label: "Data",         icon: "📂" },
];

export default function Layout({ children }) {
  const loc = useLocation();
  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-56 bg-blue-900 text-white flex flex-col">
        <div className="p-4 font-bold text-lg border-b border-blue-700">
          🌧️ Flood Relief AI
        </div>
        <nav className="flex-1 p-2">
          {NAV.map(({ path, label, icon }) => (
            <Link key={path} to={path}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-1 text-sm
                         transition-colors ${loc.pathname === path
                           ? "bg-blue-600" : "hover:bg-blue-800"}`}>
              <span>{icon}</span>{label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}