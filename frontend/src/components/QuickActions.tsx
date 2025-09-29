import React, { useState } from 'react';

const QuickActions: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [lastRun, setLastRun] = useState<string | null>(null);

  const handleRunSuggested = async () => {
    setIsRunning(true);
    // Simulate API call
    setTimeout(() => {
      setIsRunning(false);
      setLastRun(new Date().toLocaleTimeString());
    }, 2000);
  };

  const handleExport = () => {
    // Mock export functionality
    const data = {
      timestamp: new Date().toISOString(),
      epoch: 6,
      allocations: 'Mock allocation data...'
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `allocation-plan-epoch-6.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card quick-actions">
      <div className="card-header">
        <h3 className="card-title">Quick Actions</h3>
        <p className="card-subtitle">Execute common operations</p>
      </div>
      
      <div className="actions-list">
        <button 
          className="action-button primary"
          onClick={handleRunSuggested}
          disabled={isRunning}
        >
          <div className="button-content">
            <span className="button-icon">
              {isRunning ? '⏳' : '🚀'}
            </span>
            <div className="button-text">
              <span className="button-label">
                {isRunning ? 'Running...' : 'Run Suggested Allocation'}
              </span>
              <span className="button-desc">VFA + MIP optimization</span>
            </div>
          </div>
        </button>
        
        <button className="action-button secondary">
          <div className="button-content">
            <span className="button-icon">🔧</span>
            <div className="button-text">
              <span className="button-label">Open What-If</span>
              <span className="button-desc">Constraint modification</span>
            </div>
          </div>
        </button>
        
        <button 
          className="action-button secondary"
          onClick={handleExport}
        >
          <div className="button-content">
            <span className="button-icon">📊</span>
            <div className="button-text">
              <span className="button-label">Export Plan</span>
              <span className="button-desc">Download current allocation</span>
            </div>
          </div>
        </button>
        
        <button className="action-button danger">
          <div className="button-content">
            <span className="button-icon">⚠️</span>
            <div className="button-text">
              <span className="button-label">Emergency Override</span>
              <span className="button-desc">Manual intervention</span>
            </div>
          </div>
        </button>
      </div>
      
      {lastRun && (
        <div className="last-run">
          <span className="last-run-label">Last optimization:</span>
          <span className="last-run-time">{lastRun}</span>
        </div>
      )}
      
      <div className="optimization-status">
        <div className="status-header">
          <span className="status-label">System Status</span>
          <div className="status-indicator active"></div>
        </div>
        <div className="status-details">
          <div className="status-item">
            <span>VFA Model:</span>
            <span className="status-value">Active</span>
          </div>
          <div className="status-item">
            <span>MIP Solver:</span>
            <span className="status-value">Ready</span>
          </div>
          <div className="status-item">
            <span>Forecast Engine:</span>
            <span className="status-value">Updating</span>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .quick-actions {
          height: fit-content;
        }
        
        .actions-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 24px;
        }
        
        .action-button {
          display: flex;
          align-items: center;
          padding: 16px;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
          width: 100%;
          font-family: inherit;
        }
        
        .action-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .action-button.primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }
        
        .action-button.primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }
        
        .action-button.secondary {
          background: white;
          color: #4a5568;
          border: 2px solid #e2e8f0;
        }
        
        .action-button.secondary:hover {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.05);
        }
        
        .action-button.danger {
          background: white;
          color: #e53e3e;
          border: 2px solid #fed7d7;
        }
        
        .action-button.danger:hover {
          border-color: #e53e3e;
          background: rgba(229, 62, 62, 0.05);
        }
        
        .button-content {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
        }
        
        .button-icon {
          font-size: 20px;
          flex-shrink: 0;
        }
        
        .button-text {
          display: flex;
          flex-direction: column;
          gap: 2px;
          flex: 1;
        }
        
        .button-label {
          font-weight: 600;
          font-size: 14px;
        }
        
        .button-desc {
          font-size: 12px;
          opacity: 0.8;
        }
        
        .last-run {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 8px;
          margin-bottom: 16px;
          font-size: 14px;
        }
        
        .last-run-label {
          color: #667eea;
          font-weight: 500;
        }
        
        .last-run-time {
          color: #4a5568;
          font-weight: 600;
        }
        
        .optimization-status {
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        
        .status-label {
          font-weight: 600;
          font-size: 14px;
          color: #4a5568;
        }
        
        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #4caf50;
          animation: pulse 2s infinite;
        }
        
        .status-indicator.active {
          box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
        }
        
        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
          }
          70% {
            box-shadow: 0 0 0 8px rgba(76, 175, 80, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
          }
        }
        
        .status-details {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .status-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 13px;
          color: #718096;
        }
        
        .status-value {
          font-weight: 500;
          color: #4caf50;
        }
      `}</style>
    </div>
  );
};

export default QuickActions;