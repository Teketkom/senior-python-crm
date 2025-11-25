from pydantic import BaseModel
from typing import List

class OrganizationResponse(BaseModel):
    id: int
    name: str
    created_at: str
    role: str
    
    class Config:
        from_attributes = True

class OrganizationMemberResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    role: str
    
    class Config:
        from_attributes = True
