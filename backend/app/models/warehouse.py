# ─── models/warehouse.py ─────────────────────────────────────────────────────
from pydantic import BaseModel

class CentralWarehouse(BaseModel):
    name:           str
    state:          str
    latitude:       float
    longitude:      float
    initial_stock:  float       # Units of relief supplies
    supply_rate:    float       # Mean units arriving per period
    supply_std:     float       # Std dev of supply arrival
