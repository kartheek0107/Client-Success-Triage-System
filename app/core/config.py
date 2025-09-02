import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/client_success_db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_TITLE: str = os.getenv("API_TITLE", "Client Success Triage API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_KEY: str = os.getenv("API_KEY")
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")  # Default to 10 requests per minute
settings = Settings()