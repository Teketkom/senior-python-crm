from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from src.models.schema import ActivityType

class ActivityCreate(BaseModel):
    type: ActivityType
    payload: Optional[Dict[str, Any]] = None

class ActivityResponse(BaseModel):
    id: int
    deal_id: int
    author_id: Optional[int]
    type: str
    payload: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True
