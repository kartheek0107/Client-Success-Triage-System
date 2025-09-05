# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Import config, db, classifier
from app.core.config import settings
from app.db.mongo import get_db, close_db
from nlp_pipeline.models.bert_classifier import BERTTicketClassifier

# Security
from app.api.v1.auth import get_api_key

# Models
from pydantic import BaseModel
from typing import Dict

# -------------------------------
# Initialize FastAPI App
# -------------------------------
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered ticket classification system for client success teams."
)

# -------------------------------
# Rate Limiting Setup
# -------------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -------------------------------
# CORS Middleware (Optional)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Global Variables
# -------------------------------
classifier: BERTTicketClassifier

# -------------------------------
# Pydantic Models
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
# Startup & Shutdown Events
# -------------------------------
@app.on_event("startup")
def startup_event():
    global classifier
    
    # Try MongoDB connection
    mongodb_available = False
    try:
        db = get_db()
        db.client.admin.command("ping")
        print("✅ Connected to MongoDB")
        mongodb_available = True
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        if settings.REQUIRE_MONGODB:
            print("❌ MongoDB is required but unavailable. Exiting.")
            raise
        else:
            print("🔄 Continuing without MongoDB (ticket saving disabled)")

    # Load classifier (this should work regardless of MongoDB)
    try:
        print("🧠 Loading BERT ticket classifier...")
        classifier = BERTTicketClassifier()
        print("✅ BERT classifier loaded successfully")
    except Exception as e:
        print(f"❌ Classifier loading failed: {e}")
        raise
    
    # Store MongoDB status globally
    app.state.mongodb_available = mongodb_available

@app.on_event("shutdown")
def shutdown_event():
    close_db()
    print("💤 Database connections closed")


# -------------------------------
# Health & Status Endpoints
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
@app.post("/classify", response_model=ClassificationResponse)
@limiter.limit("100/minute")
def classify_ticket(
    request: Request,
    body: ClassifyRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Classify a support ticket into priority and category.
    Uses BERT model loaded at startup.
    """
    try:
        result = classifier.classify(body.subject, body.description)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


# -------------------------------
# Save Classified Ticket to MongoDB
# -------------------------------
from app.models.schemas import ClassifiedTicketCreate
from pymongo.errors import PyMongoError

@app.post("/tickets")
@limiter.limit("50/minute")
def save_ticket(
    request: Request,
    ticket: ClassifiedTicketCreate,
    api_key: str = Depends(get_api_key)
):
    """Save a classified ticket to MongoDB (if available)."""
    if not getattr(app.state, 'mongodb_available', False):
        raise HTTPException(
            status_code=503,
            detail="Database unavailable - ticket classification works but saving is disabled"
        )
    
    try:
        db = get_db()
        collection = db["classified_tickets"]
        result = collection.insert_one(ticket.dict(by_alias=True))
        return {"status": "saved", "inserted_id": str(result.inserted_id)}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")