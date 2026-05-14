# reliefnet/backend/app/db/mongo.py
"""MongoDB async client using Motor.
Provides a function to create a Motor client and expose the database.
"""

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from ..config import Settings

async def get_mongo_client(uri: str) -> AsyncIOMotorClient:
    """Create and return a Motor async client.
    Caller is responsible for closing the client when done.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    return client

def get_database(client: AsyncIOMotorClient, db_name: str):
    return client[db_name]
