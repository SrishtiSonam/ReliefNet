import React from 'react';
import { districts } from '../data/hardcodedData';

interface Constraints {
  maxTrucks: number;
  maxUAVs: number;
  priorityDistricts: string[];
  minAllocationThreshold: number;
}

interface ConstraintsPanelProps {
  constraints: Constraints;
  onConstraintsChange: (constraints: Constraints) => void;
}

const ConstraintsPanel: React.FC<ConstraintsPanelProps> = ({
  constraints,
  onConstraintsChange
}) => {
  const handleConstraintChange = (field: keyof Constraints, value: any) => {
    onConstraintsChange({
      ...constraints,
      [field]: value
    });
  };

  const handlePriorityToggle = (districtId: string) => {
    const newPriorities = constraints.priorityDistricts.includes(districtId)
      ? constraints.priorityDistricts.filter(id => id !== districtId)
      : [...constraints.priorityDistricts, districtId];
    
    handleConstraintChange('priorityDistricts', newPriorities);
  };

  return (
    <div className="card constraints-panel">
      <div className="card-header">
        <h3 className="card-title">What-If Constraints</h3>
        <p className="card-subtitle">Modify optimization parameters</p>
      </div>
      
      <div className="constraints-content">
        <div className="constraint-section">
          <h4 className="constraint-title">Vehicle Limits</h4>
          <div className="constraint-controls">
            <div className="control-group">
              <label className="control-label">Maximum Trucks:</label>
              <input
                type="number"
                min="1"
                max="20"
                value={constraints.maxTrucks}
                onChange={(e) => handleConstraintChange('maxTrucks', parseInt(e.target.value) || 1)}
                className="control-input"
              />
            </div>
            
            <div className="control-group">
              <label className="control-label">Maximum UAVs:</label>
              <input
                type="number"
                min="1"
                max="30"
                value={constraints.maxUAVs}
                onChange={(e) => handleConstraintChange('maxUAVs', parseInt(e.target.value) || 1)}
                className="control-input"
              />
            </div>
          </div>
        </div>

        <div className="constraint-section">
          <h4 className="constraint-title">Priority Districts</h4>
          <div className="priority-list">
            {districts.map(district => (
              <label key={district.id} className="priority-item">
                <input
                  type="checkbox"
                  checked={constraints.priorityDistricts.includes(district.id)}
                  onChange={() => handlePriorityToggle(district.id)}
                  className="priority-checkbox"
                />
                <div className="priority-info">
                  <span className="priority-name">{district.name}</span>
                  <span className="priority-meta">
                    Cost: {district.deprivation_cost.toFixed(2)} | 
                    Need: {district.htn.toLocaleString()}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="constraint-section">
          <h4 className="constraint-title">Allocation Thresholds</h4>
          <div className="constraint-controls">
            <div className="control-group">
              <label className="control-label">Min Allocation Threshold:</label>
              <input
                type="number"
                min="0"
                max="5000"
                step="100"
                value={constraints.minAllocationThreshold}
                onChange={(e) => handleConstraintChange('minAllocationThreshold', parseInt(e.target.value) || 0)}
                className="control-input"
              />
              <small className="control-help">
                Skip districts with shortage below this threshold
              </small>
            </div>
          </div>
        </div>

        <div className="constraint-section">
          <h4 className="constraint-title">Optimization Settings</h4>
          <div className="optimization-toggles">
            <label className="toggle-option">
              <input type="checkbox" defaultChecked />
              <span>Minimize deprivation cost g(δ)</span>
            </label>
            <label className="toggle-option">
              <input type="checkbox" defaultChecked />
              <span>Consider transportation costs</span>
            </label>
            <label className="toggle-option">
              <input type="checkbox" defaultChecked />
              <span>Apply capacity constraints</span>
            </label>
            <label className="toggle-option">
              <input type="checkbox" />
              <span>Enforce minimum safety stock</span>
            </label>
          </div>
        </div>

        <div className="constraint-actions">
          <button className="btn-primary constraint-btn">
            Apply Constraints
          </button>
          <button 
            className="btn-secondary constraint-btn"
            onClick={() => onConstraintsChange({
              maxTrucks: 8,
              maxUAVs: 12,
              priorityDistricts: [],
              minAllocationThreshold: 0
            })}
          >
            Reset to Default
          </button>
        </div>
      </div>
      
      <style jsx>{`
        .constraints-panel {
          height: fit-content;
        }
        
        .constraints-content {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .constraint-section {
          border-bottom: 1px solid #e2e8f0;
          padding-bottom: 20px;
        }
        
        .constraint-section:last-child {
          border-bottom: none;
          padding-bottom: 0;
        }
        
        .constraint-title {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
          margin-bottom: 12px;
        }
        
        .constraint-controls {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .control-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .control-label {
          font-size: 13px;
          font-weight: 500;
          color: #718096;
        }
        
        .control-input {
          padding: 8px 12px;
          border: 2px solid #e2e8f0;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
        }
        
        .control-input:focus {
          outline: none;
          border-color: #667eea;
        }
        
        .control-help {
          font-size: 12px;
          color: #a0aec0;
          font-style: italic;
        }
        
        .priority-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          max-height: 200px;
          overflow-y: auto;
        }
        
        .priority-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px;
          border-radius: 6px;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .priority-item:hover {
          background: rgba(102, 126, 234, 0.05);
        }
        
        .priority-checkbox {
          width: 16px;
          height: 16px;
          accent-color: #667eea;
        }
        
        .priority-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
          flex: 1;
        }
        
        .priority-name {
          font-size: 13px;
          font-weight: 500;
          color: #1a202c;
        }
        
        .priority-meta {
          font-size: 11px;
          color: #718096;
        }
        
        .optimization-toggles {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .toggle-option {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          font-size: 13px;
          color: #4a5568;
        }
        
        .toggle-option input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: #667eea;
        }
        
        .constraint-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .constraint-btn {
          width: 100%;
          padding: 12px;
          font-weight: 600;
          text-align: center;
        }
      `}</style>
    </div>
  );
};

export default ConstraintsPanel;