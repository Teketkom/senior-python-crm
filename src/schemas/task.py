from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    deal_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    deal_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    is_done: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
