from typing import Any, Dict, List, Optional
from datetime import datetime
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "appdb")

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(settings.database_url)
        _db = _client[settings.database_name]
    return _db


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = await get_db()
    now = datetime.utcnow()
    payload = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(payload)
    inserted = await db[collection_name].find_one({"_id": result.inserted_id})
    if inserted and "_id" in inserted:
        inserted["id"] = str(inserted.pop("_id"))
    return inserted or {}


async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    db = await get_db()
    cursor = db[collection_name].find(filter_dict or {}).sort("created_at", -1).limit(limit)
    items: List[Dict[str, Any]] = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        items.append(doc)
    return items
