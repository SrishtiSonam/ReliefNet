# reliefnet/backend/app/db/repositories/hospital_repo.py
from .base import BaseRepository
from ...models.infrastructure import Hospital
from motor.motor_asyncio import AsyncIOMotorDatabase

class HospitalRepository(BaseRepository[Hospital]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "hospitals", Hospital)

    async def get_by_hospital_id(self, hospital_id: str):
        return await self.get_by_id("hospital_id", hospital_id)
