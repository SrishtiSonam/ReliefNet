import React, { useState } from 'react';
import { districts, vehicleClasses, globalData } from '../data/hardcodedData';
import AllocationTable from '../components/AllocationTable';
import StatePanel from '../components/StatePanel';
import ConstraintsPanel from '../components/ConstraintsPanel';

interface AllocationData {
  districtId: string;
  truckUnits: number;
  truckQuantity: number;
  uavUnits: number;
  uavQuantity: number;
  totalUnits: number;
  locked: boolean;
}

const AllocationConsole: React.FC = () => {
  const [allocations, setAllocations] = useState<AllocationData[]>(
    districts.map(district => ({
      districtId: district.id,
      truckUnits: district.suggested_truck_units,
      truckQuantity: district.suggested_truck_quantity,
      uavUnits: district.suggested_UAV_units,
      uavQuantity: district.suggested_UAV_quantity,
      totalUnits: district.suggested_truck_quantity + district.suggested_UAV_quantity,
      locked: false
    }))
  );

  const [constraints, setConstraints] = useState({
    maxTrucks: 8,
    maxUAVs: 12,
    priorityDistricts: [] as string[],
    minAllocationThreshold: 0
  });

  const [isOptimizing, setIsOptimizing] = useState(false);
  const [lastOptimization, setLastOptimization] = useState<string | null>(null);

  const handleRunVFA = async () => {
    setIsOptimizing(true);
    // Simulate VFA + MIP optimization
    setTimeout(() => {
      // Mock optimization: slightly adjust allocations based on deprivation costs
      const newAllocations = allocations.map(allocation => {
        if (allocation.locked) return allocation;
        
        const district = districts.find(d => d.id === allocation.districtId)!;
        const deprivationWeight = district.deprivation_cost / 6; // Normalize
        
        // Simple heuristic: higher deprivation gets more allocation
        const adjustmentFactor = 0.8 + (deprivationWeight * 0.4);
        
        const newTruckUnits = Math.max(0, Math.round(allocation.truckUnits * adjustmentFactor));
        const newUAVUnits = Math.max(0, Math.round(allocation.uavUnits * adjustmentFactor));
        
        return {
          ...allocation,
          truckUnits: newTruckUnits,
          truckQuantity: newTruckUnits * 5000,
          uavUnits: newUAVUnits,
          uavQuantity: newUAVUnits * 200,
          totalUnits: (newTruckUnits * 5000) + (newUAVUnits * 200)
        };
      });
      
      setAllocations(newAllocations);
      setIsOptimizing(false);
      setLastOptimization(new Date().toLocaleTimeString());
    }, 3000);
  };

  const handleConstrainedReOptimize = () => {
    // Simple constraint-based reallocation
    const availableTrucks = constraints.maxTrucks;
    const availableUAVs = constraints.maxUAVs;
    
    let usedTrucks = 0;
    let usedUAVs = 0;
    
    const newAllocations = allocations.map(allocation => {
      if (allocation.locked) {
        usedTrucks += allocation.truckUnits;
        usedUAVs += allocation.uavUnits;
        return allocation;
      }
      return { ...allocation, truckUnits: 0, uavUnits: 0, truckQuantity: 0, uavQuantity: 0, totalUnits: 0 };
    });

    // Sort districts by priority (deprivation cost)
    const priorityOrder = districts
      .filter(d => !allocations.find(a => a.districtId === d.id)?.locked)
      .sort((a, b) => b.deprivation_cost - a.deprivation_cost);

    // Allocate remaining vehicles
    priorityOrder.forEach(district => {
      const allocation = newAllocations.find(a => a.districtId === district.id)!;
      
      // Allocate trucks first for high capacity needs
      if (district.htn > 1000 && usedTrucks < availableTrucks) {
        const trucksNeeded = Math.min(Math.ceil(district.htn / 5000), availableTrucks - usedTrucks);
        allocation.truckUnits = trucksNeeded;
        allocation.truckQuantity = trucksNeeded * 5000;
        usedTrucks += trucksNeeded;
      }
      
      // Fill remaining with UAVs
      const remainingNeed = Math.max(0, district.htn - allocation.truckQuantity);
      if (remainingNeed > 0 && usedUAVs < availableUAVs) {
        const uavsNeeded = Math.min(Math.ceil(remainingNeed / 200), availableUAVs - usedUAVs);
        allocation.uavUnits = uavsNeeded;
        allocation.uavQuantity = uavsNeeded * 200;
        usedUAVs += uavsNeeded;
      }
      
      allocation.totalUnits = allocation.truckQuantity + allocation.uavQuantity;
    });

    setAllocations(newAllocations);
  };

  const handleAllocationChange = (districtId: string, field: string, value: number) => {
    setAllocations(prev => prev.map(allocation => {
      if (allocation.districtId !== districtId) return allocation;
      
      const updated = { ...allocation, [field]: value };
      
      // Recalculate derived values
      if (field === 'truckUnits') {
        updated.truckQuantity = value * 5000;
      } else if (field === 'uavUnits') {
        updated.uavQuantity = value * 200;
      }
      
      updated.totalUnits = updated.truckQuantity + updated.uavQuantity;
      
      return updated;
    }));
  };

  const handleLockToggle = (districtId: string) => {
    setAllocations(prev => prev.map(allocation => 
      allocation.districtId === districtId 
        ? { ...allocation, locked: !allocation.locked }
        : allocation
    ));
  };

  const getTotalVehiclesUsed = () => {
    return {
      trucks: allocations.reduce((sum, a) => sum + a.truckUnits, 0),
      uavs: allocations.reduce((sum, a) => sum + a.uavUnits, 0),
      totalUnits: allocations.reduce((sum, a) => sum + a.totalUnits, 0)
    };
  };

  const totals = getTotalVehiclesUsed();

  return (
    <div className="allocation-console">
      <div className="console-header">
        <div>
          <h1 className="page-title">Allocation Console</h1>
          <p className="page-subtitle">Human-in-the-loop resource allocation with VFA optimization</p>
        </div>
        
        <div className="console-actions">
          <button 
            className="btn-primary"
            onClick={handleRunVFA}
            disabled={isOptimizing}
          >
            {isOptimizing ? 'Optimizing...' : 'Run VFA + MIP'}
          </button>
          <button 
            className="btn-secondary"
            onClick={handleConstrainedReOptimize}
          >
            Constrained Re-optimize
          </button>
        </div>
      </div>

      {lastOptimization && (
        <div className="optimization-status">
          <span className="status-icon">✅</span>
          <span>Last optimization completed at {lastOptimization}</span>
        </div>
      )}

      <div className="console-content">
        <div className="left-panel">
          <StatePanel />
          
          <div className="totals-card card">
            <div className="card-header">
              <h3 className="card-title">Resource Summary</h3>
            </div>
            <div className="totals-grid">
              <div className="total-item">
                <span className="total-label">Total Trucks:</span>
                <span className={`total-value ${totals.trucks > constraints.maxTrucks ? 'over-limit' : ''}`}>
                  {totals.trucks} / {constraints.maxTrucks}
                </span>
              </div>
              <div className="total-item">
                <span className="total-label">Total UAVs:</span>
                <span className={`total-value ${totals.uavs > constraints.maxUAVs ? 'over-limit' : ''}`}>
                  {totals.uavs} / {constraints.maxUAVs}
                </span>
              </div>
              <div className="total-item">
                <span className="total-label">Total Units:</span>
                <span className="total-value">{totals.totalUnits.toLocaleString()}</span>
              </div>
              <div className="total-item">
                <span className="total-label">Warehouse Stock:</span>
                <span className={`total-value ${totals.totalUnits > globalData.ICW ? 'over-limit' : ''}`}>
                  {globalData.ICW.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="center-panel">
          <div className="card allocation-table-card">
            <div className="card-header">
              <h3 className="card-title">District Allocations</h3>
              <p className="card-subtitle">Modify allocations or lock constraints</p>
            </div>
            <AllocationTable 
              allocations={allocations}
              districts={districts}
              onAllocationChange={handleAllocationChange}
              onLockToggle={handleLockToggle}
            />
          </div>
        </div>

        <div className="right-panel">
          <ConstraintsPanel 
            constraints={constraints}
            onConstraintsChange={setConstraints}
          />
          
          <div className="card rounding-preview">
            <div className="card-header">
              <h3 className="card-title">Rounding Preview</h3>
              <p className="card-subtitle">Fractional to integer conversion</p>
            </div>
            <div className="rounding-content">
              <div className="rounding-note">
                <p>All allocations are automatically rounded to integer vehicle counts:</p>
                <ul>
                  <li>Truck capacity: 5,000 units</li>
                  <li>UAV-Short capacity: 200 units</li>
                  <li>UAV-Long capacity: 500 units</li>
                </ul>
              </div>
              
              <div className="rounding-impact">
                <div className="impact-item">
                  <span>Transportation Cost Change:</span>
                  <span className="cost-change">+2.3%</span>
                </div>
                <div className="impact-item">
                  <span>Coverage Efficiency:</span>
                  <span className="efficiency">94.7%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .allocation-console {
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .console-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }
        
        .console-header h1 {
          font-size: 28px;
          font-weight: 700;
          color: #1a202c;
          margin-bottom: 8px;
        }
        
        .console-header p {
          color: #718096;
          font-size: 16px;
        }
        
        .console-actions {
          display: flex;
          gap: 16px;
        }
        
        .optimization-status {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: rgba(76, 175, 80, 0.1);
          border: 1px solid rgba(76, 175, 80, 0.3);
          border-radius: 8px;
          margin-bottom: 24px;
          color: #4caf50;
          font-weight: 500;
        }
        
        .status-icon {
          font-size: 16px;
        }
        
        .console-content {
          display: grid;
          grid-template-columns: 300px 1fr 300px;
          gap: 24px;
        }
        
        .left-panel,
        .right-panel {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .allocation-table-card {
          height: fit-content;
        }
        
        .totals-card {
          margin-top: 24px;
        }
        
        .totals-grid {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .total-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 14px;
        }
        
        .total-label {
          color: #718096;
          font-weight: 500;
        }
        
        .total-value {
          font-weight: 600;
          color: #4a5568;
        }
        
        .total-value.over-limit {
          color: #e53e3e;
          font-weight: 700;
        }
        
        .rounding-preview {
          margin-top: 24px;
        }
        
        .rounding-content {
          font-size: 14px;
        }
        
        .rounding-note {
          margin-bottom: 16px;
          color: #4a5568;
        }
        
        .rounding-note ul {
          margin-top: 8px;
          margin-left: 16px;
          color: #718096;
        }
        
        .rounding-note li {
          margin-bottom: 4px;
        }
        
        .rounding-impact {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .impact-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .impact-item span:first-child {
          color: #718096;
        }
        
        .cost-change {
          color: #ff8c00;
          font-weight: 600;
        }
        
        .efficiency {
          color: #4caf50;
          font-weight: 600;
        }
        
        @media (max-width: 1200px) {
          .console-content {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          
          .left-panel,
          .right-panel {
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            flex-direction: row;
          }
        }
        
        @media (max-width: 768px) {
          .console-header {
            flex-direction: column;
            gap: 16px;
          }
          
          .console-actions {
            flex-direction: column;
            width: 100%;
          }
          
          .left-panel,
          .right-panel {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default AllocationConsole;