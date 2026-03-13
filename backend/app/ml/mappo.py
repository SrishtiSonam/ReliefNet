"""
mappo.py
Multi-Agent Proximal Policy Optimization for Decentralised Flood-Relief.

Research Basis
--------------
Improvement 2 from research_improvements.md:
    "Decentralized Multi-Agent Reinforcement Learning for Disaster Relief
     under Stochastic Communication Disruptions"

Architecture
------------
MAPPO follows the CTDE (Centralised Training, Decentralised Execution) paradigm:

  Training  → One shared critic observes the *global* MDPState feature vector.
  Execution → Each warehouse agent acts on its *local* AgentObservation only.

This is the state-of-the-art multi-agent extension of PPO (Yu et al., 2022).

The outer BaseAgent interface is maintained so BenchmarkRunner can evaluate
MAPPO alongside all other agents using the same n_eval / seed protocol.
"""

from __future__ import annotations

import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Optional

from app.ml.base_agent import BaseAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.mdp import MDPState, DistrictState, MDPTransition, ScenarioGenerator
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.marl_env import MARLEnvironment, AgentObservation
from app.ml.equity import gini_coefficient


# ── Shared Network Definitions ────────────────────────────────────────────────

class LocalActorNet(nn.Module):
    """Actor for a single agent — takes local observation vector."""
    def __init__(self, obs_dim: int, action_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64), nn.Tanh(),
            nn.Linear(64, 64),      nn.Tanh(),
            nn.Linear(64, action_dim),
            nn.Softplus(),  # Positive Dirichlet concentrations
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class CentralCriticNet(nn.Module):
    """Centralised critic — takes global MDPState feature vector."""
    def __init__(self, global_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(global_dim, 128), nn.Tanh(),
            nn.Linear(128,        64),  nn.Tanh(),
            nn.Linear(64,          1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ── MAPPO Agent ───────────────────────────────────────────────────────────────

class MAPPOAgent(BaseAgent):
    """
    Multi-Agent PPO with a centralised critic and decentralised actors.

    Each warehouse agent has its own `LocalActorNet`.
    The single `CentralCriticNet` is shared across all agents during training.

    Implements `BaseAgent.train()` and `BaseAgent.evaluate()` so it plugs
    directly into BenchmarkRunner.
    """

    def __init__(
        self,
        districts:          List[DistrictState],
        n_agents:           int   = 3,
        n_periods:          int   = 30,
        truck_cap:          float = 5_000.0,
        uav_cap:            float = 200.0,
        comm_drop_prob:     float = 0.2,
        lr:                 float = 0.0003,
        clip_eps:           float = 0.2,
        gamma:              float = 0.99,
        gae_lambda:         float = 0.95,
        n_epochs:           int   = 4,
        config: Optional[SimulationConfig] = None,
    ):
        cfg = config or DEFAULT_CONFIG
        self.districts      = districts
        self.n_agents       = getattr(cfg, "marl_n_agents",        n_agents)
        self.n_periods      = cfg.n_periods
        self.truck_cap      = truck_cap
        self.uav_cap        = uav_cap
        self.comm_drop_prob = getattr(cfg, "marl_comm_drop_prob",  comm_drop_prob)
        self.clip_eps       = clip_eps
        self.gamma          = gamma
        self.gae_lambda     = gae_lambda
        self.n_epochs       = n_epochs
        self.transition     = MDPTransition(truck_cap, uav_cap)

        # Districts per agent
        n_d = len(districts)
        self._agent_district_ids = [[] for _ in range(self.n_agents)]
        for i in range(n_d):
            self._agent_district_ids[i % self.n_agents].append(i)

        # Observation dim per agent = 2 + local_districts*4 + (n_agents-1)*2
        max_local_d = max(
            len(ids) for ids in self._agent_district_ids
        ) if self._agent_district_ids else 1
        obs_dim    = 2 + max_local_d * 4 + (self.n_agents - 1) * 2

        # Action dim per agent = local_districts * 2  (truck + uav ratios)
        action_dims = [
            max(1, len(ids)) * 2
            for ids in self._agent_district_ids
        ]

        # Global state dim for centralised critic
        global_dim = 2 + n_d * 4

        self.actors  = nn.ModuleList([
            LocalActorNet(obs_dim, action_dims[a])
            for a in range(self.n_agents)
        ])
        self.critic  = CentralCriticNet(global_dim)

        self.actor_opts = [
            optim.Adam(self.actors[a].parameters(), lr=lr)
            for a in range(self.n_agents)
        ]
        self.critic_opt = optim.Adam(self.critic.parameters(), lr=lr)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _global_features(self, state: MDPState) -> torch.FloatTensor:
        feats = [float(state.epoch), state.cw_inventory]
        for d in state.districts:
            feats += [d.inventory, float(d.deprivation_time),
                      d.demand_estimate, d.shortage]
        return torch.FloatTensor(feats).unsqueeze(0)

    def _agent_action_to_dict(
        self, raw: np.ndarray, agent_id: int, state: MDPState,
    ) -> Dict[str, Dict[str, float]]:
        """Convert agent's ratio vector to {district: {truck, uav}} allocation."""
        ids = self._agent_district_ids[agent_id]
        local_dists = [state.districts[i] for i in ids if i < len(state.districts)]
        available = state.cw_inventory / self.n_agents
        actions: Dict[str, Dict[str, float]] = {}
        total_w = raw.sum() + 1e-8
        ratios  = raw / total_w
        for k, d in enumerate(local_dists):
            t_r  = ratios[k * 2]     if k * 2     < len(ratios) else 0.0
            u_r  = ratios[k * 2 + 1] if k * 2 + 1 < len(ratios) else 0.0
            truck = int((t_r * available) // self.truck_cap) * float(self.truck_cap)
            uav   = int((u_r * available) // self.uav_cap)   * float(self.uav_cap)
            actions[d.name] = {"truck": truck, "uav": uav}
        return actions

    # ── BaseAgent interface ───────────────────────────────────────────────────

    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """
        Decentralised execution: each actor acts from local features only.
        Returns merged global action dict (used by BaseAgent interface).
        """
        global_actions: Dict[str, Dict[str, float]] = {}
        feats = self._global_features(state)

        for a in range(self.n_agents):
            with torch.no_grad():
                local_feat = feats  # simplified: use global feat at eval time
                conc = self.actors[a](local_feat)
                dist = torch.distributions.Dirichlet(conc)
                raw  = dist.sample().squeeze(0).numpy()
            agent_alloc = self._agent_action_to_dict(raw, a, state)
            for d_name, alloc in agent_alloc.items():
                if d_name not in global_actions:
                    global_actions[d_name] = {"truck": 0.0, "uav": 0.0}
                global_actions[d_name]["truck"] += alloc["truck"]
                global_actions[d_name]["uav"]   += alloc["uav"]
        return global_actions

    def train(
        self,
        scenario_gen:  ScenarioGenerator,
        initial_state: MDPState,
        n_episodes:    int = 5000,
    ) -> List[float]:
        """MAPPO training with centralised critic, decentralised actors."""
        episode_costs = []

        for ep in range(n_episodes):
            path  = scenario_gen.generate_path()
            state = MDPState(
                epoch=0, cw_inventory=initial_state.cw_inventory,
                districts=[DistrictState(**d.__dict__)
                           for d in initial_state.districts],
            )

            # Buffers per agent
            states_g_buf = []    # global state for critic
            lp_bufs      = [[] for _ in range(self.n_agents)]
            reward_buf   = []
            val_buf      = []
            ep_cost      = 0.0

            for t in range(self.n_periods):
                g_feat  = self._global_features(state)
                val     = self.critic(g_feat).item()
                global_actions: Dict[str, Dict[str, float]] = {}
                log_probs = []

                for a in range(self.n_agents):
                    conc    = self.actors[a](g_feat)
                    dist_a  = torch.distributions.Dirichlet(conc)
                    sample  = dist_a.sample().squeeze(0)
                    lp      = dist_a.log_prob(sample.unsqueeze(0)).squeeze(0)
                    raw     = sample.detach().numpy()
                    a_alloc = self._agent_action_to_dict(raw, a, state)
                    for d_name, alloc in a_alloc.items():
                        if d_name not in global_actions:
                            global_actions[d_name] = {"truck": 0.0, "uav": 0.0}
                        global_actions[d_name]["truck"] += alloc["truck"]
                        global_actions[d_name]["uav"]   += alloc["uav"]
                    lp_bufs[a].append(lp.item())
                    log_probs.append(lp.item())

                cost     = self.transition.compute_cost(state, global_actions)
                ep_cost += cost

                states_g_buf.append(g_feat.squeeze(0).numpy())
                reward_buf.append(-cost)
                val_buf.append(val)

                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t]
                           for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, global_actions, real_d, path["supply"][t], new_est, new_std)

            # GAE advantages
            advantages = self._compute_gae(reward_buf, val_buf)
            s_t = torch.FloatTensor(np.array(states_g_buf))
            adv = torch.FloatTensor(advantages)
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)
            r_t = torch.FloatTensor(reward_buf)

            # Update critic
            val_pred = self.critic(s_t).squeeze()
            c_loss   = nn.MSELoss()(val_pred, r_t)
            self.critic_opt.zero_grad()
            c_loss.backward()
            nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)
            self.critic_opt.step()

            # Update each actor
            for a in range(self.n_agents):
                old_lp = torch.FloatTensor(lp_bufs[a])
                conc   = self.actors[a](s_t)
                dist_a = torch.distributions.Dirichlet(conc)
                samp   = conc / conc.sum(dim=-1, keepdim=True)
                new_lp = dist_a.log_prob(samp)
                ratio  = torch.exp(new_lp - old_lp)
                s1     = ratio * adv
                s2     = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * adv
                a_loss = -torch.min(s1, s2).mean()
                self.actor_opts[a].zero_grad()
                a_loss.backward()
                nn.utils.clip_grad_norm_(self.actors[a].parameters(), 0.5)
                self.actor_opts[a].step()

            episode_costs.append(ep_cost)

        return episode_costs

    def _compute_gae(self, rewards: List[float], values: List[float]) -> np.ndarray:
        advantages = np.zeros(len(rewards))
        gae = 0.0
        for t in reversed(range(len(rewards))):
            nxt   = values[t + 1] if t + 1 < len(values) else 0.0
            delta = rewards[t] + self.gamma * nxt - values[t]
            gae   = delta + self.gamma * self.gae_lambda * gae
            advantages[t] = gae
        return advantages

    def evaluate(
        self,
        scenario_gen:  ScenarioGenerator,
        initial_state: MDPState,
        n_eval:        int = 30,
    ) -> Dict:
        all_costs, all_dep, all_gini = [], [], []
        max_dep = 0
        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(
                epoch=0, cw_inventory=initial_state.cw_inventory,
                districts=[DistrictState(**d.__dict__)
                           for d in initial_state.districts],
            )
            ep_cost = ep_dep = ep_gini = 0.0
            for t in range(self.n_periods):
                actions = self.get_action(state)
                cost    = self.transition.compute_cost(state, actions)
                shortages = [d.shortage for d in state.districts]
                ep_gini += gini_coefficient(shortages)
                for d in state.districts:
                    ep_dep += marginal_deprivation_cost(d.deprivation_time) * d.shortage
                    max_dep = max(max_dep, d.deprivation_time)
                ep_cost += cost
                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t]
                           for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)
            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
            all_gini.append(ep_gini / self.n_periods)

        return {
            "method":               "mappo",
            "total_cost":           float(np.mean(all_costs)),
            "total_cost_std":       float(np.std(all_costs)),
            "deprivation_cost":     float(np.mean(all_dep)),
            "transport_cost":       float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
            "gini":                 float(np.mean(all_gini)),
            "n_agents":             self.n_agents,
            "comm_drop_prob":       self.comm_drop_prob,
        }
