"""
Action space for Approximate Dynamic Programming
Defines feasible actions for resource allocation
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Action:
    """
    Action: Allocate resources from warehouse to zone
    
    Attributes:
        warehouse_id: Source warehouse
        zone_id: Destination zone
        resources: Dict of resource_type -> quantity
        vehicle_type: 'truck' or 'uav'
        priority: Action priority (higher = more urgent)
    """
    warehouse_id: str
    zone_id: str
    resources: Dict[str, float]
    vehicle_type: str
    priority: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary"""
        return {
            'warehouse_id': self.warehouse_id,
            'zone_id': self.zone_id,
            'resources': self.resources,
            'vehicle_type': self.vehicle_type,
            'priority': self.priority
        }
    
    def __repr__(self):
        total_weight = sum(self.resources.values())
        return f"Action({self.warehouse_id}->{self.zone_id}, {total_weight:.0f}kg, {self.vehicle_type})"


def generate_feasible_actions(state, warehouses: List[Dict], 
                              max_actions: int = 20) -> List[Action]:
    """
    Generate feasible actions from current state
    
    Args:
        state: Current State object
        warehouses: List of warehouse dictionaries
        max_actions: Maximum number of actions to generate
    
    Returns:
        List of feasible Action objects
    """
    actions = []
    
    # Get zones with demand
    zones_with_demand = [zone_id for zone_id, demand in state.demand.items() 
                        if sum(demand.values()) > 0]
    
    if not zones_with_demand:
        return []
    
    # For each warehouse, generate actions to high-demand zones
    for warehouse in warehouses[:3]:  # Limit to top 3 warehouses
        warehouse_id = warehouse['warehouse_id']
        
        # For each zone with demand
        for zone_id in zones_with_demand[:5]:  # Top 5 zones
            zone_demand = state.demand[zone_id]
            
            # Determine vehicle type based on demand size
            total_demand = sum(zone_demand.values())
            
            if total_demand > 1000:
                vehicle_type = 'truck'
                capacity = 5000  # kg
            else:
                vehicle_type = 'uav'
                capacity = 50  # kg
            
            # Check vehicle availability
            if state.vehicles_available.get(vehicle_type, 0) == 0:
                continue
            
            # Allocate resources up to capacity
            allocated_resources = {}
            remaining_capacity = capacity
            
            for resource_type, demand_qty in zone_demand.items():
                available = state.inventory.get(resource_type, 0)
                allocate = min(demand_qty, available, remaining_capacity)
                
                if allocate > 0:
                    allocated_resources[resource_type] = allocate
                    remaining_capacity -= allocate
            
            if allocated_resources:
                # Calculate priority based on urgency and risk
                priority = state.risk_scores.get(zone_id, 0.5)
                priority += min(state.time_step / 72, 1.0)  # Increase with time
                priority = min(priority, 1.0)
                
                action = Action(
                    warehouse_id=warehouse_id,
                    zone_id=zone_id,
                    resources=allocated_resources,
                    vehicle_type=vehicle_type,
                    priority=priority
                )
                actions.append(action)
    
    # Sort by priority and limit
    actions.sort(key=lambda a: a.priority, reverse=True)
    return actions[:max_actions]


def get_no_action() -> Action:
    """
    Get the 'do nothing' action
    
    Returns:
        Action representing no allocation
    """
    return Action(
        warehouse_id='NONE',
        zone_id='NONE',
        resources={},
        vehicle_type='none',
        priority=0.0
    )
