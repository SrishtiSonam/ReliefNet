import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from "recharts";

const SurgeChart = ({ data, district }) => {

    if (!data || !data.predictions) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    const chartData = data.predictions.map(pred => ({
        day: `Day ${pred.day}`,
        date: pred.date,
        Food: pred.food_demand,
        Water: pred.water_demand,
        Medicine: pred.medicine_demand,
        Shelter: pred.shelter_demand
    }));

    return (
        <div className="card">
            <div className="card-header flex justify-between items-center">
                <span>Disaster Resource Surge Forecast - {district}</span>

                <span className="badge badge-info ml-2">
                    {(data.confidence * 100).toFixed(0)}% Confidence
                </span>
            </div>

            <div className="card-body">

                <ResponsiveContainer width="100%" height={320}>

                    <LineChart data={chartData}>

                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

                        <XAxis
                            dataKey="day"
                            stroke="#cbd5e1"
                            label={{
                                value: "Forecast Days",
                                position: "insideBottom",
                                offset: -5,
                                fill: "#cbd5e1"
                            }}
                        />

                        <YAxis
                            stroke="#cbd5e1"
                            label={{
                                value: "Resource Demand",
                                angle: -90,
                                position: "insideLeft",
                                fill: "#cbd5e1"
                            }}
                        />

                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#1e293b",
                                border: "1px solid #334155",
                                borderRadius: "8px",
                                color: "#f1f5f9"
                            }}
                            formatter={(value) => [`${value} units`]}
                        />

                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="Food"
                            stroke="#f59e0b"
                            strokeWidth={3}
                            dot={{ r: 4 }}
                            activeDot={{ r: 6 }}
                        />

                        <Line
                            type="monotone"
                            dataKey="Water"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            dot={{ r: 4 }}
                            activeDot={{ r: 6 }}
                        />

                        <Line
                            type="monotone"
                            dataKey="Medicine"
                            stroke="#ef4444"
                            strokeWidth={3}
                            dot={{ r: 4 }}
                            activeDot={{ r: 6 }}
                        />

                        <Line
                            type="monotone"
                            dataKey="Shelter"
                            stroke="#10b981"
                            strokeWidth={3}
                            dot={{ r: 4 }}
                            activeDot={{ r: 6 }}
                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>
        </div>
    );
};

export default SurgeChart;
