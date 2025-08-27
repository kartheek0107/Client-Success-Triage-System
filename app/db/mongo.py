from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
from typing import Optional 

_client: Optioanl[MonogoClient] = None 
_db: Optional[Database] = None 

def get_client() -> Mongoclient:
    global _client
    if _client is None:
        _client = MongoClient(setting.MONGO_URI)
    return _client

def get_db() -> Database:
    global _db
    if _db is None:
        client = get_client()
        _db = client.get_database()
    return _db

def close_db():
    global _client
    if _client is not None:
        _client.close()