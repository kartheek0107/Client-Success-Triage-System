from datetime import datetime 
from typing import Optional 
from pydantic import BaseModel, Field

class TicketBase(BaseModel):
    subject: str = Field(...,min_length=1,max_length=200)
    description:str = Field(...,min_length=1)
    client_id: str = Field(...,min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = "open"

class TicketCreate(TicketBase):
    pass

class TcketUpdate(BaseModel):
    category: Optional[str] = None 
    priority: Optional[str] = None 
    status: Optional[str] = None

class TicketinDB(TicketBase):
    id: str = Field(...,alias='id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class config:
        allow_population_by_field_name = True
        validate_assignment = True 
        extra = 'allow'