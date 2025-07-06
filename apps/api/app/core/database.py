from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def init_db():
    db.client = AsyncIOMotorClient(settings.database_url)
    db.db = db.client.get_default_database()
    
    # Create indexes
    await db.db.users.create_index("email", unique=True)
    await db.db.users.create_index("username", unique=True)
    await db.db.channels.create_index("name", unique=True)
    await db.db.messages.create_index([("channel_id", 1), ("timestamp", -1)])
    await db.db.messages.create_index("user_id")

async def close_db():
    if db.client:
        db.client.close()

def get_db():
    return db.db 