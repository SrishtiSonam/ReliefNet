# reliefnet/backend/app/db/repositories/override_repo.py
from .base import BaseRepository
from ...models.allocation import OverrideRecord
from motor.motor_asyncio import AsyncIOMotorDatabase

class OverrideRepository(BaseRepository[OverrideRecord]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "overrides", OverrideRecord)
