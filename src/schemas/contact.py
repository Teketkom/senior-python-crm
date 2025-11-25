from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    organization_id: int
    owner_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True
