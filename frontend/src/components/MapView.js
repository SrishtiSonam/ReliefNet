// components/MapView.js
const MapView = ({ districts, forecasts, recommendations }) => {
  const mapStyle = {
    width: '100%',
    height: '400px',
    backgroundColor: '#e5e7eb',
    position: 'relative',
    borderRadius: '8px',
    border: '2px solid #d1d5db'
  };

  const getDistrictColor = (district) => {
    if (district.backlog > 20) return '#ef4444'; // Red - critical
    if (district.backlog > 10) return '#f59e0b'; // Yellow - warning
    return '#10b981'; // Green - good
  };

  const getDistrictSize = (district) => {
    const forecast = forecasts[district.id] || {};
    const surgeProbability = forecast.surge_prob || 0;
    return Math.max(20, 20 + surgeProbability * 30);
  };

  return (
    <div style={mapStyle}>
      <div className="absolute inset-0 p-4">
        <div className="text-sm text-gray-600 mb-2">
          Interactive District Map (Simplified View)
        </div>
        
        <div className="grid grid-cols-2 gap-4 h-full">
          {districts.map((district, index) => {
            const isAllocated = recommendations?.allocations?.some(
              a => a.district === district.id
            );
            
            return (
              <div
                key={district.id}
                className="relative border-2 border-gray-300 rounded-lg p-3 bg-white hover:shadow-md transition-shadow"
                style={{
                  borderColor: getDistrictColor(district),
                  borderWidth: isAllocated ? '3px' : '2px'
                }}
              >
                <div className="font-semibold text-sm">{district.name}</div>
                <div className="text-xs text-gray-600 mt-1">
                  <div>Inventory: {district.inventory.toFixed(0)}</div>
                  <div>Backlog: {district.backlog.toFixed(0)}</div>
                  <div>
                    Surge Risk: {((forecasts[district.id]?.surge_prob || 0) * 100).toFixed(1)}%
                  </div>
                </div>
                
                {isAllocated && (
                  <div className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs px-2 py-1 rounded">
                    Allocated
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="absolute bottom-2 left-2 text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
              Good
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 rounded mr-1"></div>
              Warning
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
              Critical
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView ;