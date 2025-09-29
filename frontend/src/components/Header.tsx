import React from 'react';
import { scenarios } from '../data/hardcodedData';

interface HeaderProps {
  currentEpoch: number;
  currentScenario: string;
  onScenarioChange: (scenario: string) => void;
}

const Header: React.FC<HeaderProps> = ({ 
  currentEpoch, 
  currentScenario, 
  onScenarioChange 
}) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">🚁</div>
            <span className="logo-text">HumanitarianAI</span>
          </div>
        </div>
        
        <div className="header-center">
          <h1 className="page-title">Resource Allocation System</h1>
        </div>
        
        <div className="header-right">
          <div className="header-controls">
            <div className="time-control">
              <span className="epoch-label">Epoch {currentEpoch.toString().padStart(2, '0')}</span>
              <span className="epoch-time">2025-09-28 12:00</span>
            </div>
            
            <select 
              value={currentScenario}
              onChange={(e) => onScenarioChange(e.target.value)}
              className="scenario-select"
            >
              {scenarios.map(scenario => (
                <option key={scenario.id} value={scenario.id}>
                  {scenario.name}
                </option>
              ))}
            </select>
            
            <div className="user-info">
              <span className="user-role">Planner</span>
              <div className="user-avatar">JP</div>
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .header {
          background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
          color: white;
          padding: 16px 24px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .header-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .header-left {
          flex: 1;
        }
        
        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .logo-icon {
          font-size: 24px;
        }
        
        .logo-text {
          font-size: 18px;
          font-weight: 700;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .header-center {
          flex: 2;
          text-align: center;
        }
        
        .page-title {
          font-size: 20px;
          font-weight: 600;
          margin: 0;
        }
        
        .header-right {
          flex: 1;
          display: flex;
          justify-content: flex-end;
        }
        
        .header-controls {
          display: flex;
          align-items: center;
          gap: 24px;
        }
        
        .time-control {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }
        
        .epoch-label {
          font-weight: 600;
          font-size: 14px;
        }
        
        .epoch-time {
          font-size: 12px;
          opacity: 0.8;
        }
        
        .scenario-select {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          color: white;
          padding: 8px 16px;
          font-size: 14px;
          cursor: pointer;
          backdrop-filter: blur(10px);
        }
        
        .scenario-select option {
          background: #2d3748;
          color: white;
        }
        
        .user-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .user-role {
          font-size: 14px;
          opacity: 0.8;
        }
        
        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
        }
        
        @media (max-width: 768px) {
          .header-content {
            flex-direction: column;
            gap: 16px;
          }
          
          .header-left,
          .header-center,
          .header-right {
            flex: none;
          }
          
          .header-controls {
            gap: 16px;
          }
        }
      `}</style>