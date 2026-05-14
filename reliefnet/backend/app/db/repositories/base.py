# reliefnet/backend/app/db/repositories/base.py
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[ModelType]):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.model = model

    async def create(self, obj_in: ModelType) -> ModelType:
        obj_data = obj_in.model_dump()
        await self.collection.insert_one(obj_data)
        return obj_in

    async def get_by_id(self, id_field: str, id_value: Any) -> Optional[ModelType]:
        doc = await self.collection.find_one({id_field: id_value})
        if doc:
            return self.model(**doc)
        return None

    async def get_many(self, query: Dict[str, Any] = {}, limit: int = 100, skip: int = 0) -> List[ModelType]:
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            results.append(self.model(**doc))
        return results

    async def update(self, id_field: str, id_value: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        await self.collection.update_one({id_field: id_value}, {"$set": obj_in})
        return await self.get_by_id(id_field, id_value)

    async def delete(self, id_field: str, id_value: Any) -> bool:
        result = await self.collection.delete_one({id_field: id_value})
        return result.deleted_count > 0
