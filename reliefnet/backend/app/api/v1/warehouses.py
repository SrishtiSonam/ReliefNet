# reliefnet/backend/app/api/v1/warehouses.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...db.repositories.warehouse_repo import WarehouseRepository
from ...dependencies import db_dep
from ...models.infrastructure import Warehouse

router = APIRouter()

@router.get("/", response_model=List[Warehouse])
async def get_warehouses(db = Depends(db_dep)):
    repo = WarehouseRepository(db)
    return await repo.get_many()

@router.get("/{id}", response_model=Warehouse)
async def get_warehouse(id: str, db = Depends(db_dep)):
    repo = WarehouseRepository(db)
    warehouse = await repo.get_by_warehouse_id(id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.put("/{id}/inventory", response_model=Warehouse)
async def update_warehouse_inventory(id: str, inventory: dict, db = Depends(db_dep)):
    repo = WarehouseRepository(db)
    updated = await repo.update("warehouse_id", id, inventory)
    if not updated:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return updated

@router.post("/{id}/transaction", response_model=Warehouse)
async def create_warehouse_transaction(id: str, transaction: dict, db = Depends(db_dep)):
    repo = WarehouseRepository(db)
    warehouse = await repo.get_by_warehouse_id(id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    resource_map = {
        "rice": "stock_rice_tons",
        "wheat": "stock_wheat_tons",
        "medicine": "stock_medicine_kits",
        "tarpaulin": "stock_tarpaulin_units"
    }
    field = resource_map.get(transaction.get("resource", "").lower())
    if not field:
        raise HTTPException(status_code=400, detail="Invalid resource type")
        
    amount = float(transaction.get("amount", 0))
    if transaction.get("type") == "SUBTRACT":
        amount = -amount
        
    current_val = getattr(warehouse, field)
    new_val = max(0, current_val + amount)
    
    from ...models.infrastructure import WarehouseTransaction
    txn = WarehouseTransaction(
        resource=transaction.get("resource"),
        amount=abs(amount),
        type=transaction.get("type"),
        reason=transaction.get("reason", "Manual adjustment")
    )
    
    # Update inventory value and push transaction to array
    await db.get_collection("warehouses").update_one(
        {"warehouse_id": id},
        {
            "$set": {field: int(new_val) if field in ["stock_medicine_kits", "stock_tarpaulin_units"] else float(new_val)},
            "$push": {"transactions": txn.model_dump()}
        }
    )
    
    return await repo.get_by_warehouse_id(id)
