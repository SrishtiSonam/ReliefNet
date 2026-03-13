# ─── loader.py ────────────────────────────────────────────────────────────────
"""Load all CSV datasets into MongoDB."""
import pandas as pd
from pathlib import Path
from app.database import get_db
from app.utils.logger import get_logger

logger  = get_logger(__name__)
DATA_DIR = Path(__file__).parent.parent.parent / "datasets"

async def load_all_datasets():
    db = get_db()
    await _load_dfsi(db)
    await _load_flood_impact(db)
    await _load_flooded_area(db)
    await _load_flood_inventory(db)
    await _load_indofloods_events(db)
    await _load_indofloods_metadata(db)
    await _load_indofloods_catchment(db)
    await _load_precipitation(db)
    logger.info("All datasets loaded into MongoDB.")

async def _load_dfsi(db):
    df = pd.read_csv(DATA_DIR / "DFSI.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    records = df.to_dict("records")
    await db.dfsi.drop()
    await db.dfsi.insert_many(records)
    logger.info(f"DFSI loaded: {len(records)} records")

async def _load_flood_impact(db):
    df = pd.read_csv(DATA_DIR / "District_FloodImpact.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    await db.flood_impact.drop()
    await db.flood_impact.insert_many(df.to_dict("records"))

async def _load_flooded_area(db):
    df = pd.read_csv(DATA_DIR / "District_FloodedArea.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    await db.flooded_area.drop()
    await db.flooded_area.insert_many(df.to_dict("records"))

async def _load_flood_inventory(db):
    df = pd.read_csv(DATA_DIR / "India_Flood_Inventory_v3.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.where(pd.notnull(df), None)
    await db.flood_inventory.drop()
    await db.flood_inventory.insert_many(df.to_dict("records"))

async def _load_indofloods_events(db):
    df = pd.read_csv(DATA_DIR / "floodevents_indofloods.csv")
    df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
                  for c in df.columns]
    await db.indofloods_events.drop()
    await db.indofloods_events.insert_many(df.to_dict("records"))

async def _load_indofloods_metadata(db):
    df = pd.read_csv(DATA_DIR / "metadata_indofloods.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    await db.indofloods_metadata.drop()
    await db.indofloods_metadata.insert_many(df.to_dict("records"))

async def _load_indofloods_catchment(db):
    df = pd.read_csv(DATA_DIR / "catchment_characteristics_indofloods.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    await db.catchment_characteristics.drop()
    await db.catchment_characteristics.insert_many(df.to_dict("records"))

async def _load_precipitation(db):
    df = pd.read_csv(DATA_DIR / "precipitation_variables_indofloods.csv")
    df.columns = [c.strip().lower() for c in df.columns]
    await db.precipitation.drop()
    await db.precipitation.insert_many(df.to_dict("records"))
