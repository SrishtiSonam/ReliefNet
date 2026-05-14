# reliefnet/backend/app/db/repositories/allocation_repo.py
from .base import BaseRepository
from ...models.allocation import AllocationPlan
from motor.motor_asyncio import AsyncIOMotorDatabase

class AllocationRepository(BaseRepository[AllocationPlan]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "allocations", AllocationPlan)

    async def get_by_allocation_id(self, allocation_id: str):
        return await self.get_by_id("allocation_id", allocation_id)
