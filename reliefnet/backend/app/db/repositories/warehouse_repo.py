# reliefnet/backend/app/db/repositories/warehouse_repo.py
from .base import BaseRepository
from ...models.infrastructure import Warehouse
from motor.motor_asyncio import AsyncIOMotorDatabase

class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "warehouses", Warehouse)

    async def get_by_warehouse_id(self, warehouse_id: str):
        return await self.get_by_id("warehouse_id", warehouse_id)
