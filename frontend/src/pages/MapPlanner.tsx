import React, { useState } from 'react';
import { districts, roads, vehicles } from '../data/hardcodedData';

const MapPlanner: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);
  const [mapLayers, setMapLayers] = useState({
    districts: true,
    vehicles: true,
    roads: true,
    routes: false
  });

  const selectedDistrictData = selectedDistrict ? 
    districts.find(d => d.id === selectedDistrict) : null;

  const getDistrictColor = (deprivationCost: number) => {
    if (deprivationCost > 4) return '#e53e3e';
    if (deprivationCost > 2) return '#ff8c00';
    if (deprivationCost > 1) return '#ffd700';
    return '#4caf50';
  };

  const getRoadColor = (status: string) => {
    switch (status) {
      case 'open': return '#4caf50';
      case 'slow': return '#ff8c00';
      case 'blocked': return '#e53e3e';
      default: return '#718096';
    }
  };

  const handleLayerToggle = (layer: keyof typeof mapLayers) => {
    setMapLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  return (
    <div className="map-planner">
      <div className="map-header">
        <div className="map-title-section">
          <h1 className="page-title">Spatial Resource Allocation</h1>
          <p className="page-subtitle">Interactive district mapping with transportation network</p>
        </div>
        
        <div className="map-controls">
          <div className="layer-toggles">
            <label className="toggle-item">
              <input
                type="checkbox"
                checked={mapLayers.districts}
                onChange={() => handleLayerToggle('districts')}
              />
              <span>Districts</span>
            </label>
            <label className="toggle-item">
              <input
                type="checkbox"
                checked={mapLayers.vehicles}
                onChange={() => handleLayerToggle('vehicles')}
              />
              <span>Fleet</span>
            </label>
            <label className="toggle-item">
              <input
                type="checkbox"
                checked={mapLayers.roads}
                onChange={() => handleLayerToggle('roads')}
              />
              <span>Roads</span>
            </label>
            <label className="toggle-item">
              <input
                type="checkbox"
                checked={mapLayers.routes}
                onChange={() => handleLayerToggle('routes')}
              />
              <span>Routes</span>
            </label>
          </div>
          
          <button className="btn-primary simulate-btn">
            Simulate Allocation
          </button>
        </div>
      </div>
      
      <div className="map-content">
        <div className="map-container">
          <div className="map-canvas">
            <svg viewBox="0 0 800 600" className="map-svg">
              {/* Background */}
              <rect width="800" height="600" fill="#f7fafc" />
              
              {/* Grid */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e2e8f0" strokeWidth="1" opacity="0.5"/>
                </pattern>
              </defs>
              <rect width="800" height="600" fill="url(#grid)" />
              
              {/* Central Warehouse */}
              <g>
                <rect x="380" y="280" width="40" height="40" fill="#667eea" rx="8" />
                <text x="400" y="302" textAnchor="middle" fill="white" fontSize="20">🏭</text>
                <text x="400" y="335" textAnchor="middle" fill="#4a5568" fontSize="12" fontWeight="600">
                  Central Warehouse
                </text>
              </g>
              
              {/* Roads */}
              {mapLayers.roads && roads.map(road => {
                const fromCoord = road.from === 'CW' ? [400, 300] : 
                  districts.find(d => d.id === road.from)?.coordinates.map(c => c * 10) || [0, 0];
                const toCoord = road.to === 'CW' ? [400, 300] :
                  districts.find(d => d.id === road.to)?.coordinates.map(c => c * 10) || [0, 0];
                
                return (
                  <g key={road.id}>
                    <line
                      x1={fromCoord[0]}
                      y1={fromCoord[1]}
                      x2={toCoord[0]}
                      y2={toCoord[1]}
                      stroke={getRoadColor(road.status)}
                      strokeWidth="4"
                      strokeDasharray={road.status === 'blocked' ? '8,4' : 'none'}
                      opacity="0.8"
                    />
                  </g>
                );
              })}
              
              {/* Districts */}
              {mapLayers.districts && districts.map(district => {
                const x = (district.coordinates[0] - 84) * 200 + 100;
                const y = 600 - ((district.coordinates[1] - 27) * 300 + 100);
                const isSelected = selectedDistrict === district.id;
                
                return (
                  <g 
                    key={district.id}
                    className="district-marker"
                    onClick={() => setSelectedDistrict(district.id)}
                  >
                    <circle
                      cx={x}
                      cy={y}
                      r={isSelected ? "25" : "20"}
                      fill={getDistrictColor(district.deprivation_cost)}
                      stroke={isSelected ? "#1a202c" : "white"}
                      strokeWidth={isSelected ? "3" : "2"}
                      opacity="0.9"
                      className="district-circle"
                    />
                    <text
                      x={x}
                      y={y + 5}
                      textAnchor="middle"
                      fill="white"
                      fontSize="12"
                      fontWeight="600"
                      pointerEvents="none"
                    >
                      {district.id}
                    </text>
                    {district.surge_prob > 0.3 && (
                      <circle
                        cx={x + 15}
                        cy={y - 15}
                        r="8"
                        fill="#ff6b6b"
                        stroke="white"
                        strokeWidth="2"
                      />
                    )}
                  </g>
                );
              })}
              
              {/* Vehicles */}
              {mapLayers.vehicles && vehicles.filter(v => v.current_location).map(vehicle => {
                const district = districts.find(d => d.id === vehicle.current_location);
                if (!district) return null;
                
                const x = (district.coordinates[0] - 84) * 200 + 100;
                const y = 600 - ((district.coordinates[1] - 27) * 300 + 100);
                
                return (
                  <g key={vehicle.id}>
                    <circle cx={x + 30} cy={y - 30} r="12" fill="white" stroke="#4a5568" strokeWidth="2" />
                    <text x={x + 30} y={y - 25} textAnchor="middle" fontSize="16">
                      {vehicle.class_id.includes('truck') ? '🚛' : '🚁'}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
          
          <div className="map-legend">
            <h4 className="legend-title">Map Legend</h4>
            <div className="legend-items">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#4caf50' }}></div>
                <span>Low Risk (Cost ≤ 1)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#ffd700' }}></div>
                <span>Medium Risk (1-2)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#ff8c00' }}></div>
                <span>High Risk (2-4)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#e53e3e' }}></div>
                <span>Critical Risk (>4)</span>
              </div>
            </div>
            
            <div className="road-legend">
              <h5>Road Status</h5>
              <div className="legend-items">
                <div className="legend-item">
                  <div className="road-line open"></div>
                  <span>Open</span>
                </div>
                <div className="legend-item">
                  <div className="road-line slow"></div>
                  <span>Slow</span>
                </div>
                <div className="legend-item">
                  <div className="road-line blocked"></div>
                  <span>Blocked</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {selectedDistrictData && (
          <div className="district-details">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">{selectedDistrictData.name} ({selectedDistrictData.id})</h3>
                <button 
                  className="close-btn"
                  onClick={() => setSelectedDistrict(null)}
                >
                  ×
                </button>
              </div>
              
              <div className="detail-sections">
                <div className="detail-section">
                  <h4>Current Status</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span>Population Affected:</span>
                      <span>{selectedDistrictData.pop_affected.toLocaleString()}</span>
                    </div>
                    <div className="detail-item">
                      <span>Current Inventory:</span>
                      <span>{selectedDistrictData.Itn.toLocaleString()}</span>
                    </div>
                    <div className="detail-item">
                      <span>Shortage:</span>
                      <span className="shortage">{selectedDistrictData.htn.toLocaleString()}</span>
                    </div>
                    <div className="detail-item">
                      <span>Deprivation Time:</span>
                      <span>{selectedDistrictData.deprivation_time_hours}h</span>
                    </div>
                    <div className="detail-item">
                      <span>Deprivation Cost:</span>
                      <span style={{ color: getDistrictColor(selectedDistrictData.deprivation_cost) }}>
                        {selectedDistrictData.deprivation_cost.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Forecast & Surge</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span>Expected Demand:</span>
                      <span>{selectedDistrictData.dt_t_t1.toLocaleString()}</span>
                    </div>
                    <div className="detail-item">
                      <span>Surge Probability:</span>
                      <span className={selectedDistrictData.surge_prob > 0.3 ? 'surge-high' : 'surge-low'}>
                        {Math.round(selectedDistrictData.surge_prob * 100)}%
                      </span>
                    </div>
                    <div className="detail-item">
                      <span>P95 Demand:</span>
                      <span>{selectedDistrictData.forecast_quantiles.p95.toLocaleString()}</span>
                    </div>
                    <div className="detail-item">
                      <span>Forecast Variance:</span>
                      <span>{selectedDistrictData.sigma_dt}</span>
                    </div>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Spatial Relations</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span>Neighbors:</span>
                      <span>{selectedDistrictData.neighbors.join(', ')}</span>
                    </div>
                    <div className="detail-item">
                      <span>Influence Score:</span>
                      <span>{selectedDistrictData.spatial_influence_score.toFixed(2)}</span>
                    </div>
                  </div>
                  <div className="influence-note">
                    <small>Influence score represents how delivering to this district affects neighboring areas (GNN/Transformer learned parameter)</small>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Recommended Allocation</h4>
                  <div className="allocation-summary">
                    {selectedDistrictData.suggested_truck_units > 0 && (
                      <div className="allocation-row">
                        <span className="vehicle-icon">🚛</span>
                        <span>{selectedDistrictData.suggested_truck_units} Trucks</span>
                        <span className="allocation-units">
                          {selectedDistrictData.suggested_truck_quantity.toLocaleString()} units
                        </span>
                      </div>
                    )}
                    {selectedDistrictData.suggested_UAV_units > 0 && (
                      <div className="allocation-row">
                        <span className="vehicle-icon">🚁</span>
                        <span>{selectedDistrictData.suggested_UAV_units} UAVs</span>
                        <span className="allocation-units">
                          {selectedDistrictData.suggested_UAV_quantity.toLocaleString()} units
                        </span>
                      </div>
                    )}
                    {selectedDistrictData.suggested_truck_units === 0 && selectedDistrictData.suggested_UAV_units === 0 && (
                      <div className="no-allocation">No allocation recommended</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .map-planner {
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .map-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }
        
        .map-title-section h1 {
          font-size: 28px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 8px;
        }
        
        .map-title-section p {
          color: #718096;
          font-size: 16px;
        }
        
        .map-controls {
          display: flex;
          align-items: center;
          gap: 24px;
        }
        
        .layer-toggles {
          display: flex;
          gap: 16px;
        }
        
        .toggle-item {
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #4a5568;
        }
        
        .toggle-item input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: #667eea;
        }
        
        .simulate-btn {
          padding: 12px 24px;
          font-size: 14px;
          font-weight: 600;
        }
        
        .map-content {
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 24px;
        }
        
        .map-container {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .map-canvas {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }
        
        .map-svg {
          width: 100%;
          height: auto;
          cursor: crosshair;
        }
        
        .district-marker {
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .district-marker:hover .district-circle {
          transform: scale(1.1);
          transform-origin: center;
        }
        
        .map-legend {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
          height: fit-content;
        }
        
        .legend-title {
          font-size: 16px;
          font-weight: 600;
          color: #1a202c;
          margin-bottom: 16px;
        }
        
        .legend-items {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #4a5568;
        }
        
        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .road-legend {
          margin-top: 24px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .road-legend h5 {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 12px;
        }
        
        .road-line {
          width: 20px;
          height: 3px;
          border-radius: 2px;
        }
        
        .road-line.open {
          background: #4caf50;
        }
        
        .road-line.slow {
          background: #ff8c00;
        }
        
        .road-line.blocked {
          background: #e53e3e;
          background-image: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 2px,
            white 2px,
            white 4px
          );
        }
        
        .district-details {
          width: 400px;
          max-height: 600px;
          overflow-y: auto;
        }
        
        .district-details .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          color: #718096;
          cursor: pointer;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          transition: all 0.2s ease;
        }
        
        .close-btn:hover {
          background: #e2e8f0;
          color: #4a5568;
        }
        
        .detail-sections {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .detail-section h4 {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 12px;
          padding-bottom: 6px;
          border-bottom: 2px solid #667eea;
        }
        
        .detail-grid {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .detail-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 14px;
        }
        
        .detail-item span:first-child {
          color: #718096;
          font-weight: 500;
        }
        
        .detail-item span:last-child {
          color: #1a202c;
          font-weight: 600;
        }
        
        .shortage {
          color: #e53e3e !important;
        }
        
        .surge-high {
          color: #e53e3e !important;
        }
        
        .surge-low {
          color: #4caf50 !important;
        }
        
        .influence-note {
          margin-top: 8px;
          padding: 8px;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 6px;
        }
        
        .influence-note small {
          color: #667eea;
          font-size: 12px;
          line-height: 1.4;
        }
        
        .allocation-summary {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .allocation-row {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: rgba(102, 126, 234, 0.05);
          border-radius: 6px;
          font-size: 14px;
        }
        
        .allocation-row .vehicle-icon {
          font-size: 16px;
        }
        
        .allocation-units {
          margin-left: auto;
          font-weight: 600;
          color: #667eea;
        }
        
        .no-allocation {
          font-style: italic;
          color: #718096;
          text-align: center;
          padding: 16px;
        }
        
        @media (max-width: 1200px) {
          .map-content {
            grid-template-columns: 1fr;
          }
          
          .district-details {
            width: 100%;
            max-height: none;
          }
        }
        
        @media (max-width: 768px) {
          .map-header {
            flex-direction: column;
            gap: 16px;
          }
          
          .map-controls {
            flex-direction: column;
            align-items: stretch;
            gap: 16px;
          }
          
          .layer-toggles {
            justify-content: center;
            flex-wrap: wrap;
          }
        }
      `}</style>
    </div>
  );
};

export default MapPlanner;