from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
from typing import Optional 

_client: Optional[MongoClient] = None  # Fixed: Optional and MongoClient spelling
_db: Optional[Database] = None 

def get_client() -> MongoClient:  # Fixed: MongoClient spelling
    """Get MongoDB client instance (singleton pattern)."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)  # Fixed: settings spelling
    return _client

def get_db() -> Database:
    """Get MongoDB database instance."""
    global _db
    if _db is None:
        client = get_client()
        _db = client.get_database()
    return _db

def close_db():
    """Close MongoDB connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None