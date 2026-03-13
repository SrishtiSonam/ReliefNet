# ─── models/allocation.py ────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import List, Dict

class AllocationDecision(BaseModel):
    epoch:          int
    district_name:  str
    truck_units:    float
    uav_units:      float
    total_units:    float

class AllocationResult(BaseModel):
    simulation_id:      str
    method:             str     # dl_vfa | nn_vfa | ppo | rule_based | pi_bound | re_opt
    total_cost:         float
    deprivation_cost:   float
    transport_cost:     float
    uav_cost:           float
    truck_cost:         float
    max_deprivation_time: float
    demand_coverage:    float
    decisions:          List[AllocationDecision]
    deprivation_per_epoch: List[Dict]   # [{epoch, district, cost}]
