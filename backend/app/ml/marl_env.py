"""
marl_env.py
Multi-Agent Reinforcement Learning Environment for Flood-Relief Logistics.

Research Basis
--------------
Improvement 2 from research_improvements.md:
    "Decentralized Multi-Agent Reinforcement Learning for Disaster Relief
     under Stochastic Communication Disruptions"

Architecture (CTDE — Centralised Training, Decentralised Execution)
--------------------------------------------------------------------
  • Each warehouse is a separate agent with a *local observation*.
  • During training, agents share a *centralised critic* that sees the
    full global state.
  • During execution, each agent acts on its local view only.
  • With probability `comm_drop_prob` an agent's view of other agents'
    allocations is zeroed-out, simulating radio-blackout.
"""

from __future__ import annotations

import copy
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from app.ml.mdp import MDPState, MDPTransition, DistrictState, ScenarioGenerator
from app.ml.deprivation import marginal_deprivation_cost


# ── Agent Observation Dataclass ───────────────────────────────────────────────

@dataclass
class AgentObservation:
    """Per-agent partial observation at a single time step."""
    agent_id:          int
    n_periods:         int
    epoch:             int
    local_inventory:   float                      # this warehouse's share
    districts:         List[DistrictState]        # districts visible to this agent
    other_allocations: Dict[int, Dict]            # other agents' last allocs (may be masked)
    comm_dropped:      bool                       # True → other_allocations is zeroed

    def to_feature_vector(self) -> np.ndarray:
        feats = [float(self.epoch), self.local_inventory]
        for d in self.districts:
            feats += [d.inventory, float(d.deprivation_time),
                      d.demand_estimate, d.shortage]
        # Append visible inter-agent info (flattened)
        for aid, alloc in self.other_allocations.items():
            if self.comm_dropped:
                feats += [0.0, 0.0]   # blacked-out
            else:
                feats += [alloc.get("truck_total", 0.0),
                          alloc.get("uav_total",   0.0)]
        return np.array(feats, dtype=np.float32)


# ── MARL Environment ──────────────────────────────────────────────────────────

class MARLEnvironment:
    """
    Wraps the MDP to expose a multi-agent step interface.

    Each agent controls a *partition* of the central-warehouse inventory.
    Districts are split evenly (or by configured assignment) across agents.

    Parameters
    ----------
    initial_state    : MDPState  — starting global state.
    scenario_gen     : ScenarioGenerator
    n_agents         : int       — number of warehouse agents (default 3).
    comm_drop_prob   : float     — probability of inter-agent comms drop per step.
    truck_cap / uav_cap : vehicle capacities forwarded to MDPTransition.
    """

    def __init__(
        self,
        initial_state:  MDPState,
        scenario_gen:   ScenarioGenerator,
        n_agents:       int   = 3,
        comm_drop_prob: float = 0.2,
        truck_cap:      float = 5_000.0,
        uav_cap:        float = 200.0,
        n_periods:      int   = 30,
    ):
        self.initial_state  = initial_state
        self.scenario_gen   = scenario_gen
        self.n_agents       = n_agents
        self.comm_drop_prob = comm_drop_prob
        self.n_periods      = n_periods
        self.transition     = MDPTransition(truck_cap, uav_cap)

        self._state:  Optional[MDPState] = None
        self._path:   Optional[Dict]     = None
        self._t:      int                = 0
        self._last_allocs: Dict[int, Dict] = {}

        # Pre-assign districts to agents (round-robin partition)
        dists = initial_state.districts
        self._agent_district_ids: List[List[int]] = [[] for _ in range(n_agents)]
        for i, _ in enumerate(dists):
            self._agent_district_ids[i % n_agents].append(i)

    # ── Wrappers ──────────────────────────────────────────────────────────────

    def reset(self, seed: Optional[int] = None) -> List[AgentObservation]:
        """Start a new episode. Returns initial observations for all agents."""
        if seed is not None:
            np.random.seed(seed)
        self._state = MDPState(
            epoch=0,
            cw_inventory=self.initial_state.cw_inventory,
            districts=[DistrictState(**d.__dict__)
                       for d in self.initial_state.districts],
        )
        self._path       = self.scenario_gen.generate_path()
        self._t          = 0
        self._last_allocs = {a: {"truck_total": 0.0, "uav_total": 0.0}
                             for a in range(self.n_agents)}
        return self._build_observations()

    def step(
        self,
        actions_per_agent: Dict[int, Dict[str, Dict[str, float]]],
    ) -> Tuple[List[AgentObservation], Dict[int, float], bool, Dict]:
        """
        Apply each agent's partial allocation decision.

        Parameters
        ----------
        actions_per_agent : {agent_id: {district_name: {truck, uav}}}

        Returns
        -------
        observations : List[AgentObservation] (one per agent)
        rewards      : {agent_id: float}  (negative cost contribution)
        done         : bool
        info         : dict  (global cost, gini, etc.)
        """
        from app.ml.equity import gini_coefficient

        # Merge all agent actions into single global action dict
        global_actions: Dict[str, Dict[str, float]] = {}
        for agent_id, agent_action in actions_per_agent.items():
            for d_name, alloc in agent_action.items():
                if d_name not in global_actions:
                    global_actions[d_name] = {"truck": 0.0, "uav": 0.0}
                global_actions[d_name]["truck"] += alloc.get("truck", 0.0)
                global_actions[d_name]["uav"]   += alloc.get("uav",   0.0)

        # Enforce CW budget cap
        total_req = sum(v["truck"] + v["uav"] for v in global_actions.values())
        if total_req > self._state.cw_inventory + 1e-6:
            scale = self._state.cw_inventory / (total_req + 1e-8)
            for k in global_actions:
                global_actions[k]["truck"] *= scale
                global_actions[k]["uav"]   *= scale

        # Compute costs
        cost = self.transition.compute_cost(self._state, global_actions)
        shortages = [d.shortage for d in self._state.districts]
        gini = gini_coefficient(shortages)

        # Transition state
        real_d  = {d: self._path["demands"][d][self._t]
                   for d in self._path["demands"]}
        new_est = {d: self._path["demand_estimates"][d][self._t]
                   for d in self._path["demand_estimates"]}
        new_std = {d.name: d.demand_std for d in self._state.districts}
        self._state = self.transition.transition(
            self._state, global_actions,
            real_d, self._path["supply"][self._t], new_est, new_std,
        )
        self._t += 1

        # Update inter-agent allocation summary (for next step's observations)
        for agent_id, agent_action in actions_per_agent.items():
            t_sum = sum(v.get("truck", 0) for v in agent_action.values())
            u_sum = sum(v.get("uav",   0) for v in agent_action.values())
            self._last_allocs[agent_id] = {"truck_total": t_sum, "uav_total": u_sum}

        done = self._t >= self.n_periods
        obs  = self._build_observations()

        # Equal cost share per agent (can be refined to per-district attribution)
        rewards = {a: -cost / self.n_agents for a in range(self.n_agents)}
        info = {"total_cost": cost, "gini": gini, "epoch": self._t}
        return obs, rewards, done, info

    def _build_observations(self) -> List[AgentObservation]:
        """Build per-agent partial observation from global state."""
        obs = []
        for agent_id in range(self.n_agents):
            # Decide comms drop for this agent this step
            comm_dropped = np.random.random() < self.comm_drop_prob

            # Local districts
            local_district_ids = self._agent_district_ids[agent_id]
            local_districts = [self._state.districts[i]
                               for i in local_district_ids
                               if i < len(self._state.districts)]

            # Local inventory share (equal split)
            local_inv = self._state.cw_inventory / self.n_agents

            other_allocs = {a: alloc
                            for a, alloc in self._last_allocs.items()
                            if a != agent_id}

            obs.append(AgentObservation(
                agent_id          = agent_id,
                n_periods         = self.n_periods,
                epoch             = self._state.epoch,
                local_inventory   = local_inv,
                districts         = local_districts,
                other_allocations = other_allocs,
                comm_dropped      = comm_dropped,
            ))
        return obs
