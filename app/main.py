# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware  # Optional
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Import config, db, classifier
from app.core.config import settings
from app.db.mongo import get_db, close_db
from nlp_pipeline.models.bert_classifier import BERTTicketClassifier

# Security
from app.api.v1.auth import get_api_key
from app.api.v1.rate_limiter import limiter

# Models
from pydantic import BaseModel
from typing import Dict

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered ticket classification system for client success teams."
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (optional, if calling from frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global classifier
classifier: BERTTicketClassifier


# -------------------------------
# Models
# -------------------------------
class ClassifyRequest(BaseModel):
    subject: str
    description: str


class ClassificationResponse(BaseModel):
    priority: str
    priority_confidence: float
    category: str
    category_confidence: float


# -------------------------------
# Startup & Shutdown
# -------------------------------
@app.on_event("startup")
def startup_event():
    global classifier
    try:
        db = get_db()
        db.client.admin.command("ping")
        print("✅ Connected to MongoDB")

        print("🧠 Loading BERT classifier...")
        classifier = BERTTicketClassifier()
        print("✅ BERT classifier loaded")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
def shutdown_event():
    close_db()
    print("💤 DB connections closed")


# -------------------------------
# Public Health Endpoints (No Auth)
# -------------------------------
@app.get("/")
def read_root():
    try:
        db = get_db()
        db.client.admin.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"failed: {str(e)}"

    return {
        "message": "Client Success Triage system is running!",
        "environment": settings.ENVIRONMENT,
        "database_status": db_status,
        "version": settings.API_VERSION,
        "api_docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# -------------------------------
# Secure Classification Endpoint
# -------------------------------

class ClassifyRequest(BaseModel):
    subject: str
    description: str

@app.post("/classify", response_model=ClassificationResponse)
@limiter.limit("10/minute") 
def classify_ticket(
    request: Request,
    body: ClassifyRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Classify a ticket using BERT. Protected by API key and rate limiting.
    """
    try:
        result = classifier.classify(body.subject, body.description)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )