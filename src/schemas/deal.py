from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from src.models.schema import DealStatus, DealStage

class DealCreate(BaseModel):
    contact_id: Optional[int] = None
    title: str
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(..., pattern="^(USD|EUR)$")

class DealUpdate(BaseModel):
    status: Optional[DealStatus] = None
    stage: Optional[DealStage] = None
    title: Optional[str] = None
    amount: Optional[Decimal] = Field(None, ge=0)

class DealResponse(BaseModel):
    id: int
    organization_id: int
    contact_id: Optional[int]
    owner_id: int
    title: str
    amount: Decimal
    currency: str
    status: str
    stage: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
