import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Award } from 'lucide-react';

const TFTComparison = ({ data, loading }) => {
    if (loading) {
        return <div className="flex items-center justify-center h-64">Loading comparison...</div>;
    }

    if (!data || !data.comparison) {
        return <div className="text-gray-500">No comparison data available</div>;
    }

    const { tft, arima, improvement, winner } = data.comparison;

    // Format data for chart
    const chartData = tft.forecast.map((value, index) => ({
        day: `Day ${index + 1}`,
        TFT: value,
        ARIMA: arima.forecast[index]
    }));

    return (
        <div className="w-full">
            {/* Winner Badge */}
            <div className="mb-4 flex items-center justify-between">
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${winner === 'TFT' ? 'bg-green-100 border border-green-300' : 'bg-orange-100 border border-orange-300'
                    }`}>
                    <Award className={`w-5 h-5 ${winner === 'TFT' ? 'text-green-600' : 'text-orange-600'}`} />
                    <span className={`font-semibold ${winner === 'TFT' ? 'text-green-700' : 'text-orange-700'}`}>
                        Winner: {winner}
                    </span>
                </div>

                <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 border border-blue-300 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-700">
                        Improvement: {improvement}
                    </span>
                </div>
            </div>

            {/* Comparison Chart */}
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
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

                    <Line
                        type="monotone"
                        dataKey="TFT"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        name="TFT Forecast"
                    />

                    <Line
                        type="monotone"
                        dataKey="ARIMA"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ r: 3 }}
                        name="ARIMA/GARCH"
                    />
                </LineChart>
            </ResponsiveContainer>

            {/* Metrics Comparison */}
            <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2">TFT Model</h4>
                    <p className="text-xs text-blue-700">Variance: {tft.variance.toFixed(2)}</p>
                    <p className="text-xs text-blue-600 mt-1">Smoother, more accurate predictions</p>
                </div>

                <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                    <h4 className="text-sm font-semibold text-orange-900 mb-2">ARIMA/GARCH</h4>
                    <p className="text-xs text-orange-700">Variance: {arima.variance.toFixed(2)}</p>
                    <p className="text-xs text-orange-600 mt-1">Classical statistical approach</p>
                </div>
            </div>
        </div>
    );
};

export default TFTComparison;
