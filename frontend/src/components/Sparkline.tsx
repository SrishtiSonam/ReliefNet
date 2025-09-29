import React from 'react';

interface SparklineProps {
  data: number[];
  width: number;
  height: number;
  color?: string;
}

const Sparkline: React.FC<SparklineProps> = ({ 
  data, 
  width, 
  height, 
  color = '#667eea' 
}) => {
  if (!data || data.length === 0) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="sparkline-container" style={{ width, height }}>
      <svg width={width} height={height} className="sparkline">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <defs>
          <linearGradient id="sparkline-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <polyline
          points={`0,${height} ${points} ${width},${height}`}
          fill="url(#sparkline-gradient)"
          stroke="none"
        />
      </svg>
      
      <style jsx>{`
        .sparkline-container {
          position: relative;
        }
        
        .sparkline {
          display: block;
        }
      `}</style>
    </div>
  );
};

export default Sparkline;