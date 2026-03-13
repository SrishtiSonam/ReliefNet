"""
Proximal Policy Optimization (PPO) for Flood Relief Allocation
Actor-Critic structure with continuous action space mapping.
Adapted from: Schulman et al. (2017), van Steenbergen et al. (2023)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Optional
from app.ml.base_agent import BaseAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.mdp import (MDPState, MDPTransition, ScenarioGenerator,
                         DistrictState)


# ─── Actor Network ────────────────────────────────────────────────────────────
class ActorNetwork(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Softplus()   # Ensures positive concentration params for Dirichlet
        )

    def forward(self, x):
        return self.net(x)


# ─── Critic Network ───────────────────────────────────────────────────────────
class CriticNetwork(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)


# ─── PPO Agent ────────────────────────────────────────────────────────────────
class PPOAgent(BaseAgent):
    def __init__(self, districts: List[DistrictState],
                 n_periods: int = 30,
                 truck_cap: float = 5000.0, uav_cap: float = 200.0,
                 lr: float = 0.0001, clip_eps: float = 0.2,
                 gamma: float = 0.99, gae_lambda: float = 0.95,
                 n_epochs: int = 4, batch_size: int = 64,
                 buffer_size: int = 100,
                 config: Optional[SimulationConfig] = None):
        cfg = config or DEFAULT_CONFIG

        self.districts   = districts
        self.n_periods   = n_periods
        self.truck_cap   = truck_cap
        self.uav_cap     = uav_cap
        self.clip_eps    = clip_eps
        self.gamma       = gamma
        self.gae_lambda  = gae_lambda
        self.n_epochs    = n_epochs
        self.batch_size  = batch_size
        self.buffer_size = buffer_size
        self.transition  = MDPTransition(truck_cap, uav_cap)
        self.n           = len(districts)

        # Action space: 1 (keep at CW) + N*2 (truck+UAV per district)
        self.action_dim = 1 + self.n * 2
        # State features: epoch + cw_inv + per district (inv, dep_time, demand, shortage)
        self.state_dim  = 2 + self.n * 4

        self.actor  = ActorNetwork(self.state_dim, self.action_dim)
        self.critic = CriticNetwork(self.state_dim)
        self.actor_opt  = optim.Adam(self.actor.parameters(),  lr=lr)
        self.critic_opt = optim.Adam(self.critic.parameters(), lr=lr)

        self.buffer: List[Dict] = []

    def _state_to_tensor(self, state: MDPState) -> torch.FloatTensor:
        feats = [float(state.epoch), state.cw_inventory]
        for d in state.districts:
            feats += [d.inventory, float(d.deprivation_time),
                      d.demand_estimate, d.shortage]
        return torch.FloatTensor(feats).unsqueeze(0)

    def _map_action(self, raw_action: np.ndarray,
                    state: MDPState) -> Dict[str, Dict[str, float]]:
        """
        Map softmax [0,1] outputs to actual allocations.
        raw_action shape: (1 + N*2,)
        """
        available = state.cw_inventory
        actions = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

        total_w = raw_action.sum() + 1e-8
        ratios  = raw_action / total_w  # Normalize

        # Apply budget constraint
        total_requested = sum(
            int(ratios[1 + i * 2] * available // self.uav_cap) * self.uav_cap +
            (ratios[1 + i * 2 + 1] * available)
            for i in range(self.n)
        )
        scale = min(1.0, available / (total_requested + 1e-8))

        for i, d in enumerate(self.districts):
            uav_u   = int((ratios[1 + i * 2]     * available * scale) // self.uav_cap) * self.uav_cap
            truck_u = int((ratios[1 + i * 2 + 1] * available * scale) // self.truck_cap) * self.truck_cap
            actions[d.name]["uav"]   = uav_u
            actions[d.name]["truck"] = truck_u

        return actions

    def get_action(self, state: MDPState) -> Tuple[Dict, torch.Tensor, torch.Tensor]:
        s           = self._state_to_tensor(state)
        concentrations = self.actor(s)                        # shape: (1, action_dim) — all > 0
        dist        = torch.distributions.Dirichlet(concentrations)
        sample      = dist.sample().squeeze(0)                # shape: (action_dim,)
        raw         = sample.detach().numpy()                 # ratio vector, sums to 1
        actions     = self._map_action(raw, state)
        log_prob    = dist.log_prob(sample.unsqueeze(0))      # shape: (1,)
        return actions, log_prob.squeeze(0), concentrations

    def compute_advantages(self, rewards: List[float],
                           values: List[float], dones: List[bool]) -> np.ndarray:
        advantages = np.zeros(len(rewards))
        gae = 0.0
        for t in reversed(range(len(rewards))):
            nxt = values[t + 1] if t + 1 < len(values) else 0.0
            delta = rewards[t] + self.gamma * nxt * (1 - dones[t]) - values[t]
            gae   = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages[t] = gae
        return advantages

    def update(self, states, actions_log_probs, rewards, advantages):
        states_t     = torch.FloatTensor(np.array(states))
        old_log_prob = torch.FloatTensor(np.array(actions_log_probs))
        rewards_t    = torch.FloatTensor(np.array(rewards))
        adv_t        = torch.FloatTensor(advantages)
        adv_t        = (adv_t - adv_t.mean()) / (adv_t.std() + 1e-8)

        for _ in range(self.n_epochs):
            idx = np.random.choice(len(states), self.batch_size, replace=False) \
                  if len(states) > self.batch_size else np.arange(len(states))
            s   = states_t[idx]
            olp = old_log_prob[idx]
            adv = adv_t[idx]
            r   = rewards_t[idx]

            new_conc  = self.actor(s)                          # Dirichlet concentrations
            dist      = torch.distributions.Dirichlet(new_conc)
            # Re-derive action ratios from concentration means (mode proxy)
            new_sample = new_conc / new_conc.sum(dim=-1, keepdim=True)
            new_lp    = dist.log_prob(new_sample)
            ratio     = torch.exp(new_lp - olp)

            # PPO clipped objective
            surr1 = ratio * adv
            surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * adv
            actor_loss = -torch.min(surr1, surr2).mean()

            val   = self.critic(s).squeeze()
            critic_loss = nn.MSELoss()(val, r)

            self.actor_opt.zero_grad()
            actor_loss.backward()
            nn.utils.clip_grad_norm_(self.actor.parameters(), max_norm=0.5)
            self.actor_opt.step()

            self.critic_opt.zero_grad()
            critic_loss.backward()
            nn.utils.clip_grad_norm_(self.critic.parameters(), max_norm=0.5)
            self.critic_opt.step()

    def train(self, scenario_gen: ScenarioGenerator,
              initial_state: MDPState, n_episodes: int = 60000) -> List[float]:
        episode_costs = []
        for ep in range(n_episodes):
            path  = scenario_gen.generate_path()
            state = MDPState(epoch=0, cw_inventory=initial_state.cw_inventory,
                              districts=[DistrictState(**d.__dict__)
                                         for d in initial_state.districts])
            states_buf, lp_buf, reward_buf, val_buf = [], [], [], []
            ep_cost = 0.0

            for t in range(self.n_periods):
                s_feat = self._state_to_tensor(state).numpy().flatten()
                actions, log_prob, _ = self.get_action(state)
                cost    = self.transition.compute_cost(state, actions)
                ep_cost += cost
                val     = self.critic(self._state_to_tensor(state)).item()

                states_buf.append(s_feat)
                lp_buf.append(log_prob.item())
                reward_buf.append(-cost)   # Negative cost as reward
                val_buf.append(val)

                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)

            dones = [False] * (self.n_periods - 1) + [True]
            advs  = self.compute_advantages(reward_buf, val_buf, dones)
            self.update(states_buf, lp_buf, reward_buf, advs)
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
                actions, _, _ = self.get_action(state)
                cost = self.transition.compute_cost(state, actions)
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
            "method": "ppo",
            "total_cost":         float(np.mean(all_costs)),
            "total_cost_std":     float(np.std(all_costs)),
            "deprivation_cost":   float(np.mean(all_dep)),
            "transport_cost":     float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
        }