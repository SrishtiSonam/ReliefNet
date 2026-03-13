# ─── database.py ─────────────────────────────────────────────────────────────
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]

async def disconnect_db():
    global client
    if client:
        client.close()

def get_db():
    return db