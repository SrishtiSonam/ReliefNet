import { useNavigate } from 'react-router-dom';
import { Shield, Building2, Users } from 'lucide-react';

const Login = () => {
    const navigate = useNavigate();

    const roles = [
        {
            id: 'state',
            title: 'State Dashboard (SDMA)',
            description: 'State-level disaster management and resource coordination',
            icon: Shield,
            color: '#2563eb',
            path: '/state'
        },
        {
            id: 'district',
            title: 'District Dashboard (DDMA)',
            description: 'District-level operations and local response management',
            icon: Building2,
            color: '#10b981',
            path: '/district'
        },
        {
            id: 'public',
            title: 'Public Portal',
            description: 'Citizen services, relief requests, and safety information',
            icon: Users,
            color: '#f59e0b',
            path: '/public'
        }
    ];

    return (
        <div className="page" style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
        }}>
            <div className="container" style={{ maxWidth: '1200px' }}>
                <div className="text-center mb-3">
                    <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                        <span style={{ color: '#2563eb' }}>Relief</span>Net
                    </h1>
                    <p style={{ fontSize: '1.25rem', color: '#cbd5e1' }}>
                        Disaster Management Platform for India
                    </p>
                    <p className="text-muted">
                        Select your role to access the appropriate dashboard
                    </p>
                </div>

                <div className="grid grid-3 gap-3 mt-3">
                    {roles.map(role => {
                        const Icon = role.icon;
                        return (
                            <div
                                key={role.id}
                                className="card"
                                style={{
                                    cursor: 'pointer',
                                    textAlign: 'center',
                                    padding: '2rem',
                                    transition: 'all 0.3s ease',
                                    borderColor: 'transparent'
                                }}
                                onClick={() => navigate(role.path)}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.borderColor = role.color;
                                    e.currentTarget.style.transform = 'translateY(-8px)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.borderColor = 'transparent';
                                    e.currentTarget.style.transform = 'translateY(0)';
                                }}
                            >
                                <div style={{
                                    width: '80px',
                                    height: '80px',
                                    margin: '0 auto 1.5rem',
                                    borderRadius: '50%',
                                    background: `${role.color}20`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <Icon size={40} color={role.color} />
                                </div>
                                <h3 style={{ marginBottom: '0.75rem' }}>{role.title}</h3>
                                <p className="text-muted">{role.description}</p>
                                <button
                                    className="btn btn-primary mt-2"
                                    style={{ background: role.color }}
                                >
                                    Access Dashboard
                                </button>
                            </div>
                        );
                    })}
                </div>

                <div className="text-center mt-3">
                    <p className="text-muted" style={{ fontSize: '0.875rem' }}>
                        © 2024 ReliefNet - Disaster Management Platform
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
