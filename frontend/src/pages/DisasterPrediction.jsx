import React, { useState } from 'react';
import { forecastAPI } from '../services/api';

function DisasterPrediction() {
    const [formData, setFormData] = useState({
        district: '',
        disaster_type: '',
        month: '',
        season: '',
        population: '',
        rainfall_mm: ''
    });

    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setPrediction(null);

        try {
            const requestData = {
                district: formData.district,
                disaster_type: formData.disaster_type,
                date_features: {
                    month: parseInt(formData.month) || 1,
                    season: formData.season
                },
                other_features: {
                    population: parseInt(formData.population) || 0,
                    rainfall_mm: parseFloat(formData.rainfall_mm) || 0
                }
            };

            const response = await forecastAPI.getDemandForecast(requestData);
            setPrediction(response.data);
        } catch (err) {
            setError(err.response?.data?.message || err.message || 'Failed to get prediction');
        } finally {
            setLoading(false);
        }
    };

    const getSeverityColor = (severity) => {
        const colors = {
            low: 'bg-green-100 text-green-800 border-green-300',
            medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
            high: 'bg-orange-100 text-orange-800 border-orange-300',
            critical: 'bg-red-100 text-red-800 border-red-300'
        };
        return colors[severity?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-300';
    };

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Disaster Demand Prediction</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Input Parameters</h3>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="label">District</label>
                            <input
                                type="text"
                                name="district"
                                value={formData.district}
                                onChange={handleChange}
                                className="input"
                                placeholder="e.g., Mumbai, Delhi, Bangalore"
                                required
                            />
                        </div>

                        <div>
                            <label className="label">Disaster Type</label>
                            <select
                                name="disaster_type"
                                value={formData.disaster_type}
                                onChange={handleChange}
                                className="input"
                                required
                            >
                                <option value="">Select disaster type</option>
                                <option value="flood">Flood</option>
                                <option value="earthquake">Earthquake</option>
                                <option value="cyclone">Cyclone</option>
                                <option value="drought">Drought</option>
                                <option value="landslide">Landslide</option>
                                <option value="fire">Fire</option>
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Month</label>
                                <input
                                    type="number"
                                    name="month"
                                    value={formData.month}
                                    onChange={handleChange}
                                    className="input"
                                    min="1"
                                    max="12"
                                    placeholder="1-12"
                                />
                            </div>

                            <div>
                                <label className="label">Season</label>
                                <select
                                    name="season"
                                    value={formData.season}
                                    onChange={handleChange}
                                    className="input"
                                >
                                    <option value="">Select season</option>
                                    <option value="winter">Winter</option>
                                    <option value="summer">Summer</option>
                                    <option value="monsoon">Monsoon</option>
                                    <option value="autumn">Autumn</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="label">Population</label>
                            <input
                                type="number"
                                name="population"
                                value={formData.population}
                                onChange={handleChange}
                                className="input"
                                placeholder="District population"
                            />
                        </div>

                        <div>
                            <label className="label">Rainfall (mm)</label>
                            <input
                                type="number"
                                name="rainfall_mm"
                                value={formData.rainfall_mm}
                                onChange={handleChange}
                                className="input"
                                step="0.1"
                                placeholder="Expected rainfall in mm"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary w-full"
                        >
                            {loading ? '🔄 Predicting...' : '🔮 Get Prediction'}
                        </button>
                    </form>
                </div>

                {/* Results */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Results</h3>

                    {error && (
                        <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded mb-4">
                            <p className="font-medium">Error</p>
                            <p className="text-sm">{error}</p>
                        </div>
                    )}

                    {prediction ? (
                        <div className="space-y-4">
                            <div className={`border-2 rounded-lg p-4 ${getSeverityColor(prediction.severity)}`}>
                                <p className="text-sm font-medium">Severity Level</p>
                                <p className="text-2xl font-bold uppercase mt-1">{prediction.severity}</p>
                            </div>

                            <div className="border border-gray-200 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3">Predicted Resource Demand</h4>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-700">🍱 Food Packets:</span>
                                        <span className="font-bold text-lg">{prediction.predicted_demand.food.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-700">💧 Water Bottles:</span>
                                        <span className="font-bold text-lg">{prediction.predicted_demand.water.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-700">🏥 Medical Kits:</span>
                                        <span className="font-bold text-lg">{prediction.predicted_demand.medical.toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <p className="text-sm text-blue-800">
                                    <strong>Model Version:</strong> {prediction.model_version}
                                </p>
                                {prediction.confidence && (
                                    <p className="text-sm text-blue-800 mt-1">
                                        <strong>Confidence:</strong> {(prediction.confidence * 100).toFixed(1)}%
                                    </p>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p className="text-4xl mb-2">🔮</p>
                            <p>Submit the form to get disaster demand prediction</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default DisasterPrediction;
