try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("Warning: OR-Tools not installed. Solver will not function.")

import numpy as np

class DisasterReliefSolver:
    def __init__(self, districts, vehicles, roads):
        self.districts = districts
        self.vehicles = vehicles
        self.roads = roads

    def solve_allocation(self, current_demand, available_inventory):
        """
        Solves the allocation problem for a single time step.
        current_demand: dict {district_id: amount}
        available_inventory: int (total units at depot)
        """
        if not ORTOOLS_AVAILABLE:
            print("OR-Tools not available. Returning empty allocation.")
            return []

        model = cp_model.CpModel()
        
        # Variables
        # x[v, d]: amount delivered by vehicle v to district d
        x = {} 
        # y[v, d]: binary, 1 if vehicle v visits district d
        y = {}
        
        num_vehicles = len(self.vehicles)
        num_districts = len(self.districts)
        
        for v in range(num_vehicles):
            for d in range(num_districts):
                x[v, d] = model.NewIntVar(0, 1000, f'x_{v}_{d}')
                y[v, d] = model.NewBoolVar(f'y_{v}_{d}')

        # Constraints
        
        # 1. Inventory Constraint
        total_delivered = sum(x[v, d] for v in range(num_vehicles) for d in range(num_districts))
        model.Add(total_delivered <= available_inventory)

        # 2. Vehicle Capacity
        for v in range(num_vehicles):
            capacity = self.vehicles[v]['capacity_kg']
            model.Add(sum(x[v, d] for d in range(num_districts)) <= capacity)
            
            # Link x and y
            for d in range(num_districts):
                model.Add(x[v, d] <= capacity * y[v, d])

        # 3. Demand Satisfaction (Soft constraint in objective, but let's try to meet as much as possible)
        # We minimize deprivation cost: sum of (demand - delivered) * urgency
        
        # Objective Function
        # Minimize Deprivation Cost + Transport Cost
        deprivation_cost = 0
        transport_cost = 0
        
        for d in range(num_districts):
            demand = current_demand.get(self.districts[d]['district_id'], 0)
            delivered_to_d = sum(x[v, d] for v in range(num_vehicles))
            
            # Simple linear penalty for unmet demand
            # In CP-SAT, we can't easily do max(0, demand - delivered) directly in objective without aux var
            # So we define unmet_var
            unmet = model.NewIntVar(0, 10000, f'unmet_{d}')
            model.Add(unmet >= demand - delivered_to_d)
            
            urgency = int(self.districts[d]['vulnerability_score'] * 100)
            deprivation_cost += unmet * urgency

        for v in range(num_vehicles):
            for d in range(num_districts):
                # Simplified transport cost: fixed cost per visit
                cost = 10 # Placeholder for distance-based cost
                transport_cost += y[v, d] * cost

        model.Minimize(deprivation_cost + transport_cost)

        # Solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        results = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for v in range(num_vehicles):
                for d in range(num_districts):
                    if solver.Value(x[v, d]) > 0:
                        results.append({
                            "vehicle_id": v,
                            "district_id": self.districts[d]['district_id'],
                            "amount": solver.Value(x[v, d]),
                            "vehicle_type": self.vehicles[v]['type']
                        })
        return results

if __name__ == "__main__":
    # Test
    districts = [{'district_id': 0, 'vulnerability_score': 0.8}, {'district_id': 1, 'vulnerability_score': 0.5}]
    vehicles = [{'type': 'Truck', 'capacity_kg': 100}, {'type': 'UAV', 'capacity_kg': 20}]
    roads = []
    solver = DisasterReliefSolver(districts, vehicles, roads)
    alloc = solver.solve_allocation({0: 50, 1: 30}, 200)
    print("Allocation:", alloc)
