import React, { useState } from 'react';
import { vehicleClasses, vehicles, roads } from '../data/hardcodedData';
import FleetTable from '../components/FleetTable';
import RoadTable from '../components/RoadTable';
import VehicleTimeline from '../components/VehicleTimeline';

const FleetRoads: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'fleet' | 'roads'>('fleet');

  const totalVehicles = vehicleClasses.reduce((sum, vc) => sum + vc.available + vc.in_transit + (vc.charging || 0), 0);
  const availableVehicles = vehicleClasses.reduce((sum, vc) => sum + vc.available, 0);
  const inTransitVehicles = vehicleClasses.reduce((sum, vc) => sum + vc.in_transit, 0);
  const chargingVehicles = vehicleClasses.reduce((sum, vc) => sum + (vc.charging || 0), 0);

  const openRoads = roads.filter(r => r.status === 'open').length;
  const blockedRoads = roads.filter(r => r.status === 'blocked').length;
  const slowRoads = roads.filter(r => r.status === 'slow').length;

  return (
    <div className="fleet-roads">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Fleet & Transportation Network</h1>
          <p className="page-subtitle">Manage vehicle resources and monitor road conditions</p>
        </div>
        
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'fleet' ? 'active' : ''}`}
            onClick={() => setActiveTab('fleet')}
          >
            🚛 Fleet Management
          </button>
          <button 
            className={`tab-button ${activeTab === 'roads' ? 'active' : ''}`}
            onClick={() => setActiveTab('roads')}
          >
            🛣️ Road Network
          </button>
        </div>
      </div>

      {/* Fleet Overview Cards */}
      <div className="overview-cards">
        <div className="overview-card">
          <div className="card-icon fleet-icon">🚛</div>
          <div className="card-content">
            <div className="card-value">{totalVehicles}</div>
            <div className="card-label">Total Fleet Size</div>
          </div>
        </div>
        
        <div className="overview-card">
          <div className="card-icon available-icon">✅</div>
          <div className="card-content">
            <div className="card-value">{availableVehicles}</div>
            <div className="card-label">Available Now</div>
          </div>
        </div>
        
        <div className="overview-card">
          <div className="card-icon transit-icon">🚀</div>
          <div className="card-content">
            <div className="card-value">{inTransitVehicles}</div>
            <div className="card-label">In Transit</div>
          </div>
        </div>
        
        <div className="overview-card">
          <div className="card-icon charging-icon">🔋</div>
          <div className="card-content">
            <div className="card-value">{chargingVehicles}</div>
            <div className="card-label">Charging</div>
          </div>
        </div>

        {activeTab === 'roads' && (
          <>
            <div className="overview-card">
              <div className="card-icon road-open-icon">🟢</div>
              <div className="card-content">
                <div className="card-value">{openRoads}</div>
                <div className="card-label">Open Roads</div>
              </div>
            </div>
            
            <div className="overview-card">
              <div className="card-icon road-slow-icon">🟡</div>
              <div className="card-content">
                <div className="card-value">{slowRoads}</div>
                <div className="card-label">Slow Roads</div>
              </div>
            </div>
            
            <div className="overview-card">
              <div className="card-icon road-blocked-icon">🔴</div>
              <div className="card-content">
                <div className="card-value">{blockedRoads}</div>
                <div className="card-label">Blocked Roads</div>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="wave-divider"></div>

      {activeTab === 'fleet' ? (
        <div className="fleet-content">
          <div className="fleet-main">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Vehicle Classes & Capabilities</h3>
                <p className="card-subtitle">Fleet composition with capacity and cost metrics</p>
              </div>
              <FleetTable vehicleClasses={vehicleClasses} />
            </div>
            
            <div className="card timeline-card">
              <div className="card-header">
                <h3 className="card-title">Vehicle Operations Timeline</h3>
                <p className="card-subtitle">Current assignments and ETAs</p>
              </div>
              <VehicleTimeline vehicles={vehicles} vehicleClasses={vehicleClasses} />
            </div>
          </div>
          
          <div className="fleet-sidebar">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Fleet Utilization</h3>
              </div>
              <div className="utilization-content">
                {vehicleClasses.map(vc => {
                  const total = vc.available + vc.in_transit + (vc.charging || 0);
                  const utilization = ((vc.in_transit + (vc.charging || 0)) / total) * 100;
                  
                  return (
                    <div key={vc.id} className="utilization-item">
                      <div className="utilization-header">
                        <span className="vehicle-type">{vc.name}</span>
                        <span className="utilization-percent">{utilization.toFixed(0)}%</span>
                      </div>
                      <div className="utilization-bar">
                        <div 
                          className="utilization-fill"
                          style={{ 
                            width: `${utilization}%`,
                            backgroundColor: utilization > 80 ? '#e53e3e' : utilization > 50 ? '#ff8c00' : '#4caf50'
                          }}
                        ></div>
                      </div>
                      <div className="utilization-details">
                        <span>Active: {vc.in_transit + (vc.charging || 0)}</span>
                        <span>Total: {total}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Fleet Actions</h3>
              </div>
              <div className="fleet-actions">
                <button className="btn-primary action-btn">
                  🔧 Schedule Maintenance
                </button>
                <button className="btn-secondary action-btn">
                  📊 Generate Fleet Report
                </button>
                <button className="btn-secondary action-btn">
                  ⚡ Optimize Routes
                </button>
                <button className="btn-danger action-btn">
                  🚨 Emergency Recall
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="roads-content">
          <div className="roads-main">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Road Network Status</h3>
                <p className="card-subtitle">Transportation routes with travel times and conditions</p>
              </div>
              <RoadTable roads={roads} />
            </div>
          </div>
          
          <div className="roads-sidebar">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Network Health</h3>
              </div>
              <div className="network-health">
                <div className="health-metric">
                  <span className="health-label">Network Availability:</span>
                  <span className="health-value success">
                    {((openRoads / roads.length) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="health-metric">
                  <span className="health-label">Avg Travel Time:</span>
                  <span className="health-value">
                    {(roads.reduce((sum, r) => sum + r.mean_travel_time, 0) / roads.length).toFixed(1)}h
                  </span>
                </div>
                <div className="health-metric">
                  <span className="health-label">Critical Routes:</span>
                  <span className="health-value warning">{blockedRoads}</span>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Road Actions</h3>
              </div>
              <div className="road-actions">
                <button className="btn-primary action-btn">
                  🔍 Inspect Routes
                </button>
                <button className="btn-secondary action-btn">
                  📈 Traffic Analysis
                </button>
                <button className="btn-secondary action-btn">
                  🛠️ Report Incident
                </button>
                <button className="btn-danger action-btn">
                  🚧 Close Route
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .fleet-roads {
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 32px;
        }
        
        .header-content h1 {
          font-size: 28px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 8px;
        }
        
        .header-content p {
          color: #718096;
          font-size: 16px;
        }
        
        .tab-navigation {
          display: flex;
          gap: 8px;
        }
        
        .tab-button {
          padding: 12px 24px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          background: white;
          color: #4a5568;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .tab-button:hover {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.05);
        }
        
        .tab-button.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: #667eea;
          color: white;
        }
        
        .overview-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 32px;
        }
        
        .overview-card {
          display: flex;
          align-items: center;
          gap: 16px;
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          flex-shrink: 0;
        }
        
        .fleet-icon {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .available-icon {
          background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        }
        
        .transit-icon {
          background: linear-gradient(135deg, #ff8c00 0%, #ffa726 100%);
        }
        
        .charging-icon {
          background: linear-gradient(135deg, #26c6da 0%, #00bcd4 100%);
        }
        
        .road-open-icon {
          background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        }
        
        .road-slow-icon {
          background: linear-gradient(135deg, #ff8c00 0%, #ffa726 100%);
        }
        
        .road-blocked-icon {
          background: linear-gradient(135deg, #e53e3e 0%, #ff6b6b 100%);
        }
        
        .card-content {
          flex: 1;
        }
        
        .card-value {
          font-size: 24px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 4px;
        }
        
        .card-label {
          font-size: 14px;
          color: #718096;
          font-weight: 500;
        }
        
        .fleet-content,
        .roads-content {
          display: grid;
          grid-template-columns: 1fr 300px;
          gap: 24px;
        }
        
        .fleet-main,
        .roads-main {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .fleet-sidebar,
        .roads-sidebar {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .timeline-card {
          margin-top: 0;
        }
        
        .utilization-content {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .utilization-item {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .utilization-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .vehicle-type {
          font-size: 14px;
          font-weight: 600;
          color: #1a202c;
        }
        
        .utilization-percent {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
        }
        
        .utilization-bar {
          height: 8px;
          background: #e2e8f0;
          border-radius: 4px;
          overflow: hidden;
        }
        
        .utilization-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.3s ease;
        }
        
        .utilization-details {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #718096;
        }
        
        .fleet-actions,
        .road-actions {
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
        
        .network-health {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .health-metric {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 14px;
        }
        
        .health-label {
          color: #718096;
          font-weight: 500;
        }
        
        .health-value {
          font-weight: 600;
          color: #1a202c;
        }
        
        .health-value.success {
          color: #4caf50;
        }
        
        .health-value.warning {
          color: #e53e3e;
        }
        
        @media (max-width: 1200px) {
          .fleet-content,
          .roads-content {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          
          .fleet-sidebar,
          .roads-sidebar {
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            flex-direction: row;
          }
        }
        
        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            gap: 16px;
          }
          
          .tab-navigation {
            width: 100%;
          }
          
          .tab-button {
            flex: 1;
            text-align: center;
          }
          
          .overview-cards {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .fleet-sidebar,
          .roads-sidebar {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default FleetRoads;