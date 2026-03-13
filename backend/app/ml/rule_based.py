# ─── rule_based.py ────────────────────────────────────────────────────────────
import numpy as np
from typing import Dict
from app.ml.base_agent import BaseAgent
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.mdp import (MDPState, MDPTransition, ScenarioGenerator, DistrictState)


class RuleBasedHeuristic(BaseAgent):
    """
    If deprivation_time >= 2 in district n → send UAVs to cover expected demand.
    Then send all remaining supplies by truck to district with highest deprivation cost.
    """
    def __init__(self, districts, n_periods=30,
                 truck_cap=5000.0, uav_cap=200.0):
        self.districts  = districts
        self.n_periods  = n_periods
        self.truck_cap  = truck_cap
        self.uav_cap    = uav_cap
        self.transition = MDPTransition(truck_cap, uav_cap)

    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        available = state.cw_inventory
        actions   = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

        for d in state.districts:
            if d.deprivation_time >= 2 and available >= self.uav_cap:
                n_uavs = int(np.ceil(d.demand_estimate / self.uav_cap))
                uav_u  = min(n_uavs * self.uav_cap, available)
                actions[d.name]["uav"] = uav_u
                available -= uav_u

        if state.districts and available > 0:
            top = max(state.districts,
                      key=lambda x: marginal_deprivation_cost(x.deprivation_time) * x.shortage)
            actions[top.name]["truck"] += min(available, self.truck_cap)

        return actions

    def evaluate(self, scenario_gen: ScenarioGenerator,
                 initial_state: MDPState, n_eval: int = 30) -> Dict:
        all_costs, all_dep = [], []
        max_dep = 0
        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(epoch=0, cw_inventory=initial_state.cw_inventory,
                              districts=[DistrictState(**d.__dict__)
                                         for d in initial_state.districts])
            ep_cost = ep_dep = 0.0
            for t in range(self.n_periods):
                actions = self.get_action(state)
                cost    = self.transition.compute_cost(state, actions)
                for d in state.districts:
                    ep_dep += marginal_deprivation_cost(d.deprivation_time) * d.shortage
                    max_dep = max(max_dep, d.deprivation_time)
                ep_cost += cost
                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)
            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
        return {
            "method": "rule_based",
            "total_cost":         float(np.mean(all_costs)),
            "total_cost_std":     float(np.std(all_costs)),
            "deprivation_cost":   float(np.mean(all_dep)),
            "transport_cost":     float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
        }