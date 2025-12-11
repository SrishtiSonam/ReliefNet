"""
Reward function for Approximate Dynamic Programming
Calculates immediate reward for state-action pairs
"""
from typing import Dict
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import ADP_CONFIG


def calculate_reward(state, action) -> float:
    """
    Calculate immediate reward for taking action in state
    
    Reward components:
    1. Negative penalty for unmet demand (deprivation)
    2. Negative cost for transportation
    3. Positive reward for meeting high-priority demand
    
    Args:
        state: Current State object
        action: Action object
    
    Returns:
        Reward value (higher is better)
    """
    reward = 0.0
    
    # 1. Deprivation penalty
    # Penalize for unmet demand at each zone
    total_unmet_demand = 0
    for zone_id, zone_demand in state.demand.items():
        unmet = sum(zone_demand.values())
        risk_multiplier = state.risk_scores.get(zone_id, 0.5)
        total_unmet_demand += unmet * risk_multiplier
    
    deprivation_penalty = -total_unmet_demand * ADP_CONFIG['deprivation_penalty'] / 10000
    reward += deprivation_penalty
    
    # 2. Transportation cost
    if action.warehouse_id != 'NONE':
        # Estimate distance (simplified - in reality would use actual distances)
        estimated_distance_km = 100  # Default
        
        transport_cost = -estimated_distance_km * ADP_CONFIG['transport_cost_per_km']
        reward += transport_cost / 1000  # Normalize
    
    # 3. Reward for meeting demand
    if action.resources:
        resources_delivered = sum(action.resources.values())
        priority_bonus = action.priority * resources_delivered / 100
        reward += priority_bonus
    
    # 4. Time penalty (encourage faster response)
    time_penalty = -state.time_step / 100
    reward += time_penalty
    
    return reward


def calculate_terminal_reward(state) -> float:
    """
    Calculate reward at terminal state (end of episode)
    
    Args:
        state: Terminal State object
    
    Returns:
        Terminal reward
    """
    # Large penalty for any remaining unmet demand
    total_unmet = 0
    for zone_demand in state.demand.values():
        total_unmet += sum(zone_demand.values())
    
    terminal_penalty = -total_unmet * ADP_CONFIG['deprivation_penalty']
    
    # Bonus for leftover inventory (can be used for future disasters)
    leftover_bonus = sum(state.inventory.values()) * 0.1
    
    return (terminal_penalty + leftover_bonus) / 10000  # Normalize


def estimate_value_to_go(state, vfa_model) -> float:
    """
    Estimate future value using VFA model
    
    Args:
        state: Current State object
        vfa_model: Trained VFA model (NN-VFA or DL-VFA)
    
    Returns:
        Estimated future value
    """
    state_features = state.to_feature_vector()
    value = vfa_model.predict_value(state_features)
    return value


def calculate_q_value(state, action, next_state, vfa_model) -> float:
    """
    Calculate Q-value (state-action value) using Bellman equation
    
    Q(s, a) = R(s, a) + γ * V(s')
    
    Args:
        state: Current state
        action: Action taken
        next_state: Resulting next state
        vfa_model: VFA model for value estimation
    
    Returns:
        Q-value
    """
    immediate_reward = calculate_reward(state, action)
    future_value = estimate_value_to_go(next_state, vfa_model)
    
    discount_factor = ADP_CONFIG['discount_factor']
    q_value = immediate_reward + discount_factor * future_value
    
    return q_value
