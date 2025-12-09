import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ResourceDashboard = ({ warehouses }) => {
    if (!warehouses || warehouses.length === 0) {
        return <div className="loading"><div className="spinner"></div></div>;
    }

    // Aggregate stock data
    const stockData = warehouses.reduce((acc, warehouse) => {
        Object.entries(warehouse.stocks).forEach(([resource, quantity]) => {
            if (!acc[resource]) {
                acc[resource] = { resource: resource.replace(/_/g, ' ').toUpperCase(), total: 0 };
            }
            acc[resource].total += quantity;
        });
        return acc;
    }, {});

    const chartData = Object.values(stockData);

    return (
        <div className="card">
            <div className="card-header">Resource Allocation Dashboard</div>
            <div className="card-body">
                <div className="dashboard-stats mb-3">
                    {chartData.map((item, idx) => (
                        <div key={idx} className="stat-card">
                            <div className="stat-value">{item.total.toLocaleString()}</div>
                            <div className="stat-label">{item.resource}</div>
                        </div>
                    ))}
                </div>

                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="resource" stroke="#cbd5e1" />
                        <YAxis stroke="#cbd5e1" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '8px',
                                color: '#f1f5f9'
                            }}
                        />
                        <Legend />
                        <Bar dataKey="total" fill="#2563eb" />
                    </BarChart>
                </ResponsiveContainer>

                <div className="mt-3">
                    <h5>Warehouse Details</h5>
                    <div className="grid grid-2 gap-2 mt-2">
                        {warehouses.map((warehouse, idx) => (
                            <div key={idx} className="card" style={{ padding: '0.75rem' }}>
                                <h6>{warehouse.name}</h6>
                                <p className="text-muted" style={{ fontSize: '0.875rem' }}>
                                    District: {warehouse.district}
                                </p>
                                <div style={{ fontSize: '0.875rem' }}>
                                    {Object.entries(warehouse.stocks).map(([resource, qty]) => (
                                        <div key={resource} className="flex justify-between mt-1">
                                            <span>{resource.replace(/_/g, ' ')}:</span>
                                            <strong>{qty.toLocaleString()}</strong>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResourceDashboard;
