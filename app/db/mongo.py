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

def get_db():
    # Extract database name from URI or use a default
    from urllib.parse import urlparse
    parsed = urlparse(settings.MONGO_URI)
    db_name = parsed.path.strip("/") or "client_success_db"
    return _client[db_name]  # ← This is the fix

def close_db():
    """Close MongoDB connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None