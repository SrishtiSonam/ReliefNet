import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Shield, AlertTriangle, Phone } from 'lucide-react';
import MapView from '../components/MapView';
import PublicRequestForm from '../components/PublicRequestForm';
import RequestStatusTracker from '../components/RequestStatusTracker';
import { getDashboard, createPublicRequest } from '../services/api';

const PublicPortal = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [requestStatus, setRequestStatus] = useState('pending');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const response = await getDashboard('public');
            setDashboardData(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error loading data:', error);
            setLoading(false);
        }
    };

    const handleRequestSubmit = async (formData) => {
        try {
            await createPublicRequest(formData);
            setRequestStatus('pending');
            // Simulate status progression for demo
            setTimeout(() => setRequestStatus('approved'), 3000);
            setTimeout(() => setRequestStatus('in_progress'), 6000);
        } catch (error) {
            console.error('Error submitting request:', error);
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

    const shelters = dashboardData?.shelters || [];
    const alerts = dashboardData?.active_alerts || [];
    const guidelines = dashboardData?.safety_guidelines || [];

    return (
        <div className="page">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <button className="btn btn-secondary" onClick={() => navigate('/')}>
                        <ArrowLeft size={20} />
                        Back to Home
                    </button>
                    <h1 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Public Portal</h1>
                    <p className="text-muted">Citizen services, relief requests, and safety information</p>
                </div>
            </div>

            {/* Active Alerts */}
            {alerts.length > 0 && (
                <div className="card mb-3" style={{ borderColor: '#ef4444', borderWidth: '2px' }}>
                    <div className="card-header" style={{ color: '#ef4444' }}>
                        <AlertTriangle size={24} style={{ display: 'inline', marginRight: '0.5rem' }} />
                        Active Alerts
                    </div>
                    <div className="card-body">
                        {alerts.map((alert, idx) => (
                            <div key={idx} className={`badge badge-${alert.severity === 'high' ? 'danger' : 'warning'} mb-2`}
                                style={{ display: 'block', padding: '1rem', fontSize: '1rem' }}>
                                <strong>{alert.type.toUpperCase()}:</strong> {alert.message}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="grid grid-2 gap-3">
                {/* Shelter Map */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-header">
                        <MapPin size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                        Nearby Shelters & Safety Zones
                    </div>
                    <div className="card-body">
                        <MapView
                            center={[20.5937, 78.9629]}
                            zoom={6}
                            markers={shelters.map(shelter => ({
                                lat: shelter.lat,
                                lng: shelter.lng,
                                name: shelter.name,
                                description: `Capacity: ${shelter.current_occupancy}/${shelter.capacity}`,
                                details: {
                                    District: shelter.district,
                                    Facilities: shelter.facilities.join(', ')
                                }
                            }))}
                            className="map-container"
                        />
                    </div>
                </div>

                {/* Request Form */}
                <div>
                    <PublicRequestForm onSubmit={handleRequestSubmit} />
                </div>

                {/* Status Tracker */}
                <div>
                    <RequestStatusTracker status={requestStatus} />
                </div>

                {/* Safety Guidelines */}
                <div className="card">
                    <div className="card-header">
                        <Shield size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                        Safety Guidelines
                    </div>
                    <div className="card-body">
                        <ul style={{ paddingLeft: '1.5rem', margin: 0 }}>
                            {guidelines.map((guideline, idx) => (
                                <li key={idx} style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
                                    {guideline}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Emergency Contacts */}
                <div className="card">
                    <div className="card-header">
                        <Phone size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                        Emergency Contacts
                    </div>
                    <div className="card-body">
                        <div className="grid grid-2 gap-2">
                            <div className="card" style={{ padding: '1rem', background: 'var(--bg-tertiary)' }}>
                                <strong style={{ color: 'var(--danger)' }}>Emergency Services</strong>
                                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--primary)' }}>
                                    112
                                </p>
                            </div>
                            <div className="card" style={{ padding: '1rem', background: 'var(--bg-tertiary)' }}>
                                <strong>Disaster Helpline</strong>
                                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--primary)' }}>
                                    1078
                                </p>
                            </div>
                            <div className="card" style={{ padding: '1rem', background: 'var(--bg-tertiary)' }}>
                                <strong>Police</strong>
                                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--primary)' }}>
                                    100
                                </p>
                            </div>
                            <div className="card" style={{ padding: '1rem', background: 'var(--bg-tertiary)' }}>
                                <strong>Ambulance</strong>
                                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.5rem 0', color: 'var(--primary)' }}>
                                    102
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Shelter Information */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-header">Available Shelters</div>
                    <div className="card-body">
                        <div className="grid grid-3 gap-2">
                            {shelters.slice(0, 6).map((shelter, idx) => (
                                <div key={idx} className="card" style={{ padding: '1rem' }}>
                                    <h4 style={{ marginBottom: '0.5rem' }}>{shelter.name}</h4>
                                    <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0' }}>
                                        District: {shelter.district}
                                    </p>
                                    <div className="flex justify-between items-center mt-2">
                                        <span style={{ fontSize: '0.875rem' }}>Occupancy:</span>
                                        <span className={`badge ${shelter.current_occupancy / shelter.capacity > 0.8 ? 'badge-danger' : 'badge-success'}`}>
                                            {shelter.current_occupancy}/{shelter.capacity}
                                        </span>
                                    </div>
                                    <p className="text-muted" style={{ fontSize: '0.75rem', margin: '0.5rem 0 0 0' }}>
                                        Facilities: {shelter.facilities.join(', ')}
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

export default PublicPortal;
