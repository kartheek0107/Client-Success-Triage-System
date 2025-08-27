from fastapi import FastAPI
from app.core.config import settings 

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description='AI-powered ticket classification system for client success teams.'
)

@app.get("/")
def read_root():
    return {
        "message":"Client Success Triage system is reunning!!!!!",
        "environment": settings.ENVIRONMENT,
        "database": settings.MONGO_URI
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}