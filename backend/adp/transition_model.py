"""
Transition model for Approximate Dynamic Programming
Simulates state transitions after taking actions
"""
from typing import Dict
import copy


def simulate_transition(state, action):
    """
    Simulate state transition after taking action
    
    Updates:
    - Reduce inventory by allocated resources
    - Reduce demand at target zone
    - Reduce vehicle availability
    - Increment time step
    
    Args:
        state: Current State object
        action: Action object
    
    Returns:
        New State object after transition
    """
    # Create copy of state
    next_state = state.copy()
    
    # If no action, just advance time
    if action.warehouse_id == 'NONE':
        next_state.time_step += 1
        return next_state
    
    # Update inventory (reduce by allocated resources)
    for resource_type, quantity in action.resources.items():
        if resource_type in next_state.inventory:
            next_state.inventory[resource_type] -= quantity
            next_state.inventory[resource_type] = max(0, next_state.inventory[resource_type])
    
    # Update demand (reduce at target zone)
    if action.zone_id in next_state.demand:
        for resource_type, quantity in action.resources.items():
            if resource_type in next_state.demand[action.zone_id]:
                next_state.demand[action.zone_id][resource_type] -= quantity
                next_state.demand[action.zone_id][resource_type] = max(
                    0, next_state.demand[action.zone_id][resource_type]
                )
    
    # Update vehicle availability
    if action.vehicle_type in next_state.vehicles_available:
        next_state.vehicles_available[action.vehicle_type] -= 1
        next_state.vehicles_available[action.vehicle_type] = max(
            0, next_state.vehicles_available[action.vehicle_type]
        )
    
    # Advance time
    next_state.time_step += 1
    
    # Vehicles return after some time (simplified)
    if next_state.time_step % 4 == 0:  # Every 4 hours
        if action.vehicle_type == 'truck':
            next_state.vehicles_available['truck'] = min(
                next_state.vehicles_available.get('truck', 0) + 1, 20
            )
        elif action.vehicle_type == 'uav':
            next_state.vehicles_available['uav'] = min(
                next_state.vehicles_available.get('uav', 0) + 1, 10
            )
    
    return next_state


def is_terminal_state(state, max_time_steps=72) -> bool:
    """
    Check if state is terminal
    
    Terminal conditions:
    - All demand is met
    - Maximum time reached
    - No inventory left and no vehicles available
    
    Args:
        state: State object
        max_time_steps: Maximum time steps (default 72 hours = 3 days)
    
    Returns:
        True if terminal, False otherwise
    """
    # Check time limit
    if state.time_step >= max_time_steps:
        return True
    
    # Check if all demand is met
    total_demand = sum(
        sum(zone_demand.values()) for zone_demand in state.demand.values()
    )
    if total_demand == 0:
        return True
    
    # Check if no resources left
    total_inventory = sum(state.inventory.values())
    total_vehicles = sum(state.vehicles_available.values())
    
    if total_inventory == 0 and total_vehicles == 0:
        return True
    
    return False


def simulate_episode(initial_state, policy_function, vfa_model, max_steps=72):
    """
    Simulate a complete episode using a policy
    
    Args:
        initial_state: Starting State
        policy_function: Function that takes (state, actions, vfa_model) and returns best action
        vfa_model: VFA model for value estimation
        max_steps: Maximum steps per episode
    
    Returns:
        Tuple of (states, actions, rewards, total_reward)
    """
    from .action_space import generate_feasible_actions
    from .reward_function import calculate_reward
    
    states = [initial_state]
    actions = []
    rewards = []
    
    current_state = initial_state
    
    for step in range(max_steps):
        # Check if terminal
        if is_terminal_state(current_state):
            break
        
        # Generate feasible actions
        feasible_actions = generate_feasible_actions(
            current_state, 
            warehouses=[{'warehouse_id': f'WH{i:03d}'} for i in range(1, 4)]
        )
        
        if not feasible_actions:
            break
        
        # Select action using policy
        action = policy_function(current_state, feasible_actions, vfa_model)
        
        # Simulate transition
        next_state = simulate_transition(current_state, action)
        
        # Calculate reward
        reward = calculate_reward(current_state, action)
        
        # Store
        actions.append(action)
        rewards.append(reward)
        states.append(next_state)
        
        current_state = next_state
    
    total_reward = sum(rewards)
    
    return states, actions, rewards, total_reward
