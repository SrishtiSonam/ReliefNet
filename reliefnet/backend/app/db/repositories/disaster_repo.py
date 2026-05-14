# reliefnet/backend/app/db/repositories/disaster_repo.py
from .base import BaseRepository
from ...models.disaster import DisasterEvent
from motor.motor_asyncio import AsyncIOMotorDatabase

class DisasterRepository(BaseRepository[DisasterEvent]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "disasters", DisasterEvent)

    async def get_by_dis_no(self, dis_no: str):
        return await self.get_by_id("dis_no", dis_no)
