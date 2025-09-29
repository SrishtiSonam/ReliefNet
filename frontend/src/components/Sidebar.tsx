import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/map', label: 'Map Planner', icon: '🗺️' },
    { path: '/allocation', label: 'Allocation Console', icon: '⚡' },
    { path: '/fleet', label: 'Fleet & Roads', icon: '🚛' },
    { path: '/forecasts', label: 'Forecasts', icon: '📈' },
    { path: '/explainability', label: 'Explainability', icon: '🧠' },
    { path: '/scenarios', label: 'Scenarios & Stress Test', icon: '🎯' },
    { path: '/logs', label: 'Logs / Audit', icon: '📋' },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>
      
      <style jsx>{`
        .sidebar {
          width: 280px;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-right: 1px solid rgba(255, 255, 255, 0.2);
          padding: 24px 0;
          overflow-y: auto;
        }
        
        .sidebar-nav {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding: 0 16px;
        }
        
        .nav-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: 12px;
          text-decoration: none;
          color: #4a5568;
          font-weight: 500;
          transition: all 0.2s ease;
          position: relative;
        }
        
        .nav-item:hover {
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
          transform: translateX(4px);
        }
        
        .nav-item.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        
        .nav-item.active::before {
          content: '';
          position: absolute;
          left: -16px;
          top: 50%;
          transform: translateY(-50%);
          width: 4px;
          height: 24px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 0 2px 2px 0;
        }
        
        .nav-icon {
          font-size: 18px;
          min-width: 20px;
        }
        
        .nav-label {
          font-size: 14px;
          white-space: nowrap;
        }
        
        @media (max-width: 768px) {
          .sidebar {
            width: 100%;
            position: fixed;
            bottom: 0;
            left: 0;
            height: auto;
            padding: 16px 0;
            z-index: 1000;
            border-right: none;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
          }
          
          .sidebar-nav {
            flex-direction: row;
            overflow-x: auto;
            padding: 0 16px;
            gap: 8px;
          }
          
          .nav-item {
            flex-direction: column;
            gap: 4px;
            padding: 8px 12px;
            min-width: 80px;
            text-align: center;
          }
          
          .nav-label {
            font-size: 12px;
          }
          
          .nav-icon {
            font-size: 16px;
          }
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;