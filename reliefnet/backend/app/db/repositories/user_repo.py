# reliefnet/backend/app/db/repositories/user_repo.py
from .base import BaseRepository
from ...models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", User)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Return raw dict (not model) so hashed_password is accessible."""
        doc = await self.collection.find_one({"email": email})
        return doc

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Return raw dict (not model) so hashed_password is accessible."""
        doc = await self.collection.find_one({"username": username})
        return doc

    async def create(self, user_dict: dict) -> dict:
        """Insert raw dict directly (includes hashed_password)."""
        await self.collection.insert_one(user_dict)
        return user_dict
