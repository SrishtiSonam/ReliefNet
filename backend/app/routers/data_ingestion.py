# ─── routers/data_ingestion.py ────────────────────────────────────────────────
from fastapi import APIRouter, BackgroundTasks
from app.data.loader import load_all_datasets

router_di = APIRouter()

@router_di.post("/load-all")
async def load_datasets(bg: BackgroundTasks):
    bg.add_task(load_all_datasets)
    return {"message": "Dataset loading started in background."}

@router_di.get("/status")
async def data_status():
    db = get_db()
    return {
        "dfsi":                 await db.dfsi.count_documents({}),
        "flood_impact":         await db.flood_impact.count_documents({}),
        "flooded_area":         await db.flooded_area.count_documents({}),
        "flood_inventory":      await db.flood_inventory.count_documents({}),
        "indofloods_events":    await db.indofloods_events.count_documents({}),
        "indofloods_metadata":  await db.indofloods_metadata.count_documents({}),
        "catchment":            await db.catchment_characteristics.count_documents({}),
        "precipitation":        await db.precipitation.count_documents({}),
    }