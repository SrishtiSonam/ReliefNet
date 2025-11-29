import React, { useState, useEffect } from 'react';
import { healthCheck } from '../services/api';

function Dashboard() {
    const [systemStatus, setSystemStatus] = useState({
        backend: 'checking',
        forecasting: 'unknown',
        routing: 'unknown',
        decision: 'unknown'
    });

    const [stats, setStats] = useState({
        activeCases: 12,
        resourcesDeployed: 45,
        districtsMonitored: 28,
        predictionsToday: 156
    });

    useEffect(() => {
        checkSystemHealth();
    }, []);

    const checkSystemHealth = async () => {
        try {
            const response = await healthCheck();
            setSystemStatus(prev => ({
                ...prev,
                backend: 'healthy',
                mongodb: response.data.mongodb === 'connected' ? 'healthy' : 'disconnected'
            }));
        } catch (error) {
            setSystemStatus(prev => ({ ...prev, backend: 'error' }));
        }
    };

    const StatCard = ({ title, value, icon, color }) => (
        <div className="card hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
                </div>
                <div className="text-4xl">{icon}</div>
            </div>
        </div>
    );

    const StatusIndicator = ({ service, status }) => {
        const statusColors = {
            healthy: 'bg-green-500',
            checking: 'bg-yellow-500',
            unknown: 'bg-gray-400',
            error: 'bg-red-500',
            disconnected: 'bg-red-500'
        };

        return (
            <div className="flex items-center justify-between py-2">
                <span className="text-sm font-medium text-gray-700">{service}</span>
                <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full ${statusColors[status]} mr-2`}></div>
                    <span className="text-sm text-gray-600 capitalize">{status}</span>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
                <button
                    onClick={checkSystemHealth}
                    className="btn btn-primary"
                >
                    🔄 Refresh Status
                </button>
            </div>

            {/* System Status */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
                <div className="space-y-2">
                    <StatusIndicator service="Backend Express" status={systemStatus.backend} />
                    <StatusIndicator service="MongoDB" status={systemStatus.mongodb || 'unknown'} />
                    <StatusIndicator service="Forecasting Service" status={systemStatus.forecasting} />
                    <StatusIndicator service="Routing Service" status={systemStatus.routing} />
                    <StatusIndicator service="Decision Service" status={systemStatus.decision} />
                </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Active Cases"
                    value={stats.activeCases}
                    icon="🚨"
                    color="text-danger-600"
                />
                <StatCard
                    title="Resources Deployed"
                    value={stats.resourcesDeployed}
                    icon="🚑"
                    color="text-primary-600"
                />
                <StatCard
                    title="Districts Monitored"
                    value={stats.districtsMonitored}
                    icon="📍"
                    color="text-green-600"
                />
                <StatCard
                    title="Predictions Today"
                    value={stats.predictionsToday}
                    icon="📊"
                    color="text-purple-600"
                />
            </div>

            {/* Quick Actions */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button className="btn btn-primary w-full">
                        🌪️ New Prediction
                    </button>
                    <button className="btn btn-primary w-full">
                        🗺️ View Resource Map
                    </button>
                    <button className="btn btn-danger w-full">
                        🚨 Emergency Dispatch
                    </button>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-gray-200 pb-2">
                        <div>
                            <p className="text-sm font-medium text-gray-900">Flood prediction - Mumbai</p>
                            <p className="text-xs text-gray-500">2 minutes ago</p>
                        </div>
                        <span className="px-2 py-1 text-xs font-medium bg-danger-100 text-danger-800 rounded">High</span>
                    </div>
                    <div className="flex items-center justify-between border-b border-gray-200 pb-2">
                        <div>
                            <p className="text-sm font-medium text-gray-900">Resource dispatch - Delhi</p>
                            <p className="text-xs text-gray-500">15 minutes ago</p>
                        </div>
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Completed</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-900">Route optimization - Bangalore to Chennai</p>
                            <p className="text-xs text-gray-500">1 hour ago</p>
                        </div>
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">In Progress</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
