import React from 'react';

const ForecastChart: React.FC = () => {
  // Mock data for 7 epochs
  const epochs = [1, 2, 3, 4, 5, 6, 7];
  const demandData = [8500, 9200, 12000, 10500, 9800, 11200, 9600];
  const supplyData = [10000, 9500, 8000, 11000, 10500, 9200, 10800];
  const surgeThreshold = 11000;

  const maxValue = Math.max(...demandData, ...supplyData, surgeThreshold);
  const chartHeight = 200;
  const chartWidth = 400;
  const padding = 40;

  const getY = (value: number) => {
    return chartHeight - ((value / maxValue) * (chartHeight - padding)) - padding/2;
  };

  const getX = (index: number) => {
    return (index / (epochs.length - 1)) * (chartWidth - padding) + padding/2;
  };

  const demandPath = demandData.map((value, index) => 
    `${index === 0 ? 'M' : 'L'} ${getX(index)} ${getY(value)}`
  ).join(' ');

  const supplyPath = supplyData.map((value, index) => 
    `${index === 0 ? 'M' : 'L'} ${getX(index)} ${getY(value)}`
  ).join(' ');

  return (
    <div className="forecast-chart">
      <svg width={chartWidth} height={chartHeight} className="chart-svg">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => (
          <line
            key={ratio}
            x1={padding/2}
            y1={getY(maxValue * ratio)}
            x2={chartWidth - padding/2}
            y2={getY(maxValue * ratio)}
            stroke="#e2e8f0"
            strokeWidth="1"
            strokeDasharray="3,3"
          />
        ))}
        
        {/* Surge threshold line */}
        <line
          x1={padding/2}
          y1={getY(surgeThreshold)}
          x2={chartWidth - padding/2}
          y2={getY(surgeThreshold)}
          stroke="#ff6b6b"
          strokeWidth="2"
          strokeDasharray="5,5"
        />
        
        {/* Surge area highlight */}
        <rect
          x={padding/2}
          y={padding/2}
          width={chartWidth - padding}
          height={getY(surgeThreshold) - padding/2}
          fill="#ff6b6b"
          fillOpacity="0.1"
        />
        
        {/* Supply area */}
        <path
          d={`${supplyPath} L ${getX(supplyData.length - 1)} ${chartHeight - padding/2} L ${getX(0)} ${chartHeight - padding/2} Z`}
          fill="#4caf50"
          fillOpacity="0.2"
        />
        
        {/* Demand area */}
        <path
          d={`${demandPath} L ${getX(demandData.length - 1)} ${chartHeight - padding/2} L ${getX(0)} ${chartHeight - padding/2} Z`}
          fill="#667eea"
          fillOpacity="0.2"
        />
        
        {/* Supply line */}
        <path
          d={supplyPath}
          fill="none"
          stroke="#4caf50"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Demand line */}
        <path
          d={demandPath}
          fill="none"
          stroke="#667eea"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Data points */}
        {demandData.map((value, index) => (
          <circle
            key={`demand-${index}`}
            cx={getX(index)}
            cy={getY(value)}
            r="4"
            fill="#667eea"
            stroke="white"
            strokeWidth="2"
          />
        ))}
        
        {supplyData.map((value, index) => (
          <circle
            key={`supply-${index}`}
            cx={getX(index)}
            cy={getY(value)}
            r="4"
            fill="#4caf50"
            stroke="white"
            strokeWidth="2"
          />
        ))}
        
        {/* X-axis labels */}
        {epochs.map((epoch, index) => (
          <text
            key={epoch}
            x={getX(index)}
            y={chartHeight - 10}
            textAnchor="middle"
            fontSize="12"
            fill="#718096"
          >
            E{epoch}
          </text>
        ))}
        
        {/* Y-axis labels */}
        {[0, 0.5, 1].map(ratio => (
          <text
            key={ratio}
            x={15}
            y={getY(maxValue * ratio) + 4}
            textAnchor="middle"
            fontSize="11"
            fill="#718096"
          >
            {Math.round(maxValue * ratio / 1000)}k
          </text>
        ))}
      </svg>
      
      <div className="chart-legend">
        <div className="legend-item">
          <div className="legend-color demand"></div>
          <span>Demand</span>
        </div>
        <div className="legend-item">
          <div className="legend-color supply"></div>
          <span>Supply Arrival</span>
        </div>
        <div className="legend-item">
          <div className="legend-color surge"></div>
          <span>Surge Threshold</span>
        </div>
      </div>
      
      <div className="chart-insights">
        <div className="insight-item">
          <span className="insight-label">Peak Demand:</span>
          <span className="insight-value">Epoch 3 (12,000 units)</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Supply Gap:</span>
          <span className="insight-value danger">-4,000 units</span>
        </div>
      </div>
      
      <style jsx>{`
        .forecast-chart {
          padding: 16px;
        }
        
        .chart-svg {
          width: 100%;
          height: auto;
          margin-bottom: 16px;
        }
        
        .chart-legend {
          display: flex;
          justify-content: center;
          gap: 24px;
          margin-bottom: 16px;
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
          height: 3px;
          border-radius: 2px;
        }
        
        .legend-color.demand {
          background: #667eea;
        }
        
        .legend-color.supply {
          background: #4caf50;
        }
        
        .legend-color.surge {
          background: #ff6b6b;
        }
        
        .chart-insights {
          display: flex;
          justify-content: space-around;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .insight-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          text-align: center;
        }
        
        .insight-label {
          font-size: 12px;
          color: #718096;
          font-weight: 500;
        }
        
        .insight-value {
          font-size: 14px;
          font-weight: 600;
          color: #4a5568;
        }
        
        .insight-value.danger {
          color: #e53e3e;
        }
      `}</style>
    </div>
  );
};

export default ForecastChart;