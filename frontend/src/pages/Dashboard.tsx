import React from 'react';
import { globalData, districts, vehicleClasses } from '../data/hardcodedData';
import DistrictCard from '../components/DistrictCard';
import KPIStrip from '../components/KPIStrip';
import ForecastChart from '../components/ForecastChart';
import QuickActions from '../components/QuickActions';

const Dashboard: React.FC = () => {
  const highRiskDistricts = districts.filter(d => d.deprivation_cost > 3.0);
  const totalVehiclesAvailable = vehicleClasses.reduce((sum, vc) => sum + vc.available, 0);
  const totalVehiclesInTransit = vehicleClasses.reduce((sum, vc) => sum + vc.in_transit, 0);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Operations Dashboard</h1>
        <p className="dashboard-subtitle">Real-time overview of resource allocation and district status</p>
      </div>
      
      <div className="wave-divider"></div>
      
      <KPIStrip
        centralWarehouse={globalData.ICW}
        highRiskDistricts={highRiskDistricts.length}
        availableVehicles={totalVehiclesAvailable}
        inTransitVehicles={totalVehiclesInTransit}
        currentEpoch={globalData.current_epoch}
        nextUpdateEta={globalData.next_update_eta}
      />
      
      <div className="dashboard-content">
        <div className="left-column">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Demand & Supply Forecast</h3>
              <p className="card-subtitle">Next 7 epochs projection with surge indicators</p>
            </div>
            <ForecastChart />
          </div>
        </div>
        
        <div className="center-column">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">District Status Overview</h3>
              <p className="card-subtitle">{districts.length} districts monitored</p>
            </div>
            <div className="districts-grid">
              {districts.map(district => (
                <DistrictCard key={district.id} district={district} />
              ))}
            </div>
          </div>
        </div>
        
        <div className="right-column">
          <QuickActions />
          
          <div className="card mission-card">
            <div className="card-header">
              <h3 className="card-title">Mission Objective</h3>
            </div>
            <div className="mission-content">
              <p>
                Minimize total deprivation cost g(δ) across all districts while optimizing 
                resource allocation under vehicle capacity and transportation constraints. 
                Current optimization targets early intervention to prevent prolonged shortages 
                and reduce human suffering.
              </p>
              <div className="mission-metrics">
                <div className="metric">
                  <span className="metric-label">Total Deprivation Cost</span>
                  <span className="metric-value">
                    {districts.reduce((sum, d) => sum + d.deprivation_cost, 0).toFixed(2)}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Avg Deprivation Time</span>
                  <span className="metric-value">
                    {(districts.reduce((sum, d) => sum + d.deprivation_time_hours, 0) / districts.length).toFixed(1)}h
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .dashboard {
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .dashboard-header {
          text-align: center;
          margin-bottom: 32px;
        }
        
        .dashboard-title {
          font-size: 32px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 8px;
        }
        
        .dashboard-subtitle {
          font-size: 16px;
          color: #718096;
        }
        
        .dashboard-content {
          display: grid;
          grid-template-columns: 1fr 2fr 1fr;
          gap: 24px;
          margin-top: 24px;
        }
        
        .left-column,
        .right-column {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .districts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
          margin-top: 16px;
        }
        
        .mission-card {
          margin-top: 24px;
        }
        
        .mission-content {
          font-size: 14px;
          line-height: 1.6;
          color: #4a5568;
        }
        
        .mission-metrics {
          display: flex;
          gap: 24px;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .metric {
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
          font-size: 18px;
          font-weight: 600;
          color: #667eea;
        }
        
        @media (max-width: 1200px) {
          .dashboard-content {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          
          .districts-grid {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          }
        }
        
        @media (max-width: 768px) {
          .dashboard-title {
            font-size: 24px;
          }
          
          .districts-grid {
            grid-template-columns: 1fr;
          }
          
          .mission-metrics {
            flex-direction: column;
            gap: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;