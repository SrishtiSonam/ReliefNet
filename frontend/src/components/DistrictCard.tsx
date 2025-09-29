import React from 'react';
import { District } from '../data/hardcodedData';
import Sparkline from './Sparkline';

interface DistrictCardProps {
  district: District;
}

const DistrictCard: React.FC<DistrictCardProps> = ({ district }) => {
  const getDeprivationColor = (cost: number) => {
    if (cost > 4) return '#e53e3e';
    if (cost > 2) return '#ff8c00';
    if (cost > 1) return '#ffd700';
    return '#38a169';
  };

  const getSurgeLevel = (prob: number) => {
    if (prob > 0.4) return { level: 'High', color: '#e53e3e' };
    if (prob > 0.25) return { level: 'Medium', color: '#ff8c00' };
    return { level: 'Low', color: '#38a169' };
  };

  const surgeLevelInfo = getSurgeLevel(district.surge_prob);

  // Mock sparkline data for demand trend
  const sparklineData = [
    district.forecast_quantiles.p25,
    district.forecast_quantiles.p50,
    district.dt_t_t1,
    district.forecast_quantiles.p75,
    district.forecast_quantiles.p95
  ];

  return (
    <div className="district-card">
      <div className="district-header">
        <div className="district-title-section">
          <h4 className="district-name">{district.name}</h4>
          <span className="district-id">{district.id}</span>
        </div>
        {district.surge_prob > 0.3 && (
          <div className="surge-badge" style={{ backgroundColor: surgeLevelInfo.color }}>
            SURGE {Math.round(district.surge_prob * 100)}%
          </div>
        )}
      </div>

      <div className="district-stats">
        <div className="stat-row">
          <span className="stat-label">Population:</span>
          <span className="stat-value">{district.pop_affected.toLocaleString()}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Inventory:</span>
          <span className="stat-value">{district.Itn.toLocaleString()}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Shortage:</span>
          <span className="stat-value shortage">{district.htn.toLocaleString()}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Deprivation Time:</span>
          <span className="stat-value">{district.deprivation_time_hours}h</span>
        </div>
      </div>

      <div className="deprivation-cost">
        <div className="cost-header">
          <span className="cost-label">Deprivation Cost</span>
          <span 
            className="cost-value" 
            style={{ color: getDeprivationColor(district.deprivation_cost) }}
          >
            {district.deprivation_cost.toFixed(2)}
          </span>
        </div>
        <div className="cost-bar">
          <div 
            className="cost-fill" 
            style={{ 
              width: `${Math.min(district.deprivation_cost / 6 * 100, 100)}%`,
              backgroundColor: getDeprivationColor(district.deprivation_cost)
            }}
          ></div>
        </div>
      </div>

      <div className="allocation-section">
        <h5 className="allocation-title">Recommended Allocation</h5>
        <div className="allocation-items">
          {district.suggested_truck_units > 0 && (
            <div className="allocation-item">
              <span className="vehicle-icon">🚛</span>
              <span className="allocation-text">
                {district.suggested_truck_units} trucks ({district.suggested_truck_quantity.toLocaleString()} units)
              </span>
            </div>
          )}
          {district.suggested_UAV_units > 0 && (
            <div className="allocation-item">
              <span className="vehicle-icon">🚁</span>
              <span className="allocation-text">
                {district.suggested_UAV_units} UAVs ({district.suggested_UAV_quantity.toLocaleString()} units)
              </span>
            </div>
          )}
          {district.suggested_truck_units === 0 && district.suggested_UAV_units === 0 && (
            <div className="no-allocation">No allocation needed</div>
          )}
        </div>
      </div>

      <div className="demand-trend">
        <div className="trend-header">
          <span className="trend-label">Expected Demand</span>
          <span className="trend-value">{district.dt_t_t1.toLocaleString()}</span>
        </div>
        <Sparkline data={sparklineData} width={100} height={30} />
      </div>

      <style jsx>{`
        .district-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.2);
          transition: all 0.2s ease;
          position: relative;
        }
        
        .district-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        
        .district-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
        }
        
        .district-title-section {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .district-name {
          font-size: 16px;
          font-weight: 600;
          color: #1a202c;
          margin: 0;
        }
        
        .district-id {
          font-size: 12px;
          color: #718096;
          font-weight: 500;
        }
        
        .surge-badge {
          background: #e53e3e;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 600;
          letter-spacing: 0.5px;
        }
        
        .district-stats {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }
        
        .stat-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 14px;
        }
        
        .stat-label {
          color: #718096;
          font-weight: 500;
        }
        
        .stat-value {
          color: #4a5568;
          font-weight: 600;
        }
        
        .stat-value.shortage {
          color: #e53e3e;
        }
        
        .deprivation-cost {
          margin-bottom: 16px;
        }
        
        .cost-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .cost-label {
          font-size: 13px;
          color: #718096;
          font-weight: 500;
        }
        
        .cost-value {
          font-size: 16px;
          font-weight: 700;
        }
        
        .cost-bar {
          height: 4px;
          background: #e2e8f0;
          border-radius: 2px;
          overflow: hidden;
        }
        
        .cost-fill {
          height: 100%;
          border-radius: 2px;
          transition: width 0.3s ease;
        }
        
        .allocation-section {
          margin-bottom: 16px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .allocation-title {
          font-size: 13px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 8px;
        }
        
        .allocation-items {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .allocation-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
        }
        
        .vehicle-icon {
          font-size: 16px;
        }
        
        .allocation-text {
          color: #4a5568;
          font-weight: 500;
        }
        
        .no-allocation {
          font-size: 13px;
          color: #718096;
          font-style: italic;
        }
        
        .demand-trend {
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .trend-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .trend-label {
          font-size: 13px;
          color: #718096;
          font-weight: 500;
        }
        
        .trend-value {
          font-size: 14px;
          font-weight: 600;
          color: #667eea;
        }
      `}</style>
    </div>
  );
};

export default DistrictCard;