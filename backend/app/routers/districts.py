# ─── routers/districts.py ─────────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.data.demand_estimator import estimate_demand
from app.data.cost_calculator import compute_costs

router = APIRouter()

@router.get("/")
async def get_all_districts():
    db = get_db()
    docs = await db.flood_impact.find({}, {"_id": 0}).to_list(length=1000)
    return {"districts": docs}

@router.get("/{district_name}")
async def get_district(district_name: str):
    db   = get_db()
    doc  = await db.flood_impact.find_one(
        {"dist_name": {"$regex": district_name, "$options": "i"}}, {"_id": 0}
    )
    dfsi = await db.dfsi.find_one(
        {"state_name": {"$exists": True}}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(404, f"District '{district_name}' not found")
    return {"district": doc, "dfsi": dfsi}

@router.get("/{district_name}/demand")
async def get_district_demand(district_name: str, period_hours: int = 6):
    return await estimate_demand(district_name, period_hours)

@router.get("/{district_name}/costs")
async def get_district_costs(district_name: str,
                              wh_lat: float, wh_lon: float,
                              dist_lat: float, dist_lon: float):
    return await compute_costs(district_name, wh_lat, wh_lon, dist_lat, dist_lon)

@router.get("/dfsi/all")
async def get_dfsi_scores():
    db   = get_db()
    docs = await db.dfsi.find({}, {"_id": 0}).to_list(length=1000)
    return {"dfsi_scores": docs}


