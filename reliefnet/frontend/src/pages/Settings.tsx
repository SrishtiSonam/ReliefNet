import React from 'react';
import { Settings as SettingsIcon, Bell, Shield, Database, Palette } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
        <h2 className="font-bold text-2xl flex items-center gap-3">
          <SettingsIcon className="text-relief-600" /> Platform Settings
        </h2>
        <p className="text-sm text-gray-500 mt-1">Manage system preferences, notifications, and AI configurations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <Palette className="text-gray-400" />
            <h3 className="font-bold text-lg">Appearance</h3>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Dark Mode</p>
              <p className="text-xs text-gray-500">Toggle dark mode interface</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-relief-600"></div>
            </label>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <Bell className="text-gray-400" />
            <h3 className="font-bold text-lg">Notifications</h3>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Critical Alerts</p>
              <p className="text-xs text-gray-500">Push notifications for severe disasters</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-relief-600"></div>
            </label>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <Database className="text-gray-400" />
            <h3 className="font-bold text-lg">Database Sync</h3>
          </div>
          <p className="text-sm text-gray-500">Backend connection status: <span className="text-green-500 font-bold">Healthy (Connected)</span></p>
          <button className="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-sm font-bold rounded-lg w-full">Force Resync</button>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="text-gray-400" />
            <h3 className="font-bold text-lg">Security & Access</h3>
          </div>
          <p className="text-sm text-gray-500">Role: <span className="font-bold">Admin / Relief Coordinator</span></p>
          <button className="px-4 py-2 bg-red-50 text-red-600 dark:bg-red-900/20 text-sm font-bold rounded-lg w-full">Sign Out All Sessions</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
