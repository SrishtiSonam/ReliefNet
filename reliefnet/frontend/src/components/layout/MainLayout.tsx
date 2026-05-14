import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  Warehouse,
  Zap,
  Truck,
  Globe,
  Settings,
  Bell,
  UserCircle,
  Users
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const SidebarLink = ({ to, icon: Icon, children, active }: { to: string, icon: any, children: React.ReactNode, active: boolean }) => (
  <Link
    to={to}
    className={cn(
      "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200",
      active
        ? "bg-yellow-100 text-black shadow-md"
        : "text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
    )}
  >
    <Icon size={20} />
    <span className="font-medium">{children}</span>
  </Link>
);

const MainLayout: React.FC = () => {
  const location = useLocation();

  const links = [
    { to: "/", icon: LayoutDashboard, label: "Dashboard" },
    { to: "/districts", icon: Map, label: "Districts" },
    { to: "/warehouses", icon: Warehouse, label: "Warehouses" },
    { to: "/simulation", icon: Zap, label: "Simulation" },
    { to: "/allocations", icon: Truck, label: "Allocations" },
    { to: "/requests", icon: Users, label: "Citizen Requests" },
    { to: "/portal", icon: Globe, label: "Public Portal" },
  ];

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-relief-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              RN
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">ReliefNet</span>
          </div>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          {links.map((link) => (
            <SidebarLink
              key={link.to}
              to={link.to}
              icon={link.icon}
              active={location.pathname === link.to}
            >
              {link.label}
            </SidebarLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <SidebarLink to="/settings" icon={Settings} active={location.pathname === "/settings"}>
            Settings
          </SidebarLink>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              {links.find(l => l.to === location.pathname)?.label || "ReliefNet"}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-900"></span>
            </button>
            <div className="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-gray-800">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white">Admin User</p>
                <p className="text-xs text-gray-500">Relief Coordinator</p>
              </div>
              <UserCircle size={32} className="text-gray-400" />
            </div>
          </div>
        </header>

        {/* Page Area */}
        <div className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-950 p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
