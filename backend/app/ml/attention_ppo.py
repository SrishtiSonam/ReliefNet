"""
attention_ppo.py
Explainable PPO with Transformer-based Attention Actor.

Research Basis
--------------
Improvement 4 from research_improvements.md:
    "Trusting the Machine: Explainable Deep Reinforcement Learning
     Interfaces for Disaster Operations Management"

Method
------
Replaces the MLP ActorNetwork in PPOAgent with a Transformer encoder
that processes each district as a *token*.  The self-attention weights
are stored after every forward pass, giving a per-district "importance"
score that can be visualised on the React GIS map.

Architecture
------------
  DistrictEncoder  → projects 6 district features to d_model dims
  nn.MultiheadAttention → single-layer self-attention over district tokens
  Linear decoder   → action concentrations (Dirichlet)

The attention weights (shape: n_districts × n_districts) are averaged to
one scalar per district and stored in `self.last_attention`.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple

from app.ml.ppo import PPOAgent, CriticNetwork
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.mdp import MDPState, DistrictState, MDPTransition, ScenarioGenerator


# ── District Feature Encoder ──────────────────────────────────────────────────

class DistrictEncoder(nn.Module):
    """
    Project per-district feature vector to a fixed embedding dimension.
    District features: [inventory, deprivation_time, demand_estimate,
                        shortage, uav_cost, truck_cost]  → 6 dims.
    """
    FEAT_DIM = 6  # fixed

    def __init__(self, d_model: int = 32):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(self.FEAT_DIM, d_model),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, n_districts, FEAT_DIM) → (batch, n_districts, d_model)."""
        return self.proj(x)


# ── Attention Actor ───────────────────────────────────────────────────────────

class AttentionActorNetwork(nn.Module):
    """
    Single-head self-attention actor.
    Outputs Dirichlet concentration parameters, one per action dimension.
    """

    def __init__(
        self,
        n_districts:  int,
        action_dim:   int,
        d_model:      int = 32,
        n_heads:      int = 1,
        global_dim:   int = 2,   # epoch + cw_inventory
    ):
        super().__init__()
        self.n_districts  = n_districts
        self.d_model      = d_model
        self.encoder      = DistrictEncoder(d_model)
        self.attn         = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        # Global context projection (epoch + cw_inventory → d_model)
        self.global_proj  = nn.Linear(global_dim, d_model)
        # Decoder: pool attended embeddings → action concentrations
        pool_dim = d_model + d_model  # attended token pool + global context
        self.decoder = nn.Sequential(
            nn.Linear(pool_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softplus(),
        )
        # Stored attention weights after last forward pass
        self.last_attention_weights: Optional[torch.Tensor] = None  # (n_districts,)

    def forward(
        self, district_feats: torch.Tensor, global_feats: torch.Tensor,
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        district_feats : (batch, n_districts, 6)
        global_feats   : (batch, 2)   — [epoch, cw_inventory]

        Returns
        -------
        concentrations : (batch, action_dim)  — all > 0 due to Softplus
        """
        encoded = self.encoder(district_feats)        # (B, N, d_model)
        attended, attn_w = self.attn(encoded, encoded, encoded)
        # attn_w: (B, N, N)  — row = query district, col = key district weight
        # Average over query dimension → per-district importance scalar
        district_importance = attn_w.mean(dim=1)      # (B, N)
        self.last_attention_weights = district_importance.detach()

        attended_pool = attended.mean(dim=1)           # (B, d_model)
        g_emb         = self.global_proj(global_feats) # (B, d_model)
        combined      = torch.cat([attended_pool, g_emb], dim=-1)  # (B, d_model*2)
        return self.decoder(combined)                  # (B, action_dim)


# ── Attention PPO Agent ───────────────────────────────────────────────────────

class AttentionPPOAgent(PPOAgent):
    """
    PPO agent with a Transformer-Attention actor for interpretable decisions.

    Key additions over PPOAgent
    ---------------------------
    • Uses `AttentionActorNetwork` instead of the flat MLP `ActorNetwork`.
    • `explain_last_action()` returns per-district attention weights as a dict.
    • Stores `self.last_attention` — accessible from the router for GIS overlay.
    """

    def __init__(
        self,
        districts:   List[DistrictState],
        n_periods:   int   = 30,
        truck_cap:   float = 5_000.0,
        uav_cap:     float = 200.0,
        lr:          float = 0.0001,
        clip_eps:    float = 0.2,
        gamma:       float = 0.99,
        gae_lambda:  float = 0.95,
        n_epochs:    int   = 4,
        batch_size:  int   = 64,
        d_model:     int   = 32,
        n_heads:     int   = 1,
        config: Optional[SimulationConfig] = None,
    ):
        # Initialise PPOAgent base (this builds actor/critic/opts)
        super().__init__(
            districts=districts, n_periods=n_periods,
            truck_cap=truck_cap, uav_cap=uav_cap,
            lr=lr, clip_eps=clip_eps, gamma=gamma,
            gae_lambda=gae_lambda, n_epochs=n_epochs,
            batch_size=batch_size, config=config,
        )
        cfg = config or DEFAULT_CONFIG
        d_model = getattr(cfg, "attn_d_model", d_model)
        n_heads  = getattr(cfg, "attn_n_heads", n_heads)

        # Override actor with attention-based version
        self.actor = AttentionActorNetwork(
            n_districts = len(districts),
            action_dim  = self.action_dim,
            d_model     = d_model,
            n_heads     = n_heads,
            global_dim  = 2,
        )
        import torch.optim as optim
        self.actor_opt = optim.Adam(self.actor.parameters(), lr=lr)

        self.last_attention: Optional[Dict[str, float]] = None

    # ── Feature preparation ───────────────────────────────────────────────────

    def _state_to_attention_tensors(
        self, state: MDPState,
    ) -> Tuple[torch.FloatTensor, torch.FloatTensor]:
        """
        Split MDPState into:
          district_feats : (1, N, 6)  — per-district feature matrix
          global_feats   : (1, 2)     — [epoch, cw_inventory]
        """
        global_feats = torch.FloatTensor([[float(state.epoch), state.cw_inventory]])
        d_feats = []
        for d in state.districts:
            d_feats.append([
                d.inventory, float(d.deprivation_time),
                d.demand_estimate, d.shortage,
                d.uav_cost, d.truck_cost,
            ])
        district_feats = torch.FloatTensor([d_feats])  # (1, N, 6)
        return district_feats, global_feats

    def _state_to_tensor(self, state: MDPState) -> torch.FloatTensor:
        """
        Override: return a flat 1D tensor for the critic (unchanged) and
        satisfy the base class contract.  The actor uses its own tensors.
        """
        feats = [float(state.epoch), state.cw_inventory]
        for d in state.districts:
            feats += [d.inventory, float(d.deprivation_time),
                      d.demand_estimate, d.shortage]
        return torch.FloatTensor(feats).unsqueeze(0)

    # ── Overridden get_action ─────────────────────────────────────────────────

    def get_action(self, state: MDPState):
        """Sample Dirichlet action from the attention actor."""
        d_feats, g_feats = self._state_to_attention_tensors(state)
        concentrations   = self.actor(d_feats, g_feats)  # (1, action_dim)
        dist             = torch.distributions.Dirichlet(concentrations)
        sample           = dist.sample().squeeze(0)
        raw              = sample.detach().numpy()
        actions          = self._map_action(raw, state)
        log_prob         = dist.log_prob(sample.unsqueeze(0)).squeeze(0)

        # Store attention explanation
        if self.actor.last_attention_weights is not None:
            weights = self.actor.last_attention_weights.squeeze(0).numpy()
            self.last_attention = {
                d.name: float(weights[i])
                for i, d in enumerate(state.districts)
            }

        return actions, log_prob, concentrations

    # ── Explanation API ───────────────────────────────────────────────────────

    def explain_last_action(self) -> Dict[str, float]:
        """
        Returns per-district attention weights from the most recent get_action().

        Returns
        -------
        dict: {district_name: attention_weight}
            Higher weight → agent paid more attention to that district.
        """
        if self.last_attention is None:
            return {}
        total = sum(self.last_attention.values()) + 1e-9
        return {k: v / total for k, v in self.last_attention.items()}

    def evaluate(
        self,
        scenario_gen:  ScenarioGenerator,
        initial_state: MDPState,
        n_eval:        int = 30,
    ) -> Dict:
        from app.ml.deprivation import marginal_deprivation_cost
        all_costs, all_dep = [], []
        max_dep = 0
        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(
                epoch=0, cw_inventory=initial_state.cw_inventory,
                districts=[DistrictState(**d.__dict__)
                           for d in initial_state.districts],
            )
            ep_cost = ep_dep = 0.0
            for t in range(self.n_periods):
                actions, _, _ = self.get_action(state)
                cost = self.transition.compute_cost(state, actions)
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
        return {
            "method":               "attention_ppo",
            "total_cost":           float(np.mean(all_costs)),
            "total_cost_std":       float(np.std(all_costs)),
            "deprivation_cost":     float(np.mean(all_dep)),
            "transport_cost":       float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
            "explainable":          True,
        }
