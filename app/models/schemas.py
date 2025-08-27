from datetime import datetime 
from typing import Optional 
from pydantic import BaseModel, Field

class TicketBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)  # Fixed: spacing
    client_id: str = Field(..., min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = "open"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):  # Fixed: class name spelling
    category: Optional[str] = None 
    priority: Optional[str] = None 
    status: Optional[str] = None

class TicketInDB(TicketBase):  # Fixed: class name spelling
    id: str = Field(..., alias='_id')  # Fixed: MongoDB uses _id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:  # Fixed: Config capitalization
        allow_population_by_field_name = True
        validate_assignment = True 
        extra = 'allow'