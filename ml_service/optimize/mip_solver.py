from ortools.linear_solver import pywraplp
import numpy as np
from typing import Dict, List, Any
import time

def solve_allocation_mip(current_state: Dict, vfa_estimates: Dict, 
                        fleet: List[Dict], constraints: Dict = None) -> Dict:
    """
    Solve MIP for vehicle allocation using OR-Tools
    """
    start_time = time.time()
    
    # Create solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return _fallback_allocation(current_state, fleet)
    
    # Extract data
    districts = list(current_state.keys())
    vehicle_classes = [v['class'] for v in fleet]
    
    # Decision variables: x[district, vehicle_class]
    x = {}
    for d in districts:
        for v in vehicle_classes:
            x[d, v] = solver.IntVar(0, 10, f'x_{d}_{v}')
    
    # Constraints
    # Vehicle availability
    for v_info in fleet:
        v_class = v_info['class']
        available = v_info['count']
        solver.Add(sum(x[d, v_class] for d in districts) <= available)
    
    # User constraints
    if constraints:
        # Lock out districts
        if 'lock_out' in constraints:
            for district in constraints['lock_out']:
                if district in districts:
                    for v in vehicle_classes:
                        solver.Add(x[district, v] == 0)
        
        # Vehicle limits
        if 'vehicle_limits' in constraints:
            for v_class, limit in constraints['vehicle_limits'].items():
                if v_class in vehicle_classes:
                    solver.Add(sum(x[d, v_class] for d in districts) <= limit)
    
    # Objective function
    objective = solver.Objective()
    
    for d in districts:
        district_state = current_state[d]
        demand = district_state.get('demand_last_period', 0)
        backlog = district_state.get('backlog', 0)
        
        for v_info in fleet:
            v_class = v_info['class']
            capacity = v_info['capacity']
            
            # Transport cost (distance-based)
            transport_cost = 10.0  # Simplified
            
            # Deprivation penalty
            deprivation_penalty = max(0, (demand + backlog) - capacity) * 5
            
            # VFA future cost
            future_cost = vfa_estimates.get(d, 0) * 0.9  # Discount factor
            
            total_cost = transport_cost + deprivation_penalty + future_cost
            objective.SetCoefficient(x[d, v_class], total_cost)
    
    objective.SetMinimization()
    
    # Solve
    status = solver.Solve()
    solve_time = time.time() - start_time
    
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        # Extract solution
        allocations = []
        for d in districts:
            for v_info in fleet:
                v_class = v_info['class']
                count = int(x[d, v_class].solution_value())
                if count > 0:
                    # Calculate ETA based on distance and speed
                    eta = np.random.uniform(1.5, 4.0)  # Simplified
                    
                    allocations.append({
                        "district": d,
                        "truck_class": v_class,
                        "count": count,
                        "eta_hours": round(eta, 1)
                    })
        
        return {
            "allocations": allocations,
            "objective": solver.Objective().Value(),
            "solve_info": {
                "status": "optimal" if status == pywraplp.Solver.OPTIMAL else "feasible",
                "solve_time_s": round(solve_time, 2)
            }
        }
    
    else:
        return _fallback_allocation(current_state, fleet)

def _fallback_allocation(current_state: Dict, fleet: List[Dict]) -> Dict:
    """Simple fallback allocation when MIP fails"""
    allocations = []
    districts = list(current_state.keys())
    
    # Simple greedy allocation
    for i, district in enumerate(districts[:3]):  # Allocate to worst 3 districts
        if i < len(fleet):
            v_info = fleet[i]
            allocations.append({
                "district": district,
                "truck_class": v_info['class'],
                "count": 1,
                "eta_hours": 2.5
            })
    
    return {
        "allocations": allocations,
        "objective": 999.9,
        "solve_info": {
            "status": "fallback",
            "solve_time_s": 0.01
        }
    }