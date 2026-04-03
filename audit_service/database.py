from motor.motor_asyncio import AsyncIOMotorClient
from common.schemas import AuditLog
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.platform_db
logs_collection = db.audit_logs

async def setup_db():
    # Create indexes as required
    await logs_collection.create_index("correlation_id")
    await logs_collection.create_index("timestamp")
    await logs_collection.create_index("service")
