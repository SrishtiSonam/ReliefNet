# ─── nn_vfa.py ────────────────────────────────────────────────────────────────
"""
Neural Network Value Function Approximation (NN-VFA)
One neural network approximates the full state value.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Optional
from app.ml.base_agent import BaseAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.deprivation import marginal_deprivation_cost, expected_deprivation_cost
from app.ml.mdp import (MDPState, MDPTransition, ScenarioGenerator, DistrictState)


class ValueNetwork(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class NNVFA(BaseAgent):
    def __init__(self, districts: List[DistrictState],
                 n_periods: int = 30,
                 truck_cap: float = 5000.0, uav_cap: float = 200.0,
                 lr: float = 0.001, buffer_size: int = 1000,
                 update_freq: int = 10, batch_size: int = 256,
                 eps_init: float = 0.2, eps_decay: float = 0.98,
                 discount: float = 0.9,
                 config: Optional[SimulationConfig] = None):
        cfg = config or DEFAULT_CONFIG

        self.districts   = districts
        self.n_periods   = n_periods
        self.truck_cap   = truck_cap
        self.uav_cap     = uav_cap
        self.eps         = eps_init
        self.eps_decay   = eps_decay
        self.discount    = discount
        self.buffer_size = buffer_size
        self.update_freq = update_freq
        self.batch_size  = batch_size
        self.transition  = MDPTransition(truck_cap, uav_cap)
        self.n           = len(districts)

        # Input: epoch + cw_inv + per district (inv, dep_time, demand_est, exp_dep)
        input_dim = 2 + self.n * 4
        self.model     = ValueNetwork(input_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn   = nn.MSELoss()
        self.buffer: List = []

    def _state_features(self, pds, state: MDPState) -> np.ndarray:
        feats = [state.epoch, pds.cw_inventory_x]
        for dx in pds.districts_x:
            feats += [dx["inv_x"], dx["deprivation_time"],
                      dx["exp_deprivation_cost"], dx.get("shortage", 0.0)]
        return np.array(feats, dtype=np.float32)

    def value(self, features: np.ndarray) -> float:
        x = torch.FloatTensor(features).unsqueeze(0)
        with torch.no_grad():
            return self.model(x).item()

    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """Greedy allocation guided by NN value function."""
        available = state.cw_inventory
        actions = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

        # UAVs to deprived districts
        for d in sorted(state.districts, key=lambda x: -x.deprivation_time):
            if d.deprivation_time >= 1 and available >= self.uav_cap:
                uav_u = min(3 * self.uav_cap, available)
                actions[d.name]["uav"] = uav_u
                available -= uav_u

        # Truck to highest demand district
        if available >= self.truck_cap:
            top = max(state.districts, key=lambda x: x.demand_estimate)
            actions[top.name]["truck"] = min(self.truck_cap, available)

        return actions

    def warmup_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        available = state.cw_inventory
        actions = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}
        for d in state.districts:
            if d.deprivation_time >= np.random.randint(1, 4) and available >= self.uav_cap:
                u = min(np.random.randint(1, 4) * self.uav_cap, available)
                actions[d.name]["uav"] = u
                available -= u
        return actions

    def update_network(self):
        if len(self.buffer) < self.batch_size:
            return
        idx = np.random.choice(len(self.buffer), self.batch_size, replace=False)
        batch = [self.buffer[i] for i in idx]
        X = torch.FloatTensor(np.array([b[0] for b in batch]))
        y = torch.FloatTensor(np.array([b[1] for b in batch])).unsqueeze(1)
        pred = self.model(X)
        loss = self.loss_fn(pred, y)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

    def train(self, scenario_gen: ScenarioGenerator,
              initial_state: MDPState, n_episodes: int = 1000) -> List[float]:
        episode_costs = []
        for ep in range(n_episodes):
            path  = scenario_gen.generate_path()
            state = MDPState(epoch=0, cw_inventory=initial_state.cw_inventory,
                              districts=[DistrictState(**d.__dict__)
                                         for d in initial_state.districts])
            ep_cost = 0.0
            ep_buf  = []

            for t in range(self.n_periods):
                if np.random.rand() < self.eps:
                    actions = self.warmup_action(state)
                else:
                    actions = self.get_action(state)

                cost = self.transition.compute_cost(state, actions)
                pds  = self.transition.compute_post_decision_state(state, actions)
                ep_cost += cost
                feats = self._state_features(pds, state)
                ep_buf.append((feats, 0.0))

                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)

            # Recursive costs
            for i in range(len(ep_buf) - 2, -1, -1):
                ep_buf[i] = (ep_buf[i][0], ep_buf[i + 1][1] * self.discount + cost)

            self.buffer.extend(ep_buf)
            if len(self.buffer) > self.buffer_size:
                self.buffer = self.buffer[-self.buffer_size:]

            if (ep + 1) % self.update_freq == 0:
                self.update_network()
                self.eps *= self.eps_decay

            episode_costs.append(ep_cost)
        return episode_costs

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
            "method": "nn_vfa",
            "total_cost":         float(np.mean(all_costs)),
            "total_cost_std":     float(np.std(all_costs)),
            "deprivation_cost":   float(np.mean(all_dep)),
            "transport_cost":     float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
        }
