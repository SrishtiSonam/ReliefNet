import { useState } from 'react';
import { Droplet, Package, Home, Heart, AlertTriangle } from 'lucide-react';

const PublicRequestForm = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        location: '',
        lat: 19.0760,
        lng: 72.8777,
        request_type: 'food',
        description: '',
        urgency: 3
    });

    const [submitted, setSubmitted] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'urgency' ? parseInt(value) : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (onSubmit) {
            await onSubmit(formData);
            setSubmitted(true);
            setTimeout(() => setSubmitted(false), 3000);
            setFormData({
                name: '',
                phone: '',
                location: '',
                lat: 19.0760,
                lng: 72.8777,
                request_type: 'food',
                description: '',
                urgency: 3
            });
        }
    };

    const requestTypes = [
        { value: 'food', label: 'Food', icon: Package, color: '#f59e0b' },
        { value: 'water', label: 'Water', icon: Droplet, color: '#3b82f6' },
        { value: 'shelter', label: 'Shelter', icon: Home, color: '#10b981' },
        { value: 'medicine', label: 'Medicine', icon: Heart, color: '#ef4444' },
        { value: 'rescue', label: 'Rescue', icon: AlertTriangle, color: '#dc2626' }
    ];

    return (
        <div className="card">
            <div className="card-header">Request Relief Assistance</div>
            <div className="card-body">
                {submitted && (
                    <div className="badge badge-success mb-3" style={{ display: 'block', padding: '1rem' }}>
                        Request submitted successfully! Our team will contact you soon.
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Name *</label>
                        <input
                            type="text"
                            name="name"
                            className="form-input"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Phone Number *</label>
                        <input
                            type="tel"
                            name="phone"
                            className="form-input"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="+91-XXXXXXXXXX"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Location *</label>
                        <input
                            type="text"
                            name="location"
                            className="form-input"
                            value={formData.location}
                            onChange={handleChange}
                            placeholder="Enter your location"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Type of Assistance Needed *</label>
                        <div className="grid grid-3 gap-2">
                            {requestTypes.map(type => {
                                const Icon = type.icon;
                                return (
                                    <div
                                        key={type.value}
                                        className={`card ${formData.request_type === type.value ? 'border-primary' : ''}`}
                                        style={{
                                            padding: '1rem',
                                            cursor: 'pointer',
                                            borderWidth: '2px',
                                            borderColor: formData.request_type === type.value ? type.color : 'transparent'
                                        }}
                                        onClick={() => setFormData(prev => ({ ...prev, request_type: type.value }))}
                                    >
                                        <div className="flex flex-col items-center gap-1">
                                            <Icon size={32} color={type.color} />
                                            <span>{type.label}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Description *</label>
                        <textarea
                            name="description"
                            className="form-textarea"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Please describe your situation and what you need"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Urgency Level: {formData.urgency}/5</label>
                        <input
                            type="range"
                            name="urgency"
                            min="1"
                            max="5"
                            value={formData.urgency}
                            onChange={handleChange}
                            className="form-input"
                            style={{ padding: '0.5rem' }}
                        />
                        <div className="flex justify-between text-muted" style={{ fontSize: '0.875rem' }}>
                            <span>Low</span>
                            <span>Medium</span>
                            <span>High</span>
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                        Submit Request
                    </button>
                </form>
            </div>
        </div>
    );
};

export default PublicRequestForm;
