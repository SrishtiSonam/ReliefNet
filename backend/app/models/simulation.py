# ─── models/simulation.py ────────────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MethodEnum(str, Enum):
    dl_vfa     = "dl_vfa"
    nn_vfa     = "nn_vfa"
    ppo        = "ppo"
    rule_based = "rule_based"
    pi_bound   = "pi_bound"
    re_opt     = "re_opt"

class SimulationConfig(BaseModel):
    name:               str
    case_study:         str             # e.g. "kerala_2018" or "custom"
    selected_districts: List[str]       # List of district names
    warehouse_id:       str
    methods:            List[MethodEnum]
    n_periods:          int = 30        # Planning horizon
    period_hours:       int = 6         # Hours per decision epoch
    truck_capacity:     float = 5000.0
    uav_capacity:       float = 200.0
    supply_cov:         float = 0.2     # Coefficient of variation
    demand_cov:         float = 0.2
    n_training_episodes:int = 1000      # For DL-VFA / NN-VFA / PPO

class SimulationRun(BaseModel):
    id:         Optional[str] = Field(None, alias="_id")
    config:     SimulationConfig
    status:     str = "pending"         # pending | running | completed | failed
    results:    Optional[List[AllocationResult]] = None
    created_at: Optional[str] = None