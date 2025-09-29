import React from 'react';
import { globalData, districts } from '../data/hardcodedData';

const StatePanel: React.FC = () => {
  const totalShortage = districts.reduce((sum, d) => sum + d.htn, 0);
  const totalDeprivationCost = districts.reduce((sum, d) => sum + d.deprivation_cost, 0);
  const avgDeprivationTime = districts.reduce((sum, d) => sum + d.deprivation_time_hours, 0) / districts.length;
  const totalExpectedDemand = districts.reduce((sum, d) => sum + d.dt_t_t1, 0);

  return (
    <div className="card state-panel">
      <div className="card-header">
        <h3 className="card-title">Current State Summary</h3>
        <p className="card-subtitle">MDP state variables for VFA input</p>
      </div>
      
      <div className="state-variables">
        <div className="state-section">
          <h4 className="section-title">Global State</h4>
          <div className="state-items">
            <div className="state-item">
              <span className="state-label">ICW (Central Warehouse):</span>
              <span className="state-value">{globalData.ICW.toLocaleString()}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Current Epoch (t):</span>
              <span className="state-value">{globalData.current_epoch}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Total Districts:</span>
              <span className="state-value">{districts.length}</span>
            </div>
          </div>
        </div>

        <div className="state-section">
          <h4 className="section-title">Aggregated Metrics</h4>
          <div className="state-items">
            <div className="state-item">
              <span className="state-label">Σ h_tn (Total Shortage):</span>
              <span className="state-value shortage">{totalShortage.toLocaleString()}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Σ g(δ_tn) (Total Deprivation):</span>
              <span className="state-value deprivation">{totalDeprivationCost.toFixed(2)}</span>
            </div>
            <div className="state-item">
              <span className="state-label">avg(δ_tn) (Avg Depriv. Time):</span>
              <span className="state-value">{avgDeprivationTime.toFixed(1)}h</span>
            </div>
            <div className="state-item">
              <span className="state-label">Σ d_t,t+1,n (Expected Demand):</span>
              <span className="state-value">{totalExpectedDemand.toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="state-section">
          <h4 className="section-title">District Breakdown</h4>
          <div className="district-breakdown">
            {districts.slice(0, 4).map(district => (
              <div key={district.id} className="district-state-item">
                <div className="district-header">
                  <span className="district-name">{district.name}</span>
                  <span className="district-id">({district.id})</span>
                </div>
                <div className="district-metrics">
                  <div className="metric-row">
                    <span>I_tn:</span>
                    <span>{district.Itn.toLocaleString()}</span>
                  </div>
                  <div className="metric-row">
                    <span>h_tn:</span>
                    <span className="shortage">{district.htn.toLocaleString()}</span>
                  </div>
                  <div className="metric-row">
                    <span>δ_tn:</span>
                    <span>{district.deprivation_time_hours}h</span>
                  </div>
                  <div className="metric-row">
                    <span>g(δ_tn):</span>
                    <span className="deprivation">{district.deprivation_cost.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
            {districts.length > 4 && (
              <div className="more-districts">
                +{districts.length - 4} more districts...
              </div>
            )}
          </div>
        </div>

        <div className="state-section">
          <h4 className="section-title">VFA Feature Vector</h4>
          <div className="feature-explanation">
            <p>State features fed to Value Function Approximation:</p>
            <ul>
              <li><code>I^x_tn</code> - District inventories</li>
              <li><code>δ^x_tn</code> - Deprivation times</li>
              <li><code>G^x_t,t+1,n</code> - Expected deprivation costs</li>
              <li><code>ICW^x_t</code> - Central warehouse stock</li>
              <li><code>t</code> - Time epoch</li>
            </ul>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .state-panel {
          height: fit-content;
        }
        
        .state-variables {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .state-section {
          border-bottom: 1px solid #e2e8f0;
          padding-bottom: 16px;
        }
        
        .state-section:last-child {
          border-bottom: none;
          padding-bottom: 0;
        }
        
        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 12px;
          padding-bottom: 4px;
          border-bottom: 2px solid #667eea;
        }
        
        .state-items {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .state-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 13px;
          padding: 6px 0;
        }
        
        .state-label {
          color: #718096;
          font-weight: 500;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
        
        .state-value {
          color: #1a202c;
          font-weight: 600;
        }
        
        .state-value.shortage {
          color: #e53e3e;
        }
        
        .state-value.deprivation {
          color: #ff8c00;
        }
        
        .district-breakdown {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .district-state-item {
          background: rgba(102, 126, 234, 0.05);
          border-radius: 8px;
          padding: 12px;
        }
        
        .district-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .district-name {
          font-weight: 600;
          color: #1a202c;
          font-size: 13px;
        }
        
        .district-id {
          font-size: 11px;
          color: #718096;
        }
        
        .district-metrics {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 4px;
        }
        
        .metric-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 12px;
        }
        
        .metric-row span:first-child {
          color: #718096;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-weight: 500;
        }
        
        .metric-row span:last-child {
          color: #4a5568;
          font-weight: 600;
        }
        
        .metric-row .shortage {
          color: #e53e3e;
        }
        
        .metric-row .deprivation {
          color: #ff8c00;
        }
        
        .more-districts {
          text-align: center;
          color: #718096;
          font-size: 12px;
          font-style: italic;
          padding: 8px;
          background: rgba(113, 128, 150, 0.1);
          border-radius: 6px;
        }
        
        .feature-explanation {
          font-size: 13px;
          color: #4a5568;
          line-height: 1.5;
        }
        
        .feature-explanation p {
          margin-bottom: 8px;
          font-weight: 500;
        }
        
        .feature-explanation ul {
          margin-left: 16px;
          color: #718096;
        }
        
        .feature-explanation li {
          margin-bottom: 4px;
        }
        
        .feature-explanation code {
          background: rgba(102, 126, 234, 0.1);
          padding: 2px 4px;
          border-radius: 3px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 12px;
          color: #667eea;
        }
      `}</style>
    </div>
  );
};

export default StatePanel;