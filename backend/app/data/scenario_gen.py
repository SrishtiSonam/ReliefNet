# ─── scenario_gen.py ──────────────────────────────────────────────────────────
"""Generate sample paths using real INDOFLOODS precipitation data."""
import numpy as np
import pandas as pd
from app.database import get_db
from app.ml.mdp import DistrictState, ScenarioGenerator

async def build_scenario_generator(districts: list[DistrictState],
                                    supply_mean: float,
                                    n_periods: int = 30,
                                    cov: float = 0.2) -> ScenarioGenerator:
    """
    Use precipitation variability from INDOFLOODS to set supply_std.
    Higher antecedent precipitation (T1d-T10d) → higher demand variability.
    """
    db     = get_db()
    cursor = db.precipitation.find({}, {"t1d": 1, "t2d": 1, "t3d": 1})
    docs   = await cursor.to_list(length=1000)

    if docs:
        t1d_vals = [d.get("t1d", 0) for d in docs if d.get("t1d") is not None]
        precip_std = np.std(t1d_vals) if t1d_vals else supply_mean * cov
        supply_std = supply_mean * (precip_std / (np.mean(t1d_vals) + 1e-6)) \
                     if t1d_vals else supply_mean * cov
    else:
        supply_std = supply_mean * cov

    return ScenarioGenerator(
        districts    = districts,
        supply_mean  = supply_mean,
        supply_std   = min(supply_std, supply_mean * 0.4),  # Cap at 40%
        n_periods    = n_periods
    )