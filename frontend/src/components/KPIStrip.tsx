import React from 'react';

interface KPIStripProps {
  centralWarehouse: number;
  highRiskDistricts: number;
  availableVehicles: number;
  inTransitVehicles: number;
  currentEpoch: number;
  nextUpdateEta: string;
}

const KPIStrip: React.FC<KPIStripProps> = ({
  centralWarehouse,
  highRiskDistricts,
  availableVehicles,
  inTransitVehicles,
  currentEpoch,
  nextUpdateEta
}) => {
  return (
    <div className="kpi-strip">
      <div className="kpi-item">
        <div className="kpi-icon warehouse">📦</div>
        <div className="kpi-content">
          <div className="kpi-value">{centralWarehouse.toLocaleString()}</div>
          <div className="kpi-label">Central Warehouse Inventory (ICW)</div>
        </div>
      </div>
      
      <div className="kpi-item">
        <div className={`kpi-icon risk ${highRiskDistricts > 3 ? 'high' : 'medium'}`}>⚠️</div>
        <div className="kpi-content">
          <div className="kpi-value risk">{highRiskDistricts}</div>
          <div className="kpi-label">Districts in High-Risk</div>
        </div>
      </div>
      
      <div className="kpi-item">
        <div className="kpi-icon vehicles">🚛</div>
        <div className="kpi-content">
          <div className="kpi-value">{availableVehicles}</div>
          <div className="kpi-label">
            Available Vehicles 
            <span className="kpi-sub">({inTransitVehicles} in-transit)</span>
          </div>
        </div>
      </div>
      
      <div className="kpi-item">
        <div className="kpi-icon epoch">🕐</div>
        <div className="kpi-content">
          <div className="kpi-value">Epoch {currentEpoch}</div>
          <div className="kpi-label">
            Current Decision Period
            <span className="kpi-sub">Next: {nextUpdateEta}</span>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .kpi-strip {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 24px;
          margin-bottom: 32px;
        }
        
        .kpi-item {
          display: flex;
          align-items: center;
          gap: 16px;
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.2);
          transition: all 0.2s ease;
        }
        
        .kpi-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        
        .kpi-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          flex-shrink: 0;
        }
        
        .kpi-icon.warehouse {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .kpi-icon.risk {
          background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        }
        
        .kpi-icon.risk.medium {
          background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
        }
        
        .kpi-icon.vehicles {
          background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        }
        
        .kpi-icon.epoch {
          background: linear-gradient(135deg, #26c6da 0%, #00bcd4 100%);
        }
        
        .kpi-content {
          flex: 1;
          min-width: 0;
        }
        
        .kpi-value {
          font-size: 24px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 4px;
          line-height: 1.2;
        }
        
        .kpi-value.risk {
          color: #e53e3e;
        }
        
        .kpi-label {
          font-size: 14px;
          color: #718096;
          font-weight: 500;
          line-height: 1.4;
        }
        
        .kpi-sub {
          display: block;
          font-size: 12px;
          color: #a0aec0;
          margin-top: 2px;
        }
        
        @media (max-width: 1200px) {
          .kpi-strip {
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
          }
        }
        
        @media (max-width: 768px) {
          .kpi-strip {
            grid-template-columns: 1fr;
            gap: 12px;
          }
          
          .kpi-item {
            padding: 16px;
          }
          
          .kpi-icon {
            width: 40px;
            height: 40px;
            font-size: 18px;
          }
          
          .kpi-value {
            font-size: 20px;
          }
          
          .kpi-label {
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default KPIStrip;