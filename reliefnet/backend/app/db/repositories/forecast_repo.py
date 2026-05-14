# reliefnet/backend/app/db/repositories/forecast_repo.py
from .base import BaseRepository
from ...models.forecast import ForecastResult
from motor.motor_asyncio import AsyncIOMotorDatabase

class ForecastRepository(BaseRepository[ForecastResult]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "forecasts", ForecastResult)

    async def get_by_forecast_id(self, forecast_id: str):
        return await self.get_by_id("forecast_id", forecast_id)
