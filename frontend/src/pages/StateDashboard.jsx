import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, Truck, Package, AlertTriangle } from 'lucide-react';
import MapView from '../components/MapView';
import SurgeChart from '../components/SurgeChart';
import ExplainableAI from '../components/ExplainableAI';
import ResourceDashboard from '../components/ResourceDashboard';
import { getDashboard, getForecast, getExplanation, getDistrictsGeo, connectWebSocket } from '../services/api';

const StateDashboard = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [forecastData, setForecastData] = useState(null);
    const [explanationData, setExplanationData] = useState(null);
    const [districtsGeo, setDistrictsGeo] = useState([]);
    const [vehicles, setVehicles] = useState([]);

    useEffect(() => {
        loadData();

        // Connect to WebSocket for real-time vehicle updates
        const ws = connectWebSocket((data) => {
            if (data.type === 'vehicle_update') {
                setVehicles(data.vehicles);
            }
        });

        return () => {
            if (ws) ws.close();
        };
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            // Load dashboard data
            const dashResponse = await getDashboard('state_admin');
            setDashboardData(dashResponse.data);
            setVehicles(dashResponse.data.vehicles || []);

            // Load forecast for Mumbai
            const forecastResponse = await getForecast('Mumbai', 7);
            setForecastData(forecastResponse.data);

            // Load explanation
            const explanationResponse = await getExplanation('MH01');
            setExplanationData(explanationResponse.data);

            // Load district GeoJSON
            const geoResponse = await getDistrictsGeo();
            setDistrictsGeo(geoResponse.data.features || []);

            setLoading(false);
        } catch (error) {
            console.error('Error loading data:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="page">
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="page">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <button className="btn btn-secondary" onClick={() => navigate('/')}>
                        <ArrowLeft size={20} />
                        Back to Home
                    </button>
                    <h1 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>State Dashboard (SDMA)</h1>
                    <p className="text-muted">State-level disaster management and resource coordination</p>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="dashboard-stats">
                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{dashboardData?.districts?.length || 0}</div>
                            <div className="stat-label">Districts</div>
                        </div>
                        <Activity size={40} color="#2563eb" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{dashboardData?.active_missions || 0}</div>
                            <div className="stat-label">Active Missions</div>
                        </div>
                        <Truck size={40} color="#10b981" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{dashboardData?.total_requests || 0}</div>
                            <div className="stat-label">Relief Requests</div>
                        </div>
                        <Package size={40} color="#f59e0b" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{dashboardData?.total_roadblocks || 0}</div>
                            <div className="stat-label">Roadblocks</div>
                        </div>
                        <AlertTriangle size={40} color="#ef4444" />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-2 gap-3">
                {/* Map with Districts and Vehicles */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-header">Live State Map - Vehicle Tracking</div>
                    <div className="card-body">
                        <MapView
                            center={[20.5937, 78.9629]}
                            zoom={5}
                            districts={districtsGeo}
                            vehicles={vehicles}
                            className="map-full"
                        />
                    </div>
                </div>

                {/* Surge Forecast */}
                <div style={{ gridColumn: 'span 2' }}>
                    <SurgeChart data={forecastData} district="Mumbai" />
                </div>

                {/* Resource Dashboard */}
                <div style={{ gridColumn: 'span 2' }}>
                    <ResourceDashboard warehouses={dashboardData?.warehouses || []} />
                </div>

                {/* Explainable AI */}
                <div style={{ gridColumn: 'span 2' }}>
                    <ExplainableAI explanation={explanationData} />
                </div>
            </div>

            {/* Vehicle List */}
            <div className="card mt-3">
                <div className="card-header">Active Vehicles</div>
                <div className="card-body">
                    <div className="grid grid-4 gap-2">
                        {vehicles.map(vehicle => (
                            <div key={vehicle.id} className="card" style={{ padding: '1rem' }}>
                                <div className="flex justify-between items-center mb-2">
                                    <strong>{vehicle.name}</strong>
                                    <span className={`badge badge-${vehicle.status === 'in_transit' ? 'info' : vehicle.status === 'idle' ? 'success' : 'warning'}`}>
                                        {vehicle.status}
                                    </span>
                                </div>
                                <p className="text-muted" style={{ fontSize: '0.875rem', margin: 0 }}>
                                    Type: {vehicle.type.toUpperCase()}
                                </p>
                                <p className="text-muted" style={{ fontSize: '0.875rem', margin: 0 }}>
                                    Load: {vehicle.current_load}/{vehicle.capacity}
                                </p>
                                {vehicle.destination && (
                                    <p className="text-muted" style={{ fontSize: '0.875rem', margin: 0 }}>
                                        → {vehicle.destination}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StateDashboard;
