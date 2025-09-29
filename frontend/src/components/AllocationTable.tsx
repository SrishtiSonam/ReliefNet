import React from 'react';
import { District } from '../data/hardcodedData';

interface AllocationData {
  districtId: string;
  truckUnits: number;
  truckQuantity: number;
  uavUnits: number;
  uavQuantity: number;
  totalUnits: number;
  locked: boolean;
}

interface AllocationTableProps {
  allocations: AllocationData[];
  districts: District[];
  onAllocationChange: (districtId: string, field: string, value: number) => void;
  onLockToggle: (districtId: string) => void;
}

const AllocationTable: React.FC<AllocationTableProps> = ({
  allocations,
  districts,
  onAllocationChange,
  onLockToggle
}) => {
  const getDistrictData = (districtId: string) => {
    return districts.find(d => d.id === districtId)!;
  };

  const getCoveragePercentage = (allocation: AllocationData, district: District) => {
    const coverage = (allocation.totalUnits / Math.max(district.htn, 1)) * 100;
    return Math.min(coverage, 100);
  };

  return (
    <div className="allocation-table-container">
      <div className="table-wrapper">
        <table className="allocation-table">
          <thead>
            <tr>
              <th>District</th>
              <th>Current Need</th>
              <th>Trucks</th>
              <th>UAVs</th>
              <th>Total Units</th>
              <th>Coverage</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {allocations.map(allocation => {
              const district = getDistrictData(allocation.districtId);
              const coverage = getCoveragePercentage(allocation, district);
              
              return (
                <tr 
                  key={allocation.districtId}
                  className={allocation.locked ? 'locked-row' : ''}
                >
                  <td className="district-cell">
                    <div className="district-info">
                      <span className="district-name">{district.name}</span>
                      <span className="district-id">({district.id})</span>
                    </div>
                  </td>
                  
                  <td className="need-cell">
                    <div className="need-info">
                      <div className="shortage">{district.htn.toLocaleString()}</div>
                      <div className="deprivation-cost">
                        Cost: {district.deprivation_cost.toFixed(2)}
                      </div>
                    </div>
                  </td>
                  
                  <td className="vehicle-cell">
                    <div className="vehicle-input-group">
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={allocation.truckUnits}
                        onChange={(e) => onAllocationChange(
                          allocation.districtId, 
                          'truckUnits', 
                          parseInt(e.target.value) || 0
                        )}
                        disabled={allocation.locked}
                        className="vehicle-input"
                      />
                      <span className="vehicle-label">trucks</span>
                      <div className="quantity-display">
                        {allocation.truckQuantity.toLocaleString()} units
                      </div>
                    </div>
                  </td>
                  
                  <td className="vehicle-cell">
                    <div className="vehicle-input-group">
                      <input
                        type="number"
                        min="0"
                        max="15"
                        value={allocation.uavUnits}
                        onChange={(e) => onAllocationChange(
                          allocation.districtId, 
                          'uavUnits', 
                          parseInt(e.target.value) || 0
                        )}
                        disabled={allocation.locked}
                        className="vehicle-input"
                      />
                      <span className="vehicle-label">UAVs</span>
                      <div className="quantity-display">
                        {allocation.uavQuantity.toLocaleString()} units
                      </div>
                    </div>
                  </td>
                  
                  <td className="total-cell">
                    <div className="total-units">
                      {allocation.totalUnits.toLocaleString()}
                    </div>
                  </td>
                  
                  <td className="coverage-cell">
                    <div className="coverage-display">
                      <div className="coverage-percentage">
                        {coverage.toFixed(1)}%
                      </div>
                      <div className="coverage-bar">
                        <div 
                          className="coverage-fill"
                          style={{ 
                            width: `${coverage}%`,
                            backgroundColor: coverage >= 100 ? '#4caf50' : 
                                           coverage >= 80 ? '#ff8c00' : '#e53e3e'
                          }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  
                  <td className="actions-cell">
                    <button
                      className={`lock-button ${allocation.locked ? 'locked' : 'unlocked'}`}
                      onClick={() => onLockToggle(allocation.districtId)}
                      title={allocation.locked ? 'Unlock allocation' : 'Lock allocation'}
                    >
                      {allocation.locked ? '🔒' : '🔓'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      <div className="table-summary">
        <div className="summary-item">
          <span>Total Allocations:</span>
          <span>{allocations.reduce((sum, a) => sum + a.totalUnits, 0).toLocaleString()} units</span>
        </div>
        <div className="summary-item">
          <span>Locked Districts:</span>
          <span>{allocations.filter(a => a.locked).length}</span>
        </div>
        <div className="summary-item">
          <span>Avg Coverage:</span>
          <span>
            {(allocations.reduce((sum, a) => {
              const district = getDistrictData(a.districtId);
              return sum + getCoveragePercentage(a, district);
            }, 0) / allocations.length).toFixed(1)}%
          </span>
        </div>
      </div>
      
      <style jsx>{`
        .allocation-table-container {
          width: 100%;
        }
        
        .table-wrapper {
          overflow-x: auto;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
        }
        
        .allocation-table {
          width: 100%;
          border-collapse: collapse;
          background: white;
        }
        
        .allocation-table th {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 16px 12px;
          text-align: left;
          font-weight: 600;
          font-size: 14px;
          border: none;
        }
        
        .allocation-table td {
          padding: 16px 12px;
          border-bottom: 1px solid #e2e8f0;
          vertical-align: top;
        }
        
        .allocation-table tr:hover {
          background: rgba(102, 126, 234, 0.05);
        }
        
        .locked-row {
          background: rgba(255, 193, 7, 0.1) !important;
          border-left: 4px solid #ffc107;
        }
        
        .district-cell {
          min-width: 140px;
        }
        
        .district-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .district-name {
          font-weight: 600;
          color: #1a202c;
          font-size: 14px;
        }
        
        .district-id {
          font-size: 12px;
          color: #718096;
        }
        
        .need-cell {
          min-width: 120px;
        }
        
        .need-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .shortage {
          font-weight: 600;
          color: #e53e3e;
          font-size: 14px;
        }
        
        .deprivation-cost {
          font-size: 12px;
          color: #718096;
        }
        
        .vehicle-cell {
          min-width: 120px;
        }
        
        .vehicle-input-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .vehicle-input {
          width: 60px;
          padding: 6px 8px;
          border: 2px solid #e2e8f0;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          text-align: center;
        }
        
        .vehicle-input:focus {
          outline: none;
          border-color: #667eea;
        }
        
        .vehicle-input:disabled {
          background: #f7fafc;
          color: #a0aec0;
          cursor: not-allowed;
        }
        
        .vehicle-label {
          font-size: 12px;
          color: #718096;
          font-weight: 500;
        }
        
        .quantity-display {
          font-size: 11px;
          color: #667eea;
          font-weight: 500;
        }
        
        .total-cell {
          text-align: center;
        }
        
        .total-units {
          font-size: 16px;
          font-weight: 700;
          color: #1a202c;
        }
        
        .coverage-cell {
          min-width: 100px;
        }
        
        .coverage-display {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .coverage-percentage {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
        }
        
        .coverage-bar {
          width: 60px;
          height: 6px;
          background: #e2e8f0;
          border-radius: 3px;
          overflow: hidden;
        }
        
        .coverage-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.3s ease;
        }
        
        .actions-cell {
          text-align: center;
        }
        
        .lock-button {
          background: none;
          border: 2px solid #e2e8f0;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          cursor: pointer;
          font-size: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        
        .lock-button:hover {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.1);
        }
        
        .lock-button.locked {
          border-color: #ffc107;
          background: rgba(255, 193, 7, 0.1);
        }
        
        .table-summary {
          display: flex;
          justify-content: space-around;
          padding: 16px;
          background: #f7fafc;
          border-top: 1px solid #e2e8f0;
          margin-top: -1px;
          border-radius: 0 0 8px 8px;
        }
        
        .summary-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          text-align: center;
          font-size: 14px;
        }
        
        .summary-item span:first-child {
          color: #718096;
          font-weight: 500;
        }
        
        .summary-item span:last-child {
          color: #1a202c;
          font-weight: 600;
        }
        
        @media (max-width: 768px) {
          .allocation-table {
            font-size: 12px;
          }
          
          .allocation-table th,
          .allocation-table td {
            padding: 8px 6px;
          }
          
          .vehicle-input {
            width: 50px;
            font-size: 12px;
          }
          
          .table-summary {
            flex-direction: column;
            gap: 12px;
          }
          
          .summary-item {
            flex-direction: row;
            justify-content: space-between;
          }
        }
      `}</style>
    </div>
  );
};

export default AllocationTable;