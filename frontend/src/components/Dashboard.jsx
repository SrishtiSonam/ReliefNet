import React, { useEffect, useState } from 'react';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalDemand: 1250,
        fulfilled: 980,
        pending: 270,
        activeTrucks: 12,
        activeUAVs: 8
    });

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-blue-500">
                <h3 className="text-gray-400 text-sm">Total Demand</h3>
                <p className="text-3xl font-bold">{stats.totalDemand} units</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-green-500">
                <h3 className="text-gray-400 text-sm">Fulfilled</h3>
                <p className="text-3xl font-bold">{stats.fulfilled} units</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-red-500">
                <h3 className="text-gray-400 text-sm">Pending</h3>
                <p className="text-3xl font-bold">{stats.pending} units</p>
            </div>

            <div className="col-span-3 bg-gray-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Resource Allocation Status</h2>
                <div className="w-full bg-gray-700 h-4 rounded-full overflow-hidden">
                    <div className="bg-blue-500 h-full" style={{ width: '78%' }}></div>
                </div>
                <p className="mt-2 text-sm text-gray-400">78% of demand met</p>
            </div>
        </div>
    );
};

export default Dashboard;
