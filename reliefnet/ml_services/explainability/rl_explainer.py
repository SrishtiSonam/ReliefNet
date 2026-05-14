import numpy as np
import shap
from typing import Dict, List, Any
import json

class RLExplainer:
    """
    Explainability engine for RL agents in ReliefNet.
    Provides SHAP values, attention visualization, and human-readable reasoning.
    """
    def __init__(self, agent_model, env):
        self.model = agent_model
        self.env = env
        
        # We define a wrapper function for SHAP that predicts actions
        # from states for the continuous action space
        self.predict_fn = lambda x: self.model.predict(x, deterministic=True)[0]
        
    def generate_shap_explanations(self, background_states: np.ndarray, current_state: np.ndarray) -> np.ndarray:
        """
        Generate SHAP values for the given state.
        Uses a background dataset to establish baseline values.
        """
        # Using SHAP KernelExplainer for black-box RL models
        # Warning: This can be computationally expensive
        explainer = shap.KernelExplainer(self.predict_fn, background_states[:50]) # Using small sample for speed
        shap_values = explainer.shap_values(current_state, nsamples=100)
        return shap_values
        
    def generate_reasoning(self, state: np.ndarray, action: np.ndarray, district_idx: int) -> Dict[str, Any]:
        """
        Generate human-readable reasoning for why an allocation was made to a specific district.
        """
        # State index mapping (simplified from env)
        shortage_idx = self.env.num_warehouses + district_idx
        road_idx = self.env.num_warehouses + self.env.num_districts + district_idx
        flood_idx = self.env.num_warehouses + 2 * self.env.num_districts + self.env.num_warehouses * 2 + district_idx
        
        shortage = state[shortage_idx]
        road_conn = state[road_idx]
        flood_severity = state[flood_idx]
        
        reasons = []
        
        if shortage > 0.7:
            reasons.append("Critical medicine/food shortage detected.")
        elif shortage > 0.4:
            reasons.append("Moderate resource shortage.")
            
        if flood_severity > 0.6:
            reasons.append(f"High flood severity ({flood_severity:.2f}) escalating demand.")
            
        if road_conn < 0.3:
            reasons.append("Road disconnection detected. Prioritizing UAV allocation.")
        elif road_conn < 0.7:
            reasons.append("Partial road failure. Mixed fleet usage recommended.")
            
        # Confidence calculation based on how clear the signal is
        signal_strength = shortage + flood_severity + (1.0 - road_conn)
        confidence = min(0.99, 0.5 + (signal_strength / 3.0) * 0.49)
        
        return {
            "district_index": district_idx,
            "allocated_trucks_proportion": float(action[district_idx * 2]), # Assuming specific flattening
            "allocated_uavs_proportion": float(action[district_idx * 2 + 1]),
            "reasons": reasons,
            "confidence": round(confidence, 2)
        }
        
    def generate_attention_weights(self, state: np.ndarray) -> Dict[str, float]:
        """
        If using a transformer/attention-based policy, this extracts the attention weights.
        For standard MLP PPO, we can mock this using feature importance or state magnitude.
        """
        # Mock attention: heavily weighted towards districts with highest shortage * flood
        shortage_start = self.env.num_warehouses
        flood_start = shortage_start + self.env.num_districts * 2 + self.env.num_warehouses * 2
        
        shortages = state[shortage_start:shortage_start + self.env.num_districts]
        floods = state[flood_start:flood_start + self.env.num_districts]
        
        attention = shortages * 0.7 + floods * 0.3
        attention = attention / (np.sum(attention) + 1e-6) # Normalize
        
        return {f"district_{i}": float(attn) for i, attn in enumerate(attention)}

