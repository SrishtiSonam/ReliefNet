import pulp
import networkx as nx
from typing import Dict, List, Tuple, Any

class LogisticsOptimizer:
    """
    Real optimization engine for multi-period inventory planning, 
    vehicle scheduling, and route optimization.
    """
    def __init__(self, districts: List[str], warehouses: List[str], graph: nx.Graph):
        self.districts = districts
        self.warehouses = warehouses
        self.graph = graph
        
    def optimize_allocation(self, 
                            demands: Dict[str, float], 
                            inventory: Dict[str, float],
                            truck_capacity: float = 100.0,
                            uav_capacity: float = 10.0,
                            available_trucks: Dict[str, int] = None,
                            available_uavs: Dict[str, int] = None,
                            alpha: float = 1.0, # weight for suffering
                            beta: float = 0.5,  # weight for transport cost
                            gamma: float = 2.0  # weight for fairness
                           ) -> Dict[str, Any]:
        """
        Solves Mixed Integer Linear Program (MILP) to optimize relief allocation.
        """
        if available_trucks is None:
            available_trucks = {w: 5 for w in self.warehouses}
        if available_uavs is None:
            available_uavs = {w: 10 for w in self.warehouses}

        # Create LP Problem
        prob = pulp.LpProblem("ReliefNet_Allocation_Optimization", pulp.LpMinimize)
        
        # Decision Variables
        # x_w_d_t: trucks sent from warehouse w to district d
        x_trucks = pulp.LpVariable.dicts("Trucks",
                                         [(w, d) for w in self.warehouses for d in self.districts],
                                         lowBound=0, cat='Integer')
                                         
        # y_w_d_u: uavs sent from warehouse w to district d
        y_uavs = pulp.LpVariable.dicts("UAVs",
                                       [(w, d) for w in self.warehouses for d in self.districts],
                                       lowBound=0, cat='Integer')
                                       
        # Shortage at each district
        shortage = pulp.LpVariable.dicts("Shortage", self.districts, lowBound=0)
        
        # Max shortage (for min-max fairness)
        max_shortage = pulp.LpVariable("Max_Shortage", lowBound=0)
        
        # Precompute shortest paths and costs
        truck_costs = {}
        for w in self.warehouses:
            for d in self.districts:
                try:
                    # Trucks use road network, can fail if path broken
                    path_length = nx.shortest_path_length(self.graph, source=w, target=d, weight='weight')
                    truck_costs[(w, d)] = path_length
                except nx.NetworkXNoPath:
                    truck_costs[(w, d)] = 1e6 # Effectively infinite cost
                    
        # Objective Function
        # 1. Minimize total shortage (suffering)
        total_shortage = pulp.lpSum([shortage[d] for d in self.districts])
        
        # 2. Minimize transport cost
        total_transport_cost = pulp.lpSum([
            x_trucks[(w, d)] * truck_costs[(w, d)] * 1.0 + 
            y_uavs[(w, d)] * 2.5 # UAVs have a fixed/distance independent cost multiplier for simplicity, or euclidian
            for w in self.warehouses for d in self.districts
        ])
        
        # 3. Maximize fairness (minimize max_shortage)
        prob += alpha * total_shortage + beta * total_transport_cost + gamma * max_shortage
        
        # Constraints
        
        # 1. Flow conservation / Shortage definition
        for d in self.districts:
            delivered = pulp.lpSum([
                x_trucks[(w, d)] * truck_capacity + y_uavs[(w, d)] * uav_capacity
                for w in self.warehouses
            ])
            # Shortage is demand minus delivered. If delivered > demand, shortage = 0
            prob += shortage[d] >= demands.get(d, 0.0) - delivered
            # Fairness constraint: max_shortage must be >= every individual shortage
            prob += max_shortage >= shortage[d]
            
        # 2. Warehouse capacity constraints
        for w in self.warehouses:
            sent_goods = pulp.lpSum([
                x_trucks[(w, d)] * truck_capacity + y_uavs[(w, d)] * uav_capacity
                for d in self.districts
            ])
            prob += sent_goods <= inventory.get(w, 0.0)
            
        # 3. Vehicle availability constraints
        for w in self.warehouses:
            prob += pulp.lpSum([x_trucks[(w, d)] for d in self.districts]) <= available_trucks.get(w, 0)
            prob += pulp.lpSum([y_uavs[(w, d)] for d in self.districts]) <= available_uavs.get(w, 0)
            
        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Parse results
        allocation_plan = {
            "status": pulp.LpStatus[prob.status],
            "objective_value": pulp.value(prob.objective),
            "truck_allocations": {},
            "uav_allocations": {},
            "final_shortages": {}
        }
        
        for w in self.warehouses:
            for d in self.districts:
                truck_val = pulp.value(x_trucks[(w, d)])
                uav_val = pulp.value(y_uavs[(w, d)])
                if truck_val > 0:
                    allocation_plan["truck_allocations"][(w, d)] = truck_val
                if uav_val > 0:
                    allocation_plan["uav_allocations"][(w, d)] = uav_val
                    
        for d in self.districts:
            allocation_plan["final_shortages"][d] = pulp.value(shortage[d])
            
        return allocation_plan
