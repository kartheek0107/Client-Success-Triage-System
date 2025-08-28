from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict

# Import configuration and DB
from app.core.config import settings
from app.db.mongo import get_db, close_db

# Import BERT classifier
from nlp_pipeline.models.bert_classifier import BERTTicketClassifier


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered ticket classification system for client success teams."
)


# Global variable to hold the classifier
classifier: BERTTicketClassifier


# -------------------------------
# Pydantic Models for API
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
    """Initialize database and load BERT classifier on startup."""
    global classifier
    try:
        # Initialize DB
        db = get_db()
        db.client.admin.command("ping")
        print("✅ Connected to MongoDB")

        # Load BERT classifier
        print("🧠 Loading BERT ticket classifier...")
        classifier = BERTTicketClassifier()
        print("✅ BERT classifier loaded successfully")

    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
def shutdown_event():
    """Clean up database connections."""
    close_db()
    print("💤 Database connections closed")


# -------------------------------
# API Endpoints
# -------------------------------
@app.get("/")
def read_root():
    """Health and status endpoint."""
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
    """Simple health check."""
    return {"status": "healthy"}


@app.post("/classify", response_model=ClassificationResponse)
def classify_ticket(request: ClassifyRequest) -> Dict:
    """
    Classify a support ticket based on subject and description.
    
    Returns predicted priority and category with confidence scores.
    """
    try:
        result = classifier.classify(request.subject, request.description)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )