"""
routers/ml_extensions.py
New API endpoints for B.2, B.6, B.7 features.

Endpoints:
    POST /api/ml/demand-model/train       — Train Random Forest demand model
    GET  /api/ml/demand-model/importance  — Feature importance
    POST /api/ml/flood-predict            — Predict flood probability
    POST /api/ml/flood-model/train        — Train LSTM flood predictor
    GET  /api/ml/warehouses               — List all warehouses (multi-depot)
    POST /api/ml/warehouses               — Add a warehouse
    POST /api/ml/multi-depot/solve        — Solve multi-depot allocation
    POST /api/ml/multi-commodity/solve    — Solve multi-commodity allocation
"""

import numpy as np
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.auth.jwt_handler import get_current_user, require_manager_or_above
from app.database import get_db
from app.ml.demand_model import get_forecaster
from app.ml.flood_predictor import get_predictor, SEQUENCE_LEN, INPUT_DIM
from app.ml.multi_depot import (
    load_warehouses_from_db, solve_multi_depot_mip,
    DistrictDemandNode, Warehouse,
)
from app.ml.multi_commodity import (
    MCDistrictState, solve_multi_commodity_mip, COMMODITY_KEYS
)

router_ml = APIRouter()


# ════════════════════════════════════════════════════════════════════════════
# B.2 — Demand Model Endpoints
# ════════════════════════════════════════════════════════════════════════════

@router_ml.post("/demand-model/train")
async def train_demand_model(
    bg: BackgroundTasks,
    current: dict = Depends(require_manager_or_above),
):
    """Trigger async training of the Random Forest demand model."""
    bg.add_task(_train_demand_bg)
    return {"message": "Demand model training started in background.",
            "triggered_by": current["email"]}


async def _train_demand_bg():
    forecaster = get_forecaster()
    result = await forecaster.train()
    # Persist result to DB for monitoring
    from app.database import get_db
    db = get_db()
    await db.ml_training_logs.insert_one({
        "model": "demand_rf",
        "result": result,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    })


@router_ml.get("/demand-model/importance")
async def demand_feature_importance():
    """Return feature importances from the trained RF model."""
    forecaster = get_forecaster()
    if not forecaster.is_trained:
        raise HTTPException(503, "Demand model not trained yet. POST /train first.")
    return {
        "model": "random_forest",
        "feature_importances": forecaster.feature_importance(),
    }


@router_ml.get("/demand-model/status")
async def demand_model_status():
    forecaster = get_forecaster()
    return {
        "is_trained": forecaster.is_trained,
        "features":   forecaster.pipeline.named_steps["rf"].n_features_in_
                      if forecaster.is_trained else None,
    }


# ════════════════════════════════════════════════════════════════════════════
# B.7 — Flood Prediction Endpoints
# ════════════════════════════════════════════════════════════════════════════

class PrecipSequenceRequest(BaseModel):
    """10 days × 5 features (T1d–T5d). Row = day, Col = feature."""
    sequence: List[List[float]]     # shape (10, 5)
    district: Optional[str] = None

@router_ml.post("/flood-predict")
async def flood_predict(body: PrecipSequenceRequest):
    """
    Predict flood probability for next 7 days given precipitation sequence.
    """
    seq = np.array(body.sequence, dtype=np.float32)
    if seq.shape != (SEQUENCE_LEN, INPUT_DIM):
        # Auto-pad or trim
        padded = np.zeros((SEQUENCE_LEN, INPUT_DIM), dtype=np.float32)
        rows = min(seq.shape[0], SEQUENCE_LEN)
        cols = min(seq.shape[1] if seq.ndim > 1 else 1, INPUT_DIM)
        padded[-rows:, :cols] = seq[-rows:, :cols] if seq.ndim > 1 else seq[-rows:].reshape(-1, 1)
        seq = padded

    predictor = get_predictor()
    result    = predictor.predict(seq)
    if body.district:
        result["district"] = body.district
    return result


@router_ml.post("/flood-predict/batch")
async def flood_predict_batch(requests: List[PrecipSequenceRequest]):
    """Batch predict for multiple districts."""
    predictor = get_predictor()
    results = []
    for req in requests:
        seq = np.array(req.sequence, dtype=np.float32)
        if seq.shape != (SEQUENCE_LEN, INPUT_DIM):
            seq = np.zeros((SEQUENCE_LEN, INPUT_DIM), dtype=np.float32)
        r = predictor.predict(seq)
        if req.district:
            r["district"] = req.district
        results.append(r)
    return {"predictions": results}


@router_ml.post("/flood-model/train")
async def train_flood_model(
    bg: BackgroundTasks,
    n_epochs: int = 80,
    current: dict = Depends(require_manager_or_above),
):
    """Trigger async LSTM training."""
    bg.add_task(_train_flood_bg, n_epochs)
    return {"message": f"Flood LSTM training started ({n_epochs} epochs).",
            "triggered_by": current["email"]}


async def _train_flood_bg(n_epochs: int):
    predictor = get_predictor()
    result    = await predictor.train(n_epochs=n_epochs)
    from app.database import get_db
    db = get_db()
    await db.ml_training_logs.insert_one({
        "model":     "flood_lstm",
        "result":    result,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    })


@router_ml.get("/flood-model/status")
async def flood_model_status():
    predictor = get_predictor()
    return {"is_trained": predictor.is_trained}


# ════════════════════════════════════════════════════════════════════════════
# B.6 — Multi-Depot Endpoints
# ════════════════════════════════════════════════════════════════════════════

class WarehouseCreate(BaseModel):
    name:           str
    state:          str
    latitude:       float
    longitude:      float
    inventory:      float = 50_000.0
    supply_rate:    float = 5_000.0
    is_post_office: bool  = False

class DistrictNodeRequest(BaseModel):
    name:      str
    latitude:  float
    longitude: float
    demand:    float

class MultiDepotRequest(BaseModel):
    districts:      List[DistrictNodeRequest]
    truck_capacity: float = 5_000.0
    uav_capacity:   float = 200.0
    use_defaults:   bool  = True    # Include default state-capital warehouses

@router_ml.get("/warehouses")
async def list_warehouses():
    warehouses = await load_warehouses_from_db()
    return {
        "warehouses": [
            {
                "id": w.id, "name": w.name, "state": w.state,
                "latitude": w.latitude, "longitude": w.longitude,
                "inventory": w.inventory, "supply_rate": w.supply_rate,
                "is_post_office": w.is_post_office,
            }
            for w in warehouses
        ],
        "count": len(warehouses),
    }

@router_ml.post("/warehouses", status_code=201)
async def add_warehouse(
    body: WarehouseCreate,
    current: dict = Depends(require_manager_or_above),
):
    db = get_db()
    doc = body.dict()
    doc["id"] = body.name.lower().replace(" ", "_")
    await db.warehouses.insert_one(doc)
    return {"message": "Warehouse added.", "id": doc["id"]}

@router_ml.post("/multi-depot/solve")
async def solve_multi_depot(
    body: MultiDepotRequest,
    current: dict = Depends(get_current_user),
):
    """Solve multi-depot allocation MIP."""
    warehouses = await load_warehouses_from_db()

    districts = [
        DistrictDemandNode(
            name=d.name, latitude=d.latitude,
            longitude=d.longitude, demand=d.demand
        )
        for d in body.districts
    ]

    result = solve_multi_depot_mip(
        warehouses  = warehouses,
        districts   = districts,
        truck_cap   = body.truck_capacity,
        uav_cap     = body.uav_capacity,
    )

    total_cost = sum(
        route["cost"]
        for routes in result.values()
        for route in routes
    )

    return {
        "allocation": result,
        "total_cost": round(total_cost, 2),
        "warehouses_used": len({
            route["warehouse_id"]
            for routes in result.values()
            for route in routes
        }),
    }


# ════════════════════════════════════════════════════════════════════════════
# B.5 — Multi-Commodity Endpoints
# ════════════════════════════════════════════════════════════════════════════

class MCDistrictRequest(BaseModel):
    name:             str
    total_inventory:  float
    total_shortage:   float
    dep_time:         int
    total_demand:     float
    demand_std:       float
    uav_cost:         float   = 500.0
    truck_cost:       float   = 2000.0

class MultiCommodityRequest(BaseModel):
    districts:       List[MCDistrictRequest]
    cw_inventories:  Dict[str, float]   # commodity → units
    truck_cap_kg:    float = 5_000.0
    uav_cap_kg:      float = 200.0

@router_ml.post("/multi-commodity/solve")
async def solve_multi_commodity(
    body: MultiCommodityRequest,
    current: dict = Depends(get_current_user),
):
    """Solve multi-commodity MIP allocation."""
    mc_districts = [
        MCDistrictState.from_single_commodity(
            name            = d.name,
            total_inventory = d.total_inventory,
            total_shortage  = d.total_shortage,
            dep_time        = d.dep_time,
            total_demand    = d.total_demand,
            demand_std      = d.demand_std,
            uav_cost        = d.uav_cost,
            truck_cost      = d.truck_cost,
        )
        for d in body.districts
    ]

    actions = solve_multi_commodity_mip(
        districts      = mc_districts,
        cw_inventories = body.cw_inventories,
        truck_cap_kg   = body.truck_cap_kg,
        uav_cap_kg     = body.uav_cap_kg,
    )

    from app.ml.multi_commodity import compute_mc_cost
    total_cost = compute_mc_cost(mc_districts, actions,
                                  body.truck_cap_kg, body.uav_cap_kg)

    return {
        "allocation":  actions,
        "total_cost":  round(total_cost, 2),
        "commodities": COMMODITY_KEYS,
    }