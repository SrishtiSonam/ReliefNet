"""
ADP Solver using Value Iteration with VFA
Main engine for solving the resource allocation problem
"""
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import ADP_CONFIG

from .state_representation import State, create_initial_state
from .action_space import generate_feasible_actions, Action
from .reward_function import calculate_q_value, calculate_reward
from .transition_model import simulate_transition, is_terminal_state


class ADPSolver:
    """
    Approximate Dynamic Programming Solver
    
    Uses value iteration with VFA to find optimal policy
    """
    
    def __init__(self, vfa_model):
        """
        Initialize ADP solver
        
        Args:
            vfa_model: Trained VFA model (NN-VFA or DL-VFA)
        """
        self.vfa_model = vfa_model
        self.discount_factor = ADP_CONFIG['discount_factor']
        self.max_iterations = ADP_CONFIG['max_iterations']
        self.convergence_threshold = ADP_CONFIG['convergence_threshold']
        
        self.iteration_history = []
    
    def greedy_policy(self, state: State, feasible_actions: List[Action]) -> Action:
        """
        Greedy policy: Select action with highest Q-value
        
        Args:
            state: Current state
            feasible_actions: List of feasible actions
        
        Returns:
            Best action
        """
        if not feasible_actions:
            from .action_space import get_no_action
            return get_no_action()
        
        best_action = None
        best_q_value = float('-inf')
        
        for action in feasible_actions:
            # Simulate next state
            next_state = simulate_transition(state, action)
            
            # Calculate Q-value
            q_value = calculate_q_value(state, action, next_state, self.vfa_model)
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action
        
        return best_action if best_action else feasible_actions[0]
    
    def epsilon_greedy_policy(self, state: State, feasible_actions: List[Action], 
                             epsilon: float = 0.1) -> Action:
        """
        Epsilon-greedy policy for exploration
        
        Args:
            state: Current state
            feasible_actions: List of feasible actions
            epsilon: Exploration probability
        
        Returns:
            Selected action
        """
        if np.random.random() < epsilon:
            # Explore: random action
            return np.random.choice(feasible_actions)
        else:
            # Exploit: greedy action
            return self.greedy_policy(state, feasible_actions)
    
    def solve(self, initial_state: State, warehouses: List[Dict]) -> Dict[str, Any]:
        """
        Solve the ADP problem to find optimal allocation policy
        
        Args:
            initial_state: Initial state
            warehouses: List of warehouse data
        
        Returns:
            Dictionary with solution including actions and expected value
        """
        print(f"Solving ADP with {len(warehouses)} warehouses...")
        
        # Generate allocation plan
        allocation_plan = []
        current_state = initial_state
        total_reward = 0.0
        
        max_steps = 72  # 3 days
        
        for step in range(max_steps):
            if is_terminal_state(current_state):
                print(f"  Terminal state reached at step {step}")
                break
            
            # Generate feasible actions
            feasible_actions = generate_feasible_actions(current_state, warehouses)
            
            if not feasible_actions:
                print(f"  No feasible actions at step {step}")
                break
            
            # Select best action
            best_action = self.greedy_policy(current_state, feasible_actions)
            
            # Simulate transition
            next_state = simulate_transition(current_state, best_action)
            
            # Calculate reward
            reward = calculate_reward(current_state, best_action)
            total_reward += reward
            
            # Add to plan
            if best_action.warehouse_id != 'NONE':
                allocation_plan.append({
                    'step': step,
                    'time_hours': current_state.time_step,
                    'warehouse_id': best_action.warehouse_id,
                    'zone_id': best_action.zone_id,
                    'resources': best_action.resources,
                    'vehicle_type': best_action.vehicle_type,
                    'priority': best_action.priority,
                    'reward': reward
                })
            
            current_state = next_state
        
        # Calculate final metrics
        final_demand = sum(
            sum(zone_demand.values()) for zone_demand in current_state.demand.values()
        )
        
        demand_met_percentage = 100 * (1 - final_demand / max(
            sum(sum(zone_demand.values()) for zone_demand in initial_state.demand.values()),
            1
        ))
        
        result = {
            'allocation_plan': allocation_plan,
            'total_reward': total_reward,
            'steps_taken': len(allocation_plan),
            'final_inventory': current_state.inventory,
            'remaining_demand': final_demand,
            'demand_met_percentage': demand_met_percentage,
            'final_state': current_state.to_dict()
        }
        
        print(f"✓ ADP solved: {len(allocation_plan)} allocations, {demand_met_percentage:.1f}% demand met")
        
        return result


def solve_allocation_problem(warehouses_data: List[Dict], 
                            demand_data: Dict[str, Dict[str, float]],
                            vfa_model) -> Dict[str, Any]:
    """
    High-level function to solve resource allocation problem
    
    Args:
        warehouses_data: List of warehouse dictionaries
        demand_data: Dictionary of zone_id -> {resource_type -> quantity}
        vfa_model: Trained VFA model
    
    Returns:
        Solution dictionary with allocation plan
    """
    # Create initial state
    initial_state = create_initial_state(warehouses_data, demand_data)
    
    # Create solver
    solver = ADPSolver(vfa_model)
    
    # Solve
    solution = solver.solve(initial_state, warehouses_data)
    
    return solution
