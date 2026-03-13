"""
config.py
Central, frozen SimulationConfig dataclass.

All agent constructors and the DemandForecaster.train() method accept an
optional config: SimulationConfig = None parameter.  When None, a default
instance (all fields at their canonical defaults) is used.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """Single source of truth for every hyperparameter used across all agents."""

    # ── Vehicle capacities ────────────────────────────────────────────────────
    truck_cap:            float = 5_000.0
    uav_cap:              float =   200.0

    # ── MDP horizon & discounting ─────────────────────────────────────────────
    n_periods:            int   =    30
    discount:             float =   0.9

    # ── PPO hyperparameters ───────────────────────────────────────────────────
    ppo_lr:               float = 0.0001
    ppo_clip_eps:         float =   0.2
    ppo_gamma:            float =  0.99
    ppo_gae_lambda:       float =  0.95
    ppo_n_epochs:         int   =     4
    ppo_batch_size:       int   =    64

    # ── DL-VFA hyperparameters ────────────────────────────────────────────────
    dl_vfa_alpha_init:    float =   0.2
    dl_vfa_alpha_decay:   float =  0.99
    dl_vfa_eps_init:      float =   0.2
    dl_vfa_eps_decay:     float =  0.98

    # ── NN-VFA hyperparameters ────────────────────────────────────────────────
    nn_vfa_lr:            float = 0.001
    nn_vfa_batch_size:    int   =   256

    # ── MIP solver settings ───────────────────────────────────────────────────
    mip_time_limit_sec:   int   =    30
    mip_max_trucks:       int   =    10
    mip_max_uavs:         int   =    20

    # ── Random Forest demand model ────────────────────────────────────────────
    rf_n_estimators:      int   =   300
    rf_max_depth:         int   =    12
    rf_min_samples_leaf:  int   =     3

    # ── Improvement 1: Equity / Fairness Constrained PPO ─────────────────────
    equity_lambda_gini:   float =   0.3   # Gini coefficient penalty weight
    equity_lambda_maxmin: float =   0.1   # Max-Min gap penalty weight

    # ── Improvement 2: Multi-Agent RL (MAPPO) ─────────────────────────────────
    marl_n_agents:        int   =     3   # number of decentralised warehouse agents
    marl_comm_drop_prob:  float =   0.2   # per-step inter-agent comms drop probability

    # ── Improvement 3: Stochastic Road/Edge Failures ──────────────────────────
    road_failure_k:       float =   3.0   # sigmoid steepness vs DFSI score
    road_use_failures:    bool  = False   # opt-in flag (False = backward-compatible)

    # ── Improvement 4: Explainable RL (Attention-Based Policy) ───────────────
    attn_d_model:         int   =    32   # district embedding dimension
    attn_n_heads:         int   =     1   # number of self-attention heads

    # ── Improvement 5: GNN Neural Warm-Starting for MIP ──────────────────────
    gnn_use_warm_start:   bool  = False   # opt-in to neural warm-starting
    gnn_hidden_dim:       int   =    16   # GCN hidden feature dimension
    gnn_n_layers:         int   =     2   # number of graph conv layers


# Module-level default instance — import and use directly for convenience.
DEFAULT_CONFIG = SimulationConfig()
