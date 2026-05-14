import gymnasium as gym
from gymnasium import spaces
import numpy as np

class DisasterReliefEnv(gym.Env):
    """
    OpenAI Gymnasium-compatible environment for Disaster Relief Logistics.
    Models district demand, warehouse stock, transportation, road failures, 
    UAV constraints, and deprivation accumulation.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, num_districts=10, num_warehouses=3, max_trucks=50, max_uavs=20, max_steps=30):
        super(DisasterReliefEnv, self).__init__()
        
        self.num_districts = num_districts
        self.num_warehouses = num_warehouses
        self.max_trucks = max_trucks
        self.max_uavs = max_uavs
        self.max_steps = max_steps
        
        # Observation Space size calculation
        self.obs_dim = (
            self.num_warehouses + # warehouse inventory
            self.num_districts + # district shortages
            self.num_districts + # road connectivity (binary or 0-1 continuous)
            self.num_warehouses * 2 + # truck and uav availability at each warehouse
            self.num_districts + # flood severity
            1 # time period
        )
        
        # Action Space: allocation from each warehouse to each district 
        # using trucks and UAVs -> W * D * 2
        self.action_dim = self.num_warehouses * self.num_districts * 2
        
        # Continuous action space for PPO agent (outputs between 0 and 1)
        # Represents proportion of available resources allocated
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.obs_dim,), dtype=np.float32)
        self.action_space = spaces.Box(low=0, high=1, shape=(self.action_dim,), dtype=np.float32)
        
        self.current_step = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        
        # Initialize state realistically
        # E.g., high warehouse inventory, some shortages, road connectivity depends on flood severity
        state = np.zeros(self.obs_dim, dtype=np.float32)
        
        # Warehouse inventory (initially high)
        state[0:self.num_warehouses] = np.random.uniform(0.5, 1.0, self.num_warehouses)
        
        # District shortages (random initial shortages based on disaster)
        shortage_start = self.num_warehouses
        state[shortage_start:shortage_start + self.num_districts] = np.random.uniform(0.0, 0.8, self.num_districts)
        
        # Road connectivity (1 means fully connected, 0 means blocked)
        road_start = shortage_start + self.num_districts
        state[road_start:road_start + self.num_districts] = np.random.uniform(0.5, 1.0, self.num_districts)
        
        # Vehicle availability at warehouses
        vehicle_start = road_start + self.num_districts
        state[vehicle_start:vehicle_start + self.num_warehouses * 2] = 1.0
        
        # Flood severity
        flood_start = vehicle_start + self.num_warehouses * 2
        state[flood_start:flood_start + self.num_districts] = np.random.uniform(0.0, 1.0, self.num_districts)
        
        # Time period
        state[-1] = 0.0
        
        self.state = state
        return self.state, {}
        
    def step(self, action):
        self.current_step += 1
        
        # 1. State extraction
        shortage_start = self.num_warehouses
        road_start = shortage_start + self.num_districts
        flood_start = road_start + self.num_districts + self.num_warehouses * 2
        
        shortages = self.state[shortage_start:shortage_start + self.num_districts]
        road_connectivity = self.state[road_start:road_start + self.num_districts]
        flood_severity = self.state[flood_start:flood_start + self.num_districts]
        
        # 2. Process action (allocation)
        # Reshape action to (W, D, 2)
        allocation = action.reshape((self.num_warehouses, self.num_districts, 2))
        
        # Calculate delivered resources
        # Trucks depend on road connectivity, UAVs do not
        truck_delivery = np.sum(allocation[:, :, 0], axis=0) * road_connectivity
        uav_delivery = np.sum(allocation[:, :, 1], axis=0)
        
        total_delivered = truck_delivery + uav_delivery
        
        # Update shortages
        new_shortages = np.maximum(0, shortages - total_delivered * 0.5)
        # Demand escalation: shortages increase slightly over time if not met
        new_shortages = np.minimum(1.0, new_shortages + np.random.uniform(0, 0.1, self.num_districts))
        
        # Update state
        self.state[shortage_start:shortage_start + self.num_districts] = new_shortages
        self.state[-1] = self.current_step / self.max_steps
        
        # Dynamic Road Failure Simulation (roads degrade over time if flood is severe)
        degradation = flood_severity * np.random.uniform(0, 0.1, self.num_districts)
        self.state[road_start:road_start + self.num_districts] = np.maximum(0, road_connectivity - degradation)
        
        # 3. Reward Calculation
        # Deprivation Cost (minimize shortages)
        deprivation_cost = np.sum(new_shortages)
        
        # Transport Cost (proportional to allocation)
        # UAVs are more expensive than trucks
        truck_cost = np.sum(allocation[:, :, 0]) * 1.0
        uav_cost = np.sum(allocation[:, :, 1]) * 2.5
        transport_cost = truck_cost + uav_cost
        
        # Fairness Penalty (minimize variance in shortages)
        fairness_penalty = np.var(new_shortages) * 5.0
        
        # Failed Deliveries Penalty (allocating trucks to disconnected roads)
        failed_trucks = np.sum(allocation[:, :, 0], axis=0) * (1.0 - road_connectivity)
        failed_delivery_penalty = np.sum(failed_trucks) * 2.0
        
        reward = -(deprivation_cost + transport_cost + fairness_penalty + failed_delivery_penalty)
        
        terminated = self.current_step >= self.max_steps
        truncated = False
        
        info = {
            "deprivation_cost": float(deprivation_cost),
            "transport_cost": float(transport_cost),
            "fairness_penalty": float(fairness_penalty),
            "failed_delivery_penalty": float(failed_delivery_penalty),
            "avg_shortage": float(np.mean(new_shortages))
        }
        
        return self.state, float(reward), terminated, truncated, info
        
    def render(self):
        # Could implement printout or visualization here
        pass
        
    def close(self):
        pass
