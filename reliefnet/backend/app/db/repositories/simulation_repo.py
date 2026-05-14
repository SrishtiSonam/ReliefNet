# reliefnet/backend/app/db/repositories/simulation_repo.py
from .base import BaseRepository
from ...models.simulation import SimulationResult
from motor.motor_asyncio import AsyncIOMotorDatabase

class SimulationRepository(BaseRepository[SimulationResult]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "simulation_runs", SimulationResult)

    async def get_by_run_id(self, run_id: str):
        return await self.get_by_id("run_id", run_id)
