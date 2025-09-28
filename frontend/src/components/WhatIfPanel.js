// components/WhatIfPanel.js
import React, { useState } from 'react';

const WhatIfPanel = ({ onConstraintsChange, districts, fleet }) => {
  const [lockOutDistricts, setLockOutDistricts] = useState([]);
  const [vehicleLimits, setVehicleLimits] = useState({});

  const handleLockOutChange = (districtId, checked) => {
    const newLockOut = checked 
      ? [...lockOutDistricts, districtId]
      : lockOutDistricts.filter(id => id !== districtId);
    
    setLockOutDistricts(newLockOut);
    updateConstraints(newLockOut, vehicleLimits);
  };

  const handleVehicleLimitChange = (vehicleClass, limit) => {
    const newLimits = { ...vehicleLimits, [vehicleClass]: parseInt(limit) || 0 };
    setVehicleLimits(newLimits);
    updateConstraints(lockOutDistricts, newLimits);
  };

  const updateConstraints = (lockOut, limits) => {
    const constraints = {};
    
    if (lockOut.length > 0) {
      constraints.lock_out = lockOut;
    }
    
    const validLimits = Object.entries(limits).filter(([_, limit]) => limit > 0);
    if (validLimits.length > 0) {
      constraints.vehicle_limits = Object.fromEntries(validLimits);
    }
    
    onConstraintsChange(constraints);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h3 className="text-lg font-semibold mb-3">What-If Analysis</h3>
      
      <div className="space-y-4">
        <div>
          <div className="text-sm font-medium mb-2">Lock Out Districts:</div>
          <div className="space-y-1">
            {districts.map(district => (
              <label key={district.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={lockOutDistricts.includes(district.id)}
                  onChange={(e) => handleLockOutChange(district.id, e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm">{district.name}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <div className="text-sm font-medium mb-2">Vehicle Limits:</div>
          <div className="space-y-2">
            {fleet.map(vehicle => (
              <div key={vehicle.class} className="flex items-center">
                <label className="text-sm flex-1">{vehicle.class}:</label>
                <input
                  type="number"
                  min="0"
                  max={vehicle.count}
                  placeholder={`Max ${vehicle.count}`}
                  onChange={(e) => handleVehicleLimitChange(vehicle.class, e.target.value)}
                  className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={() => {
            setLockOutDistricts([]);
            setVehicleLimits({});
            onConstraintsChange({});
          }}
          className="w-full bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded transition-colors"
        >
          Reset Constraints
        </button>
      </div>
    </div>
  );
};

export default WhatIfPanel;