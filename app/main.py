from fastapi import FastAPI
from app.core.config import settings 
from app.db.mongo import get_db

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description='AI-powered ticket classification system for client success teams.'
)

@app.get("/")
def read_root():
    try:
        db = get_db()
        db.client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"failed: {str(e)}"
        
    return {
        "message": "Client Success Triage system is running!",  # Fixed: typo
        "environment": settings.ENVIRONMENT,
        "database_status": db_status,  # Fixed: show actual status, not URI for security
        "version": settings.API_VERSION
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    """Initialize database connection on startup."""
    try:
        db = get_db()
        print(f"Connected to MongoDB: {settings.ENVIRONMENT}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
def shutdown_event():
    """Clean up database connections on shutdown."""
    from app.db.mongo import close_db
    close_db()
    print("Database connections closed")