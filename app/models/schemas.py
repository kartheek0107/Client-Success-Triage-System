from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# === Core Ticket Models ===
class TicketBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    client_id: str = Field(..., min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = "open"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TicketInDB(TicketBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "allow"


# === Classified Ticket Model (for AI + DB Storage) ===
class ClassifiedTicketBase(TicketBase):
    """
    Base model for tickets that include AI predictions.
    Used when storing classified results in MongoDB.
    """
    predicted_priority: Optional[str] = None
    predicted_category: Optional[str] = None
    priority_confidence: Optional[float] = None
    category_confidence: Optional[float] = None
    classification_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassifiedTicketCreate(ClassifiedTicketBase):
    """
    Model for creating a classified ticket (from batch or API).
    """
    pass


class ClassifiedTicketInDB(ClassifiedTicketBase):
    """
    Model for classified tickets stored in MongoDB.
    """
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "allow"