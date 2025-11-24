from environment import SimulationEnvironment
import sys
import os

# Add parent directory to path to import solver
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solver.mip_solver import DisasterReliefSolver

def run_demo():
    print("Initializing Simulation...")
    env = SimulationEnvironment(data_dir="../../data")
    
    # Static vehicle data
    vehicles = [{'type': 'Truck', 'capacity_kg': 5000}, {'type': 'UAV', 'capacity_kg': 20}]
    
    for i in range(5): # Run 5 steps
        print(f"\n--- Day {i+1} ---")
        state = env.step()
        if not state:
            break
            
        print(f"Inventory: {state['inventory']}")
        print(f"Total Demand: {sum(state['demand'].values())}")
        
        # Solve Allocation
        solver = DisasterReliefSolver(env.districts, vehicles, env.roads)
        allocation = solver.solve_allocation(state['demand'], state['inventory'])
        
        print(f"Allocated: {len(allocation)} shipments")
        for alloc in allocation[:3]: # Show first 3
            print(f"  -> {alloc['vehicle_type']} to District {alloc['district_id']}: {alloc['amount']} units")

if __name__ == "__main__":
    run_demo()
