# reliefnet/backend/app/db/repositories/district_repo.py
from .base import BaseRepository
from ...models.district import DistrictFeatures
from motor.motor_asyncio import AsyncIOMotorDatabase

class DistrictRepository(BaseRepository[DistrictFeatures]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "districts", DistrictFeatures)

    async def get_by_name(self, name: str):
        return await self.get_by_id("district", name)

# reliefnet/backend/app/db/repositories/warehouse_repo.py
from .base import BaseRepository
from ...models.infrastructure import Warehouse
from motor.motor_asyncio import AsyncIOMotorDatabase

class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "warehouses", Warehouse)

    async def get_by_warehouse_id(self, warehouse_id: str):
        return await self.get_by_id("warehouse_id", warehouse_id)
