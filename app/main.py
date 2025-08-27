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
        "message":"Client Success Triage system is reunning!!!!!",
        "environment": settings.ENVIRONMENT,
        "database": settings.MONGO_URI
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    db = get_db()

@app.on_event("shutdown")
def shutdown_event():
    from app.db.mongo import close_db
    close_db()