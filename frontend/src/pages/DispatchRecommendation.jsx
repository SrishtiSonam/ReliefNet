import React, { useState } from 'react';
import { decisionAPI } from '../services/api';

function DispatchRecommendation() {
    const [formData, setFormData] = useState({
        severity: '',
        weather: '',
        traffic: '',
        distance: '',
        hospital_capacity: '',
        ambulance_availability: '',
        drone_availability: '',
        truck_availability: '',
        time_of_day: ''
    });

    const [recommendation, setRecommendation] = useState(null);
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
        setRecommendation(null);

        try {
            const requestData = {
                severity: formData.severity,
                weather: formData.weather,
                traffic: formData.traffic,
                distance: parseFloat(formData.distance),
                hospital_capacity: parseInt(formData.hospital_capacity),
                ambulance_availability: parseInt(formData.ambulance_availability),
                drone_availability: parseInt(formData.drone_availability),
                truck_availability: parseInt(formData.truck_availability) || 0,
                time_of_day: formData.time_of_day || undefined
            };

            const response = await decisionAPI.getRecommendation(requestData);
            setRecommendation(response.data);
        } catch (err) {
            setError(err.response?.data?.message || err.message || 'Failed to get recommendation');
        } finally {
            setLoading(false);
        }
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Dispatch Decision Recommendation</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Situation Parameters</h3>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Severity *</label>
                                <select
                                    name="severity"
                                    value={formData.severity}
                                    onChange={handleChange}
                                    className="input"
                                    required
                                >
                                    <option value="">Select severity</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                            </div>

                            <div>
                                <label className="label">Weather *</label>
                                <select
                                    name="weather"
                                    value={formData.weather}
                                    onChange={handleChange}
                                    className="input"
                                    required
                                >
                                    <option value="">Select weather</option>
                                    <option value="clear">Clear</option>
                                    <option value="rain">Rain</option>
                                    <option value="storm">Storm</option>
                                    <option value="fog">Fog</option>
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Traffic *</label>
                                <select
                                    name="traffic"
                                    value={formData.traffic}
                                    onChange={handleChange}
                                    className="input"
                                    required
                                >
                                    <option value="">Select traffic</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>

                            <div>
                                <label className="label">Distance (km) *</label>
                                <input
                                    type="number"
                                    name="distance"
                                    value={formData.distance}
                                    onChange={handleChange}
                                    className="input"
                                    step="0.1"
                                    min="0"
                                    placeholder="Distance to site"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="label">Hospital Capacity (%) *</label>
                            <input
                                type="number"
                                name="hospital_capacity"
                                value={formData.hospital_capacity}
                                onChange={handleChange}
                                className="input"
                                min="0"
                                max="100"
                                placeholder="0-100"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label className="label">Ambulances *</label>
                                <input
                                    type="number"
                                    name="ambulance_availability"
                                    value={formData.ambulance_availability}
                                    onChange={handleChange}
                                    className="input"
                                    min="0"
                                    placeholder="Available"
                                    required
                                />
                            </div>

                            <div>
                                <label className="label">Drones *</label>
                                <input
                                    type="number"
                                    name="drone_availability"
                                    value={formData.drone_availability}
                                    onChange={handleChange}
                                    className="input"
                                    min="0"
                                    placeholder="Available"
                                    required
                                />
                            </div>

                            <div>
                                <label className="label">Trucks</label>
                                <input
                                    type="number"
                                    name="truck_availability"
                                    value={formData.truck_availability}
                                    onChange={handleChange}
                                    className="input"
                                    min="0"
                                    placeholder="Available"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="label">Time of Day</label>
                            <select
                                name="time_of_day"
                                value={formData.time_of_day}
                                onChange={handleChange}
                                className="input"
                            >
                                <option value="">Select time</option>
                                <option value="morning">Morning</option>
                                <option value="afternoon">Afternoon</option>
                                <option value="evening">Evening</option>
                                <option value="night">Night</option>
                            </select>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary w-full"
                        >
                            {loading ? '🔄 Analyzing...' : '🚑 Get Recommendation'}
                        </button>
                    </form>
                </div>

                {/* Results */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Decision Recommendation</h3>

                    {error && (
                        <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded mb-4">
                            <p className="font-medium">Error</p>
                            <p className="text-sm">{error}</p>
                        </div>
                    )}

                    {recommendation ? (
                        <div className="space-y-4">
                            {/* Main Decision */}
                            <div className="bg-primary-50 border-2 border-primary-300 rounded-lg p-4">
                                <p className="text-sm font-medium text-primary-900 mb-2">Recommended Action:</p>
                                <p className="text-lg font-bold text-primary-900">{recommendation.decision}</p>
                            </div>

                            {/* Confidence Score */}
                            <div className="border border-gray-200 rounded-lg p-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-gray-700">Confidence Score:</span>
                                    <span className={`text-2xl font-bold ${getConfidenceColor(recommendation.confidence)}`}>
                                        {(recommendation.confidence * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div className="mt-2 bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                                        style={{ width: `${recommendation.confidence * 100}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Explanation */}
                            <div className="border border-gray-200 rounded-lg p-4">
                                <p className="text-sm font-medium text-gray-700 mb-2">Explanation:</p>
                                <p className="text-gray-900">{recommendation.explanation}</p>
                            </div>

                            {/* Alternative Options */}
                            {recommendation.alternative_options && recommendation.alternative_options.length > 0 && (
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <p className="text-sm font-medium text-gray-700 mb-2">Alternative Options:</p>
                                    <ul className="space-y-1">
                                        {recommendation.alternative_options.map((option, index) => (
                                            <li key={index} className="text-sm text-gray-700 flex items-start">
                                                <span className="mr-2">•</span>
                                                <span>{option}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Model Info */}
                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                                <p className="text-xs text-gray-600">
                                    <strong>Model Version:</strong> {recommendation.model_version}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p className="text-4xl mb-2">🚑</p>
                            <p>Submit the form to get dispatch recommendation</p>
                            <p className="text-sm mt-2">The system will analyze the situation and suggest optimal resource deployment</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default DispatchRecommendation;
