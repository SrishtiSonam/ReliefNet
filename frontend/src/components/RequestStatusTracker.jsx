import { CheckCircle, Clock, AlertCircle, XCircle } from 'lucide-react';

const RequestStatusTracker = ({ status = 'pending' }) => {
    const stages = [
        { key: 'pending', label: 'Submitted', icon: Clock, color: '#f59e0b' },
        { key: 'approved', label: 'Approved', icon: CheckCircle, color: '#3b82f6' },
        { key: 'in_progress', label: 'In Progress', icon: AlertCircle, color: '#10b981' },
        { key: 'completed', label: 'Completed', icon: CheckCircle, color: '#22c55e' }
    ];

    const currentStageIndex = stages.findIndex(s => s.key === status);

    return (
        <div className="card">
            <div className="card-header">Request Status</div>
            <div className="card-body">
                <div style={{ position: 'relative', padding: '2rem 0' }}>
                    {/* Progress Line */}
                    <div style={{
                        position: 'absolute',
                        top: '2.5rem',
                        left: '10%',
                        right: '10%',
                        height: '4px',
                        background: '#334155',
                        zIndex: 0
                    }}>
                        <div style={{
                            height: '100%',
                            background: 'linear-gradient(90deg, #3b82f6, #10b981)',
                            width: `${(currentStageIndex / (stages.length - 1)) * 100}%`,
                            transition: 'width 0.5s ease'
                        }} />
                    </div>

                    {/* Stages */}
                    <div className="flex justify-between" style={{ position: 'relative', zIndex: 1 }}>
                        {stages.map((stage, idx) => {
                            const Icon = stage.icon;
                            const isActive = idx <= currentStageIndex;
                            const isCurrent = idx === currentStageIndex;

                            return (
                                <div key={stage.key} className="flex flex-col items-center" style={{ flex: 1 }}>
                                    <div
                                        style={{
                                            width: '48px',
                                            height: '48px',
                                            borderRadius: '50%',
                                            background: isActive ? stage.color : '#334155',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            marginBottom: '0.5rem',
                                            border: isCurrent ? `3px solid ${stage.color}` : 'none',
                                            boxShadow: isCurrent ? `0 0 20px ${stage.color}50` : 'none',
                                            transition: 'all 0.3s ease'
                                        }}
                                    >
                                        <Icon size={24} color="white" />
                                    </div>
                                    <span
                                        style={{
                                            fontSize: '0.875rem',
                                            fontWeight: isCurrent ? 600 : 400,
                                            color: isActive ? '#f1f5f9' : '#64748b',
                                            textAlign: 'center'
                                        }}
                                    >
                                        {stage.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {status === 'rejected' && (
                    <div className="badge badge-danger mt-3" style={{ display: 'block', padding: '1rem' }}>
                        <XCircle size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                        Request was rejected. Please contact support for more information.
                    </div>
                )}
            </div>
        </div>
    );
};

export default RequestStatusTracker;
