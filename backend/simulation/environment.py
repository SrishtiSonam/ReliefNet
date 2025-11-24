import random
import pandas as pd
import numpy as np

class SimulationEnvironment:
    def __init__(self, data_dir="project/data"):
        self.districts = pd.read_csv(f"{data_dir}/districts.csv").to_dict('records')
        self.roads = pd.read_csv(f"{data_dir}/roads.csv").to_dict('records')
        self.demand_data = pd.read_csv(f"{data_dir}/synthetic_demand.csv")
        self.current_step = 0
        self.total_steps = 100
        
        # State
        self.road_status = { (r['source'], r['target']): 1.0 for r in self.roads } # 1.0 = open, 0.0 = closed
        self.inventory = 10000
        
    def step(self):
        """
        Advance simulation by one time step (1 day).
        Returns: current_state (demand, road_status, etc.)
        """
        if self.current_step >= self.total_steps:
            return None
        
        # 1. Get Demand for this day
        # In a real sim, we'd filter by date, here just using index as proxy
        # Simplified: Random demand fluctuation
        current_demand = {}
        for d in self.districts:
            base = d['base_demand']
            # Random surge
            surge = 100 if random.random() < 0.05 else 0
            current_demand[d['district_id']] = base + surge + random.randint(-10, 10)

        # 2. Road Failures (Aftershocks)
        if random.random() < 0.1:
            # Randomly close a road
            r = random.choice(self.roads)
            key = (r['source'], r['target'])
            self.road_status[key] = 0.0
        
        # 3. Supply Arrival
        self.inventory += 500 # Daily resupply

        self.current_step += 1
        
        # Convert tuple keys to strings for JSON serialization
        road_status_str = {f"{k[0]}-{k[1]}": v for k, v in self.road_status.items()}
        
        return {
            "step": self.current_step,
            "demand": current_demand,
            "inventory": self.inventory,
            "road_status": road_status_str
        }

    def reset(self):
        self.current_step = 0
        self.inventory = 10000
        self.road_status = { (r['source'], r['target']): 1.0 for r in self.roads }
