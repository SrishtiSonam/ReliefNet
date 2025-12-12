import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const TFTForecastChart = ({ data, loading }) => {
    if (loading) {
        return <div className="flex items-center justify-center h-64">Loading forecast...</div>;
    }

    if (!data || !data.predictions) {
        return <div className="text-gray-500">No forecast data available</div>;
    }

    // Format data for Recharts
    const chartData = data.predictions.map((value, index) => ({
        day: `Day ${index + 1}`,
        prediction: value,
        lower: data.quantiles?.q10?.[index] || value * 0.85,
        upper: data.quantiles?.q90?.[index] || value * 1.15,
    }));

    return (
        <div className="w-full">
            <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        dataKey="day"
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                    />
                    <YAxis
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                        label={{ value: 'Demand (kg)', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#fff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '12px'
                        }}
                        formatter={(value) => [`${Math.round(value)} kg`, '']}
                    />
                    <Legend />

                    {/* Upper bound */}
                    <Area
                        type="monotone"
                        dataKey="upper"
                        stroke="none"
                        fill="#93c5fd"
                        fillOpacity={0.3}
                        name="90th Percentile"
                    />

                    {/* Main prediction */}
                    <Area
                        type="monotone"
                        dataKey="prediction"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        fill="#3b82f6"
                        fillOpacity={0.1}
                        name="Prediction"
                    />

                    {/* Lower bound */}
                    <Area
                        type="monotone"
                        dataKey="lower"
                        stroke="none"
                        fill="#93c5fd"
                        fillOpacity={0.3}
                        name="10th Percentile"
                    />
                </AreaChart>
            </ResponsiveContainer>

            <div className="mt-4 text-sm text-gray-600 text-center">
                <p>Shaded area shows uncertainty range (10th-90th percentile)</p>
            </div>
        </div>
    );
};

export default TFTForecastChart;
