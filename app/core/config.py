# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB with fallback
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/client_success_db")
    
    # Allow app to start without MongoDB
    REQUIRE_MONGODB: bool = os.getenv("REQUIRE_MONGODB", "false").lower() == "true"
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_TITLE: str = os.getenv("API_TITLE", "Client Success Triage API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_KEY: str = os.getenv("API_KEY", "dev-key-change-in-production")
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")

settings = Settings()