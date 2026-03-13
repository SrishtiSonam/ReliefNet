# ─── routers/flood_events.py ──────────────────────────────────────────────────
from fastapi import APIRouter, Query
from app.database import get_db
from typing import Optional

router_fe = APIRouter()

@router_fe.get("/")
async def get_flood_events(state: Optional[str] = None,
                            flood_type: Optional[str] = None,
                            limit: int = Query(100, le=500)):
    db = get_db()
    query = {}
    if state:      query["state"] = {"$regex": state, "$options": "i"}
    if flood_type: query["flood_type"] = flood_type
    docs = await db.indofloods_events.find(query, {"_id": 0}).to_list(length=limit)
    return {"flood_events": docs, "count": len(docs)}

@router_fe.get("/inventory")
async def get_flood_inventory(state: Optional[str] = None, limit: int = 200):
    db    = get_db()
    query = {}
    if state: query["state"] = {"$regex": state, "$options": "i"}
    docs  = await db.flood_inventory.find(query, {"_id": 0}).to_list(length=limit)
    return {"events": docs, "count": len(docs)}

@router_fe.get("/kerala-2018")
async def get_kerala_2018():
    db   = get_db()
    docs = await db.flood_inventory.find(
        {"state": {"$regex": "kerala", "$options": "i"},
         "start_date": {"$regex": "2018"}},
        {"_id": 0}
    ).to_list(length=200)
    return {"kerala_2018_events": docs, "count": len(docs)}
