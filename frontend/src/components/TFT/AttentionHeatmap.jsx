import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const AttentionHeatmap = ({ data, loading }) => {
    if (loading) {
        return <div className="flex items-center justify-center h-64">Loading attention data...</div>;
    }

    if (!data || !data.variable_attention) {
        return <div className="text-gray-500">No attention data available</div>;
    }

    // Convert attention object to array for chart
    const chartData = Object.entries(data.variable_attention)
        .map(([feature, importance]) => ({
            feature: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            importance: importance,
            percentage: (importance * 100).toFixed(1)
        }))
        .sort((a, b) => b.importance - a.importance);

    // Color scale based on importance
    const getColor = (importance) => {
        if (importance > 0.25) return '#10b981'; // Green - high importance
        if (importance > 0.15) return '#f59e0b'; // Orange - medium importance
        return '#6b7280'; // Gray - low importance
    };

    return (
        <div className="w-full">
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 100 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        type="number"
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                        label={{ value: 'Importance Score', position: 'insideBottom', offset: -5, style: { fill: '#6b7280' } }}
                    />
                    <YAxis
                        type="category"
                        dataKey="feature"
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                        width={90}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#fff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '12px'
                        }}
                        formatter={(value, name, props) => [
                            `${props.payload.percentage}%`,
                            'Importance'
                        ]}
                    />
                    <Bar dataKey="importance" radius={[0, 8, 8, 0]}>
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getColor(entry.importance)} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>

            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-green-500"></div>
                    <span className="text-gray-700">High Importance (&gt;25%)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-orange-500"></div>
                    <span className="text-gray-700">Medium (15-25%)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-gray-500"></div>
                    <span className="text-gray-700">Low (&lt;15%)</span>
                </div>
            </div>
        </div>
    );
};

export default AttentionHeatmap;
