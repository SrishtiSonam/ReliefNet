import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const ExplainableAI = ({ explanation }) => {
    if (!explanation) {
        return <div className="loading"><div className="spinner"></div></div>;
    }

    const chartData = explanation.features.map(feature => ({
        name: feature.name,
        impact: Math.abs(feature.impact),
        rawImpact: feature.impact,
        value: feature.value,
        description: feature.description
    }));

    const getColor = (impact) => {
        return impact >= 0 ? '#22c55e' : '#ef4444';
    };

    return (
        <div className="card">
            <div className="card-header">
                Explainable AI - Allocation Decision
                <span className="badge badge-success ml-2">
                    {(explanation.confidence * 100).toFixed(0)}% Confidence
                </span>
            </div>
            <div className="card-body">
                <div className="mb-3">
                    <h4 className="text-primary">{explanation.decision}</h4>
                    <p className="text-secondary">{explanation.rationale}</p>
                </div>

                <h5 className="mb-2">Feature Importance (SHAP-style)</h5>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis type="number" stroke="#cbd5e1" />
                        <YAxis dataKey="name" type="category" width={150} stroke="#cbd5e1" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '8px',
                                color: '#f1f5f9'
                            }}
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const data = payload[0].payload;
                                    return (
                                        <div style={{
                                            backgroundColor: '#1e293b',
                                            border: '1px solid #334155',
                                            borderRadius: '8px',
                                            padding: '12px',
                                            color: '#f1f5f9'
                                        }}>
                                            <p><strong>{data.name}</strong></p>
                                            <p>Impact: {data.rawImpact.toFixed(3)}</p>
                                            <p>Value: {data.value.toFixed(2)}</p>
                                            <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>{data.description}</p>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <Bar dataKey="impact">
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={getColor(entry.rawImpact)} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>

                <div className="mt-3">
                    <h6>Feature Details:</h6>
                    <div className="grid grid-2 gap-2 mt-2">
                        {explanation.features.map((feature, idx) => (
                            <div key={idx} className="card" style={{ padding: '0.75rem' }}>
                                <div className="flex justify-between items-center mb-1">
                                    <strong>{feature.name}</strong>
                                    <span className={`badge ${feature.impact >= 0 ? 'badge-success' : 'badge-danger'}`}>
                                        {feature.impact >= 0 ? '+' : ''}{feature.impact.toFixed(3)}
                                    </span>
                                </div>
                                <p style={{ fontSize: '0.875rem', margin: 0 }} className="text-muted">
                                    {feature.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExplainableAI;
