import { useState } from 'react';
import { Shield, Mail, Lock, User } from 'lucide-react';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');

    const handleLogin = () => {
        if (!email || !password || !role) {
            alert('Please fill all fields');
            return;
        }

        // Navigate based on selected role
        if (role === 'central') {
            window.location.href = '/state-dashboard';
        } else if (role === 'state') {
            window.location.href = '/district-dashboard';
        } else if (role === 'public') {
            window.location.href = '/public-portal';
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: '#f0f4f8' }}>
            {/* Header Tricolor */}
            <div style={{ background: 'linear-gradient(to right, #FF9933, #FFFFFF, #138808)', padding: '4px 0' }}></div>

            <div style={{ background: '#FFFFFF', borderBottom: '1px solid #e0e0e0', padding: '12px 0' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <img
                        src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"
                        alt="Government of India"
                        style={{ height: '60px' }}
                    />
                    <div>
                        <h1 style={{ fontSize: '22px', fontWeight: '700', color: '#1a1a1a', margin: '0', lineHeight: '1.2' }}>
                            ReliefNet
                        </h1>
                        <p style={{ fontSize: '13px', color: '#666', margin: '4px 0 0 0' }}>
                            राहत नेट | Disaster Management Platform
                        </p>
                        <p style={{ fontSize: '12px', color: '#888', margin: '2px 0 0 0' }}>
                            Ministry of Home Affairs, Government of India
                        </p>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ maxWidth: '1200px', margin: '40px auto', padding: '0 20px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 450px', gap: '40px', alignItems: 'start' }}>

                    {/* Left Side - Information */}
                    <div>
                        <div style={{ background: '#FFFFFF', border: '1px solid #ddd', borderRadius: '4px', padding: '30px', marginBottom: '20px' }}>
                            <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1a1a1a', marginBottom: '16px', borderLeft: '4px solid #FF9933', paddingLeft: '16px' }}>
                                National Disaster Management Portal
                            </h2>
                            <p style={{ fontSize: '14px', color: '#444', lineHeight: '1.7', marginBottom: '16px' }}>
                                The ReliefNet platform is a comprehensive disaster management system designed to facilitate
                                coordination between Central, State, and District authorities, as well as provide essential
                                services to citizens during emergencies.
                            </p>

                            <div style={{ marginTop: '24px' }}>
                                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1a1a1a', marginBottom: '12px' }}>
                                    Key Features:
                                </h3>
                                <ul style={{ fontSize: '14px', color: '#444', lineHeight: '1.8', paddingLeft: '20px' }}>
                                    <li>Disaster monitoring and alerts</li>
                                    <li>Resource allocation and tracking</li>
                                    <li>Relief camp management</li>
                                    <li>Citizen services and requests</li>
                                    <li>Inter-agency coordination</li>
                                </ul>
                            </div>
                        </div>

                        <div style={{ background: '#FFF8E1', border: '1px solid #FFD54F', borderRadius: '4px', padding: '16px' }}>
                            <p style={{ fontSize: '13px', color: '#5D4037', margin: 0, lineHeight: '1.6' }}>
                                <strong>Notice:</strong> This is a dummy of Government of India portal. Using for education purpose only.
                            </p>
                        </div>
                    </div>

                    {/* Right Side - Login Form */}
                    <div>
                        <div style={{ background: '#FFFFFF', border: '2px solid #1976D2', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ background: '#1976D2', padding: '20px', textAlign: 'center' }}>
                                <Shield size={40} color="white" style={{ marginBottom: '8px' }} />
                                <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'white', margin: '0' }}>
                                    Secure Login
                                </h2>
                                <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.9)', margin: '8px 0 0 0' }}>
                                    सुरक्षित लॉगिन | Access Your Dashboard
                                </p>
                            </div>

                            <div style={{ padding: '30px' }}>
                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>
                                        Email Address / ईमेल पता <span style={{ color: '#d32f2f' }}>*</span>
                                    </label>
                                    <div style={{ position: 'relative' }}>
                                        <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#666' }} />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="Enter your email"
                                            style={{
                                                width: '100%',
                                                padding: '10px 12px 10px 40px',
                                                border: '1px solid #ccc',
                                                borderRadius: '2px',
                                                fontSize: '14px',
                                                outline: 'none',
                                                transition: 'border-color 0.2s',
                                                boxSizing: 'border-box'
                                            }}
                                            onFocus={(e) => e.target.style.borderColor = '#1976D2'}
                                            onBlur={(e) => e.target.style.borderColor = '#ccc'}
                                        />
                                    </div>
                                </div>

                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>
                                        Password / पासवर्ड <span style={{ color: '#d32f2f' }}>*</span>
                                    </label>
                                    <div style={{ position: 'relative' }}>
                                        <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#666' }} />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Enter your password"
                                            style={{
                                                width: '100%',
                                                padding: '10px 12px 10px 40px',
                                                border: '1px solid #ccc',
                                                borderRadius: '2px',
                                                fontSize: '14px',
                                                outline: 'none',
                                                transition: 'border-color 0.2s',
                                                boxSizing: 'border-box'
                                            }}
                                            onFocus={(e) => e.target.style.borderColor = '#1976D2'}
                                            onBlur={(e) => e.target.style.borderColor = '#ccc'}
                                        />
                                    </div>
                                </div>

                                <div style={{ marginBottom: '24px' }}>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>
                                        User Role / उपयोगकर्ता भूमिका <span style={{ color: '#d32f2f' }}>*</span>
                                    </label>
                                    <div style={{ position: 'relative' }}>
                                        <User size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#666', pointerEvents: 'none', zIndex: 1 }} />
                                        <select
                                            value={role}
                                            onChange={(e) => setRole(e.target.value)}
                                            style={{
                                                width: '100%',
                                                padding: '10px 12px 10px 40px',
                                                border: '1px solid #ccc',
                                                borderRadius: '2px',
                                                fontSize: '14px',
                                                outline: 'none',
                                                transition: 'border-color 0.2s',
                                                appearance: 'none',
                                                background: 'white',
                                                cursor: 'pointer',
                                                boxSizing: 'border-box'
                                            }}
                                            onFocus={(e) => e.target.style.borderColor = '#1976D2'}
                                            onBlur={(e) => e.target.style.borderColor = '#ccc'}
                                        >
                                            <option value="">Select your role</option>
                                            <option value="central">Central Authority / केंद्रीय प्राधिकरण</option>
                                            <option value="state">State Authority / राज्य प्राधिकरण</option>
                                            <option value="public">Public User / नागरिक उपयोगकर्ता</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    onClick={handleLogin}
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        background: '#FF9933',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '2px',
                                        fontSize: '16px',
                                        fontWeight: '700',
                                        cursor: 'pointer',
                                        transition: 'background 0.2s',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.5px'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.background = '#f57c00'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = '#FF9933'}
                                >
                                    Login / लॉगिन करें
                                </button>

                                <div style={{ marginTop: '20px', padding: '12px', background: '#f5f5f5', borderRadius: '2px', fontSize: '12px', color: '#666', textAlign: 'center' }}>
                                    For technical support, contact: <strong>support@reliefnet.gov.in</strong>
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '12px', color: '#666' }}>
                            <p style={{ margin: '8px 0' }}>
                                Designed, Developed and Hosted by<br />
                                <strong> RG14 </strong>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div style={{ background: '#1a1a1a', color: '#ccc', padding: '20px 0', marginTop: '60px' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', textAlign: 'center', fontSize: '13px' }}>
                    <p style={{ margin: '0 0 8px 0' }}>
                        © 2025 | All Rights Reserved.
                    </p>
                    <p style={{ margin: '0', fontSize: '12px' }}>
                        Last Updated: December 11, 2025 | Version 2.0
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;