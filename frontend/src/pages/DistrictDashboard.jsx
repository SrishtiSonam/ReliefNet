import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, AlertCircle, Users, Package } from 'lucide-react';
import MapView from '../components/MapView';
import { getDashboard, getPublicRequests, getRoadblocks, createRoadblock } from '../services/api';

const DistrictDashboard = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [requests, setRequests] = useState([]);
    const [roadblocks, setRoadblocks] = useState([]);
    const [showRoadblockForm, setShowRoadblockForm] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            const dashResponse = await getDashboard('district_admin');
            setDashboardData(dashResponse.data);

            const requestsResponse = await getPublicRequests();
            setRequests(requestsResponse.data);

            const roadblocksResponse = await getRoadblocks();
            setRoadblocks(roadblocksResponse.data);

            setLoading(false);
        } catch (error) {
            console.error('Error loading data:', error);
            setLoading(false);
        }
    };

    const handleRoadblockSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            await createRoadblock({
                location: formData.get('location'),
                lat: parseFloat(formData.get('lat')),
                lng: parseFloat(formData.get('lng')),
                severity: formData.get('severity'),
                description: formData.get('description'),
                reported_by: 'District Admin'
            });

            setShowRoadblockForm(false);
            loadData();
        } catch (error) {
            console.error('Error reporting roadblock:', error);
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

    const district = dashboardData?.district;
    const warehouses = dashboardData?.warehouses || [];

    return (
        <div className="page">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <button className="btn btn-secondary" onClick={() => navigate('/')}>
                        <ArrowLeft size={20} />
                        Back to Home
                    </button>
                    <h1 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>
                        District Dashboard (DDMA) - {district?.name}
                    </h1>
                    <p className="text-muted">District-level operations and local response management</p>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="dashboard-stats">
                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{requests.length}</div>
                            <div className="stat-label">Public Requests</div>
                        </div>
                        <Users size={40} color="#2563eb" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{roadblocks.length}</div>
                            <div className="stat-label">Roadblocks</div>
                        </div>
                        <AlertCircle size={40} color="#ef4444" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{warehouses.length}</div>
                            <div className="stat-label">Warehouses</div>
                        </div>
                        <Package size={40} color="#10b981" />
                    </div>
                </div>

                <div className="stat-card">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="stat-value">{district?.population?.toLocaleString() || 0}</div>
                            <div className="stat-label">Population</div>
                        </div>
                        <MapPin size={40} color="#f59e0b" />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-2 gap-3">
                {/* District Map */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-header">District Map - Roadblocks & Warehouses</div>
                    <div className="card-body">
                        <MapView
                            center={district ? [district.lat, district.lng] : [20.5937, 78.9629]}
                            zoom={12}
                            markers={[
                                ...warehouses.map(w => ({
                                    lat: w.lat,
                                    lng: w.lng,
                                    name: w.name,
                                    description: 'Warehouse',
                                    details: w.stocks
                                })),
                                ...roadblocks.map(r => ({
                                    lat: r.lat,
                                    lng: r.lng,
                                    name: r.location,
                                    description: `Severity: ${r.severity}`,
                                    details: { Description: r.description }
                                }))
                            ]}
                            className="map-container"
                        />
                    </div>
                </div>

                {/* Public Requests */}
                <div className="card">
                    <div className="card-header">Public Relief Requests</div>
                    <div className="card-body">
                        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {requests.length === 0 ? (
                                <p className="text-muted">No requests at this time</p>
                            ) : (
                                requests.map(request => (
                                    <div key={request.id} className="card mb-2" style={{ padding: '1rem' }}>
                                        <div className="flex justify-between items-center mb-1">
                                            <strong>{request.name}</strong>
                                            <span className={`badge badge-${request.status === 'completed' ? 'success' :
                                                request.status === 'in_progress' ? 'info' :
                                                    request.status === 'approved' ? 'warning' : 'danger'
                                                }`}>
                                                {request.status}
                                            </span>
                                        </div>
                                        <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0' }}>
                                            Type: {request.request_type} | Urgency: {request.urgency}/5
                                        </p>
                                        <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0' }}>
                                            Location: {request.location}
                                        </p>
                                        <p style={{ fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>
                                            {request.description}
                                        </p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Roadblocks & Reporting */}
                <div className="card">
                    <div className="card-header">
                        Roadblocks & Affected Areas
                        <button
                            className="btn btn-primary btn-sm"
                            style={{ marginRight: '0px', padding: '0.5rem 1rem' }}
                            onClick={() => setShowRoadblockForm(!showRoadblockForm)}
                        >
                            Report Roadblock
                        </button>
                    </div>
                    <div className="card-body">
                        {showRoadblockForm && (
                            <form onSubmit={handleRoadblockSubmit} className="mb-3 card" style={{ padding: '1rem', background: 'var(--bg-tertiary)' }}>
                                <div className="form-group">
                                    <label className="form-label">Location</label>
                                    <input type="text" name="location" className="form-input" required />
                                </div>
                                <div className="grid grid-2 gap-2">
                                    <div className="form-group">
                                        <label className="form-label">Latitude</label>
                                        <input type="number" step="any" name="lat" className="form-input" defaultValue={district?.lat} required />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Longitude</label>
                                        <input type="number" step="any" name="lng" className="form-input" defaultValue={district?.lng} required />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Severity</label>
                                    <select name="severity" className="form-select" required>
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Description</label>
                                    <textarea name="description" className="form-textarea" required />
                                </div>
                                <div className="flex gap-2">
                                    <button type="submit" className="btn btn-primary">Submit</button>
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowRoadblockForm(false)}>
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}

                        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {roadblocks.map(roadblock => (
                                <div key={roadblock.id} className="card mb-2" style={{ padding: '1rem' }}>
                                    <div className="flex justify-between items-center mb-1">
                                        <strong>{roadblock.location}</strong>
                                        <span className={`badge badge-${roadblock.severity === 'high' ? 'danger' :
                                            roadblock.severity === 'medium' ? 'warning' : 'info'
                                            }`}>
                                            {roadblock.severity}
                                        </span>
                                    </div>
                                    <p style={{ fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>
                                        {roadblock.description}
                                    </p>
                                    <p className="text-muted" style={{ fontSize: '0.75rem', margin: '0.5rem 0 0 0' }}>
                                        Reported by: {roadblock.reported_by}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DistrictDashboard;
