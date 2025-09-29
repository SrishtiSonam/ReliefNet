import React, { useState } from 'react';
import { districts } from '../data/hardcodedData';

const Forecasts: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>(districts[0].id);
  const [forecastMethod, setForecastMethod] = useState<'ensemble' | 'arima' | 'garch'>('ensemble');
  const [showFeatures, setShowFeatures] = useState(false);

  const district = districts.find(d => d.id === selectedDistrict)!;
  const surgeProbThreshold = 0.4;
  const highSurgeDistricts = districts.filter(d => d.surge_prob > surgeProbThreshold);

  return (
    <div className="forecasts-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Demand Forecasting & Surge Analysis</h1>
          <p className="page-subtitle">Probabilistic forecasts with uncertainty quantification for VFA state augmentation</p>
        </div>
        
        <div className="header-controls">
          <label className="toggle-control">
            <input 
              type="checkbox" 
              checked={showFeatures}
              onChange={(e) => setShowFeatures(e.target.checked)}
            />
            <span>Show VFA Features</span>
          </label>
        </div>
      </div>

      {/* Surge Alert Center */}
      {highSurgeDistricts.length > 0 && (
        <div className="alert-banner">
          <div className="alert-icon">⚠️</div>
          <div className="alert-content">
            <div className="alert-title">High Surge Probability Detected</div>
            <div className="alert-message">
              {highSurgeDistricts.length} districts show surge probability &gt; {surgeProbThreshold * 100}%: {' '}
              {highSurgeDistricts.map(d => d.name).join(', ')}
            </div>
          </div>
        </div>
      )}

      <div className="forecasts-content">
        {/* Left Panel - District Selector & Forecast Details */}
        <div className="left-panel">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Select District</h3>
            </div>
            <div className="district-selector">
              {districts.map(d => (
                <button
                  key={d.id}
                  className={`district-option ${selectedDistrict === d.id ? 'active' : ''} ${d.surge_prob > 0.3 ? 'surge' : ''}`}
                  onClick={() => setSelectedDistrict(d.id)}
                >
                  <div className="option-header">
                    <span className="option-name">{d.name}</span>
                    {d.surge_prob > 0.3 && <span className="surge-badge">⚠️</span>}
                  </div>
                  <div className="option-meta">
                    Surge: {Math.round(d.surge_prob * 100)}%
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Forecast Method</h3>
            </div>
            <div className="method-selector">
              <button
                className={`method-button ${forecastMethod === 'ensemble' ? 'active' : ''}`}
                onClick={() => setForecastMethod('ensemble')}
              >
                <div className="method-name">Heavy-Tailed Ensemble</div>
                <div className="method-desc">Recommended</div>
              </button>
              <button
                className={`method-button ${forecastMethod === 'arima' ? 'active' : ''}`}
                onClick={() => setForecastMethod('arima')}
              >
                <div className="method-name">ARIMA</div>
                <div className="method-desc">Time series</div>
              </button>
              <button
                className={`method-button ${forecastMethod === 'garch' ? 'active' : ''}`}
                onClick={() => setForecastMethod('garch')}
              >
                <div className="method-name">GARCH</div>
                <div className="method-desc">Volatility</div>
              </button>
            </div>
            
            <div className="method-explanation">
              <h4>About {forecastMethod === 'ensemble' ? 'Ensemble' : forecastMethod.toUpperCase()}</h4>
              <p>
                {forecastMethod === 'ensemble' && 
                  'Combines multiple forecasting models to capture heavy-tailed distributions and extreme events. Provides robust uncertainty quantification.'}
                {forecastMethod === 'arima' && 
                  'AutoRegressive Integrated Moving Average model for time series forecasting with trend and seasonality.'}
                {forecastMethod === 'garch' && 
                  'Generalized AutoRegressive Conditional Heteroskedasticity for volatility modeling and variance forecasting.'}
              </p>
            </div>
          </div>
        </div>

        {/* Center Panel - Main Forecast Visualization */}
        <div className="center-panel">
          <div className="card forecast-card">
            <div className="card-header">
              <h3 className="card-title">{district.name} - Demand Forecast</h3>
              <p className="card-subtitle">Next epoch (t+1) probabilistic projection</p>
            </div>
            
            {/* Quantile Distribution Chart */}
            <div className="quantile-chart">
              <svg viewBox="0 0 600 300" className="chart-svg">
                {/* Background */}
                <rect width="600" height="300" fill="#f7fafc" />
                
                {/* Quantile bands */}
                <defs>
                  <linearGradient id="quantile-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#667eea" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#667eea" stopOpacity="0.1" />
                  </linearGradient>
                </defs>
                
                {/* P5-P95 band */}
                <rect x="150" y="50" width="300" height="200" fill="url(#quantile-gradient)" opacity="0.3" />
                
                {/* P25-P75 band (IQR) */}
                <rect x="200" y="80" width="200" height="140" fill="#667eea" opacity="0.2" />
                
                {/* Median line */}
                <line x1="150" y1="150" x2="450" y2="150" stroke="#667eea" strokeWidth="3" />
                
                {/* Surge threshold */}
                {district.surge_prob > 0.2 && (
                  <>
                    <line x1="150" y1="70" x2="450" y2="70" stroke="#e53e3e" strokeWidth="2" strokeDasharray="5,5" />
                    <text x="460" y="75" fontSize="12" fill="#e53e3e" fontWeight="600">Surge</text>
                  </>
                )}
                
                {/* Quantile markers */}
                <circle cx="150" cy="50" r="4" fill="#667eea" />
                <circle cx="200" cy="80" r="4" fill="#667eea" />
                <circle cx="300" cy="150" r="6" fill="#667eea" />
                <circle cx="400" cy="220" r="4" fill="#667eea" />
                <circle cx="450" cy="250" r="4" fill="#667eea" />
                
                {/* Labels */}
                <text x="30" y="55" fontSize="12" fill="#718096">P95: {district.forecast_quantiles.p95}</text>
                <text x="30" y="85" fontSize="12" fill="#718096">P75: {district.forecast_quantiles.p75}</text>
                <text x="30" y="155" fontSize="12" fill="#718096" fontWeight="600">P50: {district.forecast_quantiles.p50}</text>
                <text x="30" y="225" fontSize="12" fill="#718096">P25: {district.forecast_quantiles.p25}</text>
                <text x="30" y="255" fontSize="12" fill="#718096">P5: {district.forecast_quantiles.p5}</text>
                
                {/* Box plot visualization */}
                <rect x="500" y="80" width="50" height="140" fill="none" stroke="#667eea" strokeWidth="2" />
                <line x1="500" y1="150" x2="550" y2="150" stroke="#667eea" strokeWidth="3" />
                <line x1="525" y1="50" x2="525" y2="80" stroke="#667eea" strokeWidth="2" />
                <line x1="525" y1="220" x2="525" y2="250" stroke="#667eea" strokeWidth="2" />
                <line x1="515" y1="50" x2="535" y2="50" stroke="#667eea" strokeWidth="2" />
                <line x1="515" y1="250" x2="535" y2="250" stroke="#667eea" strokeWidth="2" />
              </svg>
            </div>

            {/* Forecast Metrics */}
            <div className="forecast-metrics">
              <div className="metric-item">
                <span className="metric-label">Mean (μ):</span>
                <span className="metric-value">{district.dt_t_t1.toLocaleString()}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Std Dev (σ):</span>
                <span className="metric-value">{district.sigma_dt}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Median (P50):</span>
                <span className="metric-value">{district.forecast_quantiles.p50.toLocaleString()}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">IQR:</span>
                <span className="metric-value">
                  {(district.forecast_quantiles.p75 - district.forecast_quantiles.p25).toLocaleString()}
                </span>
              </div>
              <div className="metric-item surge-metric">
                <span className="metric-label">Surge Prob:</span>
                <span className={`metric-value ${district.surge_prob > 0.3 ? 'danger' : 'safe'}`}>
                  {Math.round(district.surge_prob * 100)}%
                </span>
              </div>
            </div>

            <div className="surge-explanation">
              <strong>Surge Definition:</strong> P(demand &gt; 1.5× historical mean) = {Math.round(district.surge_prob * 100)}%
              <br/>
              <small>Probability that demand exceeds spike threshold based on ensemble forecast distribution</small>
            </div>
          </div>

          {showFeatures && (
            <div className="card vfa-features-card">
              <div className="card-header">
                <h3 className="card-title">VFA State Augmentation</h3>
                <p className="card-subtitle">Forecast features added to decision state</p>
              </div>
              
              <div className="feature-list">
                <div className="feature-item">
                  <code>d̄_t,t+1,n</code>
                  <span className="feature-desc">Mean forecast</span>
                  <span className="feature-value">{district.dt_t_t1}</span>
                </div>
                <div className="feature-item">
                  <code>σ_d_t,t+1,n</code>
                  <span className="feature-desc">Variance (uncertainty)</span>
                  <span className="feature-value">{district.sigma_dt}</span>
                </div>
                <div className="feature-item">
                  <code>q_05</code>
                  <span className="feature-desc">5th percentile</span>
                  <span className="feature-value">{district.forecast_quantiles.p5}</span>
                </div>
                <div className="feature-item">
                  <code>q_25</code>
                  <span className="feature-desc">25th percentile</span>
                  <span className="feature-value">{district.forecast_quantiles.p25}</span>
                </div>
                <div className="feature-item">
                  <code>q_50</code>
                  <span className="feature-desc">Median</span>
                  <span className="feature-value">{district.forecast_quantiles.p50}</span>
                </div>
                <div className="feature-item">
                  <code>q_75</code>
                  <span className="feature-desc">75th percentile</span>
                  <span className="feature-value">{district.forecast_quantiles.p75}</span>
                </div>
                <div className="feature-item">
                  <code>q_95</code>
                  <span className="feature-desc">95th percentile</span>
                  <span className="feature-value">{district.forecast_quantiles.p95}</span>
                </div>
                <div className="feature-item highlight">
                  <code>p_surge</code>
                  <span className="feature-desc">Surge probability</span>
                  <span className="feature-value">{district.surge_prob.toFixed(3)}</span>
                </div>
              </div>

              <div className="feature-note">
                <p>
                  These probabilistic forecast outputs are appended to the MDP state vector, 
                  enabling VFAs to anticipate demand spikes and hedge allocations proactively.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Alert Priority List */}
        <div className="right-panel">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Surge Alert Priority</h3>
              <p className="card-subtitle">Districts requiring hedging</p>
            </div>
            
            <div className="priority-list">
              {districts
                .filter(d => d.surge_prob > 0.25)
                .sort((a, b) => b.surge_prob - a.surge_prob)
                .map(d => (
                  <div key={d.id} className="priority-item">
                    <div className="priority-header">
                      <span className="priority-name">{d.name}</span>
                      <span className={`priority-badge ${d.surge_prob > 0.4 ? 'critical' : 'warning'}`}>
                        {Math.round(d.surge_prob * 100)}%
                      </span>
                    </div>
                    <div className="priority-details">
                      <div className="detail-row">
                        <span>Expected:</span>
                        <span>{d.dt_t_t1.toLocaleString()}</span>
                      </div>
                      <div className="detail-row">
                        <span>P95:</span>
                        <span className="danger">{d.forecast_quantiles.p95.toLocaleString()}</span>
                      </div>
                      <div className="detail-row">
                        <span>Current Stock:</span>
                        <span>{d.Itn.toLocaleString()}</span>
                      </div>
                    </div>
                    <button className="priority-action">Allocate Now</button>
                  </div>
                ))}
              
              {districts.filter(d => d.surge_prob > 0.25).length === 0 && (
                <div className="no-alerts">
                  <div className="no-alerts-icon">✅</div>
                  <p>No high-probability surge events detected</p>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Forecast Actions</h3>
            </div>
            <div className="forecast-actions">
              <button className="btn-primary action-btn">
                📊 Export Forecasts
              </button>
              <button className="btn-secondary action-btn">
                🔄 Refresh Ensemble
              </button>
              <button className="btn-secondary action-btn">
                📈 View Historical
              </button>
              <button className="btn-secondary action-btn">
                ⚙️ Tune Parameters
              </button>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .forecasts-page {
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }
        
        .page-title {
          font-size: 28px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 8px;
        }
        
        .page-subtitle {
          color: #718096;
          font-size: 16px;
        }
        
        .toggle-control {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #4a5568;
        }
        
        .toggle-control input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: #667eea;
        }
        
        .alert-banner {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 16px 20px;
          background: linear-gradient(135deg, #e53e3e 0%, #ff6b6b 100%);
          color: white;
          border-radius: 12px;
          margin-bottom: 24px;
          box-shadow: 0 4px 16px rgba(229, 62, 62, 0.3);
        }
        
        .alert-icon {
          font-size: 24px;
        }
        
        .alert-content {
          flex: 1;
        }
        
        .alert-title {
          font-weight: 600;
          font-size: 16px;
          margin-bottom: 4px;
        }
        
        .alert-message {
          font-size: 14px;
          opacity: 0.95;
        }
        
        .forecasts-content {
          display: grid;
          grid-template-columns: 280px 1fr 300px;
          gap: 24px;
        }
        
        .left-panel,
        .right-panel {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .center-panel {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .district-selector {
          display: flex;
          flex-direction: column;
          gap: 8px;
          max-height: 400px;
          overflow-y: auto;
        }
        
        .district-option {
          padding: 12px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          background: white;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .district-option:hover {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.05);
        }
        
        .district-option.active {
          border-color: #667eea;
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        }
        
        .district-option.surge {
          border-color: #ff8c00;
        }
        
        .option-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
        }
        
        .option-name {
          font-weight: 600;
          font-size: 14px;
          color: #1a202c;
        }
        
        .surge-badge {
          font-size: 14px;
        }
        
        .option-meta {
          font-size: 12px;
          color: #718096;
        }
        
        .method-selector {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }
        
        .method-button {
          padding: 12px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          background: white;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .method-button:hover {
          border-color: #667eea;
        }
        
        .method-button.active {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.1);
        }
        
        .method-name {
          font-weight: 600;
          font-size: 14px;
          color: #1a202c;
          margin-bottom: 2px;
        }
        
        .method-desc {
          font-size: 12px;
          color: #718096;
        }
        
        .method-explanation {
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .method-explanation h4 {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 8px;
        }
        
        .method-explanation p {
          font-size: 13px;
          color: #718096;
          line-height: 1.5;
        }
        
        .forecast-card {
          min-height: 400px;
        }
        
        .quantile-chart {
          margin-bottom: 24px;
        }
        
        .chart-svg {
          width: 100%;
          height: auto;
        }
        
        .forecast-metrics {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 16px;
          margin-bottom: 16px;
          padding: 16px;
          background: #f7fafc;
          border-radius: 8px;
        }
        
        .metric-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .metric-label {
          font-size: 12px;
          color: #718096;
          font-weight: 500;
        }
        
        .metric-value {
          font-size: 16px;
          font-weight: 600;
          color: #1a202c;
        }
        
        .metric-value.danger {
          color: #e53e3e;
        }
        
        .metric-value.safe {
          color: #4caf50;
        }
        
        .surge-metric {
          grid-column: span 1;
          background: rgba(255, 140, 0, 0.1);
          padding: 8px;
          border-radius: 6px;
        }
        
        .surge-explanation {
          padding: 12px;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 8px;
          font-size: 13px;
          color: #4a5568;
          line-height: 1.5;
        }
        
        .vfa-features-card {
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        }
        
        .feature-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }
        
        .feature-item {
          display: grid;
          grid-template-columns: 100px 1fr auto;
          gap: 12px;
          align-items: center;
          padding: 10px 12px;
          background: white;
          border-radius: 6px;
          font-size: 13px;
        }
        
        .feature-item.highlight {
          border: 2px solid #667eea;
          background: rgba(102, 126, 234, 0.05);
        }
        
        .feature-item code {
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-weight: 600;
          color: #667eea;
        }
        
        .feature-desc {
          color: #718096;
        }
        
        .feature-value {
          font-weight: 600;
          color: #1a202c;
        }
        
        .feature-note {
          padding: 12px;
          background: white;
          border-radius: 8px;
          border-left: 4px solid #667eea;
          font-size: 13px;
          color: #4a5568;
          line-height: 1.5;
        }
        
        .priority-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .priority-item {
          padding: 16px;
          background: white;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          transition: all 0.2s ease;
        }
        
        .priority-item:hover {
          border-color: #667eea;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .priority-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        
        .priority-name {
          font-weight: 600;
          font-size: 14px;
          color: #1a202c;
        }
        
        .priority-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }
        
        .priority-badge.critical {
          background: #e53e3e;
          color: white;
        }
        
        .priority-badge.warning {
          background: #ff8c00;
          color: white;
        }
        
        .priority-details {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 12px;
        }
        
        .detail-row {
          display: flex;
          justify-content: space-between;
          font-size: 13px;
        }
        
        .detail-row span:first-child {
          color: #718096;
        }
        
        .detail-row span:last-child {
          font-weight: 600;
          color: #4a5568;
        }
        
        .detail-row .danger {
          color: #e53e3e;
        }
        
        .priority-action {
          width: 100%;
          padding: 8px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .priority-action:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .no-alerts {
          text-align: center;
          padding: 32px;
          color: #718096;
        }
        
        .no-alerts-icon {
          font-size: 48px;
          margin-bottom: 12px;
        }
        
        .forecast-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .action-btn {
          width: 100%;
          padding: 12px;
          text-align: left;
          font-weight: 600;
        }
        
        @media (max-width: 1200px) {
          .forecasts-content {
            grid-template-columns: 1fr;
          }
          
          .forecast-metrics {
            grid-template-columns: repeat(3, 1fr);
          }
        }
        
        @media (max-width: 768px) {
          .forecast-metrics {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default Forecasts;